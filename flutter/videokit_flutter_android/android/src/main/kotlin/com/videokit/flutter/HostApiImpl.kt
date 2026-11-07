package com.videokit.flutter

import android.annotation.SuppressLint
import android.net.Uri
import com.videokit.api.EditCommandResult
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.HostCallbackTimeouts
import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationResult
import com.videokit.api.OrientationRequest
import com.videokit.api.SessionVisibility
import com.videokit.api.VideoKitApiVersion
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEditProject
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitExportResult
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitOutputSink
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitStableError
import com.videokit.api.android.MediaSources
import com.videokit.flutter.Mappers.toAction
import com.videokit.flutter.Mappers.toCommand
import com.videokit.flutter.Mappers.toConfig
import com.videokit.flutter.Mappers.toKind
import com.videokit.flutter.Mappers.toMode
import com.videokit.flutter.Mappers.toMsg
import com.videokit.flutter.Mappers.toPlaybackState
import com.videokit.flutter.Mappers.toRequest
import com.videokit.flutter.Mappers.toSerialized
import com.videokit.flutter.Mappers.toSource
import com.videokit.flutter.Mappers.toTransform
import com.videokit.flutter.gen.CandidateResultMsg
import com.videokit.flutter.gen.CapabilitiesMsg
import com.videokit.flutter.gen.CapabilityRequestMsg
import com.videokit.flutter.gen.CommandResultMsg
import com.videokit.flutter.gen.CreateResultMsg
import com.videokit.flutter.gen.EditCommandMsg
import com.videokit.flutter.gen.EditProjectConfigMsg
import com.videokit.flutter.gen.EditResultMsg
import com.videokit.flutter.gen.ExportRequestMsg
import com.videokit.flutter.gen.ExportResultMsg
import com.videokit.flutter.gen.FlutterError
import com.videokit.flutter.gen.HandshakeRequest
import com.videokit.flutter.gen.HandshakeResponse
import com.videokit.flutter.gen.HostActionMsg
import com.videokit.flutter.gen.MediaSourceMsg
import com.videokit.flutter.gen.PlaybackStateMsg
import com.videokit.flutter.gen.PrecheckMsg
import com.videokit.flutter.gen.SeekModeMsg
import com.videokit.flutter.gen.SerializedProjectMsg
import com.videokit.flutter.gen.SessionConfigMsg
import com.videokit.flutter.gen.TransformMsg
import com.videokit.flutter.gen.VideoKitHostApi
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.withContext

/** Protocol version of the native side (14 §8.3). */
internal const val CHANNEL_PROTOCOL_VERSION: Long = 1L

/** Version of the native Kit artifacts reported in the handshake. */
internal const val NATIVE_KIT_VERSION: String = "1.0.0-dev.1"

/**
 * Pigeon HostApi of one engine (14 §8.2, §8.3). Pigeon calls the `suspend` methods on the main thread and
 * replies there; every method switches to the engine's work dispatcher (never I/O on the main thread):
 * - one method per command;
 * - unknown session ids answer `sessionReleased` (late calls after release are normal), unknown project ids
 *   `projectReleased`;
 * - internal failures become `rejected(INTERNAL_ERROR_REDACTED)`; only protocol errors (no handshake, no
 *   backend) are thrown as [FlutterError].
 */
internal class HostApiImpl(private val engine: EngineRuntime) : VideoKitHostApi {
    // ------------------------------------------------------------------ helpers

    private fun kit() = engine.kit ?: throw FlutterError("VIDEOKIT_NOT_INITIALIZED", "handshake must be the first call", null)

