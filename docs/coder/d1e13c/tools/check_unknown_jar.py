"""Tighten UNKNOWN evidence to execute the exact shipped helper member, not a second compile."""
from pathlib import Path
import subprocess,json
from build_host import B,R,J,pin,write
E=B/'evidence/unknown-jar-002';E.mkdir(exist_ok=False);W=B/'.checks/unknown-jar-002';W.mkdir(parents=True,exist_ok=False);jar=B/'artifacts/e13c-host-tools.jar'
s=B/'checks/authority-substitute/E9PcSupervisor.java'
s.write_text('package com.videokit.spike.e4; public final class E9PcSupervisor { public interface OriginalAuthority {boolean originalResourcesReturned();} public interface Cleanup {E9Record run(E9Record command)throws Exception;} public Object authority;public OriginalAuthority resources;public E9PcSupervisor(String scope){}public void retainAuthority(Object o,Cleanup cleanup,OriginalAuthority r){authority=o;resources=r;} }\n',encoding='utf-8')
commands=[[str(J/'javac.exe'),'-encoding','UTF-8','-cp',str(jar),'-d',str(W),str(s),str(B/'checks/E13CUnknownCheck.java')],[str(J/'java.exe'),'-verbose:class','-cp',str(W)+';'+str(jar),'com.videokit.spike.e4.E13CUnknownCheck',str(E/'local-test-once')]]
write(E/'inputs.json',{'jar':pin(jar),'sources':[pin(s),pin(B/'checks/E13CUnknownCheck.java')],'commands':commands,'actualHelperRecompiled':False})
for name,cmd in zip(['compile','unknown'],commands):
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen(cmd,stdout=so,stderr=se);code=p.wait(timeout=20)
 write(E/(name+'.exit.json'),{'exitCode':code,'pid':p.pid,'naturalReturn':True});assert code==0
raw=(E/'unknown.stdout.txt').read_text();assert 'PASS CLOSE_UNKNOWN' in raw
lines=[s for s in raw.splitlines() if 'com.videokit.spike.e4.E11DeploymentOnce' in s and '$$Lambda' not in s];assert len(lines)==4 and all('e13c-host-tools.jar' in s for s in lines)
assert not list(W.rglob('E11DeploymentOnce*.class'))
write(E/'results.json',{'status':'PASS_EXACT_SHIPPED_HELPER_UNKNOWN','helperClassLoadLines':lines,'actualHelperRecompiled':False,'supervisor':'FINITE_RETENTION_SUBSTITUTE_ONLY','actualCustodianUnknownClaim':False,'dispatch':0,'originalCloseAcknowledged':False,'closeAttempts':1,'secondClose':False,'deviceCalls':0})
print('PASS exact shipped helper UNKNOWN; retention substitute only; no actual UNKNOWN custodian closure claim')
