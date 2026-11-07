package com.videokit.playback

import com.videokit.api.ErrorCode
import com.videokit.api.MediaKind
import com.videokit.api.MediaTransform
import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationResult
import com.videokit.api.ResourceKind
import com.videokit.api.SessionPhase
import com.videokit.api.Size
import com.videokit.api.ThumbnailResult
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitSessionConfig
import com.videokit.core.CoreOptions
import com.videokit.core.runtime.DefaultResourceBudget
import com.videokit.testkit.CallbackMode
import com.videokit.testkit.FakeClock
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.FakeScenario
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.spi.FakeEngineOptions
import com.videokit.testkit.spi.FakeEngines
import com.videokit.testkit.spi.FakeImageEngine
import com.videokit.testkit.spi.FakeRenderTarget
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import kotlin.coroutines.ContinuationInterceptor
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

/** Image sessions (06 §6, VK-M2) and the host interaction rules (05 §4–§6) on the real session over the fake engines. */
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class ImageSessionTest {
    private class Rig(scope: CoroutineScope, val budget: DefaultResourceBudget = DefaultResourceBudget()) {
        val clock = FakeClock()
        val callbacks = RecordingHostCallbacks()
        private val engines = FakeEngines.platform(
            scope.coroutineContext[ContinuationInterceptor] as CoroutineDispatcher,
            FakeEngineOptions(
                clock = clock,
                // "big*" tokens are large photos (tiles when zoomed); everything else follows the demo scenarios.
                scenarioResolver = { source ->
                    val scenario = FakeScenario.forSource(source)
                    if (source.mediaToken.startsWith("big")) scenario.copy(videoSize = Size(8000, 6000)) else scenario
                },
            ),
        )
        val images: FakeImageEngine = engines.images as FakeImageEngine
        val kit = run {
            PlaybackVideoKit.create(
                VideoKitConfig(hostCallbacks = callbacks, resourceBudget = budget),
                engines,
                CoreOptions(isDemo = true),
                scope,
            )
        }
    }

    // The kit runs in backgroundScope, which advanceUntilIdle does not wait for: let virtual time pass instead.
    private fun TestScope.settle() {
        advanceTimeBy(1_000L)
        runCurrent()
    }

    private suspend fun TestScope.boundImage(rig: Rig, kind: MediaKind = MediaKind.IMAGE_STATIC, token: String = "photo") =
        rig.kit.createSession(VideoKitSessionConfig()).also { session ->
            assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.image(token, kind), null, emptyList()))
            session.state.first { it.phase == SessionPhase.READY }
        }

    @Test
    fun staticImageIsDecodedForItsTextureAndReportsDetails() = runTest {
        val rig = Rig(backgroundScope)
        val session = boundImage(rig)
        val state = session.state.value
        assertEquals(MediaKind.IMAGE_STATIC, state.mediaKind)
        assertTrue(state.resourcesHeld)
        val details = assertNotNull(state.imageDetails)
        assertEquals(1, details.frameCount)
        assertTrue((details.decodedBytes ?: 0L) > 0L)
        assertEquals("png", state.mediaInfo?.container)
        assertNull(state.durationUs)
        // The image memory lease is held while bound.
        assertTrue((rig.budget.freeBytes(ResourceKind.IMAGE_MEMORY) ?: 0L) < DefaultResourceBudget.DEFAULT_IMAGE_MEMORY_BYTES)
        // Video-only and animation commands are refused.
        assertEquals(VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND), session.execute(VideoKitCommand.Play))
        assertEquals(VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND), session.execute(VideoKitCommand.SetLooping(true)))
        session.release()
        assertEquals(DefaultResourceBudget.DEFAULT_IMAGE_MEMORY_BYTES, rig.budget.freeBytes(ResourceKind.IMAGE_MEMORY))
        assertEquals(0, rig.images.openHandles)
        rig.kit.close()
    }

    @Test
    fun zoomRendersTilesOfTheVisibleRegion() = runTest {
        val rig = Rig(backgroundScope)
        val session = boundImage(rig, token = "big-photo")
        assertEquals(VideoKitCommandResult.Executed, session.attachSurface(FakeRenderTarget(4000, 3000)))
        settle()
        val before = rig.images.renderedPlans.size
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SetTransform(MediaTransform(scale = 4f))))
        settle()
        val zoomed = rig.images.renderedPlans.drop(before).last()
        assertTrue(zoomed.tiles.isNotEmpty(), "tiles after zoom: $zoomed")
        assertTrue(zoomed.tiles.all { it.sampleSize < zoomed.baseSampleSize })
        session.execute(VideoKitCommand.SetTransform(MediaTransform()))
        settle()
        assertTrue(rig.images.renderedPlans.last().tiles.isEmpty())
        rig.kit.close()
    }

    @Test
    fun animatedImagePlaysLoopsAndEnds() = runTest {
        val rig = Rig(backgroundScope)
        val session = boundImage(rig, MediaKind.IMAGE_ANIMATED, "anim")
        val state = session.state.value
        assertTrue(state.looping, "animations loop by default (04A L1)")
        assertEquals(2_000_000L, state.durationUs)
        assertEquals(20, state.imageDetails?.frameCount)
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Play))
        rig.clock.advanceUs(5_000_000L)
        settle()
        assertEquals(SessionPhase.PLAYING, session.state.value.phase)
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Pause))
        assertEquals(SessionPhase.PAUSED, session.state.value.phase)
        session.execute(VideoKitCommand.SetLooping(false))
        session.execute(VideoKitCommand.Play)
        rig.clock.advanceUs(3_000_000L)
        val ended = session.state.first { it.phase == SessionPhase.ENDED }
        assertEquals(2_000_000L, ended.positionUs)
        // Replay starts from the first frame.
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Play))
        assertEquals(SessionPhase.PLAYING, session.state.value.phase)
        assertEquals(0L, session.state.value.positionUs)
        val snapshot = session.release()
        assertEquals(false, snapshot.looping)
        assertNull(snapshot.positionUs)
        rig.kit.close()
    }

    @Test
    fun unknownImageKindIsResolvedFromTheHeader() = runTest {
        val rig = Rig(backgroundScope)
        val session = boundImage(rig, MediaKind.IMAGE_UNKNOWN, "unknown")
        assertEquals(MediaKind.IMAGE_STATIC, session.state.value.mediaKind)
        rig.kit.close()
    }

    @Test
    fun corruptAndUnsupportedImagesFailTheBind() = runTest {
        val rig = Rig(backgroundScope)
        val corrupt = rig.kit.createSession(VideoKitSessionConfig())
        val result = assertIs<VideoKitCommandResult.Rejected>(corrupt.bind(FakeMediaSources.image("demo:corrupt"), null, emptyList()))
        assertEquals(ErrorCode.CORRUPT_MEDIA, result.error.code)
        assertEquals(false, corrupt.state.value.resourcesHeld)
        val unsupported = rig.kit.createSession(VideoKitSessionConfig())
        val refused =
            assertIs<VideoKitCommandResult.Rejected>(unsupported.bind(FakeMediaSources.image("demo:unsupported"), null, emptyList()))
        assertEquals(ErrorCode.UNSUPPORTED_CONTAINER, refused.error.code)
        // Another session is not affected (06 §6.2).
        boundImage(rig, token = "fine")
        assertEquals(1, rig.images.openHandles)
        rig.kit.close()
    }

    @Test
    fun memoryQuotaDegradesSamplingWithANotice() = runTest {
        val rig = Rig(backgroundScope, DefaultResourceBudget.forDevice(4, imageMemoryBytes = 1_600_000L))
        val session = rig.kit.createSession(VideoKitSessionConfig())
        val notices = async(start = CoroutineStart.UNDISPATCHED) { session.events.first { it is VideoKitEvent.TransientNotice } }
        assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.image("quota"), null, emptyList()))
        assertEquals(VideoKitEvent.TransientNotice("IMAGE_MEMORY_REDUCED_QUALITY"), notices.await())
        val details = assertNotNull(session.state.first { it.phase == SessionPhase.READY }.imageDetails)
        assertTrue((details.decodedBytes ?: Long.MAX_VALUE) <= 1_600_000L, "within the quota: $details")
        assertTrue((details.sampleSize ?: 0) > 1)
        // Nothing left for a second image: the bind fails with a resource error instead of looping.
        val other = rig.kit.createSession(VideoKitSessionConfig())
        val refused = assertIs<VideoKitCommandResult.Rejected>(other.bind(FakeMediaSources.image("other"), null, emptyList()))
        assertEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, refused.error.code)
        rig.kit.close()
    }

    @Test
    fun imageThumbnailAndSourceReleasedAfterEveryHandle() = runTest {
        val rig = Rig(backgroundScope)
        val session = boundImage(rig)
        assertIs<ThumbnailResult.Captured>(session.captureThumbnail(0, 160, 90))
        val released = async(start = CoroutineStart.UNDISPATCHED) { session.events.first { it is VideoKitEvent.SourceReleased } }
        session.release()
        assertEquals(VideoKitEvent.SourceReleased("photo"), released.await())
        assertEquals(listOf("photo"), rig.callbacks.sourceReleases.map { it.second })
        rig.kit.close()
    }

    @Test
    fun repeatedNavigationSharesOneHostRequest() = runTest {
        val rig = Rig(backgroundScope)
        val session = boundImage(rig)
        rig.callbacks.overrideMode("onNavigationRequested", CallbackMode.HANG)
        val first = async { session.requestNavigation(NavigationDirection.NEXT) }
        val second = async { session.requestNavigation(NavigationDirection.NEXT) }
        assertEquals(NavigationResult.FAILED, first.await())
        assertEquals(NavigationResult.FAILED, second.await())
        assertEquals(1, rig.callbacks.navigationRequests.size)
        rig.callbacks.overrideMode("onNavigationRequested", null)
        rig.callbacks.navigationAnswer = { NavigationResult.ACCEPTED }
        assertEquals(NavigationResult.ACCEPTED, session.requestNavigation(NavigationDirection.PREVIOUS))
        assertEquals(NavigationDirection.PREVIOUS, rig.callbacks.navigationRequests.last().direction)
        // Controls visibility is written back and reported only on change.
        session.setControlsVisible(false)
        session.setControlsVisible(false)
        session.setControlsVisible(true)
        settle()
        assertEquals(listOf(false, true), rig.callbacks.controlsVisibility.map { it.second })
        assertTrue(session.state.value.controlsVisible)
        rig.kit.close()
    }
}
