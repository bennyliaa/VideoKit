package com.videokit.spike.c05;
import android.content.Context;
import java.io.File;
import java.util.Map;
public final class DeviceFixtures {
    public static File directory(Context context){return new File(context.getFilesDir(),"d1_c05_fixtures");}
    public static Map<String,AsyncReadBridge.Provider>routes(Context context){File dir=directory(context);return Map.of(
        MediaEngine.MP4,HostFixtures.file(new File(dir,"basic.mp4").toPath()),
        MediaEngine.MKV,HostFixtures.file(new File(dir,"large.mkv").toPath()),
        MediaEngine.AVI,HostFixtures.file(new File(dir,"subtitle.avi").toPath()),
        MediaEngine.SRT,HostFixtures.srt(new File(dir,"subtitle.srt").toPath(),stage->StageLog.event(stage,"")));}
}
