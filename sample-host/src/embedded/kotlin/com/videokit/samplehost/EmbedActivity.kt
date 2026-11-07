package com.videokit.samplehost

import android.content.pm.ActivityInfo
import android.os.Bundle
import android.view.View
import android.widget.FrameLayout
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.fragment.app.FragmentManager
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.ui.android.EmbedContentKind
import com.videokit.ui.android.PlayerEmbedOptions
import com.videokit.ui.android.VideoKitEmbedFragment
import com.videokit.ui.android.VideoKitEmbedListener
import com.videokit.ui.android.VideoKitPlayerFragment
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * add-to-app page (14 §9.1): the host creates and binds a native session, hands it to [VideoKitPlayerFragment]
 * and adds a native panel to the fragment's host panel container. The session is owned by the host: it survives
 * rotation (the activity is re-created, the session and the embed engine are not) and is released when the page
 * finishes.
 */
class EmbedActivity :
    FragmentActivity(),
    VideoKitEmbedListener {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val container = FrameLayout(this).apply { id = R.id.embed_container }
        setContentView(container)
        supportFragmentManager.registerFragmentLifecycleCallbacks(PanelInstaller(), false)
        if (savedInstanceState == null) {
            val session = HostSessions.embedSession(application as SampleHostApp)
            supportFragmentManager.beginTransaction()
                .replace(R.id.embed_container, VideoKitPlayerFragment.newInstance(session, PlayerEmbedOptions()))
                .commit()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (isFinishing) HostSessions.releaseEmbedSession()
    }

    // ---------------------------------------------------------------- VideoKitEmbedListener (activity fallback)

    override fun onFullscreenRequested(fullscreen: Boolean) {
        requestedOrientation =
            if (fullscreen) ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE else ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED
    }

    override fun onFirstFrame(kind: EmbedContentKind, elapsedMs: Long, prewarmed: Boolean) {
        Metrics.log("first_frame", "kind" to kind.name, "ms" to elapsedMs, "prewarmed" to prewarmed)
        val mode = getString(if (prewarmed) R.string.first_frame_prewarmed else R.string.first_frame_cold)
        Toast.makeText(this, getString(R.string.first_frame, elapsedMs, mode), Toast.LENGTH_SHORT).show()
    }

    /** Adds the host's own panel (a neighbour strip in LocalVideoBrowser) once the embed view exists. */
    private inner class PanelInstaller : FragmentManager.FragmentLifecycleCallbacks() {
        override fun onFragmentViewCreated(fm: FragmentManager, f: Fragment, v: View, savedInstanceState: Bundle?) {
            val panels = (f as? VideoKitEmbedFragment)?.hostPanelContainer ?: return
            panels.addView(TextView(this@EmbedActivity).apply { setText(R.string.neighbour_panel) })
        }
    }
}

/** Host-owned embed session, outliving activity re-creation. Main thread only. */
internal object HostSessions {
    private var session: VideoKitSession? = null

    fun embedSession(app: SampleHostApp): VideoKitSession = session ?: run {
        val kit = requireNotNull(app.videoKit) { "VideoKit unavailable: ${app.unavailableReason}" }
        val created = kit.createSession(VideoKitSessionConfig(debugTag = "embed-page"))
        session = created
        val token = "embed-demo"
        CoroutineScope(Dispatchers.Main.immediate).launch {
            created.bind(HostKits.demoSource("normal", token), initialState = null, hostActions = app.host.actionsFor(token))
        }
        created
    }

    fun releaseEmbedSession() {
        val current = session ?: return
        session = null
        CoroutineScope(Dispatchers.Default).launch { current.release() }
    }
}
