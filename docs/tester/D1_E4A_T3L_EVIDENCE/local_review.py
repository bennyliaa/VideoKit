"""One no-write shell syntax and scope review, not device execution or payload replay."""
from pathlib import Path
import hashlib,json,subprocess,datetime
E=Path(__file__).resolve().parent;SH=r'C:\Program Files\Git\usr\bin\sh.exe'
assert not (E/'local-review.json').exists()
rows=[]
for name in ['read_guards.sh','read_receiver.sh']:
 p=E/name;text=p.read_text()
 assert all(token not in text for token in ['mkdir','cat >','tee ','kill ','rm ','mv ','/proc/7718','/proc/7722','awk','python','perl'])
 assert '> ' not in text and '>>' not in text
 if name=='read_guards.sh':
  assert text.count('/system/bin/toybox sha256sum --')==1 and text.count('/system/bin/toybox stat -c')==2
  assert 'set -e' not in text and '[ "$size" -gt 256 ]' in text and '[ "$target_L" -ne 1 ]' in text
 else:assert 'for fd in 0 1 2 3' in text and '/proc/16643/fd/$fd' in text
 out=subprocess.run([SH,'-n',str(p)],capture_output=True,timeout=15,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));(E/(name+'.syntax.stdout.txt')).write_bytes(out.stdout);(E/(name+'.syntax.stderr.txt')).write_bytes(out.stderr);assert out.returncode==0
 rows.append({'file':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'syntaxExit':0,'writeOperations':0})
result={'at':datetime.datetime.now().astimezone().isoformat(),'status':'PASS','scope':'ONE_LOCAL_NO_WRITE_SYNTAX_AND_STATIC_SCOPE_BATCH','scripts':rows,'deviceCalls':0,'mediaReads':0,'payloadWrites':0,'signals':0,'shaCallsCap':1,'targetStatCallsCap':2,'procPid':16643,'fdLinkCallsCap':4,'externalInterfaces':'Previously observed id/pwd/test/cat/stat/readlink/sha256sum/od; UID and step handling use shell builtins; set-C confined to no-write subshell'}
(E/'local-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
