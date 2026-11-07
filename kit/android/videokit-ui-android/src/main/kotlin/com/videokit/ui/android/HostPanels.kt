package com.videokit.ui.android

import android.view.View

/**
 * Shows / hides the host panel container together with the VideoKit controls (14 §9.2), with the motion duration
 * the Dart theme reports (0 when animations are reduced).
 */
internal object HostPanels {
    fun animate(container: View, visible: Boolean, animationMs: Long) {
        container.animate().cancel()
        if (visible) container.visibility = View.VISIBLE
        container.animate()
            .alpha(if (visible) 1f else 0f)
            .setDuration(animationMs.coerceAtLeast(0L))
            .withEndAction { if (!visible) container.visibility = View.INVISIBLE }
            .start()
    }
}
