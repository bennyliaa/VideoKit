"""Tester-only single-method executor. Default PLAN_ONLY. Never enables/clears/uninstalls.
Exclusive attempt directory, actual streaming log cap, failed exit halts dispatch.
"""
from pathlib import Path
import argparse,json,re,subprocess,threading
import device_guard
ROOT=Path(__file__).resolve().parents[4];ADB='D:/Android/SDK/platform-tools/adb.exe';TOTAL_LOG_BUDGET=32*1024*1024
class ExecutionUnknown(RuntimeError):pass
class CommandFailed(RuntimeError):pass
def capture(command,path,timeout,limit):
    """Bound disk writes while reading; kill only this helper's own CLI child on limit/deadline.
    Terminating adb client does NOT prove remote instrumentation stopped.
    """
    if limit<1:raise ExecutionUnknown('LOG_BUDGET_EXHAUSTED')
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);errors=[]
    def stop_local_child():
        try:
            if process.poll() is None:process.kill()
        except OSError:pass
    def reader():
        written=0
        try:
            with path.open('xb') as out:
                while True:
                    chunk=process.stdout.read1(min(65536,limit-written+1))
                    if not chunk:break
                    allowed=min(len(chunk),limit-written)
                    if allowed:out.write(chunk[:allowed]);written+=allowed
                    if len(chunk)>allowed:raise ExecutionUnknown('LOG_BUDGET_EXCEEDED')
        except Exception as error:errors.append(error);stop_local_child()
    thread=threading.Thread(target=reader,daemon=True);thread.start();thread.join(timeout)
    if thread.is_alive():
        stop_local_child();thread.join(2);raise ExecutionUnknown('COMMAND_DEADLINE_DEVICE_STATE_UNKNOWN')
    try:code=process.wait(timeout=2)
    except subprocess.TimeoutExpired:stop_local_child();raise ExecutionUnknown('COMMAND_EXIT_STATE_UNKNOWN')
    finally:
        if not thread.is_alive():process.stdout.close()
    if errors:raise errors[0]
    if code!=0:raise CommandFailed('COMMAND_EXIT_NONZERO')
    return path.read_text(encoding='utf-8',errors='replace')
def classify_output(output,group):
    if 'C14_ENVIRONMENT_BLOCKED' in output or re.search(r'\bCPU_ENVIRONMENT_BLOCKED\b',output):
        return 'ENVIRONMENT_UNKNOWN' if 'app_setting=-1' in output else 'ENVIRONMENT_BLOCKED'
    if 'FAILURES!!!' in output or re.search(r'INSTRUMENTATION_STATUS_CODE: -2\b',output):return 'TEST_FAILED'
    if 'C14_PIPELINE_CAPABILITY_BLOCKED' in output:return 'CAPABILITY_BLOCKED'
    if any(s in output for s in ['INSTRUMENTATION_FAILED','INSTRUMENTATION_ABORTED','AssumptionViolatedException']):return 'EXECUTION_UNKNOWN'
    if not re.search(r'OK\s*\(1 test\)',output):return 'EXECUTION_UNKNOWN'
    if group in ('cpu','pipeline','encoder') and 'C14_ENVIRONMENT_READY' not in output:return 'EXECUTION_UNKNOWN'
    return 'METHOD_ASSERTIONS_PASSED_REVIEW_LEDGER_AND_RAW_SEPARATELY'
