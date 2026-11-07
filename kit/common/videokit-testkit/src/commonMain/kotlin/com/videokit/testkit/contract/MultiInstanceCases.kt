package com.videokit.testkit.contract

import com.videokit.api.ErrorCode
import com.videokit.api.NoticeCodes
import com.videokit.api.ResourceKind
import com.videokit.api.SessionPhase
import com.videokit.api.SessionVisibility
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.core.runtime.DefaultResourceBudget
import com.videokit.testkit.CountingSourceFactory
import com.videokit.testkit.RecordingHostCallbacks

/**
 * Multi-instance cases of 07 §6 / 11 (1, 4, 9, 12 slots, unique audio and epochs, visibility policy, budget without
 * creation loops, single slot failure isolation, stable release). Each slot is an independent session.
 */
internal fun multiInstanceCases(): List<ContractCase> = listOf(
    multi("multi.slots_1_4_9_12", "1, 4, 9 and 12 slots bind and play independently; a 13th session is refused") {
        for (count in listOf(1, 4, 9, 12)) {
            val slots = (0 until count).map { boundCounted("slot$count-$it") }
            slots.forEachIndexed { index, (session, _) ->
                if (index % 2 == 0) expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Play), "play slot $index")
            }
            slots.forEachIndexed { index, (session, _) ->
                val expected = if (index % 2 == 0) SessionPhase.PLAYING else SessionPhase.READY
                awaitState(session.state, what = "slot $index of $count") { it.phase == expected }
                expect(session.state.value.resourcesHeld) { "slot $index of $count holds no resources" }
            }
            if (count == 12) {
                val refused = runCatching { kit.createSession(VideoKitSessionConfig()) }.exceptionOrNull()
                expectEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, (refused as? VideoKitException)?.error?.code, "13th session")
            }
            releaseAll(slots)
        }
    },
    multi(
        "multi.mixed_slots_independent",
        "video, static and animated image slots keep independent states",
        setOf(ContractFeature.IMAGES),
    ) {
        val video = boundCounted("mix-video").first
        val image = kit.createSession(VideoKitSessionConfig())
        expectEquals(VideoKitCommandResult.Executed, image.bind(subject.playableImage("mix-image"), null, emptyList()), "bind image")
        val animatedSource = subject.playableAnimatedImage("mix-anim")
        val animated = animatedSource?.let { source ->
            kit.createSession(VideoKitSessionConfig()).also {
                expectEquals(VideoKitCommandResult.Executed, it.bind(source, null, emptyList()), "bind animation")
            }
        }
        awaitState(image.state, what = "image READY") { it.phase == SessionPhase.READY }
        video.execute(VideoKitCommand.Play)
        animated?.let {
            awaitState(it.state, what = "animation READY") { state -> state.phase == SessionPhase.READY }
            it.execute(VideoKitCommand.Play)
        }
        video.execute(VideoKitCommand.Pause)
        expectEquals(SessionPhase.PAUSED, video.state.value.phase, "video")
        expectEquals(SessionPhase.READY, image.state.value.phase, "static image")
        animated?.let { awaitState(it.state, what = "animation PLAYING") { state -> state.phase == SessionPhase.PLAYING } }
        listOfNotNull(video, image, animated).forEach { it.release() }
    },
    multi("multi.unique_audio_epochs", "one audible session per epoch; switching mutes first; stale epochs are refused") {
        val a = boundCounted("audio-a").first
        val b = boundCounted("audio-b").first
        expectEquals(VideoKitCommandResult.Executed, a.execute(VideoKitCommand.SetActiveAudio(true, 1L)), "A active @1")
        expectEquals(VideoKitCommandResult.Executed, b.execute(VideoKitCommand.SetActiveAudio(false, 1L)), "B muted @1")
        // Switch: the old one is muted first, then the new one is enabled (07 §4).
        expectEquals(VideoKitCommandResult.Executed, a.execute(VideoKitCommand.SetActiveAudio(false, 2L)), "A muted @2")
        expectEquals(VideoKitCommandResult.Executed, b.execute(VideoKitCommand.SetActiveAudio(true, 2L)), "B active @2")
        // The command of epoch 1 arriving late must not make A audible again.
        expect(a.execute(VideoKitCommand.SetActiveAudio(true, 1L)) is VideoKitCommandResult.Rejected) { "stale epoch accepted" }
        expect(!a.state.value.activeAudio && b.state.value.activeAudio) {
            "audible: A=${a.state.value.activeAudio} B=${b.state.value.activeAudio}"
        }
        // The audible slot goes away: everything silent until the host chooses again.
        b.release()
        expect(!a.state.value.activeAudio) { "A became audible on its own" }
        a.release()
    },
    multi("multi.slot_failure_isolated", "a failing slot does not affect the other slots") {
        val healthy = (0 until 3).map { boundCounted("healthy-$it").first }
        healthy.forEach { it.execute(VideoKitCommand.Play) }
        val failing = kit.createSession(VideoKitSessionConfig())
        if (subject.driveToFatalError(failing)) {
            expectEquals(SessionPhase.ERROR_FATAL, failing.state.value.phase, "failing slot")
        }
        healthy.forEachIndexed { index, session ->
            awaitState(session.state, what = "healthy slot $index PLAYING") { it.phase == SessionPhase.PLAYING }
            expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Pause), "pause healthy $index")
        }
        (healthy + failing).forEach { it.release() }
    },
    multi("multi.offscreen_pauses_and_resumes", "leaving the screen pauses a playing slot; returning resumes it") {
        val session = boundCounted("offscreen-resume").first
        session.execute(VideoKitCommand.Play)
        expectEquals(
            VideoKitCommandResult.Executed,
            session.execute(VideoKitCommand.SetVisibility(SessionVisibility.OFFSCREEN)),
            "offscreen",
        )
        expectEquals(SessionPhase.PAUSED, session.state.value.phase, "offscreen phase")
        expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SetVisibility(SessionVisibility.VISIBLE)), "visible")
        awaitState(session.state, what = "PLAYING again") { it.phase == SessionPhase.PLAYING }
        // Partly visible keeps playing (04A V1, 07 §3).
        expectEquals(
            VideoKitCommandResult.Executed,
            session.execute(VideoKitCommand.SetVisibility(SessionVisibility.PARTIALLY_VISIBLE)),
            "partially visible",
        )
        expectEquals(SessionPhase.PLAYING, session.state.value.phase, "partially visible phase")
        expectEquals(SessionVisibility.PARTIALLY_VISIBLE, session.state.value.visibility, "visibility")
        // The content lock wins over every visibility (06 §4.2).
        session.execute(VideoKitCommand.HideContentForLock(true))
        session.execute(VideoKitCommand.SetVisibility(SessionVisibility.VISIBLE))
        expect(session.state.value.hiddenForLock && !session.state.value.activeAudio) { "lock lost on visibility: ${session.state.value}" }
        session.execute(VideoKitCommand.HideContentForLock(false))
        // A paused slot stays paused.
        session.execute(VideoKitCommand.Pause)
        session.execute(VideoKitCommand.SetVisibility(SessionVisibility.OFFSCREEN))
        session.execute(VideoKitCommand.SetVisibility(SessionVisibility.VISIBLE))
        expectEquals(SessionPhase.PAUSED, session.state.value.phase, "paused slot after visible")
        session.release()
    },
    multi("multi.offscreen_release_keeps_state", "an off-screen slot releases its decoder later and reopens it at the kept state") {
        val (session, factory) = boundCounted("offscreen-release")
        val events = record(session.events)
        expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SeekTo(2_000_000L)), "seek")
        session.execute(VideoKitCommand.SetSpeed(1.5f))
        session.execute(VideoKitCommand.SetVisibility(SessionVisibility.OFFSCREEN))
        val wait = subject.offscreenReleaseMs + defaultWaitMs
        awaitState(session.state, timeoutMs = wait, what = "decoder released") { !it.resourcesHeld }
        eventually("read handles closed while off screen") { factory.openHandles == 0 }
        val kept = session.state.value
        expectEquals(SessionPhase.READY, kept.phase, "phase while released")
        expectEquals(2_000_000L, kept.positionUs, "position while released")
        // Still bound: no SourceReleased, and seeking while released keeps the position for the reopen.
        expect(events.values.none { it is VideoKitEvent.SourceReleased }) { "SourceReleased while still bound" }
        expectEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SeekTo(3_000_000L)), "seek while released")
        session.execute(VideoKitCommand.SetVisibility(SessionVisibility.VISIBLE))
        val reopened = awaitState(session.state, what = "decoder reopened") { it.resourcesHeld }
        expectEquals(3_000_000L, reopened.positionUs, "position after reopen")
        expectEquals(1.5f, reopened.speed, "speed after reopen")
        session.release()
        eventually("handles closed after release") { factory.openHandles == 0 }
    },
    multi(
        "multi.budget_denied_without_creation",
        "a denied decoder reservation creates nothing, does not retry, and the report returns to zero",
        setOf(ContractFeature.BUDGET_INJECTION),
    ) {
        val budget = DefaultResourceBudget(mapOf(ResourceKind.VIDEO_DECODER to 2))
        val limited = subject.create(RecordingHostCallbacks(), budget) ?: return@multi
        try {
            val first = boundCounted("budget-1", limited)
            val second = boundCounted("budget-2", limited)
            val (third, thirdFactory) = countedVideo("budget-3")
            val denied = limited.createSession(VideoKitSessionConfig())
            val result = denied.bind(third, null, emptyList())
            expectEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, (result as? VideoKitCommandResult.Rejected)?.error?.code, "third bind")
            expectEquals(0, thirdFactory.openCount, "handles opened for the denied slot (reserve before create)")
            // Released capacity is used by the next explicit attempt only.
            first.first.release()
            expectEquals(VideoKitCommandResult.Executed, denied.bind(third, null, emptyList()), "bind after a release")
            // Resume denied: an off-screen slot that lost its decoder stays released and reports it, without loops.
            second.first.execute(VideoKitCommand.SetVisibility(SessionVisibility.OFFSCREEN))
            awaitState(second.first.state, timeoutMs = subject.offscreenReleaseMs + defaultWaitMs, what = "slot 2 released") {
                !it.resourcesHeld
            }
            val taker = boundCounted("budget-4", limited)
            val opensBefore = second.second.openCount
            val errors = record(second.first.events)
            second.first.execute(VideoKitCommand.SetVisibility(SessionVisibility.VISIBLE))
            eventually("resume denial reported") { errors.values.any { it is VideoKitEvent.ErrorRaised } }
            expect(errors.values.contains(VideoKitEvent.TransientNotice(NoticeCodes.RESOURCE_DEGRADED))) { "no RESOURCE_DEGRADED notice" }
            expect(!second.first.state.value.resourcesHeld) { "slot 2 holds a decoder beyond the limit" }
            val play = second.first.execute(VideoKitCommand.Play)
            expectEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, (play as? VideoKitCommandResult.Rejected)?.error?.code, "play while denied")
            expectEquals(opensBefore, second.second.openCount, "handles opened by denied resumes")
            listOf(second.first, denied, taker.first).forEach { it.release() }
            eventually("budget report returns to zero") {
                budget.snapshot().usages.all { it.held == 0 && it.consumers.isEmpty() }
            }
        } finally {
            limited.close()
        }
    },
)

private fun multi(id: String, description: String, requires: Set<ContractFeature> = emptySet(), body: suspend ContractScope.() -> Unit) =
    ContractCase(id, ContractGroup.MULTI_INSTANCE, description, requires, body)

private suspend fun ContractScope.boundCounted(token: String, target: VideoKit = kit): Pair<VideoKitSession, CountingSourceFactory> {
    val (source: VideoKitMediaSource, factory) = countedVideo(token)
    val session = target.createSession(VideoKitSessionConfig())
    expectEquals(VideoKitCommandResult.Executed, session.bind(source, null, emptyList()), "bind $token")
    awaitState(session.state, what = "READY ($token)") { it.phase == SessionPhase.READY }
    return session to factory
}

private suspend fun ContractScope.releaseAll(slots: List<Pair<VideoKitSession, CountingSourceFactory>>) {
    slots.forEach { it.first.release() }
    slots.forEachIndexed { index, (_, factory) -> eventually("slot $index handles closed") { factory.openHandles == 0 } }
}
