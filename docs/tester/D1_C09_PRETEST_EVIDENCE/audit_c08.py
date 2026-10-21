"""Read-only audit of frozen C08; never compare moving C09 workspace sources."""
import hashlib,json,pathlib,re,struct,tarfile,zipfile
ROOT=pathlib.Path(r'D:\CodexProjects\VideoKit'); OUT=pathlib.Path(__file__).resolve().parent; E=ROOT/'docs/coder/d1c08/evidence'
def sha(data):return hashlib.sha256(data).hexdigest()
def check(record):
 p=ROOT/record['path']; data=p.read_bytes(); assert len(data)==record['bytes'] and sha(data)==record['sha256'],record['path']
summary=json.loads((E/'freeze-summary.json').read_text());manifest=json.loads((E/'source-manifest.json').read_text())
assert sha((E/'source-manifest.json').read_bytes())==summary['source_manifest_sha256']
for r in summary['artifacts']+summary['evidence']:check(r)
print('ARTIFACT_EVIDENCE_HASH_PASS',flush=True)
expected={r['path']:r for r in manifest['source_files']}
with zipfile.ZipFile(ROOT/'docs/coder/d1c08/artifacts/D1-20261005-C08/D1-20261005-C08-source.zip') as z:
 assert set(z.namelist())==set(expected) and len(z.namelist())==len(expected)
 for i,(name,r) in enumerate(expected.items(),1):
  data=z.read(name);assert len(data)==r['bytes'] and sha(data)==r['sha256'],name
  if i%2000==0:print('ZIP_VERIFIED '+str(i),flush=True)
 config=z.read('docs/coder/d1c08/upstream/source/ffmpeg-8.0/configure').decode()
 assert 'mpeg4_decoder_select="h263_decoder"' in config
 assert 'h263_decoder_select="h263_parser ' in config
 print('ZIP_SOURCE_HASH_PASS',flush=True)
objects=json.loads((E/'ffmpeg-compiled-dependencies.json').read_text())
for r in objects['objects']:check(r)
print('267_OBJECT_HASH_PASS',flush=True)
review=json.loads((E/'ffmpeg-build-review.json').read_text());elf=[]
for record in review['libraries']:
 check(record);b=(ROOT/record['path']).read_bytes();assert b[:6]==b'\x7fELF\x02\x01'
 typ,machine=struct.unpack_from('<HH',b,16);phoff=struct.unpack_from('<Q',b,32)[0];phsize,phnum=struct.unpack_from('<HH',b,54)
 ph=[struct.unpack_from('<IIQQQQQQ',b,phoff+i*phsize) for i in range(phnum)]
 loads=[p for p in ph if p[0]==1];assert typ==3 and machine==183 and all(p[7]>=16384 and (p[3]-p[2])%p[7]==0 for p in loads)
 dyn=next(p for p in ph if p[0]==2);tags=[]
 for offset in range(dyn[2],dyn[2]+dyn[5],16):
  tag,value=struct.unpack_from('<qQ',b,offset)
  if tag==0:break
  tags.append((tag,value))
 address=next(v for t,v in tags if t==5);load=next(p for p in loads if p[3]<=address<p[3]+p[5]);stringbase=load[2]+address-load[3]
 def string(index):
  start=stringbase+index;return b[start:b.index(b'\0',start)].decode()
 needed=[string(v) for t,v in tags if t==1];soname=[string(v) for t,v in tags if t==14]
 assert needed==record['needed'] and soname==record['soname']
 elf.append(dict(file=record['path'],sha256=record['sha256'],aarch64=True,loadAlignments=[p[7] for p in loads],needed=needed,soname=soname,runtime='NOT_RUN'))
source=json.loads((E/'ffmpeg-source-identity.json').read_text())
archive=ROOT/'docs/coder/d1c08/upstream/ffmpeg-8.0.tar.xz'
if not archive.exists():
 candidates=list((ROOT/'docs/coder/d1c08/upstream').glob('*.tar.xz'));assert len(candidates)==1;archive=candidates[0]
assert sha(archive.read_bytes())==source['archive_sha256']
upstream={r['path'].split('/upstream/source/ffmpeg-8.0/',1)[1]:r for r in source['files']}
archive_count=0
with tarfile.open(archive,'r:xz') as t:
 for member in t:
  if not member.isfile():continue
  key=member.name.split('/',1)[1];r=upstream[key];data=t.extractfile(member).read()
  assert len(data)==r['bytes'] and sha(data)==r['sha256'],key
  archive_count+=1
assert archive_count==len(upstream)
generated=(ROOT/'docs/coder/d1c08/outputs/ffmpeg-build/config_components.h').read_text()
enabled={kind:re.findall(r'^#define CONFIG_(\w+)_'+kind+r' 1$',generated,re.M) for kind in ['DECODER','PARSER','DEMUXER','ENCODER','MUXER','PROTOCOL','HWACCEL']}
assert enabled==review['generated_configuration']
result=dict(candidateId=summary['candidateId'],integrity_status='PASS_FROZEN_ARCHIVES_AND_LISTED_EVIDENCE',artifacts=len(summary['artifacts']),evidenceFiles=len(summary['evidence']),zipSources=len(expected),zipSourceBytes=sum(r['bytes'] for r in expected.values()),sourceZipSha256=summary['artifacts'][0]['sha256'],freezeSummarySha256=sha((E/'freeze-summary.json').read_bytes()),upstreamArchiveSha256=source['archive_sha256'],upstreamSourceIdentityEntries=len(source['files']),upstreamTarEntriesVerified=archive_count,compiledObjectsVerified=len(objects['objects']),dependencyRecords=len(objects['dependency_files']),generatedConfiguration=enabled,libraries=elf,movingWorkspace='NOT_REVIEWED_AS_CANDIDATE',gpg='Frozen signature receipt inspected; no independent gpg rerun',gradle='NOT_RUN',device='NOT_RUN',admission='BLOCKED / NOT_READY')
(OUT/'c08-freeze-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