def require_planned(plan,group,method):
    if any(row["method"]==method for row in plan.get("not_run_unchanged_platform_limit",[])):raise ExecutionUnknown("NOT_RUN_UNCHANGED_PLATFORM_LIMIT")
    if method not in plan["groups"][group]:raise ExecutionUnknown("METHOD_NOT_ADMITTED")
    return True

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--serial');p.add_argument('--method');p.add_argument('--group',choices=['cpu','host','legacy','pipeline','encoder'],default='cpu');p.add_argument('--attempt-dir');p.add_argument('--log-budget-root');p.add_argument('--execute',action='store_true');p.add_argument('--candidate-and-data-reviewed',action='store_true');args=p.parse_args()
    if not args.execute:print(json.dumps({'state':'PLAN_ONLY_NO_DEVICE_COMMANDS','candidate':'D1-20261016-C14','required':'serial, method, exclusive tester attempt-dir, per-device log-budget-root, review; actual enabled/service preflight before each method'}));return
    if not args.candidate_and_data_reviewed or not args.serial or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,80}',args.serial) or not args.method or not re.fullmatch(r'[A-Za-z][A-Za-z0-9]{1,100}',args.method) or not args.attempt_dir or not args.log_budget_root:p.error('explicit serial/method/review/attempt-dir/log-budget-root required')
    cls={'encoder':'C14EncoderDeviceTests','pipeline':'C14PipelineDeviceTests','cpu':'C14CpuDeviceTests','host':'C14DeviceTests','legacy':'C14IsolatedDeviceTests'}[args.group]
    source=ROOT/'docs/coder/d1c14/device/com/videokit/spike/c14'/(cls+'.java')
    if args.method not in re.findall(r'@Test public void (\w+)\(',source.read_text(encoding='utf-8')):p.error('method not in frozen group')
    plan=json.loads((ROOT/'docs/coder/d1c14/tools/device_plan.json').read_text(encoding='utf-8'))
    try:require_planned(plan,args.group,args.method)
    except ExecutionUnknown as error:p.error(str(error))
    directory=Path(args.attempt_dir).resolve();budget_root=Path(args.log_budget_root).resolve();tester=(ROOT/'docs/tester').resolve()
    if not directory.is_relative_to(budget_root) or not budget_root.is_relative_to(tester) or budget_root==tester:p.error('per-device budget-root and attempt-dir must stay under docs/tester')
    directory.mkdir(parents=True,exist_ok=False);counter=0;phase='PREFLIGHT';state=None;code=None
    def checked(arguments,timeout=20):
        nonlocal counter
        counter+=1;used=sum(path.stat().st_size for path in budget_root.rglob('*.log') if path.is_file());remaining=TOTAL_LOG_BUDGET-used
        return capture([ADB,'-s',args.serial,*arguments],directory/(str(counter)+'-command.log'),timeout,min(remaining,1048576 if phase=='PREFLIGHT' else TOTAL_LOG_BUDGET))
    try:
        facts=device_guard.require_ready(args.serial,checked);(directory/'preflight.json').write_text(json.dumps(facts,indent=2),encoding='utf-8');phase='TEST'
        output=checked(['shell','am','instrument','-w','-r','-e','class','com.videokit.spike.c14.'+cls+'#'+args.method,'com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner'],240)
        state=classify_output(output,args.group);code=state
    except device_guard.EnvironmentBlocked as error:
        code=str(error);state='ENVIRONMENT_UNKNOWN' if 'UNKNOWN' in code else 'ENVIRONMENT_BLOCKED'
    except CommandFailed as error:code=str(error);state='PREPARATION_FAILED' if phase=='PREFLIGHT' else 'EXECUTION_UNKNOWN'
    except Exception as error:code=str(error) if re.fullmatch(r'[A-Z_0-9]{3,100}',str(error)) else 'EXECUTION_OR_PREPARATION_UNKNOWN';state='EXECUTION_UNKNOWN'
    passed=state=='METHOD_ASSERTIONS_PASSED_REVIEW_LEDGER_AND_RAW_SEPARATELY'
    (directory/'result.json').write_text(json.dumps({'state':state,'code':code,'phase':phase,'serial':args.serial,'method':args.method,'no_next_method_dispatched':True,'policy':'nonzero exit stops outer scheduler; no remote work stopped/released claim from CLI timeout'},indent=2),encoding='utf-8')
    if not passed:raise SystemExit(2)
if __name__=='__main__':main()
