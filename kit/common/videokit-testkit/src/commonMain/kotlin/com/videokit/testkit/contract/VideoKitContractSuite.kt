package com.videokit.testkit.contract

import com.videokit.api.ActionPlacement
import com.videokit.api.CapabilityRequest
import com.videokit.api.EditCommandResult
import com.videokit.api.EditPhase
import com.videokit.api.EditProjectConfig
import com.videokit.api.ErrorCode
import com.videokit.api.FitMode
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionStatus
import com.videokit.api.HostIcon
import com.videokit.api.MaskRegion
import com.videokit.api.MaskType
import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationResult
import com.videokit.api.OrientationRequest
import com.videokit.api.SerializedEditProject
import com.videokit.api.SessionPhase
import com.videokit.api.SinkCapabilities
import com.videokit.api.SinkErrorCode
import com.videokit.api.SourceErrorCode
import com.videokit.api.SupportLevel
import com.videokit.api.TimeRangeUs
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitAbortReason
import com.videokit.api.VideoKitApiVersion
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitEditProject
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitExportRequest
import com.videokit.api.VideoKitExportResult
import com.videokit.api.VideoKitHostAction
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.testkit.CallbackMode
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.RecordingOutputSink
import com.videokit.testkit.SinkFault
import com.videokit.testkit.SourceBehavior
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope

/**
 * Contract test suite of 04 §11: the same cases run against every [com.videokit.api.VideoKit]
 * implementation (Kotlin Fake on the JVM, real implementation on devices). Framework neutral: a runner
 * calls [run] for every case in [cases], for example from a parameterized JUnit test inside `runTest`.
 */
public object VideoKitContractSuite {
    /** All cases. */
    public val cases: List<ContractCase> = buildList {
        addAll(versionCases())
        addAll(stateMachineCases())
        addAll(commandCases())
        addAll(cancellationCases())
        addAll(releaseCases())
        addAll(isolationCases())
        addAll(faultCases())
        addAll(snapshotCases())
        addAll(multiInstanceCases())
        addAll(mediaInfoCases())
    }

    /** Runs [case] against [subject]; [background] hosts recorders and is cancelled by the caller. */
    public suspend fun run(case: ContractCase, subject: VideoKitContractSubject, background: CoroutineScope) {
        val callbacks = RecordingHostCallbacks()
        val kit = subject.create(callbacks)
        try {
            ContractScope(subject, kit, callbacks, background).apply { case.body(this) }
        } finally {
            kit.close()
        }
    }

    /** Whether [case] applies to [subject] (it implements every feature area the case requires). */
    public fun applies(case: ContractCase, subject: VideoKitContractSubject): Boolean = subject.features.containsAll(case.requires)

    private fun case(id: String, group: ContractGroup, description: String, body: suspend ContractScope.() -> Unit) =
        ContractCase(id, group, description, requirementsOf(id), body)

    private fun requirementsOf(id: String): Set<ContractFeature> = buildSet {
        if (id in imageCases()) add(ContractFeature.IMAGES)
        if (id in editingCases()) add(ContractFeature.EDITING)
    }

    // Functions, not properties: they are used while [cases] is initialized, before later properties exist.
    private fun imageCases() = setOf("state.image_rejects_video_commands")

    private fun editingCases() = setOf(
        "cancel.export",
        "cancel.export_caller",
        "release.edit_project",
        "faults.sink_open",
        "faults.sink_write",
        "faults.sink_capabilities",
        "faults.sink_space",
        "faults.export_success",
        "faults.edit_commands",
        "snapshot.edit_round_trip",
        "snapshot.future_major_rejected",
    )

    // ------------------------------------------------------------------ version & capabilities

    private fun versionCases() = listOf(
        case("version.major_is_1", ContractGroup.VERSION_AND_CAPABILITIES, "apiVersion is 1.x and compatible with 1.0.0") {
            expectEquals(1, kit.apiVersion.major, "apiVersion.major")
            expect(kit.apiVersion.isCompatibleWith(VideoKitApiVersion(1, 0, 0))) {
                "apiVersion ${kit.apiVersion} not compatible with 1.0.0"
            }
        },
        case(
            "capabilities.report",
            ContractGroup.VERSION_AND_CAPABILITIES,
            "capability report has a schema version and no probe without source",
        ) {
            val caps = kit.capabilities(CapabilityRequest())
            expect(caps.schemaVersion >= 1) { "schemaVersion ${caps.schemaVersion}" }
            expect(caps.mediaProbe == null) { "mediaProbe without source" }
        },
        case("capabilities.probe_source", ContractGroup.VERSION_AND_CAPABILITIES, "a capability request for a source probes it") {
            val (video, factory) = countedVideo("cap-video")
            val probe = kit.capabilities(CapabilityRequest(video)).mediaProbe ?: throw ContractViolation("no mediaProbe")
            expectEquals("cap-video", probe.mediaToken, "probe.mediaToken")
            expectEquals(SupportLevel.SUPPORTED, probe.playable, "probe.playable")
            eventually("probe handles closed") { factory.openHandles == 0 }
        },
        case(
            "capabilities.probe_failure",
            ContractGroup.VERSION_AND_CAPABILITIES,
            "a failing source is reported in the probe, not thrown",
        ) {
            val (video, _) = faultyVideo("cap-missing", SourceBehavior.FailOnOpen(SourceErrorCode.NOT_FOUND))
            val probe = kit.capabilities(CapabilityRequest(video)).mediaProbe ?: throw ContractViolation("no mediaProbe")
            expectEquals(SupportLevel.UNSUPPORTED, probe.playable, "probe.playable")
            expectEquals(ErrorCode.SOURCE_NOT_FOUND, probe.error?.code, "probe.error.code")
        },
        case(
            "errors.unknown_code_is_internal",
            ContractGroup.VERSION_AND_CAPABILITIES,
            "unknown error codes map to INTERNAL_ERROR_REDACTED",
        ) {
            expectEquals(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorCode.fromWireName("CODE_FROM_A_FUTURE_MINOR"), "fromWireName")
        },
    )

