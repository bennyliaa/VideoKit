"""Static JSON Schema assembly, no candidate import."""
from pathlib import Path
import json,ast
B=Path(__file__).resolve().parent
tree=ast.parse((B/'tools/fact_preauth.py').read_text())
keys=next(ast.literal_eval(n.value.args[0].func.value).split() for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='KEYS' for t in n.targets))
limits=dict(wholeSeconds=90,gateSeconds=30,qualificationSeconds=15,outerSeconds=30,proofSeconds=10,sdkChildren=1,stdoutBytes=139264,stderrBytes=8192,combinedBytes=147456,concurrency=1,retry=0)
def obj(props):return dict(type='object',additionalProperties=False,required=list(props),properties=props)
props={k:dict(type='string',minLength=1) for k in keys}
for k in keys:
 if k.endswith('Sha256') or k=='scope':props[k]=dict(type='string',pattern='^[0-9a-f]{64}$',**{'not':{'const':'0'*64}})
props['schema']={'const':'GLOBAL_IDLE_FACT_PREAUTH_V1'};props['mode']={'enum':['LIVE','OFFLINE_FIXTURE']}
props['sourceThreadId']={'const':'01a107c3-2bf9-7fa0-94a0-234258ca6774'}
for k in ('nonce','planId','sourceTurnId'):props[k]=dict(type='string',pattern='^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
for k in ('notBeforeUtc','expiresUtc'):props[k]=dict(type='string',pattern=r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?\+00:00$')
props['runId']=dict(type='string',pattern='^D1MA02-[A-Z0-9_-]{1,32}$')
props['limits']=obj({k:dict(type='integer',const=v) for k,v in limits.items()})
props['device']=obj(dict(serial={'const':'HA1Q6WXR'},model={'const':'TB138FC'},api=dict(type='integer',const=31),user=dict(type='integer',const=0)))
props['sdk']=obj(dict(path={'const':'D:/Android/SDK/platform-tools/adb.exe'},sha256={'const':'b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f'}))
queries=[('model','getprop ro.product.model'),('api','getprop ro.build.version.sdk'),('firmware','getprop ro.build.fingerprint'),('user','am get-current-user'),('system','cmd package list packages -s -U --user 0'),('role','dumpsys role'),('home','cmd package resolve-activity --brief --components --user 0 -a android.intent.action.MAIN -c android.intent.category.HOME')]
props['queries']=dict(type='array',minItems=7,maxItems=7,prefixItems=[obj(dict(id={'const':i},command={'const':c})) for i,c in queries],items=False)
d={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:videokit:global-idle-fact-preauth:v1',**obj(props),'$comment':'Runtime additionally enforces canonical paths, unique casefold keys, exact external digest/pins/policy, actual original object/owner/once, and <=90s UTC validity. Template generation gives no authority. JSON Schema integer semantics alone cannot exclude 1.0; Python exact type validator does.'}
bk='schema mode preauthSha256 scope planId runId nonce generation ownerPid ownerThread claimFileId scopeStartTick proofStartTick routeProofSha256 initialProofSha256 gateReceiptSha256 sourceSealSha256 gateSourcesSha256 binderSha256 boundAtUtc'.split()
bp={k:dict(type='integer',minimum=1) if k in ('ownerPid','ownerThread','claimFileId','scopeStartTick','proofStartTick') else dict(type='string',minLength=1) for k in bk}
bp['schema']={'const':'GLOBAL_IDLE_FACT_RUNTIME_BINDING_V1'};bp['mode']={'enum':['LIVE','OFFLINE_FIXTURE']}
for k in bk:
 if k.endswith('Sha256') or k=='scope':bp[k]=dict(type='string',pattern='^[0-9a-f]{64}$')
d['$defs']={'runtimeBinding':obj(bp),'captureV2Authorization':obj(dict(schema={'const':'GLOBAL_IDLE_FACT_CAPTURE_V2'},authorizationKind={'const':'GLOBAL_IDLE_FACT_PREAUTH_V1'},externalPreauthSha256=dict(type='string',pattern='^[0-9a-f]{64}$'),runtimeBindingSha256=dict(type='string',pattern='^[0-9a-f]{64}$')))}
p=B/'reference/fact-preauth-schema.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
