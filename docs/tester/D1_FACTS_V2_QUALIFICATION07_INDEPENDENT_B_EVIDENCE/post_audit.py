"""Independent fixed-file audit after original worker return; no PID queries."""
from pathlib import Path
from types import SimpleNamespace as N
import json,hashlib,ast,re,copy,sys
R=Path(__file__).resolve().parent;C=R.parents[1]/'coder/d1android02-facts-v2-qualification07';B=C/'rev2';sys.path.insert(0,str(R))
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def save(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=load(R/'plan.json');W=Path(plan['work']);result=load(R/'evidence/result.json');outer=load(R/'outer-final.json');checks=[]
def check(n,v,detail=None):checks.append(dict(case=n,passed=bool(v),detail=detail))
check('all-nine-independent-groups',len(result['groups'])==9 and all(x['status']=='PASS' for x in result['groups']),[(x['name'],x['status']) for x in result['groups']])
check('outer-original-return',outer['receipt']['originalWaitReturnedOnce'] and outer['receipt']['readersJoined'] and outer['receipt']['streamsAndOriginalHandleCloseReturned'] and not outer['receipt']['errors'] and not outer['receipt']['expired'] and outer['auditMismatch']==0)
check('all-originals-return-proof',result['revisionReturnProof']['allOriginalsProven'] and result['auxOriginalsReturned'] and not any(result['custody'].values()))
check('host-audit',len(result['hostPopen'])==len(result['audit']) and all(x['matches'] for x in result['audit']) and all(x.get('constructorReturned') for x in result['hostPopen']))
manifest=load(C/'full-manifest.json');bad=[]
for x in manifest['files']:
 b=(C/x['path']).read_bytes()
 if sha(b)!=x['sha256'] or len(b)!=x['bytes']:bad.append(x['path'])
check('candidate567-unchanged',len(manifest['files'])==567 and not bad,bad)
order=load(R/'order.json');changed=[]
for x in order['sources']:
 b=Path(x['path']).read_bytes()
 if len(b)!=x['bytes'] or sha(b)!=x['sha256']:changed.append(x['path'])
check('all613-frozen-inputs-unchanged',not changed,changed)
source=load(W/'actual-facts-complete-source-audit.json');a=source['rows'];p=source['planned'];check('facts64-each-field',len(a)==len(p)==64 and all(all(x[k]==y[k] for k in ('scope','path','kind','index','chargedBytes')) for x,y in zip(a,p)))
check('facts64-fee-sum',sum(x['chargedBytes'] for x in a)==source['summary']['sourceBytes']==source['summary']['plannedBytes'])
check('seed-and-phase-ownership',all(x.get('stage',y['stage'])==y['stage'] and x.get('owner',y['owner'])==y['owner'] for x,y in zip(a,p)),{'seedStage':'derived from same-scope frozen plan where private seed lacks optional stage/owner; later rows must match'})
child=[x for x in a if x['kind']=='child-reservation'];route=[x for x in a if x['kind']=='route-child-reservation'];check('child-and-route-permanent-reservations',len(child)==len(route)==1 and child[0]['chargedBytes']==139264 and route[0]['chargedBytes']==(B/'selfchecks/route_fixture.py').stat().st_size)
check('original-read-close-vs-helper-reservation',all(x['originalCloseReturned'] for x in a if x['kind'] in ('read','preauth-read','adopted-read')) and all(x.get('fixedHelperReturned') for x in a if x['kind']=='runtime-reservation'))
prod=[]
for label in plan['targets']:
 d=load(W/('production-'+label+'.json'));events=d['sourceEvents'];fees=d['runnerSourceFeeEvents'];probes=(d['terminal'] or {}).get('sourceBudgetProbe',{}).get('reads',[])
 rb=sum(x['chargedBytes'] for x in fees)+sum(x['ticket']['reservedBytes'] for x in events)+2*len(probes);rr=len(fees)+sum(x['ticket']['reservedReads'] for x in events)+len(probes)
 check('runner-original-fee-tickets-'+label,(rb,rr)==(d['runnerSourceBytes'],d['runnerSourceReads']) and all(x['originalReturned'] for x in fees),{'computed':[rb,rr],'observed':[d['runnerSourceBytes'],d['runnerSourceReads']]})
 if events:
  gb=events[0]['ticket']['baseGateBytes']+sum(x['ticket']['reservedBytes'] for x in events)+2*len(probes);gr=events[0]['ticket']['baseGateReads']+sum(x['ticket']['reservedReads'] for x in events)+len(probes)
  check('gate-original-fee-tickets-'+label,(gb,gr)==(d['gateSourcesBytes'],d['gateSourcesReads']),{'computed':[gb,gr],'observed':[d['gateSourcesBytes'],d['gateSourcesReads']]})
 check('no-unknown-reader-'+label,all(x['originalCloseReturned'] for x in d['receiptReads']) and d['gateReleased'])
 if label=='positive':
  check('positive-identity-global-and-delta',len(d['records'])==2 and all(x['merged'] for x in events) and d['pending'] is None)
  for rec in d['records']:
   co=rec['console'];r=next(x for x in d['controlAdmission']['roles'] if x['role']==rec['id']);actual=co['recordWriteBytesKnown']+2*co['consoleBytes']+co['proofReadBytes'];check('full-local-control-'+rec['id'],actual<=r['localControlBytes']<=65536,{'actual':actual,'reservation':r['localControlBytes'],'functionalRead':co['proofReadBytes'],'functionalReservation':r['functionalReadBytes']})
   ref=co['receiptRef'];good=next(x for x in d['receiptReads'] if x['role']==rec['id'] and x['error'] is None);raw=Path(ref['path']).read_bytes();writer=load(ref['path'])
   check('writer-console-original-reader-'+rec['id'],set(ref)=={'path','bytes','sha256','volumeId','fileId'} and good['expected']==ref and good['before']==good['after']=={k:ref[k] for k in ('volumeId','fileId','bytes')} and good['readBytes']==ref['bytes']==len(raw) and sha(raw)==ref['sha256']==co['captureReceiptSha256'] and co['allOriginalResourcesReturnedAtConsole'],{'reference':ref,'readBytes':good['readBytes'],'originalReaderClosed':good['originalCloseReturned'],'writerFields':sorted(writer)})
  check('gate-real64-reject65',d['terminal']['sourceBudgetProbe']['finalGateReads']==64 and d['terminal']['sourceBudgetProbe']['reject65']=='SOURCE_READ_BUDGET' and d['terminal']['sourceBudgetProbe']['ownerNextRoleReject']=='SOURCE_OWNER_BUDGET_BEFORE_LAUNCH')
 if label=='wrong-firmware':check('wrong-firmware-no-global',len(d['records'])==1 and d['records'][0]['console']['semantic']=='FACT_IDENTITY_FIRMWARE_DISAGREEMENT' and not (Path(plan['targets'][label]['home'])/'request-global_idle.json').exists())
 if label=='receipt-replace':check('samebytes-new-fileId-before-content-read',d['error']=='ORIGINAL_RECEIPT_FILE_IDENTITY' and d['replacement']['sameBytes'] and d['replacement']['differentId'] and d['receiptReads'][-1]['readBytes']==0 and d['receiptReads'][-1]['originalCloseReturned'] and d['pending'] is not None and not (Path(plan['targets'][label]['home'])/'request-global_idle.json').exists())
 prod.append(dict(label=label,gateBytes=d['gateSourcesBytes'],gateReads=d['gateSourcesReads'],runnerBytes=rb,runnerReads=rr,permanentTicketBytes=sum(x['ticket']['reservedBytes'] for x in events),permanentTicketReads=sum(x['ticket']['reservedReads'] for x in events),pending=d['pending'] is not None))
# Named producer consumers and complete embedded schema are checked on final
# bytes independently of the package's own declared allPassed flags.
ps=(B/'tools/admission_checks.ps1').read_text();named={}
for k,n in {'GICollectorSha256':'tools/fact_collector.py','GIFactPlanSha256':'reference/fact-plan.json','GIV2AdapterSha256':'tools/facts_qualification.py','GIV2CaptureSha256':'tools/outer_capture.py','GIV2OriginSha256':'tools/capture_origin.py'}.items():
 h=re.search(r"\$script:"+k+r"='([0-9a-f]{64})'",ps).group(1);named[k]=h;check('named-pin-'+k,h==sha((B/n).read_bytes()))
text=(B/'tools/fact_preauth.py').read_text();embedded=ast.literal_eval(next(x.value for x in ast.parse(text).body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='FACT_PREAUTH_SCHEMA07_RAW' for y in x.targets)));check('schema-full-original-bytes',embedded.encode()==(B/'reference/fact-preauth-schema.json').read_bytes())
def segments(s):
 starts=list(re.finditer(r'(?m)^function\s+(\w+)[^\n]*',s));return {m.group(1):s[m.start():starts[i+1].start() if i+1<len(starts) else len(s)].rstrip().replace('\r\n','\n') for i,m in enumerate(starts)}
