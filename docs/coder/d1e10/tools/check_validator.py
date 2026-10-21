"""Only offline validator negative checks; no synthetic execution/actor/catalog generation."""
import ast,json,pathlib
import validate_package as v
checks=[]
def reject(name,f):
 try:f()
 except (v.Invalid,ValueError,TypeError,KeyError):checks.append(name);return
 raise AssertionError('ACCEPTED:'+name)
reject('duplicate JSON key',lambda:v.decode(b'{"a":1,"a":2}'))
reject('nonfinite JSON',lambda:v.decode(b'{"a":NaN}'))
reject('wire CRLF',lambda:v.canonical_bytes(b'{"e9":1,"fields":{"kind":"test"}}\r\n',4096))
reject('wire unordered fields',lambda:v.canonical_bytes(b'{"e9":1,"fields":{"z":"x","a":"y"}}\n',4096))
reject('wire boolean e9 header',lambda:v.canonical_bytes(b'{"e9":true,"fields":{"kind":"test"}}\n',4096))
reject('wire field injection',lambda:v.wire({'kind':'test"injection'}))
reject('path traversal',lambda:v.local(v.R,'../escape'))
reject('absolute path pin',lambda:v.local(v.R,str(v.B.resolve())))
p=v.B/'plan/descriptor.json';reject('modified content pin',lambda:v.pin(dict(path=p.relative_to(v.R).as_posix(),bytes=p.stat().st_size,sha256='0'*64)))
old=v.read(v.B/'plan/execution-plan.json')['historicalReadOnly'];reject('closed readonly IDs reused',lambda:v.identity({k:old[k] for k in ['registry','migration','attempt','handle']},old))
reject('unbound placeholder UUIDs',lambda:v.identity(dict(registry='REQUIRED_REGISTRY',migration='REQUIRED_MIGRATION',attempt='REQUIRED_ATTEMPT',handle='REQUIRED_HANDLE'),old))
reject('timestamp without zone',lambda:v.timestamp('2026-10-18T09:00:00'))
tree=ast.parse((v.B/'tools/validate_package.py').read_text());imports=[alias.name for n in ast.walk(tree) if isinstance(n,ast.Import) for alias in n.names]
assert not any(n in ['subprocess','socket','requests','urllib','shutil','os'] for n in imports)
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['write_bytes','write_text','mkdir','unlink','rename','uuid4','uuid1','system','spawn','connect','Popen'] for n in ast.walk(tree))
print(json.dumps(dict(status='PASS_OFFLINE_VALIDATOR_CHECKS',negativeCases=checks,negativeCount=len(checks),readonlySourceAudit=True,generatedActualIds=0,deviceCalls=0,productionTestsReexecuted=False),ensure_ascii=False))
