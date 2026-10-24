"""Pure use of actual reservation builder; old bytes are shapes, never permits."""
from pathlib import Path
from types import SimpleNamespace as N
import sys,json,copy
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H/'tools'))
from production_runner import ProductionRunner
from source_budget import admit,CAPACITY_SHAPES06
from entry_gates import encode
O=Path('D:/CodexProjects/VideoKit/docs/coder/d1android02-facts-v2-qualification04');old=O/'selfchecks/work/q04-a2f9d37c/positive'
def load(p):return json.loads(p.read_bytes())
p=load(old/'permit.json');template=load(H/'release/capture-policy.json');shapes=CAPACITY_SHAPES06
home=H/'selfchecks/work/pure-model/home';p['home']=str(home);p['evidenceRoot']=str(home/'outputs');p['sources']=load(H/'reference/runner-source-seal.json')['sources'];p['sourceSeal']['path']=str(H/'reference/runner-source-seal.json');p['review']['path']=str(home.parent/'reply/review.json')
for s in p['roles']:
 s['argv']=[x.replace(str(old/'home/outputs'),str(home/'outputs')).replace(str(O),str(H)) for x in s['argv']]
 if 'payloadPin' in s:s['payloadPin']['path']=str(home/'outputs'/Path(s['payloadPin']['path']).name)
def model(p):
 r=N(permit=p,permit_bytes=encode(p),approval_bytes=(old/'approval.json').read_bytes(),permit_path=home.parent/'permit.json',approval_path=home.parent/'approval.json',permit_sha='b'*64,approval_sha='b'*64,home=home,root=home/'outputs',fixture=True,kind='OFFLINE_FIXTURE')
 r.policy_definition=lambda t:ProductionRunner.policy_definition(r,t);r.activation_definition=lambda *a:ProductionRunner.activation_definition(r,*a)
 r.capacity_template_bytes=(H/'release/capture-policy.json').stat().st_size;r.capacity_source_seal_bytes=(H/'reference/runner-source-seal.json').stat().st_size;r.capacity_copy_bytes={rel:(H/rel).stat().st_size for rel in ('tools/capture_android02.ps1','reference/exact-seven-role-plan.json','reference/route-backend-contract.json')};r.pre=[dict(event=n,bytes=z) for n,z in [('permit-read',len(r.permit_bytes)),('approval-read',len(r.approval_bytes)),('source-seal-read',r.capacity_source_seal_bytes)]]
 return r
normal=admit(model(p),template,shapes)
q=copy.deepcopy(p);q['globalIdleQualification']['evidenceRoot']='D:\\'+('x'*7186);q['globalIdleQualification']['evidenceRef']['path']=q['globalIdleQualification']['evidenceRoot']+'\\qualification-evidence.json'
try:admit(model(q),template,shapes);reason='ACCEPT'
except ValueError as e:reason=str(e)
assert reason.startswith('CONTROL_ENVELOPE_CONTROLLER_65536'),reason
out=dict(allPassed=True,normal=normal,longIndependentRoot=dict(reason=reason,wireBytes=len(encode(q['globalIdleQualification'])),permitBytes=len(encode(q)),OSReachability='NOT_PROVEN_NOT_MATERIALIZED',candidateOnly=True),GateConstructor=0,CaptureConstructor=0,claim=0,once=0,homeCreated=home.exists())
assert not home.exists();(H/'evidence').mkdir(exist_ok=True);(H/'evidence/control-envelope-pure07.json').write_bytes(encode(out));print(json.dumps(dict(normalMax=max(x['localControlBytes'] for x in normal['roles']),shared=normal['sharedBytes'],longReason=reason)))
