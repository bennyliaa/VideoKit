package com.videokit.samplehost

import android.app.Activity
import android.os.Bundle
import android.view.SurfaceHolder
import android.view.SurfaceView
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import com.videokit.api.SeekMode
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitSessionState
import com.videokit.api.android.AndroidSurface
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import java.util.Locale

/**
 * Pure-engine integration (14 §2.2): the host renders a native session into its own [SurfaceView] and drives it
 * with native commands. No Flutter is involved. The session survives rotation (the activity handles configuration
 * changes itself) and is released when the page closes.
 */
class EngineActivity : Activity() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private var session: VideoKitSession? = null
    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val app = application as SampleHostApp
        status = TextView(this)
        val kit = app.videoKit
        if (kit == null) {
            status.text = app.unavailableReason
            setContentView(status)
            return
        }
        val created = kit.createSession(VideoKitSessionConfig(debugTag = "engine-page"))
        session = created
        val surface = SurfaceView(this)
        surface.holder.addCallback(
            object : SurfaceHolder.Callback {
                override fun surfaceCreated(holder: SurfaceHolder) = Unit

                override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
                    created.attachSurface(AndroidSurface(holder.surface, width, height))
                }

                override fun surfaceDestroyed(holder: SurfaceHolder) {
                    created.detachSurface()
                }
            },
        )
        val column = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        column.addView(surface, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        column.addView(status)
        column.addView(controls(created))
        setContentView(column)

        scope.launch {
            val token = "engine-demo"
            created.bind(HostKits.demoSource("normal", token), initialState = null, hostActions = app.host.actionsFor(token))
        }
        scope.launch { created.state.collect(::render) }
    }

    override fun onDestroy() {
        val current = session
        session = null
        if (current != null) {
            // The page owns this session; release it off the main thread, independent of the page scope.
            CoroutineScope(Dispatchers.Default).launch { current.release() }
        }
        scope.cancel()
        super.onDestroy()
    }

    private fun controls(session: VideoKitSession) = LinearLayout(this).apply {
        orientation = LinearLayout.HORIZONTAL
        addView(button(R.string.action_play) { session.execute(VideoKitCommand.Play) })
        addView(button(R.string.action_pause) { session.execute(VideoKitCommand.Pause) })
        addView(button(R.string.action_back_10) { seekBy(session, -SEEK_STEP_US) })
        addView(button(R.string.action_forward_10) { seekBy(session, SEEK_STEP_US) })
    }

    private fun button(label: Int, action: suspend () -> Unit) = Button(this).apply {
        setText(label)
        setOnClickListener { scope.launch { action() } }
    }

    private suspend fun seekBy(session: VideoKitSession, deltaUs: Long) {
        val state = session.state.value
        val target = (state.positionUs + deltaUs).coerceIn(0L, state.durationUs ?: Long.MAX_VALUE)
        session.execute(VideoKitCommand.SeekTo(target, SeekMode.CLOSEST_SYNC))
    }

    private fun render(state: VideoKitSessionState) {
        val duration = state.durationUs?.let(::formatUs) ?: getString(R.string.time_unknown)
        status.text = getString(R.string.state_line, state.phase.name, formatUs(state.positionUs), duration)
    }

    private fun formatUs(us: Long): String {
        val totalSeconds = us / 1_000_000L
        return String.format(Locale.ROOT, "%02d:%02d", totalSeconds / 60, totalSeconds % 60)
    }

    private companion object {
        const val SEEK_STEP_US = 10_000_000L
    }
}
