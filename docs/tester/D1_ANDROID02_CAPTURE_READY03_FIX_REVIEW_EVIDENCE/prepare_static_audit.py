from pathlib import Path
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent
s=(R/'docs/tester/D1_ANDROID02_CAPTURE_READY02_FIX_REVIEW_EVIDENCE/independent_static_audit.py').read_text()
for a,b in [
 ("B=R/'docs/coder/d1android02-capture-ready02-fix'","B=R/'docs/coder/d1android02-capture-ready03-fix'"),
 ("old=R/'docs/coder/d1android02-capture-ready01'","old=R/'docs/coder/d1android02-capture-ready02-fix'"),
 ('ready02-fix-freeze.json','ready03-fix-freeze.json'),
 ('c5ec7bafa461bc6e99ed2790248c67edce92cf11cd4a3e33c72fed54f5b82b1e','e8750063bec93dec4dcad090b3dabab637816bcb6dea8d57f98302fdf2356b11'),
 ('len(rows)==364','len(rows)==225'),
 ('D1_ANDROID02_CAPTURE_READY02_FIX-source.zip','D1_ANDROID02_CAPTURE_READY03_FIX-source.zip'),
 ('929ae193f2cf385c911b0cb4e82e4b99aeacf6e76f819fe2107ef0303e1adb9e','bf53714ace7473a2dcb60005b7e906ee60692acb1f64a05b75d1b6dc8cf6b69f'),
 ('==365','==226'),('PASS_FROZEN364_ZIP365','PASS_FROZEN225_ZIP226'),('independent364/ZIP365','independent225/ZIP226')]:s=s.replace(a,b)
p=E/'independent_static_audit.py';assert not p.exists();p.write_text(s,encoding='utf-8')
