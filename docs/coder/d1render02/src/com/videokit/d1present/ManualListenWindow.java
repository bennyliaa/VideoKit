package com.videokit.d1present;
/** One bounded manual idle window. It never starts media, grants sound, or substitutes for a click. */
public final class ManualListenWindow {
    public static final long IDLE_NS=15000000000L;
    private long deadline;private boolean armed,closed,claimed,started;private String failure;
    public synchronized void arm(long now){if(armed||closed)throw new IllegalStateException("MANUAL_WINDOW_ONCE");armed=true;deadline=now+IDLE_NS;}
    public synchronized boolean claimClick(long now){if(!armed||closed||claimed||now>=deadline){if(armed&&now>=deadline)closed=true;return false;}claimed=true;return true;}
    public synchronized void started(){if(!claimed||started)throw new IllegalStateException("MANUAL_CLICK_REQUIRED");started=true;}
    public synchronized void failed(String code){failure=code;closed=true;}
    public synchronized boolean closeIdle(){closed=true;return started;}
    public synchronized boolean startedFromClick(){return started;}
    public synchronized String failure(){return failure;}
    public synchronized String state(){return "armed="+armed+" claimed="+claimed+" started="+started+" closed="+closed+" deadlineNs="+deadline+" failure="+failure;}
}
