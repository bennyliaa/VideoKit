"""Fixed facts preauthorization. External CLI digest is a trust input, not an issuer.

No legacy-authority synthesis; no signing/IPC or qualification issuance.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,os,threading,uuid,time
B=Path(__file__).resolve().parents[1]
COORDINATOR='01a107c3-2bf9-7fa0-94a0-234258ca6774'
FACT_PREAUTH_SCHEMA07_RAW='{\r\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\r\n  "$id": "urn:videokit:global-idle-fact-preauth:v1",\r\n  "type": "object",\r\n  "additionalProperties": false,\r\n  "required": [\r\n    "schema",\r\n    "mode",\r\n    "sourceThreadId",\r\n    "sourceTurnId",\r\n    "notBeforeUtc",\r\n    "expiresUtc",\r\n    "scope",\r\n    "planId",\r\n    "runId",\r\n    "nonce",\r\n    "home",\r\n    "evidenceRoot",\r\n    "policySha256",\r\n    "sourceSealSha256",\r\n    "gateSourcesSha256",\r\n    "collectorSha256",\r\n    "binderSha256",\r\n    "entrySha256",\r\n    "runtimeIdentitySha256",\r\n    "sdk",\r\n    "factPlanSha256",\r\n    "device",\r\n    "queries",\r\n    "limits"\r\n  ],\r\n  "properties": {\r\n    "schema": {\r\n      "const": "GLOBAL_IDLE_FACT_PREAUTH_V1"\r\n    },\r\n    "mode": {\r\n      "enum": [\r\n        "LIVE",\r\n        "OFFLINE_FIXTURE"\r\n      ]\r\n    },\r\n    "sourceThreadId": {\r\n      "const": "01a107c3-2bf9-7fa0-94a0-234258ca6774"\r\n    },\r\n    "sourceTurnId": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"\r\n    },\r\n    "notBeforeUtc": {\r\n      "type": "string",\r\n      "pattern": "^\\\\d{4}-\\\\d\\\\d-\\\\d\\\\dT\\\\d\\\\d:\\\\d\\\\d:\\\\d\\\\d(?:\\\\.\\\\d{1,6})?\\\\+00:00$"\r\n    },\r\n    "expiresUtc": {\r\n      "type": "string",\r\n      "pattern": "^\\\\d{4}-\\\\d\\\\d-\\\\d\\\\dT\\\\d\\\\d:\\\\d\\\\d:\\\\d\\\\d(?:\\\\.\\\\d{1,6})?\\\\+00:00$"\r\n    },\r\n    "scope": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{64}$",\r\n      "not": {\r\n        "const": "0000000000000000000000000000000000000000000000000000000000000000"\r\n      }\r\n    },\r\n    "planId": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"\r\n    },\r\n    "runId": {\r\n      "type": "string",\r\n      "pattern": "^D1MA02-[A-Z0-9_-]{1,32}$"\r\n    },\r\n    "nonce": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"\r\n    },\r\n    "home": {\r\n      "type": "string",\r\n      "minLength": 1\r\n    },\r\n    "evidenceRoot": {\r\n      "type": "string",\r\n      "minLength": 1\r\n    },\r\n    "policySha256": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{64}$",\r\n      "not": {\r\n        "const": "0000000000000000000000000000000000000000000000000000000000000000"\r\n      }\r\n    },\r\n    "sourceSealSha256": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{64}$",\r\n      "not": {\r\n        "const": "0000000000000000000000000000000000000000000000000000000000000000"\r\n      }\r\n    },\r\n    "gateSourcesSha256": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{64}$",\r\n      "not": {\r\n        "const": "0000000000000000000000000000000000000000000000000000000000000000"\r\n      }\r\n    },\r\n    "collectorSha256": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{64}$",\r\n      "not": {\r\n        "const": "0000000000000000000000000000000000000000000000000000000000000000"\r\n      }\r\n    },\r\n    "binderSha256": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{64}$",\r\n      "not": {\r\n        "const": "0000000000000000000000000000000000000000000000000000000000000000"\r\n      }\r\n    },\r\n    "entrySha256": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{64}$",\r\n      "not": {\r\n        "const": "0000000000000000000000000000000000000000000000000000000000000000"\r\n      }\r\n    },\r\n    "runtimeIdentitySha256": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{64}$",\r\n      "not": {\r\n        "const": "0000000000000000000000000000000000000000000000000000000000000000"\r\n      }\r\n    },\r\n    "sdk": {\r\n      "type": "object",\r\n      "additionalProperties": false,\r\n      "required": [\r\n        "path",\r\n        "sha256"\r\n      ],\r\n      "properties": {\r\n        "path": {\r\n          "const": "D:/Android/SDK/platform-tools/adb.exe"\r\n        },\r\n        "sha256": {\r\n          "const": "b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f"\r\n        }\r\n      }\r\n    },\r\n    "factPlanSha256": {\r\n      "type": "string",\r\n      "pattern": "^[0-9a-f]{64}$",\r\n      "not": {\r\n        "const": "0000000000000000000000000000000000000000000000000000000000000000"\r\n      }\r\n    },\r\n    "device": {\r\n      "type": "object",\r\n      "additionalProperties": false,\r\n      "required": [\r\n        "serial",\r\n        "model",\r\n        "api",\r\n        "user"\r\n      ],\r\n      "properties": {\r\n        "serial": {\r\n          "const": "HA1Q6WXR"\r\n        },\r\n        "model": {\r\n          "const": "TB138FC"\r\n        },\r\n        "api": {\r\n          "type": "integer",\r\n          "const": 31\r\n        },\r\n        "user": {\r\n          "type": "integer",\r\n          "const": 0\r\n        }\r\n      }\r\n    },\r\n    "queries": {\r\n      "type": "array",\r\n      "minItems": 7,\r\n      "maxItems": 7,\r\n      "prefixItems": [\r\n        {\r\n          "type": "object",\r\n          "additionalProperties": false,\r\n          "required": [\r\n            "id",\r\n            "command"\r\n          ],\r\n          "properties": {\r\n            "id": {\r\n              "const": "model"\r\n            },\r\n            "command": {\r\n              "const": "getprop ro.product.model"\r\n            }\r\n          }\r\n        },\r\n        {\r\n          "type": "object",\r\n          "additionalProperties": false,\r\n          "required": [\r\n            "id",\r\n            "command"\r\n          ],\r\n          "properties": {\r\n            "id": {\r\n              "const": "api"\r\n            },\r\n            "command": {\r\n              "const": "getprop ro.build.version.sdk"\r\n            }\r\n          }\r\n        },\r\n        {\r\n          "type": "object",\r\n          "additionalProperties": false,\r\n          "required": [\r\n            "id",\r\n            "command"\r\n          ],\r\n          "properties": {\r\n            "id": {\r\n              "const": "firmware"\r\n            },\r\n            "command": {\r\n              "const": "getprop ro.build.fingerprint"\r\n            }\r\n          }\r\n        },\r\n        {\r\n          "type": "object",\r\n          "additionalProperties": false,\r\n          "required": [\r\n            "id",\r\n            "command"\r\n          ],\r\n          "properties": {\r\n            "id": {\r\n              "const": "user"\r\n            },\r\n            "command": {\r\n              "const": "am get-current-user"\r\n            }\r\n          }\r\n        },\r\n        {\r\n          "type": "object",\r\n          "additionalProperties": false,\r\n          "required": [\r\n            "id",\r\n            "command"\r\n          ],\r\n          "properties": {\r\n            "id": {\r\n              "const": "system"\r\n            },\r\n            "command": {\r\n              "const": "cmd package list packages -s -U --user 0"\r\n            }\r\n          }\r\n        },\r\n        {\r\n          "type": "object",\r\n          "additionalProperties": false,\r\n          "required": [\r\n            "id",\r\n            "command"\r\n          ],\r\n          "properties": {\r\n            "id": {\r\n              "const": "role"\r\n            },\r\n            "command": {\r\n              "const": "dumpsys role"\r\n            }\r\n          }\r\n        },\r\n        {\r\n          "type": "object",\r\n          "additionalProperties": false,\r\n          "required": [\r\n            "id",\r\n            "command"\r\n          ],\r\n          "properties": {\r\n            "id": {\r\n              "const": "home"\r\n            },\r\n            "command": {\r\n              "const": "cmd package resolve-activity --brief --components --user 0 -a android.intent.action.MAIN -c android.intent.category.HOME"\r\n            }\r\n          }\r\n        }\r\n      ],\r\n      "items": false\r\n    },\r\n    "limits": {\r\n      "type": "object",\r\n      "additionalProperties": false,\r\n      "required": [\r\n        "wholeSeconds",\r\n        "gateSeconds",\r\n        "qualificationSeconds",\r\n        "outerSeconds",\r\n        "proofSeconds",\r\n        "sdkChildren",\r\n        "stdoutBytes",\r\n        "stderrBytes",\r\n        "combinedBytes",\r\n        "concurrency",\r\n        "retry"\r\n      ],\r\n      "properties": {\r\n        "wholeSeconds": {\r\n          "type": "integer",\r\n          "const": 90\r\n        },\r\n        "gateSeconds": {\r\n          "type": "integer",\r\n          "const": 30\r\n        },\r\n        "qualificationSeconds": {\r\n          "type": "integer",\r\n          "const": 15\r\n        },\r\n        "outerSeconds": {\r\n          "type": "integer",\r\n          "const": 30\r\n        },\r\n        "proofSeconds": {\r\n          "type": "integer",\r\n          "const": 10\r\n        },\r\n        "sdkChildren": {\r\n          "type": "integer",\r\n          "const": 1\r\n        },\r\n        "stdoutBytes": {\r\n          "type": "integer",\r\n          "const": 139264\r\n        },\r\n        "stderrBytes": {\r\n          "type": "integer",\r\n          "const": 8192\r\n        },\r\n        "combinedBytes": {\r\n          "type": "integer",\r\n          "const": 147456\r\n        },\r\n        "concurrency": {\r\n          "type": "integer",\r\n          "const": 1\r\n        },\r\n        "retry": {\r\n          "type": "integer",\r\n          "const": 0\r\n        }\r\n      }\r\n    }\r\n  },\r\n  "$comment": "Runtime additionally enforces canonical paths, unique casefold keys, exact external digest/pins/policy, actual original object/owner/once, and <=90s UTC validity. Template generation gives no authority. JSON Schema integer semantics alone cannot exclude 1.0; Python exact type validator does.",\r\n  "$defs": {\r\n    "runtimeBinding": {\r\n      "type": "object",\r\n      "additionalProperties": false,\r\n      "required": [\r\n        "schema",\r\n        "mode",\r\n        "preauthSha256",\r\n        "scope",\r\n        "planId",\r\n        "runId",\r\n        "nonce",\r\n        "generation",\r\n        "ownerPid",\r\n        "ownerThread",\r\n        "claimFileId",\r\n        "scopeStartTick",\r\n        "proofStartTick",\r\n        "routeProofSha256",\r\n        "initialProofSha256",\r\n        "gateReceiptSha256",\r\n        "sourceSealSha256",\r\n        "gateSourcesSha256",\r\n        "binderSha256",\r\n        "boundAtUtc"\r\n      ],\r\n      "properties": {\r\n        "schema": {\r\n          "const": "GLOBAL_IDLE_FACT_RUNTIME_BINDING_V1"\r\n        },\r\n        "mode": {\r\n          "enum": [\r\n            "LIVE",\r\n            "OFFLINE_FIXTURE"\r\n          ]\r\n        },\r\n        "preauthSha256": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        },\r\n        "scope": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        },\r\n        "planId": {\r\n          "type": "string",\r\n          "minLength": 1\r\n        },\r\n        "runId": {\r\n          "type": "string",\r\n          "minLength": 1\r\n        },\r\n        "nonce": {\r\n          "type": "string",\r\n          "minLength": 1\r\n        },\r\n        "generation": {\r\n          "type": "string",\r\n          "minLength": 1\r\n        },\r\n        "ownerPid": {\r\n          "type": "integer",\r\n          "minimum": 1\r\n        },\r\n        "ownerThread": {\r\n          "type": "integer",\r\n          "minimum": 1\r\n        },\r\n        "claimFileId": {\r\n          "type": "integer",\r\n          "minimum": 1\r\n        },\r\n        "scopeStartTick": {\r\n          "type": "integer",\r\n          "minimum": 1\r\n        },\r\n        "proofStartTick": {\r\n          "type": "integer",\r\n          "minimum": 1\r\n        },\r\n        "routeProofSha256": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        },\r\n        "initialProofSha256": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        },\r\n        "gateReceiptSha256": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        },\r\n        "sourceSealSha256": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        },\r\n        "gateSourcesSha256": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        },\r\n        "binderSha256": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        },\r\n        "boundAtUtc": {\r\n          "type": "string",\r\n          "minLength": 1\r\n        }\r\n      }\r\n    },\r\n    "captureV2Authorization": {\r\n      "type": "object",\r\n      "additionalProperties": false,\r\n      "required": [\r\n        "schema",\r\n        "authorizationKind",\r\n        "externalPreauthSha256",\r\n        "runtimeBindingSha256"\r\n      ],\r\n      "properties": {\r\n        "schema": {\r\n          "const": "GLOBAL_IDLE_FACT_CAPTURE_V2"\r\n        },\r\n        "authorizationKind": {\r\n          "const": "GLOBAL_IDLE_FACT_PREAUTH_V1"\r\n        },\r\n        "externalPreauthSha256": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        },\r\n        "runtimeBindingSha256": {\r\n          "type": "string",\r\n          "pattern": "^[0-9a-f]{64}$"\r\n        }\r\n      }\r\n    }\r\n  }\r\n}\r\n'
FACT_PREAUTH_SCHEMA07=json.loads(FACT_PREAUTH_SCHEMA07_RAW)
KEYS=set(FACT_PREAUTH_SCHEMA07['required'])
assert FACT_PREAUTH_SCHEMA07['additionalProperties'] is False and FACT_PREAUTH_SCHEMA07['properties']['schema']['const']=='GLOBAL_IDLE_FACT_PREAUTH_V1'
LIMITS=dict(wholeSeconds=90,gateSeconds=30,qualificationSeconds=15,outerSeconds=30,proofSeconds=10,sdkChildren=1,stdoutBytes=139264,stderrBytes=8192,combinedBytes=147456,concurrency=1,retry=0)
USED=set()
def fail(code):raise ValueError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(d):return (json.dumps(d,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def decode(raw):
 if type(raw) is not bytes or not 1<=len(raw)<=16384:fail('PREAUTH_BYTES')
 def pairs(xs):
  d={};seen=set()
  for k,v in xs:
   if k.casefold() in seen:fail('PREAUTH_DUPLICATE_FIELD')
   seen.add(k.casefold());d[k]=v
  return d
 return json.loads(raw.decode('utf-8','strict'),object_pairs_hook=pairs,parse_constant=lambda _:fail('PREAUTH_NONFINITE'))
def same(a,b):
 if type(a) is not type(b):return False
 if type(a) is dict:return set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if type(a) is list:return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return a==b
def digest(v):return type(v) is str and re.fullmatch('[0-9a-f]{64}',v) is not None and v!='0'*64
def utc(v):
 if type(v) is not str or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?\+00:00',v):fail('PREAUTH_UTC')
 return datetime.fromisoformat(v)
def uuid_text(v):
 try:return type(v) is str and str(uuid.UUID(v))==v
 except ValueError:return False
def validate(raw,approved_template_sha256,policy,pins,now=None):
 # The trusted invocation supplies this digest, never default to sha(raw).
 if type(raw) is not bytes or not digest(approved_template_sha256) or sha(raw)!=approved_template_sha256:fail('PREAUTH_EXTERNAL_HASH')
 t=decode(raw)
 if type(t) is not dict or set(t)!=KEYS:fail('PREAUTH_SCHEMA')
 if t['schema']!='GLOBAL_IDLE_FACT_PREAUTH_V1' or t['mode'] not in ('LIVE','OFFLINE_FIXTURE'):fail('PREAUTH_KIND_MODE')
 if t['sourceThreadId']!=COORDINATOR or not uuid_text(t['sourceTurnId']):fail('PREAUTH_SOURCE')
 if not uuid_text(t['nonce']) or not uuid_text(t['planId']):fail('PREAUTH_NONCE_PLAN')
 if type(t['runId']) is not str or not re.fullmatch('D1MA02-[A-Z0-9_-]{1,32}',t['runId']):fail('PREAUTH_RUN')
 for k in ('scope','policySha256','sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256'):
  if not digest(t[k]):fail('PREAUTH_HASH_TYPE:'+k)
 if not same(t['limits'],LIMITS):fail('PREAUTH_LIMITS')
 if not same(t['sdk'],pins['sdk']) or not same(t['device'],dict(serial='HA1Q6WXR',model='TB138FC',api=31,user=0)):fail('PREAUTH_SDK_DEVICE')
 if not same(t['queries'],pins['queries']):fail('PREAUTH_QUERIES')
 for k in ('sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256'):
  if t[k]!=pins[k]:fail('PREAUTH_PIN:'+k)
 if type(policy) is not dict or sha(encode(policy))!=t['policySha256']:fail('PREAUTH_POLICY')
 mode='OFFLINE_FIXTURE' if policy.get('mode')=='OFFLINE_FIXTURE' else 'LIVE' if policy.get('mode')=='PRODUCTION' else None
 if t['mode']!=mode:fail('PREAUTH_POLICY_MODE')
 for k in ('scope','planId','runId','evidenceRoot'):
  if type(t[k]) is not str or t[k]!=policy.get(k):fail('PREAUTH_POLICY_ID:'+k)
 if t['home']!=str(Path(t['evidenceRoot']).parent) or Path(t['evidenceRoot']).name!='outputs':fail('PREAUTH_HOME')
 for k in ('home','evidenceRoot'):
  if type(t[k]) is not str or not Path(t[k]).is_absolute() or str(Path(t[k]).resolve())!=t[k]:fail('PREAUTH_CANONICAL_PATH')
 for k in ('gateSourcesSha256','runtimeIdentitySha256'):
  if policy.get(k)!=t[k]:fail('PREAUTH_POLICY_PIN:'+k)
 if policy.get('entrySha256')!=pins['captureSha256'] or policy.get('outerOwnerSha256')!=pins['ownerSha256'] or policy.get('planSha256')!=pins['rolePlanSha256']:fail('PREAUTH_POLICY_SOURCES')
 lo=utc(t['notBeforeUtc']);hi=utc(t['expiresUtc']);now=now or datetime.now(timezone.utc)
 if not 0<(hi-lo).total_seconds()<=90 or not lo<=now<hi:fail('PREAUTH_WINDOW')
 return t
def load_pins(read):
 from fact_collector import QUERIES,SDK,SDK_SHA
 raw=read(B/'reference/runner-source-seal.json');seal=json.loads(raw);sources=seal['sources']
 # Gate independently hashes its fixed sources (including this binder+schema+CLI).
 return dict(sourceSealSha256=sha(raw),gateSourcesSha256=sources['reference/gate-sources.json'],collectorSha256=sources['tools/fact_collector.py'],binderSha256=sources['tools/fact_preauth.py'],entrySha256=sources['tools/facts_entry.py'],runtimeIdentitySha256=sources['reference/current-runtime-identity.json'],factPlanSha256=sources['reference/fact-plan.json'],captureSha256=sources['tools/capture_android02.ps1'],ownerSha256=sources['tools/outer_owner.py'],rolePlanSha256=sources['reference/exact-seven-role-plan.json'],sdk=dict(path=SDK,sha256=SDK_SHA),queries=[dict(id=i,command=c) for i,c in QUERIES])
def binding_bytes(actual,expected):
 decode(actual)
 if type(expected) is not bytes or actual!=expected:fail('PREAUTH_BINDING_ONCE_BYTES')
 return True
# Complete source plan is a pure function; caller supplies metadata only.
def complete_source_plan(policy,gate_files,runtime_files,size_map,raw_path=None,raw_bytes=0):
 rows=[];fixture=policy['mode']=='OFFLINE_FIXTURE';scope=policy['scope']
 def add(stage,owner,path,kind,charged):
  if type(charged) is not int or charged<0:fail('FACT_SOURCE_PLAN_AMOUNT')
  rows.append(dict(index=len(rows),scope=scope,stage=stage,owner=owner,path=str(path),kind=kind,chargedBytes=charged,reads=1))
 def read(stage,path,kind='read',owner='ORIGINAL_GATE',plus=1):add(stage,owner,path,kind,size_map[str(path)]+plus)
 if raw_path is not None:add('caller-raw','ORIGINAL_ENTRY',raw_path,'adopted-read',raw_bytes)
 read('preauth',B/'reference/runner-source-seal.json','preauth-read','ORIGINAL_PREAUTH',0)
 for rel in ('reference/gate-sources.json','tools/fact_collector.py','tools/fact_preauth.py','tools/facts_entry.py','reference/fact-plan.json'):read('preauth',B/rel,'preauth-read','ORIGINAL_PREAUTH',0)
 read('gate-constructor',B/'reference/gate-sources.json')
 for e in gate_files:read('gate-constructor',B/e['path'])
 read('gate-constructor',B/'tools/runtime_binding.py');read('gate-constructor',B/'reference/current-runtime-identity.json')
 for path in [B/'reference/current-runtime-identity.json']*2+[Path(e['path']) for e in runtime_files]:read('fixed-runtime','runtime-placeholder' if False else path,'runtime-reservation','ORIGINAL_GATE_FOR_FIXED_HELPER',0)
 if not fixture:read('gate-local-authority',Path(policy['gateAuthorization']['path']))
 if fixture:
  read('route-child-reservation',B/'selfchecks/route_fixture.py','route-child-reservation','ORIGINAL_GATE_FOR_FIXED_CHILD',0)
  read('route-preconstructor',B/'reference/runner-source-seal.json');read('route-preconstructor',B/'selfchecks/route_fixture.py')
 else:
  read('route-child-reservation',B/'tools/win32_route.py','route-child-reservation','ORIGINAL_GATE_FOR_FIXED_CHILD',0)
  add('native-image-reservation','ORIGINAL_ROUTE_CHECKER','D:/Android/SDK/platform-tools/adb.exe','native-reservation',8273560)
 read('route-validation',B/('selfchecks/route_fixture.py' if fixture else 'tools/win32_route.py'));read('route-validation',B/'reference/route-backend-contract.json')
 for rel in ('reference/runner-source-seal.json','tools/fact_preauth.py','tools/fact_collector.py','tools/facts_entry.py','reference/fact-plan.json'):read('facts-receive',B/rel)
 if fixture:
  if raw_path is not None:
   read('fixture-raw',raw_path);add('fixture-child-reservation','ORIGINAL_GATE_FOR_FIXED_CHILD',raw_path,'child-reservation',raw_bytes)
  read('fixture-runtime',B/'reference/current-runtime-identity.json');read('fixture-runtime',Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'))
  read('facts-preconstructor',B/'reference/runner-source-seal.json');read('facts-preconstructor',B/'selfchecks/fact_fixture.py')
 else:read('facts-sdk',Path('D:/Android/SDK/platform-tools/adb.exe'))
 plan=dict(schema='FACT_COMPLETE_SOURCE_PLAN06_V1',scope=scope,rows=rows,sourceReads=len(rows),sourceBytes=sum(x['chargedBytes'] for x in rows),capReads=64,capBytes=268435456,GateOrClaimOrPopenRequired=False)
 check_complete_source_plan(plan);return plan

def check_complete_source_plan(plan):
 if type(plan) is not dict or type(plan.get('rows')) is not list or any(type(x) is not dict or type(x.get('chargedBytes')) is not int or x['chargedBytes']<0 or x.get('reads')!=1 or type(x.get('reads')) is not int for x in plan['rows']):fail('FACT_SOURCE_PLAN_SCHEMA')
 if plan.get('sourceReads')!=len(plan['rows']) or plan.get('sourceBytes')!=sum(x['chargedBytes'] for x in plan['rows']):fail('FACT_SOURCE_PLAN_TOTAL')
 if plan['sourceReads']>64 or plan['sourceBytes']>268435456:fail('FACT_COMPLETE_SOURCE_BUDGET_BEFORE_USED')
 return True

FACT_RUNTIME_FILES06=[{'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe', 'bytes': 107312, 'sha256': '5640e9be2fd33d05a1a9ae1228e2354609a69ab831605995ec4e2bd6da8fff5e', 'kind': 'interpreter-executable'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python312.dll', 'bytes': 6985520, 'sha256': '886fa6b89e09ca6c87599c802402fdca160e06b2fa9c658f6fe91ed926f63e1f', 'kind': 'interpreter-dll'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python3.dll', 'bytes': 71984, 'sha256': '62845ba25fcd76557c127b01b9dc6680845f8a4acb97fadf72035d7a6eb2d2d3', 'kind': 'stable-abi-dll'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\vcruntime140.dll', 'bytes': 124544, 'sha256': 'd5e4d9a3e835fa679450145d6a7d94e36573a509317111904d9b3712c30d9066', 'kind': 'runtime-dll'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\vcruntime140_1.dll', 'bytes': 49792, 'sha256': '1f2d41c4aa5db0bc33ebf7b66d72943a817d7ce6cbe880502a9403823633093f', 'kind': 'runtime-dll'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\native\\powershell\\pwsh.exe', 'bytes': 301368, 'sha256': '362a356ce7f0940ec74f73a8fc2c990a2cc24a38a11c90bbd8eca947110ad139', 'kind': 'fixed-capture-host'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\runtime.json', 'bytes': 620, 'sha256': '73e85298033657d24d532e316c7823b7316866d7828e42361010632a36e4f9d3', 'kind': 'configured-bundle-manifest'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\LICENSE.txt', 'bytes': 25066, 'sha256': '886a0ead2d89030ee62dbff52b04e47ab91998341295bb9c56fb952b4e081c7a', 'kind': 'runtime-license'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\Lib\\json\\__init__.py', 'bytes': 14020, 'sha256': 'd5d41e2c29049515d295d81a6d40b4890fbec8d8482cfb401630f8ef2f77e4d5', 'kind': 'stdlib-source-or-extension-not-loaded-bytecode-attestation'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\Lib\\threading.py', 'bytes': 60200, 'sha256': '846f450ae794e4aab823a163f8c71d27751148af33e91dd3de886686a4e8ebfb', 'kind': 'stdlib-source-or-extension-not-loaded-bytecode-attestation'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\Lib\\subprocess.py', 'bytes': 88747, 'sha256': '85d29b2bf0249f5436838298c9a60ee93508b1102e9ac43b001f8a7e7ae8f375', 'kind': 'stdlib-source-or-extension-not-loaded-bytecode-attestation'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\Lib\\os.py', 'bytes': 40821, 'sha256': '54c43a1fc69c979c70d8f7d097174cee163bfe59937723ee353043dd4a0211e1', 'kind': 'stdlib-source-or-extension-not-loaded-bytecode-attestation'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\Lib\\encodings\\utf_8.py', 'bytes': 1005, 'sha256': 'ba0cac060269583523ca9506473a755203037c57d466a11aa89a30a5f6756f3d', 'kind': 'stdlib-source-or-extension-not-loaded-bytecode-attestation'}, {'path': 'C:\\Users\\benny\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\DLLs\\_hashlib.pyd', 'bytes': 70448, 'sha256': '00f94f34de2637c87dba0209ef22d728e90fa519ae46bde39df60df725dff496', 'kind': 'stdlib-source-or-extension-not-loaded-bytecode-attestation'}]

class PreparedFacts:
 def __init__(self,raw,approved_template_sha256,policy,fixture_raw=None):
  self.owner=(os.getpid(),threading.get_ident());self.bytes=raw;self.approved=approved_template_sha256
  self.policy=decode(encode(policy));self.sourceBytes=0;self.sourceReads=0;self.controlBytes=len(raw)+len(encode(policy));self.gate=None;self.used=False;self.prepareEntered=False;self.binding=None
  self.checked_files={};self.sourceEvents=[]
  raw_path=None
  if fixture_raw is not None:
   if self.policy['mode']!='OFFLINE_FIXTURE' or type(fixture_raw) is not bytes or not 1<=len(fixture_raw)<=139264:fail('FACT_ADOPTED_RAW_TYPE')
   raw_path=Path(self.policy['evidenceRoot']).parent.parent/'fixture-facts.raw'
   self.sourceBytes=len(fixture_raw);self.sourceReads=1;self.sourceEvents.append(dict(index=0,path=str(raw_path),scope=self.policy['scope'],kind='adopted-read',chargedBytes=len(fixture_raw),actualBytes=len(fixture_raw),originalCloseReturned=True))
  def read(p):
   from entry_gates import no_links
   no_links(p);b=Path(p).read_bytes();self.sourceBytes+=len(b);self.sourceReads+=1
   self.checked_files[str(Path(p))]=b;self.sourceEvents.append(dict(index=len(self.sourceEvents),path=str(Path(p)),scope=self.policy['scope'],kind='preauth-read',chargedBytes=len(b),actualBytes=len(b),originalCloseReturned=True))
   if self.sourceBytes>268435456 or self.sourceReads>64:fail('PREAUTH_SOURCE_BOUND')
   return b
  self.pins=load_pins(read);self.template=validate(raw,approved_template_sha256,self.policy,self.pins)
  # The actual fixed gate/collector/binder/entry pins are verified before Gate.
  for rel,k in [('reference/gate-sources.json','gateSourcesSha256'),('tools/fact_collector.py','collectorSha256'),('tools/fact_preauth.py','binderSha256'),('tools/facts_entry.py','entrySha256'),('reference/fact-plan.json','factPlanSha256')]:
   if sha(read(B/rel))!=self.pins[k]:fail('PREAUTH_CURRENT_SOURCE:'+rel)
  gate_files=json.loads(self.checked_files[str(B/'reference/gate-sources.json')])['files']
  paths={B/'reference/runner-source-seal.json',B/'reference/gate-sources.json',B/'tools/runtime_binding.py',B/'reference/current-runtime-identity.json',B/'selfchecks/route_fixture.py',B/'selfchecks/fact_fixture.py',B/'reference/route-backend-contract.json',B/'tools/win32_route.py',B/'tools/fact_preauth.py',B/'tools/fact_collector.py',B/'tools/facts_entry.py',B/'reference/fact-plan.json'}
  paths.update(B/e['path'] for e in gate_files);paths.update(Path(e['path']) for e in FACT_RUNTIME_FILES06)
  if raw_path is not None:paths.add(raw_path)
  sizes={str(x):x.stat().st_size for x in paths}
  if self.template['mode']=='LIVE':
   auth=Path(self.policy['gateAuthorization']['path']);sizes[str(auth)]=auth.stat().st_size;sizes[str(Path('D:/Android/SDK/platform-tools/adb.exe'))]=8273560
  self.sourcePlan=complete_source_plan(self.policy,gate_files,FACT_RUNTIME_FILES06,sizes,raw_path,len(fixture_raw) if fixture_raw is not None else 0)
  self.admittedBeforeUsed=True
  key=(self.template['scope'],self.template['planId'],self.template['runId'],self.template['nonce'])
  if key in USED:fail('PREAUTH_REPLAY')
  USED.add(key) # no refund/rearm, including later known rejection
 def holder(self):
  if self.owner!=(os.getpid(),threading.get_ident()):fail('PREAUTH_ORIGINAL_OWNER')
 def prepare(self):
  self.holder()
  if self.prepareEntered or self.used:fail('PREAUTH_PREPARE_ONCE')
  self.prepareEntered=True
  validate(self.bytes,self.approved,self.policy,self.pins)
  from entry_gates import GateSession,no_links
  home=Path(self.template['home']);no_links(home)
  if (home/'outputs').exists():fail('PREAUTH_FRESH_OUTPUT_REQUIRED')
  (home/'outputs').mkdir(parents=True,exist_ok=False)
  self.gate=GateSession(home,policy=self.policy,pre_events=[dict(event='preauth-template-policy-read',bytes=self.controlBytes)],complete_source_plan=self.sourcePlan,seed_source_events=self.sourceEvents)
  if self.gate.source_events[:len(self.sourceEvents)]!=self.sourceEvents:fail('FACT_ORIGINAL_SEED_CHANGED')
  if self.gate.source_bytes>268435456 or self.gate.source_reads>64:fail('SOURCE_READ_BUDGET')
  self.gate.whole=90 # narrower facts whole window, no expansion of original gates
  self.gate.prepare();return self.gate
 def current(self,gate):
  from entry_gates import GateSession
  self.holder()
  if type(gate) is not GateSession or gate is not self.gate or not gate.prepared or gate.accepted or gate.sdk_owner is not None or gate.released or gate.failure:fail('PREAUTH_ORIGINAL_PREPARED_GATE')
  if gate.scope!=self.template['scope'] or not same(gate.policy,self.policy):fail('PREAUTH_GATE_IDENTITY')
  gate.assert_held();gate.observe(gate.proof_start,10);gate.require()
  validate(self.bytes,self.approved,self.policy,self.pins)
 def bind(self,gate):
  self.current(gate)
  if self.used or self.binding is not None:fail('PREAUTH_BIND_ONCE')
  self.used=True
  from entry_gates import decode as gate_decode
  binding=dict(schema='GLOBAL_IDLE_FACT_RUNTIME_BINDING_V1',mode=self.template['mode'],preauthSha256=self.approved,scope=gate.scope,planId=gate.policy['planId'],runId=gate.policy['runId'],nonce=self.template['nonce'],generation=gate.generation,ownerPid=gate.pid,ownerThread=gate.thread,claimFileId=gate.file_id,scopeStartTick=gate.start_tick,proofStartTick=gate.proof_start_tick,routeProofSha256=gate_decode(gate.receipt_bytes)['routeSha256'],initialProofSha256=gate.proof_hash,gateReceiptSha256=sha(gate.receipt_bytes),sourceSealSha256=self.pins['sourceSealSha256'],gateSourcesSha256=gate.manifest_hash,binderSha256=self.pins['binderSha256'],boundAtUtc=datetime.now(timezone.utc).isoformat())
  self.binding=encode(binding)
  gate.charge('preauth-binding-create',len(self.binding));return self.binding
 def receive(self,gate,binding,capture,fixture_argv=None):
  self.current(gate)
  if not self.used or getattr(self,'receiveEntered',False):fail('PREAUTH_BINDING_ONCE_BYTES')
  binding_bytes(binding,self.binding)
  self.receiveEntered=True # never refund or rearm
  d=decode(binding)
  from entry_gates import decode as gate_decode
  if d['generation']!=gate.generation or d['ownerPid']!=gate.pid or d['ownerThread']!=gate.thread or d['claimFileId']!=gate.file_id or d['initialProofSha256']!=gate.proof_hash or d['gateReceiptSha256']!=sha(gate.receipt_bytes) or d['routeProofSha256']!=gate_decode(gate.receipt_bytes)['routeSha256'] or d['scopeStartTick']!=gate.start_tick or d['proofStartTick']!=gate.proof_start_tick:fail('PREAUTH_BINDING_ORIGINAL_CHANGED')
  gate.charge('preauth-template-receiver',len(self.bytes));gate.charge('preauth-binding-receiver',len(binding))
  # Re-read current source pins using original gate source accounting.
  for rel,k in [('reference/runner-source-seal.json','sourceSealSha256'),('tools/fact_preauth.py','binderSha256'),('tools/fact_collector.py','collectorSha256'),('tools/facts_entry.py','entrySha256'),('reference/fact-plan.json','factPlanSha256')]:
   if sha(gate.source_read(B/rel))!=self.pins[k]:fail('PREAUTH_RECEIVER_SOURCE:'+rel)
  from fact_collector import OwnedFactCapture
  if type(capture) is not OwnedFactCapture or capture.entered:fail('PREAUTH_ORIGINAL_CAPTURE')
  result=capture._capture_authorized(gate,fixture_argv,self.template['mode'],utc(self.template['expiresUtc']),self.pins['collectorSha256'],self.pins['factPlanSha256'],d['routeProofSha256'],dict(schema='GLOBAL_IDLE_FACT_CAPTURE_V2',authorizationKind='GLOBAL_IDLE_FACT_PREAUTH_V1',externalPreauthSha256=self.approved,runtimeBindingSha256=sha(binding)))
  return result
