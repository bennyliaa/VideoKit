package com.videokit.d1media3.android02.test;
import android.app.Instrumentation;import com.videokit.d1android.*;import com.videokit.d1input.*;import com.videokit.spike.c14.*;import com.videokit.spike.e4.*;
import java.io.*;import java.nio.charset.StandardCharsets;import java.util.*;import java.util.concurrent.CopyOnWriteArrayList;import org.json.*;

/** One exact benign case and its strong original resource references. Existing
 * E13FinishOwner performs completion. No timer releases, force-stop or retry. */
final class ExperimentJob {
 final Instrumentation runner;ExperimentContract.Method method;final ExperimentContract.Method requestedMethod;final String runId;final JSONObject identity;
 volatile long startedNano,completedNano;
 volatile Thread originalWorker;volatile boolean stopped,deadlineUnknown,workerBodyReturned;
 volatile String status="NOT_STARTED",stage="ADMITTED",firstFailure;
 final List<E4Owned<?>> assetOwners=new CopyOnWriteArrayList<>();final List<HostInputFactory> factories=new CopyOnWriteArrayList<>();final List<OwnedFiles.ReadCapability> providers=new CopyOnWriteArrayList<>();
 volatile TemporaryOutput output;volatile OwnedFiles.OutputCapability outputHost;
 File root,sourceFile,outputFile;boolean ownRoot,readOnlyCopy,copySynced;VerifiedFixtureCopy.Receipt copyReceipt;
 volatile HostMp4Inspection.Evidence observation,reopened;volatile long inputReserved,inputActual,outputAttemptReserved;final JSONArray caseReceipts=new JSONArray();volatile int peakSources;volatile String normalizedFingerprint;
 ExperimentJob(Instrumentation r,ExperimentContract.Method m,String runId,JSONObject identity){runner=r;method=m;requestedMethod=m;this.runId=runId;this.identity=identity;}
 synchronized void fail(String reason){if(firstFailure==null)firstFailure=reason;stopped=true;status="FAILED";}
 void requireAdmission()throws IOException{AndroidInput.WORKER.requireWorker();if(stopped)throw new IOException("EXPERIMENT_ADMISSION_STOPPED");E13FinishOwner.requireAdmission();}
 synchronized void reserveInput(int bytes)throws IOException{if(stopped)throw new IOException("EXPERIMENT_ADMISSION_STOPPED");if(bytes<1||bytes>65536||bytes>8388608-inputReserved)throw new IOException("INPUT_CUMULATIVE_BUDGET");inputReserved+=bytes;}
 synchronized void reserveOutput(int bytes)throws IOException{requireAdmission();if(bytes<1||bytes>65536||bytes>16777216-outputAttemptReserved)throw new IOException("OUTPUT_SCOPE_ATTEMPT_BUDGET");outputAttemptReserved+=bytes;}
 synchronized void inputReturned(int requested,int returned)throws IOException{if(returned< -1||returned>requested)throw new IOException("INVALID_READ_RESULT");if(returned>0)inputActual+=returned;}
 synchronized void observeSources(){peakSources=Math.max(peakSources,HostInputFactory.admittedSources());}
 void deadline(){deadlineUnknown=true;stopped=true;synchronized(this){if(firstFailure==null)firstFailure="METHOD_DEADLINE_UNKNOWN";}status="UNKNOWN_ORIGINAL_RETURN_PENDING";}
 private static String safe(Throwable e){String s=e.getMessage();return s!=null&&s.matches("[A-Z][A-Z0-9_]{1,95}")?s:e.getClass().getSimpleName();}
 void run(){try{
  if(requestedMethod!=ExperimentContract.Method.scopeAll)throw new IOException("EXPERIMENT_BATCH_ONLY");
  for(ExperimentContract.Method next:scopeCases()){
   requireAdmission();method=next;resetCase();runCase();cleanup();requireAdmission();
   if(!resourcesReturned())throw new IOException("CASE_ORIGINAL_RETURN_PENDING");
   caseReceipts.put(new JSONObject(receipt(false)).put("caseOriginalResourcesReturned",true).put("sameWorkerStillExecutingScope",true));
  }
  method=requestedMethod;status="OBSERVED_ALL_SCOPE_HOST_STRUCTURE_ONLY";
 }catch(Throwable e){fail(safe(e));if("MP4_SEEK_UNSUPPORTED".equals(e.getMessage()))status="UNSUPPORTED_REAL_SEEK_MAP";}
 finally{try{cleanup();}catch(Throwable t){fail("ORIGINAL_CLEANUP_UNKNOWN");}finally{completedNano=System.nanoTime();workerBodyReturned=true;E13ReturnEvents.returned();}}}
 static ExperimentContract.Method[] scopeCases(){return new ExperimentContract.Method[]{ExperimentContract.Method.preopenAdmission,ExperimentContract.Method.rejectFixture,ExperimentContract.Method.cancelLateRead,ExperimentContract.Method.writerPending,ExperimentContract.Method.inspectKnown,ExperimentContract.Method.inspectShort3,ExperimentContract.Method.inspectUnknown,ExperimentContract.Method.inspectSeek1s,ExperimentContract.Method.bbbObserve,ExperimentContract.Method.muxQualified};}
 private void resetCase(){root=null;sourceFile=null;outputFile=null;ownRoot=false;readOnlyCopy=false;copySynced=false;copyReceipt=null;observation=null;reopened=null;normalizedFingerprint=null;}
 private void runCase()throws Exception{
  requireAdmission();status="RUNNING";
  if(method==ExperimentContract.Method.rejectFixture){
   stage="REJECT_FIXTURE_BEFORE_IO";try{ExperimentContract.admit(Map.of("case","muxQualified","fixtureSha256",ExperimentContract.SAMPLE_SHA,"runId",runId));throw new IOException("GUARD_NOT_ENFORCED");}catch(IOException e){if(!"EXPERIMENT_ARGUMENT_REJECTED".equals(e.getMessage()))throw e;}
   status="PREOPEN_GUARDS_OBSERVED";return;
  }
  if(method==ExperimentContract.Method.cancelLateRead||method==ExperimentContract.Method.writerPending){stage="CONTROLLED_ORIGINAL_RETURN_BOUNDARY";if(method==ExperimentContract.Method.cancelLateRead)reserveInput(1);else reserveOutput(4);BoundaryScenarios.run(method.name(),AndroidInput.WORKER);status="PREOPEN_GUARDS_OBSERVED";return;}
  if(method==ExperimentContract.Method.preopenAdmission){preopen();status="PREOPEN_GUARDS_OBSERVED";return;}
  if(method!=ExperimentContract.Method.bbbObserve){runQualified(ExperimentContract.qualifiedFixture());return;}
  prepareAsset("sample.mp4",ExperimentContract.SAMPLE_BYTES,ExperimentContract.SAMPLE_SHA);
  stage="REAL_MP4_INSPECTION";observation=inspect(sourceFile,method.unknown,method.chunk,method.seekUs,false,"approved_720957c94b3665ff");
  requireAdmission();checkSource(observation);normalizedFingerprint=VerifiedFixtureCopy.hash(normalized(observation).toString().getBytes(StandardCharsets.UTF_8));
  if(method==ExperimentContract.Method.inspectSeek1s&&(observation.seeks.stream().noneMatch(s->s.reason.equals("SEEK_MAP")&&s.requestedTimeUs==1000000)||observation.replay.isEmpty()))throw new IOException("REAL_SEEK_OBSERVATION_MISSING");
  status="OBSERVED_HOST_STRUCTURE_ONLY";
 }
 private void newRoot()throws Exception{
  requireAdmission();File cache=runner.getTargetContext().getCacheDir().getCanonicalFile();root=new File(cache,"d1media3-android02-"+runId+"-"+method.name()).getCanonicalFile();if(!root.getParentFile().equals(cache)||root.exists()||!root.mkdir())throw new IOException("FRESH_PRIVATE_ROOT_REQUIRED");ownRoot=true;sourceFile=new File(root,"source.mp4");outputFile=new File(root,"mux-output.mp4");
 }
 private void closeOnce(E4Owned<?> owner){if(owner.state()==E4Owned.State.OPEN||owner.state()==E4Owned.State.READY)try{owner.close();}catch(Throwable e){fail("ORIGINAL_ASSET_CLOSE_UNKNOWN");}}
 private void prepareAsset(String asset,int bytes,String sha)throws Exception{
  stage="PRIVATE_APPROVED_ASSET_COPY";newRoot();E4Owned<InputStream> input=new E4Owned<>(asset,InputStream::close);E4Owned<FileOutputStream> dest=new E4Owned<>(sourceFile,FileOutputStream::close);assetOwners.add(input);assetOwners.add(dest);
  try{input.allocate(()->runner.getContext().getAssets().open(asset));requireAdmission();dest.allocate(()->OwnedFiles.createNew(sourceFile));requireAdmission();
   InputStream counted=new FilterInputStream(input.original()){
    public int read(byte[] b,int off,int n)throws IOException{requireAdmission();reserveInput(n);int got=in.read(b,off,n);inputReturned(n,got);return got;}
    public int read()throws IOException{requireAdmission();reserveInput(1);int got=in.read();inputReturned(1,got<0?-1:1);return got;}
   };
   copyReceipt=VerifiedFixtureCopy.copy(counted,dest.original(),bytes,sha,()->stopped);dest.original().flush();dest.original().getFD().sync();copySynced=true;
  }finally{closeOnce(dest);closeOnce(input);}
  requireAdmission();if(!input.returned()||!dest.returned()||copyReceipt==null||!sourceFile.setReadOnly())throw new IOException("PRIVATE_COPY_ORIGINAL_RETURN_UNPROVEN");readOnlyCopy=true;
 }
 private HostMp4Inspection.Evidence inspect(File file,boolean unknown,int chunk,long seek,boolean capture,String version)throws Exception{
  requireAdmission();OwnedFiles.ReadCapability provider=new OwnedFiles.ReadCapability(this,file,unknown,chunk);providers.add(provider);HostInputFactory factory=AndroidInput.factory(version,provider);provider.factory=factory;factories.add(factory);peakSources=Math.max(peakSources,HostInputFactory.admittedSources());
  try{return HostMp4Inspection.inspect(factory,HostMp4Inspection.Container.MP4,true,seek,capture);}
  finally{factory.close();if(!factory.awaitOriginalReturns(5000))fail("SOURCE_ORIGINAL_RETURN_PENDING");}
 }
 private void checkSource(HostMp4Inspection.Evidence e)throws Exception{
  if(!e.fullReadEof||!e.extractorEof||!e.sniffMatched||!e.peekReset||!e.endTracksObserved||!e.extractorReleaseReturned()||!e.dataSourceCloseReturned()||e.bytes!=ExperimentContract.SAMPLE_BYTES||!ExperimentContract.SAMPLE_SHA.equals(e.sha256)||e.tracks.size()!=2)throw new IOException("APPROVED_SOURCE_OBSERVATION_MISMATCH");
  boolean video=false,audio=false;for(HostMp4Inspection.Track t:e.tracks){if("video/avc".equals(t.format.sampleMimeType)&&t.format.width==320&&t.format.height==180)video=true;else if("audio/mp4a-latm".equals(t.format.sampleMimeType))audio=true;else throw new IOException("APPROVED_TRACK_UNSUPPORTED");}
  if(!video||!audio)throw new IOException("APPROVED_TRACKS_MISSING");
 }
 private void preopen()throws Exception{
  stage="BENIGN_PARAMETER_GUARDS";final int[] opens={0};AsyncReadBridge.Provider provider=c->{opens[0]++;return OwnedFiles.failed(new IOException("UNEXPECTED_SOURCE_OPEN"));};HostInputFactory f=AndroidInput.factory("metadata_only_v1",provider);factories.add(f);observeSources();
  try{for(int i=0;i<4;i++){try{HostMp4Inspection.inspect(f,i==1?null:HostMp4Inspection.Container.MP4,i!=0,i==2?-2:i==3?2000001:-1,false);throw new IOException("GUARD_NOT_ENFORCED");}catch(IOException e){String expected=i<2?"MP4_CAPABILITY_UNSUPPORTED":"MP4_SEEK_BOUNDS";if(!expected.equals(e.getMessage()))throw e;}}f.createDataSource();f.createDataSource();if(opens[0]!=0)throw new IOException("SOURCE_OPEN_BEFORE_GUARD");}finally{f.close();if(!f.awaitOriginalReturns(5000))fail("SOURCE_ORIGINAL_RETURN_PENDING");}
 }
 private void runQualified(ExperimentContract.QualifiedFixture q)throws Exception{
  if(q==null)throw new IOException("FIXTURE_BLOCKED");prepareAsset(q.asset,q.bytes,q.sha256);stage="QUALIFIED_AVC_CAPTURE";
  observation=inspect(sourceFile,method.unknown,method.chunk,method.seekUs,method==ExperimentContract.Method.muxQualified,"qualified6_"+q.sha256.substring(0,16));
  requireAdmission();QualifiedObservation.require(observation,true);
  normalizedFingerprint=VerifiedFixtureCopy.hash(normalized(observation).toString().getBytes(StandardCharsets.UTF_8));
  if(method==ExperimentContract.Method.inspectSeek1s&&(observation.seeks.stream().noneMatch(x->x.reason.equals("SEEK_MAP")&&x.requestedTimeUs==1000000)||observation.replay.isEmpty()))throw new IOException("REAL_SEEK_OBSERVATION_MISSING");
  if(method!=ExperimentContract.Method.muxQualified){status="OBSERVED_HOST_STRUCTURE_ONLY";return;}
  requireAdmission();stage="REAL_MUX_TO_TEMPORARY_OUTPUT";OwnedFiles.OutputCapability host=new OwnedFiles.OutputCapability(this,outputFile);providers.add(host.readback);requireAdmission();output=new TemporaryOutput(host,false,AndroidInput.WORKER,5000,android.os.Process.myUid(),android.os.Process.myPid());requireAdmission();
  reopened=MatureContainerRemux.writeAndInspect(observation,output);QualifiedObservation.require(reopened,false);if(output.validationAcknowledged()||output.readyAcknowledged()||output.committed()||host.readyCalls!=0)throw new IOException("HOST_STRUCTURE_ESCALATION_FORBIDDEN");
  boolean actualDuration=reopened.durationUs==1200000||reopened.tracks.stream().anyMatch(track->track.reportedDurationUs==1200000);if(!actualDuration)throw new IOException("ACTUAL_EOS_DURATION_NOT_PROVEN");status="OBSERVED_HOST_MUX_STRUCTURE_ONLY";
 }
 private void cleanup(){
  stage=stage+"_CLEANUP";for(HostInputFactory f:factories){f.close();try{if(!f.awaitOriginalReturns(5000))fail("SOURCE_ORIGINAL_RETURN_PENDING");}catch(Throwable e){fail("SOURCE_ORIGINAL_RETURN_UNKNOWN");}}
  if(output!=null)try{if(!output.abort())fail("OUTPUT_ORIGINAL_RETURN_PENDING");}catch(Throwable e){fail("OUTPUT_ORIGINAL_RETURN_UNKNOWN");}
  else if(outputHost!=null)closeOnce(outputHost.original);
  // No second close for failed/UNKNOWN allocations. EMPTY proves never admitted.
  boolean all=resourcesReturned();if(all&&ownRoot){/* Preserve this new run root as evidence. Never delete or overwrite an old run. */}
  if(!all){stopped=true;status="UNKNOWN_ORIGINAL_RETURN_PENDING";}
 }
 boolean resourcesReturned(){
  for(E4Owned<?> owner:assetOwners)if(owner.state()!=E4Owned.State.EMPTY&&!owner.returned())return false;
  for(HostInputFactory f:factories)try{if(!f.originalsReturned())return false;}catch(InterruptedException e){Thread.currentThread().interrupt();return false;}
  for(OwnedFiles.ReadCapability provider:providers)if(!provider.descriptorsReturned())return false;
  if(outputHost!=null&&!outputHost.original.returned())return false;if(output!=null&&!output.returned())return false;
  return E13SourceGroup.canFinish()&&HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0;
 }
 void awaitOriginalReturns()throws Exception{Thread worker=originalWorker;if(worker!=null&&worker!=Thread.currentThread())worker.join();E13SourceGroup.awaitOriginalReturns();}
 boolean canFinish(){return workerBodyReturned&&originalWorker!=null&&!originalWorker.isAlive()&&resourcesReturned();}
 private static JSONObject sample(HostMp4Inspection.Sample s)throws JSONException{return new JSONObject().put("ptsUs",s.timeUs).put("flags",s.flags).put("keyframe",(s.flags&1)!=0).put("size",s.size).put("sha256",s.sha256);}
 private static JSONObject normalized(HostMp4Inspection.Evidence e)throws Exception{
  JSONArray tracks=new JSONArray();for(HostMp4Inspection.Track t:e.tracks){JSONArray csd=new JSONArray();int sum=0;if(t.format.initializationData.size()>16)throw new IOException("CSD_RECEIPT_BUDGET");for(byte[] b:t.format.initializationData){sum+=b.length;if(sum>65536)throw new IOException("CSD_RECEIPT_BUDGET");csd.put(new JSONObject().put("bytes",b.length).put("sha256",VerifiedFixtureCopy.hash(b)));}JSONArray ss=new JSONArray();for(HostMp4Inspection.Sample s:t.samples)ss.put(sample(s));tracks.put(new JSONObject().put("id",t.id).put("type",t.type).put("mime",t.format.sampleMimeType).put("width",t.format.width).put("height",t.format.height).put("rotation",t.format.rotationDegrees).put("sampleRate",t.format.sampleRate).put("channels",t.format.channelCount).put("drm",t.format.drmInitData!=null).put("trackOutputReportedDurationUs",t.reportedDurationUs).put("csd",csd).put("samples",ss));}return new JSONObject().put("tracks",tracks);
 }
 private static JSONObject parser(HostMp4Inspection.Evidence e)throws Exception{
  JSONObject p=normalized(e).put("extractorClass",e.actualExtractorClass).put("kind",e.kind).put("wholeEof",e.fullReadEof).put("bytes",e.bytes).put("sha256",e.sha256).put("physicalReaderBytes",e.physicalBytesRead).put("announcedLength",e.announcedLength).put("parserEof",e.extractorEof).put("sniffMatched",e.sniffMatched).put("peekReset",e.peekReset).put("endTracks",e.endTracksObserved).put("seekable",e.seekable).put("actualSeekMapDurationUs",e.durationUs).put("extractorReleaseReturned",e.extractorReleaseReturned()).put("dataSourceCloseReturned",e.dataSourceCloseReturned());
  JSONArray ranges=new JSONArray();for(HostMp4Inspection.RangeObservation r:e.ranges)ranges.put(new JSONObject().put("position",r.position).put("remaining",r.remaining).put("absoluteEnd",r.absoluteEnd).put("sourceVersion",r.sourceVersion).put("epoch",r.epoch).put("generation",r.generation).put("uid",r.uid).put("pid",r.pid));p.put("ranges",ranges);
  JSONArray seeks=new JSONArray();for(HostMp4Inspection.SeekObservation s:e.seeks)seeks.put(new JSONObject().put("reason",s.reason).put("requestedUs",s.requestedTimeUs).put("position",s.position).put("pointTimeUs",s.pointTimeUs));p.put("seekEvents",seeks).put("parserEndPositions",new JSONArray(e.parserEofPositions));JSONArray replay=new JSONArray();for(HostMp4Inspection.ReplayObservation r:e.replay)replay.put(new JSONObject().put("trackId",r.trackId).put("sample",sample(r.sample)));return p.put("replay",replay);
 }
 String receipt(boolean finishGateReady)throws Exception{
  JSONObject result=new JSONObject().put("candidate",ExperimentContract.VERSION).put("case",method.name()).put("scopeEntry",requestedMethod.name()).put("runId",runId).put("identity",identity).put("status",deadlineUnknown?"UNKNOWN_DEADLINE_NO_SUCCESS_UPGRADE":status).put("stage",stage).put("firstFailure",firstFailure==null?JSONObject.NULL:firstFailure).put("deadlineMs",ExperimentContract.METHOD_DEADLINE_MS).put("stopped",stopped).put("qualifiedFixtureSha256",ExperimentContract.qualifiedFixture().sha256).put("media3DtsCapability","NO_INDEPENDENT_DTS_API_HOST_NO_CTTS_FIXTURE_ONLY").put("sampleRepresentation","ACTUAL_MEDIA3_ANNEXB4_HASH").put("startedNano",startedNano).put("completedNano",completedNano).put("timelyOriginalBody",workerBodyReturned&&completedNano-startedNano>=0&&completedNano-startedNano<60000000000L).put("inputAttemptedReserved",inputReserved).put("inputActuallyReturned",inputActual).put("inputBudget",8388608).put("sourcePeakObserved",peakSources).put("copyReadOnly",readOnlyCopy).put("copySyncReturned",copySynced).put("finishGateReady",finishGateReady).put("workerActuallyJoined",originalWorker!=null&&!originalWorker.isAlive()).put("originalResourcesReturned",canFinish()).put("sourceKeepers",HostInputFactory.admittedSources()).put("outputKeepers",TemporaryOutput.retained()).put("runnerFinalizerOwnerAtReceipt",E13FinishOwner.retained()).put("runnerFinishReturn","EXTERNAL_ORIGINAL_CAPTURE_REQUIRED").put("scope","HOST_STRUCTURE_ONLY_NOT_ISOLATED_OR_PLAYBACK");
  if(copyReceipt!=null)result.put("copy",new JSONObject().put("bytes",copyReceipt.bytes).put("sha256",copyReceipt.sha256).put("assetUnderlyingEof",copyReceipt.fullEof));
  if(observation!=null)result.put("observation",parser(observation));if(normalizedFingerprint!=null)result.put("normalizationFingerprint",normalizedFingerprint);if(reopened!=null)result.put("reopened",parser(reopened));
  JSONArray nativeSources=new JSONArray();for(OwnedFiles.ReadCapability provider:providers)synchronized(provider){nativeSources.put(new JSONObject().put("providerIdentityWithinProcess",System.identityHashCode(provider)).put("openCalls",provider.opens).put("closeReturns",provider.closes).put("readCalls",provider.readCalls).put("physicalBytes",provider.physicalBytes).put("actualNativeEofReads",provider.eofReads).put("readInFlightPeak",provider.peak).put("sourceEpochs",new JSONArray(provider.epochs)).put("firstReadOffsets",new JSONArray(provider.firstOffsets)).put("sameNativeFDHoldersReturned",provider.descriptorsReturned()));}result.put("nativeSources",nativeSources);
  result.put("outputAttemptedReserved",outputAttemptReserved).put("nativeMuxAttemptedReserved",outputHost==null?0:outputHost.attempted).put("outputAttemptBudget",16777216).put("nativeFdSyncCapability",true).put("nativeFdSyncSuccess",outputHost!=null&&outputHost.flushReturned).put("outputOriginalCloseReturn",outputHost!=null&&outputHost.original.returned()).put("muxWriteAcknowledgedLowerBound",outputHost==null?0:outputHost.bytes).put("muxReadyCalls",outputHost==null?0:outputHost.readyCalls).put("muxReopenCalls",outputHost==null?0:outputHost.reopens).put("muxFlushSyncReturned",outputHost!=null&&outputHost.flushReturned).put("muxWriterOriginalReturned",outputHost==null||outputHost.writerOriginalsReturned());
  if(method==ExperimentContract.Method.scopeAll)result.put("caseReceipts",caseReceipts).put("expectedCaseCount",10).put("completedCaseCount",caseReceipts.length()).put("scopeBudgetsSharedAcrossAllCases",true);
  String text=result.toString();if(text.getBytes(StandardCharsets.UTF_8).length>ExperimentContract.RECEIPT_UTF8_MAX){fail("RECEIPT_BYTE_BUDGET");return new JSONObject().put("candidate",ExperimentContract.VERSION).put("case",method.name()).put("scopeEntry",requestedMethod.name()).put("runId",runId).put("status",deadlineUnknown?"UNKNOWN_DEADLINE_RECEIPT_BUDGET":"FAILED_RECEIPT_BYTE_BUDGET").put("observationComplete",false).put("originalResourcesReturned",canFinish()).put("finishGateReady",finishGateReady).toString();}return text;
 }
}
