from pathlib import Path
B=Path(__file__).resolve().parents[1]
def edit(rel,old,new):
 p=B/rel;s=p.read_text();assert old in s,(rel,old[:60]);p.write_text(s.replace(old,new),encoding='utf-8')
J='instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java'
edit(J,'volatile Thread originalWorker;','volatile long startedNano,completedNano;\n volatile Thread originalWorker;')
edit(J,'if(method==ExperimentContract.Method.muxQualified&&ExperimentContract.qualifiedFixture()==null){stage="QUALIFIED_FIXTURE_GATE";status="FIXTURE_BLOCKED";return;}','''if(method==ExperimentContract.Method.rejectFixture){
   stage="REJECT_FIXTURE_BEFORE_IO";try{ExperimentContract.admit(Map.of("case","muxQualified","fixtureSha256",ExperimentContract.SAMPLE_SHA,"runId",runId));throw new IOException("GUARD_NOT_ENFORCED");}catch(IOException e){if(!"EXPERIMENT_ARGUMENT_REJECTED".equals(e.getMessage()))throw e;}
   status="PREOPEN_GUARDS_OBSERVED";return;
  }
  if(method==ExperimentContract.Method.cancelLateRead||method==ExperimentContract.Method.writerPending){stage="CONTROLLED_ORIGINAL_RETURN_BOUNDARY";BoundaryScenarios.run(method.name(),AndroidInput.WORKER);status="PREOPEN_GUARDS_OBSERVED";return;}''')
edit(J,'if(method==ExperimentContract.Method.muxQualified){runQualified(ExperimentContract.qualifiedFixture());return;}','''if(method!=ExperimentContract.Method.bbbObserve){runQualified(ExperimentContract.qualifiedFixture());return;}''')
edit(J,'workerBodyReturned=true;E13ReturnEvents.returned();','completedNano=System.nanoTime();workerBodyReturned=true;E13ReturnEvents.returned();')
edit(J,'new File(cache,"d1media3-android02-run")','new File(cache,"d1media3-android02-"+runId)')
edit(J,'dest.allocate(()->new FileOutputStream(sourceFile,false));','dest.allocate(()->OwnedFiles.createNew(sourceFile));')
start=(B/J).read_text().index('  if(q==null)throw new IOException("FIXTURE_BLOCKED");')
end=(B/J).read_text().index('  requireAdmission();stage="REAL_MUX_TO_TEMPORARY_OUTPUT";',start)
p=B/J;s=p.read_text();s=s[:start]+'''  if(q==null)throw new IOException("FIXTURE_BLOCKED");prepareAsset(q.asset,q.bytes,q.sha256);stage="QUALIFIED_AVC_CAPTURE";
  observation=inspect(sourceFile,method.unknown,method.chunk,method.seekUs,method==ExperimentContract.Method.muxQualified,"qualified6_"+q.sha256.substring(0,16));
  requireAdmission();QualifiedObservation.require(observation,true);
  normalizedFingerprint=VerifiedFixtureCopy.hash(normalized(observation).toString().getBytes(StandardCharsets.UTF_8));
  if(method==ExperimentContract.Method.inspectSeek1s&&(observation.seeks.stream().noneMatch(x->x.reason.equals("SEEK_MAP")&&x.requestedTimeUs==1000000)||observation.replay.isEmpty()))throw new IOException("REAL_SEEK_OBSERVATION_MISSING");
  if(method!=ExperimentContract.Method.muxQualified){status="OBSERVED_HOST_STRUCTURE_ONLY";return;}
'''+s[end:];p.write_text(s,encoding='utf-8')
edit(J,'reopened=MatureContainerRemux.writeAndInspect(observation,output);','reopened=MatureContainerRemux.writeAndInspect(observation,output);QualifiedObservation.require(reopened,false);')
edit(J,'if(all&&ownRoot){if(sourceFile.exists()&&!sourceFile.delete())fail("PRIVATE_SOURCE_DELETE_FAILED");if(outputFile.exists()&&!outputFile.delete())fail("PRIVATE_OUTPUT_DELETE_FAILED");if(!root.delete())fail("PRIVATE_ROOT_DELETE_FAILED");}','if(all&&ownRoot){/* Preserve this new run root as evidence. Never delete or overwrite an old run. */}')
edit(J,'.put("inputAttemptedReserved",inputReserved)','.put("qualifiedFixtureSha256",ExperimentContract.qualifiedFixture().sha256).put("media3DtsCapability","NO_INDEPENDENT_DTS_API_HOST_NO_CTTS_FIXTURE_ONLY").put("sampleRepresentation","ACTUAL_MEDIA3_ANNEXB4_HASH").put("startedNano",startedNano).put("completedNano",completedNano).put("timelyOriginalBody",workerBodyReturned&&completedNano-startedNano>=0&&completedNano-startedNano<60000000000L).put("inputAttemptedReserved",inputReserved)')
edit(J,'.put("muxWriteAcknowledgedLowerBound",outputHost==null?0:outputHost.bytes)','.put("outputAttemptedReserved",outputHost==null?0:outputHost.attempted).put("outputAttemptBudget",16777216).put("nativeFdSyncCapability",true).put("nativeFdSyncSuccess",outputHost!=null&&outputHost.flushReturned).put("outputOriginalCloseReturn",outputHost!=null&&outputHost.original.returned()).put("muxWriteAcknowledgedLowerBound",outputHost==null?0:outputHost.bytes)')
I='instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java'
edit(I,'worker.start();worker.join(ExperimentContract.METHOD_DEADLINE_MS);','j.startedNano=System.nanoTime();worker.start();worker.join(ExperimentContract.METHOD_DEADLINE_MS);')
edit(I,'if(worker.isAlive()){','if(worker.isAlive()||!j.workerBodyReturned||j.completedNano-j.startedNano<0||j.completedNano-j.startedNano>=60000000000L){')
F='instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java'
edit(F,' static <T>CompletionStage<T> failed', ''' static FileOutputStream createNew(File f)throws IOException{
  try{return new FileOutputStream(android.system.Os.open(f.getAbsolutePath(),android.system.OsConstants.O_WRONLY|android.system.OsConstants.O_CREAT|android.system.OsConstants.O_EXCL|android.system.OsConstants.O_NOFOLLOW,0600));}catch(android.system.ErrnoException e){throw new IOException("CREATE_NEW_PRIVATE_FILE_FAILED",e);}
 }
 static <T>CompletionStage<T> failed''')
