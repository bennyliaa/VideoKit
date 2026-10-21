package com.videokit.spike.e4;
import java.nio.file.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
/** Tester-only bounded probe against unchanged delivered production JAR. No SDK/Android/PC query. */
public class FinalJarProbe {
 public static void main(String[] a)throws Exception{
  if(a[0].equals("finish-lock")){
   AtomicReference<E13FinishOwner> held=new AtomicReference<>();AtomicBoolean requestLocked=new AtomicBoolean(),failureLocked=new AtomicBoolean();CountDownLatch finished=new CountDownLatch(1);
   E13FinishOwner f=new E13FinishOwner(new E13FinishOwner.Port(){public boolean canFinish(){return true;}public boolean mainThread(){return false;}public void finish(int code,Object saved){finished.countDown();}});held.set(f);
   E13Stages.sink(s->{if(s.contains("stage=FINISH_REQUEST"))requestLocked.set(Thread.holdsLock(held.get()));if(s.contains("stage=ORIGINAL_FAILURE"))failureLocked.set(Thread.holdsLock(held.get()));});
   f.request(-1,"TESTER_ONLY_IMMUTABLE_RESULT");if(!finished.await(2,TimeUnit.SECONDS))throw new AssertionError("bounded finisher return");f.fail("TESTER_LOG_LOCK_CHECK");
   if(!requestLocked.get()||!failureLocked.get())throw new AssertionError("expected production lock observation missing");
   System.out.println("REPRODUCED FINISH_REQUEST_sink_holds_owner_lock=true ORIGINAL_FAILURE_sink_holds_owner_lock=true finiteFinalizer=true");
  }else if(a[0].equals("archive-thread")){
   CountDownLatch inNotification=new CountDownLatch(1),release=new CountDownLatch(1);
   E13ReturnEvents.Listener listener=()->{inNotification.countDown();try{if(!release.await(2,TimeUnit.SECONDS))throw new AssertionError("notification bound");}catch(InterruptedException e){throw new RuntimeException(e);}};
   E13ReturnEvents.subscribe(listener);Thread writer=null;
   try{
    E13OperationArchive ar=new E13OperationArchive(Paths.get(a[1]),"tester-original-archive",65536);
    ar.start("TESTER_LOCAL_ARCHIVE_ONLY",List.of("NO_CHILD_OR_SDK"));ar.started(123);ar.append(new byte[]{1,2,3},3);ar.eof();ar.readerDone();ar.processExit(0);
    if(!inNotification.await(2,TimeUnit.SECONDS))throw new AssertionError("notification entered");
    var field=E13OperationArchive.class.getDeclaredField("writer");field.setAccessible(true);writer=(Thread)field.get(ar);
    boolean returned=ar.resourcesReturned(),alive=writer.isAlive();
    if(!returned||!alive)throw new AssertionError("expected flag-before-thread-return window missing");
    System.out.println("REPRODUCED archiveResourcesReturned=true originalWriterIsAlive=true originalFilesClosed=true callbackHeldInOriginalWriter=true syntheticProcessFactsOnly=true");
   }finally{release.countDown();if(writer!=null)writer.join(2500);E13ReturnEvents.unsubscribe(listener);if(writer!=null&&writer.isAlive())throw new AssertionError("tester original writer did not return");}
  }else throw new IllegalArgumentException("finite modes only");
 }
}
