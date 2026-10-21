"""Frozen files and existing records only, no imports or reruns of production functions."""
from pathlib import Path
import json,hashlib,zipfile,io,ast
R=Path(__file__).resolve().parents[3];B=R/'docs/coder/d1e4at6';E=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
sraw=(B/'evidence/serial-freeze.json').read_bytes();assert sha(sraw)=='861d2e179c66801f80353d79c6c2420a10f5748dfdd090db991a95e3ac0d6f37';s=json.loads(sraw)
m=json.loads((R/s['manifest']['path']).read_bytes());assert len(m['files'])==52 and len(s['immutable'])==54
for row in s['immutable']:
    p=R/row['path'];b=p.read_bytes();assert not p.is_symlink() and len(b)==row['bytes'] and sha(b)==row['sha256']
z=(R/s['sourceZip']['path']).read_bytes();assert sha(z)=='73bef2bc282e4474e53f9d867bc317d8ee5f6928c64ed7418a706b557b8be681'
with zipfile.ZipFile(io.BytesIO(z)) as a:
    assert len(a.infolist())==52 and set(a.namelist())=={r['path'] for r in m['files']}
    for row in m['files']:assert sha(a.read(row['path']))==row['sha256']
for name in ('exact_process.py','command_response.py','stream_base64.py','future-media-plan.json'):
    assert (B/'tools'/name).read_bytes()==(R/'docs/coder/d1e4at5/tools'/name).read_bytes()
old=ast.parse((B/'reference/T5-private_commands.py').read_text().replace('T5','T6'));new=ast.parse((B/'tools/private_commands.py').read_text())
names=['argv','context','context_script','processes_script','mkdir_script','receiver_script','proof_script','parse_line','one','receiver_observation','parse_receiver','parse_proof','check_processes']
for name in names:assert ast.dump(next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name==name))==ast.dump(next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name==name))
c=json.loads((B/'evidence/local-check-results.json').read_bytes());assert c['assertions']==len(c['checks'])==45 and all(x['passed'] for x in c['checks']) and len(c['records'])==14
def output(r):
    assert r['ownership']=='RETURNED' and r['originalExitObserved'] and not r['creationUnknown'] and r['stdinCloseError'] is None
    assert all(r[k] for k in ('stdinCloseReturned','sourceCloseReturned','writerReturned','flushReturned'))
    for stream in ('stdout','stderr'):
        d=r[stream];raw=bytes.fromhex(d['prefixHex']);assert not d['prefixTruncated'] and len(raw)==d['bytes'] and sha(raw)==d['sha256'] and d['closeReturned'] and d['error'] is None
    return bytes.fromhex(r['stdout']['prefixHex'])
for r in c['records']:output(r)
cases=[]
for case in c['realShellCases']:
    name=case['case'];r=c['records'][case['recordIndex']];raw=output(r);assert sha(raw)==case['stdoutSha256']
    lines=raw.decode().splitlines();assert len(lines)==4
    for row in case['states']:
        p=B/'evidence/local-main-001'/name/'files/e4_diag_T6P_TABLET_20261017_once'/row['name'];b=p.read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256']
    assert len(case['states'])<=2 and sum(x['bytes'] for x in case['states'])<=4096
    cases.append(dict(case=name,originalExit=r['originalExitCode'],endpointLines=lines[:3],finalLine=lines[3],states=case['states']))
normal=c['integration'];assert normal['status']=='ASCII_STREAM_DECODE_AND_RAW_SHA_VERIFIED_NOT_A_MEDIA_FIXTURE' and normal['metadataCommands']==6 and normal['producerAttempts']==1 and normal['retainedLocalOwners']==0
scope=B/'evidence/local-main-001/integration/private'
assert (scope/'payload256.bin').read_bytes()==bytes(range(256)) and (scope/'probe.ascii').read_bytes()==b'AA==' and (scope/'probe.raw').read_bytes()==b'\0'
inter=(B/'reference/T5P-interleaved-stdout.txt').read_bytes();assert len(inter)==286 and sha(inter)=='f15424ea4759dc3e299308d50f8da8ebf3a48d0e79169ee65525122a2ad7a8d3'
assert inter==(R/'docs/tester/D1_E4A_T5P_EVIDENCE/probe-original-stdout.txt').read_bytes()
out=dict(status='PASS',scope='FROZEN_IDENTITIES_AND_EXISTING_RECORDS_ONLY',sourceFiles=52,immutableFiles=54,zipBytes=len(z),assertionsRecorded=45,originalLocalRecords=14,realShellCases=cases,inheritedLogicFunctions=names,inheritedModulesByteIdentical=True,integrationRaw=256,integrationEncoded=344,normalStateFiles=2,normalStateBytes=5,oldInterleavedOriginalPreserved=True,retainedLocalOwners=0,inFlight=[],testerAdbCalls=0,testerFakeOrProbeReruns=0,testerMediaStatReadHash=0,testerGradle=0)
(E/'identity-and-recorded-evidence-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
