package com.videokit.spike.e4;

import android.content.Context;

/** Only the release-pinned authority reaches the Android observation; no device-selected trust hash. */
public final class E9Runtime {
    public static String observe(Context context){try{E9Catalog.Trusted trusted=E9Phase.catalog();return new E9CurrentObservation(context.getFilesDir().toPath(),trusted,new E9AndroidFiles()).observe();}catch(Exception e){return "BLOCKED E9_RELEASE_AUTHORITY:"+E5Trace.safe(e.getClass().getSimpleName()+":"+e.getMessage());}}
    private E9Runtime(){}
}
