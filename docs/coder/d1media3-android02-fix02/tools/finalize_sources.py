from pathlib import Path
B=Path(__file__).resolve().parents[1]
def edit(rel,a,b):
 p=B/rel;s=p.read_text();assert a in s,(rel,a[:60]);p.write_text(s.replace(a,b),encoding='utf-8')
F='instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java'
edit(F,'final List<OriginalOwner<RandomAccessFile>> originals=new CopyOnWriteArrayList<>();','final List<OriginalOwner<RandomAccessFile>> originals=new CopyOnWriteArrayList<>();final Set<OriginalOwner<RandomAccessFile>> handed=ConcurrentHashMap.newKeySet();')
edit(F,'return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){','AsyncReadBridge.Handle handle=new AsyncReadBridge.Handle(){')
edit(F,'    });\n   }catch(Throwable t){return failed(t);}','    };handed.add(owner);return CompletableFuture.completedFuture(handle);\n   }catch(Throwable t){return failed(t);}')
edit(F,'  synchronized boolean descriptorsReturned()','  void closeUnclaimed(){for(OriginalOwner<RandomAccessFile> o:originals)if(!handed.contains(o))try{if(!o.closeOnce())job.fail("UNCLAIMED_FD_ORIGINAL_UNKNOWN");}catch(Throwable e){job.fail("UNCLAIMED_FD_ORIGINAL_UNKNOWN");}}\n  synchronized boolean descriptorsReturned()')
edit(F,'boolean entered=false;try{job.requireAdmission();','boolean entered=false;String phase=job.meterPhase();boolean sdkReserved=false;try{job.requireAdmission();')
edit(F,'final String phase=job.meterPhase();job.meter.input(phase,ScopeMeter.Count.SDK_REQUEST,count);','job.meter.input(phase,ScopeMeter.Count.SDK_REQUEST,count);sdkReserved=true;')
# phase captured once before IO and never changed by completion/seek on a later case.
edit(F,'int actual=owner.call("READ_AT",raf->{raf.seek(at);job.meter.nativeAttempt(phase,request);int value=n==0?raf.read():raf.read(b,off,n);if(n==0&&value!=-1)throw new IOException("PRIVATE_FIXTURE_CHANGED");job.meter.returned(phase,ScopeMeter.Count.NATIVE_ACTUAL,ScopeMeter.Count.NATIVE_EOF,request,value);return value;});','int actual=owner.call("READ_AT",raf->{raf.seek(at);job.meter.nativeAttempt(phase,request);try{int value=n==0?raf.read():raf.read(b,off,n);if(n==0&&value!=-1)throw new IOException("PRIVATE_FIXTURE_CHANGED");job.meter.returned(phase,ScopeMeter.Count.NATIVE_ACTUAL,ScopeMeter.Count.NATIVE_EOF,request,value);return value;}catch(Throwable e){job.meter.inputUnknown(phase,ScopeMeter.Count.NATIVE_UNKNOWN,request);throw e;}});')
edit(F,'}catch(Throwable t){job.fail("NATIVE_READ_FAILED");return failed(t);}', '}catch(Throwable t){if(sdkReserved)try{job.meter.inputUnknown(phase,ScopeMeter.Count.SDK_FAILED_REQUEST,count);}catch(IOException limit){}job.fail(ExperimentJob.safe(t));return failed(t);}')
J='instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java'
edit(J,'private static String safe(Throwable e)','static String safe(Throwable e)')
edit(J,'  boolean muxerReturned=true;','  for(OwnedFiles.ReadCapability p:providers)p.closeUnclaimed();\n  boolean muxerReturned=true;')
# Account real controlled-port ACK separately, never as native file transfer.
edit(J,'BoundaryScenarios.run(method.name(),AndroidInput.WORKER);status=','BoundaryScenarios.Result controlled=BoundaryScenarios.run(method.name(),AndroidInput.WORKER);meter.controlledAcknowledged(p,controlled.inputAck,controlled.outputAck);status=')
C='src/com/videokit/d1input/BoundaryScenarios.java'
edit(C,' public static void run(String name,WorkerRule rule)throws Exception{',' public static final class Result{public final int inputAck,outputAck;Result(int i,int o){inputAck=i;outputAck=o;}}\n public static Result run(String name,WorkerRule rule)throws Exception{')
edit(C,'rule.requireWorker();if(name.equals("cancelLateRead"))cancelRead(rule);else if(name.equals("writerPending"))writer(rule);else throw new IOException("BOUNDARY_CASE_REJECTED");','rule.requireWorker();Result result;if(name.equals("cancelLateRead"))result=cancelRead(rule);else if(name.equals("writerPending"))result=writer(rule);else throw new IOException("BOUNDARY_CASE_REJECTED");')
edit(C,'need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0);','need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0);return result;')
edit(C,'private static void cancelRead(WorkerRule rule)throws Exception','private static Result cancelRead(WorkerRule rule)throws Exception')
edit(C,'  need(caller[0]==99);','  need(caller[0]==99);return new Result(read.getNow(0),0);')
edit(C,'Thread original;boolean closed;int reopen,closeCalls,ready;','Thread original;boolean closed;int reopen,closeCalls,ready,written;')
edit(C,'public CompletionStage<Integer> writeAt(long at,byte[] b,int off,int n){return CompletableFuture.completedFuture(n);}','public CompletionStage<Integer> writeAt(long at,byte[] b,int off,int n){written+=n;return CompletableFuture.completedFuture(n);}')
edit(C,'private static void writer(WorkerRule rule)throws Exception','private static Result writer(WorkerRule rule)throws Exception')
edit(C,'need(out.abort()&&out.returned());}\n }','need(out.abort()&&out.returned());}\n  return new Result(0,host.written);\n }')
I='instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java'
edit(I,'b.putString("receipt",text);b.putString("status",semantic);','j.reserveReceiptEmission(text);b.putString("receipt",text);b.putString("status",semantic);')
edit(I,'pending.putString("receipt",bounded(j.receipt(false)));sendStatus','String pendingText=bounded(j.receipt(false));j.reserveReceiptEmission(pendingText);pending.putString("receipt",pendingText);sendStatus')
edit(I,'if(!j.canFinish())sendStatus(-2,result);','if(!j.canFinish()){j.reserveReceiptEmission(text);sendStatus(-2,result);}')
print('ReadAt unknown layers, unclaimed original handle cleanup, immutable receipt emission budget and controlled ACK layers finished')
