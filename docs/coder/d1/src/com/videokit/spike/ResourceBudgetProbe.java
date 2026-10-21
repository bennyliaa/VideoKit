package com.videokit.spike;

import java.util.HashMap;
import java.util.Map;

/** Admission policy experiment, not a hardware capacity detector. */
public final class ResourceBudgetProbe {
    private final int videoLimit;
    private final long byteLimit;
    private final Map<String,Long> reservations=new HashMap<>();
    private long reserved;
    public ResourceBudgetProbe(int declaredLimit,long byteLimit){
        if(declaredLimit<0 || byteLimit<0)throw new IllegalArgumentException();
        videoLimit=Math.min(12,declaredLimit);this.byteLimit=byteLimit;
    }
    public synchronized boolean reserve(String id,long bytes){
        if(bytes<0 || reservations.containsKey(id))return false;
        if(reservations.size()>=videoLimit || bytes>byteLimit-reserved)return false;
        reservations.put(id,bytes);reserved+=bytes;return true;
    }
    public synchronized void release(String id){Long bytes=reservations.remove(id);if(bytes!=null)reserved-=bytes;}
    public synchronized long bytes(){return reserved;}
    public static void main(String[] args){
        ResourceBudgetProbe budget=new ResourceBudgetProbe(99,1200);
        for(int i=0;i<12;i++)if(!budget.reserve("slot"+i,100))throw new AssertionError("admission");
        if(budget.reserve("overflow",1))throw new AssertionError("hard limit");
        budget.release("slot0");budget.release("slot0");
        if(budget.reserve("too-large",101))throw new AssertionError("memory limit");
        if(!budget.reserve("replacement",100))throw new AssertionError("reused budget");
        budget.release("slot1");
        if(budget.bytes()!=1100)throw new AssertionError("cross-slot release");
        System.out.println("PASS hard video limit=12, reserve-before-create, overflow rejected, idempotent release, other slots retain reservations");
        System.out.println("NOT_RUN actual codec capacity, peak CPU/GPU memory, thermal degradation, Android native crash isolation");
    }
}
