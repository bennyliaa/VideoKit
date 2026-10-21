package com.videokit.spike.c07;

import android.app.Activity;
import android.os.Bundle;
import android.widget.*;
import androidx.media3.common.C;
import androidx.media3.common.Player;
import androidx.media3.common.PlaybackException;
import androidx.media3.exoplayer.ExoPlayer;
import androidx.media3.ui.PlayerView;

/** Manual visual check only, using fixed private fixture aliases; excluded from Release. */
public final class ProbeActivity extends Activity {
    private final RoutingDataSource.Group sources=new RoutingDataSource.Group();private final android.os.Handler watchdog=new android.os.Handler(android.os.Looper.getMainLooper());private java.util.concurrent.ScheduledExecutorService deadlines;private volatile int loadVersion;private volatile boolean ready;private TextView status;
    private AsyncReadBridge.Runtime runtime;private LeaseRegistry leases;private long generation;private ExoPlayer player;
    @Override public void onCreate(Bundle bundle){super.onCreate(bundle);runtime=new AsyncReadBridge.Runtime();leases=new LeaseRegistry();
        try{generation=leases.create();player=MediaEngine.player(this,runtime,leases,generation,DeviceFixtures.routes(this),sources);}
        catch(Exception e){TextView error=new TextView(this);error.setText("D1 initialization failed / D1 初始化失败");setContentView(error);return;}
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);status=new TextView(this);
        status.setText("D1 only / 仅技术验证：手机和平板检查中文字幕、旋转、Seek。缺文件或不支持编码应显示错误。");root.addView(status);
        PlayerView view=new PlayerView(this);view.setPlayer(player);root.addView(view,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout buttons=new LinearLayout(this);for(String kind:new String[]{"mp4","mkv","avi","avi-nosrt"}){Button b=new Button(this);b.setText(kind.toUpperCase());b.setOnClickListener(v->load(kind));buttons.addView(b);}
        Button subtitle=new Button(this);subtitle.setText("字幕/SUB");subtitle.setOnClickListener(v->{boolean disabled=player.getTrackSelectionParameters().disabledTrackTypes.contains(C.TRACK_TYPE_TEXT);player.setTrackSelectionParameters(player.getTrackSelectionParameters().buildUpon().setTrackTypeDisabled(C.TRACK_TYPE_TEXT,!disabled).build());});buttons.addView(subtitle);root.addView(buttons);setContentView(root);
        player.addListener(new Player.Listener(){public void onPlayerError(PlaybackException e){status.setText("D1 error code / 错误代码: "+e.errorCode);}public void onPlaybackStateChanged(int state){ready=state==Player.STATE_READY || state==Player.STATE_ENDED;if(state==Player.STATE_READY){String audio=AudioDiagnostics.tracks(player.getCurrentTracks());status.setText("D1 READY；"+audio+"；请核查实际声音/字幕，READY 不代表效果通过");}}});
        deadlines=java.util.concurrent.Executors.newSingleThreadScheduledExecutor();player.setVolume(1f);StageLog.event("MANUAL_AUDIO","volume=1 audio_focus=MEDIA system_volume_unchanged");String kind=getIntent().getStringExtra("kind");load(kind==null?"mp4":kind);
    }
    private void load(String kind){int version=++loadVersion;ready=false;String uri=kind.startsWith("avi")?MediaEngine.AVI:kind.equals("mkv")?MediaEngine.MKV:MediaEngine.MP4;player.setMediaItem(MediaEngine.item(uri,kind.equals("avi")));StageLog.event("MANUAL_PREPARE_BEGIN", "srt="+kind.equals("avi"));player.prepare();player.play();StageLog.event("MANUAL_PREPARE_RETURN","");deadlines.schedule(()->{if(version!=loadVersion || ready)return;StageLog.event("PREPARE_TIMEOUT", "manual source revocation requested; graphics release not established");StageLog.mainBlocked();sources.cancel();watchdog.post(()->{if(version==loadVersion){player.stop();status.setText("PREPARE_TIMEOUT：本样本未通过，保存日志后退出重试");}});},30,java.util.concurrent.TimeUnit.SECONDS);}
    @Override protected void onStop(){if(player!=null)player.pause();super.onStop();}
    @Override protected void onDestroy(){loadVersion++;ready=true;if(deadlines!=null)deadlines.shutdown();sources.cancel();if(player!=null)player.release();if(leases!=null && generation!=0){leases.retire(generation);new Thread(()->{try{boolean released=leases.awaitReleased(generation,10000);StageLog.event("MANUAL_SOURCE_RELEASE_QUERY","released="+released);if(released)runtime.close();}catch(InterruptedException e){Thread.currentThread().interrupt();}},"d1-activity-drain").start();}super.onDestroy();}
}
