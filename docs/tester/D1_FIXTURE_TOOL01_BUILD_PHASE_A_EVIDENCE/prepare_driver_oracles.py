from pathlib import Path
import json,hashlib,zipfile,re,collections,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1media3-android01';F=B/'reference/generation-proposal-source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,d):(E/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
assert sha(B/'evidence/media3-android01-freeze.json')=='fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a'
assert sha(R/'docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_REVIEW_REPORT_V1.0.md')=='845cd5920251c44beed2497d66d6843e5e6531e209d503cc93eb598f45fe2829'
previous=R/'docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/review-evidence-manifest.json';assert sha(previous)=='61b93d6d827cb29d868a548a2740fcfa88d9d0aeac083c4664582b72fa11d951'
for row in load(previous)['evidenceFiles']:p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
pins=[]
for rel in ['reference/generation-proposal-source/jcodec-0.2.5-sources.jar','reference/generation-proposal-source/jcodec-0.2.5.pom','reference/generation-proposal-source/LICENSE-official-repository','evidence/generation-proposal.json','GENERATION_API_SEQUENCE_PROPOSAL.txt','evidence/earlier-suite-pending.json']:
 p=B/rel;pins.append(dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
src=F/'jcodec-0.2.5-sources.jar';assert src.stat().st_size==1246282 and sha(src)=='9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db'
with zipfile.ZipFile(src) as z:
 sources=[dict(entry=n,bytes=z.getinfo(n).file_size,sha256=hashlib.sha256(z.read(n)).hexdigest()) for n in sorted(z.namelist()) if n.endswith('.java')]
 assert len(sources)==708 and sum(x['bytes'] for x in sources)==4435752
 packages=collections.Counter('net/sourceforge/jaad' if x['entry'].startswith('net/sourceforge/jaad/') else 'org/jcodec' for x in sources)
 imports=[];unsupported=[]
 for row in sources:
  s=z.read(row['entry']).decode('utf8','replace')
  for m in re.finditer(r'^import\s+(?:static\s+)?([\w.]+)',s,re.M):
   imp=m.group(1)
   if not imp.startswith(('java.','javax.','org.jcodec.')):
    imports.append(dict(source=row['entry'],imported=imp,bundled=imp.startswith('net.sourceforge.jaad.')))
    if not imp.startswith('net.sourceforge.jaad.'):unsupported.append(imports[-1])
 assert not unsupported
 selected=['org/jcodec/containers/mp4/muxer/MP4Muxer.java','org/jcodec/containers/mp4/muxer/MP4MuxerTrack.java','org/jcodec/common/io/NIOUtils.java','org/jcodec/common/Preconditions.java','net/sourceforge/jaad/aac/Decoder.java']
 excerpts=[]
 for n in selected:
  s=z.read(n).decode('utf8','replace');lines=s.splitlines()
  patterns=['output.write(buf)','out.write(bs)','channel.write((ByteBuffer) ByteBuffer.allocate(8)','out.setPosition(mdatOffset)','new Date().getTime()','Copyright (C) 2007 The Guava Authors','Public Domain license']
  hits=[]
  for i,line in enumerate(lines):
   if any(p in line for p in patterns):hits.append(dict(line=i+1,text='\n'.join(lines[max(0,i-2):min(len(lines),i+5)])))
  excerpts.append(dict(entry=n,sha256=hashlib.sha256(z.read(n)).hexdigest(),observations=hits))
save('source-inventory-and-api-evidence.json',dict(result='STATIC_SOURCE_INVENTORY_ONLY_NOT_TYPECHECK_OR_BUILD',sourceArchiveSha256=sha(src),archiveEntries=807,javaSourceCount=708,javaSourceBytes=4435752,bundledPackages=dict(packages),nonJavaJcodecImportEntries=len(imports),externalImportCandidates=unsupported,sourceList=sources,apiAndNotices=excerpts,licenseInterpretation='POM/current repository FreeBSD evidence retained; bundled JAAD headers explicitly Public Domain plus JCodec changes FreeBSD, Preconditions Guava Apache2.0 attribution also must survive; not exclusive FreeBSD or distribution clearance',buildReady='NOT_IMPLIED',runtimeLoaded=False))
defs=[
 ('FT01','build identity','Exact source archive/hash, compiler java/javac/jar/release hashes, literal args and working directory pinned; no PATH fallback'),
 ('FT02','source closure','Exact main/driver source list and per-file hashes; archive708 Java includes bundled JAAD, not an absent external dependency; no JUnit/tests/processors/plugins/dynamic resolver'),
 ('FT03','build limit','One coder build, concurrency1, -J-Xmx512m, input<=16MiB/all output<=64MiB; compiler60s observation only stops admission, preserves original process on UNKNOWN; no blind retry'),
 ('FT04','artifact origin','Frozen JAR each class matches actual compiler output/input list, main-class manifest exact, no unexpected class/resource/native; complete build receipts natural return not jar existence'),
 ('FT05','license/source notices','FreeBSD copyright/disclaimer retained plus per-file Apache/JAAD notices; bundled code provenance not erased by POM summary; no patent/FFmpeg/release clearance'),
 ('FT06','no-run gate','Build recipe has no java -jar/Main/encoder initialization/self-test/generate/MediaCodec/Media3/Android/attach; test/compile success not generation authorization'),
 ('FT07','CREATE_NEW','Fixed new canonical output, approved parent no symlink/reparse, existing output rejected without truncation; no original media read or arbitrary path/network args'),
 ('FT08','owner before allocation','One original channel holder registered before FileChannel open and MP4Muxer constructor header write; failed/UNKNOWN allocation strongly retained'),
 ('FT09','full write adapter','Library constructor/chunk/header helper can call write only once: adapter fully drains original bounded ByteBuffer or fails; no silent partial-success wrapper'),
 ('FT10','attempt reserve','Before every native write reserve requested count<=65536, checked against remaining16MiB; cumulative attempted is not returned bytes/file size/extent'),
 ('FT11','positive partial','write10 returns3 then remaining7 returns7 => attempted17/known returned10; continue same exact buffer/channel, not failure retry'),
 ('FT12','header rewrite','After prior10 bytes, seek0/write8 adds8 attempted/8 returned, final extent10 and position8; never refund overwritten bytes or derive attempt from final position'),
 ('FT13','exception/UNKNOWN','After return3 then next7 native write throws, attempted17/known returned3/actual additional amount UNKNOWN; sticky first error no rewind/reissue/second close/refund'),
 ('FT14','zero/invalid native result','Zero native return on nonempty request cannot spin forever or report full success; negative or >request reject; attempt reservation retained and first failure stops admission'),
 ('FT15','exact cap and overflow','Allow remaining exact request if valid, then next1 rejected before native invocation; long offset+len overflow/negative seek rejected without allocation/expansion'),
 ('FT16','position/size/truncate','JCodec seekable contract truthful; setPosition alone not write or budget refund; final seek points into header; unneeded truncate/read must reject or stay bounded no hidden fallback'),
 ('FT17','synthetic input','Only original deterministic YUV420J pattern, signed byte mapping,256x144/one raw55296B/six331776B; no BBB/file decode or user media input'),
 ('FT18','real six access units','Exactly6 real encoder outputs nonempty<=262144; total<=1572864; actual keyflag checked, keyInterval1/motion0; DumbRateControl startsQP20 not constantQP'),
 ('FT19','timebase/EOS','Packet pts0..5/timescale5/duration1=>0..1m us and end1.2m; driver MP4Muxer.finish does not add seventh sample; later Media3 E6 uses emptyEOS flags4 at1.2m'),
 ('FT20','NAL transition','Hash raw encoder AnnexB before mutation, let CodecMP4MuxerTrack strip PS/convert AVCC once; record actual transformed representation separately, no double conversion or unequal representation hash claim'),
 ('FT21','CSD limit','Actual SPS/PPS/CSD bytes+hash+representation, total<=65536 before accepting; retain original notices; do not fabricate CSD or mutate encoder config to meet limits'),
 ('FT22','return milestones','Record actual mux finish, optional same original force, exactly-once original close and external same-worker join separately; elapsed/deadline/receipt not return proof'),
 ('FT23','deadline/first error','60s only closes admission; preserve first error/UNKNOWN/strong refs and original process/channel; no kill/interrupt/secondclose/deletion while return unknown'),
 ('FT24','cleanup permission','Delete only newly owned candidate paths after positive original returns; failed close/allocation UNKNOWN preserves directory; no old candidates/scope/once/ledger changes'),
 ('FT25','hash manifest integrity','Built tool exact JAR/driver/compiler input hashes distinct from source archive hash; generated media size/hash/CSD/sample golden null until later authorized actual generation'),
 ('FT26','determinism scope','Synthetic pixels/timebase are deterministic; source MP4 movie header uses current Date, so no assumption of repeated whole-file identical hash without an explicit reviewed timestamp rule'),
 ('FT27','local UNKNOWN boundary','Original48945/17257 and historical parent/child remain UNKNOWN, no active-directory/owner poll/attach/intervention; continuing tool preparation is not closeout approval or host-idle proof'),
 ('FT28','later gate','StageA preparation, new frozen tool B review, future exact generation and realMedia3 fixture qualification are separate; no built-tool PASS promoted to valid media/product/D1/M0')]
save('independent-driver-oracles.json',dict(phase='A_FROZEN_BASELINE_PREPARATION_ONLY',newDriverRead=False,compilerCalls=0,toolOrEncoderRunCalls=0,cases=[dict(id=i,area=a,oracle=o,status='PREPARED_NOT_RUN',newToolVerdict='NOT_TESTED',executionAuthorized=False) for i,a,o in defs]))
save('attempt-accounting-examples.json',dict(status='DECLARATIVE_EXPECTATIONS_NOT_EXECUTED_IO_TESTS',definitions=dict(A='sum each pre-reserved native write requested count including partial continuation/header rewrites; no refunds',R='sum valid returned native counts; no durability/disk-write claim',extent='max positively observed end, distinct from total attempts; exception may make later physical state UNKNOWN'),examples=[dict(id='EX01',sequence=['position0 request10 return3','same buffer remaining request7 return7'],expected=dict(A=17,R=10,knownExtent=10,knownPosition=10)),dict(id='EX02',sequence=['EX01','setPosition0 no write','request8 return8 header rewrite'],expected=dict(A=25,R=18,knownExtent=10,knownPosition=8)),dict(id='EX03',sequence=['request10 return3','remaining request7 throws without reliable amount'],expected=dict(A=17,RKnownLowerBound=3,additionalPhysical='UNKNOWN',actualPosition='UNKNOWN',retryAllowed=False,refund=0)),dict(id='EX04',priorA=16777208,sequence=['request8 return8','next request1'],expected=dict(A=16777216,nextNativeInvoked=False)),dict(id='EX05',sequence=['nonempty request10 native returns0'],expected=dict(A=10,R=0,unboundedRetryAllowed=False,wholeWriteSuccess=False)),dict(id='EX06',sequence=['zero-length caller write'],expected=dict(nativeInvoked=False,attemptIncrement=0,returnCount=0))]))
proposal=load(B/'evidence/generation-proposal.json')
save('future-evidence-contract.json',dict(status='PREPARED_NO_NEW_DRIVER_OR_ARTIFACT_READ',buildRequired=['exact original compile/package argv/compiler/hash/input pins, one attempt and original actual process returns','all compiled classes and JAR manifest/hash/resource list; actual output footprint with no dedup masquerading as actual bytes','app/APK dependency exclusion and source/license/SBOM inclusion','no Main/encoder init/run and no generated media; original local UNKNOWN retained'],runtimeOnlyFuture=['native write per-call requested/reserved/valid returned/error+UNKNOWN, original offsets and ByteBuffer positions','cumulative attempt vs known returned vs current position vs extent/file size, rewrite/partial accounted separately','registered original owner before allocation, original finish/force/close and external worker join facts','source rights/raw pixel bytes, actual6 AU/CSD/NAL/timebase hashes and generated immutable file identity after separate permission'],currentToolBuildHash=None,currentNewDriverHash=None,currentMediaHash=None,currentCsdHashes=None,externalOwnerStatus='48945/17257 UNKNOWN no polling/intervention',generationAuthorized=False))
save('baseline-identity.json',dict(checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='PASS_FROZEN_SOURCE_AND_PRIOR_REVIEW_PRESERVATION_ONLY',androidSealSha256=sha(B/'evidence/media3-android01-freeze.json'),priorBReportSha256=sha(R/'docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_REVIEW_REPORT_V1.0.md'),priorBEvidenceManifestSha256=sha(previous),priorBEvidenceFilesUnchanged=20,baselinePins=pins,newCandidateRead=False,sourceInventoryOnly=True,compilerOrJcodecInitializationCalls=0,sdkAdbAttachProcessQueries=0))
print('PREPARED28 oracles/6 declarative examples; frozen source708 Java4435752B; no new driver/build/encoding/owner interaction')
