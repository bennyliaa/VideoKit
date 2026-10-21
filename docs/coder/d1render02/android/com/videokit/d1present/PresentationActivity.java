package com.videokit.d1present;
import android.app.Activity;
import android.app.Application;
import android.graphics.SurfaceTexture;
import android.os.*;
import android.view.*;
import android.widget.*;

/** Debug feasibility UI only, dedicated process; never starts media or sound automatically. */
public final class PresentationActivity extends Activity implements TextureView.SurfaceTextureListener {
    private TextureView texture;private TextView state;private volatile WorkSession session;private PlatformRenderer renderer;private PlatformAudio audio;
    private boolean manualOnly,manualGesture;private Button listenButton;private final ManualListenWindow manual=new ManualListenWindow();
    private final Handler ui=new Handler(Looper.getMainLooper());private boolean destroyed;private volatile boolean surfaceReady;private String uiError="";
    private final Runnable refresh=new Runnable(){public void run(){if(destroyed)return;state.setText(uiError+"\n"+(session==null?"等待明确启动；默认静音 / Idle, muted":session.state()+"\n"+renderer.state()+"\n"+audio.state()));ui.postDelayed(this,250);}};
    @Override public void onCreate(Bundle state){
        super.onCreate(state);if(!Application.getProcessName().endsWith(":presentation"))throw new IllegalStateException("DEDICATED_PRESENTATION_PROCESS_REQUIRED");
        manualOnly=getIntent().getBooleanExtra("renderManualIdle",false);
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);setContentView(root);
        TextView label=new TextView(this);label.setText("D1 有限实验 · 最多6帧/3秒PCM · 非正式播放器\n生成画面不代表解码；PCM不代表压缩音轨。默认静音。");root.addView(label);
        texture=new TextureView(this);texture.setSurfaceTextureListener(this);root.addView(texture,new LinearLayout.LayoutParams(-1,0,1));
        if(!manualOnly){button(root,"生成画面 + 静音PCM / Generated",()->startProbe(true,90));button(root,"已授权MP4原始帧 + 静音PCM",()->startProbe(false,0));}
        listenButton=button(root,"明确听音：从闲置启动完整3秒低幅声 / Listen",this::listenFromIdle);
        if(manualOnly)listenButton.setEnabled(false);
        button(root,"全静音 / Mute",()->{if(session!=null)session.mute(true);});
        button(root,"暂停 / 恢复",()->{if(session!=null)session.pause(!session.gate.paused());});
        button(root,"撤销旧播放代次 / Epoch",()->{if(session!=null)session.seek();});
        button(root,"销毁后重建呈现表面 / Recreate",this::recreateSurface);
        button(root,"取消 / Cancel",()->{if(session!=null)session.cancel();});
        this.state=new TextView(this);root.addView(this.state);ui.post(refresh);
    }
    private interface Action{void run()throws Exception;}
    private Button button(LinearLayout p,String label,Action action){Button b=new Button(this);b.setText(label);p.addView(b);b.setOnClickListener(v->{try{action.run();}catch(Exception e){uiError="BLOCKED "+e.getClass().getSimpleName()+" "+e.getMessage();}});return b;}
    private void listenFromIdle()throws Exception {
        if(session!=null)throw new IllegalStateException("LISTEN_REQUIRES_IDLE_NO_RUNNING_SUBSTITUTE");
        if(manualOnly&&!manual.claimClick(System.nanoTime()))throw new IllegalStateException("MANUAL_CLICK_WINDOW_CLOSED");
        listenButton.setEnabled(false);manualGesture=true;
        try{startProbe(true,0,false,true);if(manualOnly)manual.started();}
        catch(Exception failure){if(manualOnly)manual.failed("MANUAL_START_FAILED");throw failure;}
        finally{manualGesture=false;}
    }
    public void armManualListen(){if(!manualOnly||!surfaceReady||session!=null)throw new IllegalStateException("MANUAL_IDLE_NOT_READY");manual.arm(System.nanoTime());listenButton.setEnabled(true);}
    public boolean closeManualIdle(){if(!manualOnly)throw new IllegalStateException("NOT_MANUAL_MODE");listenButton.setEnabled(false);return manual.closeIdle();}
    public boolean manualListenStarted(){return manual.startedFromClick();}public String manualListenFailure(){return manual.failure();}public String manualState(){return manual.state();}
    public void startProbe(boolean generated,int rotation)throws Exception {
        startProbe(generated,rotation,false);
    }
    public void startProbe(boolean generated,int rotation,boolean paused)throws Exception {
        startProbe(generated,rotation,paused,false);
    }
    private void startProbe(boolean generated,int rotation,boolean paused,boolean initiallyAudible)throws Exception {
        if(manualOnly&&!manualGesture)throw new IllegalStateException("MANUAL_ONLY_EXPLICIT_LISTEN");
        if(session!=null)throw new IllegalStateException("ONE_FINITE_SESSION_PER_PROCESS");
        if(!texture.isAvailable())throw new IllegalStateException("SURFACE_NOT_AVAILABLE");
        renderer=new PlatformRenderer();audio=new PlatformAudio(this);
        String version=generated?"generated-rgba-v1-seed-"+PcmFixture.SEED:"mp4-"+RawSources.BASIC_SHA;
        session=new WorkSession(android.os.Process.myUid(),android.os.Process.myPid(),version,new RawSources(this,generated,rotation),renderer,audio);
        renderer.budget(session.pixels);renderer.attach(texture.getSurfaceTexture(),session.gate);if(paused)session.pause(true);
        // Set explicit audible intent BEFORE admitting the producer/audio threads, never after a
        // running muted session has consumed part of the three-second source.
        session.mute(!initiallyAudible);session.start();
    }
    public void recreateSurface(){
        if(session==null)return;
        surfaceReady=false;
        // TextureView owns a newly available producer; onDestroyed transfers the old one to render owner.
        ViewGroup parent=(ViewGroup)texture.getParent();int index=parent.indexOfChild(texture);ViewGroup.LayoutParams lp=texture.getLayoutParams();
        parent.removeView(texture);texture=new TextureView(this);texture.setSurfaceTextureListener(this);parent.addView(texture,index,lp);
    }
    public WorkSession session(){return session;}public boolean surfaceAvailable(){return surfaceReady&&!destroyed;}
    public void onSurfaceTextureAvailable(SurfaceTexture t,int w,int h){surfaceReady=true;if(session!=null)try{renderer.attach(t,session.gate);}catch(Exception e){uiError="BLOCKED "+e.getMessage();session.cancel();}}
    public void onSurfaceTextureSizeChanged(SurfaceTexture t,int w,int h){}
    public void onSurfaceTextureUpdated(SurfaceTexture t){}
    public boolean onSurfaceTextureDestroyed(SurfaceTexture t){if(texture.getSurfaceTexture()==t)surfaceReady=false;return session==null||renderer.destroyed(t,session.gate);}
    @Override public void onPause(){if(session!=null)session.cancel();super.onPause();}
    @Override public void onDestroy(){destroyed=true;ui.removeCallbacks(refresh);if(session!=null)session.cancel();super.onDestroy();}
}
