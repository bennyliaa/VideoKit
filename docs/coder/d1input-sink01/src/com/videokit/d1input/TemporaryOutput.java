package com.videokit.d1input;
import androidx.media3.datasource.DataSpec;import com.videokit.spike.c14.*;
import java.io.*;import java.nio.*;import java.nio.channels.*;import java.security.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;

/** One bounded temporary host output, using the original SinkCoordinator for READY arbitration.
 * One original host operation and <=64KiB private block, no internal I/O executor or file cache.
 * Cancel/timeouts reject new writes, retain the SAME grant/stage until original return. */
public final class TemporaryOutput {
 public static final long MAX_OUTPUT=16L*1024*1024;private static final Set<TemporaryOutput> OWNERS=ConcurrentHashMap.newKeySet();
 private final HostOutput host;private final WorkerRule worker;private final long timeoutMs;private final SinkCoordinator coordinator;
 private final AtomicBoolean cancelled=new AtomicBoolean();private final WritableByteChannel channel=new Channel();
 private volatile CompletableFuture<?> pending;private volatile boolean invoking,producerClosed,flushAttempted,flushed,closeAttempted,closeReturned,closeSucceeded,validated,ready,commitAttempted,commitAcknowledged,aborted,released;
 private volatile String firstFailure,sha="UNVERIFIED",validationKind="NONE";private volatile long written,extent,writeAttemptedBytes;private boolean random;
 private volatile String opKind="NONE";private volatile long opOffset;private volatile int opCount;private volatile byte[] originalBlock;
 private final AtomicBoolean writerAdmission=new AtomicBoolean();private volatile boolean writeAmountUnknown;private volatile long unknownWriteReservation;
 private final MessageDigest sequentialDigest=digest();private String expectedSequentialSha;
 public TemporaryOutput(HostOutput host,boolean requireRandom,WorkerRule worker,long timeoutMs)throws IOException {
  this.host=Objects.requireNonNull(host);this.worker=Objects.requireNonNull(worker);this.timeoutMs=timeoutMs;
  if(timeoutMs<=0||timeoutMs>5000||host.opaqueTask()==null||!host.opaqueTask().matches("[A-Za-z0-9_-]{1,64}"))throw new IOException("OUTPUT_GRANT_INVALID");
  HostOutput.Capabilities c=host.capabilities();if(c==null||!c.sequential||requireRandom&&!c.random||!c.flush||!c.close||!c.reopen)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");random=requireRandom;
  synchronized(OWNERS){if(OWNERS.size()>=2)throw new IOException("OUTPUT_RESOURCE_EXHAUSTED");OWNERS.add(this);}
  coordinator=new SinkCoordinator(host.opaqueTask(),host,timeoutMs);coordinator.start();
 }
 private synchronized void fail(String code){if(firstFailure==null)firstFailure=code;}
 private synchronized <T>T call(String kind,java.util.concurrent.Callable<CompletionStage<T>> method)throws IOException {
  worker.requireWorker();if(invoking||pending!=null||!host.originalOperationsReturned())throw new IOException("OUTPUT_ORIGINAL_PENDING");invoking=true;opKind=kind;
  try{pending=Objects.requireNonNull(method.call()).toCompletableFuture();}
  catch(Throwable t){if(kind.equals("WRITE")){writeAmountUnknown=true;unknownWriteReservation+=opCount;}IOException mapped=Failures.io(t,"OUTPUT_IO_FAILED");fail(mapped.getMessage());throw mapped;}
  finally{invoking=false;}
  try{@SuppressWarnings("unchecked") T value=(T)pending.get(timeoutMs,TimeUnit.MILLISECONDS);consumeOriginal(value,null);return value;}
  catch(TimeoutException e){if(kind.equals("WRITE")){writeAmountUnknown=true;unknownWriteReservation+=opCount;}fail("OUTPUT_TIMEOUT_PENDING");throw new IOException("OUTPUT_TIMEOUT_PENDING");}
  catch(InterruptedException e){Thread.currentThread().interrupt();cancel();fail("CANCELLED");throw new IOException("CANCELLED");}
  catch(ExecutionException e){IOException mapped=Failures.io(e,kind.equals("REOPEN")?"OUTPUT_REOPEN_FAILED":kind.equals("VALIDATE")?"OUTPUT_VALIDATION_FAILED":"OUTPUT_IO_FAILED");consumeOriginal(null,mapped);fail(mapped.getMessage());throw mapped;}
 }
 /** Reconcile only the SAME retained original result, never repeat write/flush/close. */
 public synchronized boolean observeOriginal()throws IOException {
  worker.requireWorker();CompletableFuture<?> p=pending;if(invoking||p!=null&&!p.isDone())return false;if(p==null)return true;
  try{consumeOriginal(p.get(),null);}catch(ExecutionException e){IOException mapped=Failures.io(e,"OUTPUT_IO_FAILED");consumeOriginal(null,mapped);fail(mapped.getMessage());}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}return true;
 }
 private synchronized void consumeOriginal(Object result,IOException failure)throws IOException {
  if(pending==null)return;
  if(opKind.equals("WRITE")&&failure!=null){writeAmountUnknown=true;unknownWriteReservation+=opCount;}
  if(opKind.equals("WRITE")&&failure==null){int n=result instanceof Integer?(Integer)result:-1;if(n<1||n>opCount){writeAmountUnknown=true;unknownWriteReservation+=opCount;fail("OUTPUT_INVALID_WRITE_RESULT");pending=null;originalBlock=null;throw new IOException("OUTPUT_INVALID_WRITE_RESULT");}if(!random)sequentialDigest.update(originalBlock,0,n);written+=n;extent=Math.max(extent,opOffset+n);}
  if(opKind.equals("FLUSH")&&failure==null)flushed=true;
  if(opKind.equals("CLOSE")){closeReturned=true;closeSucceeded=failure==null;}
  if(opKind.equals("COMMIT")&&failure==null)commitAcknowledged=true;
  pending=null;originalBlock=null;
 }
 public WritableByteChannel channel(){return channel;}
 private int write(long at,ByteBuffer input)throws IOException {
  worker.requireWorker();if(input.remaining()==0)return 0;
  if(!writerAdmission.compareAndSet(false,true))throw new IOException("OUTPUT_ORIGINAL_PENDING");try{
  synchronized(this){if(producerClosed||cancelled.get()||firstFailure!=null||invoking||pending!=null)throw new IOException("OUTPUT_NOT_WRITABLE");if(at<0||at>MAX_OUTPUT||!random&&at!=extent)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");int n=Math.min(65536,input.remaining());if(n>MAX_OUTPUT-at||n>MAX_OUTPUT-written)throw new IOException("OUTPUT_BYTE_BUDGET");originalBlock=new byte[n];input.duplicate().get(originalBlock);opCount=n;opOffset=at;writeAttemptedBytes+=n;}
  int n=call("WRITE",()->host.writeAt(at,originalBlock,0,opCount));input.position(input.position()+n);if(cancelled.get()){fail("CANCELLED");throw new IOException("CANCELLED");}return n;
  }finally{writerAdmission.set(false);}
 }
 public int writeAt(long at,ByteBuffer input)throws IOException {if(!random)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");return write(at,input);}
 private final class Channel implements WritableByteChannel {
  public int write(ByteBuffer b)throws IOException {if(b.remaining()>MAX_OUTPUT-extent||b.remaining()>MAX_OUTPUT-written)throw new IOException("OUTPUT_BYTE_BUDGET");int total=0;while(b.hasRemaining()){int n=TemporaryOutput.this.write(extent,b);total+=n;}return total;}
  public boolean isOpen(){return !producerClosed;}
  /** Close this non-owning producer view. Host flush/descriptor close remain explicit stages. */
  public void close(){producerClosed=true;}
 }
 public void cancel(){cancelled.set(true);coordinator.cancel();}
 public void finishWriter()throws IOException {
  worker.requireWorker();if(!producerClosed)throw new IOException("OUTPUT_PRODUCER_NOT_CLOSED");if(cancelled.get()||firstFailure!=null)throw new IOException("OUTPUT_NOT_VALIDATABLE");
  if(!flushAttempted){flushAttempted=true;call("FLUSH",host::flush);}if(!closeAttempted){closeAttempted=true;call("CLOSE",host::closeWriter);}
  if(!writerReturned()||!flushed||!closeSucceeded)throw new IOException("OUTPUT_ORIGINAL_PENDING");
  if(!random&&expectedSequentialSha==null)expectedSequentialSha=hex(sequentialDigest.digest());
 }
 public boolean writerReturned(){return closeReturned&&!invoking&&pending==null&&host.writerOriginalsReturned();}
 public HostOutput.Validation verifyAndValidate(HostOutput.Validator validator)throws IOException {
  worker.requireWorker();if(!writerReturned()||!flushed||!closeSucceeded||firstFailure!=null||cancelled.get())throw new IOException("OUTPUT_NOT_VALIDATABLE");
  AsyncReadBridge.Provider source=call("REOPEN",host::reopenReadOnly);if(source==null){fail("OUTPUT_REOPEN_FAILED");throw new IOException("OUTPUT_REOPEN_FAILED");}
  HostInputFactory f=new HostInputFactory(1,1,"output_reopen_v1",source,worker);HostDataSource ds=f.createDataSource();long bytes=0;String hash;
  try{MessageDigest digest=MessageDigest.getInstance("SHA-256");long length=ds.open(new DataSpec(f.uri()));if(length>=0&&length!=extent)throw new IOException("OUTPUT_VALIDATION_FAILED");byte[] block=new byte[65536];int n;while((n=ds.read(block,0,block.length))!=-1){bytes+=n;if(bytes>MAX_OUTPUT)throw new IOException("OUTPUT_VALIDATION_FAILED");digest.update(block,0,n);}hash=hex(digest.digest());if(bytes<1||bytes!=extent||!random&&!hash.equals(expectedSequentialSha))throw new IOException("OUTPUT_VALIDATION_FAILED");}
  catch(Throwable t){IOException error=Failures.io(t,"OUTPUT_REOPEN_FAILED");fail(error.getMessage());throw error;}
  finally{ds.close();f.close();try{if(!f.awaitOriginalReturns(5000)){fail("OUTPUT_REOPEN_FAILED");throw new IOException("OUTPUT_REOPEN_FAILED");}}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}}
  sha=hash;final long actualBytes=bytes;HostOutput.Validation proof=call("VALIDATE",()->validator.validate(host.opaqueTask(),actualBytes,hash));
  if(proof==null||!proof.structurallyValid||!host.opaqueTask().equals(proof.task)||proof.bytes!=bytes||!sha.equals(proof.sha256)||proof.kind==null||proof.kind.isEmpty()){fail("OUTPUT_VALIDATION_FAILED");throw new IOException("OUTPUT_VALIDATION_FAILED");}
  if(!proof.kind.equals("HOST_ISOLATED_FORMAT_V1")){fail("OUTPUT_VALIDATION_FAILED");throw new IOException("OUTPUT_VALIDATION_FAILED");}validationKind=proof.kind;validated=true;coordinator.validating();return proof;
 }
 public String markReady()throws IOException {worker.requireWorker();if(!validated||!writerReturned()||firstFailure!=null||cancelled.get())throw new IOException("OUTPUT_NOT_VALIDATABLE");try{String token=coordinator.finalizeReady(true);if(token==null||token.isEmpty()){fail("OUTPUT_READY_UNKNOWN");throw new IOException("OUTPUT_READY_UNKNOWN");}ready=true;return token;}catch(IOException e){fail("OUTPUT_READY_UNKNOWN");throw new IOException("OUTPUT_READY_UNKNOWN");}}
 public void commitByExplicitHost(HostOutput.Commit action)throws IOException {worker.requireWorker();if(!ready||commitAttempted||!writerReturned()||firstFailure!=null||cancelled.get())throw new IOException("OUTPUT_COMMIT_NOT_ADMITTED");synchronized(OWNERS){if(!OWNERS.contains(this)&&OWNERS.size()>=2)throw new IOException("OUTPUT_RESOURCE_EXHAUSTED");OWNERS.add(this);released=false;}commitAttempted=true;try{call("COMMIT",()->action.commit(host.opaqueTask(),coordinator.token()));}catch(IOException e){if(!commitAcknowledged)fail("OUTPUT_COMMIT_UNKNOWN");throw e;}}
 public boolean abort()throws IOException {
  worker.requireWorker();cancel();producerClosed=true;if(aborted)return true;if(!observeOriginal())return false;
  if(!host.originalOperationsReturned())return false;if(!closeAttempted){closeAttempted=true;try{call("CLOSE",host::closeWriter);}catch(IOException e){if(!writerReturned())return false;}}
  if(!writerReturned())return false;coordinator.abortBeforeReady();aborted=coordinator.state()==SinkCoordinator.State.ABORTED;ready=coordinator.state()==SinkCoordinator.State.READY;
  if(aborted)finishOriginalCallbacks();return aborted;
 }
 public void finishOriginalCallbacks()throws IOException {worker.requireWorker();if(invoking||pending!=null||!writerReturned()||coordinator.pendingCallbacks()!=0||!ready&&!aborted&&!commitAcknowledged)throw new IOException("OUTPUT_ORIGINAL_PENDING");try{coordinator.closeExecutor();coordinator.awaitOriginalCallbacks();if(!coordinator.originalCallbacksReturned())throw new IOException("OUTPUT_ORIGINAL_PENDING");released=true;OWNERS.remove(this);}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}}
 public String state(){return "acknowledgedBytesLowerBound="+written+" knownExtentLowerBound="+extent+" writeAttemptedOrReserved="+writeAttemptedBytes+" writeAmountUnknown="+writeAmountUnknown+" unknownWriteReservation="+unknownWriteReservation+" operation="+opKind+" pending="+(invoking||pending!=null)+" flush="+flushed+" closeReturned="+closeReturned+" closeSucceeded="+closeSucceeded+" originalWriterReturned="+writerReturned()+" validation="+validationKind+" validated="+validated+" ready="+ready+" commitAcknowledged="+commitAcknowledged+" aborted="+aborted+" ownerReturned="+released+" error="+firstFailure;}
 public String firstFailure(){return firstFailure;}public long acknowledgedBytesLowerBound(){return written;}public boolean writeAmountUnknown(){return writeAmountUnknown;}public boolean committed(){return commitAcknowledged;}public boolean returned(){return released;}
 public static int retained(){return OWNERS.size();}
 private static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte v:b)s.append(String.format(java.util.Locale.ROOT,"%02x",v&255));return s.toString();}
 private static MessageDigest digest(){try{return MessageDigest.getInstance("SHA-256");}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
