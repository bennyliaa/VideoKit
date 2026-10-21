from pathlib import Path
import json,hashlib,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;T=R/'docs/coder/d1fixture-tool02';OLD=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER02_FIX_PREPARATION'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
assert not (E/'authority-and-baseline.json').exists(),'STAGE_A_SNAPSHOT_NO_REPLAY'
req=R/'docs/milestones/D1_JCODEC_OBSERVATION01_TESTER_REQUIREMENTS_V1.0.md';(E/'authorized-requirements-snapshot.md').write_bytes(req.read_bytes())
seal=T/'evidence/fixture-tool02-freeze.json';assert sha(seal)=='5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d'
jar=T/'artifacts/videokit-fixture-tool02.jar';assert jar.stat().st_size==1954730 and sha(jar)=='c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd'
pins=load(T/'evidence/source-input-pins.json');source=[x for x in pins if x['path'].startswith('source/')];assert len(source)==708
actual={p.relative_to(T).as_posix() for p in (T/'source').rglob('*.java')};assert actual=={x['path'] for x in source}
for x in source:p=T/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
assert sum(x['bytes'] for x in source)==4435752
manifest=OLD/'review-evidence-manifest.json';assert sha(manifest)=='2a0a2f9143121a1b1be9221f6f01d2960f2f3a926884bf8841f09336098da90e';old=load(manifest)
assert sha(R/old['report'])=='18bc1c596c10ffeaf3dab3af9bb4e65e5f4ce73d4a9f7e5e997d476efb08b566'
for x in old['evidenceFiles']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
allowed=['source/org/jcodec/containers/mp4/boxes/DataRefBox.java','source/org/jcodec/containers/mp4/boxes/SampleDescriptionBox.java','source/org/jcodec/codecs/h264/mp4/AvcCBox.java']
relevant=allowed+['source/org/jcodec/common/io/NIOUtils.java','source/org/jcodec/containers/mp4/boxes/NodeBox.java','source/org/jcodec/containers/mp4/BoxFactory.java','source/org/jcodec/containers/mp4/DataBoxes.java','source/org/jcodec/containers/mp4/boxes/FullBox.java','source/org/jcodec/containers/mp4/boxes/AliasBox.java','source/org/jcodec/containers/mp4/boxes/UrlBox.java']
snippets=[]
for rel in relevant:
 p=T/rel;lines=p.read_text().splitlines()
 if rel in allowed:selection=range(len(lines))
 else:
  needles=['public static int skip(','ByteBuffer read(','public void parse(','static Box parseChildBox(','public Box newBox(','mappings.put(','public byte getVersion','public int getFlags','public boolean isSelfRef']
  selected=set()
  for at,line in enumerate(lines):
   if any(n in line for n in needles):selected.update(range(max(0,at-1),min(len(lines),at+18)))
  selection=sorted(selected)
 snippets.append(dict(path=(T/rel).relative_to(R).as_posix(),sha256=sha(p),lines=[dict(line=j+1,text=lines[j]) for j in selection]))
save('frozen-source-evidence.json',dict(allowedProductionDifferenceFiles=allowed,baselineAll708SourceRows=source,relevantSources=snippets,newForkRead=False,newJarsOrClassesLoaded=False))
fields=[
 ('dref','full_version_flags_word','relative0..3','one original input.getInt()','retain raw32 word; version unsigned top8/flags low24 derivable from same word; not from child/FullBox defaults'),
 ('dref','declared_entry_count_unsigned','relative4..7','one original input.getInt()','retain unsigned32 as long0..4294967295; never actual children.size, never allocate from count'),
 ('stsd','full_version_flags_word','relative0..3','one original input.getInt()','same raw32 evidence and version/flags derivation, not regenerated doWrite0'),
 ('stsd','declared_entry_count_unsigned','relative4..7','one original input.getInt()','same unsigned32 retention; doWrite max(1,boxes.size) never original count'),
 ('avcC','configuration_version','relative0','original NIOUtils.skip(input,1)','retain exactly consumed unsigned byte; equal-consumption get permitted but zero-remaining/exception state must remain baseline-equivalent'),
 ('avcC','raw_nal_length_size_byte','relative4','original input.get() assigned flags then masked0x03','retain full unsigned raw byte, reserved top6 separately derivable; keep legacy nalLengthSize=(raw&3)+1'),
 ('avcC','raw_sps_count_byte','relative5','original input.get() masked0x1f','retain full unsigned raw byte incl top3 reserved; declaredSps=(raw&31) not spsList.size'),
 ('avcC','declared_pps_count','after original SPS-length/payload loop','original input.get()&0xff','retain same consumed uint8; not ppsList.size; no new seek/read or extra NAL parse'),
 ('all3','observation_complete','after same original full parse body normal return','no additional input read','reset before first possible failure, publish complete only after original parse returns; not validation of full structure/EOF/reserved/count equality')]
