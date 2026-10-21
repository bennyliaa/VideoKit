package com.videokit.d1present;
import java.io.IOException;
/** Metadata only. Never calls a platform port or waits while holding this monitor. */
public final class PlaybackGate {
    public final String task,sourceVersion;private long epoch=1,surface;private boolean paused,cancelled;
    private int surfaceEvents;
    private long renderAckEpoch,renderAckSurface,audioAckEpoch;
    public PlaybackGate(String task,String version){this.task=task;sourceVersion=version;}
    public synchronized long epoch(){return epoch;}public synchronized long surface(){return surface;}
    public synchronized long seek()throws IOException{live();epoch++;notifyAll();return epoch;}
    public synchronized long attach()throws IOException{live();if(++surfaceEvents>8)throw new IOException("SURFACE_EVENT_BUDGET");surface++;notifyAll();return surface;}
    public synchronized void detach(long generation){if(generation==surface)surface++;notifyAll();}
    public synchronized void pause(boolean value)throws IOException{live();paused=value;notifyAll();}
    public synchronized void cancel(){cancelled=true;epoch++;surface++;notifyAll();}
    public synchronized boolean accepts(long e,long s){return !cancelled&&!paused&&epoch==e&&surface==s;}
    public synchronized boolean current(long e){return !cancelled&&epoch==e;}
    public synchronized boolean paused(){return paused;}public synchronized boolean cancelled(){return cancelled;}
    /** Effective owner ACK is separate from UI intent; old native in-flight work must return first. */
    public synchronized void renderAck(long e,long s){if(accepts(e,s)){renderAckEpoch=e;renderAckSurface=s;}}
    public synchronized void audioAck(long e){if(current(e))audioAckEpoch=e;}
    public synchronized boolean renderAcknowledged(){return !cancelled&&renderAckEpoch==epoch&&renderAckSurface==surface;}
    public synchronized boolean audioAcknowledged(){return !cancelled&&audioAckEpoch==epoch;}
    private void live()throws IOException{if(cancelled)throw new IOException("SESSION_CANCELLED");}
}
