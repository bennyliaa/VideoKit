package com.videokit.spike.e4;
import java.util.*;
import java.util.concurrent.Semaphore;
/** One original runner completion, woken by actual return events; never a timer-to-release gate. */
public final class E13FinishOwner {
 public interface Port {boolean canFinish();void finish(int code,Object saved)throws Exception;boolean mainThread();default void awaitOriginalReturns()throws Exception{}}
 private static volatile boolean admissionClosed;
 public static synchronized void requireAdmission(){if(admissionClosed)throw new IllegalStateException("E13_COMPLETION_SEALED_NO_NEW_WORK");}
 public static synchronized void admit(Runnable originalRegistration){requireAdmission();originalRegistration.run();}
 private static final Set<E13FinishOwner> OWNERS=java.util.concurrent.ConcurrentHashMap.newKeySet();
 private final Port port;private final Semaphore changed=new Semaphore(0);private final E13ReturnEvents.Listener listener=this::wake;
 public final String id=E13Stages.owner("runner");private Thread worker;private Object saved;private int code;private boolean requested,attempted,failed,subscribed=true,returned;private String failure="NONE";
 public E13FinishOwner(Port p){port=Objects.requireNonNull(p);OWNERS.add(this);E13ReturnEvents.subscribe(listener);}
 private void wake(){if(changed.availablePermits()==0)changed.release();}
 /** Caller supplies a private immutable/deep copy. First result wins; later failures can only lower qualification. */
 public void request(int c,Object copy){Thread launch=null;String detail=null;synchronized(this){if(!requested){synchronized(E13FinishOwner.class){admissionClosed=true;}requested=true;code=c;saved=copy;worker=new Thread(this::run,"e13-original-finalizer-"+id);worker.setDaemon(true);launch=worker;detail="code="+c+" publishedAt="+System.nanoTime();}wake();}if(launch!=null){try{launch.start();}catch(Throwable t){synchronized(this){failed=true;failure="FINALIZER_START_UNKNOWN";}E13Stages.at(id,"FINALIZER_UNKNOWN","FINALIZER_START_UNKNOWN");}E13Stages.at(id,"FINISH_REQUEST",detail);}}
 public void fail(String why){String detail;synchronized(this){if(!failed){failed=true;failure=why;}detail=why;wake();}E13Stages.at(id,"ORIGINAL_FAILURE",detail);}
 public synchronized boolean failed(){return failed;}public synchronized String failure(){return failure;}
 public synchronized boolean attempted(){return attempted;}public synchronized boolean returned(){return returned;}
 private void run(){
  try{for(;;){changed.acquire();port.awaitOriginalReturns();long v=E13ReturnEvents.version();if(!port.canFinish()){E13Stages.at(id,"FINISH_PENDING","returnVersion="+v);continue;}
    int c;Object r;synchronized(this){if(attempted)return;attempted=true;c=code;r=saved;}
    E13ReturnEvents.unsubscribe(listener);synchronized(this){subscribed=false;}
    if(port.mainThread())throw new IllegalStateException("E13_FINALIZER_MUST_NOT_BE_MAIN");
    E13Stages.at(id,"PLATFORM_FINISH_ENTER","failed="+failed());port.finish(c,r);synchronized(this){returned=true;}E13Stages.at(id,"PLATFORM_FINISH_RETURN","actual=true");OWNERS.remove(this);return;
   }}catch(Throwable t){synchronized(this){failed=true;failure=t.getClass().getName();}E13Stages.at(id,"FINALIZER_UNKNOWN",failure);}
 }
 public synchronized String state(){return "requested="+requested+" attempted="+attempted+" returned="+returned+" failed="+failed+" subscribed="+subscribed+" worker="+(worker==null?"NOT_STARTED":worker.getState());}
 public static int retained(){return OWNERS.size();}
}