save('byte-consumption-and-field-contract.json',dict(origin='Offsets relative to original ByteBuffer.position on entry, not whole-file offsets. Variable SPS/PPS locations follow original library only; no new parser.',fields=[dict(box=a,field=b,position=c,originalOperation=d,oracle=e,status='PREPARED_NOT_RUN') for a,b,c,d,e in fields],legacyReadSequence=dict(dref='getInt4,getInt4,NodeBox.parse',stsd='getInt4,getInt4,NodeBox.parse',avcC='skip<=1,getU8 profile,getU8compat,getU8level,getU8rawLength,getU8rawSpsCount,original SPS loop(getShort signed,getNALheader masked,original NIOUtils.read length-1),getU8ppsCount,original PPS loop'),apiNames='UNBOUND until actual frozen fork; do not invent getters or fake interfaces',newObservationGetters='readonly primitive/immutable snapshots; if complete false getters must reject or explicitly absent/untrusted, never display default0 as successful observation',extraObservedFields='Only if derived from already consumed bytes in allowed three sources and documented, no extra structural parse/reads; otherwise out of scope and blocked'))
cases=[
 ('OA01','authority','Only exact independent fork, no product/driver/old checker or runtime input changes; A never reads floating fork'),
 ('OA02','source identities','All708 base rows and635JCodec/73JAAD lineage; only3 allowed modified production files, remaining705 byte-for-byte same'),
 ('OA03','raw parents','Dref/stsd capture vf/count from exact same two getInt operations; no duplicate/get before original or new rescan/parser'),
 ('OA04','uint count','Preserve0/1 and unsigned high-bit boundary; no signed truncation/clamping; inspect no count-driven allocation first, any later dynamic case separate and safe'),
 ('OA05','actual-versus-declared','Retain declared count even different from real children; underlying parse still normal if baseline does. Policy rejects outside fork, not normalize or repair'),
 ('OA06','unknown parents','Unknown version/flags remain actual observed raw word on successful parse, not silently set0 or rejected by fork'),
 ('OA07','raw config','Original configVersion unsigned byte at skip position retained without changing empty-buffer/failure state'),
 ('OA08','raw reserved','Retain whole lengthSize byte and whole SPS-count byte before masks; keep legacy interpreted fields unchanged'),
 ('OA09','PPS count','Retain same uint8 count only after original SPS loop consumes it; malformed earlier SPS does not publish previous PPS/default value as complete'),
 ('OA10','fresh and builder','new/createEmpty/createAvcCBox/createDataRefBox/createSampleDescriptionBox and setter-created values observation false; no parse means no observation'),
 ('OA11','write not observation','doWrite/estimateSize unchanged; serializing builder/parsed boxes never generates original-observed facts or sets complete'),
 ('OA12','completion meaning','normal parse return complete only means original routine returned; NodeBox may ignore declared count/leave <8-byte tail and avcC may leave extensions; never full conformance/EOF proof'),
 ('OA13','failure reset','good parse then failure must clear previous observation before reads; incomplete never exposes old successful observation, exception class+position preserved'),
 ('OA14','legacy partial state','Do not clear original child lists or SPS/PPS lists/legacy fields to fix failed/repeated parse; baseline retains/partially appends them. New observation resets separately'),
 ('OA15','read sequence','Compare patched/baseline original byte position/remaining/order and existing getters after safe success/failure; no additional input reads, forced byteorder, flip/rewind, bounds repair'),
 ('OA16','truncated parents','Exact original getInt boundaries0..7 and child-consumption exceptions; bounded safe metadata only when separately authorized; no resource/atom attack'),
 ('OA17','short avcC','Zero/short fixed header skip vs get, existing getShort signed lengths, checkState and NIOUtils.read limit failures remain baseline exception/position; not new validator'),
 ('OA18','successful metadata','Use bounded provenance-known own minimal metadata through real original parse; input bytes oracle known at construction, not effective media/AVC decode proof'),
 ('OA19','repeated objects','Second successful parse raw fields reflect second input; existing lists append as baseline; counts never from accumulated list sizes'),
 ('OA20','readonly getters','No public mutation API to observation; primitive values/defensive immutable snapshot; getter calls no input or source mutation; concurrent use not claimed without contract'),
 ('OA21','factory/children','BoxFactory/DataBoxes/NodeBox/Header/AliasBox/UrlBox unmodified; true typed alias/url remain exact semantic source; no leaf/fourcc bypass'),
 ('OA22','algorithm preservation','All codec/muxer/doWrite/timebase/SPS/NAL/parse structural branching original; diff review before executing any future test'),
 ('OA23','artifact identity','Explicit0.2.5-videokit-observation01 new artifact/source+patch hashes; never original c4ed JAR identity/official signature; no old class shadowing'),
 ('OA24','source-to-class','Actual javac output major/source and class hashes, full JAR class set/source match, annotation processors off, tests excluded from production artifact'),
 ('OA25','licensing','Original per-file copyrights/FreeBSD/JAAD PublicDomain+FreeBSD/GuavaApache2 preserved, visible modification notice/SBOM diff; no commercial/patent/FFmpeg clearance'),
 ('OA26','build limits','Coder original compile/jar512MiB observed60s serial/input16MiB/output64MiB with original process+two streams; no new deps/network/Gradle/cache/retries'),
 ('OA27','finite unit limits','Only separately authorized bounded metadata parse <=8KiB/singleJVM256MiB/5s/same original worker join and process/two-stream natural return; no demux/media/encoder/decoder/Main/device'),
 ('OA28','differential origins','Same approved finite JVM must identify original/patched artifacts/class origin separately; avoid parent-first shadowing or testing patched against itself; future loader mechanism not presumed authorized now'),
 ('OA29','raw receipt completeness','All stdout/stderr pending/final/source/diff/class/compile-test owners/manifest/seal ZIP consistent; exit0 never replaces fields or original return'),
 ('OA30','later checker integration','Checker02 mandatory blockers cannot be removed until exact fork independentB and explicit integration/new classpath/scope; original readonly file still unparsed'),
 ('OA31','immutability','Original JAR/media/tool/checker reports/classes/seals/failedscope stay frozen; no concurrent shared cache or product dependency/APK change'),
 ('OA32','classification','A preparation only; future metadata observability is not actual file/sample/CSD/time/Media3/HOST_CONTAINER/isolated/READY/COMMIT; D1 notpassed M0notstarted oldUNKNOWN untouched')]
