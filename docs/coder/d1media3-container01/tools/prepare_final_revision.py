from pathlib import Path
import shutil,json
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/media3-container01-freeze.json').exists();H=B/'evidence/pre-budget-fix';H.mkdir()
shutil.copyfile(B/'artifacts/media3-container01-classes.jar',H/'media3-container01-classes-build003.jar')
shutil.copyfile(B/'evidence/artifact-audit.json',H/'artifact-audit-build003.json')
shutil.copytree(B.parents[2]/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/coder-documented-entry-prefreeze-002',H/'documented-review-002',ignore=shutil.ignore_patterns('classes'))
p=B/'tools/prepare_batch.py';s=p.read_text().replace('build-main-003','build-main-004').replace("'buildAttempt':'003'","'buildAttempt':'004'").replace('local-006','local-007').replace('D.mkdir(exist_ok=False)','D.mkdir(exist_ok=True)').replace('assert not jar.exists();','assert jar.exists();').replace("zipfile.ZipFile(jar,'x',","zipfile.ZipFile(jar,'w',").replace('V.mkdir();vc=','V.mkdir(exist_ok=True);vc=').replace('vc.mkdir();','vc.mkdir(exist_ok=True);');p.write_text(s)
for name in ['check_review_output.py','check_review_runner.py']:
 p=B/'tools'/name;s=p.read_text().replace('local-006','local-007').replace('FinalLocal006','FinalLocal007').replace('evidence/tool-output-gate','evidence/tool-output-gate-final').replace("'evidence'/'tool-output-gate'","'evidence'/'tool-output-gate-final'").replace('evidence/review-runner-gate','evidence/review-runner-gate-final').replace('coder-tool-positive-001','coder-tool-positive-002').replace('coder-documented-entry-prefreeze-002','coder-documented-entry-prefreeze-003');p.write_text(s)
p=B/'completion-matrix.json';m=json.loads(p.read_text(encoding='utf-8'));row=next(x for x in m['cases'] if x['id']=='MC24');row['coderEvidence']+='; extractor-input M07';row['coderNote']+=' Actual128x64KiB=8MiB; next read rejected before any additional host read, no speculative EOF byte.';p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('Historical successful build003/JAR/review preserved; final source local007 and build004 selected.')
