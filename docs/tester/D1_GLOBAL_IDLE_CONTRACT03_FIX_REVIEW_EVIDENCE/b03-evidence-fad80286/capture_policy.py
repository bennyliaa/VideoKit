"""Pure policy for three fixed owned-driver profiles, not a command launcher."""
import hashlib,json,subprocess
PLAN_KEYS=set('schema profile executable argv commandLine cwd env shell closeFds'.split())
ENV_KEYS={'SystemRoot','WINDIR','TEMP','TMP'}
def encoded(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8')
def digest(b):return hashlib.sha256(b).hexdigest()
def decode(raw,cap=16777216):
    if type(raw) is not bytes or len(raw)>cap:raise Denied('JSON_BYTES')
    def pairs(rows):
        d={};seen=set()
        for k,v in rows:
            if k.casefold() in seen:raise Denied('DUPLICATE_JSON')
            d[k]=v;seen.add(k.casefold())
        return d
    v=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=pairs)
    def depth(x,n=0):
        if n>16:raise Denied('JSON_DEPTH')
        if type(x) is dict:
            for a in x.values():depth(a,n+1)
        elif type(x) is list:
            for a in x:depth(a,n+1)
    depth(v);return v
def same(a,b):
    if type(a) is not type(b):return False
    if type(a) is dict:return set(a)==set(b) and all(same(a[k],b[k]) for k in a)
    if type(a) in (list,tuple):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b
class Denied(ValueError):pass
def validate_plan(plan,binding):
    if type(plan) is not dict or set(plan)!=PLAN_KEYS:raise Denied('PLAN_SCHEMA')
    if not same(plan,binding):raise Denied('EXACT_PRIOR_BINDING_REQUIRED')
    if plan['schema']!='OWNED_CAPTURE_PLAN_V1' or plan['profile'] not in ('python_ok','python_fail','powershell_ok'):raise Denied('FIXED_PROFILE')
    if type(plan['argv']) is not list or not 1<=len(plan['argv'])<=32 or any(type(s) is not str or not s or '\x00' in s or len(s)>1024 for s in plan['argv']):raise Denied('EXACT_ARGV')
    if type(plan['executable']) is not str or plan['executable']!=plan['argv'][0]:raise Denied('EXPLICIT_EXECUTABLE_ARGV0')
    if type(plan['commandLine']) is not str or plan['commandLine']!=subprocess.list2cmdline(plan['argv']):raise Denied('EXACT_WINDOWS_SERIALIZATION')
    if type(plan['cwd']) is not str or not plan['cwd'] or type(plan['env']) is not dict or set(plan['env'])!=ENV_KEYS:raise Denied('CWD_ENV_SCHEMA')
    if any(type(k) is not str or type(v) is not str or not v or len(v)>1024 or '\x00' in v for k,v in plan['env'].items()):raise Denied('ENV_VALUE')
    if plan['shell'] is not False or plan['closeFds'] is not True:raise Denied('NO_SHELL_OR_INHERITANCE')
    if len(encoded(plan))>8192:raise Denied('PLAN_BYTES')
    return True
def snapshot(value,depth=0):
    """Exact built-in values within bounds; unsupported data explicitly NOT_SAVED.

    No repr(), iteration or JSON hooks on arbitrary objects. Large/unknown values
    are denied, never silently truncated and called complete raw evidence.
    """
    t=type(value)
    if t is int and not -(2**63)<=value<=2**64-1:return {'type':'int','complete':False,'reason':'INTEGER_BOUND'}
    if value is None or t in (bool,int):return {'type':t.__name__,'value':value,'complete':True}
    if t is str:
        if len(value)>4096:return {'type':'str','characters':len(value),'complete':False,'reason':'VALUE_BOUND'}
        return {'type':'str','value':value,'complete':True}
    if depth>=4:return {'type':t.__name__,'complete':False,'reason':'DEPTH'}
    if t in (tuple,list):
        if len(value)>16:return {'type':t.__name__,'length':len(value),'complete':False,'reason':'ITEM_BOUND'}
        rows=[snapshot(x,depth+1) for x in value]
        return {'type':t.__name__,'items':rows,'complete':all(x['complete'] for x in rows)}
    if t is dict:
        if len(value)>16 or any(type(k) is not str or len(k)>128 for k in value):return {'type':'dict','complete':False,'reason':'KEY_BOUND_OR_TYPE'}
        rows=[{'key':k,'snapshot':snapshot(v,depth+1)} for k,v in value.items()]
        return {'type':'dict','items':rows,'complete':all(x['snapshot']['complete'] for x in rows)}
    return {'type':t.__name__,'complete':False,'reason':'UNSUPPORTED_NOT_SAVED'}
