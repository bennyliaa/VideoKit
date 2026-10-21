from pathlib import Path
import shutil,json,hashlib
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1render02-capture';B.mkdir(exist_ok=True)
assert not (B/'evidence/source-provenance.json').exists()
for name in ['tools','release','reference','selfchecks','evidence']:(B/name).mkdir(exist_ok=True)
refs=['docs/milestones/D1_RENDER02_CAPTURE_ADAPT_CODER_REQUIREMENTS_V1.0.md','docs/milestones/D1_RENDER02_CAPTURE_ADAPT_TESTER_REQUIREMENTS_V1.0.md','docs/tester/D1_RENDER02_DEVICE_TEST_REPORT_V1.0.md','docs/tester/D1_RENDER02_DEVICE_EVIDENCE/exact-operation-and-accounting-plan.json','docs/tester/D1_RENDER02_DEVICE_EVIDENCE/capture-capability-audit.json','docs/coder/d1resume02-activation/tools/capture_metadata.ps1','docs/coder/d1resume02-release/tools/observe_original.ps1']
pins=[]
for name in refs:
 p=R/name;d=B/'reference'/p.name;shutil.copyfile(p,d);pins.append({'source':name,'copy':d.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(B/'evidence/source-provenance.json').write_text(json.dumps(pins,ensure_ascii=False,indent=2),encoding='utf-8')
assert hashlib.sha256((B/'reference/capture_metadata.ps1').read_bytes()).hexdigest()=='fef62cb2a2ddbca49e22b1f041e59387185323539945d86e06dd8823449e25fe'
print('NEW PREPARATION DIRECTORY ONLY; no SDK/media/product reads')
