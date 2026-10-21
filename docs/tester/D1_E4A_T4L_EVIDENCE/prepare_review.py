from pathlib import Path
import hashlib,json,subprocess,re
E=Path(__file__).resolve().parent
assert not (E/'local-review.json').exists()
base='/storage/emulated/0/Android/data/com.videokit.app/files'
stage=base+'/e4_stage_T4P_TABLET_20261017_once'
download='/storage/emulated/0/Download'
rows=[]
for app in (False,True):
    text='''# Fixed read-only T4L checklist; subfailures preserved, no set-e.
step() { label=$1; shift; printf 'STEP_BEGIN|%s\\n' "$label"; "$@"; rc=$?; printf 'STEP_END|%s|rc=%s\\n' "$label" "$rc"; }
u=$(id -u); urc=$?; p=$(pwd); prc=$?; printf 'IDENTITY|uid=%s|idrc=%s|pwd=%s|pwdrc=%s\\n' "$u" "$urc" "$p" "$prc"
'''
    uid='10221' if app else '2000'
    text+=f'step uid test "$u" = {uid}\n'
    text+=f'if [ "$urc" != 0 ] || [ "$u" != {uid} ]; then printf "CONTEXT_REJECT\\n"; exit 0; fi\n'
    if app:
        text+='step pwd test "$p" = /data/user/0/com.videokit.app\nif [ "$prc" != 0 ] || [ "$p" != /data/user/0/com.videokit.app ]; then printf "CONTEXT_REJECT\\n"; exit 0; fi\n'
    for label,path in [('base',base),('stage',stage),('download',download)]+([('files','files'),('internal','files/e4_diag_T4P_TABLET_20261017_once')] if app else []):
        for flag in ('e','d','L','r','w','x'):
            text+=f'step {label}.{flag} test -{flag} {path}\n'
        if label in ('stage','internal'):
            text+=f'step {label}.absent_e test ! -e {path}\nstep {label}.absent_L test ! -L {path}\n'
        text+=f'step {label}.stat /system/bin/toybox stat -c %d,%i,%s,%u,%f,%Y -- {path}\n'
    text+='step tool.head0 /system/bin/toybox head -c 0 -- /dev/null\n'
    text+='printf "STEP_BEGIN|tool.sha_empty\\n"; h=$(printf "" | /system/bin/toybox sha256sum); rc=$?; printf "%s\\n" "$h"; printf "STEP_END|tool.sha_empty|rc=%s\\n" "$rc"; h=${h%% *}\n'
    text+='step tool.sha_expected test "$h" = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\n'
    text+='printf "STEP_BEGIN|tool.setC\\n"; (set -C); rc=$?; printf "STEP_END|tool.setC|rc=%s\\n" "$rc"\n'
    text+=f'step download.df /system/bin/toybox df -k {download}\nprintf "CHECKLIST_END\\n"\n'
    # Whitelist shell interfaces, no path expansion, content readers only head0 /dev/null.
    assert all(t not in text for t in ('mkdir','chmod','chown','rm ','mv ','cp ','tee ','kill ','/proc/','>>',' > ','awk','python','perl','set -e;'))
    assert text.count('head -c 0 -- /dev/null')==1 and 'head -c 256' not in text
    name=('app' if app else 'shell')+'-checklist.sh';p=E/name;p.write_bytes(text.encode())
    r=subprocess.run([r'C:\Program Files\Git\usr\bin\sh.exe','-n',str(p)],capture_output=True,timeout=15,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    assert r.returncode==0,(r.stdout,r.stderr)
    rows.append(dict(file=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),syntaxExit=r.returncode,syntaxStdoutHex=r.stdout.hex(),syntaxStderrHex=r.stderr.hex(),stepCount=text.count('step ')-1+2))
out=dict(status='PASS',scope='ONE_CONSOLIDATED_LOCAL_SYNTAX_NO_WRITE_COMPATIBILITY_REVIEW',scripts=rows,interfaces='id/pwd/test/printf/functions/if/parameter expansion/subshell/set-C; toybox stat/head0/sha256sum previously observed; df -k is read-only candidate with original errors preserved, device support not assumed',deviceCalls=0,fileContentReadBytes=0,fileWritesOnDevice=0,deviceCallsPlanned=2,metadataCap=6)
(E/'local-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
