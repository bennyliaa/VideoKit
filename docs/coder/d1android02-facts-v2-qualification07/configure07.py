from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;rev=sys.argv[1] if len(sys.argv)>1 else 'REV1';H=R/rev.lower();aud=[]
def put(p,s):p.write_bytes(s.encode())
def rep(s,a,b,n=1):assert s.count(a)==n,(a[:100],s.count(a),n);aud.append(dict(anchor=a[:100],hits=n));return s.replace(a,b)
p=H/'prepare07.py';s=p.read_text();s=rep(s,'import sys,json,uuid,hashlib,os','import sys,json,uuid,hashlib,os,time')
s=rep(s,'checks=[]',"C=Path('D:/CodexProjects/VideoKit/docs/coder');DOCS=C.parent;BATCH=json.loads((H.parent/'batch-declaration07.json').read_bytes());REV=next(x for x in BATCH['revisions'] if x['root']==str(H));SEED=uuid.UUID(REV['seed']);BATCH_START=json.loads((H.parent/'execution-start.json').read_bytes())['monotonic'] if (H.parent/'execution-start.json').exists() else time.monotonic()\nchecks=[]")
s=s.replace("H.parent/'d1android02-","C/'d1android02-").replace("H.parents[1]/'tester/","DOCS/'tester/")
s=rep(s,"'tester/D1_FACTS_V2_QUALIFICATION05_PHASE_A_EVIDENCE'","'tester/D1_FACTS_V2_QUALIFICATION05_PHASE_A_EVIDENCE'",1) if False else s
# Global batch scope IDs are fixed before first actual call, distinct per rev.
s=rep(s,"('q07-'+uuid.uuid4().hex[:8])","('q07-'+uuid.uuid5(SEED,'work').hex[:8])")
s=rep(s,"W.mkdir(parents=True);pins=","W.mkdir(parents=True,exist_ok=True);assert not (W/'f/home').exists(),'NO_PREPARE_AFTER_EXECUTION';pins=")
s=rep(s,"root=W/'f';root.mkdir();","root=W/'f';root.mkdir(exist_ok=True);")
s=rep(s,"pid=str(uuid.uuid4());run='D1MA02-Q07_FACTS'","pid=str(uuid.uuid5(SEED,'facts'));run='D1MA02-Q07_FACTS'")
s=rep(s,"pid=str(uuid.uuid4());run='D1MA02-Q07_'+label","pid=str(uuid.uuid5(SEED,label));run='D1MA02-Q07_'+label")
s=rep(s,"nonce=str(uuid.uuid4())","nonce=str(uuid.uuid5(SEED,pins['sourceSealSha256']+':nonce'))")
s=rep(s,"sourceReservation=dict(factsGate=268435456,targetGates=268435456,runnerSources=268435456,driverAndModels=201326592,total=1006632960)","sourceReservation=dict(factsGate=33554432,targetGates=67108864,runnerSources=100663296,driverAndModels=268435456,total=469762048)")
s=rep(s,"plan=dict(schema='QUALIFICATION07_BATCH_PLAN_V1',","plan=dict(schema='QUALIFICATION07_BATCH_PLAN_V1',revision=REV['id'],batchStart=BATCH_START,batchDeclarationSha256=digest(H.parent/'batch-declaration07.json'),")
put(p,s)
p=H/'preflight07.py'
if rev=='REV2':
 s=p.read_text();s=rep(s,"check('all-Python-compile',True)","check('all-Python-compile',True)\nprefix=re.search(r\"\\$prefix='([^']+)'\",c).group(1)\ncheck('PS-canonical-revision-fixture-prefix',prefix==str(H/'selfchecks/work')+'\\\\',prefix)\nfrom contract_cases import make\nfrom independent_cases_original import cases\nfrom contract03_cases import cases as extra_cases\ncheck('actual-V1-generator-inputs-before-Capture',len(make()+cases(H)+extra_cases())==346)")
 put(p,s)
for rel in ('worker07.py','driver/driver_guard07.py'):
 p=H/rel;s=p.read_text();s=rep(s,'START=time.monotonic()','START=PLAN[\'batchStart\']');put(p,s)
