from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
s=(R/'docs/coder/d1media3-android02-recovery01/tools/prepare_artifacts.py').read_text()
s=s.replace("O=R/'docs/coder/d1media3-android02'","O=R/'docs/coder/d1media3-android02-recovery01'")
s=s.replace("E/'recovery01-freeze.json'","E/'fix02-freeze.json'").replace("for n in ['001','002']:","for n in ['001']:").replace('build-002/','build-001/').replace("'finalBuild':'002'","'finalBuild':'001'")
s=s.replace('media3-android02-recovery01-','media3-android02-fix02-').replace('D1-MEDIA3-ANDROID02-RECOVERY01','D1-MEDIA3-ANDROID02-FIX02')
(B/'tools/prepare_artifacts.py').write_text(s,encoding='utf-8')
print('FIX02 artifact/source/DEX/strict300 audit configured from frozen audited Python parser workflow')
