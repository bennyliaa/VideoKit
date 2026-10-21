"""Finite host-only checks. CLI uses unchanged authorization/registry gates and an explicit local SDK port substitute."""
from pathlib import Path
import hashlib,json,subprocess,shutil,difflib
from build_host import B,R,J,pin,write,sha
E=B/'evidence/host-checks-001';W=B/'.checks/tests';JAR=B/'artifacts/e13c-host-tools.jar'
def record(fields):return (json.dumps({'e9':1,'fields':dict(sorted(fields.items()))},separators=(',',':'),ensure_ascii=True)+'\n').encode()
def main():
 E.mkdir(exist_ok=False);W.mkdir(parents=True,exist_ok=False);commands=[];results=[]
 def run(name,args,expect=0,needle=None):
  argv=[str(x) for x in args];commands.append({'name':name,'argv':argv});write(E/'commands.json',commands)
  with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
   p=subprocess.Popen(argv,stdout=so,stderr=se)
   try:code=p.wait(timeout=20)
   except subprocess.TimeoutExpired:write(E/(name+'.pending.json'),{'pid':p.pid,'originalPending':True,'killed':False});raise
  raw=(E/(name+'.stdout.txt')).read_bytes()+(E/(name+'.stderr.txt')).read_bytes()
  row={'name':name,'exitCode':code,'pid':p.pid,'naturalReturn':True,'stdout':pin(E/(name+'.stdout.txt')),'stderr':pin(E/(name+'.stderr.txt'))};write(E/(name+'.exit.json'),row)
  assert code==expect,(name,code,raw.decode(errors='replace'))
  if needle:assert needle.encode() in raw,(name,raw.decode(errors='replace'))
  results.append(row);print(name,'PASS',flush=True);return raw
 def compile(name,sources,dest,cp=JAR):
  dest.mkdir(parents=True);run(name,[J/'javac.exe','-encoding','UTF-8','-cp',cp,'-d',dest,*sources])
 real=W/'real';compile('compile-real',[B/'checks/E13COnceCheck.java'],real)
 for mode in ['E13_OK','E11_OK','E13_OLD_NAME','E11_NEW_NAME','ARBITRARY','WRONG_INTENT','FORCE_FAIL','CLOSE_IN_FLIGHT']:
  run(mode,[J/'java.exe','-cp',str(real)+';'+str(JAR),'com.videokit.spike.e4.E13COnceCheck',mode,E/'helper-fixtures'/mode],needle='PASS '+mode)
 # Real public main and actual helper from production JAR. Only E9HostDeployment.run is replaced.
 # Original DEVICE trust bytes and full registry are retained; this is not a synthetic gate bypass.
 source=R/'docs/coder/d1e13a/tools/E9HostDeployment.java';text=source.read_text(encoding='utf-8-sig')
 original='private byte[] run(List<String> args,int max)throws Exception{if(failed)throw new IOException("E9_PC_PORT_FAILED_NO_RETRY");try{return commands.run(args,max);}catch(Exception e){failed=true;throw e;}}'
 replacement='private byte[] run(List<String> args,int max)throws Exception{Files.writeString(Paths.get(System.getProperty("e13c.local.frontdoor")),String.join("\\n",args)+"\\n",StandardOpenOption.CREATE_NEW);throw new IOException("E13C_LOCAL_FIRST_SDK_BOUNDARY_NO_CHILD");}'
 assert text.count(original)==1;stub=B/'checks/port-substitute/E9HostDeployment.java';stub.parent.mkdir(exist_ok=True);stub.write_text(text.replace(original,replacement),encoding='utf-8')
 write(E/'port-substitute-source.json',{'actualPortSource':pin(source),'substitute':pin(stub),'onlyChange':'private run: record exact first SDK argv then throw before commands.run; actual entry/helper/auth/registry untouched'})
 (E/'port-substitute.diff').write_text(''.join(difflib.unified_diff(text.splitlines(True),stub.read_text().splitlines(True),fromfile=pin(source)['path'],tofile=pin(stub)['path'])),encoding='utf-8')
 port=W/'port';compile('compile-port',[stub],port)
 base=R/'docs/tester/D1_E13A_E13B_TABLET_EXECUTION/db65c958-5163-4467-90e0-6f099076142f/inputs'
 sourceConfig=base/'activation-trust-deploy.json';c=json.loads(sourceConfig.read_text())['fields'];registry=Path(c['registryPath']);registryCopy=E/'cli-fixtures/registry-copy'
 shutil.copytree(registry,registryCopy);registryRows=[pin(p) for p in sorted(registry.rglob('*')) if p.is_file()]
 write(E/'historical-input-pins.json',{'config':pin(sourceConfig),'scope':pin(base/'runtime-scope.json'),'release':pin(base/'activation-release.json'),'registryOriginalFiles':registryRows,'note':'Historical DEVICE trust retained unchanged in local fixtures. This is not a new dispatch approval; SDK run is replaced before any child.'})
 release=base/'activation-release.json';scope=base/'runtime-scope.json'
 fixed={**c,'registryPath':registryCopy.resolve().as_posix(),'scopePath':scope.resolve().as_posix()}
 def cli(name,basename='e13a-activation-deployment.once',existing=None,kind=None,synthetic=False,repeat=None):
  root=E/'cli-fixtures'/name;root.mkdir();once=root/basename
  fields={**fixed,'dispatchRecord':once.resolve().as_posix()}
  if kind:fields['kind']=kind
  if synthetic:
   import base64
   plan=json.loads(base64.urlsafe_b64decode(fields['plan']+'='*((-len(fields['plan']))%4)))['fields'];plan['environment']='SYNTHETIC_LOCAL';raw=record(plan);fields['plan']=base64.urlsafe_b64encode(raw).decode().rstrip('=');fields['planSha']=sha(raw)
  config=root/'local-test-config.json';config.write_bytes(record(fields));mark=root/'first-sdk-argv.txt'
  if existing is not None:once.write_bytes(existing)
  args=[J/'java.exe','-De13c.local.frontdoor='+str(mark),'-cp',str(port)+';'+str(JAR),'com.videokit.spike.e4.E13HostActivationSession','--approved-e13-deploy',config,sha(config.read_bytes()),release,sha(release.read_bytes()),'UNUSED_LOCAL_APP','UNUSED_LOCAL_TEST','UNUSED_LOCAL_FIXTURE']
  needle='E13C_LOCAL_FIRST_SDK_BOUNDARY_NO_CHILD' if existing is None and basename=='e13a-activation-deployment.once' and kind is None and not synthetic else 'E11_DEPLOYMENT_ALREADY_RESERVED_NO_RETRY' if existing is not None else 'E13_NEW_FIXED_ONCE_REQUIRED' if basename!='e13a-activation-deployment.once' else 'E13_CONFIG_SCHEMA' if kind else 'E13_REAL_REGISTRY_REQUIRED'
  before=once.read_bytes() if once.exists() else None;raw=run(name,args,expect=1,needle=needle)
  assert b'"kind":"pcClosed"' in raw and b'"allOriginalsReturned":"true"' in raw
  if needle=='E13C_LOCAL_FIRST_SDK_BOUNDARY_NO_CHILD':
   assert mark.exists()
   argv=mark.read_text().splitlines();assert Path(argv[0]).as_posix()=='D:/Android/SDK/platform-tools/adb.exe' and argv[1:]==['-s','HA1Q6WXR','shell','run-as','com.videokit.app','stat','-c','%u:%i','.']
   intent=json.loads(once.read_text())['fields'];assert intent['kind']=='e13ActivationDispatchIntent' and intent['config']==sha(config.read_bytes()) and intent['scope']==c['scopeSha']
   saved=once.read_bytes();run(name+'-cross-jvm-repeat',args,expect=1,needle='E11_DEPLOYMENT_ALREADY_RESERVED_NO_RETRY');assert once.read_bytes()==saved
  else:
   assert not mark.exists()
   assert (once.read_bytes() if once.exists() else None)==before
 cli('CLI_E13_EXACT')
 cli('CLI_E13_WRONG_NAME','activation-deployment.once')
 cli('CLI_E13_ARBITRARY','anything.once')
 cli('CLI_WRONG_CONFIG_ROLE',kind='activationTrust')
 cli('CLI_SYNTHETIC_DEVICE_GATE_REJECTED',synthetic=True)
 cli('CLI_PARTIAL_FILE',existing=b'{partial local fixture')
 cli('CLI_EMPTY_FILE',existing=b'')
 # Finite close-exception check: actual helper, a retention-only supervisor substitute avoids
 # leaving an intentionally permanent non-daemon UNKNOWN custodian in the developer session.
 stubS=B/'checks/authority-substitute/E9PcSupervisor.java';stubS.parent.mkdir(exist_ok=True)
 stubS.write_text('package com.videokit.spike.e4; public final class E9PcSupervisor { public interface OriginalAuthority {boolean originalResourcesReturned();} public interface Cleanup {E9Record run(E9Record command)throws Exception;} public Object authority;public OriginalAuthority resources;public E9PcSupervisor(String scope){}public void retainAuthority(Object o,Cleanup cleanup,OriginalAuthority r){authority=o;resources=r;} }\n',encoding='utf-8')
 unknown=W/'unknown';compile('compile-unknown',[stubS,B/'checks/E13CUnknownCheck.java'],unknown)
 run('CLOSE_UNKNOWN',[J/'java.exe','-cp',str(unknown)+';'+str(JAR),'com.videokit.spike.e4.E13CUnknownCheck',E/'helper-fixtures/CLOSE_UNKNOWN'],needle='PASS CLOSE_UNKNOWN')
 for row in registryRows:assert pin(R/row['path'])==row
 for p in registryCopy.rglob('*'):
  if p.is_file():assert p.read_bytes()==(registry/p.relative_to(registryCopy)).read_bytes()
 write(E/'results.json',{'status':'PASS_E13C_FINITE_HOST_CHECKS','results':results,'helperGroups':8,'publicCliAttempts':8,'closeUnknownActualHelper':True,'closeUnknownSupervisor':'RETENTION_ONLY_SUBSTITUTE_NO_CUSTODIAN_THREAD','actualCustodianInFlight':'CLOSE_IN_FLIGHT actual pcIsolationAck and original natural return verified','firstSdkPort':'LOCAL_SUBSTITUTE_THROW_NO_CHILD','realDeviceAuthorizationGate':'UNCHANGED_AND_SYNTHETIC_ENVIRONMENT_REJECTED','deviceCalls':0,'installCalls':0,'realOnceWrites':0,'localTestOnceWritesOnly':True,'oldSuitesRerun':0})
if __name__=='__main__':main()
