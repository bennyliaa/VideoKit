package com.videokit.spike;

import android.graphics.SurfaceTexture;
import android.view.Surface;
import androidx.media3.common.MediaItem;
import androidx.media3.common.PlaybackException;
import androidx.media3.common.Player;
import androidx.media3.exoplayer.ExoPlayer;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;

/** Device fixture provided separately after authorization, never embedded in APK. */
@RunWith(AndroidJUnit4.class)
public final class AndroidReadSeekProbe {
    @Test public void hostReadsAndMedia3Seek() throws Exception {
        var instrumentation=InstrumentationRegistry.getInstrumentation();
        String path=InstrumentationRegistry.getArguments().getString("mediaPath");
        assertNotNull("Pass authorized device-local read-only fixture as mediaPath",path);
        AtomicInteger handles=new AtomicInteger();AtomicLong bytes=new AtomicLong();
        AtomicReference<ExoPlayer> player=new AtomicReference<>();
        AtomicReference<PlaybackException> failure=new AtomicReference<>();
        AtomicReference<CountDownLatch> ready=new AtomicReference<>(new CountDownLatch(1));
        AtomicReference<SurfaceTexture> texture=new AtomicReference<>();AtomicReference<Surface> surface=new AtomicReference<>();
        HostDataSource.Factory host=()->{
            RandomAccessFile file=new RandomAccessFile(path,"r");handles.incrementAndGet();
            return new ReadBridge.Handle(){
                private boolean closed;
                public Long length(){try{return file.length();}catch(IOException e){return null;}}
                public synchronized int readAt(long p,byte[] b,int o,int n)throws IOException{
                    file.seek(p);int count=file.read(b,o,n);if(count>0)bytes.addAndGet(count);return count;
                }
                public synchronized void close()throws IOException{if(!closed){closed=true;try{file.close();}finally{handles.decrementAndGet();}}}
            };
        };
        try {
            instrumentation.runOnMainSync(()->{
                ExoPlayer p=Media3Wiring.player(instrumentation.getTargetContext(),host);player.set(p);
                p.setVolume(0);p.addListener(new Player.Listener(){
                    public void onPlaybackStateChanged(int state){if(state==Player.STATE_READY)ready.get().countDown();}
                    public void onPlayerError(PlaybackException e){failure.set(e);ready.get().countDown();}
                });
                SurfaceTexture t=new SurfaceTexture(false);t.setDefaultBufferSize(320,180);texture.set(t);
                Surface s=new Surface(t);surface.set(s);p.setVideoSurface(s);
                p.setMediaItem(MediaItem.fromUri("videokit://opaque/fixture.mp4"));p.prepare();
            });
            assertTrue("prepare deadline",ready.get().await(30,TimeUnit.SECONDS));assertNull("decoder/extractor error",failure.get());
            AtomicLong duration=new AtomicLong();instrumentation.runOnMainSync(()->duration.set(player.get().getDuration()));
            assertTrue("valid duration",duration.get()>0);
            for(double fraction:new double[]{0,.25,.5,.9,.99}){
                long position=(long)(duration.get()*fraction);
                instrumentation.runOnMainSync(()->player.get().seekTo(position));
                long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(30);boolean settled=false;
                while(System.nanoTime()<deadline){
                    AtomicLong actual=new AtomicLong();AtomicInteger state=new AtomicInteger();
                    instrumentation.runOnMainSync(()->{actual.set(player.get().getCurrentPosition());state.set(player.get().getPlaybackState());});
                    if(state.get()==Player.STATE_READY && Math.abs(actual.get()-position)<=500){settled=true;break;}
                    if(failure.get()!=null)break;Thread.sleep(50);
                }
                assertNull(failure.get());assertTrue("seek settled within tolerance "+fraction,settled);
            }
            assertTrue("host read used",bytes.get()>0);
            System.out.println("D1 read_bytes="+bytes.get()+" seek_positions=0,25,50,90,99; visual frame correctness not asserted");
        } finally {
            instrumentation.runOnMainSync(()->{
                if(player.get()!=null)player.get().release();
                if(surface.get()!=null)surface.get().release();if(texture.get()!=null)texture.get().release();
            });
        }
        assertEquals("all input handles released",0,handles.get());
    }
}
