package com.videokit.api.android

import android.annotation.SuppressLint
import android.content.Context
import com.videokit.api.HostIcon

/**
 * Resolves [HostIcon.Resource] names to drawable ids of the host app (04A T4). The public API carries names, not
 * numeric ids, so icons survive resource renumbering between builds and stay platform independent.
 */
public object HostIcons {
    private const val DRAWABLE = "drawable"

    /**
     * The drawable id of [icon] in [context]'s package, or `0` when it does not exist. Accepts `ic_tag` and
     * `drawable/ic_tag`.
     */
    @SuppressLint("DiscouragedApi") // Name-based lookup is the point of 04A T4; results are cached by the caller.
    public fun drawableId(context: Context, icon: HostIcon.Resource): Int {
        val name = icon.resourceRef.removePrefix("$DRAWABLE/")
        if (name.isEmpty() || '/' in name) return 0
        return context.resources.getIdentifier(name, DRAWABLE, context.packageName)
    }
}
