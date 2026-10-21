package com.videokit.spike.c11;
import java.util.*;

/** Task-local Binder incarnations. Identity keys compare by reference, never caller supplied equality. */
public final class WorkerGenerations {
    public static final int MAX_WORKERS=4;
    public static final class Worker {
        public final Object key; public final int serial,pid,uid; public final boolean primary;
        private boolean dead,hello,stopping,stopAck;private int attempts;private String stopResult="NOT_SENT";
        private Worker(Object key,int serial,int pid,int uid,boolean primary){this.key=key;this.serial=serial;this.pid=pid;this.uid=uid;this.primary=primary;}
        public synchronized boolean dead(){return dead;}
        public synchronized boolean hello(){return hello;}
        public synchronized void validated(int pid,int uid){if(this.pid!=pid || this.uid!=uid)throw new SecurityException("CPU_GENERATION_IDENTITY");hello=true;}
        public synchronized boolean queueStop(){if(dead || stopping || attempts>=3)return false;stopping=true;attempts++;stopResult="QUEUED";return true;}
        public synchronized void stopFinished(){stopFinished("UNKNOWN",false);}
        public synchronized void stopFinished(String result,boolean ack){stopping=false;stopResult=result;stopAck|=ack;}
        public synchronized int stopAttempts(){return attempts;}
        public synchronized boolean stopPending(){return stopping;}
        public synchronized boolean stopAck(){return stopAck;}
        public synchronized String stopResult(){return stopResult;}
    }
    private final ArrayList<Worker> workers=new ArrayList<>();private Worker primary;
    private boolean terminal,closed,overflow;private int rejected;
    public synchronized Worker register(Object key,int pid,int uid){
        if(key==null || pid<=0 || uid<=0)throw new SecurityException("CPU_GENERATION_IDENTITY");
        for(Worker worker:workers)if(worker.key==key){if(worker.pid!=pid || worker.uid!=uid)throw new SecurityException("CPU_GENERATION_IDENTITY");return worker;}
        if(workers.size()>=MAX_WORKERS){overflow=true;terminal=true;throw new IllegalStateException("CPU_GENERATION_OVERFLOW_QUARANTINED");}
        boolean first=workers.isEmpty() && !terminal && !closed;
        Worker worker=new Worker(key,workers.size()+1,pid,uid,first);workers.add(worker);
        if(first)primary=worker;else rejected++;
        return worker;
    }
    public synchronized Worker find(Object key){for(Worker w:workers)if(w.key==key)return w;return null;}
    public synchronized Worker primary(){return primary;}
    public synchronized boolean accept(Worker w){return w!=null && w==primary && !terminal && !closed && !w.dead();}
    public synchronized boolean died(Worker w){if(w==null || !workers.contains(w))return false;synchronized(w){w.dead=true;}if(w==primary){terminal=true;return true;}return false;}
    public synchronized void terminate(){terminal=true;}
    public synchronized void quarantine(){overflow=true;terminal=true;}
    public synchronized void bindingClosed(){closed=true;}
    public synchronized boolean closed(){return closed;}
    public synchronized boolean terminal(){return terminal;}
    public synchronized boolean allDead(){if(overflow || workers.isEmpty())return false;for(Worker w:workers)if(!w.dead())return false;return true;}
    public synchronized boolean canRelease(){return closed && allDead();}
    public synchronized int unresolved(){int n=overflow?1:0;for(Worker w:workers)if(!w.dead())n++;return n;}
    public synchronized int rejected(){return rejected;}
    public synchronized List<Worker> snapshot(){return List.copyOf(workers);}
}
