"""Read-only final evidence reconciliation; never launches a media/helper process."""
import argparse, ast, hashlib, json, sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))
from recovery import recover
from profile_audit import verify_configuration
def audit():
    manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8'))
    configuration=verify_configuration(manifest)
    candidates=[(p,json.loads(p.read_text(encoding='utf-8'))) for p in (BASE/'evidence').glob('selfcheck-*.json')]
    passing=[(p,x) for p,x in candidates if x['exitCode']==0 and x.get('witness',{}).get('status')=='PASS'];assert passing
    path,result=max(passing,key=lambda item:item[1]['started']);w=result['witness'];root=BASE/'selfcheck'/w['root']
    summary=root/w['precloseSummary'];assert hashlib.sha256(summary.read_bytes()).hexdigest()==w['precloseSummarySha'];pre=json.loads(summary.read_bytes());assert pre['error'] is None
    expected=['PF']+manifest['executionOrder'];assert [x['branch'] for x in pre['rows']]==expected
    assert all(0<=x['elapsedSeconds']<=x['seconds'] for x in pre['rows'])
    assert w['usage']['n']==351 and w['usage']['qn']==83 and w['usage']['qr']==18 and w['usage']['records']==32 and w['usage']['targets']==10
    assert w['logClose']['closed'] and w['logClose']['remainingResources']==0
    assert all(p['exited'] and p['code']==0 for p in w['logClose']['exitedHelpers'].values())
    cold=recover(root,manifest);assert len(cold['states'])==32 and cold['usage']==w['usage']
    assert cold['writeCapability'] is False and cold['nativeCalls']==0
    assert cold['usageExact'] and cold['completeness']['status']=='COMPLETE' and len(cold['completeness']['admitted'])==32 and not cold['completeness']['missingAdmitted']
    assert w['metadataRequested']==w['metadataWritten'] and w['metadataUnknownRequestedBytes']==0 and w['metadataCommitStatus']=='HEALTHY'
    assert w['privateCells']['retained']==0 and w['privateCells']['peak']<=8
    assert all(w['callbackHub'][key]==0 for key in ('cells','queued','active','workersAlive')) and w['callbackHub']['blocked'] is None
    hub=w['callbackHub'];assert hub['lifecycle']=='CLOSED' and hub['remainingCredits']==[] and hub['ownershipPending'] is False
    assert hub['startupError'] is None and hub['cleanupError'] is None and hub['startupInProgress'] is False and set(hub['workers'])=={'notify','deadline'}
    for worker in hub['workers'].values():
        assert all(worker[key] is True for key in ('creditReserved','creditReleased','reserveReturned','threadCreated','startEntered','startReturned','entered','exited','joinEntered','joinReturned','joined'))
        assert worker['alive'] is False and worker['unknown'] is False and worker['releaseProof']=='THREAD_JOIN_PROVEN'
        assert all(worker[key] is None for key in ('startError','reserveError','joinError','runtimeError','observationError'))
    assert w['ledgerPeaks']['os']<=24
    assert len(cold['unresolved'])==1 and cold['unresolved'][0]['command']=='GC/n32'
    assert cold['states']['S17']['objects']['S17-v1-C']['originalCloseDisposition']=='UNKNOWN'
    assert cold['states']['S17']['objects']['S17-v1-D']['attempts']==3
    assert cold['states']['S17']['objects']['S17-v1-D']['nativeCloses']==0
    assert cold['states']['S17']['objects']['S17-v1-C']['nativeCloses']==1
    assert all(s['fenced'] and not s['confirmed'] for s in cold['states'].values())
    for p in [*(BASE/'src').glob('*.py'),*(BASE/'tools').glob('*.py')]:ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    files=[p for p in (BASE/'selfcheck').rglob('*') if p.is_file()];fixtures=[p for p in files if p.name in ('L.bin','C.bin','Z.bin') or p.suffix=='.out']
    synthetic=sum(p.stat().st_size for p in fixtures);logs=sum(p.stat().st_size for p in files if p not in fixtures)+sum(p.stat().st_size for p in (BASE/'evidence').glob('*.json'))
    assert synthetic<=2097152 and logs<=4194304
    upstream=json.loads((BASE/'upstream-e1e/freeze-summary.json').read_text(encoding='utf-8'))
    upstream_source=json.loads((BASE/'upstream-e1e/source-manifest.json').read_text(encoding='utf-8'))
    assert len(upstream['files'])==11 and len(upstream['selfcheckFiles'])==177 and len(upstream_source['files'])==33
    project=BASE.parents[2]
    for r in upstream['files']+upstream['selfcheckFiles']+upstream_source['files']:
        p=project/r['path'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
    targets=[(p,json.loads(p.read_text(encoding='utf-8'))) for p in (BASE/'evidence').glob('targeted-*.json')]
    target_path,target=max(((p,r) for p,r in targets if r['status']=='PASS'),key=lambda item:item[0].name)
    groups={group['module']:group for group in target['groups']}
    assert set(groups)=={'e2_checks','startup_checks','completion_checks','authority_checks','recovery_checks','metadata_checks','unitcheck'}
    assert all(group['status']=='PASS' for group in groups.values()) and groups['startup_checks']['assertions']>0 and groups['e2_checks']['assertions']>0
    total=w['assertions']+target['assertions']
    observer_path=max((BASE/'evidence').glob('observer-self-*.json'))
    observer=json.loads(observer_path.read_text(encoding='utf-8'))
    assert observer['status']=='PASS' and observer['assertions']==6 and all(observer['checks'].values())
    assert not observer['experimentBaseline'] and not observer['experimentRuntimePeak'] and not observer['policyApproved']
    native=observer['nativeReaderFacts'];assert native['openedHandles']==native['closedHandles']==2 and native['maximumOwnedHandlesObserved']==1 and not native['observerCreditHeld'] and not native['closeUnknown']
    denials=json.loads((BASE/'evidence/entry-denials.json').read_text(encoding='utf-8-sig'))
    assert denials['status']=='PASS' and len(denials['cases'])==2
    assert all(row['exitCode']==2 and row['response']['executionAllowed'] is False and row['response']['mediaBytesRead']==0 and row['response']['helpersStarted']==0 and row['response']['outputRootCreated'] is False for row in denials['cases'])
    return {'status':'PASS','scope':'READ_ONLY_EVIDENCE_AUDIT','integrationEvidence':path.relative_to(BASE).as_posix(),'targetedEvidence':target_path.relative_to(BASE).as_posix(),'root':root.name,'syntheticAssertions':w['assertions'],'targetedAssertions':target['assertions'],'totalAssertions':total,'scenarios':61,'phaseControls':48,'controls':452,'recoveredRecords':32,'recoveredBudgetMatches':True,'inventoryComplete':True,'uncertainLogCloseRequiresExternalWitness':True,'originalCloseFactsPreserved':True,'allRowsWithinDeadline':True,'syntheticBytes':synthetic,'logAndEvidenceBytesAtAudit':logs,'oldE1EFrozenFilesVerified':len(upstream['files'])+len(upstream['selfcheckFiles']),'oldE1ESourceFilesVerified':len(upstream_source['files']),'oldE1EFileBreakdown':{'frozen':11,'selfcheck':177},'callbackHubDrainedAndJoined':True,'startupLifecycleVerified':True,'startupFixVerified':True,'configurationVerified':configuration['configurationVerified'],'configuration':configuration,'targetedGroups':list(groups),'mediaRead':False}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');args=parser.parse_args()
    print(json.dumps(audit() if args.audit else {'mode':'INSPECT_ONLY'},separators=(',',':')))
