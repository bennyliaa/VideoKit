package com.videokit.spike.c10;

/** Pure lifecycle facts. No timeout or successful ACK manufactures process death. */
public final class CpuLifecycle {
    public enum Binding { NOT_REQUESTED, REQUESTING, REJECTED, ACCEPTED, CONNECTED }
    public static final class Snapshot {
        public final Binding binding;public final boolean identity,startAck,stopAck,stopPending,actualDeath,sourceReleased,slotReleased;
        public final int stopAttempts,pendingCalls;public final String stopResult,firstCode,firstPhase;
        private Snapshot(CpuLifecycle s){binding=s.binding;identity=s.identity;startAck=s.startAck;stopAck=s.stopAck;stopPending=s.stopPending;actualDeath=s.actualDeath;sourceReleased=s.sourceReleased;slotReleased=s.slotReleased;stopAttempts=s.stopAttempts;pendingCalls=s.pendingCalls;stopResult=s.stopResult;firstCode=s.firstCode;firstPhase=s.firstPhase;}
        public boolean noWorkerProven(){return binding==Binding.NOT_REQUESTED || binding==Binding.REJECTED;}
        public boolean canRelease(){return (noWorkerProven() || actualDeath) && sourceReleased && pendingCalls==0 && !stopPending;}
    }
    private Binding binding=Binding.NOT_REQUESTED;private boolean identity,startAck,stopAck,stopPending,actualDeath,sourceReleased,slotReleased;
    private int stopAttempts,pendingCalls;private String stopResult="NOT_SENT",firstCode="NONE",firstPhase="NONE";
    public synchronized void requestBind(){if(binding!=Binding.NOT_REQUESTED)throw new IllegalStateException("CPU_BIND_STATE");binding=Binding.REQUESTING;}
    public synchronized void bindReturned(boolean accepted){if(binding==Binding.CONNECTED)return;binding=accepted?Binding.ACCEPTED:Binding.REJECTED;notifyAll();}
    public synchronized void connected(){binding=Binding.CONNECTED;notifyAll();}
    public synchronized void identity(){identity=true;notifyAll();}
    public synchronized void started(){startAck=true;notifyAll();}
    public synchronized void firstFailure(String code,String phase){if(firstCode.equals("NONE")){firstCode=code;firstPhase=phase;}notifyAll();}
    public synchronized void callStarted(){pendingCalls++;notifyAll();}
    public synchronized void callFinished(){if(--pendingCalls<0)throw new IllegalStateException("CPU_CALL_UNDERFLOW");notifyAll();}
    public synchronized boolean queueStop(){if(stopPending || actualDeath || stopAttempts>=3)return false;stopPending=true;stopAttempts++;stopResult="QUEUED";notifyAll();return true;}
    public synchronized void stopFinished(String result,boolean acknowledged){stopPending=false;stopResult=result;stopAck|=acknowledged;notifyAll();}
    public synchronized void death(){actualDeath=true;notifyAll();}
    public synchronized void sourceReleased(boolean released){sourceReleased=released;notifyAll();}
    public synchronized boolean releaseSlot(){if(slotReleased || !snapshot().canRelease())return false;slotReleased=true;notifyAll();return true;}
    public synchronized Snapshot snapshot(){return new Snapshot(this);}
    public static boolean environmentReady(int appSetting,boolean appEnabled,int componentSetting,boolean serviceEnabled,boolean visible,boolean isolated,boolean exported){
        return (appSetting==0 || appSetting==1) && appEnabled && (componentSetting==0 || componentSetting==1) && serviceEnabled && visible && isolated && !exported;
    }
}
