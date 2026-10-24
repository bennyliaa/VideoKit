from pathlib import Path
import ast,json,re,hashlib,collections,csv,io
R=Path(__file__).resolve().parent;B=R/'sealed-code'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads((B/p).read_bytes())
def save(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
seal=load('reference/runner-source-seal.json')['sources'];gate=load('reference/gate-sources.json')['files'];old=load('reference/upstream05-pins.json')
assert len(seal)==31 and len(gate)==23
for n,h in seal.items():assert sha((B/n).read_bytes())==h
for x in gate:assert sha((B/x['path']).read_bytes())==x['sha256']
hashmap=collections.defaultdict(set)
for n,h in seal.items():hashmap[h].add(n)
hashmap[sha((B/'reference/runner-source-seal.json').read_bytes())].add('reference/runner-source-seal.json')
for n,h in old.items():hashmap[h].add(n)
mut=[];reads=[];literals=[];patches=[];funcs=[]
for f in sorted(B.rglob('*')):
 if not f.is_file() or f.suffix not in ('.py','.ps1','.txt'):continue
 rel=f.relative_to(B).as_posix();s=f.read_text(encoding='utf-8-sig');lines=s.splitlines()
 if f.suffix=='.py':
  t=ast.parse(s)
  for n in ast.walk(t):
   if isinstance(n,(ast.Assign,ast.AnnAssign,ast.AugAssign)):
    text=ast.get_source_segment(s,n) or ''
    target=n.target if isinstance(n,(ast.AnnAssign,ast.AugAssign)) else n.targets
    targets=target if isinstance(target,list) else [target]
    if any(isinstance(x,ast.Attribute) and x.attr in ('source_bytes','source_reads','source_reserved_unknown','sourceBytes','sourceReads','sourceEvents','source_events') for x in targets):mut.append({'file':rel,'line':n.lineno,'operation':type(n).__name__,'text':text})
   if isinstance(n,ast.Call):
    fun=ast.unparse(n.func)
    if any(k in fun for k in ('read_bytes','read_text','source_read','source_charge','read_file','read_receipt')) or fun.endswith('.open'):reads.append({'file':rel,'line':n.lineno,'function':fun,'text':ast.get_source_segment(s,n)})
    if fun.endswith('.replace') and rel.split('/')[0] not in ('tools','selfchecks','driver'):patches.append({'file':rel,'line':n.lineno,'text':ast.get_source_segment(s,n)})
 for i,line in enumerate(lines,1):
  for h in re.findall(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])',line):
   matches=sorted(hashmap.get(h,[]));literals.append({'file':rel,'line':i,'literal':h,'candidateProducers':matches,'comparison':[{ 'producer':n,'currentSha256':sha((B/n).read_bytes()),'matchesCurrent':sha((B/n).read_bytes())==h} for n in matches if (B/n).is_file()],'text':line,'classification':'SOURCE_MATCH_CANDIDATE_NEEDS_NAMED_CONTEXT' if matches else 'EXTERNAL_OR_NON_SOURCE_HASH_DO_NOT_BLIND_REPLACE'})
 if f.suffix=='.ps1':
  starts=list(re.finditer(r'(?m)^function\s+([\w]+)[^\n]*',s))
  for j,m in enumerate(starts):
   segment=s[m.start():starts[j+1].start() if j+1<len(starts) else len(s)]
   funcs.append({'file':rel,'name':m.group(1),'line':s[:m.start()].count('\n')+1,'segment':segment})
save('all-source-mutations.json',mut);save('explicit-file-read-call-sites.json',reads);save('all-hash-literal-consumers.json',literals);save('build-replacements.json',patches)
named=[]
mapping={'GICollectorSha256':'tools/fact_collector.py','GIFactPlanSha256':'reference/fact-plan.json','GIV2AdapterSha256':'tools/facts_qualification.py','GIV2CaptureSha256':'tools/outer_capture.py','GIV2OriginSha256':'tools/capture_origin.py'}
s=(B/'tools/admission_checks.ps1').read_text()
for k,n in mapping.items():
 h=re.search(r"\$script:"+k+r"='([0-9a-f]{64})'",s).group(1);named.append({'name':k,'producer':n,'consumer':'tools/admission_checks.ps1','expected':h,'actual':sha((B/n).read_bytes()),'match':h==sha((B/n).read_bytes())})
