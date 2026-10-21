from pathlib import Path
import ast,datetime,hashlib,json,struct,zipfile
from review_materials import B,R,E,S,MAIN,ZIP,selected,sha,read,inputs
assert not S.exists() and not ZIP.exists()
parser=R/'docs/coder/d1fixture-tool02/tools/audit_build.py';tree=ast.parse(parser.read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='class_origin'];assert len(nodes)==1;exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen_pure_class_origin_parser','exec'))
source={}
for x in read(E/'nonmedia-001/source-pins.json'):
 p=B/x['path'];text=p.read_text();import re
 m=re.search(r'package\s+([\w.]+)\s*;',text);key=(m.group(1).replace('.','/')+'/' if m else '')+p.name;assert key not in source;source[key]=x
rows=[]
for p in sorted((E/'nonmedia-001/classes').rglob('*.class')):
 name,file,major=class_origin(p.read_bytes());key=(name.rsplit('/',1)[0]+'/' if '/' in name else '')+file;assert key in source
 x=source[key];rows.append({'class':p.relative_to(B).as_posix(),'sha256':sha(p),'name':name,'major':major,'source':x['path'],'sourceSha256':x['sha256']})
(E/'nonmedia-class-origins.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
(E/'class-parser-origin.json').write_text(json.dumps({'path':str(parser),'sha256':sha(parser),'function':'class_origin','execution':'pure Python function only, no legacy top-level'},indent=2)+'\n',encoding='utf-8')
result=inputs();paths=selected();files=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in paths:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None and len(z.namelist())==len(files)
 for x in files:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
archive={'path':ZIP.relative_to(R).as_posix(),'bytes':ZIP.stat().st_size,'sha256':sha(ZIP)}
seal={'frozenUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_COMPLETE_BLOCKED_BATCH_NO_ANDROID02_ARTIFACTS','files':files,'archive':archive,'validation':result,'excludedMutableBuildInfrastructure':['.gradle','build','app/build','build-tools-gradle-home','offline-maven'],'excludedInfrastructureNote':'No successful build; original failed client and daemon-log snapshot retained. Mirror/caches not candidate outputs. No process return inferred from exclusion.'}
S.write_text(json.dumps(seal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'seal':str(S),'sealSha256':sha(S),'files':len(files),'archive':archive,'totalSelectedBytes':sum(x['bytes'] for x in files),'validation':result},ensure_ascii=False))