p=H/'worker07.py';s=p.read_text();s=rep(s,'controlAdmission=r.control_admission,','controlAdmission=r.control_admission,runnerSourceFeeEvents=r.source_fee_events,')
needle='for x in PROFILE:assert digest'
proof="""def revision_return_proof():
 owners=[]
 for r in runners:
  g=r.gate;o=r.owner
  waits=[dict(x) for x in (o.held if o else []) if type(x) is dict and 'handleClose' in x]
  writers=[dict(x) for x in (o.held if o else []) if type(x) is dict and 'closeReturned' in x and 'writeReturned' in x]
  alive=any(isinstance(t,threading.Thread) and t.is_alive() for t in r.pending+(g.pending if g else [])+(o.held if o else []))
  gates=[dict(name=x['name'],returned=x['returned'],error=x['error']) for x in (g.held if g else []) if type(x) is dict and 'name' in x and 'returned' in x and 'error' in x]
  good=not alive and all(x['returned'] and x['error'] is None for x in gates) and all(x['wait'] and x['stdoutClose'] and x['stderrClose'] and x['handleClose'] and x['error'] is None for x in waits) and all(x['closeReturned'] and x['writeReturned'] and x['error'] is None for x in writers) and all(x['originalReturned'] for x in r.source_fee_events) and (g is None or g.lease is None or g.released and g.lease.closed)
  owners.append(dict(scope=r.permit['scope'],allProven=good,liveThreads=alive,gateOriginals=gates,outerOriginalReturns=waits,originalWriters=writers,sourceFeeEvents=r.source_fee_events,claimReleasedOrNeverHeld=(g is None or g.lease is None or g.released and g.lease.closed)))
 aux=all(c.returned and all(c.facts.get(k) for k in ('originalWaitReturned','readersJoined','streamsClosed','handleCloseReturned')) for c in caps)
 return dict(allOriginalsProven=aux and all(x['allProven'] for x in owners) and not CUSTODY and not GATE_CUSTODY and not FACT_CUSTODY and not FILE_PENDING and not RUNNER_CUSTODY,auxOriginalsProven=aux,owners=owners)

"""
s=rep(s,needle,proof+needle)
# Summaries from shared clock retain per-revision elapsed separately.
s=rep(s,"out=dict(schema='QUALIFICATION07_RESULT_V1',","out=dict(schema='QUALIFICATION07_RESULT_V1',revision=PLAN['revision'],revisionReturnProof=revision_return_proof(),batchElapsed=time.monotonic()-START,")
put(p,s)
p=H/'parse07.ps1';s=p.read_text();at=s.index('$out=@{')
inline="""$t=$null;$e=$null;$refAst=[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'tools/qualification_reference.ps1'),[ref]$t,[ref]$e)
$t=$null;$e=$null;$admitAst=[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'tools/admission_checks.ps1'),[ref]$t,[ref]$e)
$inlineRows=@()
foreach($fn in @($refAst.FindAll({param($n)$n -is [System.Management.Automation.Language.FunctionDefinitionAst]},$true))){
 $other=@($admitAst.FindAll({param($n)$n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq $fn.Name},$true))
 $left=($fn.Extent.Text -split \"`r?`n\"|ForEach-Object {$_.TrimEnd()}) -join \"`n\"
 $right=if($other.Count -eq 1){($other[0].Extent.Text -split \"`r?`n\"|ForEach-Object {$_.TrimEnd()}) -join \"`n\"}else{''}
 $same=$left -ceq $right;$inlineRows+=@{name=$fn.Name;same=$same};if(-not $same){$bad+='INLINE:'+ $fn.Name}
}
if($inlineRows.Count -ne 11){$bad+='INLINE_FUNCTION_COUNT'}
"""
s=s[:at]+inline+s[at:];s=rep(s,'files=$rows;bad=$bad;','files=$rows;inlineFunctions=$inlineRows;bad=$bad;');put(p,s)
p=H/'preflight07.py';s=p.read_text().replace('31-original-source-pins','30-original-source-pins').replace('len(src)==31','len(src)==30').replace('23-gate-pins','22-gate-pins').replace('len(gate)==23','len(gate)==22').replace('PS-exact31-source-set','PS-exact30-source-set');s=rep(s,"check('all-Python-compile',True)","check('all-Python-compile',True)\ncheck('full-named-consumers-and-source-fees',load(H/'evidence/pin-and-fee-registry07.json')['allPassed'])\ncheck('schema-full-value-preserved',load(H/'reference/source-schema-consolidation07.json')['completeRawContractEmbedded'])\ncheck('two-revision-budget-declared',plan['sourceReservation']['total']==469762048 and load(H.parent/'batch-declaration07.json')['totalReadReservation']==1006632960)")
s=rep(s,"check('unchanged-64-256MiB-caps'", "from fact_preauth import complete_source_plan,FACT_RUNTIME_FILES06\nsize_map={x['path']:Path(x['path']).stat().st_size for x in source_plan['rows']}\npolicy0=load(Path(plan['facts']['root'])/'policy.json');gf=load(H/'reference/gate-sources.json')['files']\ncomplete=complete_source_plan(policy0,gf,FACT_RUNTIME_FILES06,size_map)\ncheck('COMPLETE-explicit-obligations61',complete['sourceReads']==61,complete)\nlivep=copy.deepcopy(policy0);livep['mode']='PRODUCTION';livep['gateAuthorization']={'path':str(H/'selfchecks/work/pure-live/home/release/gate-local-authorization.json'),'sha256':'b'*64};size_map[livep['gateAuthorization']['path']]=600;size_map[str(Path('D:/Android/SDK/platform-tools/adb.exe'))]=8273560\nlive=complete_source_plan(livep,gf,FACT_RUNTIME_FILES06,size_map)\ncheck('LIVE-explicit-obligations58-model-only',live['sourceReads']==58,dict(plan=live,SDKRead=0))\ncheck('unchanged-64-256MiB-caps'")
put(p,s)
p=H/'capacity_preflight07.py';s=p.read_text();s=rep(s,"O=H.parent/'d1android02-facts-v2-qualification04'","O=Path('D:/CodexProjects/VideoKit/docs/coder/d1android02-facts-v2-qualification04')");put(p,s)
put(H/'configure-audit07.json',json.dumps(dict(allExact=True,patches=aud),indent=2)+'\n')
print('07 harness configured with one shared deadline and declared distinct revision scopes')
