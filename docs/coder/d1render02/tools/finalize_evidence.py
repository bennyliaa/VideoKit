from pathlib import Path
import hashlib,json,shutil,collections
B=Path(__file__).resolve().parents[1];E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
P=E/'metadata-rejection-003';positive=json.loads((P/'positive/receipt.json').read_text(encoding='utf-8-sig'));negative=json.loads((P/'negative/receipt.json').read_text(encoding='utf-8-sig'))
assert positive['exitCode']==0 and negative['exitCode']!=0
report=next((P/'negative/build/reports/dependency-verification').glob('*/dependency-verification-report.html'));shutil.copyfile(report,P/'negative-checksum-report.html')
pin=json.loads((E/'new-metadata-pin.json').read_text(encoding='utf-8'));probe=json.loads((P/'negative/probe-input.json').read_text(encoding='utf-8'));html=report.read_text(encoding='utf-8')
assert pin['sha256'] in html and probe['probeSha256'] in html and pin['sha256']!=probe['probeSha256']
assert sha(B/'offline-maven/com/google/guava/guava-parent/33.3.1-android/guava-parent-33.3.1-android.pom')==pin['sha256']
dump(P/'summary.json',{'result':'PASS_STRICT_METADATA_REJECTION_CONTROL','positiveExitCode':0,'negativeExitCode':negative['exitCode'],'expectedSha256':pin['sha256'],'tamperedSha256':probe['probeSha256'],'specificArtifact':'com.google.guava:guava-parent:33.3.1-android POM','actualMismatchReport':'negative-checksum-report.html','canonicalMirrorUnchanged':True,'earlierInvalidProbes':['metadata-rejection: variant selection failed both branches','metadata-rejection-002: unrelated missing transitive checker-qual both branches'],'scope':'Forced Maven POM parser, no transitive artifact download, strict=true, verifyMetadata=true. Independent provenance acceptance remains pending.'})
sbom=json.loads((B/'render02-sbom.cdx.json').read_text(encoding='utf-8'));actual=json.loads((E/'actual-consumption/artifacts.json').read_text(encoding='utf-8'));observed={x['sha256'] for x in actual if x['kind']=='binary'};runtime=[]
for c in sbom['components']:
 if c.get('group'):
  coordinate=c['group']+':'+c['name']+':'+c['version'];hashes=[h['content'] for h in c.get('hashes',[]) if h['alg']=='SHA-256'];used=[x for x in actual if x['coordinate']==coordinate and x['kind']=='binary'];runtime.append({'coordinate':coordinate,'frozenArtifactHashes':hashes,'kind':'binary' if hashes else 'metadata_or_variant_alias_no_binary','actualSelectedBinaryHashes':[x['sha256'] for x in used],'frozenHashesNotSelected':[h for h in hashes if h not in observed],'actualStrictBuildBinaryObserved':bool(used) and all(x['sha256'] in hashes for x in used) if hashes else True})
 if c.get('name')=='VideoKit CPU JNI/quota project glue':
  c['version']='D1-20261016-C14-reused-for-RENDER02'
  for nested in c.get('components',[]):
   if nested['name']=='libvideokit_cpu.so':nested['version']='D1-20261016-C14';nested['hashes']=[{'alg':'SHA-256','content':sha(B/'native-libs/arm64-v8a/libvideokit_cpu.so')}];nested['properties']=[{'name':'correspondingSource','value':'reused-native-source/cpu.c (C14); matched C14 ABI, no native rebuild; full release corresponding-source obligations remain open'}]
assert len(runtime)==35;assert all(x['actualStrictBuildBinaryObserved'] for x in runtime),[x for x in runtime if not x['actualStrictBuildBinaryObserved']]
dump(E/'runtime-35-actual-binary-identity.json',{'result':'PASS_35_LOCKED_COMPONENTS_ALL_SELECTED_BINARIES_MATCH_FROZEN_HASHES','lockedComponents':35,'binaryComponents':sum(bool(x['frozenArtifactHashes']) for x in runtime),'metadataOrVariantAliasComponents':sum(not x['frozenArtifactHashes'] for x in runtime),'components':runtime});dump(B/'render02-sbom.cdx.json',sbom)
attempts=[]
for d in sorted(E.glob('build-main-*')):
 r=json.loads((d/'receipt.json').read_text(encoding='utf-8-sig'));attempts.append({'attempt':d.name,'exitCode':r['exitCode'],'receipt':(d/'receipt.json').relative_to(B).as_posix(),'interpretation':{'001':'local Gradle daemon communication failed; compilation not reached','002':'POM-only default repository could not resolve cached module-only Android plugin','003':'fresh-home strict offline full app/test build PASS 67 executed; initial observer omitted verification progress names','004':'strict replay PASS; captured exact verification events, 67 up-to-date','005':'final explicit metadata source order strict replay PASS; exact consumed closure captured, 67 up-to-date'}[d.name[-3:]]})
dump(E/'build-attempts.json',attempts)
dump(B/'completion-matrix.json',{'candidateId':'D1-20261020-RENDER02','D1':'NOT_PASSED','M0':'NOT_STARTED','rows':[
 {'id':'META_OFFICIAL_SOURCE','status':'PASS','scope':'new official fixed-version POM/raw HTTP/checksum evidence only; not historical approval'},
 {'id':'META_INDEPENDENT_ADMISSION','status':'BLOCKED','scope':'PENDING_TESTER_REVIEW; coder cannot close P1'},
 {'id':'META_STRICT_BUILD_CLOSURE','status':'PASS','scope':'verify-metadata=true + strict; 327 actual artifacts/192 metadata; explicit module metadata can avoid Guava POM parent'},
 {'id':'META_TAMPER_REJECTION','status':'PASS','scope':'positive original parent resolves; changed parent specifically checksum-rejected'},
 {'id':'R02_BASELINE_DEFECT','status':'PASS','scope':'frozen RENDER01 reproduced drawn=1 bitmap=0 post=1; old failure retained'},
 {'id':'R02_CONTROLLED_REGRESSION','status':'PASS','scope':'actual production renderer/core JVM Android stubs; 5 render scenarios'},
 {'id':'R03_IDLE_CLICK_POLICY','status':'PASS','scope':'bounded single-click/idle/timeout JVM policy and compiled fifth same-package entry'},
 {'id':'CORE_SELF_CHECK','status':'PASS','scope':'9 existing local semantic groups'},
 {'id':'APP_TEST_BUILD_SIGNER','status':'PASS','scope':'offline app/test static package, 7 native static 16KiB and public signer verification'},
 {'id':'FROZEN_RUNTIME_NATIVE','status':'PASS','scope':'35 locked components (30 with binary hashes, 5 metadata/variant aliases), all selected binaries match frozen hashes; unused Guava JRE variant separately labelled; native7 + PCM unchanged'},
 {'id':'OLD_RENDER01_PRESERVED','status':'PASS','scope':'477 frozen files checked unchanged'},
 {'id':'ANDROID_REAL_EFFECTS','status':'NOT_RUN','scope':'no devices/SDK commands/installation/occupation queries'},
 {'id':'MANUAL_THREE_SECOND_LISTENING','status':'NOT_RUN','scope':'no human listening evidence'},
 {'id':'FULL_D1_ALL_P0','status':'BLOCKED','scope':'D1 not passed; inherited full P0, codec cross-chain/UNKNOWN, licensing/release gaps remain'},
 {'id':'M0','status':'NOT_RUN','scope':'NOT_STARTED; no M0 work'}]})
print('FINAL_EVIDENCE_READY: runtime35 exact, strict rejection verified, original freeze preserved')