ref=segments((B/'tools/qualification_reference.ps1').read_text());inline=segments(ps);check('all11-inline-functions',len(ref)==11 and all(inline[k]==v for k,v in ref.items()))
# Negative parser cases only edit separate model files, never original results.
from independent_driver import inspect_result_file
actual=load(W/'budget-result.json');reasons=load(R/'helper-reasons.json');ids=list(reasons);modelroot=R/'result-parser-models';modelroot.mkdir(exist_ok=True);parser=[]
variants=[('missing',None,'RESULT_FILE_MISSING'),('exact',actual,'RESULT_CASES_MATCHED'),('incomplete',dict(actual,complete=False),'RESULT_INCOMPLETE_OR_CASESET_MISMATCH'),('aggregate',dict(actual,allPassed=False),'RESULT_AGGREGATE_MISMATCH'),('authority',dict(actual,realAuthority=True),'RESULT_AUTHORITY_LABEL_MISMATCH')]
wrong=copy.deepcopy(actual);wrong['results'][0]['pass']=1;variants.append(('bool-type',wrong,'RESULT_BOOLEAN_TYPE_MISMATCH'))
wrong=copy.deepcopy(actual);wrong['results'].reverse();variants.append(('id-order',wrong,'RESULT_INCOMPLETE_OR_CASESET_MISMATCH'))
for label,data,want in variants:
 f=modelroot/(label+'.json')
 if data is not None:f.write_text(json.dumps(data),encoding='utf-8')
 out=inspect_result_file(N(output_path=str(f)),ids,reasons,lambda p,cap:Path(p).read_bytes());parser.append(dict(case=label,observed=out['status'],want=want,passed=out['status']==want))
