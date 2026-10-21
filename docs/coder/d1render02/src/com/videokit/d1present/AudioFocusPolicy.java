package com.videokit.d1present;
import java.io.IOException;
/** Small tested focus policy, used by the actual AudioManager thin adapter. */
public final class AudioFocusPolicy {
    private boolean audible,attempted,granted,lost,closed;private int requests;
    public synchronized void audible(boolean value){if(value&&!audible){attempted=false;lost=false;}audible=value;}
    public synchronized boolean requestNeeded(boolean paused){return !closed&&audible&&!paused&&!attempted;}
    public synchronized void requestEntered()throws IOException{if(++requests>4)throw new IOException("FOCUS_REQUEST_BUDGET");attempted=true;}
    public synchronized void requestReturned(boolean accepted){granted=accepted;}
    public synchronized void lost(){lost=true;granted=false;}
    public synchronized float gain(boolean paused){return !closed&&audible&&granted&&!lost&&!paused?0.15f:0f;}
    public synchronized void closed(){closed=true;granted=false;}
    public synchronized int requests(){return requests;}
}
