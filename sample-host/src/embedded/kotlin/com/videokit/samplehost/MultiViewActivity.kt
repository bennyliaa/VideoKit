package com.videokit.samplehost

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.widget.GridLayout
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.ui.android.EmbedContentKind
import com.videokit.ui.android.VideoKitEmbedListener
import com.videokit.ui.android.VideoKitFlutter
import com.videokit.ui.android.VideoKitFlutterView
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

/**
 * 14 §9.3 multi-instance memory comparison: four host sessions shown either by four embed engines (2×2
 * [VideoKitFlutterView]s, [MODE_FOUR_ENGINES]) or by one engine with a grid ([MODE_ONE_ENGINE]). The page logs
 * `multiview_ready` once every view has drawn its first frame; `measure/measure_memory.ps1` then reads
 * `dumpsys meminfo`. The activity handles configuration changes itself; sessions and engines end with the page.
 */
class MultiViewActivity : Activity() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private val sessions = mutableListOf<VideoKitSession>()
    private val views = mutableListOf<VideoKitFlutterView>()
    private var framesPending = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val app = application as SampleHostApp
        val kit = requireNotNull(app.videoKit) { "VideoKit unavailable: ${app.unavailableReason}" }
        val mode = intent.getStringExtra(EXTRA_MODE) ?: MODE_FOUR_ENGINES
        repeat(SESSION_COUNT) { index ->
            val session = kit.createSession(VideoKitSessionConfig(debugTag = "multiview-$index"))
            sessions += session
            val token = "multiview-$index"
            scope.launch { session.bind(HostKits.demoSource("normal", token), initialState = null, hostActions = emptyList()) }
        }
        val grid = GridLayout(this).apply {
            columnCount = 2
            rowCount = if (mode == MODE_ONE_ENGINE) 1 else 2
        }
        if (mode == MODE_ONE_ENGINE) {
            val view = embedView()
            grid.addView(view, cell(columnSpan = 2))
            view.showMultiView(sessions)
        } else {
            sessions.forEach { session ->
                val view = embedView()
                grid.addView(view, cell(columnSpan = 1))
                view.showPlayer(session)
            }
        }
        framesPending = views.size
        setContentView(grid)
        Metrics.log("multiview_open", "mode" to mode, "engines" to VideoKitFlutter.activeEngineCount)
    }

    override fun onDestroy() {
        views.forEach(VideoKitFlutterView::destroy)
        views.clear()
        val owned = sessions.toList()
        sessions.clear()
        CoroutineScope(Dispatchers.Default).launch { owned.forEach { it.release() } }
        scope.cancel()
        super.onDestroy()
    }

    private fun embedView() = VideoKitFlutterView(this).also { view ->
        views += view
        view.listener = object : VideoKitEmbedListener {
            override fun onFirstFrame(kind: EmbedContentKind, elapsedMs: Long, prewarmed: Boolean) {
                framesPending--
                if (framesPending == 0) {
                    val mode = intent.getStringExtra(EXTRA_MODE) ?: MODE_FOUR_ENGINES
                    Metrics.log("multiview_ready", "mode" to mode, "engines" to VideoKitFlutter.activeEngineCount)
                }
            }
        }
    }

    private fun cell(columnSpan: Int) = GridLayout.LayoutParams(
        GridLayout.spec(GridLayout.UNDEFINED, 1f),
        GridLayout.spec(GridLayout.UNDEFINED, columnSpan, 1f),
    ).apply {
        width = 0
        height = 0
    }

    internal companion object {
        const val EXTRA_MODE = "mode"
        const val MODE_FOUR_ENGINES = "multiview4"
        const val MODE_ONE_ENGINE = "multiview1"
        private const val SESSION_COUNT = 4

        fun intent(context: Context, mode: String): Intent = Intent(context, MultiViewActivity::class.java).putExtra(EXTRA_MODE, mode)
    }
}
