"""Review admission and prepare explicit blocked-candidate facts before freezing."""
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c08';e=base/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((e/'ffmpeg-build-review.json').read_text(encoding='utf-8'))
assert review['composition_gate']=='BLOCKED_STRICT_WHITELIST'
assert review['integration']=='STOPPED_NOT_ADMITTED' and not review['apk_built']
assert 'PASS 14' in (e/'exit-record-selfcheck.log').read_text(encoding='utf-8-sig')
assert 'BUILD SUCCESSFUL' in (e/'compile-debug-java.log').read_text(encoding='utf-8-sig')
assert json.loads((e/'integrity-check.json').read_text(encoding='utf-8'))['status']=='PASS'
assert not list((base/'native-libs').rglob('*av*.so*'))
assert not list((base/'artifacts/D1-20261005-C08').glob('*.apk'))
assert 'HOSTCC' not in (e/'ffmpeg-make.log').read_text(encoding='utf-8-sig')
assert 'HOSTLD' not in (e/'ffmpeg-make.log').read_text(encoding='utf-8-sig')
source=base/'upstream/ffmpeg-8.0.tar.xz'
assert sha(source)=='b2751fccb6cc4c77708113cd78b561059b6fa904b24162fa0be2d60273d27b8e'
signature=(e/'ffmpeg-signature.log').read_text(encoding='utf-8-sig')
assert '[GNUPG:] VALIDSIG FCF986EA15E6E293A5644F10B4322F04D67658D8 ' in signature
vulns={'source':'https://ffmpeg.org/security.html','reviewed_at':'2026-10-05','source_version':'8.0',
 'ids':['CVE-2025-69693','CVE-2025-63757','CVE-2025-67306','CVE-2026-8461','CVE-2026-30999'],
 'upstream_observation':'Official later 8.0.x fixed lists contain these IDs. No patch or version upgrade applied here.',
 'compiled_build_reachability':'NOT_ASSESSED','patched':False,'distribution':'PROHIBITED_LOCAL_EVIDENCE_ONLY'}
(e/'ffmpeg-known-vulnerabilities.json').write_text(json.dumps(vulns,indent=2),encoding='utf-8')
sbom={'bomFormat':'CycloneDX','specVersion':'1.6','version':1,'components':[{'type':'library','name':'FFmpeg','version':'8.0','purl':'pkg:generic/ffmpeg@8.0','hashes':[{'alg':'SHA-256','content':sha(source)}], 'licenses':[{'expression':'LGPL-2.1-or-later'}], 'properties':[{'name':'videokit:license-evidence','value':'configure-declared only; full compiled-object clearance incomplete'}, {'name':'videokit:admission','value':'BLOCKED_STRICT_WHITELIST'}]}],
 'properties':[{'name':'videokit:scope','value':'source-level aggregate SBOM; ELF transitive dependencies are fully enumerated in ffmpeg-build-review.json; object-level license SBOM incomplete; no App integration'}]}
(e/'ffmpeg-source-sbom.cdx.json').write_text(json.dumps(sbom,indent=2),encoding='utf-8')
facts={'candidateId':'D1-20261005-C08','candidate_state':'BLOCKED_STRICT_WHITELIST','integrity_assertions':'PASS',
 'local_pure_exit_assertions':14,'android_java_compile':'PASS','ffmpeg_cross_compile':'PASS_LOCAL_ONLY',
 'app_cpu_implementation':'NOT_IMPLEMENTED','app_cpu_integration':'NOT_ADMITTED','apk_built':False,'device_execution':'NOT_RUN',
 'C07_fail_rewritten':False,'C07_summary_sha256':sha(root/'docs/coder/d1c07/evidence/freeze-summary.json'),
 'user_instruction':'Finish blocked delivery accounting then pause development/testing and wait for user resumption.'}
(e/'candidate-self-review.json').write_text(json.dumps(facts,indent=2),encoding='utf-8')
print(json.dumps(facts,indent=2))
