"""Audit existing successful UNKNOWN JVM output; no rebuild or test replay."""
import json
from build_host import B,pin,write
E=B/'evidence/unknown-jar-002';raw=(E/'unknown.stdout.txt').read_text()
for name in ['compile','unknown']:assert json.loads((E/(name+'.exit.json')).read_text())['exitCode']==0
assert 'PASS CLOSE_UNKNOWN' in raw
lines=[s for s in raw.splitlines() if 'com.videokit.spike.e4.E11DeploymentOnce' in s and '$$Lambda' not in s]
assert len(lines)==4 and all('e13c-host-tools.jar' in s for s in lines)
assert not list((B/'.checks/unknown-jar-002').rglob('E11DeploymentOnce*.class'))
write(E/'results.json',{'status':'PASS_EXACT_SHIPPED_HELPER_UNKNOWN','helperClassLoadLines':lines,'actualHelperRecompiled':False,'supervisor':'FINITE_RETENTION_SUBSTITUTE_ONLY','actualCustodianUnknownClaim':False,'dispatch':0,'originalCloseAcknowledged':False,'closeAttempts':1,'secondClose':False,'deviceCalls':0,'auditCorrection':'Initial post-run class-origin assertion also matched runtime-generated $$Lambda classes. Corrected existing-log audit excludes generated lambdas; original two JVM exits both 0; no rerun.'})
print('PASS existing exact shipped helper UNKNOWN evidence; no JVM replay')
