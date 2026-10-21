package com.videokit.d1present;
import android.content.Context;
import android.media.*;
import android.os.Handler;
import android.os.Looper;
import android.os.HandlerThread;
import java.io.IOException;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicBoolean;

/** One AudioTrack/focus owner per presentation process. No compressed-audio decoder. */
public final class PlatformAudio implements WorkSession.AudioPort {
    private static final Semaphore ONE=new Semaphore(1);
    private final AudioManager manager;private Handler callbacks;private HandlerThread callbackThread;
    private final AudioFocusPolicy policy=new AudioFocusPolicy();private AudioTrack original;private AudioFocusRequest focus;
    private Thread owner;private boolean slot,closed,unknown,focused,paused;private long epoch=-1,writtenFrames,cumulativeBytes;
    private boolean focusAbandonEntered;
    public PlatformAudio(Context c){manager=(AudioManager)c.getSystemService(Context.AUDIO_SERVICE);}
    private void requireOwner(){if(owner==null)owner=Thread.currentThread();if(owner!=Thread.currentThread())throw new IllegalStateException("AUDIO_ORIGINAL_THREAD");}
    private void create()throws Exception {
        if(original!=null)return;if(!ONE.tryAcquire())throw new IOException("AUDIO_OWNER_OCCUPIED");slot=true;
        callbackThread=new HandlerThread("d1-original-audio-focus-callbacks");callbackThread.start();callbacks=new Handler(callbackThread.getLooper());
        original=new AudioTrack.Builder().setAudioAttributes(new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
            .setAudioFormat(new AudioFormat.Builder().setEncoding(AudioFormat.ENCODING_PCM_16BIT).setSampleRate(48000).setChannelMask(AudioFormat.CHANNEL_OUT_STEREO).build())
            .setTransferMode(AudioTrack.MODE_STREAM).setBufferSizeInBytes(15360).build();
        if(original.getState()!=AudioTrack.STATE_INITIALIZED)throw new IOException("AUDIO_INITIALIZATION_REJECTED");
        if(original.setVolume(0f)!=AudioTrack.SUCCESS)throw new IOException("AUDIO_MUTE_REJECTED");original.play();
    }
    private void volume(boolean audible)throws Exception {
        policy.audible(audible);
        if(policy.requestNeeded(paused)){
            policy.requestEntered();
            abandonFocus();
            focus=new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT)
                .setAudioAttributes(new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
                .setOnAudioFocusChangeListener(change->{if(change!=AudioManager.AUDIOFOCUS_GAIN)policy.lost();},callbacks).setAcceptsDelayedFocusGain(false).build();
            focused=manager.requestAudioFocus(focus)==AudioManager.AUDIOFOCUS_REQUEST_GRANTED;
            policy.requestReturned(focused);
        }
        if(original.setVolume(policy.gain(paused))!=AudioTrack.SUCCESS)throw new IOException("AUDIO_VOLUME_REJECTED");
    }
    private void abandonFocus()throws Exception {
        if(focus==null)return;
        if(focusAbandonEntered){unknown=true;throw new IOException("FOCUS_ORIGINAL_ABANDON_PENDING");}
        focusAbandonEntered=true;
        try{if(manager.abandonAudioFocusRequest(focus)!=AudioManager.AUDIOFOCUS_REQUEST_GRANTED)throw new IOException("FOCUS_ABANDON_UNPROVEN");focus=null;focusAbandonEntered=false;}
        catch(Throwable failure){unknown=true;throw failure;}
    }
    public int write(byte[] bytes,int n,long actualEpoch,PlaybackGate gate,java.util.function.BooleanSupplier audible,long deadline)throws Exception {
        requireOwner();if(n<1||n>Limits.PCM_BLOCK||n%4!=0)throw new IOException("PCM_LAYOUT_REJECTED");
        if(n>Limits.PCM_BYTES-cumulativeBytes)throw new IOException("PCM_TOTAL_BYTE_BUDGET");
        if(!gate.current(actualEpoch))return 0;create();
        if(epoch!=actualEpoch){original.pause();original.flush();writtenFrames=0;epoch=actualEpoch;original.play();paused=false;gate.audioAck(epoch);}
        int count=0;
        while(count<n){
            if(!gate.current(actualEpoch))return count;
            if(System.nanoTime()>deadline)throw new IOException("AUDIO_OBSERVATION_EXPIRED");
            if(gate.paused()){original.setVolume(0f);if(!paused){original.pause();paused=true;}Thread.sleep(2);continue;}
            if(paused){original.play();paused=false;}
            volume(audible.getAsBoolean());
            int written=original.write(bytes,count,n-count,AudioTrack.WRITE_NON_BLOCKING);
            if(written<0||written>n-count||written%4!=0)throw new IOException("AUDIO_WRITE_REJECTED");
            count+=written;cumulativeBytes+=written;writtenFrames+=written/4;if(written==0)Thread.sleep(2);
        }return count;
    }
    public void drain(long deadline,PlaybackGate gate,java.util.function.BooleanSupplier audible)throws Exception {
        requireOwner();if(original==null)return;
        while(!gate.cancelled()&&Integer.toUnsignedLong(original.getPlaybackHeadPosition())<writtenFrames){
            if(System.nanoTime()>deadline)throw new IOException("AUDIO_DRAIN_OBSERVATION_EXPIRED");
            if(!gate.current(epoch)){original.setVolume(0f);original.pause();original.flush();writtenFrames=0;return;}
            if(gate.paused()){original.setVolume(0f);if(!paused){original.pause();paused=true;}}
            else{if(paused){original.play();paused=false;}volume(audible.getAsBoolean());}
            Thread.sleep(2);
        }
    }
    public void close()throws Exception {
        requireOwner();if(closed)return;if(unknown)throw new IOException("AUDIO_ORIGINAL_RETURN_UNKNOWN");
        try{
            if(original!=null){if(original.setVolume(0f)!=AudioTrack.SUCCESS)throw new IOException("AUDIO_FINAL_MUTE_REJECTED");original.pause();original.flush();original.stop();original.release();original=null;}
            abandonFocus();
            // Drain already queued callbacks and externally join the SAME original callback thread.
            // Late posts to its retired Looper are rejected; none can perform AudioTrack IO.
            if(callbackThread!=null){callbackThread.quitSafely();callbackThread.join();callbackThread=null;callbacks=null;}
            policy.closed();closed=true;if(slot){slot=false;ONE.release();}
        }catch(Throwable t){unknown=true;throw t;}
    }
    public boolean returned(){return closed&&!unknown&&original==null&&focus==null&&!slot;}
    public String state(){return "writtenFrames="+writtenFrames+" defaultMuted=true focusRequestGranted="+focused+" requests="+policy.requests()+" closed="+closed+" unknown="+unknown+" (not listening proof)";}
}
