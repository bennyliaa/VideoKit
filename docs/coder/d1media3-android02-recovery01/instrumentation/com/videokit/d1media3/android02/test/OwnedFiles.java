package com.videokit.d1media3.android02.test;
import com.videokit.d1input.*;import com.videokit.spike.c14.*;import com.videokit.spike.e4.*;
import java.io.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
/** Test HOST opens only its exact new private file. SDK receives capabilities,
 * not paths. Native calls are synchronous on the original SDK bridge threads. */
final class OwnedFiles {
 static FileOutputStream createNew(File f)throws IOException{
  try{return new FileOutputStream(android.system.Os.open(f.getAbsolutePath(),android.system.OsConstants.O_WRONLY|android.system.OsConstants.O_CREAT|android.system.OsConstants.O_EXCL|android.system.OsConstants.O_NOFOLLOW,0600));}catch(android.system.ErrnoException e){throw new IOException("CREATE_NEW_PRIVATE_FILE_FAILED",e);}
 }
 static <T>CompletionStage<T> failed(Throwable e){CompletableFuture<T> f=new CompletableFuture<>();f.completeExceptionally(e);return f;}
 static final class ReadCapability implements AsyncReadBridge.Provider {
  final ExperimentJob job;final File file;final boolean unknown;final int chunk;
  final List<E4Owned<RandomAccessFile>> originals=new ArrayList<>();final List<String> epochs=new ArrayList<>();final List<Long> firstOffsets=new ArrayList<>();
  final AtomicInteger nativeReads=new AtomicInteger();volatile HostInputFactory factory;long physicalBytes,readCalls;int opens,closes,peak,eofReads;
  ReadCapability(ExperimentJob job,File file,boolean unknown,int chunk){this.job=job;this.file=file;this.unknown=unknown;this.chunk=chunk;}
  public CompletionStage<AsyncReadBridge.Handle> open(AsyncReadBridge.Cancellation token){
   try{job.requireAdmission();job.observeSources();final E4Owned<RandomAccessFile> owner=new E4Owned<>(file,RandomAccessFile::close);
    synchronized(this){if(originals.size()>=18)throw new IOException("FINITE_NATIVE_HANDLE_BUDGET");originals.add(owner);opens++;E13SourceGroup.Identity id=factory==null?null:factory.sourceIdentity();epochs.add(id==null?"SDK_IDENTITY_IN_RANGE_EVIDENCE":id.instance+":"+id.epoch);}
    owner.allocate(()->new RandomAccessFile(file,"r"));final long size=owner.original().length();
    return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){boolean first=true;final AtomicBoolean closeEntered=new AtomicBoolean();
     public Long length(){return unknown?null:size;}
     public CompletionStage<Integer> readAt(long at,byte[] b,int off,int count,AsyncReadBridge.Cancellation cancel){
      boolean entered=false;try{job.requireAdmission();if(at<0||count<1||count>65536||at>size)throw new IOException("INVALID_RANGE");if(nativeReads.incrementAndGet()!=1){nativeReads.decrementAndGet();throw new IOException("READ_IN_FLIGHT");}entered=true;
       synchronized(ReadCapability.this){peak=Math.max(peak,nativeReads.get());readCalls++;if(first){firstOffsets.add(at);first=false;}}
       int n=(int)Math.min(Math.min(count,chunk),size-at);if(n==0){job.reserveInput(1);owner.original().seek(at);int eof=owner.original().read();job.inputReturned(1,eof<0?-1:1);if(eof!=-1)throw new IOException("PRIVATE_FIXTURE_CHANGED");synchronized(ReadCapability.this){eofReads++;}return CompletableFuture.completedFuture(-1);}
       job.reserveInput(n);owner.original().seek(at);int actual=owner.original().read(b,off,n);job.inputReturned(n,actual);if(actual>0)synchronized(ReadCapability.this){physicalBytes+=actual;}
       return CompletableFuture.completedFuture(actual);
      }catch(Throwable t){job.fail("NATIVE_READ_FAILED");return failed(t);}finally{if(entered)nativeReads.decrementAndGet();}
     }
     public CompletionStage<Void> closeAsync(){if(!closeEntered.compareAndSet(false,true))return failed(new IOException("ORIGINAL_CLOSE_ALREADY_ENTERED"));try{if(!job.stopped&&owner.original().getFilePointer()==size){try{job.reserveInput(1);int eof=owner.original().read();job.inputReturned(1,eof<0?-1:1);if(eof==-1)synchronized(ReadCapability.this){eofReads++;}else job.fail("PRIVATE_FIXTURE_CHANGED");}catch(Throwable probe){job.fail("NATIVE_EOF_WITNESS_FAILED");}}owner.close();synchronized(ReadCapability.this){closes++;}return CompletableFuture.completedFuture(null);}catch(Throwable t){job.fail("NATIVE_CLOSE_UNKNOWN");return failed(t);}}
    });
   }catch(Throwable t){return failed(t);}
  }
  synchronized boolean descriptorsReturned(){for(E4Owned<?> owner:originals)if(!owner.returned())return false;return nativeReads.get()==0;}
 }
 static final class OutputCapability implements HostOutput {
  final ExperimentJob job;final File file;final E4Owned<FileOutputStream> original;
  final ReadCapability readback;final String task="android02_mux_private";final AtomicInteger active=new AtomicInteger();
  long bytes,attempted;int flushes,closes,reopens,readyCalls;boolean flushReturned;SinkCoordinator.HostState terminal=SinkCoordinator.HostState.WRITING;
  OutputCapability(ExperimentJob job,File file)throws Exception{this.job=job;this.file=file;readback=new ReadCapability(job,file,false,65536);original=new E4Owned<>(file,FileOutputStream::close);job.outputHost=this;original.allocate(()->createNew(file));}
  public String opaqueTask(){return task;}public Capabilities capabilities(){return new Capabilities(true,false,true,true,true);}
  public CompletionStage<Integer> writeAt(long at,byte[] b,int off,int n){active.incrementAndGet();try{job.requireAdmission();AndroidInput.WORKER.requireWorker();if(at!=bytes||n<1||n>65536||n>16777216-attempted)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");job.reserveOutput(n);attempted+=n;original.original().write(b,off,n);bytes+=n;return CompletableFuture.completedFuture(n);}catch(Throwable t){return failed(PlatformOutputErrors.map(t));}finally{active.decrementAndGet();}}
  public CompletionStage<Void> flush(){active.incrementAndGet();try{AndroidInput.WORKER.requireWorker();original.original().flush();original.original().getFD().sync();flushes++;flushReturned=true;return CompletableFuture.completedFuture(null);}catch(Throwable t){return failed(PlatformOutputErrors.map(t));}finally{active.decrementAndGet();}}
  public CompletionStage<Void> closeWriter(){active.incrementAndGet();try{AndroidInput.WORKER.requireWorker();original.close();closes++;return CompletableFuture.completedFuture(null);}catch(Throwable t){return failed(PlatformOutputErrors.map(t));}finally{active.decrementAndGet();}}
  public boolean originalOperationsReturned(){return active.get()==0;}public boolean writerOriginalsReturned(){return active.get()==0&&original.returned();}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){reopens++;if(!writerOriginalsReturned()||!flushReturned||reopens!=1||!file.setReadOnly())return failed(new IOException("OUTPUT_REOPEN_FAILED"));return CompletableFuture.completedFuture(readback);}
  public CompletionStage<String> markReady(String id){readyCalls++;return failed(new IOException("HOST_STRUCTURE_IS_NOT_READY"));}
  public CompletionStage<Void> abort(String id){terminal=SinkCoordinator.HostState.ABORTED;return CompletableFuture.completedFuture(null);}
  public CompletionStage<SinkCoordinator.Status> query(String id){return CompletableFuture.completedFuture(new SinkCoordinator.Status(terminal,null));}
  public SinkCoordinator.Status originalTerminalStatus(String id){return new SinkCoordinator.Status(terminal,null);}
 }
 private OwnedFiles(){}
}
