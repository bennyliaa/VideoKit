from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1e13f';E=R/'docs/tester/D1_E13F_REVIEW_EVIDENCE';checks=[];seen={}
def raw(p):
 p=Path(p);p=p if p.is_absolute() else R/p;b=p.read_bytes();seen.setdefault(p.as_posix(),hashlib.sha256(b).hexdigest());return b
def obj(p):return json.loads(raw(p).decode('utf-8-sig'))
def ck(name,v):
 checks.append({'id':name,'pass':bool(v)})
 if not v:raise AssertionError(name)
def pin(x):
 b=raw(x['path']);ck('length:'+x['path'],len(b)==x['bytes']);ck('sha:'+x['path'],hashlib.sha256(b).hexdigest()==x['sha256'])
seal=B/'evidence/e13f-freeze.json';ck('external E13F seal',hashlib.sha256(raw(seal)).hexdigest()=='7b72f1bade91286b7d99fbba5459777261e905f4317e0daa969042148b5bf38f')
s=obj(seal);rows=s['immutableFiles'];ck('1179 unique rows',len(rows)==1179==len({x['path'] for x in rows}))
for x in rows:pin(x)
with zipfile.ZipFile(R/s['archive']['path']) as z:
 members={x['path']:x for x in rows if x['path']!=s['archive']['path']};ck('1178 exact unique ZIP members',len(z.namelist())==1178==len(set(z.namelist())) and set(z.namelist())==set(members));ck('ZIP CRC',z.testzip() is None)
 for name,x in members.items():
  b=z.read(name);ck('ZIP length/hash:'+name,len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'])
priorcounts=[]
for prior in s['priorSeals']:
 pin(prior['seal']);d=obj(prior['seal']['path']);old=d['immutableFiles'];ck('old row count:'+prior['seal']['path'],len(old)==prior['immutableRowsVerified']);priorcounts.append(len(old))
 for x in old:pin(x)
inputs=obj(B/'evidence/final-build-inputs.json');missing=[]
for x in inputs['files']:
 if Path(x['path']).name=='fixture-signing.p12' and not (R/x['path']).exists():missing.append(x);continue
 pin(x)
ck('142 final build inputs',len(inputs['files'])==142)
derivation=obj(B/'evidence/source-derivation.json')
for x in derivation['files']:
 pin(x['current'])
 if x.get('baseline'):pin(x['baseline'])
 if x.get('relationship')=='BYTE_IDENTICAL':ck('identical source:'+x['current']['path'],x['current']['sha256']==x['baseline']['sha256'])
manifest=obj(B/'evidence/host-jar-manifest.json');pin(manifest['jar'])
with zipfile.ZipFile(R/manifest['jar']['path']) as z:
 ck('183 exact JAR classes',len(z.namelist())==183 and set(z.namelist())=={x['entry'] for x in manifest['classes']})
 for x in manifest['classes']:
  pin(x['source']);b=z.read(x['entry']);ck('JAR member:'+x['entry'],len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']);ck('no test/shadow source:'+x['entry'],'platform-substitutes' not in x['source']['path'] and 'E13FHostCheck' not in x['entry'])
 for x in obj(B/'evidence/tested-final-class-equivalence.json')['members']:
  b=raw(B/'evidence/tested-class-bytes'/x['attempt']/x['entry']);ck('exact prior tested final class:'+x['attempt']+':'+x['entry'],b==z.read(x['entry']) and hashlib.sha256(b).hexdigest()==x['sha256'])
audit=obj(B/'evidence/apk-delivery-final/apk-audit.json');native=obj(B/'evidence/apk-delivery-final/sbom-difference.json')
for apk in audit['apks']:
 pin(apk)
 with zipfile.ZipFile(R/apk['path']) as z:
  dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
  markers={'app':['E13PermissionProbe','E13FinishOwner','E13ReturnEvents','awaitOriginalReturnOrUnknown'],'test':['E13Instrumentation','originalFailure','TestWatcher'],'fixture':['SenderService','E13BindingOwner','ORIGINAL_ACK_WAIT_ENTER']}[apk['kind']]
  for m in markers:ck('DEX production marker:'+apk['kind']+':'+m,m.encode() in dex)
  ck('no JVM check class in DEX:'+apk['kind'],b'E13FAndroidCheck' not in dex and b'E13FHostCheck' not in dex)
  if apk['kind']=='app':
   ck('seven native APK members',len([n for n in z.namelist() if n.endswith('.so') and n.startswith('lib/')])==7)
   for x in native['nativeLibraries']:pin(x);ck('exact native APK:'+x['entry'],z.read(x['entry'])==raw(x['path']))
  else:ck('no native in other APK:'+apk['kind'],not any(n.startswith('lib/') and n.endswith('.so') for n in z.namelist()))
ck('lock unchanged',raw(B/'app/gradle.lockfile')==raw('docs/coder/d1e13a/app/gradle.lockfile'))
ck('35 Maven coordinates',len([l for l in raw(B/'app/gradle.lockfile').decode().splitlines() if l and not l.startswith(('#','empty='))])==35)
ck('fixture no Maven runtime',not [l for l in raw(B/'fixture/gradle.lockfile').decode().splitlines() if l and not l.startswith(('#','empty='))])
plan=obj(B/'release/candidate-binding.json');ck('draft null actual scope/release/once',all(plan[x] is None for x in ['actualScope','actualRelease','actualOnce']));ck('source pin absent',plan['dispositionSourcePin']=='ABSENT' and 'DISPOSITION_SHA="ABSENT"' in raw(B/'tools/E13GuardLocation.java').decode());ck('T07 not run',plan['T07']=='NOT_RUN');ck('51/53 proposal only',plan['status']=='DRAFT_NO_DISPATCH' and plan['budgetProposal']['successOperations']==51 and plan['budgetProposal']['maxOperationsWithOccupation']==53)
build=obj(B/'evidence/build-results.json');ck('one build attempt pass',[x['exitCode'] for x in build['attempts']]==[0])
for x in build['attempts']:
 t=raw(x['log']).decode('utf-8',errors='replace');ck('original Gradle result:'+x['id'],('BUILD SUCCESSFUL' in t) if x['exitCode']==0 else ('AccessDeniedException' in t or 'Script compilation errors' in t))
commands_checked=0
for folder in ['host-007']:
 commands=obj(B/'evidence'/folder/'commands.json')
 for c in commands:
  name=c.get('name',c.get('mode'));p=B/'evidence'/folder/(name+'.exit.json')
  if p.exists():
   exitrec=obj(p);ck('original exit:'+folder+':'+name,exitrec.get('exitCode',exitrec.get('exit'))==0);raw(p.with_name(name+'.stdout.txt'));raw(p.with_name(name+'.stderr.txt'));commands_checked+=1

fixtures=obj(B/'evidence/test-fixture-class-manifest.json')
for x in fixtures['files']:pin(x)
binding=obj(B/'evidence/public-008/class-binding.json')
for x in binding['productionSources']:pin(x)
for group in binding['groups']:
 for x in group['shadowSources']:pin(x)
 pin(group['testSource'])
 folder=B/'evidence/public-008'/group['group']
 receipt=obj(folder/'exit.json')
 ck('public natural exit:'+group['group'],receipt.get('exitCode')==0)
 text=raw(folder/'stdout.txt').decode('utf-8-sig');raw(folder/'stderr.txt')
 ck('public original PASS evidence:'+group['group'],'PASS '+group['group'].split('-')[0] in text)
 ck('no manual true:'+group['group'],'manualTrue=0' in text)
 if 'FAIL_MARKER' in group['group']:ck('failure keeps same responsibility:'+group['group'],'responsibilityRetained=true' in text and 'nextScopeBlocked=true' in text)
 else:ck('combined full chain:'+group['group'],'actualPublicClaimToIsolationToWriterJoinToPcJoinToOneMarkerToNewScope=true' in text)
 commands_checked+=1
orders=raw(B/'evidence/join-orders-009/check.stdout.txt').decode()
for n in range(3):ck('join ordering:'+str(n),'PASS JOIN_ORDER '+str(n) in orders)

snap=[{'path':p,'sha256':v} for p,v in sorted(seen.items())]
(E/'reviewed-input-snapshot.json').write_text(json.dumps(snap,indent=2),'utf-8')
result={'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_DELIVERY_INTEGRITY_NOT_PRODUCT_ACCEPTANCE','checkCount':len(checks),'checks':checks,'uniqueFilesRead':len(seen),'priorManifestCounts':priorcounts,'commandsChecked':commands_checked,'privateSigningInputsOmitted':missing,'candidateSelfChecksExecuted':0,'candidateBuilds':0,'deviceCalls':0,'originalHandleQueries':0}
(E/'independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','privateSigningInputsOmitted']}))
