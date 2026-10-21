package com.videokit.d1input;
import com.videokit.spike.c14.*;import java.util.concurrent.*;
/** Temporary host capability; no path/credential constructor and no final M0 API claim. */
public interface HostOutput extends SinkCoordinator.Host {
 /** Truth from the authority retaining the SAME original tasks/threads, never an ACK counter. */
 interface Originals {boolean originalOperationsReturned();}
 final class Capabilities {
  public final boolean sequential,random,flush,close,reopen;
  public Capabilities(boolean sequential,boolean random,boolean flush,boolean close,boolean reopen){this.sequential=sequential;this.random=random;this.flush=flush;this.close=close;this.reopen=reopen;}
 }
 String opaqueTask();Capabilities capabilities();
 CompletionStage<Integer> writeAt(long at,byte[] bytes,int offset,int count);
 CompletionStage<Void> flush();CompletionStage<Void> closeWriter();
 boolean originalOperationsReturned();
 /** Optional nonblocking terminal fact from the SAME task's original host arbitration/query.
  * This accessor performs no RPC. Failed/cancelled ACK or returned threads do not prove it. */
 default SinkCoordinator.Status originalTerminalStatus(String opaqueTask){return new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);}
 /** Host must prove the SAME writer/descriptor AND all its original tasks physically returned.
  * An async host cannot implement this using merely an early future callback. */
 boolean writerOriginalsReturned();
 CompletionStage<AsyncReadBridge.Provider> reopenReadOnly();
 interface Validator extends Originals {CompletionStage<Validation> validate(String opaqueTask,long bytes,String sha256);}
 final class Validation {
  public final String task,sha256,kind;public final long bytes;public final boolean structurallyValid;
  public Validation(String task,long bytes,String sha,String kind,boolean valid){this.task=task;this.bytes=bytes;sha256=sha;this.kind=kind;structurallyValid=valid;}
 }
 /** Explicit HOST action after READY, never an implicit side effect of writer close/validation. */
 enum CommitOutcome {UNKNOWN,CONFIRMED_COMMITTED,CONFIRMED_NOT_APPLIED}
 interface Commit extends Originals {
  CompletionStage<Void> commit(String opaqueTask,String readyToken);
  /** Nonblocking truth for THIS exact original COMMIT/task/token, optionally established by
   * its original host query. Must not issue/retry an RPC or infer outcome from cancellation,
   * writer return, READY, absence of ACK, or an unrelated task. UNKNOWN retains the owner. */
  default CommitOutcome originalOutcome(String opaqueTask,String readyToken){return CommitOutcome.UNKNOWN;}
 }
}
