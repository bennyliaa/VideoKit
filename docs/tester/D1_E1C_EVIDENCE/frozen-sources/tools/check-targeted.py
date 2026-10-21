"""Explicit independent negative checks; no J/R/media execution."""
import argparse,importlib,json,sys,time,traceback
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))
def run():
    if (BASE/'evidence/freeze-summary.json').exists():raise RuntimeError('FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED')
    logs=sum(p.stat().st_size for p in (BASE/'selfcheck').rglob('*') if p.is_file() and p.name not in ('L.bin','C.bin','Z.bin') and p.suffix!='.out')+sum(p.stat().st_size for p in (BASE/'evidence').glob('*.json'))
    if logs+524288>4194304:raise RuntimeError('AGGREGATE_NEGATIVE_CHECK_LOG_LIMIT')
    manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8-sig'));results=[];stamp=str(time.time_ns())
    for name in ('authority_checks','recovery_checks','metadata_checks','unitcheck'):
        try:
            module=importlib.import_module(name)
            result=module.run() if name=='unitcheck' else module.run_checks(BASE/'selfcheck'/(name+'-'+stamp),manifest)
        except Exception:result={'status':'FAIL','error':traceback.format_exc(),'scope':name}
        results.append(result)
    report={'scope':'E1C_TARGETED_SYNTHETIC_CHECKS','status':'PASS' if all(r['status']=='PASS' for r in results) else 'FAIL','groups':results,'assertions':sum(r.get('assertions',0) for r in results),'helpersStarted':False,'mediaRead':False}
    path=BASE/'evidence'/('targeted-'+stamp+'.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'evidence':str(path),'status':report['status'],'assertions':report['assertions'],'groups':[{'scope':r['scope'],'status':r['status'],'assertions':r.get('assertions'),'error':r.get('error')} for r in results]},separators=(',',':')))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');a=p.parse_args()
    sys.exit(run() if a.run else print('INSPECT_ONLY: explicit --run required'))
