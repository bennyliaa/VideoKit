from pathlib import Path
import json,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];O=R/'docs/coder/d1media3-container02';assert not (B/'evidence/media3-android01-freeze.json').exists()
for name in ['review_all.py','run_suites.py']:
 p=B/'tools'/name;s=p.read_text();marker="for mode,cp in [('source',source),('production',prod)]:" if name=='review_all.py' else 'for name,cls,extra in plan:'
 assert marker in s;s=s.replace(marker,"plan += [('android-ready-host','AndroidReadyCheck',[str(D),str(project/fixture['path'])])]\n"+marker);p.write_text(s,encoding='utf-8')
for name in ['check_review_output.py','check_review_runner.py']:
 s=(O/'tools'/name).read_text().replace('media3-container02','media3-android01').replace('D1_MEDIA3_CONTAINER02','D1_MEDIA3_ANDROID01').replace('==60','==62').replace("'positiveOriginalReturnedRuns':60","'positiveOriginalReturnedRuns':62")
 (B/'tools'/name).write_text(s,encoding='utf-8')
shutil.copyfile(O/'media3-container02-sbom.cdx.json',B/'media3-android01-sbom.cdx.json')
print('Read-only review root ANDROID01;62-process full entry, existing8-per-tool path gates; one new6-group actual host helper suite.')
