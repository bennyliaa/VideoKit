"""Exact bundled-runtime preflight for this single capture candidate only."""
from pathlib import Path
import hashlib,json,sys,struct,time
IDENTITY_SHA256='2593ddab8ed0a7cee369c13a145817c4365ce1847f18e0d7167db453060e5d48'
PY=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require_runtime(policy,stage):
 meta=Path(__file__).resolve().parents[1]/'reference/current-runtime-identity.json'
 if not meta.is_file():raise ValueError('RUNTIME_METADATA_MISSING:'+stage)
 if policy.get('runtimeIdentitySha256')!=IDENTITY_SHA256:raise ValueError('RUNTIME_METADATA_POLICY_PIN_MISMATCH:'+stage)
 if sha(meta)!=IDENTITY_SHA256:raise ValueError('RUNTIME_METADATA_FILE_PIN_MISMATCH:'+stage)
 d=json.loads(meta.read_text(encoding='utf-8'));exe=next(x for x in d['files'] if x['kind']=='interpreter-executable')
 if policy.get('outerPythonSha256')!=exe['sha256']:raise ValueError('RUNTIME_POLICY_PYTHON_PIN_MISMATCH:'+stage+':expected='+str(policy.get('outerPythonSha256'))+':bound='+exe['sha256'])
 if Path(sys.executable).resolve()!=PY.resolve() or Path(d['executable']).resolve()!=PY.resolve():raise ValueError('RUNTIME_EXECUTABLE_PATH_MISMATCH:'+stage)
 if list(sys.version_info[:3])!=d['version'] or struct.calcsize('P')*8!=d['pointerBits'] or sys.platform!=d['platform'] or sys.implementation.name!=d['implementation'] or sys.implementation.cache_tag!=d['cacheTag']:raise ValueError('RUNTIME_VERSION_ARCH_IMPLEMENTATION_MISMATCH:'+stage)
 for pin in d['files']:
  path=Path(pin['path'])
  if not path.is_file():raise ValueError('RUNTIME_REQUIRED_FILE_MISSING:'+path.name+':'+stage)
  if path.stat().st_size!=pin['bytes'] or sha(path)!=pin['sha256']:raise ValueError('RUNTIME_FILE_PIN_MISMATCH:'+path.name+':'+stage)
 return {'stage':stage,'checkedAtMonotonic':time.monotonic(),'identitySha256':IDENTITY_SHA256,'pythonSha256':exe['sha256'],'version':d['version'],'pointerBits':d['pointerBits'],'filesChecked':len(d['files'])}
