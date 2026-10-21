"""Bounded in-process entry rejection checks. No Engine, observer, worker or helper."""
import contextlib,hashlib,importlib.util,io,json,sys
from pathlib import Path
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))
import admission,controller,synthetic_admission,gcore,runtime_metrics,notifications

def load(name,relative):
    spec=importlib.util.spec_from_file_location(name,BASE/relative);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def run():
    if (BASE/'evidence/freeze-summary.json').exists():raise RuntimeError('FROZEN_PACKAGE_READ_ONLY')
    runner=load('e2c_inherited_full','tools/run-selfcheck.py');rdiag=load('e2c_inherited_r','tools/diagnose-r.py');gdiag=load('e2c_fixed_g_entry','tools/diagnose-g.py')
    reservation=BASE/'evidence/g-lifecycle-reservation.json';before=hashlib.sha256(reservation.read_bytes()).hexdigest()
    guards=[];cases=[]
    def forbidden(*args,**kwargs):guards.append('FORBIDDEN_RESOURCE_CONSTRUCTOR');raise RuntimeError('FORBIDDEN_RESOURCE_CONSTRUCTOR')
    plan=[('real-request',admission.main,['--request-real','E2C-REAL-DENIED']),
          ('controller-full',controller.run,['--synthetic-selfcheck']),
          ('controller-mock-full',controller.run,['--synthetic-selfcheck','--synthetic-observer-mock']),
          ('controller-real-mixed',controller.run,['--synthetic-selfcheck','--synthetic-observer-mock','--profile','REAL_IO']),
          ('inherited-runner-full',runner.main,['--run']),
          ('inherited-runner-mock',runner.main,['--run','--synthetic-observer-mock']),
          ('inherited-r-diagnostic',rdiag.run,[])]
    with contextlib.ExitStack() as stack:
        for target in ('subprocess.Popen','controller.Engine','controller.fixtures','gcore.Native','runtime_metrics.Win32MetricReader','notifications.CompletionHub'):
            stack.enter_context(patch(target,forbidden))
        for name,fn,args in plan:
            output=io.StringIO()
            with patch.object(sys,'argv',[name,*args]),contextlib.redirect_stdout(output):code=fn()
            response=json.loads(output.getvalue());assert code==2 and response['helpersStarted']==0
            assert response.get('mediaBytesRead',0)==0 and response.get('executionAllowed',response.get('realExecutionAllowed')) is False
            cases.append(dict(name=name,exitCode=code,response=response))
        api={}
        for name,fn in [('reserve_actual',synthetic_admission.reserve_actual),('claim_actual',synthetic_admission.claim_actual)]:
            try:fn('E2C-DENIED')
            except gcore.Refused as error:
                assert str(error)=='E2C_ACTUAL_FULL_NOT_AUTHORIZED_NEW_BATCH_REQUIRED';api[name]=str(error)
            else:raise AssertionError('ACTUAL_ENTRY_ACCEPTED')
        try:gdiag.fresh_file(reservation,dict(shouldNeverReplace=True))
        except FileExistsError:single='EXCLUSIVE_EXISTING_RESERVATION_REFUSED_NO_DIAGNOSTIC_RUN'
        else:raise AssertionError('SINGLE_G_RESERVATION_REPLACED')
    assert not guards and hashlib.sha256(reservation.read_bytes()).hexdigest()==before
    report=dict(schema=1,status='PASS',scope='E2C_ENTRY_DENIALS',cases=cases,actualAPIDenials=api,
        singleGReservationCheck=single,singleGReservationSha256=before,singleGReservationUnchanged=True,
        forbiddenConstructorsEntered=guards,newHelpers=0,newDiagnosticG=0,newOSMetricSamples=0,
        mediaBytesRead=0,realRootCreated=False,noInFlight=True,realExecutionAllowed=False)
    path=BASE/'evidence/entry-denials.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(evidence=str(path),status='PASS',cases=len(cases),newDiagnosticG=0,newHelpers=0)))

if __name__=='__main__':run()
