"""Opt-in synthetic tool integration. Import and default CLI perform no execution."""
import argparse, json, sys, traceback
from gcore import *
from gengine import Engine
from scenarios import Scenarios
from phases import preflight, Cleanup

def fixtures(root):
    root.mkdir(parents=True,exist_ok=False)
    for name,n in [('L.bin',131072),('C.bin',4096),('Z.bin',0)]:
        with open(root/name,'xb') as file:
            for start in range(0,n,4096):file.write(bytes((i%251 for i in range(start,min(start+4096,n)))))

def run():
    parser=argparse.ArgumentParser();modes=parser.add_mutually_exclusive_group();modes.add_argument('--synthetic-selfcheck',action='store_true');modes.add_argument('--recover-selfcheck');options=parser.parse_args()
    manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8-sig'))
    if options.recover_selfcheck:
        from recovery import recover
        need(Path(options.recover_selfcheck).name==options.recover_selfcheck,'SELF_CHECK_NAME_ONLY')
        result=recover(BASE/'selfcheck'/options.recover_selfcheck,manifest)
        print(json.dumps(result,separators=(',',':')));return 0
    if not options.synthetic_selfcheck:
        print(json.dumps({'mode':'INSPECT_ONLY','branches':len(manifest['branches']),'mediaExecution':'DISABLED'}));return 0
    need(not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED')
    existing=[p for p in (BASE/'selfcheck').rglob('*') if p.is_file()]
    fixture_bytes=sum(p.stat().st_size for p in existing if p.name in ('L.bin','C.bin','Z.bin') or p.suffix=='.out')
    log_bytes=sum(p.stat().st_size for p in existing if not(p.name in ('L.bin','C.bin','Z.bin') or p.suffix=='.out'))
    need(fixture_bytes+135500<=2097152,'AGGREGATE_SYNTHETIC_LIMIT');need(log_bytes+800000<=4194304,'AGGREGATE_LOG_LIMIT')
    root=BASE/'selfcheck'/('check-'+time.strftime('%Y%m%dT%H%M%S'))
    fixtures(root);e=Engine(root,manifest);driver=Scenarios(e);error=None
    try:
        preflight(e)
        ordered=[r for r in manifest['branches'] if r['id'] not in ('P10-D','P10-C')]+[r for r in manifest['branches'] if r['id'] in ('P10-D','P10-C')]
        for row in ordered:
            e.begin(row['id']);driver.run(row['id']);e.flow.finish()
    except Exception:
        error=traceback.format_exc();print(error,file=sys.stderr)
    try:
        cleanup=Cleanup(e);cleanup.run()
        report={'status':'PASS' if error is None else 'FAIL','error':error,'rows':e.results,'assertions':e.assertions}
        witness=cleanup.finish(report);print(json.dumps(witness,separators=(',',':')))
        return 0 if error is None else 1
    except Exception:
        print(traceback.format_exc(),file=sys.stderr)
        # Exceptional stop preserves unresolved tickets. Terminate only our two known
        # child process instances, then observe actual exit; never infer native close.
        for channel in e.channels.values():
            if channel.process.poll() is None:
                channel.process.terminate()
            try:channel.process.wait(timeout=5)
            except subprocess.TimeoutExpired:pass
        e.io.shutdown(wait=False,cancel_futures=True)
        return 2

if __name__=='__main__':sys.exit(run())
