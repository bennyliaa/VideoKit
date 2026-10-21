"""Inspect/freeze or external-hash READ-ONLY verify. Never imports transfer runners or starts processes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import io
import json
import os
import stat
import zipfile

ROOT=Path(__file__).resolve().parents[4]
BASE='docs/coder/d1e4at3'
CANDIDATE='D1-20261017-E4A-T3'
DOCS=['docs/coder/D1_E4A_T3_DELIVERY_V1.0.md','docs/coder/D1_E4A_T3_DIAGNOSTIC_PLAN_V1.0.md']
SEAL=BASE+'/evidence/features-freeze.json'
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
    checks=reader.json(BASE+'/evidence/local-check-results.json')
    require(checks['status']=='PASS' and checks['scope']=='OFFLINE_T3_PRODUCTION_PARSER_ONLY' and checks['attempt']=='main-001','one offline final batch')
    require(checks['assertions']==len(checks['checks']) and all(r['passed'] for r in checks['checks']),'all final assertions')
    for row in checks['inputs']:reader.match(row)
    reader.match(checks['original'])
    attempt=reader.json(BASE+'/evidence/attempt-result.json');log=reader.data(BASE+'/evidence/checks.log')
    require(attempt['status']=='PASS' and attempt['attempt']=='main-001' and len(log)==attempt['logBytes'] and sha(log)==attempt['logSha256'],'original batch log binding')
    require(all(checks[k]==0 for k in ['adbCalls','processStarts','deviceRuns','realMediaBytesRead','gradleRuns','retainedLocalOwners','sourcePayloadBytesRead']),'offline only')
    require(all(checks[k] is False for k in ['legacy43Repeated','legacy63Repeated','legacy72Repeated']),'no historical suite repeated')
    refs=reader.json(BASE+'/evidence/reference-map.json')
    for row in refs['files']:
        reader.match(dict(path=row['destination'],bytes=row['bytes'],sha256=row['sha256']))
        require(reader.data(row['source'])==reader.data(row['destination']),'immutable reference changed')
    original=reader.data(BASE+'/reference/features-original-stdout.txt')
    require(len(original)==220 and sha(original)=='05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce','original tester feature bytes')
    record=reader.json(BASE+'/reference/features-record.json')
    require(record['stdout']['bytes']==220 and record['stdout']['sha256']==sha(original) and bytes.fromhex(record['stdout']['prefixHex'])==original and not record['stdout']['prefixTruncated'],'complete original output binding')
    require(sha(reader.data(BASE+'/reference/T2-freeze.json'))=='ce571e95cd294a46b2f852e2d07c7f91126d2b388eb6b27ddcc589e91010b09a','old T2 external seal')
    old=reader.json(BASE+'/reference/T2-freeze.json');container=reader.data(BASE+'/reference/T2-source.zip');manifest=reader.data(BASE+'/reference/T2-source-manifest.json')
    require(sha(container)==old['sourceZip']['sha256']=='9d4d2f6a65b93876fedf6df0257704beecb73cfc6d81928e349ed9a32237ac54' and sha(manifest)==old['manifest']['sha256'],'complete original T2 source')
    with zipfile.ZipFile(io.BytesIO(container)) as archive:
        require(set(archive.namelist())=={r['path'] for r in json.loads(manifest.decode('utf-8'))['files']},'original source exact set')
        pump=archive.read('docs/coder/d1e4at2/tools/exact_process.py');reader.logical+=len(pump)
        require(pump==reader.data(BASE+'/tools/exact_process.py') and sha(pump)=='f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d','T1 owner unchanged')
        remote=archive.read('docs/coder/d1e4at2/tools/remote_command.py');reader.logical+=len(remote)
        expected=remote.decode('utf-8').replace('files/e4_diag_T2P_TABLET_20261017_once','files/e4_diag_T3P_TABLET_20261017_once').replace('E4T2P_TABLET_20261017_ONCE','E4T3P_TABLET_20261017_ONCE')
        require(reader.data(BASE+'/tools/remote_command.py').decode('utf-8').replace('\r\n','\n')==expected.replace('\r\n','\n'),'remaining remote builders and marker parsers unchanged except new identity')
    require(sha(reader.data(BASE+'/reference/e4a-freeze.json'))==PRODUCT_SHA,'product unchanged')
    plan=reader.json(BASE+'/tools/diagnostic-plan.json')
    require(plan['executionAuthorized'] is False and plan['batch']=='D1-E4A-T3P-TABLET-20261017' and plan['payloadBytes']==256 and plan['producerAttemptsCap']==1 and plan['metadataCommandsCap']==20 and plan['perCommandSeconds']==15 and plan['cleanupSeconds']==2 and plan['logTotalBytes']==1048576,'new exact unauthorized plan')
    require(reader.data(BASE+'/payload256.bin')==bytes(range(256)),'fixed payload')
    integrations=checks['integrations'];require(len(integrations)==8 and all(r['result']['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED' for r in integrations),'old ownership remains unknown')
    final=integrations[-1]['result'];require(final['status']=='SYNTHETIC_DIAGNOSTIC_VERIFIED_NOT_A_MEDIA_FIXTURE' and final['metadataCommands']==6 and final['producerAttempts']==1,'other formats synthetic contract only')
    return dict(localAssertions=checks['assertions'],localAttempts=1,actualChildProcessStarts=0,adbCalls=0,deviceRuns=0,realMediaBytesRead=0,gradleRuns=0,retainedLocalOwners=0,originalFeatureBytes=220,originalFeatureSha256=sha(original),realOriginalRegression='PASS_OFFLINE',otherCommandFormats='SYNTHETIC_ONLY_DEVICE_UNKNOWN',oldT2P='NOT_ADMITTED_METADATA1_PRODUCER0_NO_NEW_FILES',deviceDiagnostic='NOT_RUN',payloadBytes=256,productFreezeUnchanged=PRODUCT_SHA,D1='NOT_PASSED',M0='NOT_STARTED')

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
