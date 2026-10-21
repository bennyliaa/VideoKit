package com.videokit.d1input;
import androidx.media3.datasource.DataSpec;import com.videokit.spike.c14.*;
import java.io.*;import java.nio.*;import java.nio.channels.*;import java.security.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;

/** ACK facts never prove physical return. Original truth remains with the same host authorities,
 * original read registry/workers and existing SinkCoordinator. Cached views observe the original
 * invocation (not a replacement task); no new executor, release ledger or return counter. */
public final class TemporaryOutput {
 public static final long MAX_OUTPUT=16L*1024*1024;private static final Set<TemporaryOutput> OWNERS=ConcurrentHashMap.newKeySet();
 private final HostOutput host;private final WorkerRule worker;private final long timeoutMs;private final SinkCoordinator coordinator;
 private final AtomicBoolean cancelled=new AtomicBoolean(),ownerCall=new AtomicBoolean();private final WritableByteChannel channel=new Channel();
 private volatile CompletableFuture<?> pending;private volatile boolean invoking,coordinatorInvoking,producerClosed,flushAttempted,flushed,closeAttempted,closeReturned,closeSucceeded,validated,ready,commitAttempted,commitAcknowledged,aborted,released;
 private volatile boolean reopenAttempted,validationAttempted;private volatile HostOutput.Validator validatorOriginal;private volatile HostOutput.Commit commitOriginal;
 private volatile HostOutput.CommitOutcome commitOutcome=HostOutput.CommitOutcome.UNKNOWN;
 private volatile AsyncReadBridge.Provider reopenedProvider;private volatile HostOutput.Validation validationReceipt;private volatile HostInputFactory reopenedInput;private volatile boolean reopenedInputClosed,hashComplete;
 private volatile CompletableFuture<String> readyView;private volatile CompletableFuture<Void> abortView;private volatile CompletableFuture<SinkCoordinator.Status> queryView;
 private volatile CompletionStage<?> readyOriginalStage,abortOriginalStage,queryOriginalStage;private volatile boolean readyEntered,abortEntered,queryEntered;private volatile String readyToken;
 private volatile String readyPhase="NOT_ADMITTED",abortPhase="NOT_ADMITTED",queryPhase="NOT_ADMITTED";
 private volatile String firstFailure,sha="UNVERIFIED",validationKind="NONE";private volatile long written,extent,writeAttemptedBytes;private final boolean random;
 private volatile String opKind="NONE",flushPhase="NOT_ADMITTED",closePhase="NOT_ADMITTED",reopenPhase="NOT_ADMITTED",validationPhase="NOT_ADMITTED",commitPhase="NOT_ADMITTED";
 private volatile long opOffset;private volatile int opCount;private volatile byte[] originalBlock;private volatile boolean writeAmountUnknown,unknownRecordedForOriginal;private volatile long unknownWriteReservation;
 private final MessageDigest sequentialDigest=digest();private String expectedSequentialSha;
 public TemporaryOutput(HostOutput host,boolean requireRandom,WorkerRule worker,long timeoutMs)throws IOException {
  this.host=Objects.requireNonNull(host);this.worker=Objects.requireNonNull(worker);this.timeoutMs=timeoutMs;
  if(timeoutMs<=0||timeoutMs>5000||host.opaqueTask()==null||!host.opaqueTask().matches("[A-Za-z0-9_-]{1,64}"))throw new IOException("OUTPUT_GRANT_INVALID");
  HostOutput.Capabilities c=host.capabilities();if(c==null||!c.sequential||requireRandom&&!c.random||!c.flush||!c.close||!c.reopen)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");random=requireRandom;
  synchronized(OWNERS){if(OWNERS.size()>=2)throw new IOException("OUTPUT_RESOURCE_EXHAUSTED");OWNERS.add(this);}
  coordinator=new SinkCoordinator(host.opaqueTask(),new SinkCoordinator.Host(){public CompletionStage<String> markReady(String id){return readyHost(id);}public CompletionStage<Void> abort(String id){return abortHost(id);}public CompletionStage<SinkCoordinator.Status> query(String id){return queryHost(id);}},timeoutMs);coordinator.start();
 }
 private void enter()throws IOException {worker.requireWorker();if(!ownerCall.compareAndSet(false,true))throw new IOException("OUTPUT_ORIGINAL_PENDING");}private void leave(){ownerCall.set(false);}
 private synchronized void fail(String code){if(firstFailure==null)firstFailure=code;}
 private void recordWriteUnknown(){writeAmountUnknown=true;if(!unknownRecordedForOriginal){unknownWriteReservation+=opCount;unknownRecordedForOriginal=true;}}
 private boolean validatorReturned(){try{return validatorOriginal==null||validatorOriginal.originalOperationsReturned();}catch(Throwable unknown){return false;}}
 private boolean commitReturned(){try{return commitOriginal==null||commitOriginal.originalOperationsReturned();}catch(Throwable unknown){return false;}}
 private boolean readOriginalsReturned(){try{return reopenedInput==null||reopenedInputClosed&&reopenedInput.originalsReturned();}catch(InterruptedException e){Thread.currentThread().interrupt();return false;}}
 private boolean allHostOriginalsReturned(){try{return !invoking&&!coordinatorInvoking&&host.originalOperationsReturned()&&validatorReturned()&&commitReturned()&&readOriginalsReturned();}catch(Throwable unknown){return false;}}
 private void requirePrevious()throws IOException {if(pending!=null||!allHostOriginalsReturned())throw new IOException("OUTPUT_ORIGINAL_PENDING");}
 private void phase(String kind,String value){switch(kind){case "FLUSH":flushPhase=value;break;case "CLOSE":closePhase=value;break;case "REOPEN":reopenPhase=value;break;case "VALIDATE":validationPhase=value;break;case "COMMIT":commitPhase=value;break;default:break;}}
 /** Entry flags change only AFTER admission. A throwing invocation stays UNKNOWN/failed. */
 private synchronized <T>T call(String kind,java.util.concurrent.Callable<CompletionStage<T>> method,HostOutput.Originals authority)throws IOException {
  worker.requireWorker();requirePrevious();invoking=true;opKind=kind;phase(kind,"INVOKING");
  switch(kind){case "WRITE":unknownRecordedForOriginal=false;break;case "FLUSH":flushAttempted=true;break;case "CLOSE":closeAttempted=true;break;case "REOPEN":reopenAttempted=true;break;case "VALIDATE":validationAttempted=true;validatorOriginal=(HostOutput.Validator)authority;break;case "COMMIT":commitAttempted=true;commitOriginal=(HostOutput.Commit)authority;break;default:break;}
  try{pending=Objects.requireNonNull(method.call()).toCompletableFuture();phase(kind,"ACK_PENDING");}
  catch(Throwable t){phase(kind,"INVOCATION_UNKNOWN");if(kind.equals("WRITE"))recordWriteUnknown();IOException mapped=Failures.io(t,fallback(kind));fail(mapped.getMessage());throw mapped;}
  finally{invoking=false;}
  try{@SuppressWarnings("unchecked") T value=(T)pending.get(timeoutMs,TimeUnit.MILLISECONDS);consumeOriginal(value,null);return value;}
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
 public boolean observeOriginal()throws IOException {enter();try{return observeNow();}finally{leave();}}
 private synchronized void consumeOriginal(Object result,IOException failure)throws IOException {
  if(pending==null)return;
  if(failure==null&&opKind.equals("REOPEN")&&!(result instanceof AsyncReadBridge.Provider))failure=new IOException("OUTPUT_REOPEN_FAILED");
  if(failure==null&&opKind.equals("VALIDATE")&&!(result instanceof HostOutput.Validation))failure=new IOException("OUTPUT_VALIDATION_FAILED");
  phase(opKind,failure==null?"ACKED":"ACK_FAILED");if(failure!=null)fail(failure.getMessage());
  if(opKind.equals("WRITE")&&failure!=null)recordWriteUnknown();
  if(opKind.equals("WRITE")&&failure==null){int n=result instanceof Integer?(Integer)result:-1;if(n<1||n>opCount){recordWriteUnknown();fail("OUTPUT_INVALID_WRITE_RESULT");pending=null;originalBlock=null;throw new IOException("OUTPUT_INVALID_WRITE_RESULT");}if(!random)sequentialDigest.update(originalBlock,0,n);written+=n;extent=Math.max(extent,opOffset+n);}
  if(opKind.equals("FLUSH")&&failure==null)flushed=true;if(opKind.equals("CLOSE")){closeReturned=true;closeSucceeded=failure==null;}
  if(opKind.equals("REOPEN")&&failure==null)reopenedProvider=(AsyncReadBridge.Provider)result;
  if(opKind.equals("VALIDATE")&&failure==null)validationReceipt=(HostOutput.Validation)result;
  if(opKind.equals("COMMIT")&&failure==null){commitAcknowledged=true;commitOutcome=HostOutput.CommitOutcome.CONFIRMED_COMMITTED;}pending=null;originalBlock=null;
 }
 private void observeCommitOutcome(){
  if(!commitAttempted||commitAcknowledged||commitOutcome!=HostOutput.CommitOutcome.UNKNOWN||pending!=null||!allHostOriginalsReturned())return;
  try{HostOutput.CommitOutcome fact=commitOriginal.originalOutcome(host.opaqueTask(),readyToken);if(fact!=null)commitOutcome=fact;}catch(Throwable unknown){/* unavailable authority never proves a business outcome */}
 }
 private void observeTerminalAuthority(){
  if(!queryEntered||pending!=null||!allHostOriginalsReturned())return;
  try{SinkCoordinator.Status fact=host.originalTerminalStatus(host.opaqueTask());if(fact==null)return;if(fact.state==SinkCoordinator.HostState.ABORTED)aborted=true;if(fact.state==SinkCoordinator.HostState.READY&&fact.token!=null&&!fact.token.isEmpty()){ready=true;readyToken=fact.token;}}catch(Throwable unknown){/* no terminal proof */}
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
 public void cancel(){cancelled.set(true);coordinator.cancel();}
 public void finishWriter()throws IOException {enter();try{
  if(!producerClosed)throw new IOException("OUTPUT_PRODUCER_NOT_CLOSED");if(cancelled.get()||firstFailure!=null)throw new IOException("OUTPUT_NOT_VALIDATABLE");
  if(!flushAttempted)call("FLUSH",host::flush);if(!flushed)throw new IOException("OUTPUT_ORIGINAL_PENDING");if(!closeAttempted)call("CLOSE",host::closeWriter);
  requirePrevious();if(!writerReturned()||!closeSucceeded)throw new IOException("OUTPUT_ORIGINAL_PENDING");if(!random&&expectedSequentialSha==null)expectedSequentialSha=hex(sequentialDigest.digest());
 }finally{leave();}}
 public boolean writerReturned(){try{return closeAttempted&&!invoking&&pending==null&&host.writerOriginalsReturned();}catch(Throwable unknown){return false;}}
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
  requirePrevious();if(!validationAttempted)call("VALIDATE",()->validator.validate(host.opaqueTask(),extent,sha),validator);HostOutput.Validation p=validationReceipt;
  if(p==null||!p.structurallyValid||!host.opaqueTask().equals(p.task)||p.bytes!=extent||!sha.equals(p.sha256)||!"HOST_ISOLATED_FORMAT_V1".equals(p.kind)){fail("OUTPUT_VALIDATION_FAILED");throw new IOException("OUTPUT_VALIDATION_FAILED");}
  if(!validated){validationKind=p.kind;validated=true;coordinator.validating();}return p;
 }finally{leave();}}
 /** These views preserve the SAME host invocation/ACK; only the authorities prove return. */
 private CompletionStage<String> readyHost(String id){
  CompletableFuture<String> view;synchronized(this){if(readyView!=null)return readyView;if(!allHostOriginalsReturned())return HostInputFactory.failed("OUTPUT_ORIGINAL_PENDING");readyEntered=true;coordinatorInvoking=true;readyView=view=new CompletableFuture<>();}
  readyPhase="INVOKING";try{CompletionStage<String> original=Objects.requireNonNull(host.markReady(id));readyOriginalStage=original;readyPhase="ACK_PENDING";coordinatorInvoking=false;original.whenComplete((token,error)->{if(error==null){readyPhase="ACKED";readyToken=token;ready=token!=null&&!token.isEmpty();view.complete(token);}else{readyPhase="ACK_FAILED";IOException e=Failures.io(error,"OUTPUT_READY_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}});}catch(Throwable t){readyPhase="INVOCATION_UNKNOWN";IOException e=Failures.io(t,"OUTPUT_READY_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}finally{coordinatorInvoking=false;}return view;
 }
 private CompletionStage<Void> abortHost(String id){
  CompletableFuture<Void> view;synchronized(this){if(abortView!=null)return abortView;if(!allHostOriginalsReturned())return HostInputFactory.failed("OUTPUT_ORIGINAL_PENDING");abortEntered=true;coordinatorInvoking=true;abortView=view=new CompletableFuture<>();}
  abortPhase="INVOKING";try{CompletionStage<Void> original=Objects.requireNonNull(host.abort(id));abortOriginalStage=original;abortPhase="ACK_PENDING";coordinatorInvoking=false;original.whenComplete((v,error)->{if(error==null){abortPhase="ACKED";view.complete(null);}else{abortPhase="ACK_FAILED";IOException e=Failures.io(error,"OUTPUT_ABORT_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}});}catch(Throwable t){abortPhase="INVOCATION_UNKNOWN";IOException e=Failures.io(t,"OUTPUT_ABORT_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}finally{coordinatorInvoking=false;}return view;
 }
 private CompletionStage<SinkCoordinator.Status> queryHost(String id){
  CompletableFuture<SinkCoordinator.Status> view;synchronized(this){if(queryView!=null)return queryView;if(!allHostOriginalsReturned())return HostInputFactory.failed("OUTPUT_ORIGINAL_PENDING");queryEntered=true;coordinatorInvoking=true;queryView=view=new CompletableFuture<>();}
  queryPhase="INVOKING";try{CompletionStage<SinkCoordinator.Status> original=Objects.requireNonNull(host.query(id));queryOriginalStage=original;queryPhase="ACK_PENDING";coordinatorInvoking=false;original.whenComplete((s,error)->{if(error==null){queryPhase="ACKED";if(s!=null&&s.state==SinkCoordinator.HostState.READY&&s.token!=null){ready=true;readyToken=s.token;}if(s!=null&&s.state==SinkCoordinator.HostState.ABORTED)aborted=true;view.complete(s);}else{queryPhase="ACK_FAILED";IOException e=Failures.io(error,"OUTPUT_ABORT_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}});}catch(Throwable t){queryPhase="INVOCATION_UNKNOWN";IOException e=Failures.io(t,"OUTPUT_ABORT_UNKNOWN");fail(e.getMessage());view.completeExceptionally(e);}finally{coordinatorInvoking=false;}return view;
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
  try{String token=coordinator.finalizeReady(true);if(token==null||token.isEmpty())throw new IOException("OUTPUT_READY_UNKNOWN");ready=true;readyToken=token;return token;}catch(IOException e){fail("OUTPUT_READY_UNKNOWN");throw new IOException("OUTPUT_READY_UNKNOWN");}
 }finally{leave();}}
 public void commitByExplicitHost(HostOutput.Commit action)throws IOException {enter();try{
  if(!ready||commitAttempted||!writerReturned()||firstFailure!=null||cancelled.get())throw new IOException("OUTPUT_COMMIT_NOT_ADMITTED");requirePrevious();
  joinCoordinatorOriginals();requirePrevious();
  synchronized(OWNERS){if(!OWNERS.contains(this)&&OWNERS.size()>=2)throw new IOException("OUTPUT_RESOURCE_EXHAUSTED");OWNERS.add(this);released=false;}
  try{call("COMMIT",()->action.commit(host.opaqueTask(),readyToken),action);}catch(IOException e){if(commitAttempted&&!commitAcknowledged)fail("OUTPUT_COMMIT_UNKNOWN");throw e;}
 }finally{leave();}}
 public boolean abort()throws IOException {enter();try{
  cancel();producerClosed=true;if(!observeNow()||!allHostOriginalsReturned())return false;
  if(commitAttempted){observeCommitOutcome();if(commitOutcome!=HostOutput.CommitOutcome.UNKNOWN)finishCallbacksNow();return false;}
  observeTerminalAuthority();if(aborted||ready){finishCallbacksNow();return aborted&&released;}
  if(!closeAttempted){try{call("CLOSE",host::closeWriter);}catch(IOException e){if(!writerReturned())return false;}}
  if(!writerReturned()||!allHostOriginalsReturned())return false;
  try{coordinator.abortBeforeReady();}catch(IOException e){cleanupFailure(e);if(!allHostOriginalsReturned()||coordinator.pendingCallbacks()!=0)return false;try{coordinator.reconcile();}catch(IOException unresolved){cleanupFailure(unresolved);observeTerminalAuthority();if(aborted||ready)finishCallbacksNow();return aborted&&released;}}
  aborted=coordinator.state()==SinkCoordinator.State.ABORTED;ready=ready||coordinator.state()==SinkCoordinator.State.READY;
  if(!allHostOriginalsReturned())return false;if(aborted)finishCallbacksNow();return aborted&&released;
 }finally{leave();}}
 private void finishCallbacksNow()throws IOException {
  requirePrevious();observeCommitOutcome();observeTerminalAuthority();if(!writerReturned()||!ready&&!aborted||commitAttempted&&commitOutcome==HostOutput.CommitOutcome.UNKNOWN)throw new IOException("OUTPUT_ORIGINAL_PENDING");
  joinCoordinatorOriginals();requirePrevious();released=true;OWNERS.remove(this);
 }
 private void joinCoordinatorOriginals()throws IOException {try{coordinator.closeExecutor();coordinator.awaitOriginalCallbacks();if(!coordinator.originalCallbacksReturned())throw new IOException("OUTPUT_ORIGINAL_PENDING");}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}}
 public void finishOriginalCallbacks()throws IOException {enter();try{finishCallbacksNow();}finally{leave();}}
 public String state(){return "acknowledgedBytesLowerBound="+written+" knownExtentLowerBound="+extent+" writeAttemptedOrReserved="+writeAttemptedBytes+" writeAmountUnknown="+writeAmountUnknown+" unknownWriteReservation="+unknownWriteReservation+" operation="+opKind+" pending="+(invoking||coordinatorInvoking||pending!=null)+" flushPhase="+flushPhase+" flush="+flushed+" closePhase="+closePhase+" closeReturned="+closeReturned+" closeSucceeded="+closeSucceeded+" reopenPhase="+reopenPhase+" validationPhase="+validationPhase+" commitPhase="+commitPhase+" originalWriterReturned="+writerReturned()+" allOriginalHostTasksReturned="+allHostOriginalsReturned()+" validatorOriginalReturned="+validatorReturned()+" commitOriginalReturned="+commitReturned()+" reopenReadOriginalsReturned="+readOriginalsReturned()+" validation="+validationKind+" validatedAck="+validated+" readyEntered="+readyEntered+" readyAck="+ready+" commitAcknowledged="+commitAcknowledged+" readyPhase="+readyPhase+" commitOutcome="+commitOutcome+" abortPhase="+abortPhase+" queryPhase="+queryPhase+" abortEntered="+abortEntered+" queryEntered="+queryEntered+" abortedAck="+aborted+" ownerReturned="+returned()+" error="+firstFailure;}
 public String firstFailure(){return firstFailure;}public long acknowledgedBytesLowerBound(){return written;}public boolean writeAmountUnknown(){return writeAmountUnknown;}public long unknownWriteReservation(){return unknownWriteReservation;}public boolean validationAcknowledged(){return validationReceipt!=null;}public boolean readyAcknowledged(){return ready;}public String readyAcknowledgementToken(){return readyToken;}public boolean committed(){return commitOutcome==HostOutput.CommitOutcome.CONFIRMED_COMMITTED;}public boolean returned(){return released&&allHostOriginalsReturned()&&pending==null;}
 public static int retained(){return OWNERS.size();}
 private static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte v:b)s.append(String.format(java.util.Locale.ROOT,"%02x",v&255));return s.toString();}
 private static MessageDigest digest(){try{return MessageDigest.getInstance("SHA-256");}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