f=modelroot/'duplicate.json';f.write_text('{"schema":"x",'+json.dumps(actual)[1:],encoding='utf-8');out=inspect_result_file(N(output_path=str(f)),ids,reasons,lambda p,cap:Path(p).read_bytes());parser.append(dict(case='duplicate-field',observed=out['status'],want='RESULT_FILE_INVALID_JSON',passed=out['status']=='RESULT_FILE_INVALID_JSON'));check('parser8-models',all(x['passed'] for x in parser),parser)
check('time-and-process-budget',result['seconds']<360 and outer['seconds']<360 and len(result['hostPopen'])+2+4+1<=25)
check('source-reservations-under1GiB',plan['sourceReservations']['total']<=1073741824)
check('all-new-file-close',all(x['closeReturned'] for x in result['fileEvents']))
save('post-audit.json',dict(allPassed=all(x['passed'] for x in checks),checks=checks,productionBudgets=prod,sourceReads=64,sourceBytes=source['summary']['sourceBytes'],hostPopen=len(result['hostPopen']),actualTotalGraph=len(result['hostPopen'])+2+4+1,parserModels=parser,productRunsAdded=0,oldObjectQueries=0,SDK=0,Git=0));print(json.dumps(dict(allPassed=all(x['passed'] for x in checks),checks=len(checks),failures=[x for x in checks if not x['passed']])))
