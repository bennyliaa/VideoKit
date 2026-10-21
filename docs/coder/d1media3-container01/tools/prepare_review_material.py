from pathlib import Path
import json,shutil,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2];O=R/'docs/coder/d1input-sink05';assert not (B/'evidence/media3-container01-freeze.json').exists()
for name in ['admit_dependencies.py','adapt_batch.py','fixture_scope.py','add_review_cases.py']:
 p=B/'tools'/name;s=p.read_text();needle='B=Path(__file__).resolve().parents[1]';assert needle in s;s=s.replace(needle,needle+";assert not (B/'evidence/media3-container01-freeze.json').exists(),'FROZEN'",1);p.write_text(s,encoding='utf-8')
for name in ['check_review_output.py','check_review_runner.py']:
 s=(O/'tools'/name).read_text().replace('input-sink05','media3-container01').replace('D1_INPUT_SINK05','D1_MEDIA3_CONTAINER01').replace('local-005','local-006').replace('FinalLocal005','FinalLocal006')
 if name=='check_review_runner.py':s=s.replace('==50','==56').replace("'positiveOriginalReturnedRuns':50","'positiveOriginalReturnedRuns':56")
 (B/'tools'/name).write_text(s,encoding='utf-8')
for name in ['D1_INPUT_SINK01_PHASE_B_REVIEW_REPORT_V1.0.md','official-added-dependencies','apache-license-source']:
 p=O/'reference'/name
 if p.is_dir():shutil.copytree(p,B/'reference'/name)
 elif p.is_file():shutil.copyfile(p,B/'reference'/name)
