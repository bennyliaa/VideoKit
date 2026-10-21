"""Explicit one-cycle metadata check of this configuration process only, never G/J/R PF."""
import argparse,ctypes,json,os,sys,time
from pathlib import Path
from ctypes import wintypes
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-self',action='store_true');options=parser.parse_args()
    if not options.run_self:print('INSPECT_ONLY: explicit --run-self required');return 0
    if (BASE/'evidence/freeze-summary.json').exists():raise RuntimeError('FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED')
    from gcore import Ledger
    from runtime_metrics import Win32MetricReader,_FILETIME,_THREADENTRY32,_PROCESS_MEMORY_COUNTERS_EX
    ledger=Ledger();reader=Win32MetricReader(ledger);k=reader.k
    k.GetCurrentProcess.argtypes=[];k.GetCurrentProcess.restype=wintypes.HANDLE
    a,b,c,d=(_FILETIME() for _ in range(4))
    if not k.GetProcessTimes(k.GetCurrentProcess(),ctypes.byref(a),ctypes.byref(b),ctypes.byref(c),ctypes.byref(d)):raise RuntimeError('SELF_CREATION_TIME_UNAVAILABLE')
    creation=(int(a.dwHighDateTime)<<32)|int(a.dwLowDateTime)
    identity=dict(pid=os.getpid(),creationTime100ns=creation,owner='E2-CONFIGURATION-PROCESS-ONLY')
    begin=time.monotonic();observed=reader.read_cycle({'G':identity})['G'];elapsed=time.monotonic()-begin;facts=reader.facts()
    checks={
        'originalSelfIdentity':observed['pid']==identity['pid'] and observed['creationTime100ns']==creation,
        'availableNonnegativeMetrics':observed['threads']>0 and observed['handles']>0 and observed['workingSetBytes']>0 and observed['privateBytes']>0,
        'singleObserverCredit':ledger.peak==1 and not ledger.live,
        'actualNativeHandlesClosed':facts['openedHandles']==facts['closedHandles']==2 and facts['maximumOwnedHandlesObserved']==1,
        'noUnknownOrReservedOwner':not facts['observerCreditHeld'] and not facts['closeUnknown'],
        'pinnedX64Structures':ctypes.sizeof(_FILETIME)==8 and ctypes.sizeof(_THREADENTRY32)==28 and ctypes.sizeof(_PROCESS_MEMORY_COUNTERS_EX)==80}
    report=dict(scope='E2_CONFIGURATION_PROCESS_METADATA_SELF_CHECK_ONLY',status='PASS' if all(checks.values()) else 'FAIL',
                assertions=len(checks),checks=checks,identity=identity,observed=observed,elapsedSeconds=elapsed,nativeReaderFacts=facts,
                policyApproved=False,experimentBaseline=False,experimentRuntimePeak=False,mediaBytesRead=0,helpersStarted=0,realPFRun=False,real61Run=False)
    stamp=str(time.time_ns());path=BASE/'evidence'/('observer-self-'+stamp+'.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(evidence=str(path),**report),separators=(',',':')));return 0 if report['status']=='PASS' else 2

if __name__=='__main__':raise SystemExit(main())
