from pathlib import Path
import json,struct,hashlib,zipfile,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1media3-android01'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(E/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def methods(b):
 def u(p):
  v=0;s=0
  while True:
   a=b[p];p+=1;v|=(a&127)<<s
   if not a&128:return v,p
   s+=7
 sn,so=struct.unpack_from('<II',b,56);tn,to=struct.unpack_from('<II',b,64);mn,mo=struct.unpack_from('<II',b,88);cn,co=struct.unpack_from('<II',b,96);ss=[]
 for i in range(sn):
  p=struct.unpack_from('<I',b,so+i*4)[0];_,p=u(p);ss.append(b[p:b.index(0,p)].decode('utf8','replace'))
 types=[ss[struct.unpack_from('<I',b,to+i*4)[0]] for i in range(tn)];ms=[(types[c],ss[n]) for c,proto,n in [struct.unpack_from('<HHI',b,mo+i*8) for i in range(mn)]];out={}
 for i in range(cn):
  cls=types[struct.unpack_from('<I',b,co+i*32)[0]];p=struct.unpack_from('<I',b,co+i*32+24)[0]
  if not p:continue
  sizes=[]
  for j in range(4):n,p=u(p);sizes.append(n)
  for j in range(sizes[0]+sizes[1]):_,p=u(p);_,p=u(p)
  rows=[]
  for n in sizes[2:]:
   idx=0
   for j in range(n):
    delta,p=u(p);idx+=delta;flags,p=u(p);code,p=u(p);row=dict(name=ms[idx][1],codeOffset=code,accessFlags=flags)
    if code:
     units=struct.unpack_from('<I',b,code+12)[0];row.update(instructionUnits=units,instructionsSha256=hashlib.sha256(b[code+16:code+16+units*2]).hexdigest())
    rows.append(row)
  out[cls]=rows
 return out
required={'test':{'Lcom/videokit/d1media3/android01/test/Media3Instrumentation;':['onCreate','onStart','finish','onException'],'Lcom/videokit/d1media3/android01/test/ExperimentJob;':['run','canFinish','resourcesReturned','runQualified','receipt'],'Lcom/videokit/d1media3/android01/test/OwnedFiles$ReadCapability;':['open','descriptorsReturned']},'app':{'Lcom/videokit/d1android/ExperimentContract;':['admit','qualifiedFixture'],'Lcom/videokit/d1android/VerifiedFixtureCopy;':['copy'],'Lcom/videokit/d1input/HostMp4Inspection;':['inspect'],'Lcom/videokit/spike/e4/E13FinishOwner;':['run','request'],'Landroidx/media3/extractor/mp4/Mp4Extractor;':['read','sniff'],'Landroidx/media3/extractor/mp4/FragmentedMp4Extractor;':['read','sniff'],'Landroidx/media3/muxer/FragmentedMp4Muxer;':['writeSampleData','close']}}
results={}
for kind,checks in required.items():
 with zipfile.ZipFile(B/f'artifacts/media3-android01-{kind}-debug.apk') as z:
  allMethods={k:v for n in z.namelist() if n.endswith('.dex') for k,v in methods(z.read(n)).items()}
  rows={}
  for cls,names in checks.items():
   actual=allMethods[cls]
   for name in names:assert any(x['name']==name and x['codeOffset']>0 and x['instructionUnits']>0 for x in actual),(cls,name)
   rows[cls]=[x for x in actual if x['name'] in names]
  if kind=='test':assert not any(c.startswith('Landroidx/media3/') or c.startswith('Lorg/jcodec/') for c in allMethods)
  results[kind]=rows
save('dex-implemented-methods.json',dict(result='PASS_ACTUAL_DEX_CODE_OFFSETS_STATIC_ONLY',classes=results,doesNotProveAndroidExecution=True))
supp=R/'docs/coder/d1media3-android01-closeout01/supplement-manifest.json';d=load(supp)
for r in d['files']:p=R/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
plan=R/'docs/coder/D1_MEDIA3_ANDROID01_READY_ORIGINAL_SESSION_CLOSEOUT_PLAN_V1.0.md';assert sha(plan)=='e6055b772048a0f192efe594258a690d0d2575ca8732522999ce11c29be5a129'
save('closeout-supplement-review.json',dict(result='REVIEWED_PLAN_A_RETAINS_UNKNOWN_NO_CURRENT_STATE_PROOF',planSha256=sha(plan),supplementManifestSha256=sha(supp),filesVerified=len(d['files']),oneTimeResults=load(R/'docs/coder/d1media3-android01-closeout01/one-time-existing-session-results.json'),reviewerDidNotPollOrAttachOrIntervene=True,parentDispatchGate='NOT_PROVEN_CLOSED; loaded parent for-loop can still dispatch final case if child returns',futureOptions='A retain UNKNOWN; B exact original parent atomic dispatch barrier only if approved existing capability confirmed; C separately approved exact-parent-first intervention with narrow-window/new-child check and evidence-loss disclosure; none executed',rootCause='UNKNOWN',pidReuseOrCurrentIdentity='NOT_VERIFIED',jcmdOwnPid='UNKNOWN_TARGET_ARGUMENT_39256_IS_NOT_JCMD_PID',recommendation='Keep static materials verdict separate; coordinator decides exact original-owner resolution and new execution gate. Do not clear UNKNOWN, kill child first, repeat tests, or infer global idle'))
old=load(R/'docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_A_EVIDENCE/independent-oracles.json')['cases'];assert len(old)==24
staticIds={'MA01','MA02','MA03','MA10','MA12','MA14','MA15','MA21','MA22','MA23','MA24'}
for c in old:
 c['phaseAStatus']=c['status'];c['status']='PASS_STATIC_MATERIAL_ONLY' if c['id'] in staticIds else 'NOT_RUN_ACTUAL_PATH';c['independentRuntime']='NOT_RUN_BY_FORMAL_B_INSTRUCTION';c['actualAndroid']='NOT_RUN';c['executionAuthorized']=False
 if c['id'] in {'MA16','MA17','MA18','MA19','MA20'}:c['status']='FIXTURE_BLOCKED_REAL_POSITIVE_NOT_RUN'
 if c['id']=='MA15':c['status']='SOURCE_PROPOSAL_REVIEWED_UNBUILT_BLOCKS_EXECUTION'
 if c['id']=='MA21':c['status']='INHERITED_LIMITED_FIX_STATIC_DIFF_ONLY_NEW_RUNTIME_NOT_RUN'
save('independent-ma01-ma24-results.json',dict(overall='STATIC_MATERIAL_REVIEW_COMPLETE_WITH_LOCAL_UNKNOWN_AND_FUNCTIONAL_GAPS',cases=old,localOriginalReturn='UNKNOWN',newIndependentFunctionalRuns=0,sourceProposalBuiltLoadedEncoded=False))
save('review-process-note.json',dict(initialAuditExit=1,reason='Tester overbroad active-directory exclusion also matched old immutable candidate suites-001. Narrowed exclusion to exact current Android01 active directory before further audit.',initialScript='audit_materials-initial.py',finalScript='audit_materials.py',productFailure=False,productOrOldEvidenceChanged=False,initialFailureOccurredBeforeStaticJvmTools=True,finalStaticToolsReturned=True,caseTestsRun=False))
print('PASS DEX implementation offsets; external closeout supplement; MA01-24 static/NOT_RUN mapping')