save('independent-oa01-oa32-oracles.json',dict(phase='A_FROZEN_BASELINE_ONLY',status='PREPARED_NOT_RUN',cases=[dict(id=a,area=b,oracle=c,status='PREPARED_NOT_RUN',floatingForkRead=False,dynamicExecuted=False) for a,b,c in cases],candidateForkIdentity=None,dynamicCasesActuallyRun=0,newBuildProcesses=0,mediaReads=0))
failure=[
 ('parents_short','0..7 bytes relative to parent start','getInt atomic consumption4/4; baseline BufferUnderflow at original boundary','same legacy partial fields/lists; no complete observation'),
 ('avcc_empty','original skip=min(remaining,1), then profile get','replacing skip by get must preserve same exception class/position and old legacy getters even if throw statement location differs','no phantom observed config0'),
 ('avcc_short_header','before rawLength/SPS-count/PPS-count originally consumed','existing fields assigned in original order; no eager full preflight changing baseline assignment/position','only complete false, no stale raw values trusted'),
 ('avcc_bad_ps','safe bounded payload that baseline rejects; never huge length/metadata allocation','original signed getShort, masked NAL checkState and NIOUtils.read behavior preserved; future actual error class/position compared','do not validate/repair lengths or clear old lists'),
 ('node_early_return','valid minimal children or no children; <8 tail/count mismatch','super.parse normal return can retain tail or count mismatch, patch completion is not legal-container verdict','later qualification must check raw declarations separately'),
 ('reused_success_fail','one good parse, same object short failing parse','observation false/reset before possible failure; original legacy partial state identical to baseline','new getters absent/throw/untrusted while false, no previous complete true'),
 ('reused_success_success','same original object parses next safe input','new raw fields reflect latest consumed values; original children/SPS/PPS append unchanged','new declared count distinct from accumulated actual counts')]
