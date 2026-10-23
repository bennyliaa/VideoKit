"""Exclude immutable evidence paths unsupported by Git for Windows; no Git writes."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,re,subprocess
G=Path(__file__).resolve().parent;ROOT=G.parents[3]
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def put(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def git(*args,input=None):return subprocess.run(['git',*args],cwd=ROOT,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
def main():
 old=load(G/'stage-plan.json');assert git('branch','--show-current').decode().strip()==old['branch'] and git('rev-parse','HEAD').decode().strip()==old['baseHead'];assert not git('diff','--cached','--name-only','-z')
 data=load(G/'whitelist.json');excluded=load(G/'excluded.json');rows=[];new=[];rehashed=[]
 for x in data['files']:
  p=ROOT/x['path'];b=p.read_bytes();assert len(b)<=1048576
  if re.search(r'(?:^|/)(?:aux|con|prn|nul|com[1-9]|lpt[1-9])(?:\.[^/]*)?(?:/|$)',x['path'],re.I):new.append(dict(**x,reason='WINDOWS_RESERVED_PATH_COMPONENT_GIT_OPEN_UNSUPPORTED_LOCAL_ORIGINAL_PRESERVED'));continue
  y=dict(x)
  if p in [G/'README.md',G/'verify_stage.py']:
   rehashed.append(dict(path=x['path'],initialSha256=x['sha256'],finalSha256=sha(b),reason='Git-only description/verifier adjusted before final stage; outside frozen test manifest'))
   y.update(bytes=len(b),sha256=sha(b),gitBlobSha1=blob(b))
  else:assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
  rows.append(y)
 p=Path(__file__).resolve();b=p.read_bytes();rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha(b),gitBlobSha1=blob(b),origins=['checkpoint-own-platform-path-review-tool'],licenseReview='VideoKit-owned Git-only audit helper'))
 attrs=git('check-attr','-z','--all','--stdin',input=b'\0'.join(x['path'].encode() for x in rows)+b'\0');assert not attrs
 put(G/'whitelist-v2.json',dict(schema='CONTRACT03_GIT_DATA_WHITELIST_V2',baseHead=old['baseHead'],files=rows,previousPlanSha256=sha((G/'stage-plan.json').read_bytes()),reason='Exclude Windows reserved-name paths unsupported by Git, preserve originals and frozen test manifest; index was empty after failure',controlFilesSeparate=['whitelist-v2.json','excluded-v2.json','review-checks-v2.json']))
 excluded['schema']='CONTRACT03_GIT_EXCLUSIONS_V2';excluded['inspectedExcludedFiles'].extend(new);excluded['gitOnlySupersededLocalFiles']=['whitelist.json','excluded.json','review-checks.json','stage-plan.json','pathspec.nul'];put(G/'excluded-v2.json',excluded)
 checks=load(G/'review-checks.json');checks.update(schema='CONTRACT03_GIT_PRESTAGE_REVIEW_V2',utc=datetime.now(timezone.utc).isoformat(),dataFiles=len(rows),dataBytes=sum(x['bytes'] for x in rows),maxFileBytes=max(x['bytes'] for x in rows),inspectedExcludedFiles=len(excluded['inspectedExcludedFiles']),excludedByReason=dict(collections.Counter(x['reason'] for x in excluded['inspectedExcludedFiles'])),firstStageFailure='Git unable to open reserved aux component; tool chunk66f3be exit1; no staged changes afterwards',gitPathProtectionDisabled=False,originalEvidenceRenamedOrModified=False,gitOnlyRehashedFiles=rehashed,allOtherDataHashesUnchanged=True)
 put(G/'review-checks-v2.json',checks)
 final=[*rows]
 for name in ['whitelist-v2.json','excluded-v2.json','review-checks-v2.json']:
  p=G/name;b=p.read_bytes();assert len(b)<=1048576;final.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha(b),gitBlobSha1=blob(b),origins=['checkpoint-control-file']))
 final.sort(key=lambda x:x['path']);plan=dict(old,files=final,schema='CONTRACT03_EXACT_LOCAL_STAGE_PLAN_V2',previousPlanSha256=sha((G/'stage-plan.json').read_bytes()),reservedPathsExcluded=len(new));put(G/'stage-plan-v2.json',plan)
 with (G/'pathspec-v2.nul').open('xb') as f:f.write(b'\0'.join((':(literal)'+x['path']).encode() for x in final)+b'\0')
 print(json.dumps(dict(files=len(final),bytes=sum(x['bytes'] for x in final),reservedExcluded=len(new),excludedTotal=len(excluded['inspectedExcludedFiles']),maxBytes=max(x['bytes'] for x in final),stagePlanSha256=sha((G/'stage-plan-v2.json').read_bytes()))))
if __name__=='__main__':main()
