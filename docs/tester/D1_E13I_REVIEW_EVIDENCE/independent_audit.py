from pathlib import Path
import json,hashlib,zipfile,datetime,re
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1e13i';E=R/'docs/tester/D1_E13I_REVIEW_EVIDENCE';checks=[];seen={}
def raw(p):
 p=Path(p);p=p if p.is_absolute() else R/p;b=p.read_bytes();seen.setdefault(p.as_posix(),hashlib.sha256(b).hexdigest());return b
def obj(p):return json.loads(raw(p).decode('utf-8-sig'))
def ck(n,v):
 checks.append({'id':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
def pin(r):
 b=raw(r['path']);ck('bytes:'+r['path'],len(b)==r['bytes']);ck('sha:'+r['path'],hashlib.sha256(b).hexdigest()==r['sha256'])
sp=B/'evidence/e13i-freeze.json';ck('exact external seal',hashlib.sha256(raw(sp)).hexdigest()=='d18b61928227bff9fb46848b5ae7d6c40a869c7a1976b23f5a72467d05a7ddf6');s=obj(sp)
ck('415 unique rows',len(s['immutableFiles'])==415==len({r['path'] for r in s['immutableFiles']}))
for r in s['immutableFiles']:pin(r)
with zipfile.ZipFile(R/s['archive']['path']) as z:
 members={r['path']:r for r in s['immutableFiles'] if r['path']!=s['archive']['path']};ck('414 exact ZIP members',len(z.namelist())==414==len(set(z.namelist())) and set(z.namelist())==set(members));ck('ZIP CRC',z.testzip() is None)
 for n,r in members.items():
  b=z.read(n);ck('ZIP member:'+n,len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'])
prior=[]
for g in s['priorSeals']:
 pin(g['seal']);old=obj(g['seal']['path'])['immutableFiles'];ck('old count:'+g['seal']['path'],len(old)==g['immutableRowsVerified']);prior.append(len(old))
 for r in old:pin(r)
m=obj(B/'evidence/host-jar-manifest.json');pin(m['jar']);base=obj('docs/coder/d1e13f/evidence/host-jar-manifest.json');pin(base['jar']);new=[]
with zipfile.ZipFile(R/m['jar']['path']) as z,zipfile.ZipFile(R/base['jar']['path']) as old:
 ck('193 exact final classes',len(z.namelist())==193 and set(z.namelist())=={r['entry'] for r in m['classes']})
 for r in m['classes']:
  pin(r['source']);b=z.read(r['entry']);ck('JAR member:'+r['entry'],len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'])
  if r['origin']=='UNCHANGED_REVIEWED_E13F':ck('old class exact:'+r['entry'],b==old.read(r['entry']))
  else:new.append(r['entry']);ck('actual tested new production bytes:'+r['entry'],b==raw(B/'evidence/actual-tested-production-class-bytes'/r['entry']))
 ck('183 old 10 new bijection',len(new)==10 and set(z.namelist())-set(old.namelist())==set(new))
 ck('no fixtures in final JAR',not any(any(p in n for p in ['ICheck','IFixtures','IAdditionalCheck','HCheck']) for n in z.namelist()))
proto=obj(B/'evidence/protocol-source-manifest.json');pin(proto['metadata']);ck('ten exact official files',len(proto['files'])==10)
for r in proto['files']:pin(r);ck('one pinned official commit:'+r['repositoryPath'],r['commit']==proto['commit']=='1cf2f017d312f73b3dc53bda85ef2610e35a80e9')
for r in obj(B/'evidence/protocol-excerpt-manifest.json')['excerpts']:
 pin(r['source']);pin(r['excerpt']);lines=raw(r['source']['path']).decode().splitlines();expected='\n'.join(lines[r['firstLine']-1:r['lastLine']])+'\n';ck('excerpt from whole source:'+r['excerpt']['path'],raw(r['excerpt']['path']).decode().replace('\r\n','\n')==expected)
script=obj(B/'evidence/script-binding.json');pin(script['script']);pin(script['old']);marker=b'# Same original local context';ck('owner body exact actual bytes',raw(script['script']['path']).split(marker,1)[1]==raw(script['old']['path']).split(marker,1)[1])
java=raw(B/'tools/E13IReadOnly.java').decode();ps=raw(script['script']['path']).decode();ck('Java production release absent','APPROVED_REQUEST_SHA="ABSENT"' in java);ck('PS before context gate',ps.index("$approvedRequestSha='ABSENT'")<ps.index('# Same original local context'))
modes=obj(B/'evidence/host-001/results.json')['modes'];ck('31 peer modes',len(modes)==31)
commands=0
for n in ['compile']+modes+['describe','public-reject']:
 r=obj(B/'evidence/host-001'/(n+'.exit.json'));ck('host actual exit:'+n,r['exitCode']==(1 if n=='public-reject' else 0) and r['naturalReturn'] and r['parentOriginalWaitReturned'] and r['parentRecordingFilesCloseReturned']);raw(B/'evidence/host-001'/(n+'.stdout.txt'));raw(B/'evidence/host-001'/(n+'.stderr.txt'));commands+=1
for n in ['test-probe-compile','additional-gates','parent-custody','observer-parse','correct-unissued','wrong-role']:
 r=obj(B/'evidence/supplement-002'/(n+'.exit.json'));ck('supplement actual exit:'+n,r['exitCode']==(1 if n in ['correct-unissued','wrong-role'] else 0) and r['naturalReturn']);raw(B/'evidence/supplement-002'/(n+'.stdout.txt'));raw(B/'evidence/supplement-002'/(n+'.stderr.txt'));commands+=1
parent=obj(B/'evidence/supplement-002/parent-custody.exit.json');ck('parent timeout qualifier not upgraded',parent['qualificationPreserved'] is False and parent['parentOriginalWaitReturned'] and parent['parentRecordingFilesCloseReturned'])
fact=raw(B/'evidence/host-001/WIRE_OVER/final-owner-facts.txt').decode();values={k:int(v) for k,v in re.findall(r'(chargedWire|incomingWire|intendedTx|retainedWire)=(\d+)',fact)}
ck('existing evidence actual exceeds retention reservation',values['chargedWire']==values['incomingWire']+values['intendedTx'] and values['chargedWire']>70656 and values['retainedWire']<=70656)
snap=[{'path':p,'sha256':h} for p,h in sorted(seen.items())];(E/'reviewed-input-snapshot.json').write_text(json.dumps(snap,indent=2),'utf-8')
result={'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_PACKAGE_AND_ORIGINAL_EVIDENCE_INTEGRITY_NOT_RELEASE_ACCEPTANCE','checkCount':len(checks),'checks':checks,'uniqueFrozenFilesRead':len(seen),'priorManifestRows':prior,'originalCommandReceipts':commands,'oldClasses':183,'newClasses':10,'wireOverExistingFacts':values,'candidateProductionJavaExecutions':0,'candidateFullSuiteExecutions':0,'testerExtractedHarnessASTProbes':1,'candidateCompilations':0,'sdkExecutions':0,'networkConnections':0,'oldHandleQueries':0}
(E/'independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
