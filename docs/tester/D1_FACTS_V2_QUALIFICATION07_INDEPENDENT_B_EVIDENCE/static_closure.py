from pathlib import Path
import json,ast,re,hashlib,collections
R=Path(__file__).resolve().parent;B=R.parents[1]/'coder/d1android02-facts-v2-qualification07/rev2'
load=lambda p:json.loads(Path(p).read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest()
seal=load(B/'reference/runner-source-seal.json')['sources'];gate=load(B/'reference/gate-sources.json')['files'];old=load(B/'reference/upstream05-pins.json')
checks=[]
def c(k,v):checks.append(dict(case=k,passed=bool(v)))
c('source30',len(seal)==30 and all(sha((B/n).read_bytes())==h for n,h in seal.items()));c('gate22',len(gate)==22 and all(sha((B/x['path']).read_bytes())==x['sha256'] for x in gate))
trees={f.relative_to(B).as_posix():ast.parse(f.read_text(encoding='utf-8-sig')) for f in (B/'tools').glob('*.py')}
t=trees['tools/production_runner.py'];sourceFiles=next(ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='SOURCE_FILES' for x in n.targets));ps=(B/'tools/admission_checks.ps1').read_text();keys=ast.literal_eval('['+re.search(r'\$srcKeys=@\(([^\n]+)\)',ps).group(1)+']');c('Runner-and-PS-source-set',set(sourceFiles)==set(keys)==set(seal))
policy=load(B/'release/capture-policy.json')
for k,n in {'entrySha256':'tools/capture_android02.ps1','outerOwnerSha256':'tools/outer_owner.py','gateSourcesSha256':'reference/gate-sources.json','runnerSourceSha256':'tools/production_runner.py','runtimeIdentitySha256':'reference/current-runtime-identity.json','runtimeBindingSourceSha256':'tools/runtime_binding.py','planSha256':'reference/exact-seven-role-plan.json'}.items():c(k,policy[k]==sha((B/n).read_bytes()))
hashmap=collections.defaultdict(set)
for n,h in {**old,**seal}.items():hashmap[h].add(n)
for n,h in old.items():hashmap[h].add(n)
literals=[]
for f in (B/'tools').glob('*'):
 if f.suffix not in ('.py','.ps1'):continue
 for i,line in enumerate(f.read_text(encoding='utf-8-sig').splitlines(),1):
  for h in re.findall(r'(?<![0-9a-f])[a-f0-9]{64}(?![0-9a-f])',line):
   for n in hashmap.get(h,[]):
    if (B/n).is_file():literals.append(dict(consumer=f.relative_to(B).as_posix(),line=i,producer=n,match=h==sha((B/n).read_bytes())))
c('all-identified-named-source-literals',all(x['match'] for x in literals))
budgetTree=trees['tools/source_budget.py'];shape=next(ast.literal_eval(n.value) for n in budgetTree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CAPACITY_SHAPES06' for x in n.targets));c('capacity-entire-shape-value',shape==load(B/'reference/control-message-shapes06.json'))
oldTree=ast.parse((R.parent/'D1_FACTS_V2_QUALIFICATION07_PHASE_A_EVIDENCE/sealed-code/tools/source_budget.py').read_text(encoding='utf-8-sig'))
for name in ('size','admit'):
 a=next(n for n in budgetTree.body if isinstance(n,ast.FunctionDef) and n.name==name);b=next(n for n in oldTree.body if isinstance(n,ast.FunctionDef) and n.name==name);c('capacity-full-AST-'+name,ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False))
mut=[]
for rel,t in trees.items():
 for n in ast.walk(t):
  if isinstance(n,ast.AugAssign) and isinstance(n.target,ast.Attribute) and n.target.attr in ('source_bytes','source_reads','source_reserved_unknown','sourceBytes','sourceReads'):
   mut.append(dict(file=rel,line=n.lineno,target=ast.unparse(n.target),expression=ast.unparse(n)))
# Final source-stage branch counts from the exact fixed graph, not new runs.
p=load(R/'fact-source-plan.json');stages=collections.defaultdict(lambda:dict(reads=0,bytes=0))
for x in p['rows']:stages[x['stage']]['reads']+=1;stages[x['stage']]['bytes']+=x['chargedBytes']
o=dict(allPassed=all(x['passed'] for x in checks),checks=checks,namedLiteralConsumers=literals,sourceMutations=mut,RAWActual=dict(reads=64,bytes=p['sourceBytes']),COMPLETEStatic=dict(reads=61,bytes=p['sourceBytes']-3*139264-1),LIVEStatic=dict(reads=58,notExecuted=True,includesOriginalRouteSelfRead=True),stages=dict(stages),productFunctionsCalled=0)
(R/'static-closure.json').write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(allPassed=o['allPassed'],checks=len(checks),literalConsumers=len(literals),mutations=len(mut),bad=[x for x in checks if not x['passed']])))
