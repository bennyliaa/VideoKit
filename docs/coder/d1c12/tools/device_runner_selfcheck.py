from pathlib import Path
import sys,tempfile
import run_device_c12 as runner
checks=0
def yes(value):
 global checks
 assert value;checks+=1
yes(runner.classify_output('C12_ENVIRONMENT_READY\nFAILURES!!!','cpu')=='TEST_FAILED')
yes(runner.classify_output('C12_ENVIRONMENT_BLOCKED app_setting=2\nOK (1 test)','cpu')=='ENVIRONMENT_BLOCKED')
yes(runner.classify_output('C12_ENVIRONMENT_BLOCKED app_setting=-1','cpu')=='ENVIRONMENT_UNKNOWN')
yes(runner.classify_output('C12_ENVIRONMENT_READY\nOK (1 test)','cpu').startswith('METHOD_ASSERTIONS_PASSED'))
yes(runner.classify_output('OK (0 tests)','cpu')=='EXECUTION_UNKNOWN')
yes(runner.classify_output('OK (1 test)','cpu')=='EXECUTION_UNKNOWN')
yes(runner.classify_output('INSTRUMENTATION_ABORTED','cpu')=='EXECUTION_UNKNOWN')
base=Path(__file__).resolve().parents[1]/'outputs';directory=Path(tempfile.mkdtemp(prefix='runner-local-',dir=base))
path=directory/'bounded.log'
try:runner.capture([sys.executable,'-c','import os; os.write(1,b"x"*8192)'],path,3,1024);raise AssertionError('unbounded output accepted')
except runner.ExecutionUnknown as error:yes(str(error)=='LOG_BUDGET_EXCEEDED');yes(path.stat().st_size<=1024)
try:runner.capture([sys.executable,'-c','import time; time.sleep(3)'],directory/'timeout.log',.05,1024);raise AssertionError('deadline ignored')
except runner.ExecutionUnknown as error:yes('DEADLINE' in str(error))
try:runner.capture([sys.executable,'-c','raise SystemExit(3)'],directory/'exit.log',3,1024);raise AssertionError('exit ignored')
except runner.CommandFailed:checks+=1
try:runner.capture([sys.executable,'-c','print("must not overwrite")'],path,3,1024);raise AssertionError('old result overwritten')
except FileExistsError:checks+=1
print('PASS',checks,'local output-bound/classification/exit/deadline/no-overwrite checks; only own Python children; NO ADB')
