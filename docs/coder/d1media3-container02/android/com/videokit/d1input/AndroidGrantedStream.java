package com.videokit.d1input;
import android.os.ParcelFileDescriptor;import android.system.Os;import com.videokit.spike.c14.*;import com.videokit.spike.e4.E4Owned;
import java.io.*;import java.util.concurrent.*;
/** Host already registered/adopted this granted descriptor/stream in its original E4Owned holder.
 * SDK opens no path and owns no second FD closer. Host retains authorization/fence/reopen authority. */
public final class AndroidGrantedStream implements HostOutput {
 public interface Authority extends SinkCoordinator.Host,HostOutput.Originals {
  CompletionStage<AsyncReadBridge.Provider> reopenReadOnly();
  default SinkCoordinator.Status originalTerminalStatus(String task){return new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);}
 }
 private final E4Owned<ParcelFileDescriptor.AutoCloseOutputStream> original;private final ParcelFileDescriptor sameFd;private final Authority authority;private final String task;
 private volatile int active;private long position;private boolean failed;
 public AndroidGrantedStream(String task,E4Owned<ParcelFileDescriptor.AutoCloseOutputStream> original,ParcelFileDescriptor sameFd,Authority authority){this.task=task;this.original=original;this.sameFd=sameFd;this.authority=authority;}
 public String opaqueTask(){return task;}public Capabilities capabilities(){return new Capabilities(true,false,true,true,true);}
 private <T>CompletionStage<T> failed(Throwable t){CompletableFuture<T> f=new CompletableFuture<>();f.completeExceptionally(PlatformOutputErrors.map(t));return f;}
 public CompletionStage<Integer> writeAt(long at,byte[] bytes,int offset,int count){active++;try{AndroidInput.WORKER.requireWorker();if(failed||at!=position||count<1||count>65536)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");original.original().write(bytes,offset,count);position+=count;return CompletableFuture.completedFuture(count);}catch(Throwable t){failed=true;return failed(t);}finally{active--;}}
 public CompletionStage<Void> flush(){active++;try{AndroidInput.WORKER.requireWorker();original.original().flush();Os.fsync(sameFd.getFileDescriptor());return CompletableFuture.completedFuture(null);}catch(Throwable t){return failed(t);}finally{active--;}}
 public CompletionStage<Void> closeWriter(){active++;try{AndroidInput.WORKER.requireWorker();original.close();return CompletableFuture.completedFuture(null);}catch(Throwable t){return failed(t);}finally{active--;}}
 public boolean originalOperationsReturned(){return active==0&&authority.originalOperationsReturned();}public boolean writerOriginalsReturned(){return active==0&&original.returned();}
 public SinkCoordinator.Status originalTerminalStatus(String task){return authority.originalTerminalStatus(task);}
 public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){return authority.reopenReadOnly();}
 public CompletionStage<String> markReady(String id){return authority.markReady(id);}public CompletionStage<SinkCoordinator.Status> query(String id){return authority.query(id);}public CompletionStage<Void> abort(String id){return authority.abort(id);}
}
