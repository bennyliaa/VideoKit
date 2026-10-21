"""Execute actual J parent helper with pending-disk/console faults; same original child always waited/closed."""
from pathlib import Path
import importlib.util,subprocess,types,json,hashlib,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence/parent-faults-002';E.mkdir(exist_ok=False);source=B/'tools/check_host.py';results=[]
for mode in ['PENDING_WRITE','CONSOLE','BOTH']:
 root=E/mode;root.mkdir();spec=importlib.util.spec_from_file_location('j_parent_'+mode,source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.E=root;module.commands=[];module.OWNERS={};originalWrite=module.write;captured={}
 class Original(subprocess.Popen):
  def __init__(self,*a,**kw):
   super().__init__(*a,**kw);captured['process']=self
  def wait(self,timeout=None):return super().wait(timeout=0.02 if timeout==20 else timeout)
 def write(p,v):
  if mode in ['PENDING_WRITE','BOTH'] and p.name.endswith('.pending.json'):raise OSError('CONTROLLED_PENDING_DISK_FAILURE')
  originalWrite(p,v)
 def console(*args,**kw):
  if mode in ['CONSOLE','BOTH']:raise OSError('CONTROLLED_CONSOLE_FAILURE')
 module.subprocess=types.SimpleNamespace(Popen=Original,TimeoutExpired=subprocess.TimeoutExpired);module.write=write;module.print=console
 qualified=False
 try:module.run('original',[sys.executable,'-B','-c',"import time;time.sleep(0.35);print('LOCAL_ORIGINAL_CHILD_RETURN')"])
 except AssertionError:qualified=False
 else:raise AssertionError('qualification must remain failed')
 record=json.loads((root/'original.exit.json').read_text());assert not module.OWNERS and record['pid']==captured['process'].pid and record['exitCode']==0 and record['parentOriginalWaitReturned'] and record['parentRecordingFilesCloseReturned'] and not record['qualificationPreserved'];assert record['diagnosticFailures']
 results.append(dict(mode=mode,originalProcessSame=True,naturalWaitReturned=True,originalFilesCloseReturned=True,qualification=False,diagnosticFailures=record['diagnosticFailures'],kill=False));print(mode,'PASS same Popen waited and original files closed')
(E/'results.json').write_text(json.dumps(dict(status='PASS_ACTUAL_PARENT_LOG_FAULT_CUSTODY',source=source.relative_to(R).as_posix(),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),onlyWaitAdapterSeconds=0.02,groups=results,newUnknownObjects=0),indent=2)+'\n')
