from pathlib import Path
import json, hashlib, re, datetime
E=Path(__file__).resolve().parent
R=E.parent/'D1_RESUME01_CAPTURE_EXECUTION/20b08d64-6fd0-4a88-8b72-c80615e58258/outputs'
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
    with (E/name).open('x',encoding='utf-8',newline='\n') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
ops=[]
for tag in ['identity','global']:
    rid='RESUME02_M1_'+tag
    c=json.loads((E/('M1-'+tag+'-console.bin')).read_text(encoding='utf-8-sig'))
    t=json.loads((E/('M1-'+tag+'-tool-result.json')).read_text(encoding='utf-8-sig'))
    assert t['exit_code']==0 and not t.get('session_id') and not t['output']
    assert c['captureQualified'] and c['allOriginalResourcesReturnedAtConsole'] and c['waitReturned'] and c['processDisposed']
    assert c['firstFailure'] is None and not c['rawAmountUnknown'] and not c['recordWriteAmountUnknown']
    assert h(R/(rid+'-receipt.json'))==c['captureReceiptSha256']
    assert all(x['closed'] and x['writeReturned'] and not x['writeFailed'] and not x['openUnknown'] for x in c['metadata'])
    for x in c['readers']:
        assert all(x[k] for k in ['eof','readTaskReturned','pipeCloseReturned','fileCloseEntered','fileCloseReturned'])
        assert not x['savedAmountUnknown'] and x['rawBytes']==x['savedBytes']==(R/(rid+'-'+x['role']+'.bin')).stat().st_size
    ops.append({'id':rid,'sdkCalls':1,'workUnits':1,'rawBytes':c['rawBytesKnown'],'savedBytes':sum(x['savedBytes'] for x in c['readers']),'metadataWrittenBytes':c['recordWriteBytesKnown'],'consoleOriginalBytes':(E/('M1-'+tag+'-console.bin')).stat().st_size,'consoleEvidenceCopyBytes':(E/('M1-'+tag+'-console.bin')).stat().st_size,'controllerPid':c['controllerPid'],'childPid':c['childPid'],'toolExit':0,'allOriginalResourcesReturned':True,'receiptSha256':c['captureReceiptSha256']})
s=(R/'RESUME02_M1_global-stdout.bin').read_text(encoding='utf-8')
head='ACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)'
assert s.startswith(head+'\n') and s.count(head)==1
assert s.count('  All known processes:')==1 and s.count('  OOM levels:')==1
assert s.index('  All known processes:')<s.index('  OOM levels:')
assert len(re.findall(r'^  mForceBackgroundCheck=(?:true|false)$',s,re.M))==1
assert re.search(r'\n  mForceBackgroundCheck=(?:true|false)\n?\Z',s)
records=[]
for m in re.finditer(r'^  \*APP\* UID (\d+) ProcessRecord\{[^\n]+\n(?:(?!^  \*APP\*|^  OOM levels:).*(?:\n|\Z))*',s,re.M):
    block=m.group(0)
    if re.search(r'ProcessRecord\{[^\n]*:com\.lendmanager\.',block):
        lines=block.splitlines()
        selected=[x for x in lines if any(k in x for k in ['*APP*','pid=','foregroundActivities=','curProcState=','cached=','hasForegroundActivities=','hasVisibleActivities=','topUi=','visible=true','visibleTask='])]
        records.append({'uid':int(m.group(1)),'startLine':s[:m.start()].count('\n')+1,'observations':selected})
assert any('com.lendmanager.app/' in x['observations'][0] for x in records)
top=[{'line':i+1,'text':v} for i,v in enumerate(s.splitlines()) if 'com.lendmanager.app/' in v and '(top-activity)' in v]
assert top
audit={'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'ENV_WAIT_OTHER_PROJECT_OCCUPIED','capturePhysicalStatus':'PASS_RETURNED','completeFullSource':True,'sourceBytes':(R/'RESUME02_M1_global-stdout.bin').stat().st_size,'sourceSha256':h(R/'RESUME02_M1_global-stdout.bin'),'records':records,'topActivityEvidence':top,'instrumentationMentionLines':[{'line':i+1,'text':v} for i,v in enumerate(s.splitlines()) if 'instrumentation' in v.lower()],'approvedForNext':False,'noFurtherSDKCalls':True}
save('M1-global-semantic-audit.json',audit)
save('execution-step-02.json',dict(ops[1],semanticStatus=audit['status'],approvedForNext=False))
proof=R/'RESUME02_M1_identity-completion-proof.json'
ledger={'atUtc':audit['atUtc'],'scopeId':'20b08d64-6fd0-4a88-8b72-c80615e58258','status':'STOPPED_ENV_WAIT_OTHER_PROJECT_OCCUPIED','supersedesInitialSnapshot':'actual-execution-ledger.json','identityAuditCorrection':'execution-step-01-correction.json','maxWorkUnits':43,'enteredWorkUnits':2,'unenteredWorkUnits':41,'operations':ops,'rawSdkBytesKnown':sum(x['rawBytes'] for x in ops),'rawSdkAmountUnknown':False,'rawSavedBytesKnown':sum(x['savedBytes'] for x in ops),'captureRecordWritesKnown':sum(x['metadataWrittenBytes'] for x in ops),'originalConsoleBytesKnown':sum(x['consoleOriginalBytes'] for x in ops),'consoleEvidenceCopiesKnown':sum(x['consoleEvidenceCopyBytes'] for x in ops),'externalCompletionProofBytesKnown':proof.stat().st_size,'externalCompletionProofSha256':h(proof),'controlReserveHeldConservatively':786432,'oldKnownControl2272Held':True,'oldUnknown8192Held':True,'noRefundOfHistoricalUnknown':True,'globalUnallocated409600Used':0,'remainingReservedIsNotRetryAuthorization':True,'captureRootRetained':str(R),'deploymentStarted':False,'dispositionInstalled':False,'caseClaimCreated':False,'permitFileRemainsFrozen':True,'semanticAdmissionConsumedByTwoReads':True,'autoRetry':False,'next':'NONE_STOPPED','notRun':['M1_ps','deployment Java and its 35 SDK children','M2_identity','M2_global','ordinarySenderCannotBindCodec','all other cases']}
save('actual-execution-ledger-final-v1.0.json',ledger)
save('scope-stop-record.json',{'status':ledger['status'],'atUtc':audit['atUtc'],'cause':'Fresh full M1 global snapshot shows another project live/top activity','globalCompletionProofCreated':False,'approvedForNext':False,'pendingOriginalResources':False,'automaticNextTask':False,'noStopOrKillOrRetryPerformed':True})
print(json.dumps({'status':ledger['status'],'workUnits':2,'rawSdkBytes':ledger['rawSdkBytesKnown'],'records':records,'top':top,'captureRecordWrites':ledger['captureRecordWritesKnown'],'console':ledger['originalConsoleBytesKnown'],'proofBytes':ledger['externalCompletionProofBytesKnown']},ensure_ascii=False))
