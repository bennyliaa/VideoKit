"""Stage-A-reviewed helper dispatch. No top-level product import or execution.

Full candidate/order binding is required after formal B dispatch. This file is
not a runnable authorization, and does not recover any previous Capture.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib,json,os,threading,subprocess

PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
HELPER_NAME='independent_budget.ps1'
BUDGET_INPUT_FIELDS=frozenset(('schema','artifactRoot','candidateRoot','admissionPath','admissionSha256','ref','root','name','wire','context','expectedFingerprint','expectedCaseIds'))

def digest(raw):return hashlib.sha256(raw).hexdigest()
def environment_digest():return digest(json.dumps(dict(os.environ),sort_keys=True,separators=(',',':')).encode())

@dataclass(frozen=True)
class CallSpec:
 key:str
 argv:tuple
 executable:str
 cwd:object
 env:object
 helper:str
 input_path:str
 output_path:str
 def kwargs(self):
  return dict(executable=self.executable,cwd=self.cwd,env=self.env,shell=False,close_fds=True,stdin=-3,stdout=-1,stderr=-1)
 def plan(self):return dict(argv=list(self.argv),cwd=self.cwd,env=self.env,profile=self.key)

def build_budget_spec(driver_root,scope_root):
 helper=str(Path(driver_root)/HELPER_NAME)
 input_path=str(Path(scope_root)/'budget-input.json')
 output_path=str(Path(scope_root)/'budget-result.json')
 return CallSpec(key='budget',argv=(PS,'-NoProfile','-NonInteractive','-File',helper,'-InputFile',input_path,'-OutputFile',output_path),executable=PS,cwd=None,env=None,helper=helper,input_path=input_path,output_path=output_path)

def freeze_helper_tuple(driver_root,scope_root):
 # The freezer and actual caller use exactly the same builder.
 return build_budget_spec(driver_root,scope_root)

class ClosedGuard:
 def __init__(self,formal_order,specs,original_popen,read_bound):
  self.order=formal_order;self.specs=specs;self.original_popen=original_popen
  self.read_bound=read_bound # Existing owned-IO receiver, retains unknown original refs.
  self.used=set();self.active=None;self.local=threading.local();self.calls=[];self.audit=[];self.stop=False
 def admit_before_capture(self,spec):
  if self.order.get('stage')!='FORMAL_B_FROZEN' or self.order.get('approved') is not True:raise ValueError('FORMAL_B_ORDER_REQUIRED')
  if self.stop or spec.key in self.used or self.specs.get(spec.key)!=spec:raise ValueError('EXACT_CALL_SPEC_REQUIRED')
  if spec.helper!=str(Path(self.order['driverRoot'])/HELPER_NAME) or spec.input_path!=str(Path(self.order['scopeRoot'])/'budget-input.json') or spec.output_path!=str(Path(self.order['scopeRoot'])/'budget-result.json'):raise ValueError('CALL_ROOT_BINDING_BEFORE_CAPTURE')
  if str(Path.cwd())!=self.order['cwd'] or environment_digest()!=self.order['inheritedEnvSha256']:raise ValueError('HOST_CONTEXT_MISMATCH_BEFORE_CAPTURE')
  if spec.executable!=spec.argv[0] or spec.helper!=spec.argv[4] or Path(spec.helper).name!=HELPER_NAME:raise ValueError('HELPER_CALLSITE_MISMATCH_BEFORE_CAPTURE')
  if not Path(spec.helper).is_file():raise ValueError('HELPER_FILE_MISSING_BEFORE_CAPTURE')
  if not Path(spec.input_path).is_file():raise ValueError('INPUT_FILE_MISSING_BEFORE_CAPTURE')
  if digest(self.read_bound(spec.helper,1048576))!=self.order['sourcePins'][spec.helper]:raise ValueError('HELPER_SOURCE_MISMATCH_BEFORE_CAPTURE')
  raw=self.read_bound(spec.input_path,1048576)
  if len(raw)>1048576 or digest(raw)!=self.order['inputPins'][spec.input_path]:raise ValueError('HELPER_INPUT_MISMATCH_BEFORE_CAPTURE')
  data=json.loads(raw.decode('utf-8-sig'))
  if type(data) is not dict or set(data)!=BUDGET_INPUT_FIELDS or data['schema']!='INDEPENDENT_BUDGET_INPUT_V1':raise ValueError('HELPER_INPUT_SCHEMA_BEFORE_CAPTURE')
  expected_admission=str(Path(self.order['candidateRoot'])/'tools/admission_checks.ps1')
  if data['candidateRoot']!=self.order['candidateRoot'] or data['artifactRoot']!=self.order['driverRoot'] or data['admissionPath']!=expected_admission or data['admissionSha256']!=self.order['sourcePins'][expected_admission]:raise ValueError('HELPER_CANDIDATE_BINDING_BEFORE_CAPTURE')
  if Path(spec.output_path).exists():raise ValueError('OUTPUT_ALREADY_EXISTS_BEFORE_CAPTURE')
  self.active=spec
  return dict(key=spec.key,spec=spec,checkedBeforeCapture=True)
 def check(self,argv,kwargs):
  spec=self.active
  if self.stop or spec is None or argv!=list(spec.argv) or kwargs!=spec.kwargs():raise ValueError('EXACT_ACTIVE_CALL_REQUIRED')
  if str(Path.cwd())!=self.order['cwd'] or environment_digest()!=self.order['inheritedEnvSha256']:raise ValueError('HOST_CONTEXT_CHANGED_NO_CONSTRUCTOR')
  if digest(self.read_bound(spec.helper,1048576))!=self.order['sourcePins'][spec.helper]:raise ValueError('HELPER_SOURCE_CHANGED_NO_CONSTRUCTOR')
  return spec
 def construct(self,argv,*pos,**kwargs):
  if pos:raise ValueError('NO_EXTRA_POSITIONAL_OPTIONS')
  spec=self.check(argv,kwargs)
  if spec.key in self.used:raise ValueError('EXACT_TUPLE_ONCE')
  self.used.add(spec.key);row=dict(key=spec.key,argv=list(argv),kwargs=kwargs);self.calls.append(row)
  self.local.expected=(kwargs['executable'],subprocess.list2cmdline(argv),kwargs['cwd'],kwargs['env'])
  try:
   original=self.original_popen(argv,**kwargs);row['constructorReturned']=True;return original
  finally:self.local.expected=None
 def observe(self,event,args):
  if event!='subprocess.Popen':return
  match=getattr(self.local,'expected',None)==args;self.audit.append(dict(matches=match))
  if not match:self.stop=True

def inspect_result_file(spec,expected_case_ids,expected_reasons,read_bound):
 # Failure metadata is saved even for missing/partial/malformed JSON.
 p=Path(spec.output_path)
 if not p.is_file():return dict(status='RESULT_FILE_MISSING',exists=False,path=spec.output_path)
 if p.stat().st_size>1048576:return dict(status='RESULT_FILE_BYTE_BOUND',exists=True,path=spec.output_path)
 raw=read_bound(p,1048576);base=dict(exists=True,path=spec.output_path,bytes=len(raw),sha256=digest(raw))
 def unique(pairs):
  d={};seen=set()
  for k,v in pairs:
   if k.casefold() in seen:raise ValueError('RESULT_DUPLICATE_FIELD')
   seen.add(k.casefold());d[k]=v
  return d
 try:d=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=unique)
 except (ValueError,UnicodeError) as e:return dict(base,status='RESULT_FILE_INVALID_JSON',error=type(e).__name__+':'+str(e))
 if type(d) is not dict or d.get('schema')!='INDEPENDENT_Q07_BUDGET_RESULT_V1':return dict(base,status='RESULT_SCHEMA_MISMATCH')
 rows=d.get('results');ids=[x.get('id') for x in rows] if type(rows) is list and all(type(x) is dict for x in rows) else None
 if ids!=expected_case_ids or d.get('complete') is not True or d.get('expectedCaseIds')!=expected_case_ids:return dict(base,status='RESULT_INCOMPLETE_OR_CASESET_MISMATCH',observedCaseIds=ids)
 if type(d.get('allPassed')) is not bool or any(type(x.get('pass')) is not bool for x in rows):return dict(base,status='RESULT_BOOLEAN_TYPE_MISMATCH')
 if d.get('syntheticAuthority') is not True or d.get('realAuthority') is not False or d.get('actualProductionOwner') is not False:return dict(base,status='RESULT_AUTHORITY_LABEL_MISMATCH')
 if any(x.get('want')!=expected_reasons[x['id']] or type(x.get('reason')) is not str or x['pass']!=(x['reason']==expected_reasons[x['id']]) for x in rows):return dict(base,status='RESULT_ROW_REASON_MISMATCH')
 if d['allPassed']!=all(x['pass'] for x in rows):return dict(base,status='RESULT_AGGREGATE_MISMATCH')
 return dict(base,status='RESULT_CASES_MATCHED' if d['allPassed'] else 'RESULT_CASE_FAILURES',data=d)

def budget_models(runtime):
 """Actual future callsite; candidate selfchecks helper is never selected."""
 spec=build_budget_spec(runtime.driver_root,runtime.scope_root)
 try:admission=runtime.guard.admit_before_capture(spec)
 except BaseException as error:
  runtime.save_call_failure(spec,'PRECONSTRUCTOR_REJECTED',error,capture=None)
  raise
 # No Capture/Journal factory is called before successful admission.
 capture=runtime.construct_capture_after_admission(admission,spec.plan())
 try:
  capture.launch(runtime.guard,90)
  disposition=capture.collect()
 except BaseException as error:
  # Existing original-owner retention protocol must keep these actual refs.
  runtime.retain_original_and_record(spec,capture,error)
  raise
 if not capture.returned or disposition.startswith('RETAIN'):
  runtime.retain_original_and_record(spec,capture,RuntimeError('ORIGINAL_NOT_RETURNED'))
  raise ValueError('ORIGINAL_NOT_RETURNED')
 # Persist native exit/stdout/stderr/return facts BEFORE inspecting result JSON.
 runtime.save_original_call(spec,capture,disposition)
 result=inspect_result_file(spec,runtime.expected_case_ids,runtime.expected_case_reasons,runtime.read_frozen_bytes)
 result['originalExitCode']=capture.exit_code
 result['originalStderrBytes']=len(capture.buffers[1])
 result['originalReturned']=capture.returned
 result['disposition']=disposition
 runtime.save_helper_result(spec,result)
 if capture.exit_code!=0 or capture.buffers[1] or result['status']!='RESULT_CASES_MATCHED':raise ValueError('HELPER_RESULT_NOT_ACCEPTED')
 return result
