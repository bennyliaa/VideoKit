"""Offline metadata semantic checks only. No product/binding/source/native execution or device query."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
sys.dont_write_bytecode=True
from process_record import parse
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';E.mkdir(exist_ok=True)
root=R/'docs/tester/D1_E11_FINAL_R1_TABLET_EXECUTION/a129ad0a-9d93-49c6-8289-9087afd419ff/evidence'
names=['metadata-03-activity-processes-stdout.txt','metadata-23-before-normalAviSixRealFrames-activity-stdout.txt','metadata-29-before-capabilityDenialDoesNotOpenSource-activity-stdout.txt','metadata-35-before-cancelRejectsWrongEpochOversizeAndLateFrame-activity-stdout.txt']
ref=B/'reference/raw';ref.mkdir(parents=True,exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(raw),'sha256':sha(raw)}
inputs=[]
for name in names:
 p=root/name;target=ref/name;target.write_bytes(p.read_bytes());inputs.append({'source':pin(p),'copy':pin(target)})
base=(ref/names[0]).read_text();site=base.index('  OOM levels:\n')
def active_item(i,pkg='other.project.test',finished='false'):
 return ('    Instrumentation #'+str(i)+': ActiveInstrumentation{abcdef '+pkg+'/.Runner '+('FINISHED ' if finished=='true' else '')+'0 procs}\n'
  +'      mClass=ComponentInfo{'+pkg+'/.Runner}\n      mFinished='+finished+'\n'
  +'      mRunningProcesses:\n      mTargetProcesses=['+pkg+',\n        '+pkg+':worker]\n'
  +'      mTargetInfo=ApplicationInfo{123 '+pkg+'}\n        packageName='+pkg+'\n'
  +'mHasBackgroundActivityStartsPermission=false\nmHasBackgroundForegroundServiceStartsPermission=false\n'
  +'      mArguments=Bundle[{case=controlled-metadata-fixture,\n        continuation=preserve-this-line}]\n')
one='  Active instrumentation:\n'+active_item(0)+'\n'
two='  Active instrumentation:\n'+active_item(0)+active_item(1,'com.videokit.app.test','true')+'\n'
cases=[]
for item,name in zip(inputs,names):cases.append((name.replace('.txt',''),(ref/name).read_text(),'IDLE','HISTORICAL_REAL_VENDOR_RAW',0,''))
cases += [
 ('active-other-project',base[:site]+one+base[site:],'ACTIVE','CONTROLLED_INSERTION_AOSP_ACTIVE_BLOCK_IN_REAL_RAW',0,one),
 ('active-multiple-finished-and-multiline',base[:site]+two+base[site:],'ACTIVE','CONTROLLED_INSERTION_AOSP_ACTIVE_BLOCK_IN_REAL_RAW',0,two),
 ('unsupported-exit-zero','Unknown command: instrumentation\n','BLOCKED','SYNTHETIC_DIAGNOSTIC_NOT_VENDOR_OBSERVATION',0,''),
 ('unsupported-with-good-header','ACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)\nError: unknown command\n','BLOCKED','CONTROLLED_DIAGNOSTIC',0,''),
 ('truncated-before-final-tail',base[:base.rindex('  mForceBackgroundCheck=')],'BLOCKED','CONTROLLED_TRUNCATION_REAL_RAW',0,''),
 ('missing-header',base.split('\n',1)[1],'BLOCKED','CONTROLLED_MUTATION_REAL_RAW',0,''),
 ('unknown-format-oom',base.replace('  OOM levels:','  OEM_UNRECOGNIZED_OOM:'),'BLOCKED','CONTROLLED_MUTATION_REAL_RAW',0,''),
 ('tail-then-warning',base+'Warning: incomplete dump\n','BLOCKED','CONTROLLED_APPEND_REAL_RAW',0,''),
 ('duplicate-header',base+base,'BLOCKED','CONTROLLED_DUPLICATE_REAL_RAW',0,''),
 ('missing-command-status',base,'BLOCKED','CONTROLLED_MISSING_STATUS',None,''),
 ('command-failed-after-valid-text',base,'BLOCKED','CONTROLLED_RETURNED_NONZERO',1,''),
 ('empty-active-header',base[:site]+'  Active instrumentation:\n'+base[site:],'BLOCKED','CONTROLLED_INCOMPLETE_ACTIVE_BLOCK',0,''),
 ('active-missing-body-field',base[:site]+one.replace('      mArguments=','      UNRECOGNIZED=')+base[site:],'BLOCKED','CONTROLLED_INCOMPLETE_ACTIVE_BLOCK',0,''),
 ('oversize-active-block',base[:site]+one.replace('preserve-this-line','x'*3500)+base[site:],'BLOCKED','CONTROLLED_LIMIT',0,''),
 ('overlong-raw-line',base[:site]+('x'*4097)+'\n'+base[site:],'BLOCKED','CONTROLLED_LIMIT',0,''),
 ('truncation-diagnostic',base+'*** DUMP TIMEOUT ***\n','BLOCKED','CONTROLLED_DIAGNOSTIC',0,''),
]
out=E/'metadata-shell-cases';out.mkdir(exist_ok=False);results=[]
shell=Path('C:/Program Files/Git/bin/bash.exe'); wrapper=B/'tools/run_shell_reader.sh'
wrapper.write_text('set -eu\n. '+str(B/'tools/processes_reader.sh').replace(chr(92),'/')+'\ne13b_parse_processes\n',encoding='utf-8',newline='\n')
for name,text,expected,origin,status,expected_block in cases:
 payload=text+('' if status is None else '\nE13B_DUMPSYS_EXIT='+str(status)+'\n')
 file=out/(name+'.input.txt');file.write_text(payload,encoding='utf-8',newline='\n')
 command=[str(shell),'--noprofile','--norc','--posix',wrapper.as_posix()]
 result=subprocess.run(command,input=file.read_bytes(),capture_output=True,timeout=15)
 (out/(name+'.stdout.txt')).write_bytes(result.stdout);(out/(name+'.stderr.txt')).write_bytes(result.stderr)
 if expected=='BLOCKED':assert result.returncode==42,(name,result.returncode,result.stdout,result.stderr);parsed={'state':'BLOCKED'}
 else:
  assert result.returncode==0,(name,result.stdout,result.stderr)
  parsed=parse(result.stdout);assert parsed['state']==expected,(name,parsed)
  if expected_block:assert parsed['completeActiveBlock']==expected_block,(name,'active block changed/lost lines')
 row={'case':name,'expected':expected,'origin':origin,'originalDeviceExecution':False,'input':pin(file),'argv':command,'exitCode':result.returncode,'stdout':pin(out/(name+'.stdout.txt')),'stderr':pin(out/(name+'.stderr.txt')),'parsed':parsed}
 results.append(row);print(name,expected,'PASS',flush=True)
summary={'status':'PASS_METADATA_SEMANTICS_ONLY','cases':results,'historicalVendorInputs':inputs,'shellReader':pin(B/'tools/processes_reader.sh'),'pythonFraming':pin(B/'tools/process_record.py'),'activeFixturesAreDerivedNotActualDeviceEvents':True,'deviceCalls':0,'productTests':0,'builds':0}
(E/'metadata-shell-check-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