    /** Runs [block] off the main thread; maps unexpected failures with [onFailure]. */
    private suspend fun <T> work(onFailure: (Exception) -> T, block: suspend () -> T): T = withContext(engine.workDispatcher) {
        try {
            block()
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (protocol: FlutterError) {
            throw protocol
        } catch (failure: Exception) {
            onFailure(failure)
        }
    }

    private suspend fun command(sessionId: String, block: suspend (VideoKitSession) -> VideoKitCommandResult): CommandResultMsg {
        val holder = engine.sessions[sessionId] ?: return VideoKitCommandResult.SessionReleased.toMsg()
        return work(Mappers::internalFailure) { block(holder.session).toMsg() }
    }

    private suspend fun edit(projectId: String, block: suspend (VideoKitEditProject) -> EditCommandResult): EditResultMsg {
        val holder = engine.projects[projectId] ?: return EditCommandResult.ProjectReleased.toMsg()
        return work({ EditCommandResult.Rejected(Mappers.redacted(it)).toMsg() }) { block(holder.project).toMsg() }
    }

    private fun invalidArgument(what: String) =
        VideoKitStableError(ErrorCode.INVALID_ARGUMENT, ErrorStage.UNKNOWN, false, diagnostic = "INVALID_ARGUMENT:$what")

    private fun notShared() = VideoKitStableError(ErrorCode.SESSION_RELEASED, ErrorStage.BIND, false, diagnostic = "NOT_SHARED")

    private fun released() = VideoKitStableError(ErrorCode.SESSION_RELEASED, ErrorStage.EDIT, false, diagnostic = "PROJECT_RELEASED")

    /** Resolves `uri:` / `registered:` / `demo:` references (14 §8.3); `null` for unknown references. */
    @SuppressLint("UseKtx") // The plugin does not depend on androidx.core-ktx for one Uri.parse call.
    private fun resolveSource(msg: MediaSourceMsg): VideoKitMediaSource? {
        val ref = msg.sourceRef
        return when {
            ref.startsWith("uri:") -> MediaSources.fromUri(
                engine.context,
                Uri.parse(ref.removePrefix("uri:")),
                msg.mediaToken,
                msg.mediaKind.toKind(),
                msg.displayName,
                msg.mimeType,
            )

            ref.startsWith("registered:") -> VideoKitFlutter.registeredSource(ref.removePrefix("registered:"))?.let { msg.toSource(it) }

            ref.startsWith("demo:") ->
                engine.backend
                    ?.demoSource(ref.removePrefix("demo:"), msg.mediaToken, msg.mediaKind.toKind())
                    ?.copy(displayName = msg.displayName)

            else -> null
        }
    }

    private fun resolveSink(ref: String): VideoKitOutputSink? = when {
        ref.startsWith("registered:") -> VideoKitFlutter.registeredSink(ref.removePrefix("registered:"))
        ref == "demo:memory" -> engine.backend?.demoSink()
        else -> null
    }

    private fun registerSession(session: VideoKitSession, hostOwned: Boolean = false): String {
        engine.sessions[session.sessionId]?.let { return it.sessionId }
        val holder = SessionHolder(
            session.sessionId,
            session,
            engine.scope,
            engine.nowMs,
            engine.sessionFanout::send,
            engine.main,
            hostOwned,
        )
        engine.sessions[session.sessionId] = holder
        holder.start(onReleased = { engine.sessions.remove(session.sessionId)?.stop() })
        return session.sessionId
    }

    private fun registerProject(project: VideoKitEditProject): String {
        val holder = ProjectHolder(project.projectId, project, engine.scope, engine.editFanout::send)
        engine.projects[project.projectId] = holder
        holder.start()
        return project.projectId
    }

    // ------------------------------------------------------------------ handshake & capabilities

    override fun handshake(request: HandshakeRequest): HandshakeResponse {
        val backend = VideoKitFlutter.resolveBackend()
            ?: throw FlutterError(
                VideoKitFlutter.NO_BACKEND,
                "No VideoKit backend: call VideoKitFlutter.setBackend() in release builds",
                null,
            )
        val timeouts = runCatching {
            HostCallbackTimeouts(
                request.hostActionTimeoutMs,
                request.navigationTimeoutMs,
                request.recoveryDecisionTimeoutMs,
                request.notificationTimeoutMs,
            )
        }.getOrDefault(HostCallbackTimeouts())
        engine.ensureKit(backend, timeouts)
        return HandshakeResponse(CHANNEL_PROTOCOL_VERSION, NATIVE_KIT_VERSION, VideoKitApiVersion.CURRENT.toString(), backend.isDemo)
    }

    override suspend fun capabilities(request: CapabilityRequestMsg): CapabilitiesMsg {
        val kit = kit()
        return withContext(engine.workDispatcher) { kit.capabilities(request.toRequest(::resolveSource)).toMsg() }
    }

    // ------------------------------------------------------------------ sessions

    override fun createSession(config: SessionConfigMsg): CreateResultMsg = try {
        CreateResultMsg(id = registerSession(kit().createSession(config.toConfig())))
    } catch (failure: VideoKitException) {
        CreateResultMsg(error = failure.error.toMsg())
    }

    /** Observes a session the native host shared with `VideoKitFlutter.shareSession` (add-to-app, 14 §9.1). */
    override fun adoptSession(sessionId: String): CreateResultMsg {
        kit()
        val session = VideoKitFlutter.sharedSession(sessionId)
            ?: return CreateResultMsg(error = notShared().toMsg())
        return CreateResultMsg(id = registerSession(session, hostOwned = true))
    }

    override suspend fun bind(
        sessionId: String,
        source: MediaSourceMsg,
        initial: PlaybackStateMsg?,
        actions: List<HostActionMsg>,
    ): CommandResultMsg = command(sessionId) { session ->
        val resolved = resolveSource(source) ?: return@command VideoKitCommandResult.Rejected(invalidArgument("UNKNOWN_SOURCE_REF"))
        session.bind(resolved, initial?.toPlaybackState(), actions.map { it.toAction() })
    }

    override suspend fun play(sessionId: String): CommandResultMsg = command(sessionId) { it.execute(VideoKitCommand.Play) }

    override suspend fun pause(sessionId: String): CommandResultMsg = command(sessionId) { it.execute(VideoKitCommand.Pause) }

    override suspend fun seekTo(sessionId: String, positionUs: Long, mode: SeekModeMsg): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SeekTo(positionUs, mode.toMode())) }

    override suspend fun setSpeed(sessionId: String, speed: Double): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SetSpeed(speed.toFloat())) }

    override suspend fun setMuted(sessionId: String, muted: Boolean): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SetMuted(muted)) }

    override suspend fun setVolume(sessionId: String, volume: Double): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SetVolume(volume.toFloat())) }

    override suspend fun selectAudioTrack(sessionId: String, trackId: String?): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SelectAudioTrack(trackId)) }

    override suspend fun selectSubtitleTrack(sessionId: String, trackId: String?): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SelectSubtitleTrack(trackId)) }

    override suspend fun setTransform(sessionId: String, transform: TransformMsg): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SetTransform(transform.toTransform())) }

    override suspend fun setOrientation(sessionId: String, request: String): CommandResultMsg = command(sessionId) { session ->
        val value = enumValues<OrientationRequest>().firstOrNull { it.name == request }
            ?: return@command VideoKitCommandResult.Rejected(invalidArgument("ORIENTATION_REQUEST"))
        session.execute(VideoKitCommand.SetOrientation(value))
    }

    override suspend fun setFullscreen(sessionId: String, fullscreen: Boolean): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SetFullscreen(fullscreen)) }

    override suspend fun setVisibility(sessionId: String, visibility: String): CommandResultMsg = command(sessionId) { session ->
        val value = enumValues<SessionVisibility>().firstOrNull { it.name == visibility }
            ?: return@command VideoKitCommandResult.Rejected(invalidArgument("VISIBILITY"))
        session.execute(VideoKitCommand.SetVisibility(value))
    }

    override suspend fun setActiveAudio(sessionId: String, active: Boolean, audioEpoch: Long): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SetActiveAudio(active, audioEpoch)) }

    override suspend fun hideContentForLock(sessionId: String, hidden: Boolean): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.HideContentForLock(hidden)) }

    override suspend fun setLooping(sessionId: String, looping: Boolean): CommandResultMsg =
        command(sessionId) { it.execute(VideoKitCommand.SetLooping(looping)) }

    override suspend fun requestHostAction(sessionId: String, actionId: String): CommandResultMsg =
        command(sessionId) { it.requestHostAction(actionId) }

    override suspend fun requestNavigation(sessionId: String, direction: String): String {
        val holder = engine.sessions[sessionId] ?: return NavigationResult.UNAVAILABLE.name
        val value = enumValues<NavigationDirection>().firstOrNull { it.name == direction } ?: return NavigationResult.UNAVAILABLE.name
        return work({ NavigationResult.FAILED.name }) { holder.session.requestNavigation(value).name }
    }

    override fun setControlsVisible(sessionId: String, visible: Boolean) {
        engine.sessions[sessionId]?.session?.setControlsVisible(visible)
    }

    override suspend fun updateHostActions(sessionId: String, actions: List<HostActionMsg>) {
        val holder = engine.sessions[sessionId] ?: return
        work({ }) { holder.session.updateHostActions(actions.map { it.toAction() }) }
    }

    override suspend fun captureState(sessionId: String): PlaybackStateMsg? {
        val holder = engine.sessions[sessionId] ?: return null
        return work({ null }) { holder.session.captureState().toMsg() }
    }

    override suspend fun release(sessionId: String): PlaybackStateMsg? {
        val holder = engine.sessions[sessionId] ?: return null
        if (holder.hostOwned) {
            // The host owns the session: stop observing it in this engine and hand back its current state.
            engine.sessions.remove(sessionId)?.stop()
            return work({ null }) { holder.session.captureState().toMsg() }
        }
        return work({ null }) { holder.session.release().toMsg() }
    }

    // ------------------------------------------------------------------ textures

    override fun createTexture(sessionId: String, width: Long, height: Long): Long {
        val holder = engine.sessions[sessionId] ?: return -1L
        val registry = engine.textures ?: return -1L
        holder.texture?.let { return it.textureId }
        val binding = TextureBinding(registry, holder.session, width.toInt(), height.toInt()) { textureId ->
            engine.notifyTextureChanged(sessionId, textureId)
        }
        if (binding.attach() !is VideoKitCommandResult.Executed) {
            binding.dispose()
            return -1L
        }
        holder.texture = binding
        return binding.textureId
    }

    override fun resizeTexture(sessionId: String, width: Long, height: Long) {
        engine.sessions[sessionId]?.texture?.resize(width.toInt(), height.toInt())
    }

    override fun disposeTexture(sessionId: String) {
        val holder = engine.sessions[sessionId] ?: return
        holder.texture?.dispose()
        holder.texture = null
    }

    // ------------------------------------------------------------------ edit projects

    override fun createEditProject(config: EditProjectConfigMsg): CreateResultMsg = try {
        CreateResultMsg(id = registerProject(kit().createEditProject(config.toConfig())))
    } catch (failure: VideoKitException) {
        CreateResultMsg(error = failure.error.toMsg())
    }

    override suspend fun restoreEditProject(serialized: SerializedProjectMsg, config: EditProjectConfigMsg): CreateResultMsg {
        val kit = kit()
        return work({ CreateResultMsg(error = Mappers.redacted(it).toMsg()) }) {
            try {
                CreateResultMsg(id = registerProject(kit.restoreEditProject(serialized.toSerialized(), config.toConfig())))
            } catch (failure: VideoKitException) {
                CreateResultMsg(error = failure.error.toMsg())
            }
        }
    }

    override suspend fun addSource(projectId: String, source: MediaSourceMsg): CreateResultMsg {
        val holder = engine.projects[projectId] ?: return CreateResultMsg(error = released().toMsg())
        return work({ CreateResultMsg(error = Mappers.redacted(it).toMsg()) }) {
            val resolved = resolveSource(source) ?: return@work CreateResultMsg(error = invalidArgument("UNKNOWN_SOURCE_REF").toMsg())
            try {
                CreateResultMsg(id = holder.project.addSource(resolved).sourceId)
            } catch (failure: VideoKitException) {
                CreateResultMsg(error = failure.error.toMsg())
            }
        }
    }

    override suspend fun applyEdit(projectId: String, command: EditCommandMsg): EditResultMsg = edit(projectId) { project ->
        val parsed = command.toCommand() ?: return@edit EditCommandResult.Rejected(invalidArgument("EDIT_COMMAND:${command.kind}"))
        project.apply(parsed)
    }

    override suspend fun undo(projectId: String): EditResultMsg = edit(projectId) { it.undo() }

    override suspend fun redo(projectId: String): EditResultMsg = edit(projectId) { it.redo() }

    override suspend fun snapshot(projectId: String): SerializedProjectMsg? {
        val holder = engine.projects[projectId] ?: return null
        return work({ null }) { holder.project.snapshot().toMsg() }
    }

    override fun previewSession(projectId: String): CreateResultMsg {
        val holder = engine.projects[projectId] ?: return CreateResultMsg(error = released().toMsg())
        return try {
            CreateResultMsg(id = registerSession(holder.project.previewSession()))
        } catch (failure: VideoKitException) {
            CreateResultMsg(error = failure.error.toMsg())
        }
    }

    override suspend fun checkExport(projectId: String, request: ExportRequestMsg): PrecheckMsg {
        val holder = engine.projects[projectId]
        val sink = resolveSink(request.sinkRef)
        if (holder == null || sink == null) {
            val problem = if (holder == null) released() else invalidArgument("UNKNOWN_SINK_REF")
            return PrecheckMsg(false, null, 0L, null, listOf(problem.toMsg()), emptyList(), emptyList())
        }
        return work({ PrecheckMsg(false, null, 0L, null, listOf(Mappers.redacted(it).toMsg()), emptyList(), emptyList()) }) {
            holder.project.checkExport(request.toRequest(), sink).toMsg()
        }
    }

    override suspend fun exportProject(projectId: String, request: ExportRequestMsg): ExportResultMsg {
        val holder = engine.projects[projectId]
        val sink = resolveSink(request.sinkRef)
        if (holder == null || sink == null) {
            val problem = if (holder == null) released() else invalidArgument("UNKNOWN_SINK_REF")
            return VideoKitExportResult.Failed(request.exportId, problem).toMsg()
        }
        return work({ VideoKitExportResult.Failed(request.exportId, Mappers.redacted(it)).toMsg() }) {
            try {
                holder.project.export(request.toRequest(), sink).toMsg()
            } catch (failure: VideoKitException) {
                VideoKitExportResult.Failed(request.exportId, failure.error).toMsg()
            }
        }
    }

    override suspend fun cancelExport(projectId: String, exportId: String) {
        val holder = engine.projects[projectId] ?: return
        work({ }) { holder.project.cancelExport(exportId) }
    }

    override suspend fun detectCandidates(projectId: String, atUs: Long): CandidateResultMsg {
        val holder = engine.projects[projectId] ?: return CandidateResultMsg(emptyList(), released().toMsg())
        return work({ CandidateResultMsg(emptyList(), Mappers.redacted(it).toMsg()) }) { holder.project.detectCandidates(atUs).toMsg() }
    }

    override suspend fun closeEditProject(projectId: String) {
        val holder = engine.projects.remove(projectId) ?: return
        holder.project.close()
        holder.stop()
    }

    override suspend fun closeAll() {
        work({ }) {
            engine.sessions.values.toList().forEach { holder ->
                if (holder.hostOwned) engine.sessions.remove(holder.sessionId)?.stop() else holder.session.release()
            }
            engine.projects.values.toList().forEach { holder ->
                holder.project.close()
                holder.stop()
            }
            engine.projects.clear()
        }
    }
}
