from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'docs/coder/d1android02-capture-ready02-fix';B=R/'docs/coder/d1android02-capture-ready03-fix'
assert not B.exists();B.mkdir()
for d in ['tools','selfchecks','reference','evidence','release']:(B/d).mkdir()
for rel in ['tools/outer_owner.py','tools/strict-receipt.ps1.txt','selfchecks/capture_fixture.py','selfchecks/run_checks.py','reference/exact-seven-role-plan.json','reference/legacy-tool-route-contract.json','reference/local-policy-counterexample-NOT-ANDROID.txt','reference/original-outer-owner-contract.md','release/capture-policy.json','release/activation-required.template.json']:
 data=(O/rel).read_bytes()
 if rel.endswith(('.py','.md')):data=data.decode('utf-8').replace('d1android02-capture-ready02-fix','d1android02-capture-ready03-fix').replace('D1_ANDROID02_CAPTURE_READY02_FIX_REVIEW_EVIDENCE','D1_ANDROID02_CAPTURE_READY03_FIX_REVIEW_EVIDENCE').encode()
 (B/rel).write_bytes(data)
(B/'reference/ready02-entry.ps1').write_bytes((O/'tools/capture_android02.ps1').read_bytes())
(B/'reference/ready02-outer-owner.py').write_bytes((O/'tools/outer_owner.py').read_bytes())
for p in [R/'docs/milestones/D1_ANDROID02_CAPTURE_READY03_FIX_CODER_REQUIREMENTS_V1.0.md',R/'docs/tester/D1_ANDROID02_CAPTURE_READY02_FIX_PHASE_B_REVIEW_REPORT_V1.0.md']:(B/'reference'/p.name).write_bytes(p.read_bytes())
print(str(B))
