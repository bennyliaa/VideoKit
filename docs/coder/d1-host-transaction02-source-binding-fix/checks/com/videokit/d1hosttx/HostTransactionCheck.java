package com.videokit.d1hosttx;

import com.videokit.d1input.*;import com.videokit.spike.c14.*;import com.videokit.spike.e4.*;
import java.io.*;import java.nio.*;import java.nio.file.*;import java.util.*;import java.util.concurrent.*;

/** Eight declared finite real-file cases. Only host fault gates and Android URI
 * platform port are controlled; original SDK/Media3 classes come from pinned JARs. */
public final class HostTransactionCheck {
 static Thread worker;static Path work;static int passed;static final List<Map<String,Object>> evidence=new ArrayList<>();
 static void need(boolean b,String m){if(!b)throw new AssertionError(m);}
 interface Call {void run()throws Exception;}
 static void rejected(Call c,String reason)throws Exception{try{c.run();throw new AssertionError("accepted: "+reason);}catch(IOException e){need(reason.equals(e.getMessage()),"expected "+reason+", got "+e.getMessage());}}
 static final class Case implements AutoCloseable {
  final Path home,sourcePath;final E13SourceGroup group;final Binding binding;final byte[] sample;final OwnedFileProvider provider;final LocalTransaction host;final TemporaryOutput output;
  final LabelView labelView;
  E13SourceGroup.Consumer first,second;
  Case(String name,LocalTransaction.Fault fault,boolean twoConsumers)throws Exception{
   this(name,fault,twoConsumers,"TX_"+name,false);
  }
  Case(String name,LocalTransaction.Fault fault,boolean twoConsumers,String sourceTask,boolean mutableLabel)throws Exception{
   home=work.resolve(name);Files.createDirectory(home);sourcePath=home.resolve("source.bin");
   group=new E13SourceGroup(new E13SourceGroup.Identity(1,1,sourceTask,1,"source_"+name));binding=new Binding("TX_"+name,"grant_"+name,group,1);sample=LocalFormat.generated(binding);need(sample.length<=8*1024*1024,"sample cap");Files.write(sourcePath,sample,StandardOpenOption.CREATE_NEW);
   provider=new OwnedFileProvider(sourcePath,false);first=group.consumer(group.identity,provider);first.open(group.identity);
   if(twoConsumers){second=group.consumer(group.identity,provider);second.open(group.identity);}
   host=new LocalTransaction(home.resolve("output"),binding,group,provider,sample.length,LocalFormat.hash(sample),fault);
   labelView=mutableLabel?new LabelView(host):null;
   output=new TemporaryOutput(mutableLabel?labelView:host,false,()->{if(Thread.currentThread()!=worker)throw new IOException("WORKER_REQUIRED");},fault==LocalTransaction.Fault.ACK_AND_TAIL_GATES?250:1000,1,1);
  }
  void copy(boolean corrupt)throws Exception{
   byte[] b=new byte[65536];int n;boolean changed=false;
   while((n=first.read(group.identity,b))!=-1){if(corrupt&&!changed){b[n-1]^=1;changed=true;}output.channel().write(ByteBuffer.wrap(b,0,n));}
   first.close();output.channel().close();
   if(second==null)need(group.awaitReturn(3000)&&provider.originalsReturned(),"source original return");
  }
  void ready()throws Exception{output.finishWriter();output.verifyAndValidate(host);need(output.validationAcknowledged()&&!output.readyAcknowledged()&&!output.committed(),"validate is not ready or commit");output.markReady();need(output.readyAcknowledged()&&!output.committed(),"ready is not committed");}
  void committed()throws Exception{output.commitByExplicitHost(host);need(host.awaitOriginalTasks(3000),"original commit thread return");output.observeOriginal();output.finishOriginalCallbacks();need(output.committed()&&output.returned(),"commit and original return separate");}
  void log(String name,Map<String,Object> extra)throws Exception{
   Map<String,Object> row=new LinkedHashMap<>();row.put("case",name);row.put("pass",true);row.put("binding",binding.key());row.put("sampleBytes",sample.length);row.put("sampleSha256",LocalFormat.hash(sample));row.put("sdkClassOrigin",TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation().toString());row.put("sdkState",output.state());row.put("sdkFirstFailure",output.firstFailure());row.put("sdkOwnerReturned",output.returned());row.put("hostOriginalTasksReturned",host.originalOperationsReturned());row.put("writerCloseCalls",host.closeCalls);row.put("reopenCalls",host.reopens);row.put("validateCalls",host.validations);row.put("readyCalls",host.readyCalls);row.put("commitCalls",host.commitCalls);row.put("abortCalls",host.abortCalls);row.put("businessQueries",host.businessQueries);row.put("payloadRequested",host.payloadRequested);row.put("payloadActual",host.payloadActual);row.put("recordWrites",host.recordWrites);row.put("recordBytes",host.recordBytes);row.put("sourceReadRequested",provider.readRequested);row.put("sourceReadActual",provider.readActual);row.put("sourceOriginalCloseCalls",provider.closeCalls);row.putAll(extra);evidence.add(row);Files.writeString(home.resolve("result.json"),json(row)+"\n",StandardOpenOption.CREATE_NEW);passed++;System.out.println("PASS "+name+" commitRPC="+host.commitCalls+" returned="+output.returned());
  }
  public void close()throws Exception{
   // Only declared controlled gates are released. Never retries COMMIT/close.
   host.allowAck.countDown();host.allowTail.countDown();provider.allowLateRead.countDown();
   need(host.awaitOriginalTasks(3000),"unreturned host original: stop new cases");group.closeAll();need(group.awaitReturn(3000)&&provider.originalsReturned(),"unreturned source original: stop new cases");
   if(!output.returned()){
    output.observeOriginal();
    if(host.commitCalls==0)output.abort();else if(output.committed()||host.originalOutcome(binding.transactionId,output.readyAcknowledgementToken())!=HostOutput.CommitOutcome.UNKNOWN)output.finishOriginalCallbacks();
   }
   need(output.returned(),"SDK original retained: no fabricated cleanup");host.releaseReturnedHostOwner();
  }
 }
 /** Original SDK captures opaqueTask once. Later accessor relabeling must not
  * redirect or revoke that same original host grant. No SDK field is mutated. */
 static final class LabelView implements HostOutput {
  final LocalTransaction original;String label;
  LabelView(LocalTransaction h){original=h;label=h.opaqueTask();}
  public String opaqueTask(){return label;}public Capabilities capabilities(){return original.capabilities();}
  public CompletionStage<Integer> writeAt(long at,byte[] b,int off,int n){return original.writeAt(at,b,off,n);}
  public CompletionStage<Void> flush(){return original.flush();}public CompletionStage<Void> closeWriter(){return original.closeWriter();}
  public boolean originalOperationsReturned(){return original.originalOperationsReturned();}public boolean writerOriginalsReturned(){return original.writerOriginalsReturned();}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){return original.reopenReadOnly();}
  public CompletionStage<String> markReady(String id){return original.markReady(id);}public CompletionStage<SinkCoordinator.Status> query(String id){return original.query(id);}public CompletionStage<Void> abort(String id){return original.abort(id);}
  public SinkCoordinator.Status originalTerminalStatus(String id){return original.originalTerminalStatus(id);}
 }
 static void normal()throws Exception{try(Case c=new Case("normal",LocalTransaction.Fault.NONE,false)){
  c.copy(false);c.ready();c.committed();byte[] record=c.host.recordSnapshot();LocalTransaction.Publication q=c.host.recoveryReference().queryReadOnly(c.binding);
  need(q.outcome==HostOutput.CommitOutcome.CONFIRMED_COMMITTED&&q.readable&&q.sha256.equals(LocalFormat.hash(c.sample)),"actual publication readable from known record");need(c.host.recordUnchanged(record),"readonly recovery must not write");
  Binding wrong=new Binding(c.binding.transactionId,c.binding.grant,c.group,2);rejected(()->c.host.queryPublication(wrong),"OUTPUT_GRANT_INVALID");
  c.host.moveDrainedSource(c.binding,c.sourcePath,c.home.resolve("moved-source.bin"));need(!Files.exists(c.sourcePath)&&Arrays.equals(c.sample,LocalFormat.readBounded(c.home.resolve("moved-source.bin"))),"actual source move content");
  c.output.cancel();need(!c.output.abort()&&c.output.committed()&&c.host.abortCalls==0,"committed cannot cancel into aborted");c.log("normal",Map.of("queryFromRecordedIdentity",true,"readOnlyRecordUnchanged",true,"sourceMovedWithIdentityAndContent",true,"wrongOutputVersionRejected",true));
 }}
 static void validation()throws Exception{try(Case c=new Case("validation_rejected",LocalTransaction.Fault.NONE,false)){
  c.copy(true);c.output.finishWriter();rejected(()->c.output.verifyAndValidate(c.host),"OUTPUT_VALIDATION_FAILED");need(!c.output.validationAcknowledged()&&!c.output.readyAcknowledged()&&c.host.readyCalls==0&&c.host.commitCalls==0,"bad actual content not ready");String first=c.output.firstFailure();need(c.output.abort()&&c.output.returned()&&!c.host.temporaryExists()&&!c.host.publishedExists(),"abort real rejected temp");need(Objects.equals(first,c.output.firstFailure()),"first error sticky");c.log("validation_rejected",Map.of("actualBytesCorrupted",true,"noReadyOrCommit",true));
 }}
 static void cancel()throws Exception{try(Case c=new Case("cancel_before_ready",LocalTransaction.Fault.NONE,false)){
  c.copy(false);c.output.cancel();rejected(c.output::finishWriter,"OUTPUT_NOT_VALIDATABLE");need(c.output.abort()&&c.output.returned()&&c.host.readyCalls==0&&c.host.commitCalls==0&&!c.host.temporaryExists(),"cancel real temporary file before ready");c.log("cancel_before_ready",Map.of("cancelledBeforeReady",true));
 }}
 static void publishFailure()throws Exception{try(Case c=new Case("publish_fails",LocalTransaction.Fault.PUBLISH_TARGET_EXISTS,false)){
  c.copy(false);c.ready();rejected(()->c.output.commitByExplicitHost(c.host),"OUTPUT_IO_FAILED");need(c.host.awaitOriginalTasks(3000),"publish failure original thread joined");String first=c.output.firstFailure();c.output.observeOriginal();c.output.finishOriginalCallbacks();
  LocalTransaction.Publication q=c.host.queryPublication(c.binding);need(q.outcome==HostOutput.CommitOutcome.CONFIRMED_NOT_APPLIED&&!q.readable&&c.host.temporaryExists()&&!c.output.committed()&&c.output.returned()&&c.host.commitCalls==1&&c.host.abortCalls==0,"real Files.move rejection is not rollback or retry");need(first.equals(c.output.firstFailure()),"failure retained");c.log("publish_fails",Map.of("actualExistingDirectoryTarget",true,"queryOutcome",q.outcome.name()));
 }}
 static void unknown()throws Exception{try(Case c=new Case("unknown_then_query",LocalTransaction.Fault.UNKNOWN_AFTER_PUBLISH,false)){
  c.copy(false);c.ready();rejected(()->c.output.commitByExplicitHost(c.host),"OUTPUT_COMMIT_UNKNOWN");need(c.host.awaitOriginalTasks(3000),"unknown result does not mean thread unknown");c.output.observeOriginal();String first=c.output.firstFailure();
  need(!c.output.committed()&&!c.output.returned()&&TemporaryOutput.retained()==1,"unknown holds original SDK owner");rejected(c.output::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");need(!c.output.abort()&&c.host.abortCalls==0,"no abort or second commit to fix unknown");
  byte[] record=c.host.recordSnapshot();c.host.queryAuthorityAvailable=true;LocalTransaction.Publication q=c.host.queryPublication(c.binding);need(q.readable&&q.phase.equals("COMMIT_ENTERED"),"query reconstructs actual publication from known incomplete record");need(c.host.recordUnchanged(record),"recovery query is read only");c.output.observeOriginal();c.output.finishOriginalCallbacks();
  need(c.output.committed()&&c.output.returned()&&c.host.commitCalls==1&&first.equals(c.output.firstFailure()),"same original fact, sticky failure, no retry/refund");c.log("unknown_then_query",Map.of("unknownOwnerHeldBeforeQuery",true,"originalACKFailed",true,"readOnlyRecovery",true));
 }}
 static void late()throws Exception{try(Case c=new Case("query_before_ack",LocalTransaction.Fault.ACK_AND_TAIL_GATES,false)){
  c.copy(false);c.ready();rejected(()->c.output.commitByExplicitHost(c.host),"OUTPUT_TIMEOUT_PENDING");need(c.host.publicationReturned.await(1000,TimeUnit.MILLISECONDS),"publication has returned");LocalTransaction.Publication q=c.host.queryPublication(c.binding);
  need(q.outcome==HostOutput.CommitOutcome.CONFIRMED_COMMITTED&&q.readable&&!c.output.returned()&&!c.host.originalOperationsReturned(),"business query is not original ACK/thread return");
  c.host.allowAck.countDown();need(c.host.ackCompleted.await(1000,TimeUnit.MILLISECONDS),"same original ack complete");c.output.observeOriginal();need(c.output.committed()&&!c.output.returned(),"ACK still not host tail return");rejected(c.output::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");
  c.host.allowTail.countDown();need(c.host.awaitOriginalTasks(3000),"same original commit thread joined");c.output.finishOriginalCallbacks();need(c.output.returned()&&c.host.commitCalls==1,"release only original return");c.log("query_before_ack",Map.of("queryCommittedBeforeACK",true,"ACKBeforeOriginalTail",true,"originalThreadJoined",true));
 }}
 static void dual()throws Exception{try(Case c=new Case("dual_consumer_move",LocalTransaction.Fault.NONE,true)){
  c.copy(false);need(!c.group.snapshot().released()&&!c.group.tryReturn(),"first consumer cannot release all source");c.ready();c.committed();
  rejected(()->c.host.moveDrainedSource(c.binding,c.sourcePath,c.home.resolve("moved-source.bin")),"SOURCE_ORIGINAL_PENDING");need(Files.exists(c.sourcePath),"move not performed while second consumer owns source");c.second.close();need(c.group.awaitReturn(3000)&&c.provider.originalsReturned(),"both original consumers returned");
  c.host.moveDrainedSource(c.binding,c.sourcePath,c.home.resolve("moved-source.bin"));c.log("dual_consumer_move",Map.of("firstCloseDidNotDrain",true,"moveBlockedUntilBothReturned",true,"actualMoveAfterDrained",true));
 }}
 static void oldGeneration()throws Exception{
  Path home=work.resolve("late_old_generation");Files.createDirectory(home);Path file=home.resolve("source.bin");byte[] raw=new byte[]{1,2,3,4};Files.write(file,raw,StandardOpenOption.CREATE_NEW);
  E13SourceGroup old=new E13SourceGroup(new E13SourceGroup.Identity(1,1,"OLD",1,"source_old"));OwnedFileProvider provider=new OwnedFileProvider(file,true);E13SourceGroup.Consumer c=old.consumer(old.identity,provider);c.open(old.identity);byte[] consumerBytes=new byte[4];Future<Integer> pending=old.submit(()->c.read(old.identity,consumerBytes));
  try{need(provider.readEntered.await(1000,TimeUnit.MILLISECONDS),"actual old original read entered");old.closeAll();need(!old.tryReturn(),"retired generation not released while original read pending");provider.allowLateRead.countDown();
   try{pending.get(3000,TimeUnit.MILLISECONDS);throw new AssertionError("late old data accepted");}catch(ExecutionException e){need(e.getCause() instanceof IOException,"old read rejected with SDK error");}
   need(old.awaitReturn(3000)&&provider.originalsReturned()&&Arrays.equals(consumerBytes,new byte[4])&&provider.readActual==4,"original physical bytes counted but never published after cancellation");
   E13SourceGroup fresh=new E13SourceGroup(new E13SourceGroup.Identity(1,1,"NEW",2,"source_new"));OwnedFileProvider p2=new OwnedFileProvider(file,false);E13SourceGroup.Consumer n=fresh.consumer(fresh.identity,p2);
   try{rejected(()->n.open(old.identity),"SOURCE_IDENTITY_REJECTED");n.open(fresh.identity);byte[] b=new byte[4];need(n.read(fresh.identity,b)==4&&Arrays.equals(b,raw),"fresh epoch independent");}finally{n.close();need(fresh.awaitReturn(3000)&&p2.originalsReturned(),"fresh actual source returned");}
   Map<String,Object> row=new LinkedHashMap<>();row.put("case","late_old_generation");row.put("pass",true);row.put("physicalLateBytes",provider.readActual);row.put("callerBytesUnchanged",true);row.put("oldActualCloseCalls",provider.closeCalls);row.put("freshEpoch",2);row.put("sourceOwnersReturned",E13SourceGroup.canFinish());evidence.add(row);Files.writeString(home.resolve("result.json"),json(row)+"\n",StandardOpenOption.CREATE_NEW);passed++;System.out.println("PASS late_old_generation oldActualBytes=4 callerBytes=0");
  }finally{provider.allowLateRead.countDown();old.closeAll();need(old.awaitReturn(3000),"old original return cleanup");}
 }
 static void sourceTaskMatrix()throws Exception {try(Case c=new Case("source_task_matrix",LocalTransaction.Fault.NONE,false,"SRC_A",false)){
  E13SourceGroup wrong=new E13SourceGroup(new E13SourceGroup.Identity(1,1,"SRC_B",1,c.group.identity.instance));
  try{
   Binding wrongBinding=new Binding(c.binding.transactionId,c.binding.grant,wrong,1);need(c.binding.uid==wrongBinding.uid&&c.binding.pid==wrongBinding.pid&&c.binding.epoch==wrongBinding.epoch&&c.binding.generation==wrongBinding.generation&&c.binding.sourceInstance.equals(wrongBinding.sourceInstance),"only task differs among source fields");need(!c.binding.key().equals(wrongBinding.key()),"source task encoded");
   rejected(()->c.binding.requireSource(wrong),"SOURCE_IDENTITY_REJECTED");
   int hostOwners=LocalTransaction.retainedHostOwners();Path bad=c.home.resolve("wrong-source-output");
   rejected(()->new LocalTransaction(bad,c.binding,wrong,c.provider,c.sample.length,LocalFormat.hash(c.sample),LocalTransaction.Fault.NONE),"SOURCE_IDENTITY_REJECTED");need(!Files.exists(bad)&&LocalTransaction.retainedHostOwners()==hostOwners,"actual constructor rejects before filesystem/host registration");
   wrong.closeAll();need(wrong.awaitReturn(3000),"wrong group actually drained");c.copy(false);c.ready();c.committed();need(c.group.snapshot().released(),"original source actually drained before wrong move");
   byte[] before=LocalFormat.readBounded(c.sourcePath),record=c.host.recordSnapshot();Path target=c.home.resolve("wrong-move.bin");int io=c.host.sourceMoveIoAdmissions,q=c.host.businessQueries;
   rejected(()->c.host.moveDrainedSource(wrongBinding,c.sourcePath,target),"OUTPUT_GRANT_INVALID");need(io==c.host.sourceMoveIoAdmissions&&!Files.exists(target)&&Arrays.equals(before,LocalFormat.readBounded(c.sourcePath)),"wrong-task move rejected at binding gate before product IO admission");
   rejected(()->c.host.recoveryReference().queryReadOnly(wrongBinding),"OUTPUT_GRANT_INVALID");need(q==c.host.businessQueries&&c.host.recordUnchanged(record),"wrong-task recovery rejects before product record-read admission");
   Binding same=new Binding(c.binding.transactionId,c.binding.grant,c.group,1);c.binding.require(same);c.binding.requireSource(c.group);need(c.host.queryPublication(same).readable,"new wrapper for same original authority remains legal");
   need(new DataInputStream(new ByteArrayInputStream(record)).readInt()==LocalTransaction.RECORD_MAGIC,"new record v2");
   c.host.moveDrainedSource(same,c.sourcePath,c.home.resolve("moved-source.bin"));c.log("source_task_matrix",Map.of("sourceTaskA","SRC_A","sourceTaskB","SRC_B","wrongConstructorNoDirectory",true,"wrongMoveIoAdmissions",0,"wrongRecoveryAdmissions",0,"sameOriginalAuthorityWrapperAccepted",true,"recordVersion",2));
  }finally{wrong.closeAll();need(wrong.awaitReturn(3000),"matrix wrong source returned");}
 }}
 static void authorityMatrix()throws Exception {try(Case c=new Case("source_authority_matrix",LocalTransaction.Fault.NONE,false,"SRC_SAME",false)){
  E13SourceGroup other=new E13SourceGroup(new E13SourceGroup.Identity(1,1,"SRC_SAME",1,c.group.identity.instance));
  try{
   Binding sameFields=new Binding(c.binding.transactionId,c.binding.grant,other,1);need(c.binding.key().equals(sameFields.key()),"record codec represents values, not a forged authority token");
   rejected(()->c.binding.requireSource(other),"SOURCE_IDENTITY_REJECTED");rejected(()->c.binding.require(sameFields),"OUTPUT_GRANT_INVALID");Path bad=c.home.resolve("other-authority-output");
   rejected(()->new LocalTransaction(bad,c.binding,other,c.provider,c.sample.length,LocalFormat.hash(c.sample),LocalTransaction.Fault.NONE),"SOURCE_IDENTITY_REJECTED");need(!Files.exists(bad),"different original authority refused even generation1 and fields match");
   other.closeAll();need(other.awaitReturn(3000),"other authority drained");c.copy(false);c.ready();c.committed();int io=c.host.sourceMoveIoAdmissions,q=c.host.businessQueries;byte[] raw=LocalFormat.readBounded(c.sourcePath),record=c.host.recordSnapshot();Path dest=c.home.resolve("other-authority-move.bin");
   rejected(()->c.host.moveDrainedSource(sameFields,c.sourcePath,dest),"OUTPUT_GRANT_INVALID");rejected(()->c.host.queryPublication(sameFields),"OUTPUT_GRANT_INVALID");need(io==c.host.sourceMoveIoAdmissions&&q==c.host.businessQueries&&!Files.exists(dest)&&Arrays.equals(raw,LocalFormat.readBounded(c.sourcePath))&&c.host.recordUnchanged(record),"wrong authority refused before product IO/query admission");
   c.log("source_authority_matrix",Map.of("identicalFieldsDifferentOriginalGroupRejected",true,"sameSerializedValuesDoNotAuthorize",true,"generationOneNotAuthority",true));
  }finally{other.closeAll();need(other.awaitReturn(3000),"other authority returned");}
 }}
 static void encodingMatrix()throws Exception {
  E13SourceGroup a=new E13SourceGroup(new E13SourceGroup.Identity(1,1,"SRC|A",1,"B")),b=new E13SourceGroup(new E13SourceGroup.Identity(1,1,"SRC",1,"A|B"));
  try{
   Binding x=new Binding("TX_CODEC","grant_codec",a,1),y=new Binding("TX_CODEC","grant_codec",b,1);need(!x.key().equals(y.key())&&x.key().startsWith("HTB2:"),"length-coded private key cannot separator-alias");byte[] packet=LocalFormat.generated(x);LocalFormat.validate(packet,x,packet.length,LocalFormat.hash(packet));rejected(()->LocalFormat.validate(packet,y,packet.length,LocalFormat.hash(packet)),"OUTPUT_VALIDATION_FAILED");
   byte[] old=packet.clone();ByteBuffer.wrap(old).putInt(0x564b4831);rejected(()->LocalFormat.validate(old,x,old.length,LocalFormat.hash(old)),"OUTPUT_VALIDATION_FAILED");rejected(()->LocalTransaction.requireRecordVersion(0x48545831),"OUTPUT_RECORD_VERSION_UNSUPPORTED");LocalTransaction.requireRecordVersion(LocalTransaction.RECORD_MAGIC);
   Map<String,Object> row=new LinkedHashMap<>();row.put("case","private_encoding_matrix");row.put("pass",true);row.put("sourceTaskAndInstanceSeparatorCollisionRejected",true);row.put("VKH1HeaderRejected",true);row.put("HTX1HeaderRejectedBySharedProductionVersionFunction",true);row.put("oldTransactionFilesRead",0);row.put("recordMigrationOrCommitReplay",false);evidence.add(row);Files.writeString(work.resolve("private-encoding-result.json"),json(row)+"\n",StandardOpenOption.CREATE_NEW);passed++;System.out.println("PASS private_encoding_matrix taskLengthCoded=true legacyRecordHeaderRejected=true");
  }finally{a.closeAll();b.closeAll();need(a.awaitReturn(3000)&&b.awaitReturn(3000),"encoding model authorities returned");}
 }
 static void opaqueTaskSnapshot()throws Exception {try(Case c=new Case("original_task_snapshot",LocalTransaction.Fault.NONE,false,"SRC_SNAPSHOT",true)){
  String key=c.binding.key(),captured=c.host.opaqueTask();c.labelView.label="ACCESSOR_CHANGED_LABEL";need(!c.labelView.opaqueTask().equals(captured),"accessor relabel actually changed");c.copy(false);c.ready();c.committed();need(c.host.queryPublication(c.binding).readable&&c.binding.key().equals(key)&&c.binding.sourceTask.equals("SRC_SNAPSHOT"),"original captured task/grant remains legal");
  c.log("original_task_snapshot",Map.of("accessorChangedWithoutGrantRedirection",true,"originalCapturedTaskAccepted",true,"sourceTaskSnapshotImmutable",true));
 }}
 static String json(Object o){if(o==null)return "null";if(o instanceof Boolean||o instanceof Number)return o.toString();if(o instanceof Map){StringJoiner s=new StringJoiner(",","{","}");for(Map.Entry<?,?> e:((Map<?,?>)o).entrySet())s.add(json(e.getKey().toString())+":"+json(e.getValue()));return s.toString();}if(o instanceof List){StringJoiner s=new StringJoiner(",","[","]");for(Object e:(List<?>)o)s.add(json(e));return s.toString();}return "\""+o.toString().replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r")+"\"";}
 public static void main(String[] args)throws Exception{
  worker=Thread.currentThread();worker.setName("hosttx-single-test-worker");need(args.length==1,"exact output root");work=Path.of(args[0]);need(work.isAbsolute()&&!Files.exists(work),"new independent test root");Files.createDirectory(work);
  normal();validation();cancel();publishFailure();unknown();late();dual();oldGeneration();
  sourceTaskMatrix();authorityMatrix();encodingMatrix();opaqueTaskSnapshot();
  // Exactly the affected frozen authority regression entry (three scenarios),
  // not the old complete selfcheck launcher or unrelated suites.
  com.videokit.d1input.IndependentAuthorityCheck.main(new String[0]);
  need(passed==12&&TemporaryOutput.retained()==0&&HostInputFactory.admittedSources()==0&&E13SourceGroup.canFinish()&&LocalTransaction.retainedHostOwners()==0,"all original host/SDK/source owners returned");
  Map<String,Object> summary=new LinkedHashMap<>();summary.put("cases",evidence);summary.put("passed",passed);summary.put("originalRealFileCases",8);summary.put("sourceBindingMatrixGroups",4);summary.put("affectedFrozenAuthorityScenarios",3);summary.put("SDKOwners",TemporaryOutput.retained());summary.put("hostOwners",LocalTransaction.retainedHostOwners());summary.put("sourceOwners",E13SourceGroup.retained());summary.put("AndroidActual",false);summary.put("Media3FormatValidation",false);summary.put("localControlledValidationTagOnly",true);summary.put("media3DataSourceOrigin",androidx.media3.datasource.DataSource.class.getProtectionDomain().getCodeSource().getLocation().toString());Files.writeString(work.resolve("summary.json"),json(summary)+"\n",StandardOpenOption.CREATE_NEW);System.out.println("DONE hostTransactionCases=8 sourceBindingGroups=4 affectedOriginalAuthority=3 originalOwners0=true noCommitRetry=true");
 }
}
