"""Independent exact-stage template corpus; no process/Gate/claim bodies."""
from datetime import datetime,timezone,timedelta
import copy,json
def matrix(fp,p,t,pins):
 rows=[];raw=fp.encode(t);old=fp.sha(raw);now=datetime.now(timezone.utc)
 def test(name,d,expected,layer='INTERNAL_SYNTHETIC_OFFLINE_HASH',approved=None):
  b=fp.encode(d) if type(d) is dict else d;h=fp.sha(b) if approved is None else approved;actual='ACCEPT'
  try:fp.validate(b,h,p,pins,now=now)
  except (ValueError,TypeError,KeyError,UnicodeDecodeError) as e:actual=str(e)
  rows.append(dict(case=name,layer=layer,expected=expected,actual=actual,pass_=actual==expected,inputSha256=fp.sha(b),approvedSha256=h,pureOnly=True))
 test('independent-valid-offline',t,'ACCEPT')
 for k in t:
  d=copy.deepcopy(t);d[k]=None;test('old-approved-hash:'+k,d,'PREAUTH_EXTERNAL_HASH','FIXED_ORIGINAL_HASH',old)
  d=copy.deepcopy(t);d.pop(k);test('closed-field-delete:'+k,d,'PREAUTH_SCHEMA')
 d=copy.deepcopy(t);d['runSdkNow']=True;test('forbidden-extra-action',d,'PREAUTH_SCHEMA')
 test('duplicate-exact',raw.replace(b'"schema":',b'"schema":"x","schema":',1),'PREAUTH_DUPLICATE_FIELD')
 test('duplicate-case',raw.replace(b'"schema":',b'"SCHEMA":"x","schema":',1),'PREAUTH_DUPLICATE_FIELD')
 test('nonfinite',b'{"n":NaN}','PREAUTH_NONFINITE')
 test('old-hash-pretty-json',json.dumps(t,indent=2).encode(),'PREAUTH_EXTERNAL_HASH','FIXED_ORIGINAL_HASH',old)
 # Hash explicitly approves exact raw bytes. Compactness is observed separately.
 test('synthetic-approved-pretty-json',json.dumps(t,indent=2).encode(),'ACCEPT','RAW_HASH_SERIALIZATION_OBSERVATION')
 for k in ['sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256']:
  for v,reason in [('0'*64,'PREAUTH_HASH_TYPE:'+k),('A'*64,'PREAUTH_HASH_TYPE:'+k),('1'*64,'PREAUTH_PIN:'+k)]:
   d=copy.deepcopy(t);d[k]=v;test('internal-pin:'+k+':'+v[0],d,reason)
 for k in fp.LIMITS:
  for v in [True,float(fp.LIMITS[k]),fp.LIMITS[k]+1,fp.LIMITS[k]-1]:
   d=copy.deepcopy(t);d['limits'][k]=v;test('internal-budget:'+k+':'+repr(v),d,'PREAUTH_LIMITS')
 for k in ['sdk','device']:
  for field in t[k]:
   for v in [None,True,1.0,'EXTRA']:
    d=copy.deepcopy(t);d[k][field]=v;test('internal-fixed:'+k+':'+field+':'+repr(v),d,'PREAUTH_SDK_DEVICE')
 for i in range(7):
  for op in ['delete','extra','command','id']:
   d=copy.deepcopy(t)
   if op=='delete':d['queries'].pop(i)
   elif op=='extra':d['queries'][i]['shell']=True
   else:d['queries'][i][op]='UNAPPROVED'
   test('internal-query:'+str(i)+':'+op,d,'PREAUTH_QUERIES')
 for value in ['2026-10-23T00:00:00Z','2026-10-23T00:00:00','2026-10-23T00:00:00+01:00','2026-10-23T00:00:00.1234567+00:00',True,0]:
  d=copy.deepcopy(t);d['notBeforeUtc']=value;test('internal-utc:'+repr(value),d,'PREAUTH_UTC')
 for name,lo,hi in [('expired',-91,-1),('future',1,80),('over90',-1,90),('zero',0,0),('reverse',1,0)]:
  d=copy.deepcopy(t);d['notBeforeUtc']=(now+timedelta(seconds=lo)).isoformat();d['expiresUtc']=(now+timedelta(seconds=hi)).isoformat();test('internal-window:'+name,d,'PREAUTH_WINDOW')
 for k,v,code in [('schema','WRONG','PREAUTH_KIND_MODE'),('mode','LIVE','PREAUTH_POLICY_MODE'),('sourceThreadId','wrong','PREAUTH_SOURCE'),('sourceTurnId','wrong','PREAUTH_SOURCE'),('nonce','wrong','PREAUTH_NONCE_PLAN'),('planId','wrong','PREAUTH_NONCE_PLAN'),('runId','wrong','PREAUTH_RUN'),('scope','1'*64,'PREAUTH_POLICY_ID:scope'),('policySha256','1'*64,'PREAUTH_POLICY'),('home',t['home']+'-other','PREAUTH_HOME')]:
  d=copy.deepcopy(t);d[k]=v;test('internal-identity:'+k,d,code)
 return dict(cases=rows,total=len(rows),bad=[x for x in rows if not x['pass_']],productConstructors=0,allExternalApprovals='SYNTHETIC_OFFLINE_ONLY',signaturesOrHumanIdentityProven=False)
