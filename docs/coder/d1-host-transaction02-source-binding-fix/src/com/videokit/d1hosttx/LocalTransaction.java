package com.videokit.d1hosttx;

import com.videokit.d1input.HostOutput;
import com.videokit.spike.c14.*;
import com.videokit.spike.e4.E13SourceGroup;
import java.io.*;import java.nio.*;import java.nio.channels.*;import java.nio.file.*;import java.nio.file.attribute.*;import java.util.*;import java.util.concurrent.*;

/** One finite replaceable LOCAL TEST host authority. SDK state/return rules remain
 * the original TemporaryOutput/SinkCoordinator. No database or Media3 replacement.
 * Its validation tag is the original controlled host port's closed-string token;
 * it is NOT a claim of Android isolated format validation or MP4 validity. */
public final class LocalTransaction implements HostOutput,HostOutput.Validator,HostOutput.Commit {
 static final int RECORD_MAGIC=0x48545832;
 static void requireRecordVersion(int magic)throws IOException {if(magic!=RECORD_MAGIC)throw new IOException("OUTPUT_RECORD_VERSION_UNSUPPORTED");}
 private static final Set<LocalTransaction> ORIGINAL_HOST_OWNERS=ConcurrentHashMap.newKeySet();
 public enum Fault {NONE,PUBLISH_TARGET_EXISTS,UNKNOWN_AFTER_PUBLISH,ACK_AND_TAIL_GATES}
 public final Binding binding;private final Path root,temp,published,record;private final E13SourceGroup source;
 private final long expectedBytes;private final String expectedSha;private final FileIdentity originalFileIdentity;private final OwnedFileProvider sourceProvider;
 private FileChannel originalWriter;private boolean closeEntered,closeReturned,flushed,validated,aborted,ready,commitEntered;
 private volatile boolean physicalUnknown;private volatile CommitOutcome outcome=CommitOutcome.UNKNOWN;private String token="";
 private final Fault fault;private final List<Thread> originalThreads=new CopyOnWriteArrayList<>();private OwnedFileProvider readback;
 private CompletableFuture<Void> closeStage,commitStage;
 public final CountDownLatch publicationReturned=new CountDownLatch(1),allowAck=new CountDownLatch(1),ackCompleted=new CountDownLatch(1),allowTail=new CountDownLatch(1);
 public volatile boolean queryAuthorityAvailable;public int writes,flushCalls,closeCalls,reopens,validations,readyCalls,commitCalls,abortCalls,businessQueries,recordWrites,sourceMoveIoAdmissions;
 public long payloadRequested,payloadActual,recordBytes;private String firstFailure;
 public LocalTransaction(Path freshRoot,Binding binding,E13SourceGroup source,OwnedFileProvider sourceProvider,long bytes,String sha,Fault fault)throws IOException {
  this.binding=binding;this.source=source;this.sourceProvider=sourceProvider;binding.requireSource(source);expectedBytes=bytes;expectedSha=sha;this.fault=fault;
  if(bytes<1||bytes>LocalFormat.MAX||sha==null||!sha.matches("[0-9a-f]{64}"))throw new IOException("OUTPUT_GRANT_INVALID");
  root=freshRoot.toAbsolutePath().normalize();if(!root.equals(freshRoot)||Files.exists(root))throw new IOException("NEW_OWNED_SCOPE_REQUIRED");
  Files.createDirectory(root);if(!root.toRealPath().equals(root))throw new IOException("OUTPUT_GRANT_INVALID");
  temp=root.resolve("temporary.bin");published=root.resolve("published.bin");record=root.resolve("transaction.record");
  // Register this authority before the original native file creation. A failed
  // original open/close is never repaired with another descriptor or second close.
  ORIGINAL_HOST_OWNERS.add(this);
  try{originalWriter=FileChannel.open(temp,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE);originalFileIdentity=FileIdentity.capture(temp);}catch(IOException e){physicalUnknown=true;throw e;}
  queryAuthorityAvailable=fault!=Fault.UNKNOWN_AFTER_PUBLISH;
  if(fault==Fault.PUBLISH_TARGET_EXISTS)Files.createDirectory(published);
  try{saveRecord("WRITING");}catch(IOException e){physicalUnknown=true;throw e;}
 }
 private synchronized void fail(String why){if(firstFailure==null)firstFailure=why;}
 public synchronized String firstFailure(){return firstFailure;}
 private void task(String id)throws IOException{if(!binding.transactionId.equals(id))throw new IOException("OUTPUT_GRANT_INVALID");}
 private void sameTemp()throws IOException{originalFileIdentity.requireSame(temp);}
 public String opaqueTask(){return binding.transactionId;}
 public Capabilities capabilities(){return new Capabilities(true,false,true,true,true);}
 public synchronized CompletionStage<Integer> writeAt(long at,byte[] b,int off,int count){
  try{
   if(closeEntered||commitEntered||aborted||count<1||count>65536||at!=payloadActual||at+count>16L*1024*1024)throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");
   sameTemp();writes++;payloadRequested+=count;int n=originalWriter.write(ByteBuffer.wrap(b,off,count),at);if(n<1)throw new IOException("OUTPUT_IO_FAILED");payloadActual+=n;return CompletableFuture.completedFuture(n);
  }catch(IOException e){fail(e.getMessage());return failed(e);}
 }
 public synchronized CompletionStage<Void> flush(){try{if(closeEntered||aborted)throw new IOException("OUTPUT_IO_FAILED");flushCalls++;originalWriter.force(true);flushed=true;return CompletableFuture.completedFuture(null);}catch(IOException e){physicalUnknown=true;fail(e.getMessage());return failed(e);}}
 public synchronized CompletionStage<Void> closeWriter(){
  if(closeEntered)return closeStage;closeEntered=true;closeCalls++;closeStage=new CompletableFuture<>();
  try{originalWriter.close();closeReturned=true;closeStage.complete(null);}catch(IOException e){physicalUnknown=true;fail(e.getMessage());closeStage.completeExceptionally(e);}return closeStage;
 }
 public synchronized boolean writerOriginalsReturned(){return closeReturned&&!physicalUnknown;}
 public boolean originalOperationsReturned(){return !physicalUnknown&&originalThreads.stream().noneMatch(Thread::isAlive)&&(readback==null||readback.originalsReturned());}
 public synchronized CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){
  try{if(!flushed||!closeReturned||aborted||commitEntered||readback!=null)throw new IOException("OUTPUT_REOPEN_FAILED");sameTemp();readback=new OwnedFileProvider(temp,false,originalFileIdentity);reopens++;return CompletableFuture.completedFuture(readback);}catch(IOException e){fail(e.getMessage());return failed(e);}
 }
 public synchronized CompletionStage<Validation> validate(String id,long bytes,String sha){
  try{task(id);if(!flushed||!closeReturned||readback==null||!readback.originalsReturned()||commitEntered)throw new IOException("OUTPUT_VALIDATION_FAILED");validations++;sameTemp();
   byte[] actual=LocalFormat.readBounded(temp);LocalFormat.validate(actual,binding,expectedBytes,expectedSha);
   if(bytes!=expectedBytes||!sha.equals(expectedSha))throw new IOException("OUTPUT_VALIDATION_FAILED");sameTemp();validated=true;saveRecord("VALIDATED");
   return CompletableFuture.completedFuture(new Validation(id,bytes,sha,"HOST_ISOLATED_FORMAT_V1",true));
  }catch(IOException e){fail("OUTPUT_VALIDATION_FAILED");return failed(new IOException("OUTPUT_VALIDATION_FAILED"));}
 }
 public synchronized CompletionStage<String> markReady(String id){
  try{task(id);if(!validated||!writerOriginalsReturned()||!originalOperationsReturned()||aborted)throw new IOException("OUTPUT_NOT_VALIDATABLE");readyCalls++;
   if(!ready){token="ready_"+binding.grant;ready=true;saveRecord("READY");}return CompletableFuture.completedFuture(token);
  }catch(IOException e){fail(e.getMessage());return failed(e);}
 }
 public synchronized CompletionStage<SinkCoordinator.Status> query(String id){try{task(id);return CompletableFuture.completedFuture(originalTerminalStatus(id));}catch(IOException e){return failed(e);}}
 public synchronized SinkCoordinator.Status originalTerminalStatus(String id){
  if(!binding.transactionId.equals(id))return new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);
  return new SinkCoordinator.Status(ready?SinkCoordinator.HostState.READY:aborted?SinkCoordinator.HostState.ABORTED:SinkCoordinator.HostState.WRITING,ready?token:null);
 }
 public synchronized CompletionStage<Void> abort(String id){
  try{task(id);if(ready||commitEntered)throw new IOException("OUTPUT_ABORT_UNKNOWN");if(!closeReturned||!originalOperationsReturned())throw new IOException("OUTPUT_ORIGINAL_PENDING");
   abortCalls++;if(!aborted){sameTemp();Files.delete(temp);aborted=true;saveRecord("ABORTED");}return CompletableFuture.completedFuture(null);
  }catch(IOException e){fail(e.getMessage());return failed(e);}
 }
 public synchronized CompletionStage<Void> commit(String id,String givenToken){
  try{task(id);if(commitEntered||!ready||!validated||!token.equals(givenToken)||!writerOriginalsReturned()||!originalOperationsReturned())throw new IOException("OUTPUT_COMMIT_NOT_ADMITTED");
   commitEntered=true;commitCalls++;commitStage=new CompletableFuture<>();saveRecord("COMMIT_ENTERED");
   Thread original=new Thread(this::publishOnce,"hosttx-original-commit-"+binding.transactionId);originalThreads.add(original);original.start();return commitStage;
  }catch(IOException e){fail(e.getMessage());return failed(e);}
 }
 private void publishOnce(){
  try{
   sameTemp();Files.move(temp,published); // no REPLACE: never overwrite a target
   originalFileIdentity.requireSame(published);
   LocalFormat.validate(LocalFormat.readBounded(published),binding,expectedBytes,expectedSha);
   if(fault==Fault.UNKNOWN_AFTER_PUBLISH){publicationReturned.countDown();fail("OUTPUT_COMMIT_UNKNOWN");commitStage.completeExceptionally(new IOException("OUTPUT_COMMIT_UNKNOWN"));return;}
   synchronized(this){outcome=CommitOutcome.CONFIRMED_COMMITTED;saveRecord("COMMITTED");}publicationReturned.countDown();
   if(fault==Fault.ACK_AND_TAIL_GATES&&!allowAck.await(3000,TimeUnit.MILLISECONDS))throw new IOException("OUTPUT_COMMIT_UNKNOWN");
   commitStage.complete(null);ackCompleted.countDown();
   if(fault==Fault.ACK_AND_TAIL_GATES&&!allowTail.await(3000,TimeUnit.MILLISECONDS)){physicalUnknown=true;fail("OUTPUT_ORIGINAL_PENDING");}
  }catch(FileAlreadyExistsException e){
   try{sameTemp();synchronized(this){outcome=CommitOutcome.CONFIRMED_NOT_APPLIED;saveRecord("NOT_APPLIED");}}catch(IOException uncertain){outcome=CommitOutcome.UNKNOWN;}
   publicationReturned.countDown();fail("OUTPUT_IO_FAILED");commitStage.completeExceptionally(new IOException("OUTPUT_IO_FAILED"));
  }catch(Throwable e){publicationReturned.countDown();fail("OUTPUT_COMMIT_UNKNOWN");commitStage.completeExceptionally(new IOException("OUTPUT_COMMIT_UNKNOWN"));}
 }
 public synchronized CommitOutcome originalOutcome(String id,String givenToken){
  if(!binding.transactionId.equals(id)||!token.equals(givenToken)||!originalOperationsReturned())return CommitOutcome.UNKNOWN;return outcome;
 }
 public static final class Publication {
  public final CommitOutcome outcome;public final boolean readable;public final String sha256,phase,bindingKey;private Publication(CommitOutcome o,boolean r,String s,String p,String k){outcome=o;readable=r;sha256=s;phase=p;bindingKey=k;}
 }
 /** A non-forgeable in-process reference to THIS known local record, not a URI. */
 public final class RecoveryRef {
  private RecoveryRef(){}
  public Publication queryReadOnly(Binding actual)throws IOException {
   binding.require(actual);synchronized(LocalTransaction.this){if(businessQueries>=8)throw new IOException("OUTPUT_BYTE_BUDGET");businessQueries++;}
   if(!queryAuthorityAvailable)return new Publication(CommitOutcome.UNKNOWN,false,"UNKNOWN","QUERY_UNAVAILABLE",binding.key());
   long n=Files.size(record);if(n<1||n>4096)throw new IOException("OUTPUT_STATE_UNKNOWN");byte[] raw=Files.readAllBytes(record);
   String phase,recordToken,fileIdentity;long bytes;String sha;
   try(DataInputStream in=new DataInputStream(new ByteArrayInputStream(raw))){
    requireRecordVersion(in.readInt());if(!in.readUTF().equals(binding.key()))throw new IOException("OUTPUT_GRANT_INVALID");phase=in.readUTF();recordToken=in.readUTF();bytes=in.readLong();sha=in.readUTF();fileIdentity=in.readUTF();if(in.read()!=-1)throw new IOException("OUTPUT_STATE_UNKNOWN");
   }
   if(bytes!=expectedBytes||!sha.equals(expectedSha)||!recordToken.equals(token))throw new IOException("OUTPUT_GRANT_INVALID");
   if((phase.equals("COMMITTED")||phase.equals("COMMIT_ENTERED"))&&Files.isRegularFile(published,LinkOption.NOFOLLOW_LINKS)){
    if(!fileIdentity.equals(originalFileIdentity.recordId()))throw new IOException("OUTPUT_GRANT_INVALID");originalFileIdentity.requireSame(published);LocalFormat.validate(LocalFormat.readBounded(published),binding,bytes,sha);
    return new Publication(CommitOutcome.CONFIRMED_COMMITTED,true,sha,phase,binding.key());
   }
   if(phase.equals("NOT_APPLIED")){sameTemp();return new Publication(CommitOutcome.CONFIRMED_NOT_APPLIED,false,sha,phase,binding.key());}
   return new Publication(CommitOutcome.UNKNOWN,false,sha,phase,binding.key());
  }
 }
 public RecoveryRef recoveryReference(){return new RecoveryRef();}
 /** Exactly one requested readonly query can establish the same original fact;
  * never issues COMMIT, changes a record, or clears the first failure. */
 public Publication queryPublication(Binding actual)throws IOException {Publication p=recoveryReference().queryReadOnly(actual);if(p.outcome!=CommitOutcome.UNKNOWN)outcome=p.outcome;return p;}
 private synchronized void saveRecord(String phase)throws IOException {
  ByteArrayOutputStream raw=new ByteArrayOutputStream();try(DataOutputStream out=new DataOutputStream(raw)){out.writeInt(RECORD_MAGIC);out.writeUTF(binding.key());out.writeUTF(phase);out.writeUTF(token);out.writeLong(expectedBytes);out.writeUTF(expectedSha);out.writeUTF(originalFileIdentity.recordId());}
  byte[] bytes=raw.toByteArray();if(bytes.length>4096||recordWrites>=12)throw new IOException("OUTPUT_BYTE_BUDGET");
  Path next=root.resolve("transaction.record.next");try(FileChannel f=FileChannel.open(next,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){ByteBuffer b=ByteBuffer.wrap(bytes);while(b.hasRemaining())f.write(b);f.force(true);}Files.move(next,record,StandardCopyOption.REPLACE_EXISTING);recordWrites++;recordBytes+=bytes.length;
 }
 public boolean awaitOriginalTasks(long millis)throws InterruptedException {
  long end=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(millis);for(Thread t:originalThreads){long left=end-System.nanoTime();if(left>0)t.join(Math.max(1,TimeUnit.NANOSECONDS.toMillis(left)));if(t.isAlive())return false;}return originalOperationsReturned();
 }
 public void moveDrainedSource(Binding actual,Path ownedSource,Path ownedDestination)throws IOException,InterruptedException {
  binding.require(actual);binding.requireSource(source);
  if(outcome!=CommitOutcome.CONFIRMED_COMMITTED||!originalOperationsReturned()||!source.tryReturn()||!source.snapshot().released()||!sourceProvider.originalsReturned())throw new IOException("SOURCE_ORIGINAL_PENDING");
  if(!ownedSource.getParent().equals(root.getParent())||!ownedDestination.getParent().equals(root.getParent())||Files.exists(ownedDestination))throw new IOException("SOURCE_MOVE_NOT_ADMITTED");
  sourceMoveIoAdmissions++;sourceProvider.requireOriginalFile(ownedSource);byte[] bytes=LocalFormat.readBounded(ownedSource);LocalFormat.validate(bytes,binding,expectedBytes,expectedSha);Files.move(ownedSource,ownedDestination);
  sourceProvider.requireMovedOriginal(ownedDestination);if(!Arrays.equals(bytes,LocalFormat.readBounded(ownedDestination)))throw new IOException("SOURCE_MOVE_IDENTITY_UNKNOWN");
 }
 public boolean temporaryExists(){return Files.isRegularFile(temp,LinkOption.NOFOLLOW_LINKS);}public boolean publishedExists(){return Files.isRegularFile(published,LinkOption.NOFOLLOW_LINKS);}
 public void releaseReturnedHostOwner()throws IOException {if(!writerOriginalsReturned()||!originalOperationsReturned()||!(aborted||outcome!=CommitOutcome.UNKNOWN))throw new IOException("OUTPUT_ORIGINAL_PENDING");ORIGINAL_HOST_OWNERS.remove(this);}
 public static int retainedHostOwners(){return ORIGINAL_HOST_OWNERS.size();}
 public boolean recordUnchanged(byte[] previous)throws IOException{return Arrays.equals(previous,Files.readAllBytes(record));}
 public byte[] recordSnapshot()throws IOException{return Files.readAllBytes(record);}
 private static <T>CompletableFuture<T> failed(Throwable e){CompletableFuture<T> f=new CompletableFuture<>();f.completeExceptionally(e);return f;}
}
