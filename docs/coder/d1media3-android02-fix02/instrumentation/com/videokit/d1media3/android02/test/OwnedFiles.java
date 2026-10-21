package com.videokit.d1media3.android02.test;
import com.videokit.d1android.*;import com.videokit.d1input.*;import com.videokit.spike.c14.*;import com.videokit.spike.e4.*;
import java.io.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
/** Exact new private files only. No post-open FileOutputStream wrapper or alias close authority. */
final class OwnedFiles {
 static <T>CompletionStage<T> failed(Throwable e){CompletableFuture<T> f=new CompletableFuture<>();f.completeExceptionally(e);return f;}
 /** This OutputStream object and raw keeper exist in Job BEFORE Os.open. It is the sole closer. */
 static final class RawWrite extends OutputStream {
  final ExperimentJob job;final File file;final String role;final ScopeMeter.Descriptor slot;final OriginalOwner<FileDescriptor> owner;
  volatile boolean flushReturned,syncReturned;
  RawWrite(ExperimentJob job,File file,String role)throws IOException{this.job=job;this.file=file;this.role=role;slot=job.meter.descriptor(role,true);owner=new OriginalOwner<>(role,fd->{try{android.system.Os.close(fd);slot.closed();}catch(Throwable t){slot.unknown();throw t;}});}
  void open()throws IOException{try{owner.allocate(()->android.system.Os.open(file.getAbsolutePath(),android.system.OsConstants.O_WRONLY|android.system.OsConstants.O_CREAT|android.system.OsConstants.O_EXCL|android.system.OsConstants.O_NOFOLLOW,0600));slot.adopted();}catch(Throwable e){slot.unknown();throw OriginalIO.map(e);}}
  public void write(int value)throws IOException{write(new byte[]{(byte)value},0,1);}
  public void write(byte[] b,int off,int n)throws IOException{
   Objects.checkFromIndexSize(off,n,b.length);if(n==0)return;job.requireAdmission();final String phase=job.meterPhase();job.meter.outputRequest(phase,n);
   int done=0;while(done<n){final int start=off+done,request=n-done;job.requireAdmission();int got=owner.call("WRITE",fd->{job.meter.outputAttempt(phase,request);try{int value=android.system.Os.write(fd,b,start,request);job.meter.outputReturned(phase,request,value);return value;}catch(Throwable e){job.meter.outputUnknown(phase,request);throw e;}});if(got<1)throw new IOException("INVALID_WRITE_RESULT");done+=got;}
  }
  public void flush()throws IOException{owner.call("JAVA_UNBUFFERED_FLUSH",fd->{flushReturned=true;return null;});}
  void sync()throws IOException{owner.call("FSYNC",fd->{android.system.Os.fsync(fd);syncReturned=true;return null;});}
  public void close()throws IOException{if(!owner.closeOnce())throw new IOException("RAW_FD_ORIGINAL_CLOSE_UNKNOWN");}
  boolean returned(){return owner.returned();}
  Map<String,Object> snapshot(){Map<String,Object> m=new LinkedHashMap<>(owner.snapshot());m.put("flushReturned",flushReturned);m.put("syncReturned",syncReturned);m.put("platformStreamAliases",0);m.put("nativeCloser","SAME_OWNED_RAW_OS_CLOSE_ONCE");return m;}
 }
 private static final class OriginalIO{static IOException map(Throwable e){return e instanceof IOException?(IOException)e:new IOException("RAW_FD_API_UNPROVEN",e);}}
 static final class ReadCapability implements AsyncReadBridge.Provider {
  final ExperimentJob job;final File file;final boolean unknown;final int chunk;
  final List<OriginalOwner<RandomAccessFile>> originals=new CopyOnWriteArrayList<>();final Set<OriginalOwner<RandomAccessFile>> handed=ConcurrentHashMap.newKeySet();final List<String> epochs=new ArrayList<>();final List<Long> firstOffsets=new ArrayList<>();
  final AtomicInteger nativeReads=new AtomicInteger();volatile HostInputFactory factory;long physicalBytes,readCalls;int opens,closes,peak,eofReads;
  ReadCapability(ExperimentJob job,File file,boolean unknown,int chunk){this.job=job;this.file=file;this.unknown=unknown;this.chunk=chunk;}
  public CompletionStage<AsyncReadBridge.Handle> open(AsyncReadBridge.Cancellation token){
   try{job.requireAdmission();job.observeSources();final ScopeMeter.Descriptor slot=job.meter.descriptor("READ_RAF",true);final OriginalOwner<RandomAccessFile> owner=new OriginalOwner<>("READ_RAF",raf->{try{raf.close();slot.closed();}catch(Throwable t){slot.unknown();throw t;}});
    synchronized(this){if(originals.size()>=18)throw new IOException("FINITE_NATIVE_HANDLE_BUDGET");originals.add(owner);opens++;E13SourceGroup.Identity id=factory==null?null:factory.sourceIdentity();epochs.add(id==null?"SDK_IDENTITY_IN_RANGE_EVIDENCE":id.instance+":"+id.epoch);}
    try{owner.allocate(()->new RandomAccessFile(file,"r"));slot.adopted();}catch(Throwable e){slot.unknown();throw e;}final long size=owner.call("LENGTH",RandomAccessFile::length);
    AsyncReadBridge.Handle handle=new AsyncReadBridge.Handle(){boolean first=true;final AtomicBoolean closeEntered=new AtomicBoolean();
     public Long length(){return unknown?null:size;}
     public CompletionStage<Integer> readAt(long at,byte[] b,int off,int count,AsyncReadBridge.Cancellation cancel){
      boolean entered=false;String phase=job.meterPhase();boolean sdkReserved=false;try{job.requireAdmission();if(at<0||count<1||count>65536||at>size)throw new IOException("INVALID_RANGE");job.meter.input(phase,ScopeMeter.Count.SDK_REQUEST,count);sdkReserved=true;
       if(nativeReads.incrementAndGet()!=1){nativeReads.decrementAndGet();throw new IOException("READ_IN_FLIGHT");}entered=true;
       synchronized(ReadCapability.this){peak=Math.max(peak,nativeReads.get());readCalls++;if(first){firstOffsets.add(at);first=false;}}
       int n=(int)Math.min(Math.min(count,chunk),size-at);final int request=n==0?1:n;
       int actual=owner.call("READ_AT",raf->{raf.seek(at);job.meter.nativeAttempt(phase,request);try{int value=n==0?raf.read():raf.read(b,off,n);if(n==0&&value!=-1)throw new IOException("PRIVATE_FIXTURE_CHANGED");job.meter.returned(phase,ScopeMeter.Count.NATIVE_ACTUAL,ScopeMeter.Count.NATIVE_EOF,request,value);return value;}catch(Throwable e){job.meter.inputUnknown(phase,ScopeMeter.Count.NATIVE_UNKNOWN,request);throw e;}});
       job.meter.returned(phase,ScopeMeter.Count.SDK_ACTUAL,ScopeMeter.Count.SDK_EOF,count,actual);
       synchronized(ReadCapability.this){if(actual<0)eofReads++;else physicalBytes+=actual;}return CompletableFuture.completedFuture(actual);
      }catch(Throwable t){if(sdkReserved)try{job.meter.inputUnknown(phase,ScopeMeter.Count.SDK_FAILED_REQUEST,count);}catch(IOException limit){}job.fail(ExperimentJob.safe(t));return failed(t);}finally{if(entered)nativeReads.decrementAndGet();}
     }
     public CompletionStage<Void> closeAsync(){if(!closeEntered.compareAndSet(false,true))return failed(new IOException("ORIGINAL_CLOSE_ALREADY_ENTERED"));
      try{if(!job.stopped&&"NONE".equals(owner.snapshot().get("firstFailure"))){try{owner.call("CLOSE_EOF_WITNESS",raf->{if(raf.getFilePointer()==size){String phase=job.meterPhase();job.meter.input(phase,ScopeMeter.Count.DIRECT_EOF,1);job.meter.nativeAttempt(phase,1);int eof=raf.read();job.meter.returned(phase,ScopeMeter.Count.NATIVE_ACTUAL,ScopeMeter.Count.NATIVE_EOF,1,eof);if(eof!=-1)throw new IOException("PRIVATE_FIXTURE_CHANGED");synchronized(ReadCapability.this){eofReads++;}}return null;});}catch(Throwable probe){job.fail("NATIVE_EOF_WITNESS_FAILED");}}
       if(!owner.closeOnce())throw new IOException("NATIVE_CLOSE_UNKNOWN");synchronized(ReadCapability.this){closes++;}return CompletableFuture.completedFuture(null);
      }catch(Throwable t){job.fail("NATIVE_CLOSE_UNKNOWN");return failed(t);}
     }
    };handed.add(owner);return CompletableFuture.completedFuture(handle);
   }catch(Throwable t){return failed(t);}
  }
  void closeUnclaimed(){for(OriginalOwner<RandomAccessFile> o:originals)if(!handed.contains(o))try{if(!o.closeOnce())job.fail("UNCLAIMED_FD_ORIGINAL_UNKNOWN");}catch(Throwable e){job.fail("UNCLAIMED_FD_ORIGINAL_UNKNOWN");}}
  synchronized boolean descriptorsReturned(){for(OriginalOwner<?> owner:originals)if(!owner.returned())return false;return nativeReads.get()==0;}
 }
 static final class OutputCapability implements HostOutput {
  final ExperimentJob job;final File file;final RawWrite original;final ReadCapability readback;final String task="android02_fix02_mux_private";final AtomicInteger active=new AtomicInteger();
  long bytes,attempted;int flushes,closes,reopens,readyCalls;boolean flushReturned;SinkCoordinator.HostState terminal=SinkCoordinator.HostState.WRITING;
  OutputCapability(ExperimentJob job,File file)throws Exception{this.job=job;this.file=file;readback=new ReadCapability(job,file,false,65536);original=new RawWrite(job,file,"MUX_DEST");job.outputHost=this;job.rawWriters.add(original);original.open();}
  public String opaqueTask(){return task;}public Capabilities capabilities(){return new Capabilities(true,false,true,true,true);}
  public CompletionStage<Integer> writeAt(long at,byte[] b,int off,int n){active.incrementAndGet();try{job.requireAdmission();AndroidInput.WORKER.requireWorker();if(at!=bytes||n<1||n>65536||n>16777216-attempted)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");attempted+=n;original.write(b,off,n);bytes+=n;return CompletableFuture.completedFuture(n);}catch(Throwable t){return failed(PlatformOutputErrors.map(t));}finally{active.decrementAndGet();}}
  public CompletionStage<Void> flush(){active.incrementAndGet();try{AndroidInput.WORKER.requireWorker();original.flush();original.sync();flushes++;flushReturned=true;return CompletableFuture.completedFuture(null);}catch(Throwable t){return failed(PlatformOutputErrors.map(t));}finally{active.decrementAndGet();}}
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
