"""One finite local shell syntax/field contract check, no device or real media."""
from pathlib import Path
import hashlib,json,subprocess,shlex,datetime
E=Path(__file__).resolve().parent;SH=r'C:\Program Files\Git\usr\bin\sh.exe'
assert not (E/'local-review.json').exists()
fields=(E/'owner3_fields.sh').read_text();body=(E/'owner3_body.sh').read_text();control='set -efu\n'+fields+'\n'+body
assert all(x not in control for x in ['awk','python','perl','/proc/7718','force-stop','kill -KILL','kill -9'])
assert control.count('/system/bin/toybox kill -TERM 7722')==1
assert '/proc/7722/fd/3' in control and "owner_pair_verify \"$f\" \"$v\"" in control
(E/'owner3_control.sh').write_text(control,encoding='utf-8',newline='\n')
base=['S','7718']+['0']*17+['7571831']+['0']*3
stat='7722 (tee) '+' '.join(base)
q=shlex.quote
for name,text in [('uid-good','Name:\ttee\nUid:\t10221\t10221\t10221\t10221\n'),('uid-bad','Uid:\t10221\t2000\t10221\t10221\n'),('uid-missing','Name:\ttee\n'),('uid-duplicate','Uid:\t10221\t10221\t10221\t10221\n'*2)]: (E/(name+'.txt')).write_text(text,encoding='utf-8',newline='\n')
tests=[('good-stat',f'owner_stat_verify {q(stat)}',True),('wrong-pid',f'owner_stat_verify {q(stat.replace("7722 (","9999 ("))}',False),('wrong-comm',f'owner_stat_verify {q(stat.replace("(tee)","(other)"))}',False),('wrong-parent',f'owner_stat_verify {q(stat.replace("S 7718 ","S 1 "))}',False),('wrong-ticks',f'owner_stat_verify {q(stat.replace("7571831","7571832"))}',False),('short-stat',"owner_stat_verify '7722 (tee) S 7718'",False)]
for name,want in [('uid-good',True),('uid-bad',False),('uid-missing',False),('uid-duplicate',False)]:tests.append((name,'owner_uid_verify '+q((E/(name+'.txt')).as_posix()),want))
tests += [('same-dev-inode',"owner_pair_verify '74|123|10221' '74|123|10221'",True),('wrong-dev',"owner_pair_verify '75|123|10221' '74|123|10221'",False),('wrong-inode',"owner_pair_verify '74|124|10221' '74|123|10221'",False),('wrong-owner',"owner_pair_verify '74|123|2000' '74|123|2000'",False),('malformed-stat-pair',"owner_pair_verify '74|123' '74|123'",False)]
testscript='set -efu\n'+fields+'\n'
for name,cmd,want in tests:
 testscript+=f'if {cmd}; then actual=yes; else actual=no; fi; test "$actual" = '+('yes' if want else 'no')+f'; printf "LOCAL_ASSERT|{name}|PASS\\n"\n'
for name,s,expected in [('observe-same',stat,'STILL_VISIBLE'),('observe-zombie',stat.replace(') S ',') Z '),'ZOMBIE'),('observe-reused',stat.replace('7571831','7571832'),'REUSED'),('observe-malformed','7722 (tee) S','UNKNOWN')]:
 testscript+=f'owner_observe_fields {q(s)}; test "$OWNER_OBSERVATION" = {expected}; printf "LOCAL_ASSERT|{name}|PASS\\n"\n'
(E/'local_parse_check.sh').write_text(testscript,encoding='utf-8',newline='\n')
records=[]
for name,args in [('syntax',[SH,'-n',str(E/'owner3_control.sh')]),('synthetic-fields',[SH,str(E/'local_parse_check.sh')])]:
 p=subprocess.run(args,capture_output=True,timeout=15,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));(E/(name+'.stdout.txt')).write_bytes(p.stdout);(E/(name+'.stderr.txt')).write_bytes(p.stderr);records.append({'name':name,'argv':args,'exit':p.returncode,'stdoutBytes':len(p.stdout),'stderrBytes':len(p.stderr)});assert p.returncode==0
assert (E/'synthetic-fields.stdout.txt').read_text().count('LOCAL_ASSERT|')==19
summary={'at':datetime.datetime.now().astimezone().isoformat(),'status':'PASS','scope':'ONE_LOCAL_SYNTAX_AND_19_SYNTHETIC_FIELD_ASSERTIONS_NO_DEVICE','controlSha256':hashlib.sha256(control.encode()).hexdigest(),'fieldsSha256':hashlib.sha256(fields.encode()).hexdigest(),'records':records,'deviceCalls':0,'mediaReads':0,'termCalls':0,'externalDeviceCommands':['id','pwd','cat','toybox od','toybox tr','toybox readlink','toybox stat','toybox date','toybox sleep','toybox kill','toybox ps'],'remainingHarmlessCompatibilityGate':'one command before exact control; no parent proc or real content'}
(E/'local-review.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary))
