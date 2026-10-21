from pathlib import Path
import shutil,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];I=R/'docs/coder/d1e13i';assert not (B/'tools/E13JSocket.java').exists()
for d in ['artifacts','reference','evidence']: (B/d).mkdir(parents=True,exist_ok=True)
shutil.copyfile(I/'artifacts/e13f-reviewed-base.jar',B/'artifacts/e13f-reviewed-base.jar')
for d in ['protocol','protocol-excerpts']:shutil.copytree(I/'reference'/d,B/'reference'/d)
for name in ['E13IIdentity.java','E13IArchive.java','E13ISocket.java','E13IReadOnly.java','ICheck.java','IFixtures.java']:
 t=(I/'tools'/name).read_text().replace('E13I','E13J').replace('e13i','e13j');(B/'tools'/name.replace('E13I','E13J')).write_text(t,encoding='utf-8')
t=(I/'tools/observe_i_only.ps1').read_text().replace('E13I','E13J').replace('e13i','e13j').replace('I-only','J-only').replace('I_EXECUTION','J_EXECUTION');(B/'tools/observe_j_only.ps1').write_text(t,encoding='utf-8')
for rel in ['docs/tester/D1_E13I_FIXED_SOCKET_REVIEW_REPORT_V1.0.md','docs/coder/d1e13h/evidence/local-probe-environment-history.json']:shutil.copyfile(R/rel,B/'reference'/Path(rel).name)
print('Prepared separate J candidate; old I unchanged')
