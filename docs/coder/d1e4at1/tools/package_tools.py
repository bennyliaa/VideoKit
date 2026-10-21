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
BASE='docs/coder/d1e4at1'
CANDIDATE='D1-20261017-E4A-T1'
DOCS=['docs/coder/D1_E4A_T1_DELIVERY_V1.0.md','docs/coder/D1_E4A_T1_PRELOAD_PLAN_V1.0.md']
SEAL=BASE+'/evidence/close-freeze.json'
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
    require(checks['status']=='PASS' and checks['scope']=='T1_PRODUCTION_STDIN_CLOSE_AND_ALLOCATION_ONLY' and checks['legacy72Repeated'] is False,'targeted local scope')
    for row in checks['inputs']:reader.match(row)
    cases=checks['cases'];expected={'success_transfer','no_process','no_stdin','throw_before','throw_after','blocked_return'}
    require(len(cases)==6 and {c['case'] for c in cases}==expected,'six exact isolated cases')
    counts=0;children=0;unknown=0
    for case in cases:
        require(case['exitCode']==0,'case interpreter did not exit');reader.match(case['log']);reader.match(case['result']);proof=reader.json(case['result']['path'])
        require(proof['status']=='PASS' and proof['assertions']==case['assertions'] and proof['registryManuallyCleared'] is False and proof['forcedGc'] is False,'real case scope')
        require(all(proof.get(k)==0 for k in ['adbCalls','deviceRuns','gradleRuns','realMediaBytesRead']),'forbidden activity')
        counts+=proof['assertions'];children+=proof['actualChildLaunches']
        if case['case'] in {'throw_before','throw_after'}:
            require(proof['retainedOwnersAtCaseExit']==1 and proof['proof']['closeCalls']==1,'intentional unknown owner erased/retried')
            r=proof['results'][0];require(r['ownership']=='UNKNOWN_RETAINED' and r['originalExitCode']==0 and not r['stdinCloseReturned'] and r['writerReturned'],'exact exit0 close-error counterexample');unknown+=1
        else:require(proof['retainedOwnersAtCaseExit']==0,'unexpected unreturned case')
    require(counts==checks['assertions'] and unknown==2,'assertion/unknown counts')
    refs=reader.json(BASE+'/evidence/reference-map.json')
    for row in refs['files']:
        reader.match(dict(path=row['destination'],bytes=row['bytes'],sha256=row['sha256']))
        if (ROOT/row['source']).is_file():require(reader.data(row['source'])==reader.data(row['destination']),'old reference changed')
    oldseal=BASE+'/reference/02-transfer-freeze.json';oldmanifest=BASE+'/reference/03-source-manifest.json';oldzip=BASE+'/reference/04-D1-20261017-E4A-T-source.zip'
    require(sha(reader.data(oldseal))=='3b650fd8f14956216e9fa5c9f43ebe916e5b832980a6e450515275e09425902a','old tool seal')
    seal=reader.json(oldseal);require(sha(reader.data(oldmanifest))==seal['manifest']['sha256'] and sha(reader.data(oldzip))=='faeec9c657ae813e85ed23a042eeb900f9b26bb76cced52f4bfe1d9196fa6cdc','old complete container')
    with zipfile.ZipFile(io.BytesIO(reader.data(oldzip))) as archive:
        require(set(archive.namelist())=={r['path'] for r in reader.json(oldmanifest)['files']},'old exact source container')
        for row in reader.json(BASE+'/evidence/derived-map.json')['files']:
            source=archive.read(row['source']);reader.logical+=len(source);require(sha(source)==row['sourceSha256'],'derivation source binding');reader.match(dict(path=row['destination'],bytes=row['bytes'],sha256=row['sha256']))
    require(sha(reader.data(BASE+'/reference/05-e4a-freeze.json'))==PRODUCT_SHA,'product seal changed')
    require(reader.json(BASE+'/tools/tablet-preload-plan.json')['executionAuthorized'] is False,'preload authorization false')
    return dict(localAssertions=counts,isolatedCaseInterpreters=6,actualOwnedFakeChildren=children,intentionalUnknownAtIsolatedExit=unknown,isolatedExitNotCreditedAsRelease=True,legacy72Repeated=False,
                adbCalls=0,deviceRuns=0,gradleRuns=0,realMediaBytesRead=0,productFreezeUnchanged=PRODUCT_SHA,transportRootCause='UNKNOWN',devicePreload='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')

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
