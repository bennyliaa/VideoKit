package com.videokit.testkit.contract

import com.videokit.api.SessionPhase
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSessionConfig
import com.videokit.testkit.CountingSourceFactory
import com.videokit.testkit.SourceBehavior

/** Media info cases (04A P2; TEST-R2 R2-06: the file size comes from the host source after bind). */
internal fun mediaInfoCases(): List<ContractCase> = listOf(
    ContractCase(
        "state.media_info_file_size",
        ContractGroup.STATE_MACHINE,
        "after bind, mediaInfo.fileSizeBytes is the size of the host source even when the descriptor has no length",
        emptySet(),
    ) {
        val expected = SourceBehavior.DEMO_BYTES.size.toLong()
        val media = buildList {
            add("video" to subject.playableVideo("size-video"))
            if (ContractFeature.IMAGES in subject.features) add("image" to subject.playableImage("size-image"))
        }
        for ((what, base) in media) {
            // The host knows the size only from the opened handle (the App passes no knownLength).
            val source: VideoKitMediaSource = base.copy(knownLength = null, sourceFactory = CountingSourceFactory())
            val session = kit.createSession(VideoKitSessionConfig())
            expectEquals(VideoKitCommandResult.Executed, session.bind(source, null, emptyList()), "bind $what")
            val ready = awaitState(session.state, what = "$what READY") { it.phase == SessionPhase.READY }
            expectEquals(expected, ready.mediaInfo?.fileSizeBytes, "$what fileSizeBytes")
            session.release()
        }
    },
)
