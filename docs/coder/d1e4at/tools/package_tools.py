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
BASE='docs/coder/d1e4at'
CANDIDATE='D1-20261017-E4A-T'
DOCS=['docs/coder/D1_E4A_T_DELIVERY_V1.0.md','docs/coder/D1_E4A_T_PRELOAD_PLAN_V1.0.md']
SEAL=BASE+'/evidence/transfer-freeze.json'
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
    checks=reader.json(BASE+'/evidence/local-check-results.json');require(checks['status']=='PASS' and checks['exitCode']==0,'local batch status')
    for row in checks['inputs']:reader.match(row)
    reader.match(checks['log']);reader.match(checks['ownedResults'])
    main=reader.json(BASE+'/evidence/local-check-results-before-repair-001.json')
    require(main['status']=='PASS' and main['kind']=='MAIN' and checks['kind']=='REPAIR' and checks['repairReason'],'preserved main and necessary repair')
    for row in main['inputs']:
        copy=dict(row);copy['path']=BASE+'/evidence/preserved-main-sources/'+Path(row['path']).name;reader.match(copy)
    reader.match(main['log']);reader.match(main['ownedResults'])
    owned=reader.json(checks['ownedResults']['path']);require(owned['status']=='PASS' and owned['assertions']==checks['assertions'] and owned['commands']==len(owned['processes'])<=128 and owned['retainedProcessOwners']==0,'finite actual process evidence')
    require(all(owned.get(k)==0 for k in ['adbCalls','deviceRuns','gradleRuns','realMediaBytesRead']),'local scope violated')
    actual=0;preflight=0
    for record in owned['processes']:
        require(record['ownership']=='RETURNED','unreturned owner')
        if record['originalExitObserved']:
            require(any(arg.endswith('fake_child.py') for arg in record['argv']),'unexpected actual process');actual+=1
        else:
            require(record['firstError']=='SOURCE_PREHASH_MISMATCH','unexpected prelaunch outcome');preflight+=1
    require(actual+preflight==owned['commands'],'process records count')
    for row in reader.json(BASE+'/evidence/reference-map.json')['files']:
        reader.match(dict(path=row['destination'],bytes=row['bytes'],sha256=row['sha256']))
        if row['source']=='docs/coder/d1e4a/evidence/e4a-freeze.json':require(row['sha256']==PRODUCT_SHA,'old product anchor')
        if (ROOT/row['source']).is_file():require(reader.data(row['source'])==reader.data(row['destination']),'original reference changed')
    plan=reader.json(BASE+'/tools/tablet-preload-plan.json');require(plan['executionAuthorized'] is False and len(plan['files'])==2,'future plan not authorized')
    return dict(localAssertions=owned['assertions'],callRecords=owned['commands'],actualOwnedFakeProcesses=actual,sourcePreflightRefusals=preflight,retainedProcessOwners=0,
                adbCalls=0,deviceRuns=0,gradleRuns=0,realMediaBytesRead=0,productFreezeUnchanged=PRODUCT_SHA,transportRootCause='UNKNOWN_NOT_INFERRED_FROM_LOCAL_FAKE_SUCCESS',devicePreload='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')
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
