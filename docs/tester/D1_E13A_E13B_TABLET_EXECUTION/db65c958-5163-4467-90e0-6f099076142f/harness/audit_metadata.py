"""Independent parsing of already returned original metadata bytes only. Never dispatches."""
from pathlib import Path
import base64,hashlib,json,re,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];R=B.parents[3]
ident=sys.argv[1];stage=sys.argv[2];C=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def ck(n,v,d=None):C.append(dict(name=n,passed=bool(v),detail=d))
m=load(R/'docs/coder/d1e13b/release/metadata'/f'{stage}.argv.json');expected=load(R/'docs/coder/d1e13b/release/metadata/expected-baseline.json')
receipt=load(B/'evidence'/f'{ident}-receipt.json');intent=load(B/'evidence'/f'{ident}-intent.json')
raw=(B/'evidence'/f'{ident}-stdout.txt').read_bytes();err=(B/'evidence'/f'{ident}-stderr.txt').read_bytes()
ck('exact reviewed original argv',intent['argv']==m['argv'])
ck('raw stdout hash',len(raw)==receipt['stdoutBytes'] and sha(raw)==receipt['stdoutSha256'])
ck('raw stderr hash',len(err)==receipt['stderrBytes'] and sha(err)==receipt['stderrSha256'])
ck('known original client and readers returned',receipt['originalProcessReturned'] and receipt['bothOriginalPipesReturned'] and receipt['stdinClosed'])
ck('original exit0 and bounded output',receipt['exitCode']==0 and len(raw)+len(err)<=65536 and not receipt['overflow'] and not receipt['responseTimedOut'])
text=raw.decode('utf-8',errors='strict').replace('\r\n','\n');head=f'E13A_METADATA\t{stage}\tD1-20261018-E13A\n';ck('exact metadata header',text.startswith(head))
at=len(head);fields={}
for rec in m['records']:
 label=rec['label'];begin='BEGIN\t'+label+'\n';end='\nEND\t'+label+'\n'
 if not text.startswith(begin,at):raise ValueError('MISSING_OR_OUT_OF_ORDER_RECORD '+label)
 stop=text.find(end,at+len(begin))
 if stop<0:raise ValueError('TRUNCATED_RECORD '+label)
 value=text[at+len(begin):stop];fields[label]=value;at=stop+len(end)
 ck('record cap '+label,len(value.encode('utf-8'))<=rec['maxBytes'])
ck('complete metadata end no diagnostic suffix',text[at:]==f'E13A_METADATA_END\t{stage}\n')
ck('device identity',fields['SERIAL']=='HA1Q6WXR' and fields['MODEL']=='TB138FC' and fields['API']=='31' and 'arm64-v8a' in fields['ABI'].split(',') and fields['CURRENT_USER']=='0')
ck('user0 unlocked','UserInfo{0:' in fields['USER0_STATE'] and 'State: RUNNING_UNLOCKED' in fields['USER0_STATE'])
snapshot=fields['INSTRUMENTATION'].splitlines()
ck('supported complete idle snapshot',len(snapshot)==8 and snapshot[0]=='E13B_PROCESS_SNAPSHOT_V1 state=IDLE' and snapshot[1]=='SOURCE_HEADER ACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)' and snapshot[2]=='SOURCE_ANCHORS all_known=1 oom_levels=1 final_tail=1 command_exit=0' and re.fullmatch(r'SOURCE_SCAN bytes=[0-9]+ lines=[0-9]+ active_entries=0',snapshot[3]) and re.fullmatch(r'SOURCE_TAIL  mForceBackgroundCheck=(true|false)',snapshot[4]) and snapshot[5:]==['ACTIVE_BLOCK_BEGIN','ACTIVE_BLOCK_END','E13B_PROCESS_SNAPSHOT_END'])
for name in ['APP_SERVICES','FIXTURE_SERVICES']:ck('no active services '+name,fields[name]=='ACTIVITY MANAGER SERVICES (dumpsys activity services)\n  (nothing)')
if stage in ['M1_PRE_DEPLOY','M2_POST_DEPLOY_PRE_CASE']:ck('no related process before dependent dispatch',len(fields['RELATED_PS'].splitlines())==1 and fields['RELATED_PS'].split()==['PID','PPID','UID','NAME'])
version=15 if stage=='M1_PRE_DEPLOY' else 17
by={a['kind']:a for a in expected['targetApks']};source=expected['sourcePair']
pkgIds={}
for kind,uid in [('app',10221),('test',10222)]+([] if stage=='M1_PRE_DEPLOY' else [('fixture',None)]):
 value=fields['APK_'+kind.upper()].splitlines();wanted=source[kind] if stage=='M1_PRE_DEPLOY' else by[kind]['sha256']
 ck('exact installed APK '+kind,len(value)==2 and value[0].startswith('/data/app/') and value[0].endswith('/base.apk') and value[1].split()==[wanted,value[0]])
 dump=fields['PKG_'+kind.upper()];uids=re.findall(r'^\s*userId=([0-9]+)$',dump,re.M);versions=re.findall(r'^\s*versionCode=([0-9]+)\b',dump,re.M)
 ck('unique package UID/version '+kind,len(uids)==1 and len(versions)==1)
 actual=int(uids[0]);pkgIds[kind]=actual
 ck('exact package UID '+kind,actual==uid if uid is not None else actual>=10000 and actual not in [10221,10222])
 ck('installed enabled nonsuspended '+kind,bool(re.search(r'^\s*User 0:.*installed=true.*hidden=false.*suspended=false.*enabled=0\b',dump,re.M)))
 if kind=='app':ck('exact app version',int(versions[0])==version)
 if kind=='fixture':ck('fixture version1',int(versions[0])==1)