def audit_decision(event,args,plan,binding,*,active,same_owner,event_unused):
    """Windows CPython event args are (explicit exe, serialized args, cwd, env)."""
    raw=snapshot(args)
    if type(args) is tuple and len(args)==4 and type(args[3]) is dict and set(args[3])!=ENV_KEYS:
        # Valid future plans use only the four explicitly approved non-secret
        # environment values. Do not spill arbitrary ambient credentials when
        # rejecting an unrelated/unknown Popen event.
        if 'items' in raw:raw['items'][3]={'type':'dict','complete':False,'reason':'UNAPPROVED_ENV_VALUES_NOT_SAVED','keyCount':len(args[3])}
        raw['complete']=False
    if len(encoded(raw))>16384:
        raw={'type':type(args).__name__,'complete':False,'reason':'RAW_PAYLOAD_BYTES_BOUND','snapshotSha256':digest(encoded(raw))}
    row={'event':event if type(event) is str else 'NON_STRING_EVENT','rawPayload':raw,'rawPayloadComplete':raw['complete'],'allowed':False,'reason':None}
    try:
        if type(event) is not str or event!='subprocess.Popen':raise Denied('UNEXPECTED_EVENT')
        if active is not True or same_owner is not True or event_unused is not True:raise Denied('SCOPE_OWNER_OR_ONCE')
        validate_plan(plan,binding)
        if type(args) is not tuple or len(args)!=4 or not raw['complete']:raise Denied('AUDIT_STRUCTURE_OR_EVIDENCE_BOUND')
        exe,cmd,cwd,env=args
        if type(exe) is not str or exe!=plan['executable']:raise Denied('AUDIT_EXPLICIT_EXECUTABLE')
        if type(cmd) is not str or cmd!=plan['commandLine']:raise Denied('AUDIT_EXACT_COMMAND_LINE')
        if type(cwd) is not str or cwd!=plan['cwd'] or not same(env,plan['env']):raise Denied('AUDIT_CWD_OR_ENV')
        row['allowed']=True
    except (Denied,TypeError) as e:row['reason']=str(e)
    return row
FACT_KEYS=set('phase preflightRejected auditObserved auditRejectedBeforeCreate popenObjectReturned identityBound constructorTempsReturned originalWaitReturned readersJoined streamsClosed handleCloseReturned otherEvidenceReturned'.split())
def disposition(f):
    if type(f) is not dict or set(f)!=FACT_KEYS:return 'RETAIN_MISSING_FACTS'
    if any(type(f[k]) is not bool for k in FACT_KEYS-{'phase'}):return 'RETAIN_INVALID_FACTS'
    if f['phase']=='PREFLIGHT':
        if f['popenObjectReturned'] or f['auditObserved'] or any(f[k] for k in ('originalWaitReturned','readersJoined','streamsClosed','handleCloseReturned')):return 'RETAIN_INCONSISTENT_PHASE'
        return 'FAIL_CLEAN_NO_CONSTRUCTOR' if f['preflightRejected'] and f['otherEvidenceReturned'] else 'RETAIN_PREFLIGHT_EVIDENCE_UNKNOWN'
    if f['phase']=='AUDIT_REJECTED_PRE_CREATEPROCESS':
        if f['popenObjectReturned'] or f['identityBound'] or any(f[k] for k in ('originalWaitReturned','readersJoined','streamsClosed','handleCloseReturned')):return 'RETAIN_INCONSISTENT_PHASE'
        if not(f['auditObserved'] and f['auditRejectedBeforeCreate']):return 'RETAIN_UNPROVEN_PRE_CREATE'
        return 'FAIL_CLEAN_PRE_CREATE' if f['constructorTempsReturned'] and f['otherEvidenceReturned'] else 'RETAIN_CONSTRUCTOR_TEMP_UNKNOWN'
    if f['phase']=='CONSTRUCTOR_ENTERED':return 'RETAIN_CONSTRUCTOR_RETURN_UNKNOWN'
    if f['phase']=='CREATED_ORIGINAL':
        if not f['popenObjectReturned'] or f['preflightRejected'] or f['auditRejectedBeforeCreate']:return 'RETAIN_INCONSISTENT_PHASE'
        if all(f[k] for k in ('originalWaitReturned','readersJoined','streamsClosed','handleCloseReturned','otherEvidenceReturned')):
            return 'RETURNED_BOUND' if f['identityBound'] and f['auditObserved'] else 'FAIL_CLEAN_IDENTITY_OR_AUDIT_REJECTED'
        return 'RETAIN_ORIGINAL_CREATED_PENDING'
    return 'RETAIN_PHASE_UNKNOWN'
def stop_body(batch,nonce):return {'schema':'OWNED_DRIVER_STOP_V1','batch':batch,'nonce':nonce,'action':'STOP_NEW_ADMISSION'}
def parse_stop(raw,expected):
    if type(raw) is not bytes or len(raw)>1024:raise Denied('STOP_BYTES')
    def pairs(rows):
        d={}
        for k,v in rows:
            if k in d:raise Denied('STOP_DUPLICATE')
            d[k]=v
        return d
    v=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs)
    if not same(v,expected) or encoded(v)!=raw:raise Denied('STOP_SCOPE_OR_CANONICAL')
    return True
