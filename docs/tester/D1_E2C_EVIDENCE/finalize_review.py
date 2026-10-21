"""Static E2C report/link/unchanged-input finalization. No candidate execution."""
from pathlib import Path
import ast,hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e2c';OLD=ROOT/'docs/coder/d1e2b'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_E2C_RESOURCE_REVIEW_REPORT_V1.0.md'
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',report.read_text(encoding='utf-8')):
 target=m.group(1);lm=re.search(r':(\d+)$',target);line=int(lm.group(1)) if lm else None
 if lm:target=target[:lm.start()]
 p=Path(target);assert p.exists(),target
 if line:assert 1<=line<=len(p.read_text(encoding='utf-8-sig').splitlines())
archive=read(OUT/'archive-and-manifest-audit.json');assert sha(BASE/'evidence/freeze-summary.json')==archive['freezeSha256']
for r in archive['allCheckedEntries']:assert sha(ROOT/r['path'])==r['sha256']
for folder in ['upstream-e2b','upstream-e2a','upstream-e2','upstream-e1e']:
 f=read(BASE/folder/'freeze-summary.json');s=read(BASE/folder/'source-manifest.json')
 for r in f['files']+f['selfcheckFiles']+s['files']:assert sha(ROOT/r['path'])==r['sha256']
for r in read(BASE/'upstream-e1e/preserved-baselines.json')['files']:assert sha(ROOT/r['path'])==r['sha256']
def item(base,rel,name,cls=None,normalize=False):
 source=(base/rel).read_text(encoding='utf-8')
 if normalize:source=source.replace('E2B','E2C')
 tree=ast.parse(source);nodes=tree.body
 if cls:nodes=next(n for n in nodes if isinstance(n,ast.ClassDef) and n.name==cls).body
 return ast.dump(next(n for n in nodes if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name==name),include_attributes=False)
preserved=[]
for rel,name,cls in [('src/authority.py','SourceAuthority',None),('src/authority.py','SourceBridge',None),('src/authority.py','complete_source_response',None),('src/authority.py','capture_ready_request',None),('src/authority.py','validate_ready_request',None),('src/gcore.py','Store',None),('src/gcore.py','Native',None),('src/gengine.py','grant','Ops'),('src/gengine.py','ready','Ops'),('src/gengine.py','takeover','Ops')]:
 assert item(BASE,rel,name,cls)==item(OLD,rel,name,cls),name
 preserved.append(dict(path=rel,symbol=(cls+'.' if cls else '')+name,astUnchangedFromE2B=True))
for name in ['start','_start_worker','_cleanup_workers_owned','_cleanup_workers','ensure_accepting']:
 assert item(BASE,'src/notifications.py',name,'CompletionHub')==item(OLD,'src/notifications.py',name,'CompletionHub',True),name
 preserved.append(dict(path='src/notifications.py',symbol='CompletionHub.'+name,astUnchangedAfterExplicitE2BToE2CLabelNormalization=True))
preserved.append(dict(path='src/notifications.py',symbol='CompletionHub.close',astUnchanged=False,reviewedChange='Additional monitor_inflight condition wait uses original end deadline and stops if expired; original worker startup/cleanup proof retained'))
save('preserved-fix-static-audit.json',dict(scope='Selected static AST identity only, not regression rerun',preserved=preserved))
anchors={}
for rel in ['src/authority.py','src/notifications.py','src/gengine.py','src/phases.py']:
 anchors[rel]=[dict(line=i,text=s) for i,s in enumerate((BASE/rel).read_text(encoding='utf-8').splitlines(),1) if re.search(r'archive|compact|quiescent|monitor_inflight|del cell|cell_history|cell_total|held|finish_source|privateCells|cellHistory',s)]
save('archive-caller-and-quiescence-anchors.json',dict(scope='Static caller/ownership review; no full-driver execution',anchors=anchors,callerContract='Creator-thread serial boundary after original method has consumed its cell/Future; not arbitrary asynchronous revocation',reviewedCallers=['ordinary open/read result','held open/read gate','zero bridge and short/error return','Flow begin/transaction/finish','Cleanup release_gate/owner_notice/final receipt','failure return summary']))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E2C independent lifecycle whole-package review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),conclusion='LIFECYCLE_REFERENCE_FIX_STATICALLY_CLOSED_WITHIN_DECLARED_SERIAL_CALLER_CONTRACT; RECOMMEND_SEPARATELY_AUTHORIZED_FIXED_SIX_POINT_POST_FIX_OS_COMPARISON',findings=[],candidateIntegrity='PASS',candidateUnchanged=True,producerSelectedChecks=dict(targeted=1125,lifecycle=170,beforeFixDiagnosticG=1,beforeFixOSPoints=6,postFixOS='NOT_RUN',actualFull='NOT_RUN',scope='Existing evidence only'),oldG369FailPreserved=True,exactCBackend='UNKNOWN',handleTypeCausality='UNKNOWN',ownFunctionalTests=0,newSampling=False,selfcheckRerun=False,PFStarted=False,mediaIO=False,mediaStat=False,build=False,adb=False,newHelperProcesses=0,newWorkerThreads=0,inFlight=[],thresholdsChanged=False,nextOSExperimentAuthorized=False,actualFullAuthorized=False,realExperimentAuthorized=False,D1Passed=False,M0Started=False,C14Resumed=False,notification='Pending direct authorized coordinator notification'))
print(json.dumps(dict(reportSha256=sha(report),newFindings=0,postFixOS=False,oldGResourceBlocked=True,candidateUnchanged=True,inFlight=[])))
