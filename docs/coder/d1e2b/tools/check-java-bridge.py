"""Explicit self-owned non-media A05 checks; no formal PF, RPC, or input binding."""
import argparse,json,os,subprocess,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
JAVA=Path('D:/Android/Android Studio/jbr/bin/java.exe')
FLAGS=['--enable-preview','--enable-native-access=ALL-UNNAMED','--add-opens=java.base/java.io=ALL-UNNAMED']
def run():
    if (BASE/'evidence/freeze-summary.json').exists():raise RuntimeError('FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED')
    owned=BASE/'selfcheck';owned.mkdir(exist_ok=True)
    for part in [owned,*owned.parents]:
        if part.is_symlink() or part.is_junction():raise RuntimeError('OWNED_PROBE_REPARSE_ROOT_DENIED')
    existing=[p for p in owned.rglob('*') if p.is_file()]
    fixtures=sum(p.stat().st_size for p in existing if p.name in ('L.bin','C.bin','Z.bin') or p.suffix=='.out')
    logs=sum(p.stat().st_size for p in existing if p.name not in ('L.bin','C.bin','Z.bin') and p.suffix!='.out')+sum(p.stat().st_size for p in (BASE/'evidence').glob('*.json'))
    if fixtures+4113>2097152 or logs+65536>4194304:raise RuntimeError('AGGREGATE_OWNED_BRIDGE_CHECK_LIMIT')
    stamp=str(time.time_ns());root=owned/('java-bridge-'+stamp);root.mkdir(exist_ok=False)
    with (root/'L.bin').open('xb') as file:file.write(b'X'*4096)
    with (root/'C.bin').open('xb') as file:file.write(b'D'*17)
    cases=[(name,name,list(FLAGS)) for name in ('success','path-separation','query-failure','field-missing','field-type','symbol-missing','close-race')]
    for name,missing in [('missing-native-access',FLAGS[1]),('missing-java-io-open',FLAGS[2]),('missing-preview',FLAGS[0])]:cases.append((name,'blocked-flags',[flag for flag in FLAGS if flag!=missing]))
    results=[];status='PASS';pending=None
    for name,mode,flags in cases:
        args=[str(JAVA),*flags,'-cp',str(BASE/'artifacts/java'),'videokit.e1.JavaBridgeProbe','--owned-file-probe',str(root),mode]
        started=time.time_ns();process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        try:stdout,stderr=process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            status='PENDING';pending={'case':name,'pid':process.pid,'rule':'STOP_WAITING_NO_FORCE_KILL_OR_EXIT_INFERRED'};break
        ended=time.time_ns()
        if len(stdout)>8192 or len(stderr)>8192:raise RuntimeError('OWNED_BRIDGE_RECEIPT_LIMIT')
        out=stdout.decode('utf-8',errors='replace').strip();err=stderr.decode('utf-8',errors='replace')
        report=None
        try:report=json.loads(out) if out else None
        except json.JSONDecodeError:pass
        expected_preview_rejection=name=='missing-preview' and report is None and process.returncode!=0 and 'UnsupportedClassVersionError' in err and 'preview' in err.lower()
        passed=bool(report and report.get('status')=='PASS' and process.returncode==0) or expected_preview_rejection
        if report and report.get('status')=='PASS':
            fields=report['openReceipt'].split('|');passed=passed and len(fields)==11 and report['nativeCloses']==1 and report['nativeReads']==report['nativeSeeks']==0 and report['threadsJoined'] is True and report['pid']==process.pid
            if name in ('success','path-separation','close-race'):passed=passed and fields[-1]=='PROVEN' and fields[0]=='4096' and len(fields[2].split(':'))==3
            else:passed=passed and fields[-1]=='BLOCKED_VERSION_NOT_PROVEN' and fields[:3]==['-1','-1','']
        assertions=report.get('assertions',0) if report else int(expected_preview_rejection)
        results.append(dict(case=name,status='PASS' if passed else 'FAIL',exitCode=process.returncode,pid=process.pid,startedNs=started,endedNs=ended,processExitObserved=True,assertions=assertions,previewStartupRejected=expected_preview_rejection,receipt=report,stderr=err))
        if not passed:status='FAIL'
    result=dict(scope='E2B_SELF_OWNED_JAVA_BRIDGE_METADATA_CHECKS',status=status,assertions=sum(case['assertions'] for case in results),cases=results,pending=pending,noInFlight=pending is None and len(results)==len(cases),fixtureBytes=4113,fixtureRoot=root.name,
                plannedProcesses=len(cases),completedProcesses=len(results),mediaBytesRead=0,formalPFRun=False,formal61Run=False,
                limits='Uses only newly created L.bin(4096B)/C.bin(17B). Decoy-path comparison is not an actual rename/replacement test; no test_media path, helper RPC or real-run grant.')
    path=BASE/'evidence'/('java-bridge-'+stamp+'.json');path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(evidence=str(path),status=status,completedProcesses=len(results),pending=pending),separators=(',',':')))
    return 0 if status=='PASS' else 2 if status=='PENDING' else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');args=parser.parse_args()
    raise SystemExit(run() if args.run else print('INSPECT_ONLY: explicit --run required'))