ck('original data identities',fields['DATA_APP']=='10221|6972' and fields['DATA_TEST']=='10222|4741')
if stage=='M1_PRE_DEPLOY':ck('fixture actually absent',fields['FIXTURE_ABSENT']=='')
ledgerInfo=None
if stage!='M2_POST_DEPLOY_PRE_CASE':
 for path,want in expected['fixedStat'].items():ck('original stat '+path,fields['STAT:'+path]==want)
 for control in expected['fixedControlPins']:
  value=base64.b64decode(''.join(fields['CONTROL:'+control['path']].split()),validate=True)
  ck('original control '+control['path'],len(value)==control['bytes'] and sha(value)==control['sha256'])
 inv=fields['INVENTORY'].splitlines();ck('exact complete control inventory',inv==expected['inventory'])
 ck('no active operation.pending','files/e4a_output_budget/operation.pending' not in inv)
 ledger=base64.b64decode(''.join(fields['CONTROL:files/e4a_output_budget/ledger.bin'].split()),validate=True)
 ck('2271B accepted full ledger',len(ledger)==2271 and sha(ledger)=='e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649')
 ck('accepted old1011B prefix',sha(ledger[:1011])=='f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba')
 lines=ledger.decode('ascii').splitlines(keepends=True);chain=sha(lines[0].encode('ascii'));tasks={};rs=ss=0
 for line in lines[1:]:
  payload,digest=line.rstrip('\n').rsplit(' ',1);ck('ledger chain row',sha((chain+' '+payload).encode('ascii'))==digest);chain=digest;p=payload.split(' ')
  if p[0]=='R':ck('unique reservation',p[1] not in tasks);tasks[p[1]]=None;rs+=1
  elif p[0]=='S':ck('unique settlement',p[1] in tasks and tasks[p[1]] is None and p[2] in ['READY','ABORTED']);tasks[p[1]]=int(p[3]);ss+=1
  else:ck('known ledger row',False)
 consumed=sum(v for v in tasks.values() if v is not None);reserved=sum(2097152 for v in tasks.values() if v is None)
 ledgerInfo=dict(bytes=len(ledger),sha256=sha(ledger),consumed=consumed,reserved=reserved,recordsR=rs,recordsS=ss,lastChain=chain)
 ck('actual214483 7R7S zeroreserved',consumed==214483 and reserved==0 and rs==ss==7)
result=dict(status='PASS_CURRENT_DEVICE_METADATA' if all(c['passed'] for c in C) else 'BLOCKED_CURRENT_DEVICE_METADATA',atUtc=datetime.now(timezone.utc).isoformat(),stage=stage,originalId=ident,checks=C,failed=[c for c in C if not c['passed']],device=dict(serial=fields['SERIAL'],model=fields['MODEL'],api=int(fields['API']),user=int(fields['CURRENT_USER']),appVersion=version,packageUids=pkgIds),ledger=ledgerInfo,deviceCallsByAudit=0)
(B/'evidence'/f'{ident}-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=result['status'],checkCount=len(C),failed=result['failed'],device=result['device'],ledger=ledgerInfo),ensure_ascii=False))
