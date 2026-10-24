from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old63=P/'D1_FACTS_V2_QUALIFICATION04_INDEPENDENT_B_EVIDENCE/phase-A63-trace.json';old21=P/'D1_FACTS_V2_QUALIFICATION06_PHASE_A_EVIDENCE/oracle.json';old18=P/'D1_FACTS_V2_QUALIFICATION07_PHASE_A_EVIDENCE/oracle.json'
notes={
'S01':('STATIC_REVIEW_ONLY_PATCH_FAILURE_VARIANTS_NOT_RUN','static-closure.json; frozen build patch audit; no product-source mutation'),
'S02':('STATIC_AND_ACTUAL_CHILD_EVENT','static-closure.json; post-audit.json'),
'S03':('ACTUAL64_CORE_FIELDS_SEED_PHASE_DERIVED','post-audit.json seed-and-phase-ownership; private seed optional phase/owner derived from frozen same-scope plan'),
'S04':('RAW_ACTUAL_COMPLETE_LIVE_STATIC_ONLY','static-closure.json'),
'S05':('ACTUAL_PERMANENT_CHILD_NOT_PHYSICAL_CLOSE_CLAIM','post-audit.json child-and-route-permanent-reservations'),
'S06':('REAL_GATE64_65_AND_AUX_CAP_MODELS_NOT_REAL_BYTE_BOUNDARY','post-audit.json gate-real64-reject65; 18 helper'),
'S07':('ACTUAL_ORIGINAL_READS_AND_DECLARED_HELPER_RESERVATIONS','post-audit.json'),
'S08':('LIVE_NOT_RUN','no native route or real UNKNOWN injection'),
'S09':('ACTUAL_ORIGINAL_TICKET_AND_DELTA','post-audit.json productionBudgets'),
'S10':('ACTUAL_SUCCESS_LEDGER_REJECT_PATH_STATIC','facts chunks/summary; helper original outputs; no deliberate product-plan mismatch injection'),
'P01':('STATIC_CLOSURE_AND_ACTUAL_CURRENT_ENTRY','static-closure.json; current V1 and V2'),
'P02':('CURRENT_PRODUCER_ACTUAL_NEGATIVE_PATCH_VARIANTS_STATIC','post-audit.json named pins; preflight wrong source; V1 corpus'),
'P03':('ACTUAL_V1_346_AND_V2_PRODUCTION','evidence/group-8.json; actual production'),
'P04':('STATIC_ALL11_AND_ACTUAL_INLINE_REFERENCE','post-audit.json all11-inline-functions; static-closure capacity AST'),
'P05':('STATIC_IDENTIFIED_SOURCE_CONSUMERS','static-closure.json; external non-source hashes not rewritten'),
'B01':('ACTUAL_CORE_FUNCTION_CLUSTER','nine groups; production/receipt/control audits'),
'B02':('ACTUAL_18_AUX_AND_CURRENT346','evidence/group-7.json; evidence/group-8.json'),
'B03':('FINITE_CONSTRUCTOR_MODEL_REAL_UNKNOWN_NOT_INJECTED','independent-models.json; no old object queries')}
rows18=[dict(x,currentStatus=notes[x['id']][0],evidence=notes[x['id']][1],oldStatusPreserved=x['status']) for x in load(old18)['cases']]
rows21=[dict(x,currentStatus='RELATED_LIMITED_CURRENT_COVERAGE_NO_FULL_CASE_PASS',evidence='current RAW64 and original production/receipt/18 helper; old05 numeric path not replayed; see 07 trace boundaries',oldStatusPreserved=x['status']) for x in load(old21)['cases']]
rows63=[dict(id=x['id'],required=x['required'],oldStatusPreserved=x['status'],currentStatus='MAPPED_RELATED_COVERAGE_NOT_INDIVIDUALLY_REEXECUTED',evidence='current final schema/runtime/pins; original production and ticket/helper/receipt/control groups; no all63 case PASS claim') for x in load(old63)['rows']]
out={'priorSources':[{'path':str(p),'sha256':sha(p)} for p in (old63,old21,old18)],'counts':{'prior63':len(rows63),'prior21':len(rows21),'current18':len(rows18)},'rows63':rows63,'rows21':rows21,'rows18':rows18,'noCartesianRun':True,'oldStatusesUnchanged':True,'noPriorDynamicPassBackfill':True}
(R/'oracle-trace.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out['counts']))