    // ------------------------------------------------------------------ state machine

    private fun stateMachineCases() = listOf(
        case("state.created", ContractGroup.STATE_MACHINE, "a new session is CREATED and holds no resources") {
            val a = kit.createSession(VideoKitSessionConfig())
            val b = kit.createSession(VideoKitSessionConfig())
            expectEquals(SessionPhase.CREATED, a.state.value.phase, "phase")
            expect(!a.state.value.resourcesHeld) { "resourcesHeld before bind" }
            expect(a.sessionId.isNotEmpty() && a.sessionId != b.sessionId) { "session ids must be unique and non-empty" }
        },
        case("state.bind_video_ready", ContractGroup.STATE_MACHINE, "binding a video reaches READY and holds resources") {
            val session = kit.createSession(VideoKitSessionConfig())
            val (video, _) = countedVideo("bind-video")
            expectEquals(VideoKitCommandResult.Executed, session.bind(video, null, emptyList()), "bind result")
            val state = awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
            expectEquals(com.videokit.api.MediaKind.VIDEO, state.mediaKind, "mediaKind")
            expect(state.resourcesHeld) { "resourcesHeld after bind" }
            expect((state.durationUs ?: 0L) > 0L) { "durationUs ${state.durationUs}" }
        },
        case("state.play_pause", ContractGroup.STATE_MACHINE, "READY → PLAYING ⇄ PAUSED and position advances while playing") {
            val session = boundVideo("play-pause")
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Play), "play")
            awaitState(session.state, what = "PLAYING") { it.phase == SessionPhase.PLAYING || it.phase == SessionPhase.BUFFERING }
            subject.advanceMediaTime(1_000_000L)
            awaitState(session.state, what = "position advanced") { it.positionUs > 0L }
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Pause), "pause")
            awaitState(session.state, what = "PAUSED") { it.phase == SessionPhase.PAUSED }
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Play), "resume")
            awaitState(session.state, what = "PLAYING again") { it.phase == SessionPhase.PLAYING || it.phase == SessionPhase.BUFFERING }
        },
        case("state.commands_before_bind_rejected", ContractGroup.STATE_MACHINE, "playback commands in CREATED are Rejected") {
            val session = kit.createSession(VideoKitSessionConfig())
            listOf(VideoKitCommand.Play, VideoKitCommand.Pause, VideoKitCommand.SeekTo(1_000L)).forEach { command ->
                val result = session.execute(command)
                expectEquals(ErrorCode.INVALID_STATE, (result as? VideoKitCommandResult.Rejected)?.error?.code, "$command before bind")
            }
            expectEquals(SessionPhase.CREATED, session.state.value.phase, "phase unchanged")
        },
        case(
            "state.image_rejects_video_commands",
            ContractGroup.STATE_MACHINE,
            "image sessions report video-only commands as Unsupported",
        ) {
            val session = kit.createSession(VideoKitSessionConfig())
            expectEquals(VideoKitCommandResult.Executed, session.bind(subject.playableImage("image-1"), null, emptyList()), "bind image")
            awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
            listOf(VideoKitCommand.SetSpeed(2f), VideoKitCommand.SeekTo(0L), VideoKitCommand.SelectAudioTrack(null)).forEach { command ->
                expectEquals(VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND), session.execute(command), "$command on image")
            }
            val snapshot = session.captureState()
            expect(snapshot.positionUs == null && snapshot.speed == null && snapshot.audioTrackId == null) {
                "video fields in image snapshot: $snapshot"
            }
        },
        case("state.rebind_releases_previous", ContractGroup.STATE_MACHINE, "re-binding releases the old source and emits SourceReleased") {
            val session = kit.createSession(VideoKitSessionConfig())
            val events = record(session.events)
            val (first, firstFactory) = countedVideo("rebind-a")
            val (second, _) = countedVideo("rebind-b")
            session.bind(first, null, emptyList())
            session.bind(second, null, emptyList())
            awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
            eventually("SourceReleased(rebind-a) event") { events.values.contains(VideoKitEvent.SourceReleased("rebind-a")) }
            eventually("onSourceReleased callback") { callbacks.sourceReleases.contains(session.sessionId to "rebind-a") }
            expectEquals(0, firstFactory.openHandles, "open handles of the old source")
        },
        case("state.playback_ends", ContractGroup.STATE_MACHINE, "playing to the end reaches ENDED; Play restarts") {
            val session = boundVideo("ends")
            val events = record(session.events)
            val duration = session.state.value.durationUs ?: throw ContractViolation("no duration")
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SeekTo(duration - 500_000L)), "seek near end")
            session.execute(VideoKitCommand.Play)
            subject.advanceMediaTime(1_000_000L)
            awaitState(session.state, what = "ENDED") { it.phase == SessionPhase.ENDED }
            eventually("PlaybackEnded event") { VideoKitEvent.PlaybackEnded in events.values }
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Play), "replay")
            awaitState(session.state, what = "PLAYING after ENDED") { it.phase == SessionPhase.PLAYING && it.positionUs < duration }
        },
    )

    // ------------------------------------------------------------------ command results

    private fun commandCases() = listOf(
        case(
            "command.rapid_seeks",
            ContractGroup.COMMAND_RESULTS,
            "rapid seeks: only the latest executes, earlier ones may be Superseded",
        ) {
            val session = boundVideo("seeks")
            val targets = listOf(1_000_000L, 1_500_000L, 2_000_000L)
            val results = coroutineScope { targets.map { target -> async { session.execute(VideoKitCommand.SeekTo(target)) } }.awaitAll() }
            results.forEach { expect(it == VideoKitCommandResult.Executed || it == VideoKitCommandResult.Superseded) { "seek result $it" } }
            expectEquals(VideoKitCommandResult.Executed, results.last(), "last seek result")
            awaitState(session.state, what = "final seek applied") { it.positionUs == targets.last() && it.seekingToUs == null }
        },
        case("command.invalid_arguments", ContractGroup.COMMAND_RESULTS, "invalid arguments are Rejected") {
            val session = boundVideo("invalid")
            listOf(
                VideoKitCommand.SetSpeed(-1f),
                VideoKitCommand.SetSpeed(Float.NaN),
                VideoKitCommand.SetVolume(2f),
                VideoKitCommand.SelectAudioTrack("no-such-track"),
                VideoKitCommand.SelectSubtitleTrack("no-such-track"),
                VideoKitCommand.SeekTo(-5L),
            ).forEach { command ->
                val result = session.execute(command)
                expectEquals(ErrorCode.INVALID_ARGUMENT, (result as? VideoKitCommandResult.Rejected)?.error?.code, "$command")
            }
        },
        case("command.settings_round_trip", ContractGroup.COMMAND_RESULTS, "setting commands are Executed and reflected in state") {
            val session = boundVideo("settings")
            val second = session.state.value.audioTracks.getOrNull(1) ?: throw ContractViolation("subject video needs two audio tracks")
            listOf(
                VideoKitCommand.SetSpeed(1.5f),
                VideoKitCommand.SetMuted(true),
                VideoKitCommand.SetVolume(0.5f),
                VideoKitCommand.SelectAudioTrack(second.id),
                VideoKitCommand.SelectSubtitleTrack(null),
                VideoKitCommand.SetTransform(com.videokit.api.MediaTransform(2f, 0.1f, -0.1f, 90, FitMode.FILL)),
                VideoKitCommand.SetOrientation(OrientationRequest.LANDSCAPE),
                VideoKitCommand.SetFullscreen(true),
                VideoKitCommand.SetVisibility(com.videokit.api.SessionVisibility.OFFSCREEN),
            ).forEach { expectEquals(VideoKitCommandResult.Executed, session.execute(it), "$it") }
            val state = session.state.value
            expect(state.speed == 1.5f && state.muted && state.volume == 0.5f && state.selectedAudioTrackId == second.id) { "state $state" }
            expect(
                state.transform.scale == 2f && state.orientation.fullscreen && state.orientation.request == OrientationRequest.LANDSCAPE,
            ) {
                "state $state"
            }
        },
        case("command.stale_audio_epoch", ContractGroup.COMMAND_RESULTS, "SetActiveAudio with an older epoch is Rejected") {
            val session = boundVideo("epoch")
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SetActiveAudio(true, 5L)), "epoch 5")
            val stale = session.execute(VideoKitCommand.SetActiveAudio(false, 3L))
            expect(stale is VideoKitCommandResult.Rejected) { "stale epoch returned $stale" }
            expect(session.state.value.activeAudio) { "stale command changed activeAudio" }
        },
        case("command.lock_wins_over_audio", ContractGroup.COMMAND_RESULTS, "HideContentForLock silences and blocks audio activation") {
            val session = boundVideo("lock")
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.HideContentForLock(true)), "lock")
            expect(session.state.value.hiddenForLock && !session.state.value.activeAudio) { "locked state ${session.state.value}" }
            val activate = session.execute(VideoKitCommand.SetActiveAudio(true, 100L))
            expect(activate is VideoKitCommandResult.Rejected) { "audio activation while locked returned $activate" }
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.HideContentForLock(false)), "unlock")
            expect(!session.state.value.hiddenForLock) { "still hidden after unlock" }
        },
        case("command.host_action_pending_merged", ContractGroup.COMMAND_RESULTS, "repeated clicks on a pending host action are merged") {
            callbacks.hostActionAnswer = { HostActionResult(HostActionStatus.PENDING) }
            val session = kit.createSession(VideoKitSessionConfig())
            session.bind(subject.playableVideo("actions"), null, listOf(tagAction()))
            awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
            expectEquals(VideoKitCommandResult.Executed, session.requestHostAction("tag"), "first request")
            expect(session.state.value.hostActions.single().pending) { "action not pending" }
            expectEquals(VideoKitCommandResult.Superseded, session.requestHostAction("tag"), "second request while pending")
            expectEquals(1, callbacks.hostActionRequests.size, "callback invocations")
            session.updateHostActions(listOf(tagAction().copy(pending = false, selected = true)))
            expect(!session.state.value.hostActions.single().pending) { "still pending after host update" }
            callbacks.hostActionAnswer = { HostActionResult(HostActionStatus.COMPLETED) }
            expectEquals(VideoKitCommandResult.Executed, session.requestHostAction("tag"), "request after completion")
            expectEquals(2, callbacks.hostActionRequests.size, "callback invocations")
            expectEquals("actions", callbacks.hostActionRequests.first().mediaToken, "request mediaToken")
        },
        case(
            "command.attach_unknown_target",
            ContractGroup.COMMAND_RESULTS,
            "a foreign render target type is Unsupported(DEVICE_CAPABILITY)",
        ) {
            val session = boundVideo("foreign-target")
            val foreign = object : com.videokit.api.VideoKitSurfaceTarget {
                override val width: Int = 16
                override val height: Int = 9
            }
            expectEquals(
                VideoKitCommandResult.Unsupported(UnsupportedReason.DEVICE_CAPABILITY),
                session.attachSurface(foreign),
                "attach result",
            )
            session.release()
            expectEquals(VideoKitCommandResult.SessionReleased, session.attachSurface(foreign), "attach after release")
        },
        case("command.unknown_host_action", ContractGroup.COMMAND_RESULTS, "unknown host actions are Rejected without calling the host") {
            val session = boundVideo("unknown-action")
            val result = session.requestHostAction("nope")
            expect(result is VideoKitCommandResult.Rejected) { "unknown action returned $result" }
            expect(callbacks.hostActionRequests.isEmpty()) { "host was called" }
        },
        case("command.controls_and_navigation", ContractGroup.COMMAND_RESULTS, "controls visibility and navigation reach the host") {
            callbacks.navigationAnswer = { NavigationResult.ACCEPTED }
            val session = boundVideo("controls")
            session.setControlsVisible(false)
            expect(!session.state.value.controlsVisible) { "controlsVisible not updated" }
            eventually("onControlsVisibilityChanged") { callbacks.controlsVisibility.contains(session.sessionId to false) }
            expectEquals(NavigationResult.ACCEPTED, session.requestNavigation(NavigationDirection.NEXT), "navigation result")
            expectEquals(NavigationDirection.NEXT, callbacks.navigationRequests.single().direction, "navigation direction")
        },
    )

    // ------------------------------------------------------------------ cancellation & timeout

    private fun cancellationCases() = listOf(
        case(
            "cancel.bind_closes_handles",
            ContractGroup.CANCELLATION_AND_TIMEOUT,
            "cancelling bind closes every handle; the session can bind again",
        ) {
            val session = kit.createSession(VideoKitSessionConfig())
            val (hanging, factory) = faultyVideo("hang-bind", SourceBehavior.HangOnRead)
            val job = launchInBackground { session.bind(hanging, null, emptyList()) }
            eventually("bind started reading") { factory.readCount > 0 }
            job.cancel()
            job.join()
            eventually("handles closed after cancel") { factory.openHandles == 0 }
            expectEquals(VideoKitCommandResult.Executed, session.bind(subject.playableVideo("after-cancel"), null, emptyList()), "re-bind")
            awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
        },
        case("timeout.source_read", ContractGroup.CANCELLATION_AND_TIMEOUT, "a hanging source read times out as SOURCE_TIMEOUT") {
            val session = kit.createSession(VideoKitSessionConfig())
            val (hanging, factory) = faultyVideo("hang-read", SourceBehavior.HangOnRead)
            val result =
                within("bind with hanging source", subject.sourceTimeoutMs + defaultWaitMs) { session.bind(hanging, null, emptyList()) }
            expectEquals(ErrorCode.SOURCE_TIMEOUT, (result as? VideoKitCommandResult.Rejected)?.error?.code, "bind error")
            expectEquals(SessionPhase.ERROR_RECOVERABLE, session.state.value.phase, "phase")
            eventually("handles closed") { factory.openHandles == 0 }
        },
        case(
            "timeout.host_action_callback",
            ContractGroup.CANCELLATION_AND_TIMEOUT,
            "a hanging host action callback fails as HOST_CALLBACK_FAILED",
        ) {
            callbacks.overrideMode("onHostActionRequested", CallbackMode.HANG)
            val session = kit.createSession(VideoKitSessionConfig())
            val events = record(session.events)
            session.bind(subject.playableVideo("hang-action"), null, listOf(tagAction()))
            awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
            val result = within("host action with hanging callback", subject.callbackTimeouts.hostActionMs + defaultWaitMs) {
                session.requestHostAction("tag")
            }
            expectEquals(ErrorCode.HOST_CALLBACK_FAILED, (result as? VideoKitCommandResult.Rejected)?.error?.code, "result")
            expect(!session.state.value.hostActions.single().pending) { "still pending after timeout" }
            eventually("HostActionFailed event") { events.values.any { it is VideoKitEvent.HostActionFailed && it.actionId == "tag" } }
        },
        case(
            "cancel.export",
            ContractGroup.CANCELLATION_AND_TIMEOUT,
            "cancelExport aborts the sink, never marks ready, reaches CANCELLED",
        ) {
            val project = projectWithClip("cancel-export")
            val sink = RecordingOutputSink()
            val request = VideoKitExportRequest(exportId = "export-cancel")
            val outcome = kotlinx.coroutines.CompletableDeferred<VideoKitExportResult>()
            launchInBackground {
                outcome.complete(project.export(request, sink))
            }
            awaitState(project.state, what = "EXPORTING") { it.phase == EditPhase.EXPORTING }
            eventually("sink opened") { sink.handles.isNotEmpty() }
            project.cancelExport("export-cancel")
            val result = within("export to finish") { outcome.await() }
            expect(result is VideoKitExportResult.Cancelled && result.exportId == "export-cancel") { "export returned $result" }
            awaitState(project.state, what = "CANCELLED") { it.phase == EditPhase.CANCELLED }
            expect(sink.readyCalls.isEmpty()) { "markReady called after cancel" }
            expect(sink.abortCalls.any { it.second == VideoKitAbortReason.CANCELLED }) { "abort not called: ${sink.abortCalls}" }
        },
        case("cancel.export_caller", ContractGroup.CANCELLATION_AND_TIMEOUT, "cancelling the export caller aborts the sink") {
            val project = projectWithClip("caller-cancel")
            val sink = RecordingOutputSink()
            val job = launchInBackground { project.export(VideoKitExportRequest(exportId = "export-caller"), sink) }
            awaitState(project.state, what = "EXPORTING") { it.phase == EditPhase.EXPORTING }
            eventually("sink opened") { sink.handles.isNotEmpty() }
            job.cancel()
            job.join()
            eventually("sink aborted") { sink.abortCalls.isNotEmpty() }
            awaitState(project.state, what = "not exporting") { it.phase != EditPhase.EXPORTING && it.phase != EditPhase.CANCELLING }
            expect(sink.readyCalls.isEmpty()) { "markReady called after caller cancellation" }
        },
    )

    // ------------------------------------------------------------------ release

    private fun releaseCases() = listOf(
        case("release.idempotent", ContractGroup.RELEASE, "release is idempotent and later calls report SessionReleased") {
            val session = kit.createSession(VideoKitSessionConfig())
            val (video, factory) = countedVideo("release-1")
            session.bind(video, null, emptyList())
            awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
            val first = session.release()
            val second = session.release()
            expectEquals(first, second, "second release snapshot")
            expectEquals(SessionPhase.RELEASED, session.state.value.phase, "phase")
            expect(!session.state.value.resourcesHeld) { "resources held after release" }
            expectEquals(VideoKitCommandResult.SessionReleased, session.execute(VideoKitCommand.Play), "play after release")
            expectEquals(VideoKitCommandResult.SessionReleased, session.execute(VideoKitCommand.Release), "Release after release")
            expectEquals(VideoKitCommandResult.SessionReleased, session.bind(video, null, emptyList()), "bind after release")
            session.close()
            eventually("handles closed") { factory.openHandles == 0 }
            eventually("onSourceReleased") { callbacks.sourceReleases.contains(session.sessionId to "release-1") }
            eventually("final snapshot delivered") {
                callbacks.snapshots.any {
                    it.sessionId == session.sessionId &&
                        it.mediaToken == "release-1"
                }
            }
        },
        case("release.concurrent", ContractGroup.RELEASE, "concurrent release calls return the same snapshot") {
            val session = boundVideo("release-concurrent")
            val snapshots = coroutineScope { List(3) { async { session.release() } }.awaitAll() }
            expect(snapshots.distinct().size == 1) { "different snapshots $snapshots" }
        },
        case("release.during_bind", ContractGroup.RELEASE, "release during a slow bind completes and closes handles") {
            val session = kit.createSession(VideoKitSessionConfig())
            val (hanging, factory) = faultyVideo("release-bind", SourceBehavior.HangOnRead)
            val bind = kotlinx.coroutines.CompletableDeferred<VideoKitCommandResult>()
            launchInBackground { bind.complete(session.bind(hanging, null, emptyList())) }
            eventually("bind started reading") { factory.readCount > 0 }
            within("release during bind") { session.release() }
            expectEquals(VideoKitCommandResult.SessionReleased, within("bind result") { bind.await() }, "bind result")
            eventually("handles closed") { factory.openHandles == 0 }
        },
        case("release.kit_close", ContractGroup.RELEASE, "closing VideoKit releases its sessions; new sessions are refused") {
            val a = boundVideo("close-a")
            val b = boundVideo("close-b")
            kit.close()
            awaitState(a.state, what = "a RELEASED") { it.phase == SessionPhase.RELEASED }
            awaitState(b.state, what = "b RELEASED") { it.phase == SessionPhase.RELEASED }
            val refused = runCatching { kit.createSession(VideoKitSessionConfig()) }.exceptionOrNull()
            expect(refused is VideoKitException) { "createSession after close returned/threw $refused" }
        },
        case(
            "release.edit_project",
            ContractGroup.RELEASE,
            "closing an edit project is idempotent; later commands report ProjectReleased",
        ) {
            val project = projectWithClip("project-release")
            val preview = project.previewSession()
            project.close()
            project.close()
            awaitState(project.state, what = "RELEASED") { it.phase == EditPhase.RELEASED }
            expectEquals(EditCommandResult.ProjectReleased, project.apply(VideoKitEditCommand.RemoveClip("x")), "apply after close")
            awaitState(preview.state, what = "preview RELEASED") { it.phase == SessionPhase.RELEASED }
        },
    )

    // ------------------------------------------------------------------ callback isolation

    private fun isolationCases() = listOf(
        case("isolation.throwing_callbacks", ContractGroup.CALLBACK_ISOLATION, "throwing callbacks never break the session") {
            callbacks.mode = CallbackMode.THROW
            val session = kit.createSession(VideoKitSessionConfig())
            expectEquals(VideoKitCommandResult.Executed, session.bind(subject.playableVideo("throwing"), null, listOf(tagAction())), "bind")
            awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Play), "play")
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Pause), "pause")
            val action = session.requestHostAction("tag")
            expectEquals(ErrorCode.HOST_CALLBACK_FAILED, (action as? VideoKitCommandResult.Rejected)?.error?.code, "host action")
            expectEquals(NavigationResult.FAILED, session.requestNavigation(NavigationDirection.PREVIOUS), "navigation")
            session.setControlsVisible(false)
            within("release with throwing callbacks") { session.release() }
        },
        case(
            "isolation.hanging_callbacks",
            ContractGroup.CALLBACK_ISOLATION,
            "hanging notification callbacks never block commands or release",
        ) {
            callbacks.mode = CallbackMode.HANG
            val session = kit.createSession(VideoKitSessionConfig())
            within("bind with hanging callbacks") { session.bind(subject.playableVideo("hanging"), null, emptyList()) }
            awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
            within("commands with hanging callbacks") {
                session.execute(VideoKitCommand.Play)
                session.execute(VideoKitCommand.Pause)
                session.execute(VideoKitCommand.SetVisibility(com.videokit.api.SessionVisibility.BACKGROUND))
            }
            within("release with hanging callbacks") { session.release() }
        },
        case("isolation.session_failure", ContractGroup.CALLBACK_ISOLATION, "one failing session does not affect another") {
            val good = boundVideo("isolation-good")
            val bad = kit.createSession(VideoKitSessionConfig())
            val (broken, _) = faultyVideo("isolation-bad", SourceBehavior.FailOnOpen(SourceErrorCode.DISCONNECTED))
            val result = bad.bind(broken, null, emptyList())
            expect(result is VideoKitCommandResult.Rejected) { "bad bind returned $result" }
            expectEquals(SessionPhase.ERROR_RECOVERABLE, bad.state.value.phase, "bad phase")
            expectEquals(VideoKitCommandResult.Executed, good.execute(VideoKitCommand.Play), "good play")
            awaitState(good.state, what = "good PLAYING") { it.phase == SessionPhase.PLAYING || it.phase == SessionPhase.BUFFERING }
            eventually("recoverable error reported to host") {
                callbacks.recoverableErrors.any { it.code == ErrorCode.SOURCE_DISCONNECTED }
            }
        },
    )

    // ------------------------------------------------------------------ fault mapping

    private fun faultCases() = listOf(
        case("faults.source_codes", ContractGroup.FAULT_MAPPING, "classified source failures map to the matching stable codes") {
            SourceErrorCode.entries.forEach { code ->
                listOf(SourceBehavior.FailOnOpen(code), SourceBehavior.FailOnRead(code)).forEach { behavior ->
                    val session = kit.createSession(VideoKitSessionConfig())
                    val (video, factory) = faultyVideo("fault-${code.name}", behavior)
                    val result = session.bind(video, null, emptyList())
                    expectEquals(code.errorCode, (result as? VideoKitCommandResult.Rejected)?.error?.code, "$behavior")
                    expectEquals(code.errorCode, session.state.value.error?.code, "state error for $behavior")
                    eventually("handles closed for $behavior") { factory.openHandles == 0 }
                    session.release()
                }
            }
        },
        case(
            "faults.unclassified_source_redacted",
            ContractGroup.FAULT_MAPPING,
            "unclassified source failures are INTERNAL_ERROR_REDACTED without details",
        ) {
            val secret = "hunter2-secret"
            val session = kit.createSession(VideoKitSessionConfig())
            val (video, _) = faultyVideo("fault-unclassified", SourceBehavior.ThrowOnOpen(secret))
            val error =
                (session.bind(video, null, emptyList()) as? VideoKitCommandResult.Rejected)?.error
                    ?: throw ContractViolation("not rejected")
            expectEquals(ErrorCode.INTERNAL_ERROR_REDACTED, error.code, "code")
            val diagnostic = error.diagnostic.orEmpty()
            expect(secret !in diagnostic && "smb://" !in diagnostic && "nas" !in diagnostic) { "diagnostic leaks details: $diagnostic" }
        },
        case("faults.sink_open", ContractGroup.FAULT_MAPPING, "a sink that refuses to open maps to OUTPUT_PERMISSION_DENIED") {
            val project = projectWithClip("sink-open")
            val sink = RecordingOutputSink(fault = SinkFault.FailOnOpen(SinkErrorCode.PERMISSION_DENIED))
            val failure = (project.export(VideoKitExportRequest(), sink) as? VideoKitExportResult.Failed)?.error
            expectEquals(ErrorCode.OUTPUT_PERMISSION_DENIED, failure?.code, "export failure")
            awaitState(project.state, what = "FAILED") { it.phase == EditPhase.FAILED }
            expect(sink.readyCalls.isEmpty()) { "markReady called" }
        },
        case("faults.sink_write", ContractGroup.FAULT_MAPPING, "a sink write failure aborts the output and never marks it ready") {
            val project = projectWithClip("sink-write")
            val sink = RecordingOutputSink(fault = SinkFault.FailOnWrite(SinkErrorCode.SPACE_INSUFFICIENT, afterBytes = 1L))
            val failure = (project.export(VideoKitExportRequest(), sink) as? VideoKitExportResult.Failed)?.error
            expectEquals(ErrorCode.OUTPUT_SPACE_INSUFFICIENT, failure?.code, "export failure")
            expect(sink.readyCalls.isEmpty()) { "markReady called" }
            expectEquals(1, sink.abortCalls.size, "abort calls")
            expectEquals(VideoKitAbortReason.EXPORT_FAILED, sink.abortCalls.single().second, "abort reason")
        },
        case("faults.sink_capabilities", ContractGroup.FAULT_MAPPING, "a sink without any write mode fails before export starts") {
            val project = projectWithClip("sink-caps")
            val sink =
                RecordingOutputSink(capabilities = SinkCapabilities(sequentialWrite = false, randomWrite = false, fileDescriptor = false))
            val precheck = project.checkExport(VideoKitExportRequest(), sink)
            expect(!precheck.ok && precheck.problems.any { it.code == ErrorCode.OUTPUT_CAPABILITY_UNSUPPORTED }) { "precheck $precheck" }
            val failure = (project.export(VideoKitExportRequest(), sink) as? VideoKitExportResult.Failed)?.error
            expectEquals(ErrorCode.OUTPUT_CAPABILITY_UNSUPPORTED, failure?.code, "export failure")
            expect(sink.openRequests.isEmpty()) { "sink opened despite failed precheck" }
        },
        case("faults.sink_space", ContractGroup.FAULT_MAPPING, "known insufficient free space fails the precheck") {
            val project = projectWithClip("sink-space")
            val sink =
                RecordingOutputSink(capabilities = SinkCapabilities(sequentialWrite = true, randomWrite = true, knownFreeSpaceBytes = 1L))
            val precheck = project.checkExport(VideoKitExportRequest(), sink)
            expect(!precheck.ok && precheck.problems.any { it.code == ErrorCode.OUTPUT_SPACE_INSUFFICIENT }) { "precheck $precheck" }
        },
        case("faults.export_success", ContractGroup.FAULT_MAPPING, "a successful export marks the output ready exactly once") {
            val project = projectWithClip("export-ok")
            val sink = RecordingOutputSink()
            val result = within("export") { project.export(VideoKitExportRequest(exportId = "export-ok"), sink) }
            val succeeded = result as? VideoKitExportResult.Succeeded ?: throw ContractViolation("export returned $result")
            expectEquals(1, sink.readyCalls.size, "markReady calls")
            expect(sink.abortCalls.isEmpty()) { "abort called on success" }
            expectEquals("export-ok", succeeded.exportId, "exportId")
            expect(succeeded.media.sourceTokens == listOf("export-ok")) { "sourceTokens ${succeeded.media.sourceTokens}" }
            expectEquals(project.state.value.timeline.durationUs, succeeded.media.durationUs, "durationUs")
            expectEquals(kit.isDemo, succeeded.media.isDemo, "isDemo")
            awaitState(project.state, what = "COMPLETED") { it.phase == EditPhase.COMPLETED }
        },
        case("faults.edit_commands", ContractGroup.FAULT_MAPPING, "invalid edit commands are Rejected; undo/redo restore the timeline") {
            val project = kit.createEditProject(EditProjectConfig())
            val token = project.addSource(subject.playableVideo("edit"))
            val duration = project.state.value.timeline.sources.single().probe?.durationUs ?: throw ContractViolation("no probe")
            expect(project.apply(VideoKitEditCommand.AddClip("no-source", 0L, 1_000L)) is EditCommandResult.Rejected) {
                "unknown source accepted"
            }
            expect(project.apply(VideoKitEditCommand.AddClip(token.sourceId, 0L, duration + 1L)) is EditCommandResult.Rejected) {
                "out of range accepted"
            }
            expect(project.undo() is EditCommandResult.Rejected) { "undo with empty stack accepted" }
            val applied = project.apply(VideoKitEditCommand.AddClip(token.sourceId, 0L, duration / 2))
            expect(applied is EditCommandResult.Applied) { "valid clip returned $applied" }
            expect(project.state.value.canUndo && project.state.value.timeline.clips.size == 1) { "state ${project.state.value}" }
            expect(project.undo() is EditCommandResult.Applied && project.state.value.timeline.clips.isEmpty()) { "undo failed" }
            expect(project.redo() is EditCommandResult.Applied && project.state.value.timeline.clips.size == 1) { "redo failed" }
        },
    )

    // ------------------------------------------------------------------ snapshots

    private fun snapshotCases() = listOf(
        case("snapshot.playback_round_trip", ContractGroup.SNAPSHOT_COMPATIBILITY, "a playback snapshot restored with bind round-trips") {
            val probe = boundVideo("snapshot-probe")
            val secondTrack =
                probe.state.value.audioTracks.getOrNull(1)?.id ?: throw ContractViolation("subject video needs two audio tracks")
            probe.release()
            val initial = VideoKitPlaybackState(
                zoom = 2f,
                panX = 0.1f,
                panY = -0.2f,
                rotationDeg = 90,
                fitMode = FitMode.FILL,
                preferredOrientation = OrientationRequest.PORTRAIT,
                fullscreen = true,
                positionUs = 1_000_000L,
                speed = 1.5f,
                volume = 0.5f,
                muted = true,
                audioTrackId = secondTrack,
            )
            val session = kit.createSession(VideoKitSessionConfig())
            session.bind(subject.playableVideo("snapshot"), initial, emptyList())
            awaitState(session.state, what = "READY") { it.phase == SessionPhase.READY }
            val captured = session.captureState()
            expectEquals(VideoKitPlaybackState.CURRENT_SCHEMA_VERSION, captured.schemaVersion, "schemaVersion")
            expectEquals("snapshot", captured.mediaToken, "mediaToken")
            val restoredFields = listOf(
                captured.zoom, captured.panX, captured.panY, captured.rotationDeg, captured.fitMode, captured.preferredOrientation,
                captured.fullscreen, captured.positionUs, captured.speed, captured.volume, captured.muted, captured.audioTrackId,
            )
            val expectedFields = listOf(
                initial.zoom, initial.panX, initial.panY, initial.rotationDeg, initial.fitMode, initial.preferredOrientation,
                initial.fullscreen, initial.positionUs, initial.speed, initial.volume, initial.muted, initial.audioTrackId,
            )
            expectEquals(expectedFields, restoredFields, "restored fields")
        },
        case("snapshot.edit_round_trip", ContractGroup.SNAPSHOT_COMPATIBILITY, "an edit project snapshot restores clips and masks") {
            val project = projectWithClip("edit-snapshot")
            val duration = project.state.value.timeline.durationUs
            val mask = project.apply(
                VideoKitEditCommand.AddMask(
                    MaskType.MANUAL,
                    MaskRegion(0.1f, 0.2f, 0.3f, 0.25f),
                    TimeRangeUs(0L, duration / 2),
                    strength = 0.75f,
                ),
            )
            expect(mask is EditCommandResult.Applied) { "mask returned $mask" }
            val snapshot = project.snapshot()
            expectEquals(SerializedEditProject.CURRENT_SCHEMA_VERSION, snapshot.schemaVersion, "schemaVersion")
            val restored = kit.restoreEditProject(snapshot, EditProjectConfig())
            expectEquals(project.state.value.timeline.clips, restored.state.value.timeline.clips, "clips")
            expectEquals(project.state.value.masks, restored.state.value.masks, "masks")
            expectEquals(
                project.state.value.timeline.sources.map {
                    it.mediaToken
                },
                restored.state.value.timeline.sources.map { it.mediaToken },
                "sources",
            )
        },
        case(
            "snapshot.future_major_rejected",
            ContractGroup.SNAPSHOT_COMPATIBILITY,
            "a snapshot of an unknown future major version is rejected",
        ) {
            val project = projectWithClip("future")
            val future = project.snapshot().let { it.copy(schemaVersion = it.schemaVersion + 1) }
            val failure = runCatching { kit.restoreEditProject(future, EditProjectConfig()) }.exceptionOrNull()
            expectEquals(ErrorCode.UNSUPPORTED_SNAPSHOT_VERSION, (failure as? VideoKitException)?.error?.code, "future snapshot error")
        },
    )

    // ------------------------------------------------------------------ helpers

    private suspend fun ContractScope.boundVideo(token: String): VideoKitSession {
        val session = kit.createSession(VideoKitSessionConfig())
        val result = session.bind(subject.playableVideo(token), null, emptyList())
        expectEquals(VideoKitCommandResult.Executed, result, "bind $token")
        awaitState(session.state, what = "READY ($token)") { it.phase == SessionPhase.READY }
        return session
    }

    private suspend fun ContractScope.projectWithClip(token: String): VideoKitEditProject {
        val project = kit.createEditProject(EditProjectConfig())
        val source: VideoKitMediaSource = subject.playableVideo(token)
        val sourceToken = project.addSource(source)
        val duration = project.state.value.timeline.sources.first { it.sourceId == sourceToken.sourceId }.probe?.durationUs
            ?: throw ContractViolation("no probe for $token")
        val result = project.apply(VideoKitEditCommand.AddClip(sourceToken.sourceId, 0L, minOf(duration, 3_000_000L)))
        expect(result is EditCommandResult.Applied) { "AddClip returned $result" }
        return project
    }

    private fun tagAction() = VideoKitHostAction(
        actionId = "tag",
        labelKey = "action.tag",
        contentDescriptionKey = "action.tag.description",
        icon = HostIcon.BuiltIn("tag"),
        placement = ActionPlacement.PRIMARY_BAR,
    )
}