edit(F,'long bytes;int flushes','long bytes,attempted;int flushes')
edit(F,'new FileOutputStream(file,false)','createNew(file)')
edit(F,'n>16777216-bytes','n>16777216-attempted')
edit(F,'original.original().write(b,off,n);','attempted+=n;original.original().write(b,off,n);')
edit(F,'android01_mux_private','android02_mux_private')
# One attempt budget, never refund short acknowledgements or unknown writes.
edit('src/com/videokit/d1input/TemporaryOutput.java','n>MAX_OUTPUT-written','n>MAX_OUTPUT-writeAttemptedBytes')
edit('src/com/videokit/d1input/TemporaryOutput.java','b.remaining()>MAX_OUTPUT-written','b.remaining()>MAX_OUTPUT-writeAttemptedBytes')
edit('src/com/videokit/d1input/MatureContainerRemux.java','  MatureMuxerBinding binding=new MatureMuxerBinding(output);','  com.videokit.d1android.QualifiedObservation.require(input,true);\n  MatureMuxerBinding binding=new MatureMuxerBinding(output);')
# CSD list grouping can change; concatenated actual AnnexB CSD must match same exact20 bytes.
p=B/'src/com/videokit/d1input/MatureContainerRemux.java';s=p.read_text();a=s.index('  if(actual.format.initializationData.size()!=');b=s.index('  for(int i=0;i<6;i++)if(actual.samples',a);s=s[:a]+'''  if(!com.videokit.d1android.QualifiedObservation.csdHash(actual).equals(com.videokit.d1android.QualifiedObservation.csdHash(track))){output.rejectHostStructure();throw new IOException("MP4_REOPEN_CONFIG_MISMATCH");}
'''+s[b:];p.write_text(s,encoding='utf-8')
edit('src/com/videokit/d1android/ExperimentContract.java','/** Empty registry is deliberate: approved320x180+AAC cannot be used as AVC6.\n  * A future reviewed candidate must embed its exact qualified manifest and asset;\n  * runtime arguments cannot register a fixture. No hashes/CSD are invented here. */','/** Only the exact independently qualified synthetic asset is registered. BBB remains observation-only. */')
print('Android02 full fixed-fixture path, single attempt budgets and original-deadline evidence implemented')
