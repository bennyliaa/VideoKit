package com.videokit.d1input;
import com.videokit.spike.c14.*;import java.util.concurrent.*;
/** Temporary host capability; no path/credential constructor and no final M0 API claim. */
public interface HostOutput extends SinkCoordinator.Host {
 final class Capabilities {
  public final boolean sequential,random,flush,close,reopen;
  public Capabilities(boolean sequential,boolean random,boolean flush,boolean close,boolean reopen){this.sequential=sequential;this.random=random;this.flush=flush;this.close=close;this.reopen=reopen;}
 }
 String opaqueTask();Capabilities capabilities();
 CompletionStage<Integer> writeAt(long at,byte[] bytes,int offset,int count);
 CompletionStage<Void> flush();CompletionStage<Void> closeWriter();
 boolean originalOperationsReturned();
 /** Host must prove the SAME writer/descriptor AND all its original tasks physically returned.
  * An async host cannot implement this using merely an early future callback. */
 boolean writerOriginalsReturned();
 CompletionStage<AsyncReadBridge.Provider> reopenReadOnly();
 interface Validator {CompletionStage<Validation> validate(String opaqueTask,long bytes,String sha256);}
 final class Validation {
  public final String task,sha256,kind;public final long bytes;public final boolean structurallyValid;
  public Validation(String task,long bytes,String sha,String kind,boolean valid){this.task=task;this.bytes=bytes;sha256=sha;this.kind=kind;structurallyValid=valid;}
 }
 /** Explicit HOST action after READY, never an implicit side effect of writer close/validation. */
 interface Commit {CompletionStage<Void> commit(String opaqueTask,String readyToken);}
}
