"""Static derivation only. Never import/execute candidate modules."""
from pathlib import Path
import json,hashlib,ast,difflib
B=Path(__file__).resolve().parent
OLD=B.parent/'d1android02-global-idle-contract03-fix'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
oldseal=json.loads((OLD/'reference/runner-source-seal.json').read_bytes())
assert sha((OLD/'reference/runner-source-seal.json').read_bytes())=='4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93'
extras=['release/capture-policy.json','selfchecks/fixture_inputs.py','selfchecks/contract_cases.py','selfchecks/contract03_cases.py','selfchecks/independent_cases_original.py','selfchecks/review_semantics.ps1','selfchecks/prestart_lifetimes.ps1']
for rel in list(oldseal['sources'])+extras:
 if rel=='reference/gate-sources.json':continue
 src=OLD/rel;raw=src.read_bytes()
 if rel in oldseal['sources']:assert sha(raw)==oldseal['sources'][rel],rel
 dst=B/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():dst.write_bytes(raw)
for rel in ('tools/capture_android02.ps1','tools/entry_gates.py'):
 p=B/rel;s=p.read_text();s=s.replace('D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE','D1_READONLY_FACTS_PREAUTH01_REVIEW_EVIDENCE');p.write_text(s,encoding='utf-8',newline='\n')
# Keep the legacy validator, split only the common process body from authorization.
p=B/'tools/fact_collector.py';s=p.read_text()
if 'def _capture_authorized(' not in s:
 start=s.index('  if any(k in os.environ for k in ENV):')
 end=s.index(' def finish_after_original_collect_return',start)
 body=s[start:end]
 oldreturn=body.index('  return dict(schema=')
 body=body[:oldreturn]+"  receipt=dict(schema='GLOBAL_IDLE_FACT_CAPTURE_V1',scope=gate.scope,mode=mode,sourceSha256=source_sha,planSha256=plan_sha,routeProofSha256=route_sha,initialProofSha256=gate.proof_hash,hostEnvironment='INHERITED_SEVEN_OVERRIDES_ABSENT',rawSha256=sha(raw),rawBytes=len(raw),stdoutBytes=self.counts[0],stderrBytes=self.counts[1],hostElapsedSeconds=self.elapsed,collectedAtUtc=self.startedUtc,originalBodyReturned=True,outerControllerReturnStillRequired=True,facts=parsed)\n  receipt.update(authorization);return receipt\n"
 replacement="  return self._capture_authorized(gate,fixture_argv,authority['mode'],hi,authority['collectorSha256'],authority['planSha256'],authority['routeProofSha256'],dict(authoritySha256=approved_authority_sha256,approvalSha256=approved_approval_sha256))\n def _capture_authorized(self,gate,fixture_argv,mode,hi,source_sha,plan_sha,route_sha,authorization):\n  # Shared original capture, never manufacture legacy authority/approval.\n  if self.entered:raise ValueError('FACT_ONCE')\n"+body
 s=s[:start]+replacement+s[end:]
 # Every source verification in either branch uses the original bounded ledger.
 s=s.replace("sha(Path(__file__).read_bytes())","sha(gate.source_read(Path(__file__)))").replace("sha((B/'reference/fact-plan.json').read_bytes())","sha(gate.source_read(B/'reference/fact-plan.json'))").replace("sha(Path(SDK).read_bytes())","sha(gate.source_read(SDK))")
 p.write_text(s,encoding='utf-8',newline='\n')
new=['tools/fact_preauth.py','tools/facts_entry.py','reference/fact-preauth-schema.json']
p=B/'tools/admission_checks.ps1';s=p.read_text();s=__import__('re').sub(r"(\$script:GICollectorSha256=')[0-9a-f]{64}(')",lambda m:m[1]+sha((B/'tools/fact_collector.py').read_bytes())+m[2],s);p.write_text(s,encoding='utf-8',newline='\n')
p=B/'tools/production_runner.py';s=p.read_text();needle="'selfchecks/fact_fixture.py')"
if needle in s:s=s.replace(needle,"'selfchecks/fact_fixture.py',"+','.join(repr(x) for x in new)+")")
p.write_text(s,encoding='utf-8',newline='\n')
for p in (B/'tools').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
g=json.loads((OLD/'reference/gate-sources.json').read_bytes());g['files'] += [dict(path=x) for x in new]
for r in g['files']:r['sha256']=sha((B/r['path']).read_bytes())
put(B/'reference/gate-sources.json',g)
sources={x:sha((B/x).read_bytes()) for x in list(oldseal['sources'])+new}
put(B/'reference/runner-source-seal.json',dict(schema='PRODUCTION_RUNNER_SOURCE_SEAL_V1',sources=sources))
p=B/'release/capture-policy.json';d=json.loads(p.read_bytes())
for key,rel in [('entrySha256','tools/capture_android02.ps1'),('outerOwnerSha256','tools/outer_owner.py'),('gateSourcesSha256','reference/gate-sources.json'),('runnerSourceSha256','tools/production_runner.py')]:d[key]=sources[rel]
put(p,d)
delta=[];patch=[]
for rel in sources:
 a=(OLD/rel).read_bytes() if (OLD/rel).exists() else b'';b=(B/rel).read_bytes()
 if a!=b:
  delta.append(dict(path=rel,oldSha256=sha(a) if a else None,newSha256=sha(b)))
  if rel.endswith(('.py','.ps1','.json')):patch.extend(difflib.unified_diff(a.decode().splitlines(True),b.decode().splitlines(True),fromfile='CONTRACT03/'+rel,tofile='PREAUTH01/'+rel))
put(B/'reference/source-delta.json',delta);(B/'reference/source-delta.patch').write_text(''.join(patch),encoding='utf-8')
put(B/'reference/upstream.json',dict(sourceSeal='4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93',oldSources=oldseal['sources']))
print(json.dumps(dict(sources=len(sources),gate=len(g['files']),sourceSeal=sha((B/'reference/runner-source-seal.json').read_bytes()))))
