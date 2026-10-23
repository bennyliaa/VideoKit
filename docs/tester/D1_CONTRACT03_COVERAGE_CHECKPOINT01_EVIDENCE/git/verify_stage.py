"""Read-only index and frozen-byte verification after exact staging."""
from pathlib import Path
import hashlib,json,subprocess,sys
G=Path(__file__).resolve().parent;ROOT=G.parents[3]
def run(*args):return subprocess.run(['git',*args],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 planPath=G/(sys.argv[1] if len(sys.argv)>1 else 'stage-plan-v2.json');plan=json.loads(planPath.read_bytes());rows=plan['files'];paths={x['path'] for x in rows}
 assert run('rev-parse','HEAD').decode().strip()==plan['baseHead']
 assert run('branch','--show-current').decode().strip()==plan['branch']
 index={}
 for rec in run('ls-files','--stage','-z').split(b'\0'):
  if not rec:continue
  a,p=rec.split(b'\t',1);mode,oid,stage=a.decode().split();assert stage=='0';index[p.decode()]=oid
 for x in rows:
  b=(ROOT/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path'];assert index[x['path']]==x['gitBlobSha1'],x['path']
 changed={p.decode() for p in run('diff','--cached','--name-only','-z').split(b'\0') if p}
 assert changed and changed<=paths,sorted(changed-paths)
 p=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 assert p.returncode in (0,2),p.returncode
 detail=p.stdout+p.stderr
 with (G/'staged-whitespace-check.txt').open('xb') as f:f.write(detail)
 num=run('diff','--cached','--numstat','-z').split(b'\0');adds=0;dels=0
 for rec in num:
  if not rec:continue
  a,d,path=rec.split(b'\t',2);assert a!=b'-' and d!=b'-';adds+=int(a);dels+=int(d)
 result=dict(schema='CONTRACT03_STAGED_REVIEW_V2',baseHead=plan['baseHead'],branch=plan['branch'],selectedFiles=len(rows),changedFiles=len(changed),unchangedSelectedFiles=len(rows)-len(changed),unexpectedStagedFiles=0,sourceBytesAndGitBlobsExact=True,linesAdded=adds,linesDeleted=dels,allChangedBlobsText=True,whitespaceExitCode=p.returncode,whitespaceDiagnosticBytes=len(detail),whitespaceDiagnosticSha256=sha(detail),whitespacePolicy='Preserve frozen raw bytes; review diagnostics rather than normalize original evidence.',stagePlanSha256=sha(planPath.read_bytes()),actualSDKAndDevices=0,automaticNextTest=False)
 with (G/'stage-review-v2.json').open('xb') as f:f.write((json.dumps(result,indent=2)+'\n').encode())
 print(json.dumps(result))
if __name__=='__main__':main()
