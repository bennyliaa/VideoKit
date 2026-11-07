package com.videokit.testkit.contract

import com.videokit.api.HostCallbackTimeouts
import com.videokit.api.MediaKind
import com.videokit.api.SessionPhase
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSession
import com.videokit.testkit.FakeClock
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.FakeScenario
import com.videokit.testkit.FakeVideoKit
import com.videokit.testkit.FakeVideoKitOptions
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withTimeoutOrNull
import kotlinx.coroutines.yield

/**
 * [VideoKitContractSubject] for the Kotlin Fake. Pass a scope whose dispatcher is the test dispatcher
 * (for example `TestScope.backgroundScope`) so that all latencies and timeouts run on virtual time.
 */
public class FakeContractSubject(
    private val scope: CoroutineScope,
    /** Clock shared by the created instances. */
    public val clock: FakeClock = FakeClock(),
    /** Base options; `scope` and `clock` are replaced. */
    private val baseOptions: FakeVideoKitOptions = FakeVideoKitOptions(),
) : VideoKitContractSubject {
    override val callbackTimeouts: HostCallbackTimeouts get() = baseOptions.callbackTimeouts

    override val sourceTimeoutMs: Long get() = baseOptions.sourceTimeoutMs

    override fun create(callbacks: VideoKitHostCallbacks): VideoKit =
        FakeVideoKit(callbacks, baseOptions.copy(scope = scope, clock = clock))

    override fun playableVideo(token: String): VideoKitMediaSource = FakeMediaSources.video(token)

    override fun playableImage(token: String): VideoKitMediaSource = FakeMediaSources.image(token, MediaKind.IMAGE_STATIC)

    override suspend fun advanceMediaTime(us: Long) {
        clock.advanceUs(us)
        yield()
    }

    /** Binds the `demo:corrupt` scenario and plays across its corrupt position. */
    override suspend fun driveToFatalError(session: VideoKitSession): Boolean {
        val corruptAt = FakeScenario.named("corrupt")?.corruptAtUs ?: return false
        if (session.bind(FakeMediaSources.video("demo:corrupt"), null, emptyList()) != VideoKitCommandResult.Executed) return false
        session.execute(VideoKitCommand.SeekTo(corruptAt - 100_000L))
        session.execute(VideoKitCommand.Play)
        advanceMediaTime(500_000L)
        return withTimeoutOrNull(15_000L) { session.state.first { it.phase == SessionPhase.ERROR_FATAL } } != null
    }
}
