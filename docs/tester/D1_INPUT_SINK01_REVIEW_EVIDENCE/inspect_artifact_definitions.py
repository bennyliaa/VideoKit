from pathlib import Path
import ast,struct,zipfile,json
E=Path(__file__).resolve().parent;B=Path('D:/CodexProjects/VideoKit/docs/coder/d1input-sink01')
tree=ast.parse((E/'audit_frozen.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pool','axml','dexclasses']]
exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen_parser','exec'))
with zipfile.ZipFile(B/'artifacts/input-sink01-compile-probe-debug.apk') as z:
 classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))]
 tags=axml(z.read('AndroidManifest.xml'))
 print(json.dumps(dict(androidDefinitions=[c for c in classes if c.startswith('Landroid/')],hostFixtureDefinitions=[c for c in classes if 'HostFixtures' in c],manifest=tags),ensure_ascii=False,indent=2))
