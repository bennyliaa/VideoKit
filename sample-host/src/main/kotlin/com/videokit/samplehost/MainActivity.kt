package com.videokit.samplehost

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast

/**
 * Entry screen (14 §2.2): the pure-engine page, the add-to-app page and the two multi-view variants of the 14 §9.3
 * memory comparison. The launch extras in [LaunchExtras] let the measurement scripts prewarm and open pages.
 */
class MainActivity : Activity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val padding = (16 * resources.displayMetrics.density).toInt()
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(padding, padding, padding, padding)
        }
        if (HostKits.isDemo) column.addView(TextView(this).apply { setText(R.string.demo_badge) })
        column.addView(entry(R.string.engine_page_title, R.string.engine_page_summary) { open(PAGE_ENGINE) })
        column.addView(entry(R.string.embed_page_title, R.string.embed_page_summary) { open(PAGE_EMBED) })
        column.addView(entry(R.string.multiview4_title, R.string.multiview4_summary) { open(PAGE_MULTIVIEW_FOUR) })
        column.addView(entry(R.string.multiview1_title, R.string.multiview1_summary) { open(PAGE_MULTIVIEW_ONE) })
        setContentView(column)

        if (savedInstanceState == null) {
            if (intent.getBooleanExtra(LaunchExtras.PREWARM, true)) EmbedSupport.prewarm()
            intent.getStringExtra(LaunchExtras.OPEN)?.let { page ->
                handler.postDelayed({ open(page) }, intent.getLongExtra(LaunchExtras.OPEN_DELAY_MS, 0L))
            }
        }
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        super.onDestroy()
    }

    private fun open(page: String) {
        if (page == PAGE_ENGINE) {
            startActivity(Intent(this, EngineActivity::class.java))
            return
        }
        val app = application as SampleHostApp
        val message = when {
            !EmbedSupport.inFlavor -> getString(R.string.embed_not_in_flavor)
            !EmbedSupport.isAvailable() -> getString(R.string.embed_unavailable)
            app.videoKit == null -> app.unavailableReason
            else -> null
        }
        if (message != null) {
            Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        } else {
            EmbedSupport.open(this, page)
        }
    }

    private fun entry(title: Int, summary: Int, onClick: () -> Unit) = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        addView(
            Button(context).apply {
                setText(title)
                setOnClickListener { onClick() }
            },
        )
        addView(TextView(context).apply { setText(summary) })
    }

    internal companion object {
        const val PAGE_ENGINE = "engine"
        const val PAGE_EMBED = "embed"
        const val PAGE_MULTIVIEW_FOUR = "multiview4"
        const val PAGE_MULTIVIEW_ONE = "multiview1"
    }
}
