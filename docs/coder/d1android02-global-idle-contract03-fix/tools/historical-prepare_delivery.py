"""Evidence reconciliation and documents; does not mutate sealed runtime source."""
from pathlib import Path
import hashlib,json,difflib
B=Path(__file__).resolve().parents[1];OLD=B.parent/'d1android02-compat03-schema-parity01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def put(p,t):p.write_text(t,encoding='utf-8',newline='\n')
seal=json.loads((B/'reference/runner-source-seal.json').read_text());old=json.loads((OLD/'reference/runner-source-seal.json').read_text())
for p,h in seal['sources'].items():assert sha(B/p)==h
assert sha(OLD/'reference/runner-source-seal.json')=='2595222c18a6a1494ce48bb7c8eea365a4334ddce6ea7bdb1efa624cbcec0c69'
changed=[];diff=[]
for p,h in seal['sources'].items():
 if p not in old['sources'] or h!=old['sources'][p]:
  changed.append(dict(path=p,oldSha256=old['sources'].get(p),newSha256=h,bytes=(B/p).stat().st_size))
  before=(OLD/p).read_text(encoding='utf-8').splitlines(True) if (OLD/p).exists() else []
  diff.extend(difflib.unified_diff(before,(B/p).read_text(encoding='utf-8').splitlines(True),fromfile='compat03/'+p,tofile='contract02/'+p))
save(B/'reference/source-delta.json',changed);put(B/'reference/source-delta.patch',''.join(diff))
up=B/'reference/upstream';sources=[]
for f in sorted(up.glob('fetch-round*.json')):
 for r in json.loads(f.read_text()):
  if r.get('commit') and r.get('sha256'):sources.append(r)
enum=(up/'enum-pinned.txt').read_text();role=(up/'role-shell.txt').read_text()
for k,v in dict(PERSISTENT=0,PERSISTENT_UI=1,TOP=2,BOUND_TOP=3,FOREGROUND_SERVICE=4,BOUND_FOREGROUND_SERVICE=5,IMPORTANT_FOREGROUND=6,IMPORTANT_BACKGROUND=7,TRANSIENT_BACKGROUND=8,BACKUP=9,SERVICE=10,RECEIVER=11,TOP_SLEEPING=12,HEAVY_WEIGHT=13,HOME=14,LAST_ACTIVITY=15,CACHED_ACTIVITY=16,CACHED_ACTIVITY_CLIENT=17,CACHED_RECENT=18,CACHED_EMPTY=19,NONEXISTENT=20).items():assert f'{k} = {v},' in enum
assert 'case "get-role-holders"' not in role
assert all('case "'+x+'"' in role for x in ('add-role-holder','remove-role-holder','clear-role-holders'))
save(B/'reference/upstream-source-closure.json',dict(tag='android-12.0.0_r1',baseCommit='cebf5c06997b64f4e47a1611edb5f97044509d76',permissionCommit='c11239c07afab2d6093c8efb3fa59328b7389df7',files=sources,enumTableChecked=True,roleGetterExists=False,replacement='dumpsys role (no fallback)',deviceHelpQueries=0))
criteria=json.loads((B.parent.parent/'tester/D1_GLOBAL_IDLE_SEMANTICS01_CRITERIA_EVIDENCE/criteria.json').read_text())
mapping={'I01':['F01','F02','F03'],'I02':['F04','F05','F07','X_RAW_HASH','X_RAW_SIZE','X_RETURN_UNKNOWN'],'I03':['F06','P03','P04','H02'],'P01':['P01','P02'],'P02':['P03','P04','X_UID_SUMMARY'],'P03':['P05','P10','P11'],'P04':['P11','P12','P13'],'P05':['P09','P14'],'P06':['P05','P06','P07','X_CASE','X_UNICODE'],'P07':['P07','P08','X_CORE_OTHER_USER'],'P08':['P06','X_PID_DUP','X_TOKEN_DUP'],'S01':['S01','S05','P13'],'S02':['S02','S03','S05','S08'],'S03':['S06','S10'],'S04':['S07','S09'],'T01':['S02','S03','S04','X_NULL_SUFFIX','X_MALFORMED_INSTR'],'R01':['R01','R03','R04','R05','X_OTHER_DISPLAY','X_EXTRA_DISPLAY'],'R02':['R06','R05'],'Q01':['R01','R02','Q02','X_FACT_api','X_SERVICE_firmware'],'Q02':['R08','Q01','X_SERVICE_process','X_HIST_owner','X_HIST_pid'],'Q03':['Q03','Q02','X_FACT_expiresAtUtc'],'H01':['H01','H02'],'B01':['Q04','X_FACT_collectorSourceSha256','X_FACT_factPlanSha256']}
assert set(mapping)=={x['id'] for x in criteria['acceptance']}
results=json.loads((B/'evidence/contract-result.json').read_text());sem=json.loads((Path(results['work'])/'semantic-results.json').read_text(encoding='utf-8-sig'));by={x['id']:x for x in sem}
for v in mapping.values():assert all(by[k]['pass'] for k in v)
save(B/'reference/criteria-map.json',dict(schema='GLOBAL_IDLE_CONTRACT02_RULE_MAPPING_V1',independentCriteriaSha256=sha(B.parent.parent/'tester/D1_GLOBAL_IDLE_SEMANTICS01_CRITERIA_EVIDENCE/criteria.json'),ruleCount=23,criteriaCases=45,actualSemanticCases=len(sem),mapping=[dict(rule=k,cases=v,status='DEVELOPER_FIXTURE_CHECKS_PASSED_INDEPENDENT_B_NOT_RUN') for k,v in mapping.items()],returnBoundary='Semantic PASS internal only. Existing original Owner/controller/END regression required; no new actual UNKNOWN injected or repaired.'))
save(B/'evidence/current-source-audit.json',dict(sourceSealSha256=sha(B/'reference/runner-source-seal.json'),sourceCount=len(seal['sources']),gateCount=9,changed=changed,originalSourceSealPreserved=sha(OLD/'reference/runner-source-seal.json'),archivedRawPreserved=sha(B.parent/'d1android02-global-idle-semantics01/reference/original-global_idle-stdout.bin'),independentB='NOT_RUN',live='NOT_RUN'))
print(json.dumps(dict(sourceSeal=sha(B/'reference/runner-source-seal.json'),changes=len(changed),semanticCases=len(sem))))
