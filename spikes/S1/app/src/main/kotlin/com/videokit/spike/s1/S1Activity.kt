package com.videokit.spike.s1

import android.app.Activity
import android.os.Bundle
import android.util.Log
import android.view.SurfaceHolder
import android.view.SurfaceView
import android.view.WindowManager
import com.videokit.api.Size
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import java.io.File

/**
 * Runs the S1 measurement. Samples are pushed to the app's external files directory
 * (`/sdcard/Android/data/com.videokit.spike.s1/files/`); start with
 * `adb shell am start -n com.videokit.spike.s1/.S1Activity --es files a.mp4,b.mkv [--es conditions local,lat50]
 * [--es prefetch 64,256,1024 (KiB)] [--ei reps 20]`.
 * Results: `files/s1_results.jsonl` and logcat tag `S1RESULT`; the last line is `{"event":"done"}`.
 */
class S1Activity : Activity() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private lateinit var view: SurfaceView
    private var started = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        view = SurfaceView(this)
        setContentView(view)
        view.holder.addCallback(
            object : SurfaceHolder.Callback {
                override fun surfaceCreated(holder: SurfaceHolder) = start()

                override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) = Unit

                override fun surfaceDestroyed(holder: SurfaceHolder) = Unit
            },
        )
    }

    private fun start() {
        if (started) return
        started = true
        val dir = getExternalFilesDir(null) ?: filesDir
        val names = intent.getStringExtra("files")?.split(',')?.map { it.trim() }?.filter { it.isNotEmpty() }.orEmpty()
        val files = names.map { File(dir, it) }.filter { it.isFile }
        val wanted = intent.getStringExtra("conditions")?.split(',')?.map { it.trim() }?.toSet()
        val conditions = Condition.ALL.filter { wanted == null || it.name in wanted }
        val out = File(dir, "s1_results.jsonl").apply { delete() }
        val reps = intent.getIntExtra("reps", 1).coerceAtLeast(1)
        val prefetch = intent.getStringExtra("prefetch")?.split(',')?.mapNotNull { it.trim().toIntOrNull()?.times(1024) } ?: S1BenchDefaults.PREFETCH
        MainThreadWatch.install()
        Log.i("S1RESULT", "files=${files.map { it.name }} conditions=${conditions.map { it.name }}")
        val bench = S1Bench(this, { view.holder.surface.takeIf { it.isValid }?.let { it to Size(view.width, view.height) } }, out)
        scope.launch(Dispatchers.Default) { bench.run(files, conditions, prefetch, reps) }
    }

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }
}

/** Defaults of the S1 run. */
object S1BenchDefaults {
    /** Read-ahead sizes compared (15 §4 S1: three sizes): 64 KiB, 256 KiB (Kit default), 1 MiB. */
    val PREFETCH: List<Int> = listOf(64 * 1024, 256 * 1024, 1024 * 1024)
}
