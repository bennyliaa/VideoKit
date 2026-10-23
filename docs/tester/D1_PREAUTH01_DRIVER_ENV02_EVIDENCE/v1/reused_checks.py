def reject(fn,expected=None):
 try:fn()
 except (ValueError,TypeError,KeyError) as e:
  if expected is not None:assert str(e)==expected,(expected,str(e))
  return str(e)
 raise AssertionError('EXPECTED_REJECTION')

def inputs(name):
 d=json.loads((H/'reference/prepared-inputs.json').read_bytes())[name];return copy.deepcopy(d['policy']),copy.deepcopy(d['template']),copy.deepcopy(d['pins'])

def pure_templates():
 p,t,pins=inputs('pure');raw=encode(t);approved=sha(raw);assert validate(raw,approved,p,pins)==t;cases=[]
 def check(label,d,expected=None,external=None):
  b=encode(d) if type(d) is dict else d
  cases.append(dict(case=label,reason=reject(lambda:validate(b,sha(b) if external is None else external,p,pins),expected)))
 for k in t:
  d=copy.deepcopy(t);d.pop(k);check('delete:'+k,d,'PREAUTH_SCHEMA')
  d=copy.deepcopy(t);d[k]=None;check('null:'+k,d)
 d=copy.deepcopy(t);d['extra']=True;check('extra',d,'PREAUTH_SCHEMA')
 check('case-duplicate',raw.replace(b'"schema":',b'"Schema":"x","schema":',1),'PREAUTH_DUPLICATE_FIELD')
 check('default-external',t,'PREAUTH_EXTERNAL_HASH',external='')
 check('wrong-external',t,'PREAUTH_EXTERNAL_HASH',external='a'*64)
 d=copy.deepcopy(t);d['sourceTurnId']=str(uuid.uuid4());check('caller-generated-not-external-approved',d,'PREAUTH_EXTERNAL_HASH',external=approved)
 for k in ('scope','sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256','policySha256'):
  d=copy.deepcopy(t);d[k]='1'*64;check('changed:'+k,d)
 for k in LIMITS:
  for v in (True,float(LIMITS[k]),LIMITS[k]+1):
   d=copy.deepcopy(t);d['limits'][k]=v;check('budget:'+k+':'+repr(v),d,'PREAUTH_LIMITS')
 for k in ('sdk','device'):
  for field in t[k]:
   d=copy.deepcopy(t);d[k].pop(field);check('nested-delete:'+k+':'+field,d)
   d=copy.deepcopy(t);d[k][field]=True;check('nested-change:'+k+':'+field,d)
 for i in range(7):
  for field in ('id','command'):
   d=copy.deepcopy(t);d['queries'][i][field]='UNAPPROVED';check('query:'+str(i)+':'+field,d,'PREAUTH_QUERIES')
 d=copy.deepcopy(t);d['queries'].reverse();check('query-order',d,'PREAUTH_QUERIES')
 for label,lo,hi in [('expired',-100,-10),('future',10,80),('too-long',-1,91),('reversed',2,1)]:
  d=copy.deepcopy(t);now=datetime.now(timezone.utc);d.update(notBeforeUtc=(now+timedelta(seconds=lo)).isoformat(),expiresUtc=(now+timedelta(seconds=hi)).isoformat());check(label,d,'PREAUTH_WINDOW')
 for k,v in [('schema','GLOBAL_IDLE_FACT_AUTHORITY_V1'),('mode','LIVE'),('mode','live'),('sourceThreadId',str(uuid.uuid4())),('nonce','OLD'),('planId','OLD'),('home',str(B/'elsewhere')),('runId','OLD')]:
  d=copy.deepcopy(t);d[k]=v;check('identity:'+k+':'+v,d)
 # No constructor or existing claim is involved in these gate identity models.
 ticket=object.__new__(PreparedFacts);ticket.owner=(os.getpid(),threading.get_ident());ticket.gate=object();ticket.template=t;ticket.policy=p
 cases.append(dict(case='wrong-original-gate-model',reason=reject(lambda:ticket.current(object()),'PREAUTH_ORIGINAL_PREPARED_GATE')))
 ticket.owner=(os.getpid(),-1);cases.append(dict(case='wrong-owner-model',reason=reject(lambda:ticket.current(object()),'PREAUTH_ORIGINAL_OWNER')))
 # Registry model covers exact scope/plan/run/nonce already consumed.
 ticket2=PreparedFacts(raw,approved,p);cases.append(dict(case='preauth-replay-before-gate',reason=reject(lambda:PreparedFacts(raw,approved,p),'PREAUTH_REPLAY')));assert ticket2.gate is None
 argv=[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'];assert validate_fixture_argv(argv)==argv
 bad=argv.copy();bad[0]='D:/Android/SDK/platform-tools/adb.exe';cases.append(dict(case='wrong-fact-program-pure',reason=reject(lambda:validate_fixture_argv(bad),'FACT_FIXTURE_ARGV')))
 save(W/'template-cases.json',cases);return dict(negative=len(cases),positive=1,allConstructorsForNegatives=0,externalFixtureIsSynthetic=True)

def prestart():
 c,b,e=child([PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/prestart_lifetimes.ps1'),'-OutputFile',str(W/'prestart.json')]);d=json.loads((W/'prestart.json').read_text(encoding='utf-8-sig'));assert c==0 and not e and d['allPassed'];return d
