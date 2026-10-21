package com.videokit.d1android;
/** Last controlled marker AFTER the synchronous return signal. This is NOT OS thread exit. */
public final class CompletionPoint {
 public interface Clock{long nanoTime();}public interface Signal{void run()throws Exception;}public interface Failure{void failed(Throwable e);}
 private volatile boolean bodyReturned;private volatile long completedNano;
 public void afterSignal(Signal signal,Clock clock)throws Exception{try{signal.run();}finally{completedNano=clock.nanoTime();bodyReturned=true;}}
 public void finishAfterSignal(Signal signal,Clock clock,Failure failure){try{signal.run();}catch(Throwable t){failure.failed(t);}finally{completedNano=clock.nanoTime();bodyReturned=true;}}
 public boolean bodyReturned(){return bodyReturned;}public long completedNano(){return completedNano;}
 public boolean timely(long started,long limit){long elapsed=completedNano-started;return bodyReturned&&elapsed>=0&&elapsed<limit;}
}
