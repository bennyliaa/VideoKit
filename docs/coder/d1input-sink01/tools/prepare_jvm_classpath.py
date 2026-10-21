from pathlib import Path
import json,hashlib,shutil,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parents[1];root=ET.parse(B/'gradle/verification-metadata.xml').getroot();pins={}
for a in root.iter():
 if a.tag.split('}')[-1]=='artifact':pins[a.get('name')]={h.get('value') for h in a if h.tag.split('}')[-1]=='sha256'}
rows=[]
for name in ['guava-33.3.1-android.jar','failureaccess-1.0.2.jar','listenablefuture-9999.0-empty-to-avoid-conflict-with-guava.jar']:
 files=list((B/'offline-maven').rglob(name));assert len(files)==1;src=files[0];h=hashlib.sha256(src.read_bytes()).hexdigest();assert h in pins[name];dst=B/'deps'/name;shutil.copyfile(src,dst);rows.append({'source':src.relative_to(B).as_posix(),'path':dst.relative_to(B).as_posix(),'sha256':h,'pinSource':'existing RENDER02 verification metadata','newDownloads':0})
(B/'evidence/jvm-transitive-classpath.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