dups=[]
for x in funcs:
 if x['file']!='tools/qualification_reference.ps1':continue
 peers=[a for a in funcs if a['file']=='tools/admission_checks.ps1' and a['name']==x['name']]
 if peers:
  a=peers[0];norm=lambda v:v.rstrip().replace('\r\n','\n')
  dups.append({'function':x['name'],'referenceLine':x['line'],'inlineLine':a['line'],'textEqual':norm(x['segment'])==norm(a['segment']),'referenceSha256':sha(norm(x['segment']).encode()),'inlineSha256':sha(norm(a['segment']).encode())})
save('named-pins-and-inline-copies.json',{'namedPins':named,'duplicateFunctions':dups,'literalOccurrences':len(literals),'allSourcePinsVerified':31,'allGatePinsVerified':23})
plan=load('reference/fact-source-plan06.json');assert len(plan['rows'])==64
runtime=load('reference/current-runtime-identity.json');runtimeSizes={x['path'].replace('\\','/').casefold():x['bytes'] for x in runtime['files']}
rawInventory=[x for x in json.loads((R/'extraction-audit.json').read_text())['inventory'] if x['path']=='selfchecks/work/q06-482f38b7/f/fixture-facts.raw'];assert len(rawInventory)==1 and rawInventory[0]['bytes']==139264
rowChecks=[]
for i,x in enumerate(plan['rows']):
 path=x['path'].replace('\\','/');marker='/d1android02-facts-v2-qualification06/';rel=path.split(marker,1)[1] if marker in path else None
 if rel and (B/rel).is_file():amount=(B/rel).stat().st_size
 elif rel and rel.endswith('/fixture-facts.raw'):amount=139264
 else:amount=runtimeSizes[path.casefold()]
 expected=amount+(x['kind']=='read');assert x['index']==i and x['scope']==plan['scope'] and x['chargedBytes']==expected and x['reads']==1
 rowChecks.append({'index':i,'stage':x['stage'],'path':x['path'],'kind':x['kind'],'independentFileOrDeclaredBytes':amount,'expectedCharge':expected,'matches':True})
save('independent-row-byte-verification.json',rowChecks)
groups=[]
for stage in dict.fromkeys(x['stage'] for x in plan['rows']):
 a=[x for x in plan['rows'] if x['stage']==stage];groups.append({'stage':stage,'reads':len(a),'bytes':sum(x['chargedBytes'] for x in a),'owner':sorted(set(x['owner'] for x in a))})
assert sum(x['reads'] for x in groups)==64 and sum(x['bytes'] for x in groups)==8967668
child=next(x for x in plan['rows'] if x['kind']=='child-reservation');route=(B/'selfchecks/route_fixture.py').stat().st_size
save('branch-stage-obligations.json',{'mode':'STATIC_NOT_ACTUAL_LEDGER','RAW_FILE':{'implementedPlanReads':64,'implementedPlanBytes':8967668,'groups':groups,'childManualChargeHasNoEvent':True,'childIndex':child['index'],'hypotheticalReturnedEvents':63,'extraRouteSelfHashReads':1,'extraRouteSelfHashBytes':route,'completeExplicitObligationsReads':65,'completeExplicitObligationsBytes':8967668+route},'COMPLETE':{'implementedPlanReads':61,'implementedPlanBytes':8967668-3*139264-1,'extraRouteSelfHashReads':1,'completeExplicitObligationsReads':62},'LIVE':{'formulaReads':'6+(1+23+2)+16+1auth+1native+2route+5receive+1sdk =58','nativeKnownBytes':8273560,'rawFixtureAndGuardReads':0,'extraExplicitSelfHash':{'file':'tools/win32_route.py','line':489,'reads':1,'bytes':(B/'tools/win32_route.py').stat().st_size},'completeExplicitObligationsReads':59,'nativeUnknownBranch':'manual known/reservedUnknown update has no source_event; not success full-plan evidence','note':'auth length/runtime/local inputs require final pinned candidate; no LIVE executed'},'separateAuthorityLanes':['PreparedFacts private seed to original Gate','Gate full fact plan:64/256MiB','ProductionRunner source:256/512MiB independent','SourceBudget original Gate/Runner permanent reservation and child PS delta','V2 host _SOURCE_READS:8192/512MiB','PS qualification reference reservation and actual read/close events','control template/policy/context/proof/receipt distinct from source']})
print(json.dumps({'mutations':len(mut),'readSites':len(reads),'hashOccurrences':len(literals),'namedPins':named,'inlineCopies':dups,'stages':groups},ensure_ascii=False))
