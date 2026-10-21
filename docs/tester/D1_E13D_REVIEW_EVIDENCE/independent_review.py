"""Tester-owned offline byte/source audit; never executes candidate tooling."""
from pathlib import Path
import hashlib,json,zipfile,datetime
R=Path('D:/CodexProjects/VideoKit'); E=R/'docs/tester/D1_E13D_REVIEW_EVIDENCE'
checks=[]; before={}
def raw(path):
 p=Path(path); p=p if p.is_absolute() else R/p
 b=p.read_bytes(); before.setdefault(p.as_posix(),hashlib.sha256(b).hexdigest()); return b
def test(name,ok):
 checks.append({'id':name,'pass':bool(ok)})
 if not ok: raise AssertionError(name)
def obj(path): return json.loads(raw(path).decode('utf-8-sig'))
def pin(row):
 b=raw(row['path']);test('bytes:'+row['path'],len(b)==row['bytes']);test('sha:'+row['path'],hashlib.sha256(b).hexdigest()==row['sha256'])
sealpath='docs/coder/d1e13d/evidence/e13d-freeze.json'
test('E13D external seal',hashlib.sha256(raw(sealpath)).hexdigest()=='acc83e5aff9288099c1f324fb24394316dedfd83272cce66cd8299a215b66365')
s=obj(sealpath);test('nine unique rows',len(s['immutableFiles'])==9==len({x['path'] for x in s['immutableFiles']}))
for row in s['immutableFiles']:pin(row)
test('ZIP expected SHA',s['archive']['sha256']=='dbe40dc80a4962b53f677fdc55d034b0d1b282529d6fb9a37109e25fd04d6385')
with zipfile.ZipFile(R/s['archive']['path']) as z:
 members={x['path']:x for x in s['immutableFiles'] if x['path']!=s['archive']['path']}
 test('eight exact ZIP members',len(z.namelist())==8 and len(set(z.namelist()))==8 and set(z.namelist())==set(members))
 test('ZIP CRC',z.testzip() is None)
 for name,row in members.items():
  b=z.read(name);test('ZIP bytes/hash:'+name,len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'])
inputs=obj('docs/coder/d1e13d/evidence/input-verification.json')
for row in inputs['reports']:pin(row)
manifest_counts=[]
for group in inputs['frozenManifests']:
 pin(group['manifest']); rows=obj(group['manifest']['path'])[group['rowKey']]
 test('input manifest count:'+group['manifest']['path'],len(rows)==group['rowsVerified'])
 for row in rows:pin(row)
 manifest_counts.append(len(rows))
source=obj('docs/coder/d1e13d/evidence/source-excerpts.json')
for item in source['sources']:
 pin(item['source']);lines=raw(item['source']['path']).decode('utf-8-sig').splitlines()
 for ex in item['excerpts']:
  expected='\n'.join(f'{i+1}: {lines[i]}' for i in range(ex['firstLine']-1,ex['lastLine']))
  test('source excerpt:'+item['source']['path']+':'+str(ex['firstLine']),expected==ex['text'])
deps=obj('docs/coder/d1e13d/evidence/cached-dependency-source-excerpts.json');pin(deps['versionAuthority'])
dependency_supplement=[]
for d in deps['dependencies']:
 pin(d['cachedArchive'])
 with zipfile.ZipFile(d['cachedArchive']['path']) as z:b=z.read(d['entry'])
 test('dependency entry SHA:'+d['entry'],len(b)==d['entryBytes'] and hashlib.sha256(b).hexdigest()==d['entrySha256'])
 lines=b.decode().splitlines()
 for ex in d['excerpts']:
  test('dependency excerpt:'+str(ex['firstLine'])+':'+d['entry'],ex['text']=='\n'.join(f'{i+1}: {lines[i]}' for i in range(ex['firstLine']-1,ex['lastLine'])))
 # Read the complete onException tail, not only the coder excerpt ending at 638.
 ranges=[(638,675)] if '/AndroidJUnitRunner' in d['entry'] else [(90,125),(391,458)]
 dependency_supplement.append({'entry':d['entry'],'ranges':[{'firstLine':a,'lastLine':b,'text':'\n'.join(f'{i+1}: {lines[i]}' for i in range(a-1,min(b,len(lines))))} for a,b in ranges]})
base=obj('docs/coder/d1e13a/evidence/e13a-freeze.json')
jars=[x for x in base['immutableFiles'] if x['path'].endswith('.jar') and 'host' in x['path'].lower()]
test('one base host jar',len(jars)==1)
basejar=jars[0]['path']; newjar='docs/coder/d1e13c/artifacts/e13c-host-tools.jar';raw(basejar);raw(newjar)
class_checks=[]
with zipfile.ZipFile(R/basejar) as a,zipfile.ZipFile(R/newjar) as b:
 for prefix in ['com/videokit/spike/e4/E13HostCase','com/videokit/spike/e4/E9PcSupervisor']:
  names=[n for n in a.namelist() if (n==prefix+'.class' or n.startswith(prefix+'$')) and n.endswith('.class')]
  test('nonempty class family:'+prefix,bool(names))
  for n in names:test('actual shipped JAR identity:'+n,a.read(n)==b.read(n));class_checks.append(n)
boundary=obj('docs/coder/d1e13d/evidence/observation-boundaries.json');pin(boundary['psRaw'])
lines=raw(boundary['psRaw']['path']).decode().splitlines()
for row in boundary['matchingLines']:test('original ps line:'+str(row['line']),lines[row['line']-1]==row['text'])
test('scope pin in ps',any('116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef' in x['text'] for x in boundary['matchingLines']))
# No execution of candidate self-check, compiler, Java, adb, STATUS or live-handle APIs.
E.mkdir(exist_ok=True,parents=True)
(E/'dependency-independent-supplement.json').write_text(json.dumps(dependency_supplement,ensure_ascii=False,indent=2),'utf-8')
snap=[{'path':p,'sha256':h} for p,h in sorted(before.items())]
(E/'reviewed-input-snapshot.json').write_text(json.dumps(snap,indent=2),'utf-8')
unchanged=all(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in snap)
test('all independent reviewed inputs unchanged',unchanged)
result={'status':'PASS_OFFLINE_EVIDENCE_AND_SOURCE_INTEGRITY','atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'checkCount':len(checks),'uniqueFilesRead':len(before),'oldManifestRowCounts':manifest_counts,'sourceFiles':len(source['sources']),'exactShippedClasses':class_checks,'candidateSelfChecksExecuted':0,'builds':0,'deviceCalls':0,'liveHandleQueries':0,'rootCause':'NOT_UNIQUELY_DETERMINED','productResult':'NOT_PASSED'}
(E/'independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','exactShippedClasses']}))
