from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=R/'docs/coder/d1android02-capture-ready01';B=R/'docs/coder/d1android02-capture-ready02-fix'
assert not B.exists();B.mkdir()
for d in ['tools','selfchecks','evidence','reference','release']:(B/d).mkdir()
for rel in ['tools/capture_android02.ps1','tools/semantic-gates.ps1.txt','reference/exact-seven-role-plan.json','reference/legacy-tool-route-contract.json','selfchecks/capture_fixture.py','release/capture-policy.json','release/activation-required.template.json']:
 (B/rel).write_bytes((O/rel).read_bytes())
for rel in ['docs/milestones/D1_ANDROID02_CAPTURE_READY02_FIX_CODER_REQUIREMENTS_V1.0.md','docs/tester/D1_ANDROID02_CAPTURE_READY01_PHASE_B_REVIEW_REPORT_V1.0.md']:(B/'reference'/Path(rel).name).write_bytes((R/rel).read_bytes())
(B/'reference/ready01-entry.ps1').write_bytes((O/'tools/capture_android02.ps1').read_bytes())
sample=R/'docs/tester/D1_ANDROID02_CAPTURE_READY01_REVIEW_EVIDENCE/fixtures/independent-001/semantic-owner/outputs/production-like-receipt.txt'
(B/'reference/local-policy-counterexample-NOT-ANDROID.txt').write_bytes(sample.read_bytes())
print(str(B))
