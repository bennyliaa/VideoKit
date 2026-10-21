"""Local evidence accounting and quoting round-trip only; no ADB or candidate execution."""
from pathlib import Path
import ast,hashlib,json,shlex
E=Path(__file__).resolve().parent
tree=ast.parse((E/'execute.py').read_text(encoding='utf-8'))
assigns={n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
task=ast.literal_eval(assigns['TASK']);script=ast.literal_eval(assigns['SCRIPT'].func.value).replace('TASK',task)
command='run-as com.videokit.app sh -c '+shlex.quote(script)
assert shlex.split(command)==['run-as','com.videokit.app','sh','-c',script]
receipts=[json.loads(p.read_bytes()) for p in sorted(E.glob('*-receipt.json'))]
assert len(receipts)==5 and all(r['clientReturned'] for r in receipts)
assert [r['exitCode'] for r in receipts]==[0,0,0,0,127]
assert sum(r['savedBytes'] for r in receipts)<8*1024*1024
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(result='BLOCKED_PREFLIGHT_TESTER_QUOTING_ERROR',testerIssue='E5CEXEC-T01',productDefect=False,device='HA1Q6WXR',appUid=10221,testUid=10222,user=0,existingVersionCode=1,existingVersionName='D1-E4A',installedApkIdentity='EXACT_E4A_SHA_AND_PRIOR_SIGNER_IDENTITY_MATCH',installedEnabled=0,freeKiB=85360328,metadataAdmission='NOT_COLLECTED_INVALID_SHELL_QUOTING',rootAdmission='NOT_RUN',deployment='BLOCKED_NOT_ATTEMPTED',fixture='NOT_RUN',query='NOT_RUN',G01='AWAITING_ANDROID_EVIDENCE_AND_REVIEW',adbCalls=5,adbReceipts=receipts,clientOwnersReturned=True,inFlight=[],batchLogBytes=sum(r['savedBytes'] for r in receipts),batchLogLimitBytes=8*1024*1024,installCalls=0,instrumentationCalls=0,mediaContentHashBytes=0,n2NewStateEvidence='NOT_COLLECTED_DO_NOT_CLAIM_FRESH_PRESERVATION_PASS',priorN2='FAIL_PENDING_UNKNOWN_NOT_UPGRADED',candidateSourcesChanged=False,correctedRunnerSha256=sha(E/'execute.py'),originalFailedRunnerSha256=sha(E/'execute-original-failed.py'),quoteCheck='LOCAL_AST_PARSE_AND_SHLEX_ROUNDTRIP_PASS_NOT_DEVICE_EXECUTION',correctedCommandSha256=hashlib.sha256(command.encode()).hexdigest(),retry=False,newDispatchRequired=True,D1='NOT_PASSED',M0='NOT_STARTED')
with (E/'blocked-result.json').open('x',encoding='utf-8') as out:json.dump(result,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps({k:result[k] for k in ['result','adbCalls','batchLogBytes','deployment','fixture','query','clientOwnersReturned','quoteCheck']}))
