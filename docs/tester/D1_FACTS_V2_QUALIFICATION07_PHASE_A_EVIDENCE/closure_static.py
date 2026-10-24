from pathlib import Path
import ast,re,json,hashlib
R=Path(__file__).resolve().parent;B=R/'sealed-code'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda n:json.loads((B/n).read_bytes())
seal=load('reference/runner-source-seal.json')['sources'];g=load('reference/gate-sources.json')['files'];policy=load('release/capture-policy.json')
s=(B/'tools/production_runner.py').read_text();t=ast.parse(s)
names=next(ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='SOURCE_FILES' for a in n.targets))
ps=(B/'tools/admission_checks.ps1').read_text();pskeys=ast.literal_eval('['+re.search(r'\$srcKeys=@\(([^\n]+)\)',ps).group(1)+']')
assert set(names)==set(seal)==set(pskeys) and len(names)==len(pskeys)==31
fields={'entrySha256':'tools/capture_android02.ps1','outerOwnerSha256':'tools/outer_owner.py','gateSourcesSha256':'reference/gate-sources.json','runnerSourceSha256':'tools/production_runner.py','runtimeIdentitySha256':'reference/current-runtime-identity.json','runtimeBindingSourceSha256':'tools/runtime_binding.py','planSha256':'reference/exact-seven-role-plan.json'}
policyChecks=[{'field':k,'producer':n,'matches':policy[k]==sha((B/n).read_bytes())} for k,n in fields.items()];assert all(x['matches'] for x in policyChecks)
pinmap=json.loads((R/'all-hash-literal-consumers.json').read_text(encoding='utf-8'));product=[x for x in pinmap if x['file'].startswith('tools/')]
sourceLiterals=[dict(file=x['file'],line=x['line'],producer=c['producer'],matches=c['matchesCurrent']) for x in product for c in x['comparison']]
counterText=[]
for p in (B/'tools').glob('*.ps1'):
 for i,line in enumerate(p.read_text().splitlines(),1):
  if re.search(r'(qualificationEvidenceSource(Bytes|Reads)|\$s\.(used|reads)|sourceReads|source_bytes|source_reads).*([+]=|\+\+|=)',line):counterText.append({'file':p.relative_to(B).as_posix(),'line':i,'text':line})
out={'source31AndRunnerAndPSKeySetEqual':True,'gate23MembershipSubsetOf31':set(x['path'] for x in g).issubset(seal),'policyChecks':policyChecks,'sourceLiteralConsumers':sourceLiterals,'PSCounterSites':counterText,'bounds':'No product module loaded. Hash joins identify named source references; unmatched SDK/runtime/product/signature/proof hashes are not rewritten. Dynamic references require final packet checks in B.'}
(R/'consumer-closure.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'source31':len(names),'gate23':len(g),'namedSourceLiteralChecks':len(sourceLiterals),'sourceLiteralMismatches':sum(not x['matches'] for x in sourceLiterals),'policyChecks':len(policyChecks),'psCounterSites':len(counterText)}))
