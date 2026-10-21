raise SystemExit("REFERENCE_ONLY: C14 inherited admission already prepared/hashed; do not overwrite C14 NOTICE/SBOM with legacy generator. Use frozen inherited-native-admission receipt.")
from pathlib import Path
import hashlib,json,shutil,sys
root=Path(sys.argv[1]).resolve();old=root/'docs/coder/d1c09';base=root/'docs/coder/d1c14';e=base/'evidence';inherit=e/'inherited-c09';inherit.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
assert sha(old/'evidence/freeze-summary.json')=='cdc48afed4f10e38fca5ad5efaf3fb4602947acc2166caa1f08d255bb89ce4fa'
summary=json.loads((old/'evidence/freeze-summary.json').read_text(encoding='utf-8'));frozen={r['path']:r for r in summary['evidence']}
names=['ffmpeg-source-identity.json','ffmpeg-signature.log','ffmpeg-key-import.log','ffmpeg-admission.json','ffmpeg-object-source-license-map.json','ffmpeg-security-coverage.json','ffmpeg-8.0-to-8.0.3-delta.json','iamf-equivalent-fixed-function.txt','ffmpeg-security.html','ffmpeg-download.html','quota-build.json','ndk-NOTICE.txt','ndk-NOTICE.toolchain.txt','ndk-source.properties.txt','dependency-baseline-review.json','c09-sbom.cdx.json','cpu-native-dependencies.txt','jni-source-dependency-map.json']
records=[]
for name in names:
 p=old/'evidence'/name;expected=frozen[p.relative_to(root).as_posix()];assert sha(p)==expected['sha256'];q=inherit/name;shutil.copyfile(p,q);records.append(row(q))
for name in ['ffmpeg-generated','security-patches']:
 for p in (old/'evidence'/name).rglob('*'):
  if p.is_file():
   assert sha(p)==frozen[p.relative_to(root).as_posix()]['sha256'];q=inherit/p.relative_to(old/'evidence');q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
mapping=json.loads((inherit/'ffmpeg-object-source-license-map.json').read_text(encoding='utf-8'));assert len(mapping['objects'])==266
mapping['scope']='266 compiled FFmpeg objects and all non-system compiler dependencies; inherited paths identify immutable C09 provenance; generated files/full compressed corresponding source retained in C14'
(inherit/'ffmpeg-object-source-license-map.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8')
for record in records:
 if record['path'].endswith('ffmpeg-object-source-license-map.json'):
  record.update(row(inherit/'ffmpeg-object-source-license-map.json'));record['metadata_only_correction']='scope 267 -> 266; object/dependency arrays unchanged'
for lib in ['libavcodec.so','libavformat.so','libavutil.so','libswscale.so','libvideokit_alloc.so']:
 assert sha(base/'native-libs/arm64-v8a'/lib)==sha(old/'native-libs/arm64-v8a'/lib)
assert sha(base/'native/quota.c')==sha(old/'native/quota.c')
shutil.copyfile(old/'native/cpu.c',inherit/'c09-cpu.c');shutil.copyfile(old/'native/lease.c',inherit/'c09-lease.c')
assert sha(base/'upstream/ffmpeg-8.0.3.tar.xz')=='6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818'
notice=base/'notice-assets/licenses/NOTICE-C14.txt';notice.write_text((old/'notice-assets/licenses/NOTICE-C09.txt').read_text(encoding='utf-8').replace('C09','C14').replace('c09','c14')+'\nC14 reuses byte-identical audited FFmpeg 8.0.3 and allocation quota libraries from C09. Only task/control/lifecycle glue and JNI package identity changed; no upstream codec modifications. Original correspondence and source hashes are anchored by inherited-c09 evidence.\n',encoding='utf-8')
sbom=json.loads((inherit/'c09-sbom.cdx.json').read_text(encoding='utf-8'));sbom['metadata']['component']['name']='VideoKit D1 C14 local Debug lifecycle experiment';sbom['metadata']['component']['version']='D1-20261016-C14';sbom['properties'].append({'name':'inherited-native-provenance','value':'C09 signed 8.0.3/config/266 objects/608 dependencies/quota sources unchanged; no FFmpeg rebuild or dependency upgrade; new JNI package/lifecycle glue audited separately'})
for component in sbom['components']:
 if component.get('name')=='VideoKit CPU JNI/quota project glue':component['version']='D1-20261016-C14'
(e/'c14-sbom.cdx.json').write_text(json.dumps(sbom,indent=2),encoding='utf-8')
for name in ['docs/tester/D1_C09_TEST_REPORT_V1.0.md','docs/milestones/D1_C14_CODER_REQUIREMENTS_V1.0.md']:
 p=root/name;shutil.copyfile(p,e/('input-'+p.name))
result={'candidateId':'D1-20261016-C14','sourceCandidate':'D1-20261016-C09','sourceSummarySha256':sha(old/'evidence/freeze-summary.json'),'ffmpegVersion':'8.0.3','sourceArchive':row(base/'upstream/ffmpeg-8.0.3.tar.xz'),'unchangedNative':[row(base/'native-libs/arm64-v8a'/name) for name in ['libavcodec.so','libavformat.so','libavutil.so','libswscale.so','libvideokit_alloc.so']],'inheritedVerifiedInputs':records,'objectMapCorrection':'scope wording 267 -> actual 266 in C14 only; records unchanged','signature':'C09 verified receipt reused, no new GPG invocation','admission':'DEBUG_EXPERIMENT_ONLY / PRODUCT_DISTRIBUTION_NOT_APPROVED'}
(e/'inherited-native-admission.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('C09 admission anchored; 5 unchanged native inputs, 266 objects; full source archive and licenses retained')
