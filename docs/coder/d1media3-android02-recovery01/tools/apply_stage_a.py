from pathlib import Path
import json,hashlib,shutil,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';assert json.loads((E/'build-001/owner.json').read_text())['exitCode']==0
snap=E/'build-001/before-stage-a';snap.mkdir()
for n in ['src','android','upstream','instrumentation','app/src']:shutil.copytree(B/n,snap/n)
for n in ['app/build.gradle.kts','tools/build_once.py']:p=snap/n;p.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(B/n,p)
for rel,n in [('app/build/outputs/apk/debug/app-debug.apk','app.apk'),('app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk','test.apk')]:shutil.copyfile(B/rel,snap/n)
for name,folder in [('app-classes.jar','app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'),('test-classes.jar','app/build/intermediates/javac/debugAndroidTest/compileDebugAndroidTestJavaWithJavac/classes')]:
 with zipfile.ZipFile(snap/name,'x',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((B/folder).rglob('*.class')):z.write(p,p.relative_to(B/folder).as_posix())
for n in ['D1_MEDIA3_ANDROID02_CONTAINER_PHASE_A_REPORT_V1.0.md']:shutil.copyfile(R/'docs/tester'/n,B/'reference'/n)
shutil.copytree(R/'docs/tester/D1_MEDIA3_ANDROID02_CONTAINER_PHASE_A_EVIDENCE',B/'reference/android02-stage-a')
requirement=R/'docs/milestones/D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_CODER_REQUIREMENTS_V1.0.md';shutil.copyfile(requirement,B/'reference'/requirement.name)
def edit(rel,old,new):
 p=B/rel;s=p.read_text();assert old in s,(rel,old[:50]);p.write_text(s.replace(old,new),encoding='utf-8')
C='src/com/videokit/d1android/ExperimentContract.java'
edit(C,'  inspectKnown(65536','  scopeAll(65536,false,-1),inspectKnown(65536')
edit(C,'try{return Method.valueOf(args.get("case"));}','try{Method m=Method.valueOf(args.get("case"));if(m!=Method.scopeAll)throw new IllegalArgumentException("EXPERIMENT_BATCH_ONLY");return m;}')
for rel in [C,'app/build.gradle.kts','app/src/androidTest/AndroidManifest.xml']:edit(rel,'D1-MEDIA3-ANDROID02-CONTAINER','D1-MEDIA3-ANDROID02-RECOVERY01')
Q='src/com/videokit/d1android/QualifiedObservation.java'
edit(Q,'s.flags!=q.flags.get(i)','!supportedFlags(s.flags,i)')
edit(Q,' private QualifiedObservation(){}',''' /** Raw extractor flags stay in receipts. LAST_SAMPLE is a Media3 marker, not a host key boolean. */
 public static boolean supportedFlags(int raw,int index){int allowed=C.BUFFER_FLAG_KEY_FRAME|C.BUFFER_FLAG_LAST_SAMPLE;return (raw&C.BUFFER_FLAG_KEY_FRAME)!=0&&(raw&~allowed)==0&&((raw&C.BUFFER_FLAG_LAST_SAMPLE)==0||index==5);}
 private QualifiedObservation(){}''')
M='src/com/videokit/d1input/MatureContainerRemux.java'
edit(M,'new BufferInfo(sample.timeUs,sample.size,sample.flags)','new BufferInfo(sample.timeUs,sample.size,sample.flags&C.BUFFER_FLAG_KEY_FRAME)')
edit(M,'actual.samples.get(i).timeUs!=track.samples.get(i).timeUs','(actual.samples.get(i).flags&C.BUFFER_FLAG_KEY_FRAME)!=(track.samples.get(i).flags&C.BUFFER_FLAG_KEY_FRAME)||actual.samples.get(i).timeUs!=track.samples.get(i).timeUs')
J='instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java'
edit(J,'final ExperimentContract.Method method;','ExperimentContract.Method method;final ExperimentContract.Method requestedMethod;')
edit(J,'runner=r;method=m;','runner=r;method=m;requestedMethod=m;')
edit(J,'volatile long inputReserved,inputActual;','volatile long inputReserved,inputActual,outputAttemptReserved;final JSONArray caseReceipts=new JSONArray();')
edit(J,' synchronized void inputReturned',' synchronized void reserveOutput(int bytes)throws IOException{requireAdmission();if(bytes<1||bytes>65536||bytes>16777216-outputAttemptReserved)throw new IOException("OUTPUT_SCOPE_ATTEMPT_BUDGET");outputAttemptReserved+=bytes;}\n synchronized void inputReturned')
edit(J,' void run(){try{',''' void run(){try{
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
 private void runCase()throws Exception{''')
edit(J,' }catch(Throwable e){fail(safe(e));if("MP4_SEEK_UNSUPPORTED".equals(e.getMessage()))status="UNSUPPORTED_REAL_SEEK_MAP";}\n finally{try{cleanup();}catch(Throwable t){fail("ORIGINAL_CLEANUP_UNKNOWN");}finally{completedNano=System.nanoTime();workerBodyReturned=true;E13ReturnEvents.returned();}}}\n private void newRoot()', ' }\n private void newRoot()')
edit(J,'BoundaryScenarios.run(method.name(),AndroidInput.WORKER);','if(method==ExperimentContract.Method.cancelLateRead)reserveInput(1);else reserveOutput(4);BoundaryScenarios.run(method.name(),AndroidInput.WORKER);')
edit(J,'"d1media3-android02-"+runId','"d1media3-android02-"+runId+"-"+method.name()')
edit(J,'.put("case",method.name()).put("runId",runId)','.put("case",method.name()).put("scopeEntry",requestedMethod.name()).put("runId",runId)')
edit(J,'.put("outputAttemptedReserved",outputHost==null?0:outputHost.attempted)','.put("outputAttemptedReserved",outputAttemptReserved).put("nativeMuxAttemptedReserved",outputHost==null?0:outputHost.attempted)')
edit(J,'  String text=result.toString();','  if(method==ExperimentContract.Method.scopeAll)result.put("caseReceipts",caseReceipts).put("expectedCaseCount",10).put("completedCaseCount",caseReceipts.length()).put("scopeBudgetsSharedAcrossAllCases",true);\n  String text=result.toString();')
F='instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java'
edit(F,'attempted+=n;original.original().write','job.reserveOutput(n);attempted+=n;original.original().write')
I='instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java'
edit(I,'return status.equals("OBSERVED_HOST_STRUCTURE_ONLY")','return status.equals("OBSERVED_ALL_SCOPE_HOST_STRUCTURE_ONLY")||status.equals("OBSERVED_HOST_STRUCTURE_ONLY")')
# Latest appended authority explicitly covers necessary stage-A source changes within total2 builds.
P='tools/build_once.py'
edit(P,"assert prior.get('sourceCompileFailure') and prior.get('daemonOriginalReturned') and prior.get('exitCode')==1","assert prior.get('daemonOriginalReturned') and prior.get('exitCode') in [0,1] and (prior.get('sourceCompileFailure') or (E/'stage-a-source-change-authority.json').exists())")
dump={'reportSha256':'82a2f7942023d16a7cf98a4e5c24be052e2d8ebf946b401ab63742bd2724a02c','authoritySnapshot':str(requirement.relative_to(R)),'authoritySnapshotSha256':hashlib.sha256(requirement.read_bytes()).hexdigest(),'reason':'New full-stage-A requirements arrived during first build: single original scope worker runs10 cases with same cumulative input/output counters; raw flags preserve and predeclare LAST_SAMPLE semantics; new recovery version. Current supplement explicitly allows necessary changes under max2 concentrated builds.','firstBuild':{'exitCode':0,'sourceErrors':False,'initialSourcePins':'initial-recovery-input-pins.json'},'nextBuildMaximum':1}
(E/'stage-a-source-change-authority.json').write_text(json.dumps(dump,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pins=[{'path':p.relative_to(B).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for name in ['src','android','upstream','instrumentation','app/src','instrumentation-assets','notice-assets','gradle'] for p in sorted((B/name).rglob('*')) if p.is_file()]+[{'path':n,'sha256':hashlib.sha256((B/n).read_bytes()).hexdigest()} for n in ['app/build.gradle.kts','app/gradle.lockfile','settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties']]
(E/'final-build-input-pins.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
print('First build/source artifacts preserved; complete stage-A changes prepared for second and final build')
