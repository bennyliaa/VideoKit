"""Generate three exact REVIEW_ONLY direct adb argv/scripts, never execute them."""
from pathlib import Path
import base64,hashlib,json,re,shlex
B=Path(__file__).resolve().parents[1];R=B.parents[2];O=B/'release/metadata';O.mkdir(parents=True,exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):b=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':sha(b)}
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source=R/'docs/tester/D1_E13_REVIEW_EVIDENCE/three-metadata-field-plan.json';plan=json.loads(source.read_text(encoding='utf-8'))
baseline=R/plan['baselineReceipt']['path'];assert pin(baseline)==plan['baselineReceipt']
text=baseline.read_text();inventory=text.split('INVENTORY_BEGIN\n',1)[1].split('\nINVENTORY_END',1)[0].splitlines()
stats={a:b for a,b in re.findall(r'^STAT\t([^\n\t]+)\t([^\n]+)$',text,re.M)}
for row in plan['ledger']['newOutputs']:stats['files/e4a_outputs/'+row['task']+'.mp4']=row['acceptedStat']
assert len(plan['fixedStatPaths'])==34 and len(plan['fixedControlPins'])==18
assert all(p in stats for p in plan['fixedStatPaths'])
control={p:base64.b64decode(''.join(raw.split()),validate=True) for p,raw in re.findall(r'DATA_BEGIN\t([^\n]+)\n(.*?)DATA_END',text,re.S)}
for row in plan['fixedControlPins']:assert len(control[row['path']])==row['bytes'] and sha(control[row['path']])==row['sha256']
apks=json.loads((B/'evidence/apk-delivery/apk-audit.json').read_text())['apks'];by={p['kind']:p for p in apks}
Q=shlex.quote
helper='''set -eu
export LC_ALL=C
emit() {
 label="$1"; max="$2"; shift 2
 if value=$("$@" 2>&1); then :; else printf 'RECORD_ERROR\\t%s\\n' "$label" >&2; exit 21; fi
 size=$(printf '%s' "$value" | wc -c)
 if [ "$size" -gt "$max" ]; then printf 'RECORD_OVERSIZE\\t%s\\n' "$label" >&2; exit 22; fi
 printf 'BEGIN\\t%s\\n%s\\nEND\\t%s\\n' "$label" "$value" "$label"
}
'''
statExpected={p:stats[p] for p in plan['fixedStatPaths']}
js(O/'expected-baseline.json',{'sourceFieldPlan':pin(source),'acceptedRaw':pin(baseline),'fixedStat':statExpected,'fixedControlPins':plan['fixedControlPins'],'inventory':sorted(inventory),'ledger':plan['ledger'],'targetApks':apks,'appVersion':17,'appRole':'ACTIVATION','gateAbi':1,'sourceVersion':15,'sourcePair':{'app':'2f323c16e896b0535e80cccce05bbcf3051224f0add279a51392312083e89f48','test':'e644dce77be6ccb0e7f99d82f2479fc92238aad682bb022bb95835fc015d0bfb'},'sourceData':['10221|6972','10222|4741'],'fixtureUid':'observe >=10000 distinct 10221/10222; never invent expected UID','scope':'REVIEW_ONLY; no actual device observation or scope granted'})
manifests=[]
for stage in ['M1_PRE_DEPLOY','M2_POST_DEPLOY_PRE_CASE','M3_AFTER_SIX']:
 records=[];nested=[];lines=[helper, "printf 'E13A_METADATA\\t"+stage+"\\tD1-20261018-E13A\\n'"]
 def emit(label,cap,args,private=False):
  if args[:2]==['sh','-c']:nested.append(args[2])
  records.append({'label':label,'maxBytes':cap,'private':private});return 'emit '+Q(label)+' '+str(cap)+' '+' '.join(Q(x) for x in args)
 lines += [emit('SERIAL',64,['getprop','ro.serialno']),emit('MODEL',128,['getprop','ro.product.model']),emit('API',16,['getprop','ro.build.version.sdk']),emit('ABI',128,['getprop','ro.product.cpu.abilist']),emit('CURRENT_USER',16,['am','get-current-user'])]
 user="dumpsys user | awk '/UserInfo/ {want=($0 ~ /UserInfo\\{0:/)} want && /UserInfo|State:/ {print}'"
 lines += [emit('USER0_STATE',512,['sh','-c',user]),emit('RELATED_PS',4096,['sh','-c',"ps -A -o PID,PPID,UID,NAME | awk 'NR==1 || $4 ~ /^com[.]videokit[.](app|e13[.]sender)([:.]|$)/ {print}'"]),emit('INSTRUMENTATION',4096,['dumpsys','activity','instrumentation']),emit('APP_SERVICES',4096,['dumpsys','activity','services','com.videokit.app']),emit('FIXTURE_SERVICES',4096,['dumpsys','activity','services','com.videokit.e13.sender'])]
 for kind,pkg in [('app','com.videokit.app'),('test','com.videokit.app.test')]+([] if stage=='M1_PRE_DEPLOY' else [('fixture','com.videokit.e13.sender')]):
  # Only reviewed APKs are hashed. Media files below are stat-only.
  body="p=$(pm path "+pkg+"); case \"$p\" in package:/data/app/*/base.apk) ;; *) exit 23;; esac; p=${p#package:}; case \"$p\" in *'\n'*) exit 24;; esac; printf '%s\\n' \"$p\"; sha256sum \"$p\""
  lines.append(emit('APK_'+kind.upper(),1024,['sh','-c',body]))
  fields="dumpsys package "+pkg+" | awk '/^[ ]*(userId=|versionCode=|User 0:)/ {print}'"
  lines.append(emit('PKG_'+kind.upper(),2048,['sh','-c',fields]))
 lines += [emit('DATA_APP',128,['run-as','com.videokit.app','stat','-c','%u|%i','.']),emit('DATA_TEST',128,['run-as','com.videokit.app.test','stat','-c','%u|%i','.'])]
 if stage=='M1_PRE_DEPLOY':lines.append(emit('FIXTURE_ABSENT',256,['pm','list','packages','com.videokit.e13.sender']))
 if stage!='M2_POST_DEPLOY_PRE_CASE':
  block=[helper]
  for path in plan['fixedStatPaths']:block.append(emit('STAT:'+path,160,['stat','-c','%d|%i|%u|%f|%s|%b',path],True))
  block.append(emit('INVENTORY',8192,['sh','-c','find files/e4a_output_budget files/e4a_outputs -maxdepth 4 -print | sort'],True))
  for row in plan['fixedControlPins']:
   path=row['path'];block.append('[ -f '+Q(path)+' ] && [ ! -L '+Q(path)+' ] || exit 25')
   block.append('[ "$(wc -c < '+Q(path)+')" -eq '+str(row['bytes'])+' ] || exit 26')
   cap=4*((row['bytes']+2)//3);cap+=((cap+75)//76)+1
   block.append(emit('CONTROL:'+path,cap,['base64',path],True))
  nested.append('\n'.join(block));lines.append('run-as com.videokit.app sh -c '+Q('\n'.join(block)))
 lines.append("printf 'E13A_METADATA_END\\t"+stage+"\\n'")
 script='\n'.join(lines)+'\n';file=O/(stage+'.sh');file.write_text(script,encoding='utf-8',newline='\n')
 # Markers count towards the whole record/client allocation; no silent tail/truncation is used.
 bound=sum(r['maxBytes']+len(r['label'])*2+16 for r in records)+256
 assert bound<=65536,(stage,bound)
 argv=['D:/Android/SDK/platform-tools/adb.exe','-s','HA1Q6WXR','shell','sh','-c',Q(script)]
 item={'id':stage,'status':'REVIEW_ONLY_NOT_EXECUTED','script':pin(file),'argv':argv,'nestedShellBodiesForSyntaxAudit':nested,'originalPcClients':1,'extraJavaWrappers':0,'maxCombinedOriginalTextBytes':65536,'recordOutputUpperBound':bound,'originalResponseSeconds':55,'records':records,'mediaPayloadReads':0,'recordTruncationAllowed':False}
 js(O/(stage+'.argv.json'),item);manifests.append(item)
js(O/'three-client-manifest.json',{'sourceFieldPlan':pin(source),'status':'EXACT_ARGV_SCRIPTS_REVIEW_ONLY','clients':manifests,'totalOriginalClients':3,'totalTextUpperBound':196608,'budgetPcTotal':48,'budgetTextTotal':2097152,'controllerDeviceUseEvidenceRequiredBeforeM1':True,'unknownOrOccupied':'STOP/WAIT; no extra polling/client authorised','actualScope':None,'actualDeviceRuns':0})
print(json.dumps({'scripts':3,'records':[len(x['records']) for x in manifests],'worstText':[x['recordOutputUpperBound'] for x in manifests],'originalClients':3,'executed':0}))
