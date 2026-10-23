"""Only pure data, serialization and AST review. Never imports future_capture.
No installed audit hook, process construction, ctypes, candidate or old-state IO.
"""
from pathlib import Path
import ast,copy,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from capture_policy import *
from profiles import proposals
from evidence_io import chunk_rows
R=Path(__file__).resolve().parent
def main():
    plans=proposals();results=[];payloads=[]
    def check(name,fn):
        detail=fn();results.append({'name':name,'passed':True,'detail':detail})
    def denied(fn):
        try:fn()
        except (Denied,ValueError,TypeError) as e:return type(e).__name__+':'+str(e)
        raise AssertionError('EXPECTED_REJECTION')
    for p in plans:
        check('exact-plan-'+p['profile'],lambda p=p:validate_plan(p,p))
        raw=(p['executable'],p['commandLine'],p['cwd'],dict(p['env']))
        row=audit_decision('subprocess.Popen',raw,p,p,active=True,same_owner=True,event_unused=True)
        assert row['allowed'] and row['rawPayloadComplete']
        payloads.append({'origin':'SERIALIZED_PROPOSAL_NOT_ACTUAL_AUDIT_EVENT','profile':p['profile'],'rawEventArgs':list(raw),'decision':row})
        check('serialized-positive-'+p['profile'],lambda row=row:row['allowed'])
    p=plans[0];good=(p['executable'],p['commandLine'],p['cwd'],dict(p['env']))
    cases=[('none-executable',(None,*good[1:])),('same-basename-foreign-path',('C:/Untrusted/python.exe',*good[1:])),('path-alias-backslash',(p['executable'].replace('/','\\'),*good[1:])),('extra-argv',(good[0],good[1]+' --unapproved',*good[2:])),('different-cwd',(*good[:2],'D:/Other',good[3])),('ambient-env-none',(*good[:3],None)),('unknown-arity',good[:3]),('list-not-tuple',list(good)),('bytes-commandline',(good[0],b'bytes',*good[2:])),('oversized-commandline',(good[0],'x'*5000,*good[2:])),('extra-env-key',(*good[:3],dict(good[3],UNAPPROVED='NOT_SAVED_VALUE')))]
    class NoRepr:
        def __repr__(self):raise AssertionError('ARBITRARY_REPR_FORBIDDEN')
    cases.append(('unsupported-object',(NoRepr(),*good[1:])))
    for name,args in cases:
        row=audit_decision('subprocess.Popen',args,p,p,active=True,same_owner=True,event_unused=True);assert not row['allowed']
        payloads.append({'origin':'PURE_NEGATIVE_MODEL_NOT_ACTUAL_AUDIT_EVENT','name':name,'decision':row});check('audit-reject-'+name,lambda row=row:row['reason'])
    for field in ('active','same_owner','event_unused'):
        kw={'active':True,'same_owner':True,'event_unused':True};kw[field]=False
        row=audit_decision('subprocess.Popen',good,p,p,**kw);assert not row['allowed'];check('audit-'+field+'-false',lambda row=row:row['reason'])
    for name,edit in [('none-exe',lambda q:q.__setitem__('executable',None)),('extra-args',lambda q:q['argv'].append('--extra')),('wrong-path',lambda q:q['argv'].__setitem__(0,'C:/Wrong/python.exe')),('shell-true',lambda q:q.__setitem__('shell',True)),('int-closefds',lambda q:q.__setitem__('closeFds',1)),('missing-cwd',lambda q:q.pop('cwd')),('unknown-key',lambda q:q.__setitem__('extra',True))]:
        q=copy.deepcopy(p);edit(q);check('preconstructor-'+name,lambda q=q:denied(lambda:validate_plan(q,p)))
    check('unknown-event',lambda: not audit_decision('not.Popen',good,p,p,active=True,same_owner=True,event_unused=True)['allowed'])
    f={k:False for k in FACT_KEYS};f.update(phase='PREFLIGHT',preflightRejected=True,otherEvidenceReturned=True)
    check('known-preconstructor-fail-normal',lambda: disposition(f)=='FAIL_CLEAN_NO_CONSTRUCTOR' or (_ for _ in ()).throw(AssertionError()))
    a={k:False for k in FACT_KEYS};a.update(phase='AUDIT_REJECTED_PRE_CREATEPROCESS',auditObserved=True,auditRejectedBeforeCreate=True,otherEvidenceReturned=True)
    assert disposition(a)=='RETAIN_CONSTRUCTOR_TEMP_UNKNOWN';check('pre-Create-is-not-temp-return',lambda:disposition(a))
    verified=dict(a,constructorTempsReturned=True);assert disposition(verified)=='FAIL_CLEAN_PRE_CREATE';check('conditional-real-temp-proof-required',lambda:disposition(verified))
    c={k:False for k in FACT_KEYS};c.update(phase='CONSTRUCTOR_ENTERED',otherEvidenceReturned=True)
    assert disposition(c)=='RETAIN_CONSTRUCTOR_RETURN_UNKNOWN';check('constructor-unknown-no-zero-default',lambda:disposition(c))
    c={k:False for k in FACT_KEYS};c.update(phase='CREATED_ORIGINAL',popenObjectReturned=True,identityBound=True,auditObserved=True,constructorTempsReturned=True,originalWaitReturned=True,readersJoined=True,streamsClosed=True,handleCloseReturned=True,otherEvidenceReturned=True)
    assert disposition(c)=='RETURNED_BOUND';check('created-known-return-semantic-FAIL-can-exit',lambda:disposition(c))
    bad_identity=dict(c,identityBound=False);assert disposition(bad_identity)=='FAIL_CLEAN_IDENTITY_OR_AUDIT_REJECTED';check('identity-rejection-still-closes-originals',lambda:disposition(bad_identity))
    for k in ('originalWaitReturned','readersJoined','streamsClosed','handleCloseReturned','otherEvidenceReturned'):
        q=dict(c);q[k]=False;assert disposition(q).startswith('RETAIN');check('pending-'+k,lambda q=q:disposition(q))
    for k in FACT_KEYS:
        q=dict(c);q.pop(k);assert disposition(q).startswith('RETAIN');check('missing-fact-'+k,lambda q=q:disposition(q))
    inconsistent=dict(f,popenObjectReturned=True);assert disposition(inconsistent)=='RETAIN_INCONSISTENT_PHASE';check('inconsistent-preconstructor-phase',lambda:disposition(inconsistent))
    badtype=dict(c,handleCloseReturned=1);assert disposition(badtype)=='RETAIN_INVALID_FACTS';check('no-int-for-bool-return',lambda:disposition(badtype))
    stop=stop_body('SAMPLE_NOT_EXECUTED','NONCE_NOT_AUTHORITY');check('stop-exact',lambda:parse_stop(encoded(stop),stop))
    for name,v in [('nonce',dict(stop,nonce='wrong')),('action',dict(stop,action='CLOSE_HANDLE')),('extra',dict(stop,force=True))]:check('stop-reject-'+name,lambda v=v:denied(lambda:parse_stop(encoded(v),stop)))
    check('stop-reject-duplicate',lambda:denied(lambda:parse_stop(encoded(stop).replace(b'"schema":',b'"schema":"duplicate","schema":'),stop)))
    check('stop-reject-overlong',lambda:denied(lambda:parse_stop(b'x'*1025,stop)))
    rows=[{'i':i,'value':'x'*500} for i in range(1000)];chunks=chunk_rows(rows)
    assert sum(map(len,chunks))==1000 and all(len(encoded(x))<=65536 for x in chunks);check('evidence-split-1000-before-open',lambda:{'chunks':len(chunks),'maxBytes':max(len(encoded(x)) for x in chunks)})
    check('reject-unsplittable-single-row',lambda:denied(lambda:chunk_rows([{'value':'x'*70000}])))
    check('reject-JSON-case-duplicate',lambda:denied(lambda:decode(b'{"PID":1,"pid":2}')))
    # Review the prospective launch and failure source without importing it.
    src=(R/'future_capture.py').read_text(encoding='utf-8');tree=ast.parse(src)
    popens=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='subprocess' and n.func.attr=='Popen']
    assert len(popens)==1 and {'executable','cwd','env','shell','close_fds','stdin','stdout','stderr'}<={k.arg for k in popens[0].keywords}
    assert not any(isinstance(n,ast.If) and ast.unparse(n.test).startswith('__name__') for n in tree.body)
    check('static-single-explicit-Popen-no-active-entry',lambda:{'PopenSites':1,'futureModuleImported':False})
    verify=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify_future_authority')
    ns={'Denied':Denied,'digest':digest,'Path':Path};exec(compile(ast.Module(body=[verify],type_ignores=[]),'<pure-authority-function-only>','exec'),ns)
    inactive=json.loads((R/'INACTIVE_AUTHORITY_TEMPLATE.json').read_text());b=encoded(inactive)
    check('static-dispatch-is-not-dynamic-authority',lambda:denied(lambda:ns['verify_future_authority'](inactive,b,digest(b),'NOT_GRANTED','NOT_GRANTED')))
    for path in R.glob('*.py'):ast.parse(path.read_text(encoding='utf-8-sig'),filename=path.name)
    # These are file artifacts from pure review, never real audit records.
    out=R/'pure-evidence';out.mkdir(exist_ok=False)
    (out/'actual-serialized-proposals.json').write_bytes(encoded({'status':'INACTIVE_SERIALIZED_ONLY','plans':plans}))
    for i,part in enumerate(chunk_rows(payloads,32768)):(out/('audit-payload-models-'+str(i)+'.json')).write_bytes(encoded(part))
    result={'status':'PURE_AND_AST_PASS_NOT_DYNAMIC_VALIDATION','checks':len(results),'results':results,'installedHooks':0,'PopenCalls':0,'ctypesCalls':0,'candidateImports':0,'oldQueriesOrPolls':0,'actualAuditEventsObserved':0,'dynamicValidation':'NOT_RUN_REQUIRES_LATER_DISPATCH'}
    (out/'pure-review-result.json').write_bytes(encoded(result));print(json.dumps({'status':result['status'],'checks':len(results),'PopenCalls':0,'actualAuditEventsObserved':0}))
if __name__=='__main__':main()
