package com.videokit.spike.e4;

import java.io.IOException;

/** Actual synchronous callback return ledger. Cancellation/ACK failure never completes an active call. */
public final class E5CallbackGate {
    private int inFlight,entered,returned;private boolean startAck,failed,cancelled;
    public static boolean synchronous(int flags){return (flags&1)==0;}
    public final class Call {
        final Thread original=Thread.currentThread();final boolean start;boolean done;
        Call(boolean start){this.start=start;}
        public void returned(boolean ack)throws IOException{
            synchronized(E5CallbackGate.this){
                if(Thread.currentThread()!=original || done)throw new IOException("E5_CALLBACK_ORIGINAL_RETURN_REQUIRED");
                done=true;inFlight--;returned++;if(!ack)failed=true;if(start && ack)startAck=true;
            }
        }
    }
    public synchronized Call enter(String status)throws IOException{
        if(failed || entered>=128 || inFlight!=0)throw new IOException("E5_CALLBACK_ADMISSION_REFUSED");
        entered++;inFlight++;return new Call("STARTED".equals(status));
    }
    public synchronized void cancel(){cancelled=true;}
    public synchronized boolean startProven(){return startAck && !failed && !cancelled;}
    public synchronized boolean startAckReturned(){return startAck;}
    public synchronized boolean ackFailed(){return failed;}
    public synchronized int inFlight(){return inFlight;}
    public synchronized int entered(){return entered;}
    public synchronized int returned(){return returned;}
}
