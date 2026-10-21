package com.videokit.spike.e4;

import java.io.IOException;

/** Production CONTROL return barrier. The admitted call is counted until its actual finally. */
public final class E4ReturnGate {
    private int calls;private boolean ownerReturned,finishClaimed;
    public synchronized void admit()throws IOException{if(ownerReturned || finishClaimed)throw new IOException("E4A_CONTROL_AFTER_OWNER");if(calls>=2)throw new IOException("E4A_CONTROL_BUDGET");calls++;}
    public synchronized void returned(){if(calls<=0)throw new IllegalStateException("control underflow");calls--;notifyAll();}
    public synchronized void ownerReturned(){ownerReturned=true;notifyAll();}
    public synchronized int inFlight(){return calls;}
    public void runAdmitted(Runnable call,Runnable afterActualReturn){try{call.run();}finally{returned();afterActualReturn.run();}}
    public synchronized boolean drained(){return ownerReturned && calls==0;}
    public synchronized boolean claimFinish(){if(!drained() || finishClaimed)return false;finishClaimed=true;return true;}
}
