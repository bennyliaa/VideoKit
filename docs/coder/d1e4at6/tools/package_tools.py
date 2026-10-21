"""Inspect/freeze or external-hash READ-ONLY verify. Never imports transfer runners or starts processes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import ast
import hashlib
import io
import json
import os
import stat
import zipfile

ROOT=Path(__file__).resolve().parents[4]
BASE='docs/coder/d1e4at6'
CANDIDATE='D1-20261017-E4A-T6'
DOCS=['docs/coder/D1_E4A_T6_DELIVERY_V1.0.md','docs/coder/D1_E4A_T6_BINARY_TRANSFER_PLAN_V1.0.md']
SEAL=BASE+'/evidence/serial-freeze.json'
MANIFEST=BASE+'/evidence/source-manifest.json'
ZIP=BASE+'/artifacts/'+CANDIDATE+'-source.zip'
PRODUCT_SHA='a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d'
def require(value,message):
    if not value:raise ValueError(message)
def canonical(value):return (json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode('utf-8')
def sha(raw):return hashlib.sha256(raw).hexdigest()
class Reader:
    def __init__(self):self.cache={};self.bytes=0;self.logical=0
    def data(self,name):
        require(isinstance(name,str) and '\\' not in name and ':' not in name and not name.startswith('/') and '..' not in Path(name).parts,'relative package path')
        if name not in self.cache:
            p=ROOT/name;require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(ROOT),'file role: '+name)
            for ancestor in [p,*p.parents]:
                if ancestor==ROOT.parent:break
                require(not getattr(ancestor.stat(),'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400),'reparse path')
            require(p.stat().st_size<=8*1048576,'single file budget')
            data=p.read_bytes();require(len(data)==p.stat().st_size,'changed read');self.bytes+=len(data);require(self.bytes<=96*1048576,'physical read budget');self.cache[name]=data
        return self.cache[name]
    def row(self,name):raw=self.data(name);return dict(path=name,bytes=len(raw),sha256=sha(raw))
    def match(self,row):require(self.row(row['path'])=={key:row[key] for key in ('path','bytes','sha256')},'identity mismatch: '+row['path'])
    def json(self,name):return json.loads(self.data(name).decode('utf-8-sig'))
    def usage(self):return dict(physicalBytesRead=self.bytes,logicalZipBytesRead=self.logical,fileReads=len(self.cache),realMediaBytesRead=0,adbCalls=0,processStarts=0)
def sources():
    names=[]
    for directory,folders,files in os.walk(ROOT/BASE,followlinks=False):
        folders[:]=sorted(f for f in folders if f not in {'artifacts','__pycache__','.git'})
        for filename in sorted(files):
            p=Path(directory)/filename;name=p.relative_to(ROOT).as_posix()
            if name in {SEAL,MANIFEST} or filename.endswith('.pyc'):continue
            require(filename not in {'local.properties','.env'} and p.suffix.lower() not in {'.jks','.keystore','.key','.pem','.p12'},'private file')
            names.append(name)
    names+=DOCS;require(len(names)==len(set(names)) and len(names)<=512,'exact finite source set');return sorted(names)
def facts(reader):
    checks=reader.json(BASE+'/evidence/local-check-results.json');require(checks['status']=='PASS' and checks['scope']=='T6_SERIAL_PARENT_PROBE_LOCAL_ONLY' and checks['attempt']=='main-001','one finite serial batch')
    require(checks['assertions']==len(checks['checks']) and all(c['passed'] for c in checks['checks']),'all final checks')
    for row in checks['inputs']:reader.match(row)
    attempt=reader.json(BASE+'/evidence/check-attempt.json')
    for row in attempt['inputs']:reader.match(row)
    end=reader.json(BASE+'/evidence/check-attempt-result.json');log=reader.data(BASE+'/evidence/checks.log')
    require(end['status']=='PASS' and end['exitCode']==0 and end['logBytes']==len(log) and end['logSha256']==sha(log),'original batch result and log')
    require(checks['actualLocalProcessCalls']==len(checks['records'])==14 and all(r['ownership']=='RETURNED' and r['originalExitObserved'] for r in checks['records']),'actual original local owners returned')
    require(all(checks[k]==0 for k in ['adbCalls','deviceRuns','realMediaStat','realMediaBytesRead','gradleRuns','retainedLocalOwners','stressAttempts']) and checks['historicalSuitesRepeated'] is False,'local scope no stress or history suite')
    require([c['case'] for c in checks['realShellCases']]==['normal','printf-nonzero','decoder-nonzero','od-nonzero','truncated-file','wrong-hex'],'real shell finite endpoint cases')
    for case in checks['realShellCases']:
        require(len(case['states'])<=2 and sum(r['bytes'] for r in case['states'])<=4096,'bounded exact state files')
    refs=reader.json(BASE+'/evidence/reference-map.json')
    for row in refs['files']:
        reader.match(dict(path=row['destination'],bytes=row['bytes'],sha256=row['sha256']));require(reader.data(row['source'])==reader.data(row['destination']),'old reference unchanged')
    oldraw=reader.data(BASE+'/reference/T5-freeze.json');require(sha(oldraw)=='425c53957f6733eda7c23d3cbb81251c31ddd20c3ab4da5a87187ff799291363','T5 external seal');old=reader.json(BASE+'/reference/T5-freeze.json')
    for row in refs['inheritedFiles']:
        actual=reader.row(row['destination']);original=next(r for r in old['immutable'] if r['path']==row['source'])
        require(actual['sha256']==row['sha256']==original['sha256'] and actual['bytes']==original['bytes'] and reader.data(row['source'])==reader.data(row['destination']),'exact inherited stream owner response and future plan')
    require(sha(reader.data(BASE+'/tools/exact_process.py'))=='f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d' and sha(reader.data(BASE+'/reference/product-freeze.json'))==PRODUCT_SHA,'strong close and product unchanged')
    before=ast.parse(reader.data(BASE+'/reference/T5-private_commands.py').decode('utf-8').replace('T5','T6'));after=ast.parse(reader.data(BASE+'/tools/private_commands.py').decode('utf-8'))
    names=['argv','context','context_script','processes_script','mkdir_script','receiver_script','proof_script','parse_line','one','receiver_observation','parse_receiver','parse_proof','check_processes']
    for name in names:
        oldfn=next(n for n in before.body if isinstance(n,ast.FunctionDef) and n.name==name);newfn=next(n for n in after.body if isinstance(n,ast.FunctionDef) and n.name==name)
        require(ast.dump(oldfn)==ast.dump(newfn),'unchanged receiver/proof logic: '+name)
    interleaved=reader.data(BASE+'/reference/T5P-interleaved-stdout.txt');require(len(interleaved)==286 and sha(interleaved)=='f15424ea4759dc3e299308d50f8da8ebf3a48d0e79169ee65525122a2ad7a8d3','real original interleaved bytes')
    p=reader.json(BASE+'/tools/diagnostic-plan.json');require(p['executionAuthorized'] is False and p['batch']=='D1-E4A-T6P-TABLET-20261017' and p['rawBytes']==256 and p['encodedBytes']==344 and p['metadataCap']==20 and p['producerCap']==1 and p['perCommandSeconds']==15 and p['cleanupSeconds']==2 and p['logBytes']==1048576 and p['probeStateFilesPlanned']==2 and p['probeStateBytesPlanned']==5 and p['probeStateFileCap']==4 and p['probeStateBytesCap']==4096,'new exact proposal')
    require(reader.data(BASE+'/payload256.bin')==bytes(range(256)),'own256 payload')
    r=checks['integration'];require(r['status']=='ASCII_STREAM_DECODE_AND_RAW_SHA_VERIFIED_NOT_A_MEDIA_FIXTURE' and r['metadataCommands']==6 and r['producerAttempts']==1 and r['rawSource']['streamBytes']==256 and r['encoding']['actualSubmittedBytes']==344 and r['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED','local integration keeps full raw proof and ownership boundary')
    return dict(localAssertions=checks['assertions'],localAttempts=1,actualLocalProcessCalls=14,retainedLocalOwners=0,stressAttempts=0,adbCalls=0,deviceRuns=0,realMediaBytesRead=0,gradleRuns=0,receiptWriter='UNIQUE_PARENT_AFTER_SEQUENTIAL_COMMAND_RETURNS',probeStateFiles=2,probeStateNormalBytes=5,probeStateFileCap=4,probeStateBytesCap=4096,oldT5P='NOT_ADMITTED_PRODUCER0_NO_DIRECTORY',streamEncoderUnchanged=True,deviceDecoderSupport='UNKNOWN_REQUIRE_SERIAL_PROBE',deviceDiagnostic='NOT_RUN',productFreezeUnchanged=PRODUCT_SHA,D1='NOT_PASSED',M0='NOT_STARTED')

def new(name,raw):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as file:file.write(raw);file.flush();os.fsync(file.fileno())
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['inspect','freeze','verify']);parser.add_argument('--expected-freeze');a=parser.parse_args();reader=Reader()
    if a.mode=='verify':
        require(a.expected_freeze is not None,'external freeze hash required');raw=reader.data(SEAL);require(sha(raw)==a.expected_freeze.lower(),'external freeze mismatch');seal=reader.json(SEAL)
        require(seal['candidate']==CANDIDATE and seal['state']=='FROZEN_LOCAL_ONLY_PENDING_REVIEW','frozen candidate state')
        reader.match(seal['manifest']);reader.match(seal['sourceZip']);manifest=reader.json(MANIFEST);expected={r['path']:r for r in manifest['files']}
        require(len(expected)==len(manifest['files']) and sorted(expected)==sources(),'exact source set changed')
        require({r['path'] for r in seal['immutable']}==set(expected)|{MANIFEST,ZIP},'immutable exact set')
        for row in seal['immutable']:reader.match(row)
        with zipfile.ZipFile(io.BytesIO(reader.data(ZIP))) as archive:
            entries=archive.infolist();require(len(entries)==len(expected) and {e.filename for e in entries}==set(expected),'exact archive membership')
            require(sum(e.file_size for e in entries)<=32*1048576,'logical archive budget')
            for entry in entries:
                require(not entry.flag_bits&1 and not stat.S_ISLNK(entry.external_attr>>16),'archive role')
                data=archive.read(entry);reader.logical+=len(data);row=expected[entry.filename];require(len(data)==row['bytes'] and sha(data)==row['sha256'],'archive member identity')
        require(facts(reader)==seal['facts'],'semantic facts changed');print(canonical(dict(candidate=CANDIDATE,integrity='PASS',readOnly=True,freezeSha256=sha(raw),sourceFiles=len(expected),immutableFiles=len(seal['immutable']),sourceZip=seal['sourceZip'],facts=seal['facts'],readUsage=reader.usage())).decode());return
    require(not (ROOT/SEAL).exists() and not (ROOT/MANIFEST).exists() and not (ROOT/ZIP).exists(),'freeze or partial already exists; never overwrite')
    rows=[reader.row(name) for name in sources()];require(sum(r['bytes'] for r in rows)<=32*1048576,'source budget');summary=facts(reader)
    if a.mode=='inspect':print(canonical(dict(candidate=CANDIDATE,mode='INSPECT',sourceFiles=len(rows),sourceBytes=sum(r['bytes'] for r in rows),facts=summary,readUsage=reader.usage())).decode());return
    manifest=canonical(dict(schema=1,candidate=CANDIDATE,files=rows,scope='Own binary transfer utility, fake data/process evidence and source references; no real media, APK or device run'))
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for row in rows:
            info=zipfile.ZipInfo(row['path'],(2026,10,17,0,0,0));info.external_attr=0o100644<<16;archive.writestr(info,reader.data(row['path']),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    zipped=buf.getvalue();require(len(zipped)<=8*1048576,'archive physical bound');new(MANIFEST,manifest);new(ZIP,zipped)
    m=dict(path=MANIFEST,bytes=len(manifest),sha256=sha(manifest));z=dict(path=ZIP,bytes=len(zipped),sha256=sha(zipped))
    seal=canonical(dict(schema=1,candidate=CANDIDATE,state='FROZEN_LOCAL_ONLY_PENDING_REVIEW',frozenAtUtc=datetime.now(timezone.utc).isoformat(),manifest=m,sourceZip=z,immutable=rows+[m,z],facts=summary))
    new(SEAL,seal);print(canonical(dict(candidate=CANDIDATE,freezeSha256=sha(seal),sourceFiles=len(rows),immutableFiles=len(rows)+2,sourceZip=z,facts=summary,readUsage=reader.usage())).decode())
if __name__=='__main__':main()
