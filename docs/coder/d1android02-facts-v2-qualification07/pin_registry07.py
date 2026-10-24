"""All named producer consumers and every explicit counter-change site."""
from pathlib import Path
import sys,json,re,hashlib,ast
R=Path(__file__).resolve().parent;H=R/(sys.argv[1].lower() if len(sys.argv)>1 else 'rev1');sys.path[:0]=[str(H/'tools')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
rows=[]
def check(n,ok,detail=None):rows.append(dict(id=n,pass_=bool(ok),detail=detail));assert ok,n
src=load(H/'reference/runner-source-seal.json')['sources'];g=load(H/'reference/gate-sources.json')['files']
check('source30-all-bytes',len(src)==30 and all(sha(H/n)==v for n,v in src.items()))
check('gate22-all-bytes',len(g)==22 and all(sha(H/e['path'])==e['sha256'] for e in g))
a=(H/'tools/admission_checks.ps1').read_text();c=(H/'tools/capture_android02.ps1').read_text();o=(H/'tools/outer_owner.py').read_text();eg=(H/'tools/entry_gates.py').read_text()
for symbol,rel in dict(GICollectorSha256='tools/fact_collector.py',GIFactPlanSha256='reference/fact-plan.json',GIV2AdapterSha256='tools/facts_qualification.py',GIV2CaptureSha256='tools/outer_capture.py',GIV2OriginSha256='tools/capture_origin.py').items():
 value=re.search(r"\$script:"+symbol+r"='([0-9a-f]{64})'",a).group(1);check('PS-symbol:'+symbol,value==sha(H/rel),dict(source=rel,value=value))
for name,text,rel,count in [('Owner-Runner',o,'tools/production_runner.py',1),('PS-Runner',a,'tools/production_runner.py',2),('entry-Owner',c,'tools/outer_owner.py',5),('entry-admission',c,'tools/admission_checks.ps1',1)]:check(name,text.count(sha(H/rel))==count,dict(source=rel,occurrences=count))
for name,text in [('Owner-Gate',o),('entry-Gate',c)]:check(name,sha(H/'reference/gate-sources.json') in text)
from fact_preauth import load_pins,FACT_PREAUTH_SCHEMA07_RAW
pins=load_pins(lambda p:Path(p).read_bytes())
for k,rel in dict(sourceSealSha256='reference/runner-source-seal.json',gateSourcesSha256='reference/gate-sources.json',collectorSha256='tools/fact_collector.py',binderSha256='tools/fact_preauth.py',entrySha256='tools/facts_entry.py',runtimeIdentitySha256='reference/current-runtime-identity.json',factPlanSha256='reference/fact-plan.json',captureSha256='tools/capture_android02.ps1',ownerSha256='tools/outer_owner.py',rolePlanSha256='reference/exact-seven-role-plan.json').items():check('Python-load-pins:'+k,pins[k]==sha(H/rel),rel)
check('whole-schema-under-checked-producer',FACT_PREAUTH_SCHEMA07_RAW.encode()==(H/'reference/fact-preauth-schema.json').read_bytes())
helper='47f9d48af2d3106c6b04f67e079bd6b48b3befb4b0c25061f3a6508426e3c982';meta='2593ddab8ed0a7cee369c13a145817c4365ce1847f18e0d7167db453060e5d48'
check('fixed-runtime-helper',sha(H/'tools/runtime_binding.py')==helper and all(helper in x for x in (c,o,eg)))
check('fixed-runtime-identity',sha(H/'reference/current-runtime-identity.json')==meta and meta in c)
catalog=[]
allowed={('entry_gates.py','source_charge'):'CANONICAL_SOURCE_EVENT',('entry_gates.py','prepare'):'ORIGINAL_UNKNOWN_NATIVE_AMOUNT_RETENTION',('production_runner.py','read_file'):'RUNNER_PREOPEN_FEE_EVENT',('production_runner.py','read_receipt'):'ORIGINAL_RECEIPT_PREOPEN_FEE_EVENT',('source_budget.py','reserve'):'ORIGINAL_DUAL_PERMANENT_TICKET_EVENT',('source_budget.py','probe'):'BOUNDED_GATE64_RUNNER_FEE_PROBE',('source_budget.py','work'):'BOUNDED_GATE64_PROBE_ORIGINAL_WORKER',('fact_preauth.py','read'):'PREAUTH_ORIGINAL_READ_AND_EVENT'}
allowed[('source_budget.py','fixture_probe')]='BOUNDED_GATE64_RUNNER_FEE_PROBE'
for f in (H/'tools').glob('*.py'):
 tree=ast.parse(f.read_text());parents={child:parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
 for n in ast.walk(tree):
  if not isinstance(n,ast.AugAssign) or not isinstance(n.target,ast.Attribute) or n.target.attr not in ('source_bytes','source_reads','source_reserved_unknown','sourceBytes','sourceReads'):continue
  p=n;fn=None
  while p in parents:
   p=parents[p]
   if isinstance(p,(ast.FunctionDef,ast.AsyncFunctionDef)):fn=p.name;break
  key=(f.name,fn);check('explicit-charge-site:'+f.name+':'+str(n.lineno),key in allowed,dict(function=fn,field=n.target.attr))
  catalog.append(dict(path=f.relative_to(H).as_posix(),line=n.lineno,function=fn,field=n.target.attr,classification=allowed[key]))
fc=(H/'tools/fact_collector.py').read_text();check('raw-child-only-unified-charge',"gate.source_charge(argv[7],len(raw),'child-reservation')" in fc and 'gate.source_bytes+=len(raw)' not in fc)
check('route-child-explicit-read-kept',"Path(__file__).read_bytes()" in (H/'selfchecks/route_fixture.py').read_text())
check('route-child-reserved-before-Popen',eg.index("self.source_charge(script,script.stat().st_size,'route-child-reservation')")<eg.index("r=self.original('checker-start'"))
check('complete-rows-before-compare',(H/'tools/facts_entry.py').read_text().index("name='fact-source-ledger-")<(H/'tools/facts_entry.py').read_text().index("raise ValueError('FACT_COMPLETE_SOURCE_PLAN_ACTUAL_MISMATCH')"))
check('all-builder-patches-counted',load(H/'reference/build-patch-audit07.json')['allExactCounts'])
out=dict(allPassed=True,checks=rows,counterSites=catalog,controlChildRead=dict(path='selfchecks/route_fixture.py',expression="Path(sys.argv[1]).read_bytes()",originalLane='Gate control checker-context-read, separate from source self-hash',count=1),batchOnlyReadReservation=dict(ownerRuntimeHelper='Exact fixed helper metadata two reads +14 files on each original runtime_checks call, bounded in driverAndModels 256MiB; not reclassified as Gate source reads',controllerRuntime='Original fixed PS metadata/file hashes, bounded in driverAndModels; physicalIO not claimed'),SDK=0,productResources=0)
(H/'evidence').mkdir(exist_ok=True);(H/'evidence/pin-and-fee-registry07.json').write_bytes((json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(namedAndFeeChecks=len(rows),counterSites=len(catalog),allPassed=True)))