for name in ['D1_MEDIA3_CONTAINER01_CODER_REQUIREMENTS_V1.0.md','D1_MEDIA3_CONTAINER01_TESTER_REQUIREMENTS_V1.0.md']:shutil.copyfile(R/'docs/milestones'/name,B/'reference'/name)
report=R/'docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_REPORT_V1.0.md';assert hashlib.sha256(report.read_bytes()).hexdigest()=='edb4cd48b9bd1c04f0d1f9ddff5f80a6a16257e0055a7aa4c3eb000a303870d7';shutil.copyfile(report,B/'reference'/report.name)
cases=json.loads((R/'docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/independent-cases.json').read_text());shutil.copyfile(R/'docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/independent-cases.json',B/'reference/stage-a-independent-cases.json')
mapping={
 'MC01':('SOURCE_ADMITTED_STRICT_CONSUMED_INDEPENDENT_PENDING','evidence/extractor-source-admission.json; evidence/dependency-license-difference.json; evidence/actual-consumption','Exact same version and actual class origins; independent new-use admission not self-issued.'),
 'MC02':('FIXTURE_GAP','reference/approved-sample-scope.json','Original attributed read-only file hash verified. No new encoded fixture/tool admitted or executed.'),
 'MC03':('FIXTURE_MISMATCH_NOT_RUN','reference/approved-sample-scope.json','320x180 + audio +8s does not qualify. No adaptation or fabricated NAL.'),
 'MC04':('PARTIAL_ACTUAL','extractor-input M05; baseline core S05_CAP','MP4 capability/scope/seek bounds rejected before source open; baseline grants preserved; real muxer capability positive NOT_RUN.'),
 'MC05':('NOT_RUN_PLATFORM','platform-availability','Mp4Extractor constructor fails at missing android/content/pm/PackageManager$NameNotFoundException; no track/sample parse observed.'),
 'MC06':('NOT_RUN_PLATFORM','platform-availability','FragmentedMp4Extractor fails at android/os/Parcelable; no fragmented parse observed.'),
 'MC07':('PARTIAL_ACTUAL_NOT_MP4_PARSE','extractor-input M01','REAL DefaultExtractorInput +DataSource/readAt 3+3+1; qualified MP4 short-read result NOT_RUN.'),
 'MC08':('PARTIAL_ACTUAL_NOT_MP4_PARSE','approved-read; extractor-input M02','Original349102B fullEOF/hash known and unknown; real DefaultExtractorInput; unknown-length MP4 parse NOT_RUN.'),
 'MC09':('NOT_RUN_PLATFORM','src/com/videokit/d1input/HostMp4Inspection.java','sniff/reset wired only; real sniff/peek parse not executed.'),
 'MC10':('PARTIAL_ACTUAL_NOT_SEEKMAP','extractor-input M03','Actual absolute5, remaining2 -> streamLength7; no actual SeekMap/RESULT_SEEK observation.'),
 'MC11':('ACTUAL_READING_BOUNDARY_ONLY','extractor-input M03/M05; baseline core I03/I04','Long overflow rejected before host; sparse3GiB+7 bounded read preserved. Not malformed parser allocation proof.'),
 'MC12':('NOT_RUN_MP4_MALFORMED','extractor-input M02/M06','Raw readFully truncation and platform failure cannot READY tested; malformed atoms/sample-size parser behavior NOT_RUN; internal Media3 allocation bounds unproved.'),
 'MC13':('PARTIAL_ACTUAL_REUSED_SOURCE_BOUNDARY','input suite; core I05/I06','Real DataSource host-count/redaction tests retained; same faults during MP4 parse NOT_RUN.'),
 'MC14':('PARTIAL_ACTUAL','extractor-input M04; latecancel suite','Real DefaultExtractorInput cancelled while original read/close late; exact original caller/bridge workers joined; MP4 parser lifecycle NOT_RUN.'),
 'MC15':('ACTUAL_REUSED_BOUNDARY','core I12; original17','Original pending/FAILED close gates unchanged; explicit same known-failed retry only. No extractor-release proof substituted.'),
 'MC16':('PARTIAL_ACTUAL','approved-read; src/com/videokit/d1input/HostMp4Inspection.java','Real full raw EOF349102/hash separately observed; parser end/trailing atom policy unexecuted. Host result is structural only and makes no trailing semantic/decode guarantee.'),
 'MC17':('NOT_RUN_REAL_MUXER','baseline unchanged MatureMuxerBinding; new MatureContainerRemux','Exact track/CSD preconditions wired, runtime blocked before track construction.'),
 'MC18':('NOT_RUN_GENUINE_MUX_SAMPLES','baseline unchanged MatureMuxerBinding','No qualified compressed sample; no claimed positive sample/ByteBuffer forwarding.'),
 'MC19':('NOT_RUN_LEGAL_FINISH','unchanged upstream E6Muxer; reference phase-A report','StageA five invalid gates inherited, not newly counted. Exactly6 payload +0B flags4 EOS=last+200000 declared. No positive finalize evidence.'),
 'MC20':('NOT_RUN_TIMING','unchanged E6Muxer; interface decisions','PTS integers in microseconds, conservative exact re-extracted PTS; max payloadPTS2s may yield EOS2.2s. Final duration/timescale and rounding unverified.'),
 'MC21':('NOT_RUN_CODED_ORACLE','src/com/videokit/d1input/MatureContainerRemux.java','Expected same-library AnnexB output, exact ordered CSD arrays and access-unit hashes; no undeclared prefix/timing normalization. Needs qualified fixture to validate rule.'),
 'MC22':('NOT_RUN_PLATFORM_AND_FIXTURE','platform-availability; reference/approved-sample-scope.json','Actual library constructor failed SparseArray, no encoded fixture qualifies; no real muxed payload emitted.'),
 'MC23':('PARTIAL_ACTUAL_REUSED_SINK_BOUNDARY','core S01; independent-host; matrix','Retained partial physical/ACK/caller/UNKNOWN guards; actual muxer encountering partial fault NOT_RUN.'),
 'MC24':('PARTIAL_ACTUAL','core I07/I10/S02; extractor-input; source-differences','8MiB cumulative reader budget incl hash/replays,16MiB output,64KiB blocks, source2/inflight1/queue0; no proof of parser internal allocation bounds.'),
 'MC25':('ACTUAL_REUSED_SINK_BOUNDARY','core S03/S04; original17; matrix; cancel-CLOSE/FLUSH','Same original stages/tails retained; no automatic blind retries; no Android fsync claim.'),
 'MC26':('ACTUAL_REUSED_GATE_NEW_FAILURE_PATH','original17; extractor-input M06','Writer actual-return gate reused before grant reopen; platform failure closes its same factory and joins. Real muxed readback NOT_RUN.'),
 'MC27':('NOT_RUN_REAL_STRUCTURE','src/com/videokit/d1input/TemporaryOutput.java; MatureContainerRemux.java','Typed distinct host result wired; no successful real remux/structure/CSD/duration evidence.'),
 'MC28':('PARTIAL_ACTUAL_FAILURE_ONLY','extractor-input M06; core S03/S04','Platform/structure failure cannot READY and originals return. Real media hash/track/sample/timing negative cases NOT_RUN.'),
 'MC29':('PARTIAL_ACTUAL_REUSED_SOURCE_BOUNDARY','core I07/I10; source-differences','Original source2/per-source1/queue0 unchanged; simultaneous real parser/readback NOT_RUN.'),
 'MC30':('ACTUAL_REUSED_05_BOUNDARIES','original-responses; orders; coordinator-orders; independent-host','Same response, observer and actual SDK thread gates replayed source and production JAR first; zero counter not proof.'),
 'MC31':('ACTUAL_FAILURE_AND_SOURCE_AUDIT_NO_SUCCESS_CLAIM','extractor-input M06; source-differences','New kind HOST_MEDIA3_MP4_STRUCTURE_V1, no signer/READY/COMMIT call from new flow; successful host parse NOT_RUN. Legacy controlled validators remain explicitly synthetic boundary tests.'),
 'MC32':('NOT_RUN','platform-availability; artifact-audit','No Android FD/fsync/codec, device, isolated slot/death/content/timeline, real business commit or playback. No new authority.')}
for row in cases['cases']:
 status,evidence,note=mapping[row['id']];row.update(coderStatus=status,coderEvidence=evidence,coderNote=note)
cases.update(phase='CODER_SELF_CHECK_MAPPING_NOT_PHASE_B',newCandidateTested=True,status='LIMITED_READ_PROGRESS_WITH_PLATFORM_AND_FIXTURE_GAPS',independentVerdict='PENDING');(B/'completion-matrix.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf-8')
bom=json.loads((O/'input-sink05-sbom.cdx.json').read_text());bom['metadata']['component'].update(name='VideoKit D1 MEDIA3_CONTAINER01 compile probe',version='D1-20261021-MEDIA3-CONTAINER01')
for row in json.loads((B/'evidence/extractor-source-admission.json').read_text())['records']:
 name=row['coordinate'].split(':')[1];bom['components'].append({'type':'library','group':'androidx.media3','name':name,'version':'1.9.3','purl':'pkg:maven/androidx.media3/'+name+'@1.9.3','hashes':[{'alg':'SHA-256','content':row['aarSha256']}],'licenses':[{'expression':'Apache-2.0'}],'properties':[{'name':'identitySource','value':'Official fixed POM/module and original strict binary pins; new-use independent admission PENDING'}]})
(B/'media3-container01-sbom.cdx.json').write_text(json.dumps(bom,indent=2),encoding='utf-8')
print('Stage-A32 cases mapped; inherited admission evidence and updated SBOM preserved; review tools prepared.')
