package com.videokit.d1input;
import androidx.media3.datasource.DataSpec;import com.videokit.spike.c14.*;
import java.io.*;import java.nio.*;import java.nio.channels.*;import java.security.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;

/** ACK facts never prove physical return. Original truth remains with the same host authorities,
 * original read registry/workers and existing SinkCoordinator. Cached views observe the original
 * invocation (not a replacement task); no new executor, release ledger or return counter. */
public final class TemporaryOutput {
 public static final long MAX_OUTPUT=16L*1024*1024;private static final Set<TemporaryOutput> OWNERS=ConcurrentHashMap.newKeySet();
 private final HostOutput host;private final String task;private final WorkerRule worker;private final long timeoutMs;private final SinkCoordinator coordinator;
 private final AtomicBoolean cancelled=new AtomicBoolean(),ownerCall=new AtomicBoolean();private final WritableByteChannel channel=new Channel();
 private volatile CompletableFuture<?> pending;private volatile boolean invoking,coordinatorInvoking,producerClosed,flushAttempted,flushed,closeAttempted,closeReturned,closeSucceeded,validated,ready,commitAttempted,commitAcknowledged,aborted,released;
 private volatile boolean reopenAttempted,validationAttempted;private volatile HostOutput.Validator validatorOriginal;private volatile HostOutput.Commit commitOriginal;
 private volatile boolean hostInspectionAttempted,hostInspectionActive;private volatile HostMp4Inspection.Evidence hostStructure;
 private volatile HostOutput.CommitOutcome commitOutcome=HostOutput.CommitOutcome.UNKNOWN;
 private volatile boolean terminalProtocolUnknown;
 private volatile AsyncReadBridge.Provider reopenedProvider;private volatile HostOutput.Validation validationReceipt;private volatile HostInputFactory reopenedInput;private volatile boolean reopenedInputClosed,hashComplete;
 private volatile CompletableFuture<String> readyView;private volatile CompletableFuture<Void> abortView;private volatile CompletableFuture<SinkCoordinator.Status> queryView;
 private volatile CompletionStage<?> readyOriginalStage,abortOriginalStage,queryOriginalStage;private volatile boolean readyEntered,abortEntered,queryEntered;private volatile String readyToken;
 private volatile CompletableFuture<?> readyObserverStage,abortObserverStage,queryObserverStage;
 private volatile boolean readyResponseReceived,readyResponseSucceeded,readyResponseAccepted;private volatile String readyResponseRejection="NONE",terminalRejectionSource="NONE",terminalRejectionReason="NONE";private volatile String originalReadyResponseToken;
 private volatile String readyPhase="NOT_ADMITTED",abortPhase="NOT_ADMITTED",queryPhase="NOT_ADMITTED";
 private volatile String firstFailure,sha="UNVERIFIED",validationKind="NONE";private volatile long written,extent,writeAttemptedBytes;private final boolean random;
 private volatile String opKind="NONE",flushPhase="NOT_ADMITTED",closePhase="NOT_ADMITTED",reopenPhase="NOT_ADMITTED",validationPhase="NOT_ADMITTED",commitPhase="NOT_ADMITTED";
 private volatile long opOffset;private volatile int opCount;private volatile byte[] originalBlock;private volatile boolean writeAmountUnknown,unknownRecordedForOriginal;private volatile long unknownWriteReservation;
 private final MessageDigest sequentialDigest=digest();private String expectedSequentialSha;
 public TemporaryOutput(HostOutput host,boolean requireRandom,WorkerRule worker,long timeoutMs)throws IOException {
  this.host=Objects.requireNonNull(host);this.worker=Objects.requireNonNull(worker);this.timeoutMs=timeoutMs;
  HostOutput.Capabilities c;try{task=host.opaqueTask();c=host.capabilities();}catch(Throwable t){throw Failures.io(t,"OUTPUT_GRANT_INVALID");}
  if(timeoutMs<=0||timeoutMs>5000||task==null||!task.matches("[A-Za-z0-9_-]{1,64}"))throw new IOException("OUTPUT_GRANT_INVALID");
  if(c==null||!c.sequential||requireRandom&&!c.random||!c.flush||!c.close||!c.reopen)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");random=requireRandom;
  synchronized(OWNERS){if(OWNERS.size()>=2)throw new IOException("OUTPUT_RESOURCE_EXHAUSTED");OWNERS.add(this);}
  coordinator=new SinkCoordinator(task,new SinkCoordinator.Host(){public CompletionStage<String> markReady(String id){return readyHost(id);}public CompletionStage<Void> abort(String id){return abortHost(id);}public CompletionStage<SinkCoordinator.Status> query(String id){return queryHost(id);}},timeoutMs);coordinator.start();
 }
 private void enter()throws IOException {worker.requireWorker();if(!ownerCall.compareAndSet(false,true))throw new IOException("OUTPUT_ORIGINAL_PENDING");}private void leave(){ownerCall.set(false);}
 private synchronized void fail(String code){if(firstFailure==null)firstFailure=code;}
 private void recordWriteUnknown(){writeAmountUnknown=true;if(!unknownRecordedForOriginal){unknownWriteReservation+=opCount;unknownRecordedForOriginal=true;}}
 private boolean validatorReturned(){try{return validatorOriginal==null||validatorOriginal.originalOperationsReturned();}catch(Throwable unknown){return false;}}
 private boolean commitReturned(){try{return commitOriginal==null||commitOriginal.originalOperationsReturned();}catch(Throwable unknown){return false;}}
 private boolean readOriginalsReturned(){try{return reopenedInput==null||reopenedInputClosed&&reopenedInput.originalsReturned();}catch(InterruptedException e){Thread.currentThread().interrupt();return false;}}
 private boolean allHostOriginalsReturned(){try{return !invoking&&!coordinatorInvoking&&host.originalOperationsReturned()&&validatorReturned()&&commitReturned()&&readOriginalsReturned();}catch(Throwable unknown){return false;}}
 private void requirePrevious()throws IOException {if(pending!=null||!allHostOriginalsReturned()||!scopedResponsesAnswered())throw new IOException("OUTPUT_ORIGINAL_PENDING");}
 private static boolean answered(boolean entered,CompletableFuture<?> view){return !entered||view!=null&&view.isDone();}
 private boolean scopedResponsesAnswered(){return answered(readyEntered,readyView)&&answered(abortEntered,abortView)&&answered(queryEntered,queryView);}
 private static boolean observerReturned(CompletionStage<?> original,CompletableFuture<?> observer){return original==null||observer!=null&&observer.isDone();}
 private boolean scopedObserversReturned(){return scopedResponsesAnswered()&&observerReturned(readyOriginalStage,readyObserverStage)&&observerReturned(abortOriginalStage,abortObserverStage)&&observerReturned(queryOriginalStage,queryObserverStage);}
 private void phase(String kind,String value){switch(kind){case "FLUSH":flushPhase=value;break;case "CLOSE":closePhase=value;break;case "REOPEN":reopenPhase=value;break;case "VALIDATE":validationPhase=value;break;case "COMMIT":commitPhase=value;break;default:break;}}
 /** Entry flags change only AFTER admission. A throwing invocation stays UNKNOWN/failed. */
 private synchronized <T>T call(String kind,java.util.concurrent.Callable<CompletionStage<T>> method,HostOutput.Originals authority)throws IOException {
  worker.requireWorker();requirePrevious();invoking=true;opKind=kind;phase(kind,"INVOKING");
  switch(kind){case "WRITE":unknownRecordedForOriginal=false;break;case "FLUSH":flushAttempted=true;break;case "CLOSE":closeAttempted=true;break;case "REOPEN":reopenAttempted=true;break;case "VALIDATE":validationAttempted=true;validatorOriginal=(HostOutput.Validator)authority;break;case "COMMIT":commitAttempted=true;commitOriginal=(HostOutput.Commit)authority;break;default:break;}
  try{CompletionStage<T> original=method.call();if(original==null)throw invalidHostResult();pending=original.toCompletableFuture();if(pending==null)throw invalidHostResult();phase(kind,"ACK_PENDING");}
  catch(Throwable t){phase(kind,"INVOCATION_UNKNOWN");if(kind.equals("WRITE"))recordWriteUnknown();IOException mapped=Failures.io(t,fallback(kind));fail(mapped.getMessage());throw mapped;}
  finally{invoking=false;}
  try{@SuppressWarnings("unchecked") T value=(T)pending.get(timeoutMs,TimeUnit.MILLISECONDS);IOException rejected=consumeOriginal(value,null);if(rejected!=null)throw rejected;return value;}
  catch(TimeoutException e){if(kind.equals("WRITE"))recordWriteUnknown();fail("OUTPUT_TIMEOUT_PENDING");throw new IOException("OUTPUT_TIMEOUT_PENDING");}
  catch(InterruptedException e){if(kind.equals("WRITE"))recordWriteUnknown();Thread.currentThread().interrupt();cancel();fail("CANCELLED");throw new IOException("CANCELLED");}
  catch(ExecutionException|CancellationException e){IOException mapped=Failures.io(e,fallback(kind));consumeOriginal(null,mapped);throw mapped;}
 }
 private <T>T call(String k,java.util.concurrent.Callable<CompletionStage<T>> c)throws IOException{return call(k,c,null);}
 private static String fallback(String k){return k.equals("REOPEN")?"OUTPUT_REOPEN_FAILED":k.equals("VALIDATE")?"OUTPUT_VALIDATION_FAILED":k.equals("COMMIT")?"OUTPUT_COMMIT_UNKNOWN":"OUTPUT_IO_FAILED";}
 private synchronized boolean observeNow()throws IOException {
  CompletableFuture<?> p=pending;if(invoking||p!=null&&!p.isDone())return false;if(p==null){observeCommitOutcome();return true;}
  try{consumeOriginal(p.get(),null);}catch(ExecutionException|CancellationException e){consumeOriginal(null,Failures.io(e,fallback(opKind)));}catch(InterruptedException e){Thread.currentThread().interrupt();fail("CANCELLED");throw new IOException("CANCELLED");}observeCommitOutcome();return true;
 }
 public boolean observeOriginal()throws IOException {enter();try{return observeNow()&&scopedResponsesAnswered()&&coordinator.originalResponsesAnswered();}finally{leave();}}
 private synchronized IOException consumeOriginal(Object result,IOException failure)throws IOException {
  if(pending==null)return null;
  if(failure==null&&opKind.equals("WRITE")&&(!(result instanceof Integer)||(Integer)result<1||(Integer)result>opCount))failure=new IOException("OUTPUT_INVALID_WRITE_RESULT");
  if(failure==null&&opKind.equals("REOPEN")&&!(result instanceof AsyncReadBridge.Provider))failure=new IOException("OUTPUT_REOPEN_FAILED");
  if(failure==null&&opKind.equals("VALIDATE")&&(!(result instanceof HostOutput.Validation)||!validValidation((HostOutput.Validation)result)))failure=new IOException("OUTPUT_VALIDATION_FAILED");
  if(failure==null&&(opKind.equals("FLUSH")||opKind.equals("CLOSE")||opKind.equals("COMMIT"))&&result!=null)failure=invalidHostResult();
  phase(opKind,failure==null?"ACKED":"ACK_FAILED");if(failure!=null)fail(failure.getMessage());
  if(opKind.equals("WRITE")&&failure!=null)recordWriteUnknown();
  if(opKind.equals("WRITE")&&failure==null){int n=(Integer)result;if(!random)sequentialDigest.update(originalBlock,0,n);written+=n;extent=Math.max(extent,opOffset+n);}
  if(opKind.equals("FLUSH")&&failure==null)flushed=true;if(opKind.equals("CLOSE")){closeReturned=true;closeSucceeded=failure==null;}
  if(opKind.equals("REOPEN")&&failure==null)reopenedProvider=(AsyncReadBridge.Provider)result;
  if(opKind.equals("VALIDATE")&&failure==null)validationReceipt=(HostOutput.Validation)result;
  if(opKind.equals("COMMIT")&&failure==null){commitAcknowledged=true;if(!acceptCommitOutcome(HostOutput.CommitOutcome.CONFIRMED_COMMITTED,"COMMIT_ACK"))failure=invalidHostResult();}pending=null;originalBlock=null;return failure;
 }
 private void observeCommitOutcome(){
  if(!commitAttempted||commitAcknowledged||commitOutcome!=HostOutput.CommitOutcome.UNKNOWN||pending!=null||!allHostOriginalsReturned())return;
  try{HostOutput.CommitOutcome fact=commitOriginal.originalOutcome(task,readyToken);acceptCommitOutcome(fact,"COMMIT_AUTHORITY");}catch(Throwable unknown){fail("OUTPUT_COMMIT_UNKNOWN");}
 }
 private static IOException invalidHostResult(){return new IOException("OUTPUT_INVALID_HOST_RESULT");}
 private boolean validValidation(HostOutput.Validation p){return p!=null&&p.structurallyValid&&task.equals(p.task)&&p.bytes==extent&&p.bytes>0&&p.bytes<=MAX_OUTPUT&&sha.equals(p.sha256)&&"HOST_ISOLATED_FORMAT_V1".equals(p.kind);}
 private String terminalRejection(SinkCoordinator.Status p){
  if(!SinkCoordinator.validStatus(p))return "INVALID_RESULT";
  if(p.state==SinkCoordinator.HostState.READY){if(aborted)return "CONFLICT_WITH_ABORTED";if(readyToken!=null&&!readyToken.equals(p.token))return "TOKEN_CHANGED";}
  if(p.state==SinkCoordinator.HostState.ABORTED&&ready)return "CONFLICT_WITH_READY";
  if(p.state==SinkCoordinator.HostState.WRITING&&(ready||aborted))return "TERMINAL_REGRESSION";return null;
 }
 /** All first/late ACK, QUERY and readonly facts pass this one atomic adoption gate. */
 private synchronized boolean acceptTerminal(SinkCoordinator.Status p,String source){
  String rejected=terminalRejection(p);if(rejected!=null){terminalRejectionSource=source;terminalRejectionReason=rejected;badTerminal();return false;}
  boolean authoritative=source.equals("QUERY_ORIGINAL_ACK")||source.equals("TERMINAL_AUTHORITY");
  if(p.state==SinkCoordinator.HostState.READY){ready=true;readyToken=p.token;if(authoritative)terminalProtocolUnknown=false;}
  if(p.state==SinkCoordinator.HostState.ABORTED){aborted=true;if(authoritative)terminalProtocolUnknown=false;}return true;
 }
 private synchronized boolean acceptCommitOutcome(HostOutput.CommitOutcome fact,String source){
  if(fact==null){fail("OUTPUT_INVALID_HOST_RESULT");return false;}if(fact==HostOutput.CommitOutcome.UNKNOWN)return true;
  if(!ready||aborted||commitOutcome!=HostOutput.CommitOutcome.UNKNOWN&&commitOutcome!=fact){terminalRejectionSource=source;terminalRejectionReason="COMMIT_TERMINAL_CONFLICT";badTerminal();return false;}
  commitOutcome=fact;return true;
 }
 private IOException badTerminal(){terminalProtocolUnknown=true;fail("OUTPUT_INVALID_HOST_RESULT");return invalidHostResult();}
 private void observeTerminalAuthority(){
  if(released||!(readyEntered||abortEntered||queryEntered)||pending!=null||!allHostOriginalsReturned())return;
  try{acceptTerminal(host.originalTerminalStatus(task),"TERMINAL_AUTHORITY");}catch(Throwable unknown){terminalProtocolUnknown=true;fail("OUTPUT_ABORT_UNKNOWN");}
 }
 public WritableByteChannel channel(){return channel;}
 private int write(long at,ByteBuffer input)throws IOException {enter();try{
  if(input.remaining()==0)return 0;synchronized(this){if(producerClosed||cancelled.get()||firstFailure!=null||invoking||pending!=null)throw new IOException("OUTPUT_NOT_WRITABLE");requirePrevious();if(at<0||at>MAX_OUTPUT||!random&&at!=extent)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");int n=Math.min(65536,input.remaining());if(n>MAX_OUTPUT-at||n>MAX_OUTPUT-written)throw new IOException("OUTPUT_BYTE_BUDGET");originalBlock=new byte[n];input.duplicate().get(originalBlock);opCount=n;opOffset=at;writeAttemptedBytes+=n;}
  int n=call("WRITE",()->host.writeAt(at,originalBlock,0,opCount));input.position(input.position()+n);if(cancelled.get()){fail("CANCELLED");throw new IOException("CANCELLED");}return n;
 }finally{leave();}}
 public int writeAt(long at,ByteBuffer input)throws IOException {if(!random)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");return write(at,input);}
 private final class Channel implements WritableByteChannel {
  public int write(ByteBuffer b)throws IOException {if(b.remaining()>MAX_OUTPUT-extent||b.remaining()>MAX_OUTPUT-written)throw new IOException("OUTPUT_BYTE_BUDGET");int total=0;while(b.hasRemaining())total+=TemporaryOutput.this.write(extent,b);return total;}
  public boolean isOpen(){return !producerClosed;}public void close(){producerClosed=true;}
 }
 public void cancel(){cancelled.set(true);coordinator.cancel();HostInputFactory f=reopenedInput;if(hostInspectionActive&&f!=null)f.close();}
 public void finishWriter()throws IOException {enter();try{
  if(!producerClosed)throw new IOException("OUTPUT_PRODUCER_NOT_CLOSED");if(cancelled.get()||firstFailure!=null)throw new IOException("OUTPUT_NOT_VALIDATABLE");
  if(!flushAttempted)call("FLUSH",host::flush);if(!flushed)throw new IOException("OUTPUT_ORIGINAL_PENDING");if(!closeAttempted)call("CLOSE",host::closeWriter);
  requirePrevious();if(!writerReturned()||!closeSucceeded)throw new IOException("OUTPUT_ORIGINAL_PENDING");if(!random&&expectedSequentialSha==null)expectedSequentialSha=hex(sequentialDigest.digest());
 }finally{leave();}}
 public boolean writerReturned(){try{return closeAttempted&&!invoking&&pending==null&&host.writerOriginalsReturned();}catch(Throwable unknown){return false;}}
 /** Separate read-only host evidence. NEVER enters validation/READY/COMMIT states or
  * issues HOST_ISOLATED_FORMAT_V1. Same reopen authority and original worker joins. */
 public HostMp4Inspection.Evidence inspectHostMp4Structure(HostMp4Inspection.Container container)throws IOException {enter();try{
  HostMp4Inspection.requireAdmission(container,true,-1);
  if(hostInspectionAttempted||!writerReturned()||!flushed||!closeSucceeded||firstFailure!=null||cancelled.get())throw new IOException("OUTPUT_NOT_VALIDATABLE");requirePrevious();
  hostInspectionAttempted=true;
  if(!reopenAttempted)call("REOPEN",host::reopenReadOnly);requirePrevious();if(reopenedProvider==null)throw new IOException("OUTPUT_REOPEN_FAILED");
  HostInputFactory f=new HostInputFactory(1,1,"host_mp4_structure_v1",reopenedProvider,worker);reopenedInput=f;reopenedInputClosed=false;hostInspectionActive=true;
  try{
   if(cancelled.get()){f.close();throw new IOException("CANCELLED");}
   HostMp4Inspection.Evidence fact=HostMp4Inspection.inspect(f,container,true,-1,false);
   if(cancelled.get())throw new IOException("CANCELLED");
   if(!fact.fullReadEof||!fact.extractorEof||fact.bytes!=extent||!random&&!fact.sha256.equals(expectedSequentialSha))throw new IOException("OUTPUT_HOST_STRUCTURE_MISMATCH");
   hostStructure=fact;
  }catch(Throwable t){IOException e=Failures.io(t,"OUTPUT_HOST_STRUCTURE_FAILED");fail(e.getMessage());throw e;}
  finally{f.close();reopenedInputClosed=true;hostInspectionActive=false;try{if(!f.awaitOriginalReturns(5000)){fail("OUTPUT_ORIGINAL_PENDING");throw new IOException("OUTPUT_ORIGINAL_PENDING");}}catch(InterruptedException e){Thread.currentThread().interrupt();fail("CANCELLED");throw new IOException("CANCELLED");}}
  requirePrevious();if(cancelled.get()){fail("CANCELLED");throw new IOException("CANCELLED");}return hostStructure;
 }catch(IOException e){if(hostInspectionAttempted)fail(e.getMessage());throw e;}finally{leave();}}
 void rejectHostStructure(){fail("OUTPUT_HOST_STRUCTURE_FAILED");}
 public HostOutput.Validation verifyAndValidate(HostOutput.Validator validator)throws IOException {enter();try{
  if(!writerReturned()||!flushed||!closeSucceeded||firstFailure!=null||cancelled.get())throw new IOException("OUTPUT_NOT_VALIDATABLE");requirePrevious();
  if(validatorOriginal!=null&&validatorOriginal!=validator)throw new IOException("OUTPUT_VALIDATOR_IDENTITY");
  if(!reopenAttempted)call("REOPEN",host::reopenReadOnly);requirePrevious();if(reopenedProvider==null){fail("OUTPUT_REOPEN_FAILED");throw new IOException("OUTPUT_REOPEN_FAILED");}
  if(!hashComplete){HostInputFactory f=new HostInputFactory(1,1,"output_reopen_v1",reopenedProvider,worker);reopenedInput=f;reopenedInputClosed=false;HostDataSource ds=f.createDataSource();long bytes=0;String hash;
   try{MessageDigest d=digest();long length=ds.open(new DataSpec(f.uri()));if(length>=0&&length!=extent)throw new IOException("OUTPUT_VALIDATION_FAILED");byte[] block=new byte[65536];int n;while((n=ds.read(block,0,block.length))!=-1){bytes+=n;if(bytes>MAX_OUTPUT)throw new IOException("OUTPUT_VALIDATION_FAILED");d.update(block,0,n);}hash=hex(d.digest());if(bytes<1||bytes!=extent||!random&&!hash.equals(expectedSequentialSha))throw new IOException("OUTPUT_VALIDATION_FAILED");}
   catch(Throwable t){IOException e=Failures.io(t,"OUTPUT_REOPEN_FAILED");fail(e.getMessage());throw e;}
   finally{ds.close();f.close();reopenedInputClosed=true;try{if(!f.awaitOriginalReturns(5000)){fail("OUTPUT_REOPEN_FAILED");throw new IOException("OUTPUT_REOPEN_FAILED");}}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}}
   sha=hash;hashComplete=true;
  }
  requirePrevious();if(!validationAttempted)call("VALIDATE",()->validator.validate(task,extent,sha),validator);HostOutput.Validation p=validationReceipt;
  if(p==null||!p.structurallyValid||!task.equals(p.task)||p.bytes!=extent||!sha.equals(p.sha256)||!"HOST_ISOLATED_FORMAT_V1".equals(p.kind)){fail("OUTPUT_VALIDATION_FAILED");throw new IOException("OUTPUT_VALIDATION_FAILED");}
  if(!validated){validationKind=p.kind;validated=true;coordinator.validating();}return p;
 }finally{leave();}}
 /** These views preserve the SAME host invocation/ACK; only the authorities prove return. */
 private CompletionStage<String> readyHost(String id){
  CompletableFuture<String> view;synchronized(this){if(readyView!=null)return readyView;if(!allHostOriginalsReturned())return HostInputFactory.failed("OUTPUT_ORIGINAL_PENDING");readyEntered=true;coordinatorInvoking=true;readyView=view=new CompletableFuture<>();}
  readyPhase="INVOKING";
  try{CompletionStage<?> original=Objects.requireNonNull(host.markReady(id));readyOriginalStage=original;readyPhase="ACK_PENDING";coordinatorInvoking=false;
   readyObserverStage=original.whenComplete((value,error)->{
    synchronized(this){readyResponseReceived=true;readyResponseSucceeded=error==null;originalReadyResponseToken=value instanceof String?(String)value:null;
     if(error==null){SinkCoordinator.Status fact=new SinkCoordinator.Status(SinkCoordinator.HostState.READY,originalReadyResponseToken);if(!(value instanceof String)||!acceptTerminal(fact,"READY_ORIGINAL_ACK")){if(!(value instanceof String))acceptTerminal(null,"READY_ORIGINAL_ACK");readyResponseRejection=terminalRejectionReason;error=invalidHostResult();}else readyResponseAccepted=true;}
     else readyResponseRejection="ORIGINAL_ACK_FAILED";
    }
    if(error==null){readyPhase="ACKED";view.complete((String)value);}
    else{readyPhase=readyResponseSucceeded?"ACK_REJECTED":"ACK_FAILED";IOException e=Failures.io(error,"OUTPUT_READY_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}
   }).toCompletableFuture();
  }catch(Throwable t){readyPhase="INVOCATION_UNKNOWN";terminalProtocolUnknown=true;IOException e=Failures.io(t,"OUTPUT_READY_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}finally{coordinatorInvoking=false;}return view;
 }
 private CompletionStage<Void> abortHost(String id){
  CompletableFuture<Void> view;synchronized(this){if(abortView!=null)return abortView;if(!allHostOriginalsReturned())return HostInputFactory.failed("OUTPUT_ORIGINAL_PENDING");abortEntered=true;coordinatorInvoking=true;abortView=view=new CompletableFuture<>();}
  abortPhase="INVOKING";
  try{CompletionStage<?> original=Objects.requireNonNull(host.abort(id));abortOriginalStage=original;abortPhase="ACK_PENDING";coordinatorInvoking=false;
   abortObserverStage=original.whenComplete((value,error)->{if(error==null&&value!=null)error=badTerminal();if(error==null){abortPhase="ACKED";view.complete(null);}else{abortPhase="ACK_FAILED";IOException e=Failures.io(error,"OUTPUT_ABORT_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}}).toCompletableFuture();
  }catch(Throwable t){abortPhase="INVOCATION_UNKNOWN";terminalProtocolUnknown=true;IOException e=Failures.io(t,"OUTPUT_ABORT_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}finally{coordinatorInvoking=false;}return view;
 }
 private CompletionStage<SinkCoordinator.Status> queryHost(String id){
  CompletableFuture<SinkCoordinator.Status> view;synchronized(this){if(queryView!=null)return queryView;if(!allHostOriginalsReturned())return HostInputFactory.failed("OUTPUT_ORIGINAL_PENDING");queryEntered=true;coordinatorInvoking=true;queryView=view=new CompletableFuture<>();}
  queryPhase="INVOKING";
  try{CompletionStage<?> original=Objects.requireNonNull(host.query(id));queryOriginalStage=original;queryPhase="ACK_PENDING";coordinatorInvoking=false;
   queryObserverStage=original.whenComplete((value,error)->{if(error==null&&!acceptTerminal(value instanceof SinkCoordinator.Status?(SinkCoordinator.Status)value:null,"QUERY_ORIGINAL_ACK"))error=invalidHostResult();if(error==null){queryPhase="ACKED";view.complete((SinkCoordinator.Status)value);}else{queryPhase="ACK_FAILED";IOException e=Failures.io(error,"OUTPUT_ABORT_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}}).toCompletableFuture();
  }catch(Throwable t){queryPhase="INVOCATION_UNKNOWN";terminalProtocolUnknown=true;IOException e=Failures.io(t,"OUTPUT_ABORT_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}finally{coordinatorInvoking=false;}return view;
 }
 private void cleanupFailure(IOException waitingFailure){
  // A gate failure before QUERY admission is not an executed RPC failure. Views only
  // observe the one original invocation; no new RPC is issued to manufacture history.
  boolean timedOut=false;Throwable cause=waitingFailure;for(int n=0;n<8&&cause!=null;n++,cause=cause.getCause())if("OUTPUT_STATE_UNKNOWN".equals(cause.getMessage()))timedOut=true;
  // The original may ACK between get() throwing and this catch. That late ACK does
  // not erase the wait's already-observed timeout. Entry is still required.
  boolean enteredWait="OUTPUT_ABORT_UNKNOWN".equals(waitingFailure.getMessage())?abortEntered:queryEntered;
  if(timedOut&&enteredWait||abortEntered&&abortView!=null&&!abortView.isDone()||queryEntered&&queryView!=null&&!queryView.isDone())fail("OUTPUT_TIMEOUT_PENDING");
  else if(queryEntered||abortEntered&&abortView!=null&&abortView.isCompletedExceptionally())fail("OUTPUT_ABORT_UNKNOWN");
 }
 public String markReady()throws IOException {enter();try{
  if(!validated||!writerReturned()||firstFailure!=null||cancelled.get())throw new IOException("OUTPUT_NOT_VALIDATABLE");requirePrevious();if(ready)return readyToken;
  try{String token=coordinator.finalizeReady(true);if(!acceptTerminal(new SinkCoordinator.Status(SinkCoordinator.HostState.READY,token),"READY_AWAIT_RESULT"))throw new IOException("OUTPUT_READY_UNKNOWN");return token;}catch(IOException e){fail("OUTPUT_READY_UNKNOWN");throw new IOException("OUTPUT_READY_UNKNOWN");}
 }finally{leave();}}
 public void commitByExplicitHost(HostOutput.Commit action)throws IOException {enter();try{
  if(!ready||commitAttempted||!writerReturned()||firstFailure!=null||cancelled.get())throw new IOException("OUTPUT_COMMIT_NOT_ADMITTED");requirePrevious();
  joinCoordinatorOriginals();requirePrevious();
  synchronized(OWNERS){if(!OWNERS.contains(this)&&OWNERS.size()>=2)throw new IOException("OUTPUT_RESOURCE_EXHAUSTED");OWNERS.add(this);released=false;}
  try{call("COMMIT",()->action.commit(task,readyToken),action);}catch(IOException e){if(commitAttempted&&!commitAcknowledged)fail("OUTPUT_COMMIT_UNKNOWN");throw e;}
 }finally{leave();}}
 public boolean abort()throws IOException {enter();try{
  cancel();producerClosed=true;if(!observeNow()||!allHostOriginalsReturned())return false;
  if(commitAttempted){observeCommitOutcome();if(commitOutcome!=HostOutput.CommitOutcome.UNKNOWN)finishCallbacksNow();return false;}
  observeTerminalAuthority();if(aborted||ready){if(!scopedResponsesAnswered()||!coordinator.originalResponsesAnswered())return false;finishCallbacksNow();return aborted&&released;}
  if(!closeAttempted){try{call("CLOSE",host::closeWriter);}catch(IOException e){if(!writerReturned())return false;}}
  if(!writerReturned()||!allHostOriginalsReturned())return false;
  try{coordinator.abortBeforeReady();}catch(IOException e){cleanupFailure(e);if(!allHostOriginalsReturned()||coordinator.pendingCallbacks()!=0)return false;try{coordinator.reconcile();}catch(IOException unresolved){cleanupFailure(unresolved);observeTerminalAuthority();if(aborted||ready)finishCallbacksNow();return aborted&&released;}}
  SinkCoordinator.State terminal=coordinator.state();if(terminal==SinkCoordinator.State.ABORTED)acceptTerminal(new SinkCoordinator.Status(SinkCoordinator.HostState.ABORTED,null),"COORDINATOR_RESULT");if(terminal==SinkCoordinator.State.READY)acceptTerminal(new SinkCoordinator.Status(SinkCoordinator.HostState.READY,coordinator.token()),"COORDINATOR_RESULT");
  if(!allHostOriginalsReturned()||!scopedResponsesAnswered()||!coordinator.originalResponsesAnswered())return false;if(aborted)finishCallbacksNow();return aborted&&released;
 }finally{leave();}}
 private void finishCallbacksNow()throws IOException {
  requirePrevious();observeCommitOutcome();observeTerminalAuthority();if(!writerReturned()||!ready&&!aborted||terminalProtocolUnknown||commitAttempted&&commitOutcome==HostOutput.CommitOutcome.UNKNOWN)throw new IOException("OUTPUT_ORIGINAL_PENDING");
  joinCoordinatorOriginals();requirePrevious();released=true;OWNERS.remove(this);
 }
 private void joinCoordinatorOriginals()throws IOException {
  if(!scopedResponsesAnswered()||!coordinator.originalResponsesAnswered())throw new IOException("OUTPUT_ORIGINAL_PENDING");
  try{long end=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(timeoutMs);while(!scopedObserversReturned()){if(System.nanoTime()>=end)throw new IOException("OUTPUT_ORIGINAL_PENDING");Thread.sleep(1);}coordinator.awaitOriginalCallbacks(timeoutMs);if(!scopedObserversReturned()||!coordinator.originalCallbacksReturned())throw new IOException("OUTPUT_ORIGINAL_PENDING");}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}
 }
 public void finishOriginalCallbacks()throws IOException {enter();try{finishCallbacksNow();}finally{leave();}}
 public String state(){return "acknowledgedBytesLowerBound="+written+" knownExtentLowerBound="+extent+" writeAttemptedOrReserved="+writeAttemptedBytes+" writeAmountUnknown="+writeAmountUnknown+" unknownWriteReservation="+unknownWriteReservation+" operation="+opKind+" pending="+(invoking||coordinatorInvoking||pending!=null||!scopedObserversReturned()||!coordinator.originalResponsesCompleted())+" flushPhase="+flushPhase+" flush="+flushed+" closePhase="+closePhase+" closeReturned="+closeReturned+" closeSucceeded="+closeSucceeded+" reopenPhase="+reopenPhase+" validationPhase="+validationPhase+" commitPhase="+commitPhase+" originalWriterReturned="+writerReturned()+" allOriginalHostTasksReturned="+allHostOriginalsReturned()+" validatorOriginalReturned="+validatorReturned()+" commitOriginalReturned="+commitReturned()+" reopenReadOriginalsReturned="+readOriginalsReturned()+" validation="+validationKind+" validatedAck="+validated+" readyEntered="+readyEntered+" readyAck="+ready+" commitAcknowledged="+commitAcknowledged+" readyResponseReceived="+readyResponseReceived+" readyResponseSucceeded="+readyResponseSucceeded+" readyResponseAccepted="+readyResponseAccepted+" readyResponseRejection="+readyResponseRejection+" terminalRejectionSource="+terminalRejectionSource+" terminalRejectionReason="+terminalRejectionReason+" scopedObserversReturned="+scopedObserversReturned()+" coordinatorResponsesCompleted="+coordinator.originalResponsesCompleted()+" terminalProtocolUnknown="+terminalProtocolUnknown+" readyPhase="+readyPhase+" commitOutcome="+commitOutcome+" abortPhase="+abortPhase+" queryPhase="+queryPhase+" abortEntered="+abortEntered+" queryEntered="+queryEntered+" abortedAck="+aborted+" ownerReturned="+returned()+" error="+firstFailure;}
 public String firstFailure(){return firstFailure;}public long acknowledgedBytesLowerBound(){return written;}public boolean writeAmountUnknown(){return writeAmountUnknown;}public long unknownWriteReservation(){return unknownWriteReservation;}public boolean validationAcknowledged(){return validationReceipt!=null;}public boolean readyAcknowledged(){return ready;}public String readyAcknowledgementToken(){return readyToken;}public boolean committed(){return commitOutcome==HostOutput.CommitOutcome.CONFIRMED_COMMITTED;}public boolean returned(){return released&&!terminalProtocolUnknown&&allHostOriginalsReturned()&&pending==null&&scopedObserversReturned()&&coordinator.originalCallbacksReturned();}
 public boolean originalReadyResponseReceived(){return readyResponseReceived;}public boolean originalReadyResponseAccepted(){return readyResponseAccepted;}public String originalReadyResponseRejection(){return readyResponseRejection;}
 public static int retained(){return OWNERS.size();}
 private static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte v:b)s.append(String.format(java.util.Locale.ROOT,"%02x",v&255));return s.toString();}
 private static MessageDigest digest(){try{return MessageDigest.getInstance("SHA-256");}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
