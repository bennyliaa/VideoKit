"""File-only post audit of frozen records and new original-return receipts."""
from pathlib import Path
import json,hashlib,zipfile,time
R=Path(__file__).resolve().parent;T=R.parents[1];B=T.parent/'coder/d1android02-global-idle-contract03-fix';D=B.parent/'d1android02-global-idle-contract03-selfcheck02'
READ=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def rd(p):
 p=Path(p)
 with p.open('rb') as f:b=f.read(10485761)
 assert len(b)<=10485760;READ.append(dict(path=str(p),bytes=len(b)));return b
def load(p):return json.loads(rd(p))
def save(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def packet(base,manifest,expected,archive,archiveSHA,members):
 raw=rd(base/manifest);assert sha(raw)==expected;rows=json.loads(raw)['files']
 for x in rows:
  b=rd(base/x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
 assert sha(rd(archive))==archiveSHA
 with zipfile.ZipFile(archive) as z:
  names=z.namelist();assert len(names)==members and len(set(names))==members
  for x in [*rows,dict(path=manifest,bytes=len(raw),sha256=expected)]:
   assert x['path'] in names;b=z.read(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
 return dict(rows=len(rows),bytes=sum(x['bytes'] for x in rows),bad=0,zipMembers=members,zipSHA256=archiveSHA,zipOriginalFileClosed=True)
def main():
 assert not (R/'post-audit.json').exists();start=time.monotonic();o=load(R/'order.json');W=Path(o['work']);w=load(R/'worker-final.json');out=load(R/'outer-final.json');assert not w['newUnknown'] and w['allOwnOriginalsReturned'] and all(x==0 for x in w['custody'].values()) and out['receipt']['streamsAndOriginalHandleCloseReturned']
 a=packet(B,'reference/freeze-manifest.json','55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81',B.parent/'d1android02-global-idle-contract03-fix-blocked-frozen.zip','45fb593f8b7aa916095540275a7287bdf01e524f5a983befc3768e9c9cb4a58c',99)
 d=packet(D,'reference/material-manifest.json','ec171260f95bfcfd712d4e2245c68b6612f2a8939631ba79a92f9b7f73b2343a',B.parent/'d1android02-global-idle-contract03-selfcheck02-frozen.zip','d3425d18bbf12910ac204bf9d0db7ab03c32687c4f47f95266387aca72af2c65',485)
 am=rd(T/'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_MANIFEST_V1.0.json');assert sha(am)=='8208c09cd12d91c942a9ceadaffe17842ddc0911515b276ccd5c18877210c066'
 for x in json.loads(am)['files']:
  b=rd(x['absolutePath']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
 for x in o['sources']:assert sha(rd(x['path']))==x['sha256']
 receipts=[]
 for p in sorted((R/'aux').glob('*/runtime/outer-original-return.json')):
  r=load(p);assert r['originalWaitReturnedOnce'] and r['readersJoined'] and r['streamsAndOriginalHandleCloseReturned'] and not r['expired'] and not r['errors'];receipts.append(dict(path=str(p),pid=r['identity']['pid'],exitCode=r['exitCode'],seconds=r['seconds'],rawCounts=r['rawCounts']))
 assert len(receipts)==7
 faults=load(R/'fault-summary.json');expiry=load(R/'fault-EXPIRE_DURING_MATERIALIZE.json');assert not (W/'f-7/actual-home').exists()
 verdict=dict(expiryOriginalRaw=expiry,adjudication='FAIL_TARGET_NOT_COVERED: 9s permit expired before home/gate/materialization. OriginalClaimReleased=false remains raw; release was not applicable because no original claim was entered. No completion proof exists to replace.',newHomeCreated=False,claimEntered=False,noSecondAttempt=True)
 save(R/'expiry-target-adjudication.json',verdict)
 result=dict(schema='CONTRACT03_B_POST_AUDIT_V1',candidate=a,developerMaterial=d,semanticAFiles=408,semanticABad=0,ownFrozenSourcesBad=0,ownAuxReturns=receipts,workerOriginalIdentity=out['receipt']['identity'],workerExitCode=2,toolExitCode=1,actualFaultTargets=w['faultExactTargets'],uncovered=w['faultUncovered'],allNewOriginalsReturned=True,newUnknown=False,oldRuntimeQueries=0,postReadBytes=sum(x['bytes'] for x in READ),postReadCalls=len(READ),seconds=time.monotonic()-start,verdict='FAIL_TARGET_COVERAGE_GAPS_NO_NEW_CONFIRMED_PRODUCT_SOURCE_DEFECT',automaticNextTest=False)
 save(R/'post-audit.json',result);print(json.dumps(dict(candidateRows=a['rows'],candidateZip=a['zipMembers'],developerRows=d['rows'],developerZip=d['zipMembers'],ABad=0,auxReturned=7,uncovered=w['faultUncovered'],postBytes=result['postReadBytes'])))
if __name__=='__main__':main()
