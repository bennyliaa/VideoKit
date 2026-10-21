from pathlib import Path
import json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parents[2];B=R/'docs/coder/d1fixture-tool01';O=R/'docs/coder/d1media3-android01';assert not B.exists();B.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['source','driver/com/videokit/fixturetool','reference','licenses','tools','evidence','artifacts']:(B/name).mkdir(parents=True)
source=O/'reference/generation-proposal-source';archive=source/'jcodec-0.2.5-sources.jar';assert archive.stat().st_size==1246282 and sha(archive)=='9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db'
for p in source.iterdir():
 if p.is_file() and p.suffix!='.java':shutil.copyfile(p,B/'reference'/p.name)
shutil.copyfile(source/'LICENSE-official-repository',B/'licenses/JCODEC-FreeBSD-LICENSE.txt')
for p in [R/'docs/milestones/D1_FIXTURE_TOOL01_BUILD_CODER_REQUIREMENTS_V1.0.md',R/'docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_REVIEW_REPORT_V1.0.md',O/'GENERATION_API_SEQUENCE_PROPOSAL.txt']:
 shutil.copyfile(p,B/'reference'/p.name)
rows=[]
with zipfile.ZipFile(archive) as z:
 for n in z.namelist():
  p=Path(n);assert not p.is_absolute() and '..' not in p.parts
  if n.endswith('.java'):
   assert n.startswith(('org/jcodec/','net/sourceforge/jaad/'));out=B/'source'/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(z.read(n));rows.append({'archiveEntry':n,'path':out.relative_to(B).as_posix(),'bytes':out.stat().st_size,'sha256':sha(out)})
assert sum(x['bytes'] for x in rows)<16*1024*1024
(B/'evidence/extracted-source-identity.json').write_text(json.dumps({'archiveSha256':sha(archive),'unmodifiedJavaFiles':rows,'totalBytes':sum(x['bytes'] for x in rows),'executedOrLoaded':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'mainJavaFiles':len(rows),'sourceBytes':sum(x['bytes'] for x in rows),'candidate':str(B)},indent=2))
