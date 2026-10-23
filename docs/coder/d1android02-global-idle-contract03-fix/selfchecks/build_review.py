"""Assemble affected existing real PS/owner regressions; exclude Native/OS tests."""
from pathlib import Path
B=Path(__file__).resolve().parents[1];OLD=B.parent/'d1android02-compat03-schema-parity01'
s=(OLD/'selfchecks/run_checks.py').read_text();start=s.index('\ntry:\n from repair_cases')
tail=s[s.index('\nfinally:',start):]
s=s[:start].replace('d1android02-compat03-schema-parity01','d1android02-global-idle-contract03-fix').replace('D1_COMPAT03_SCHEMA_PARITY01_REVIEW_EVIDENCE','D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE')
s=s.replace(" cases.append({'name':name", " from fixture_inputs import qualification\n p['globalIdleQualification']=qualification(p['scope'],p['runId']);p['globalIdleQualification']['reviewEvidenceSha256']=p['review']['sha256']\n cases.append({'name':name")
s=s.replace("scenario not in ('BUSY','OWNER_END_TAIL')","scenario not in ('BUSY','OWNER_END_TAIL','PRESTART_KNOWN_REJECT')")
s=s.replace("'BUSY','OWNER_END_TAIL']","'BUSY','PRESTART_KNOWN_REJECT','OWNER_END_TAIL']")
s=s.replace("  if scenario=='OWNER_END_TAIL':assert","  if scenario=='PRESTART_KNOWN_REJECT':\n   co=decode((root/'identity-console.bin').read_bytes());assert co['noStartResourcesReturned'] and not co['startEntered'] and co['processDisposed'] and co['processDisposeCalls']==1 and len(co['readers'])==2 and all(x['fileOpenReturned'] and x['fileCloseReturned'] and x['pipeNeverCreated'] and not x['pipeCloseReturned'] and not x['eof'] and x['fileCloseCalls']==1 for x in co['readers']);assert co['initializationFailure']=='CONTROLLED_PRESTART_AFTER_TWO_FILES'\n  if scenario=='OWNER_END_TAIL':assert")
new='''
try:
 check('default-and-live-without-authority-denied',default_deny)
 check('prior-source-scope-schema-budget-denials',authority)
 check('real-PS-seven-original-END-and-once',full_cli)
 check('finite-original-owner-failures',finite_failures)
 check('production-consumer-post-delta-guards',ps_post_guards)
 check('changed-materialization-rejected',changed_materialization)
'''
(B/'selfchecks/run_affected.py').write_text(s+new+tail,encoding='utf-8',newline='\n')
