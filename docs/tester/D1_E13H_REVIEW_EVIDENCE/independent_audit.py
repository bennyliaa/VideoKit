from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1e13h';E=R/'docs/tester/D1_E13H_REVIEW_EVIDENCE';checks=[];seen={}
def raw(p):
 p=Path(p);p=p if p.is_absolute() else R/p;b=p.read_bytes();seen.setdefault(p.as_posix(),hashlib.sha256(b).hexdigest());return b
def obj(p):return json.loads(raw(p).decode('utf-8-sig'))
def ck(n,v):
 checks.append({'id':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
def pin(r):
 b=raw(r['path']);ck('bytes:'+r['path'],len(b)==r['bytes']);ck('sha:'+r['path'],hashlib.sha256(b).hexdigest()==r['sha256'])
sp=B/'evidence/e13h-freeze.json';ck('external seal',hashlib.sha256(raw(sp)).hexdigest()=='befdcfcc5c04722cb138f845a27fe6d434d63fd204c211b39028914cdce2fc9e');s=obj(sp)
ck('181 unique rows',len(s['immutableFiles'])==181==len({r['path'] for r in s['immutableFiles']}))
for r in s['immutableFiles']:pin(r)
with zipfile.ZipFile(R/s['archive']['path']) as z:
 members={r['path']:r for r in s['immutableFiles'] if r['path']!=s['archive']['path']};ck('180 exact ZIP members',len(z.namelist())==180==len(set(z.namelist())) and set(z.namelist())==set(members));ck('ZIP CRC',z.testzip() is None)
 for n,r in members.items():
  b=z.read(n);ck('ZIP member:'+n,len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'])
prior=[]
for group in s['priorSeals']:
 pin(group['seal']);old=obj(group['seal']['path'])['immutableFiles'];ck('old count:'+group['seal']['path'],len(old)==group['immutableRowsVerified']);prior.append(len(old))
 for r in old:pin(r)
m=obj(B/'evidence/host-jar-manifest.json');pin(m['jar'])
base=obj('docs/coder/d1e13f/evidence/host-jar-manifest.json');pin(base['jar'])
new=[]
with zipfile.ZipFile(R/m['jar']['path']) as z,zipfile.ZipFile(R/base['jar']['path']) as old:
 ck('188 exact final JAR members',len(z.namelist())==188 and set(z.namelist())=={r['entry'] for r in m['classes']})
 for r in m['classes']:
  pin(r['source']);b=z.read(r['entry']);ck('JAR member:'+r['entry'],len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'])
  if r['origin']=='BYTE_IDENTICAL_REVIEWED_E13F':ck('old class unchanged:'+r['entry'],b==old.read(r['entry']))
  else:
   new.append(r['entry']);ck('actual compiled new bytes:'+r['entry'],b==raw(B/'evidence/actual-tested-class-bytes'/r['entry']))
 ck('183 old plus five new only',len(old.namelist())==183 and len(new)==5 and set(z.namelist())-set(old.namelist())==set(new))
 ck('HCheck absent',not any('HCheck' in n for n in z.namelist()))
script=obj(B/'evidence/script-binding.json');pin(script['script']);pin(script['reviewedOriginal']);marker=b'# Same original local context'
ck('original owner body exact bytes',raw(script['script']['path']).split(marker,1)[1]==raw(script['reviewedOriginal']['path']).split(marker,1)[1])
java=raw(B/'tools/E13GReadOnly.java').decode();ps=raw(script['script']['path']).decode('utf-8-sig')
ck('direct SDK production disabled','static final boolean DIRECT_ADB_NO_RESTART_PROVEN=false;' in java and not s['productionEnabled'])
ck('Java public rejection before any Chain','if(!DIRECT_ADB_NO_RESTART_PROVEN)throw new IOException' in java)
ck('PS reject before context','throw \'G_PRODUCTION_REJECTED_SERVER_REPLACEMENT_RACE_SDK_PROTOCOL_MAPPING_UNPROVEN\'' in ps and ps.index("throw 'G_PRODUCTION_REJECTED_SERVER_REPLACEMENT_RACE_SDK_PROTOCOL_MAPPING_UNPROVEN'")<ps.index('# Same original local context'))
proto=obj(B/'evidence/protocol-source-and-binary-binding.json');pin(proto['sdkBinary']);ck('source mapping and race unproven',proto['exactSdkBuildToOfficialSourceMapping']=='UNPROVEN' and proto['remainingServerReplacementRace'] and not proto['productionEnabled'])
commands=0
for mode in ['compile','SUCCESS','TIMEOUT','POLICY','WRITE_FAILURE']:
 r=obj(B/'evidence/host-001'/(mode+'.exit.json'));ck('original host exit:'+mode,r['exitCode']==0 and r['naturalReturn']);raw(B/'evidence/host-001'/(mode+'.stdout.txt'));raw(B/'evidence/host-001'/(mode+'.stderr.txt'));commands+=1
for mode in ['VERSION_OK','VERSION_BAD','VERSION_TIMEOUT','describe','observer-parse','public-reject','correct-role-disabled','wrong-exe','wrong-serial-argv-role']:
 r=obj(B/'evidence/final-002'/(mode+'.exit.json'));expected=1 if mode in ['public-reject','correct-role-disabled','wrong-exe','wrong-serial-argv-role'] else 0;ck('original final exit:'+mode,r['exitCode']==expected and r['naturalReturn']);raw(B/'evidence/final-002'/(mode+'.stdout.txt'));err=raw(B/'evidence/final-002'/(mode+'.stderr.txt')).decode('utf-8',errors='replace');commands+=1
 if mode=='public-reject':ck('actual Java rejection evidence','G_PRODUCTION_REJECTED_BEFORE_OWNER_OR_NETWORK' in err)
 if mode=='correct-role-disabled':ck('actual PS rejection evidence','G_PRODUCTION_REJECTED_SERVER_REPLACEMENT_RACE' in err)
pending=obj(B/'evidence/host-001/VERSION_OK.pending.json');ck('initial local probe pending retained',pending=={'pid':30384,'killed':False,'originalPending':True})
hist=obj(B/'evidence/local-probe-environment-history.json');ck('no retroactive ACK',hist['naturalExitAck']=='UNPROVEN' and hist['readerCloseAck']=='UNPROVEN' and hist['notOldLostDiagnostic'])
snap=[{'path':p,'sha256':h} for p,h in sorted(seen.items())]
E.mkdir(parents=True,exist_ok=True);(E/'reviewed-input-snapshot.json').write_text(json.dumps(snap,indent=2),'utf-8')
result={'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_PREPARE_ONLY_INTEGRITY_AND_HARD_REFUSAL_EVIDENCE','checkCount':len(checks),'checks':checks,'uniqueFrozenFilesRead':len(seen),'priorManifestRows':prior,'originalCommandReceipts':commands,'baseClasses':183,'newClasses':len(new),'candidateExecutions':0,'candidateCompilations':0,'sdkExecutions':0,'networkConnections':0,'originalHandleQueries':0,'newLocalProbeUnknown':'SEPARATE_NO_ACK'}
(E/'independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
