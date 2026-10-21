from pathlib import Path
B=Path(__file__).resolve().parents[1];P=B/'instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java';old=P.read_text();a=old.index(' private static JSONObject sample(');b=old.index(' String receipt(',a);helpers=old[a:b]
header='''package com.videokit.d1media3.android02.test;
import android.app.Instrumentation;import com.videokit.d1android.*;import com.videokit.d1input.*;import com.videokit.spike.c14.*;import com.videokit.spike.e4.*;
import java.io.*;import java.nio.charset.StandardCharsets;import java.util.*;import java.util.concurrent.CopyOnWriteArrayList;import org.json.*;
/** One original Job/worker, immutable published receipts and original resource keepers. */
final class ExperimentJob {
 final Instrumentation runner;volatile ExperimentContract.Method method;final ExperimentContract.Method requestedMethod;final String runId;final JSONObject identity;
 final ScopeJournal journal=new ScopeJournal();final ScopeMeter meter=new ScopeMeter();final CompletionPoint completion=new CompletionPoint();
 volatile long startedNano,completedNano;volatile Thread originalWorker;volatile boolean stopped,deadlineUnknown,workerBodyReturned;
 volatile String status="NOT_STARTED",stage="ADMITTED",ioPhase="CONTROLLED",firstFailure;
 final List<OriginalOwner<InputStream>> assetOwners=new CopyOnWriteArrayList<>();final List<OwnedFiles.RawWrite> rawWriters=new CopyOnWriteArrayList<>();
 final List<HostInputFactory> factories=new CopyOnWriteArrayList<>();final List<OwnedFiles.ReadCapability> providers=new CopyOnWriteArrayList<>();
 volatile TemporaryOutput output;volatile OwnedFiles.OutputCapability outputHost;volatile MatureMuxerBinding muxerBinding;
 File root,sourceFile,outputFile;boolean ownRoot,readOnlyCopy,copySynced;VerifiedFixtureCopy.Receipt copyReceipt;
 HostMp4Inspection.Evidence observation,reopened;volatile int peakSources;String normalizedFingerprint;
 ExperimentJob(Instrumentation r,ExperimentContract.Method m,String runId,JSONObject identity){runner=r;method=m;requestedMethod=m;this.runId=runId;this.identity=identity;}
 synchronized void fail(String why){if(firstFailure==null)firstFailure=why;stopped=true;status="FAILED";}
 void requireAdmission()throws IOException{AndroidInput.WORKER.requireWorker();if(stopped)throw new IOException("EXPERIMENT_ADMISSION_STOPPED");E13FinishOwner.requireAdmission();}
 String meterPhase(){return method.name()+"_"+ioPhase;}
 HostMp4Inspection.Phases phases(boolean reopen){return new HostMp4Inspection.Phases(){public void phase(String p){ioPhase=(reopen?"REOPEN_":"")+p;}public int maxReadRequest(){return method==ExperimentContract.Method.inspectShort3?4:65536;}};}
 synchronized void observeSources(){peakSources=Math.max(peakSources,HostInputFactory.admittedSources());}
 void deadline(){deadlineUnknown=true;stopped=true;synchronized(this){if(firstFailure==null)firstFailure="METHOD_DEADLINE_UNKNOWN";}status="UNKNOWN_ORIGINAL_RETURN_PENDING";}
 private static String safe(Throwable e){String s=e.getMessage();return s!=null&&s.matches("[A-Z][A-Z0-9_]{1,95}")?s:e.getClass().getSimpleName();}
 void run(){try{
  if(requestedMethod!=ExperimentContract.Method.scopeAll)throw new IOException("EXPERIMENT_BATCH_ONLY");
  for(ExperimentContract.Method next:scopeCases()){
   requireAdmission();method=next;resetCase();publishCurrent();runCase();cleanup();publishCurrent();requireAdmission();
   if(!resourcesReturned())throw new IOException("CASE_ORIGINAL_RETURN_PENDING");journal.completed(workerSnapshot().put("caseOriginalResourcesReturned",true).put("sameWorkerStillExecutingScope",true).toString());
  }
  method=requestedMethod;status="OBSERVED_ALL_SCOPE_HOST_STRUCTURE_ONLY";
 }catch(Throwable e){fail(safe(e));if("MP4_SEEK_UNSUPPORTED".equals(e.getMessage()))status="UNSUPPORTED_REAL_SEEK_MAP";}
 finally{
  try{cleanup();}catch(Throwable t){fail("ORIGINAL_CLEANUP_UNKNOWN");}
  try{if(method!=ExperimentContract.Method.scopeAll)publishCurrent();}catch(Throwable t){fail("RECEIPT_CONTENT_BUDGET");}
  // No controlled resource callback follows this synchronous return signal.
  completion.finishAfterSignal(E13ReturnEvents::returned,System::nanoTime,t->fail("RETURN_SIGNAL_UNKNOWN"));
  completedNano=completion.completedNano();workerBodyReturned=completion.bodyReturned();
 }}
 static ExperimentContract.Method[] scopeCases(){return new ExperimentContract.Method[]{ExperimentContract.Method.preopenAdmission,ExperimentContract.Method.rejectFixture,ExperimentContract.Method.cancelLateRead,ExperimentContract.Method.writerPending,ExperimentContract.Method.inspectKnown,ExperimentContract.Method.inspectShort3,ExperimentContract.Method.inspectUnknown,ExperimentContract.Method.inspectSeek1s,ExperimentContract.Method.bbbObserve,ExperimentContract.Method.muxQualified};}
 private void resetCase(){root=null;sourceFile=null;outputFile=null;ownRoot=false;readOnlyCopy=false;copySynced=false;copyReceipt=null;observation=null;reopened=null;normalizedFingerprint=null;ioPhase="CONTROLLED";}
 private void runCase()throws Exception {
  requireAdmission();status="RUNNING";
  if(method==ExperimentContract.Method.rejectFixture){stage="REJECT_FIXTURE_BEFORE_IO";try{ExperimentContract.admit(Map.of("case","scopeAll","fixtureSha256",ExperimentContract.SAMPLE_SHA,"runId",runId));throw new IOException("GUARD_NOT_ENFORCED");}catch(IOException e){if(!"EXPERIMENT_ARGUMENT_REJECTED".equals(e.getMessage()))throw e;}status="PREOPEN_GUARDS_OBSERVED";return;}
  if(method==ExperimentContract.Method.cancelLateRead||method==ExperimentContract.Method.writerPending){stage="CONTROLLED_ORIGINAL_RETURN_BOUNDARY";String p=meterPhase();if(method==ExperimentContract.Method.cancelLateRead)meter.input(p,ScopeMeter.Count.CONTROLLED_INPUT,1);else{meter.outputRequest(p,4);meter.outputAttempt(p,4);}BoundaryScenarios.run(method.name(),AndroidInput.WORKER);status="PREOPEN_GUARDS_OBSERVED";return;}
  if(method==ExperimentContract.Method.preopenAdmission){preopen();status="PREOPEN_GUARDS_OBSERVED";return;}
  if(method!=ExperimentContract.Method.bbbObserve){runQualified(ExperimentContract.qualifiedFixture());return;}
  prepareAsset("sample.mp4",ExperimentContract.SAMPLE_BYTES,ExperimentContract.SAMPLE_SHA);stage="REAL_BBB_OBSERVATION_ONLY";publishCurrent();
  observation=inspect(sourceFile,false,65536,-1,false,"approved_720957c94b3665ff");checkSource(observation);normalizedFingerprint=VerifiedFixtureCopy.hash(normalized(observation).toString().getBytes(StandardCharsets.UTF_8));status="OBSERVED_HOST_STRUCTURE_ONLY";
 }
 private void newRoot()throws Exception{requireAdmission();File cache=runner.getTargetContext().getCacheDir().getCanonicalFile();root=new File(cache,"d1media3-android02-"+runId+"-"+method.name()).getCanonicalFile();if(!root.getParentFile().equals(cache)||root.exists()||!root.mkdir())throw new IOException("FRESH_PRIVATE_ROOT_REQUIRED");ownRoot=true;sourceFile=new File(root,"source.mp4");outputFile=new File(root,"mux-output.mp4");}
 private void prepareAsset(String asset,int bytes,String sha)throws Exception {
  stage="PRIVATE_APPROVED_ASSET_COPY";ioPhase="COPY";newRoot();ScopeMeter.Descriptor slot=meter.descriptor("ASSET_STREAM",false);
  OriginalOwner<InputStream> input=new OriginalOwner<>("ASSET_STREAM",stream->{try{stream.close();slot.closed();}catch(Throwable e){slot.unknown();throw e;}});assetOwners.add(input);
  OwnedFiles.RawWrite dest=new OwnedFiles.RawWrite(this,sourceFile,"COPY_DEST");rawWriters.add(dest);
  try{try{input.allocate(()->runner.getContext().getAssets().open(asset));slot.adopted();}catch(Throwable e){slot.unknown();throw e;}requireAdmission();dest.open();requireAdmission();
   InputStream counted=new InputStream(){public int read(byte[] b,int off,int n)throws IOException{requireAdmission();String phase=meterPhase();meter.input(phase,ScopeMeter.Count.COPY_REQUEST,n);int got=input.call("ASSET_READ",stream->stream.read(b,off,n));meter.returned(phase,ScopeMeter.Count.COPY_ACTUAL,ScopeMeter.Count.COPY_EOF,n,got);return got;}
    public int read()throws IOException{requireAdmission();String phase=meterPhase();meter.input(phase,ScopeMeter.Count.COPY_REQUEST,1);int got=input.call("ASSET_EOF",InputStream::read);meter.returned(phase,ScopeMeter.Count.COPY_ACTUAL,ScopeMeter.Count.COPY_EOF,1,got<0?-1:1);return got;}};
   copyReceipt=VerifiedFixtureCopy.copy(counted,dest,bytes,sha,()->stopped);dest.flush();dest.sync();copySynced=dest.syncReturned;
  }finally{try{dest.close();}catch(Throwable e){fail("RAW_COPY_CLOSE_UNKNOWN");}try{if(!input.closeOnce())fail("ORIGINAL_ASSET_CLOSE_UNKNOWN");}catch(Throwable e){fail("ORIGINAL_ASSET_CLOSE_UNKNOWN");}}
  requireAdmission();if(!input.returned()||!dest.returned()||copyReceipt==null||!sourceFile.setReadOnly())throw new IOException("PRIVATE_COPY_ORIGINAL_RETURN_UNPROVEN");readOnlyCopy=true;publishCurrent();
 }
 private HostMp4Inspection.Evidence inspect(File file,boolean unknown,int chunk,long seek,boolean capture,String version)throws Exception {
  requireAdmission();OwnedFiles.ReadCapability p=new OwnedFiles.ReadCapability(this,file,unknown,chunk);providers.add(p);HostInputFactory f=AndroidInput.factory(version,p);p.factory=f;factories.add(f);observeSources();
  try{return HostMp4Inspection.inspect(f,HostMp4Inspection.Container.MP4,true,seek,capture,phases(false));}finally{f.close();if(!f.awaitOriginalReturns(5000))fail("SOURCE_ORIGINAL_RETURN_PENDING");}
 }
 private void checkSource(HostMp4Inspection.Evidence e)throws Exception{if(!e.fullReadEof||!e.extractorEof||!e.sniffMatched||!e.peekReset||!e.endTracksObserved||!e.extractorReleaseReturned()||!e.dataSourceCloseReturned()||e.bytes!=ExperimentContract.SAMPLE_BYTES||!ExperimentContract.SAMPLE_SHA.equals(e.sha256)||e.tracks.size()!=2)throw new IOException("APPROVED_SOURCE_OBSERVATION_MISMATCH");boolean video=false,audio=false;for(HostMp4Inspection.Track t:e.tracks){if("video/avc".equals(t.format.sampleMimeType)&&t.format.width==320&&t.format.height==180)video=true;else if("audio/mp4a-latm".equals(t.format.sampleMimeType))audio=true;else throw new IOException("APPROVED_TRACK_UNSUPPORTED");}if(!video||!audio)throw new IOException("APPROVED_TRACKS_MISSING");}
 private void preopen()throws Exception{stage="BENIGN_PARAMETER_GUARDS";final int[] opens={0};AsyncReadBridge.Provider p=c->{opens[0]++;return OwnedFiles.failed(new IOException("UNEXPECTED_SOURCE_OPEN"));};HostInputFactory f=AndroidInput.factory("metadata_only_v1",p);factories.add(f);observeSources();try{for(int i=0;i<4;i++){try{HostMp4Inspection.inspect(f,i==1?null:HostMp4Inspection.Container.MP4,i!=0,i==2?-2:i==3?2000001:-1,false);throw new IOException("GUARD_NOT_ENFORCED");}catch(IOException e){String expected=i<2?"MP4_CAPABILITY_UNSUPPORTED":"MP4_SEEK_BOUNDS";if(!expected.equals(e.getMessage()))throw e;}}f.createDataSource();f.createDataSource();if(opens[0]!=0)throw new IOException("SOURCE_OPEN_BEFORE_GUARD");}finally{f.close();if(!f.awaitOriginalReturns(5000))fail("SOURCE_ORIGINAL_RETURN_PENDING");}}
 private void runQualified(ExperimentContract.QualifiedFixture q)throws Exception{
  prepareAsset(q.asset,q.bytes,q.sha256);stage="QUALIFIED_AVC_CAPTURE";publishCurrent();observation=inspect(sourceFile,method.unknown,method.chunk,method.seekUs,method==ExperimentContract.Method.muxQualified,"qualified6_"+q.sha256.substring(0,16));requireAdmission();QualifiedObservation.require(observation,true);normalizedFingerprint=VerifiedFixtureCopy.hash(normalized(observation).toString().getBytes(StandardCharsets.UTF_8));publishCurrent();
  if(method==ExperimentContract.Method.inspectSeek1s&&(observation.seeks.stream().noneMatch(s->s.reason.equals("SEEK_MAP")&&s.requestedTimeUs==1000000)||observation.replay.isEmpty()))throw new IOException("REAL_SEEK_OBSERVATION_MISSING");
  if(method!=ExperimentContract.Method.muxQualified){status="OBSERVED_HOST_STRUCTURE_ONLY";return;}
  stage="REAL_MUX_TO_TEMPORARY_OUTPUT";ioPhase="MUX";OwnedFiles.OutputCapability host=new OwnedFiles.OutputCapability(this,outputFile);providers.add(host.readback);requireAdmission();output=new TemporaryOutput(host,false,AndroidInput.WORKER,5000,android.os.Process.myUid(),android.os.Process.myPid());
  // Metadata keeper is in this original Job BEFORE mature muxer construction.
  muxerBinding=new MatureMuxerBinding(output);publishCurrent();reopened=MatureContainerRemux.writeAndInspect(observation,output,muxerBinding,phases(true));QualifiedObservation.require(reopened,false);
  if(output.validationAcknowledged()||output.readyAcknowledged()||output.committed()||host.readyCalls!=0)throw new IOException("HOST_STRUCTURE_ESCALATION_FORBIDDEN");status="OBSERVED_HOST_MUX_STRUCTURE_ONLY";
 }
 private void cleanup(){stage=stage+"_CLEANUP";for(HostInputFactory f:factories){f.close();try{if(!f.awaitOriginalReturns(5000))fail("SOURCE_ORIGINAL_RETURN_PENDING");}catch(Throwable e){fail("SOURCE_ORIGINAL_RETURN_UNKNOWN");}}
  boolean muxerReturned=true;if(muxerBinding!=null){try{muxerReturned=muxerBinding.cleanupCloseOnce();}catch(Throwable e){muxerReturned=false;}if(!muxerReturned)fail("MUXER_ORIGINAL_CLOSE_UNKNOWN");}
  if(muxerReturned){if(output!=null)try{if(!output.abort())fail("OUTPUT_ORIGINAL_RETURN_PENDING");}catch(Throwable e){fail("OUTPUT_ORIGINAL_RETURN_UNKNOWN");}
   for(OwnedFiles.RawWrite raw:rawWriters)if(raw!= (outputHost==null?null:outputHost.original)||output==null)try{raw.close();}catch(Throwable e){fail("RAW_FD_ORIGINAL_CLOSE_UNKNOWN");}}
  for(OriginalOwner<InputStream> owner:assetOwners)try{if(!owner.closeOnce())fail("ASSET_ORIGINAL_CLOSE_UNKNOWN");}catch(Throwable e){fail("ASSET_ORIGINAL_CLOSE_UNKNOWN");}
  if(!resourcesReturned()){stopped=true;status="UNKNOWN_ORIGINAL_RETURN_PENDING";}
 }
 boolean resourcesReturned(){for(OriginalOwner<?> o:assetOwners)if(!o.returned())return false;for(OwnedFiles.RawWrite raw:rawWriters)if(!raw.returned())return false;for(HostInputFactory f:factories)try{if(!f.originalsReturned())return false;}catch(InterruptedException e){Thread.currentThread().interrupt();return false;}for(OwnedFiles.ReadCapability p:providers)if(!p.descriptorsReturned())return false;if(muxerBinding!=null&&!muxerBinding.returned())return false;if(output!=null&&!output.returned())return false;return E13SourceGroup.canFinish()&&HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0;}
 void awaitOriginalReturns()throws Exception{Thread w=originalWorker;if(w!=null&&w!=Thread.currentThread())w.join();E13SourceGroup.awaitOriginalReturns();}
 boolean canFinish(){return workerBodyReturned&&originalWorker!=null&&!originalWorker.isAlive()&&resourcesReturned();}
'''
tail=''' private JSONObject workerSnapshot()throws Exception {
  if(Thread.currentThread()!=originalWorker)throw new IOException("WORKER_SNAPSHOT_ONLY");
  JSONObject r=new JSONObject().put("case",method.name()).put("status",status).put("stage",stage).put("firstFailure",firstFailure==null?JSONObject.NULL:firstFailure).put("caseMeter",new JSONObject(meter.caseSnapshot(method.name()))).put("copyReadOnly",readOnlyCopy).put("copySyncReturned",copySynced);
  if(copyReceipt!=null)r.put("copy",new JSONObject().put("bytes",copyReceipt.bytes).put("sha256",copyReceipt.sha256).put("assetUnderlyingEof",copyReceipt.fullEof));
  if(observation!=null)r.put("observation",parser(observation));if(reopened!=null)r.put("reopened",parser(reopened));if(normalizedFingerprint!=null)r.put("normalizationFingerprint",normalizedFingerprint);
  if(muxerBinding!=null)r.put("muxerKeeper",new JSONObject(muxerBinding.snapshot()));
  r.put("muxReopenCalls",outputHost==null?0:outputHost.reopens).put("muxReadyCalls",outputHost==null?0:outputHost.readyCalls).put("muxNativeSyncReturned",outputHost!=null&&outputHost.flushReturned);
  return r;
 }
 private void publishCurrent()throws Exception{journal.current(workerSnapshot().toString());}
 /** Observer reads immutable completed JSON and synchronized meter/owner snapshots only. */
 String receipt(boolean finishGateReady)throws Exception {
  ScopeJournal.Snapshot s=journal.snapshot();JSONArray history=new JSONArray();for(String encoded:s.completed)history.put(new JSONObject(encoded));
  JSONObject r=new JSONObject().put("candidate",ExperimentContract.VERSION).put("scopeEntry",requestedMethod.name()).put("case",method.name()).put("runId",runId).put("identity",identity).put("status",deadlineUnknown?"UNKNOWN_DEADLINE_NO_SUCCESS_UPGRADE":status).put("stage",stage).put("currentCasePartial",method!=ExperimentContract.Method.scopeAll).put("firstFailure",firstFailure==null?JSONObject.NULL:firstFailure).put("caseReceipts",history).put("completedCaseCount",history.length()).put("expectedCaseCount",10).put("currentSnapshot",new JSONObject(s.current)).put("snapshotOverflow",s.overflow).put("scopeBudgetsSharedAcrossAllCases",true).put("meter",new JSONObject(meter.snapshot())).put("sourceLeasePeakObserved",peakSources).put("nativeFdPeakIsSourceLeasePeak",false).put("media3DtsCapability","NO_INDEPENDENT_DTS_API_UNPROVEN").put("startedNano",startedNano).put("completedNano",completedNano).put("timelyOriginalBody",completion.timely(startedNano,60000000000L)).put("lastControlledReturnSignalBeforeMarker",completion.bodyReturned()).put("workerActuallyJoined",originalWorker!=null&&!originalWorker.isAlive()).put("originalResourcesReturned",canFinish()).put("finishGateReady",finishGateReady).put("sourceKeepers",HostInputFactory.admittedSources()).put("outputKeepers",TemporaryOutput.retained()).put("runnerFinalizerOwnerAtReceipt",E13FinishOwner.retained()).put("runnerFinishReturn","EXTERNAL_ORIGINAL_CAPTURE_REQUIRED").put("receiptOutboundAttemptedBeforeThisEmission",s.emittedAttempted).put("scope","HOST_STRUCTURE_ONLY_NOT_ISOLATED_OR_PLAYBACK");
  JSONArray raw=new JSONArray();for(OwnedFiles.RawWrite writer:rawWriters)raw.put(new JSONObject(writer.snapshot()));r.put("rawDescriptorKeepers",raw);if(muxerBinding!=null)r.put("muxerKeeper",new JSONObject(muxerBinding.snapshot()));
  String text=r.toString();if(text.getBytes(StandardCharsets.UTF_8).length>ScopeJournal.STATUS_LIMIT){fail("RECEIPT_BYTE_BUDGET");r=new JSONObject().put("candidate",ExperimentContract.VERSION).put("scopeEntry",requestedMethod.name()).put("runId",runId).put("case",method.name()).put("stage",stage).put("status","BLOCKED_RECEIPT_BYTE_BUDGET").put("observationComplete",false).put("caseReceipts",history).put("completedCaseCount",history.length()).put("currentSnapshot",new JSONObject(s.current)).put("snapshotOverflow",s.overflow).put("fullMeterExportBlocked",true).put("firstFailure",firstFailure==null?JSONObject.NULL:firstFailure).put("originalResourcesReturned",canFinish());text=r.toString();if(text.getBytes(StandardCharsets.UTF_8).length>ScopeJournal.STATUS_LIMIT)throw new IOException("RECEIPT_HISTORY_BUDGET_INVARIANT");}return text;
 }
 void reserveReceiptEmission(String text)throws IOException{journal.reserveEmission(text.getBytes(StandardCharsets.UTF_8).length);}
}
'''
P.write_text(header+helpers+tail,encoding='utf-8')
print('Full five-fix Job written; snapshots immutable, raw/muxer keepers in finish gate, completion after return signal')