save('failure-and-default-state-contract.json',dict(cases=[dict(id=a,scenario=b,baselineObligation=c,observationObligation=d,status='PREPARED_NOT_RUN') for a,b,c,d in failure],notAllowed=['new parser','pre-scan','extra native source reads','alter mature exception policy','repair or normalize counts','clear legacy lists','builder/doWrite generation of observed facts','serializing parsed object to infer original bytes','default0 treated as observed','candidate fork inspection in phaseA'],laterDynamicScope='NOT_AUTHORIZED_BY_THIS_PHASE'))
save('future-b-evidence-and-identity-contract.json',dict(state='PHASE_A_ONLY_FUTURE_B_NOT_AUTHORIZED',newArtifactLabel='0.2.5-videokit-observation01',newJarSha256=None,newForkSealSha256=None,patchSha256=None,newGetterBindings=None,newClassIdentities=None,allowedModifiedSourcePaths=allowed,unchangedSourceExpected=705,allSourceExpected=708,baseSourceArchiveSha256='9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db',baseToolJarSha256=sha(jar),requiredFrozenDelivery=['full main report and actual new label/manifest','708 before-after source hashes/3 exact diff/patch SHA/no other production changes','byte-consumption/new-getter completeness-state contract for every retained field','original compiler/jar and finite unit-test process+streams and actual return receipts','actual javac class provenance and production/test packaging split','original copyright notices/new modification notices/SBOM changes','full immutable seal+ZIP same-member/hash evidence'],futureIndependentB=['coordinator verify full freeze then explicit separateB authorization','independent source/diff/API and class/JAR/license/provenance review before runtime','finite dynamic metadata only if separately authorized; exact method names from frozen code not guessed','no actual MP4/demux/encoder/decoder/Main/Media3/Android/device or old session','checker integration and real immutable file check are yet another explicit batch'],defaultObservationState='NOT_OBSERVED_MUST_NOT_CLAIM_FIELD_VALUES',wholeQualification='OPEN_BLOCKED',oldScopesNotReplayable=['D1QUAL01-CANDIDATE-001']))
save('authority-and-baseline.json',dict(checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),requirementsSha256=sha(req),baselineToolSealSha256=sha(seal),baselineToolJarSha256=sha(jar),all708SourceBytes=sum(x['bytes'] for x in source),all708SourceHashesMatched=True,oldChecker02ReportSha256=old['reportSha256'],oldChecker02ManifestSha256=sha(manifest),oldChecker02EvidenceFilesPreserved=len(old['evidenceFiles']),allowedProductionDifferenceFiles=allowed,floatingForkQueriesOrReads=0,newCompilerJarJvmProcesses=0,actualMediaReads=0,newObservabilityCodeWritten=0,oldSessionQueriesOrInterventions=0,stage='A_ONLY_PREPARATION',status='ORACLES_PREPARED_NOT_RUN'))
print('A_ONLY_PREPARED_NOT_RUN:708 baseline source pins;3 allowed;OA01-32; no floating fork/runtime/media')
