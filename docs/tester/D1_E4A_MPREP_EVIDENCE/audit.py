"""Existing receipt audit only. No ADB, production runner, or additional real-media reads."""
from pathlib import Path
import json,hashlib
E=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
r=json.loads((E/'result.json').read_bytes());rows=[];originals={};texts={}
for row in r['records']:
    ref=row['ref'];p=E/ref['file'];b=p.read_bytes();assert len(b)==ref['bytes'] and sha(b)==ref['sha256'];v=json.loads(b);originals[ref['file']]=v
    assert v['status']=='PROCESS_IO_COMPLETE_ONLY' and v['ownership']=='RETURNED' and v['originalExitCode']==0 and v['originalExitObserved'] and not v['errors'] and not v['creationUnknown']
    assert all(v[k] for k in ('flushReturned','stdinCloseReturned','sourceCloseReturned','writerReturned')) and v['stdinCloseError'] is None
    for stream in ('stdout','stderr'):
        s=v[stream];raw=bytes.fromhex(s['prefixHex']);assert not s['prefixTruncated'] and len(raw)==s['bytes'] and sha(raw)==s['sha256'] and s['closeReturned'] and s['error'] is None
        if stream=='stdout':texts[row['stage']]=raw.decode('ascii');(E/(row['stage']+'-stdout.txt')).write_bytes(raw)
        else:assert not raw
    rows.append(dict(stage=row['stage'],file=ref['file'],recordBytes=len(b),sha256=sha(b),elapsedSeconds=v['elapsedSeconds'],stdoutBytes=v['stdout']['bytes'],stdoutSha256=v['stdout']['sha256'],stdinBytes=v['submittedBytes'],exit=0,ownership='RETURNED'))
assert r['status']=='TWO_FIXTURES_PREPARED_NOT_PRODUCT_PASS' and r['metadataCommands']==13 and r['producerAttempts']=={'basic.mp4':1,'subtitle.avi':1} and r['retainedLocalOwners']==0
assert len(rows)==15 and r['mp4Dependency']['verifiedOriginalStages']==4 and r['mp4Dependency']['verifiedContent'] and r['mp4Dependency']['originalOwnersReturned']
attempt=json.loads((E/'attempt.json').read_bytes());files=[]
for spec in attempt['sourceFiles']:
    alias=spec['alias'];f=r['files'][alias];ev=f['evidence'];ref=f['ready'];b=(E/ref['file']).read_bytes();assert len(b)==ref['bytes'] and sha(b)==ref['sha256'];body=json.loads(b)
    assert body['batch']==r['batch']==attempt['batch'] and body['manifestSha256']==r['manifestSha256']==attempt['manifestSha256'] and body['file']==spec and body['evidence']==ev and body['state']=='READY_FROM_CURRENT_ORIGINAL_RECORDS'
    assert set(body['originals'])=={'producer','temp','publish','final'}
    for stage,rr in body['originals'].items():
        bb=(E/rr['ref']['file']).read_bytes();assert len(bb)==rr['ref']['bytes'] and sha(bb)==rr['ref']['sha256'];o=json.loads(bb);assert o==originals[rr['ref']['file']] and o['argv']==rr['expectedArgv']
    source=ev['rawSource'];enc=ev['encoding'];n=spec['bytes'];h=spec['sha256'];wire=spec['encodedBytes'];assert wire==4*((n+2)//3)
    assert source['expectedBytes']==source['prehash']['rawBytes']==source['streamBytes']==n and source['expectedSha256']==source['prehash']['rawSha256']==source['streamSha256']==h and source['actualRawCloseReturned'] and source['streamReachedDeclaredEnd']
    assert enc['expectedBytes']==enc['actualSubmittedBytes']==source['prehash']['encodedBytes']==wire and enc['expectedSha256']==enc['actualSubmittedSha256']==source['prehash']['encodedSha256'] and enc['noEncodedDiskCopy']
    v=originals[body['originals']['producer']['ref']['file']];assert v['submittedBytes']==wire and v['submittedSha256']==enc['expectedSha256'] and v['sourceStreamReadBytes']==wire
    rx=ev['receiver'];assert rx['DECODE']=={'rc':'0'} and rx['BEGIN']['pid']==rx['END']['pid'] and rx['END']['bytes']==str(n) and rx['END']['decoderRc']==rx['END']['statRc']=='0' and rx['BEGIN']['path']==rx['END']['path']==spec['temp']
    tmp=ev['tempProof'];final=ev['finalProof'];pub=ev['publication'];stamp=tmp['before'];assert tmp['after']==pub['stamp']==final['before']==final['after']==stamp
    assert tmp['sha']==final['sha']==h and tmp['bytes']==final['bytes']==str(n) and tmp['path']==spec['temp'] and final['path']==spec['final'] and pub['tempAbsent']=='1'
    dev,ino,count,uid,mode,mtime=stamp.split(',');assert count==str(n) and uid=='10221' and int(mode,16)&0o170000==0o100000 and not int(mode,16)&2
    assert ev['allOriginalOwnersReturned'] and ev['tempAbsenceObserved'] and f['readyVerified']['verifiedOriginalStages']==4
    files.append(dict(alias=alias,rawBytes=n,rawSha256=h,encodedBytes=wire,encodedSha256=enc['expectedSha256'],rawReadBytes=2*n,encodedGeneratedBytes=2*wire,deviceHashBytes=2*n,stamp=stamp,receiverPid=rx['BEGIN']['pid'],final=spec['final'],ready=ref,peakTrackedBufferBytes=source['peakTrackedBufferBytes']))
out=dict(audit='PASS',status=r['status'],records=rows,files=files,initialSpace=r['initialSpace'],mp4Dependency=r['mp4Dependency'],decoderProbe=r['decoderProbe'],uidSnapshot=texts['uid-snapshot'],hostRawReadBytes=sum(f['rawReadBytes'] for f in files),encodedGeneratedBytes=sum(f['encodedGeneratedBytes'] for f in files),encodedSubmittedBytes=sum(f['encodedBytes'] for f in files),deviceIndependentHashBytes=sum(f['deviceHashBytes'] for f in files),receiptMetadataReads=r['receiptMetadataReads'],receiptMetadataReadBytes=r['receiptMetadataReadBytes'],originalArtifactBytes=sum((E/x).stat().st_size for x in ['attempt.json','result.json',*[row['file'] for row in rows],*[f['ready']['file'] for f in files]]),retainedLocalOwners=0,inFlight=[],priorRemoteOwnership=r['priorRemoteOwnership'],productMethodsRun=r['productMethodsRun'],oldResidualAccess=0,extraRealMediaReads=0,extraDeviceCalls=0)
(E/'receipt-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
