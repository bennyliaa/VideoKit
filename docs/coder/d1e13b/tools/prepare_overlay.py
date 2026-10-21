"""Metadata overlay only: exact base product reuse and three direct argv; never executes adb."""
from pathlib import Path
import hashlib,json,re,shlex,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e13a';O=B/'release/metadata';O.mkdir(parents=True,exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):b=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':sha(b)}
def js(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
Q=shlex.quote
reader=(B/'tools/processes_reader.sh').read_text()
collector='''e13b_collect_state() {
 if value=$({
  if dumpsys activity processes 2>&1; then e_dump_code=0; else e_dump_code=$?; fi
  printf '\\nE13B_DUMPSYS_EXIT=%s\\n' "$e_dump_code"
 } | e13b_parse_processes); then e_collect_code=0; else e_collect_code=$?; fi
 size=$(printf '%s' "$value" | wc -c)
 if [ "$size" -gt 4096 ]; then printf 'RECORD_OVERSIZE\\tINSTRUMENTATION\\n' >&2; exit 22; fi
 printf 'BEGIN\\tINSTRUMENTATION\\n%s\\nEND\\tINSTRUMENTATION\\n' "$value"
 if [ "$e_collect_code" -ne 0 ]; then printf 'E13B_METADATA_BLOCKED\\n' >&2; exit 21; fi
 case "$value" in
  'E13B_PROCESS_SNAPSHOT_V1 state=IDLE'*) :;;
  'E13B_PROCESS_SNAPSHOT_V1 state=ACTIVE'*) printf 'E13B_ENVIRONMENT_WAIT_NO_DEPLOY_NO_TEST\\n' >&2; exit 73;;
  *) printf 'E13B_METADATA_BLOCKED_UNKNOWN_FRAME\\n' >&2; exit 21;;
 esac
}
'''
user_filter='''dumpsys user | {
 e_want=0
 while IFS= read -r e_row; do
  case "$e_row" in *UserInfo*)case "$e_row" in *'UserInfo{0:'*)e_want=1;;*)e_want=0;;esac;;esac
  if [ "$e_want" -eq 1 ]; then case "$e_row" in *UserInfo*|*State:*)printf '%s\\n' "$e_row";;esac;fi
 done
}'''
ps_filter='''ps -A -o PID,PPID,UID,NAME | {
 IFS= read -r e_row || exit 1
 printf '%s\\n' "$e_row"
 while IFS= read -r e_row; do
  case "$e_row" in *com.videokit.app*|*com.videokit.e13.sender*)printf '%s\\n' "$e_row";;esac
 done
}'''
def pkg_filter(pkg):return 'dumpsys package '+pkg+''' | sed -n '/^[ ]*userId=/p; /^[ ]*versionCode=/p; /^[ ]*User 0:/p' '''
base=json.loads((OLD/'release/metadata/three-client-manifest.json').read_text());clients=[]
for item in base['clients']:
 stage=item['id'];oldscript=R/item['script']['path'];script=oldscript.read_text()
 expected='emit INSTRUMENTATION 4096 dumpsys activity instrumentation';assert script.count(expected)==1
 script=script.replace(expected,reader+'\n'+collector+'\ne13b_collect_state')
 nested=[]
 for body in item['nestedShellBodiesForSyntaxAudit']:
  replacement=body
  if body.startswith('dumpsys user | awk '):replacement=user_filter
  elif body.startswith('ps -A -o PID,PPID,UID,NAME | awk '):replacement=ps_filter
  else:
   m=re.match(r'dumpsys package ([A-Za-z0-9.]+) \| awk ',body)
   if m:replacement=pkg_filter(m[1])
  if replacement!=body:
   assert script.count(Q(body))==1,(stage,body[:40]);script=script.replace(Q(body),Q(replacement))
  nested.append(replacement)
 assert 'awk ' not in script and 'dumpsys activity instrumentation' not in script
 assert script.count('if dumpsys activity processes 2>&1;')==1 # exactly one query; other occurrences are source/header checks
 file=O/(stage+'.sh');file.write_text(script,encoding='utf-8',newline='\n')
 argv=item['argv'][:-1]+[Q(script)];assert shlex.split(argv[-1])==[script]
 cmdchars=len(subprocess.list2cmdline(argv).encode('utf-16-le'))//2+1;assert cmdchars<=32767,(stage,cmdchars)
 new=dict(item);new.update({'script':pin(file),'argv':argv,'metadataRevision':'D1-E13B-METADATA-ONLY','baseProductCandidate':'D1-20261018-E13A','windowsCommandLineUtf16UnitsIncludingNul':cmdchars,'nestedShellBodiesForSyntaxAudit':nested+[reader+'\n'+collector],'instrumentationParser':pin(B/'tools/processes_reader.sh'),'instrumentationRecordVersion':'E13B_PROCESS_SNAPSHOT_V1','idleMeans':'No active instrumentation in one complete supported snapshot only; not general device idle/resourcesReleased','environmentWaitExit':73,'blockedExits':[21,22],'previousArgv':pin(OLD/'release/metadata'/(stage+'.argv.json'))})
 js(O/(stage+'.argv.json'),new);clients.append(new)
expected=json.loads((OLD/'release/metadata/expected-baseline.json').read_text());expected['instrumentationEvidence']={'route':'unfiltered dumpsys activity processes','header':'ACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)','requiredAnchors':['  All known processes:','  OOM levels:','  mForceBackgroundCheck=true|false as last nonblank source line','exactly one original E13B_DUMPSYS_EXIT=0 marker'],'activeList':'Entire block from Active instrumentation header through before OOM levels, including all entries/continuations/unindented flags; no package filter','idle':'Header+all-known+OOM+final-tail+original-exit all complete, zero active header/items/hints; never empty grep','unknown':'BLOCKED, including diagnostics even command exit0, malformed/missing/over-limit fields','active':'ENVIRONMENT_WAIT, client exit73 after complete record; stop before deployment/testing, no auto extra query','outputRecordCap':4096,'internalInputBounds':{'bytes':524288,'lines':8192,'lineBytes':4096,'activeBlockBytes':3000},'accounting':'Internal on-device metadata scan is not retained as PC text; original PC response/2MiB budget does not increase. Bounds violations block; no truncation-as-success.'}
js(O/'expected-baseline.json',expected)
manifest={'status':'E13B_METADATA_OVERLAY_REVIEW_ONLY','baseProductCandidate':'D1-20261018-E13A','productVersion':17,'acceptedSourceVersion':15,'baseMetadataManifest':pin(OLD/'release/metadata/three-client-manifest.json'),'clients':clients,'totalOriginalClients':3,'totalTextUpperBound':196608,'budgetPcTotal':48,'budgetTextTotal':2097152,'recordBoundsUnchanged':[x['recordOutputUpperBound'] for x in clients],'otherRecordFilterAdjustment':'Remove unproved awk dependency: same requested user/ps/package fields via shell builtins or standard sed. No added query/client/field budget.','actualScope':None,'deviceCalls':0}
js(O/'three-client-manifest.json',manifest)
baseBinding=OLD/'release/candidate-binding.json';basePlan=OLD/'release/device-plan.json'
js(B/'release/overlay-binding.json',{'status':'DRAFT_METADATA_ONLY_NOT_APPROVAL','baseCandidateBinding':pin(baseBinding),'baseDevicePlan':pin(basePlan),'baseArtifacts':json.loads(baseBinding.read_text())['targetApks']+[json.loads(baseBinding.read_text())['hostJar']],'metadataManifest':pin(O/'three-client-manifest.json'),'productChanges':False,'APK_JAR_nativeBuilds':0,'version':17,'acceptedSourceVersion':15,'scopeDraftsChanged':False,'actualScope':None,'actualOnce':None})
js(B/'release/state-collector-fragment.json',{'definition':reader+'\n'+collector,'query':'dumpsys activity processes','queryCountPerClient':1,'noUnprovedAwkDependency':True,'sourceReader':pin(B/'tools/processes_reader.sh')})
print(json.dumps({'clients':3,'recordBounds':[x['recordOutputUpperBound'] for x in clients],'commandLineUnits':[x['windowsCommandLineUtf16UnitsIncludingNul'] for x in clients],'baseVersion':17,'builds':0}))
