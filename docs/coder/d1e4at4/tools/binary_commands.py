"""Fixed app-specific staging and bounded file-to-file copy. Shell stdin never carries payload."""
import re
import shlex

BATCH='D1-E4A-T4P-TABLET-20261017'
NONCE='E4T4P_TABLET_20261017_ONCE'
SERIAL='HA1Q6WXR'
PACKAGE='com.videokit.app'
UID=10221
PWD='/data/user/0/com.videokit.app'
EXT='/storage/emulated/0/Android/data/com.videokit.app/files'
STAGE=EXT+'/e4_stage_T4P_TABLET_20261017_once'
SOURCE=STAGE+'/payload256.bin'
DIRECTORY='files/e4_diag_T4P_TABLET_20261017_once'
TARGET=DIRECTORY+'/payload256.bin'
EMPTY='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
SHA='40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880'
STAT='%d,%i,%s,%u,%f,%Y'

def argv(adb,script,app=True):
    prefix=['run-as',PACKAGE] if app else []
    return [str(adb),'-s',SERIAL,'shell','-n','-T','-e','none',*prefix,'sh','-c',shlex.quote(script)]

def context(app=True):
    return f'u=$(id -u); test "$u" = {UID if app else 2000}; '+(f'p=$(pwd); test "$p" = {PWD}; test -d files; test ! -L files; ' if app else '')

def role(path,directory=True):
    return f'test -{"d" if directory else "f"} {path}; test ! -L {path}; '

def absent(path):return f'test ! -e {path}; test ! -L {path}; '
def stamp(path):return f'/system/bin/toybox stat -c {STAT} -- {path}'
def line(kind,fields):return f'printf "T4_{kind}|{NONCE}|{fields}\\n"'

def base_script(app):
    fields=f'uid=%s|base={EXT}|stamp=%s'+(f'|pwd=%s' if app else '')
    args=' "$u" "$m"'+(' "$p"' if app else '')
    # Existing framework-provided app-specific base required; never mkdir its parents or change permissions.
    return ('set -eu; '+context(app)+role(EXT)+f'test -r {EXT}; test -w {EXT}; test -x {EXT}; '+absent(STAGE)+
            (absent(DIRECTORY) if app else '')+
            f'm=$({stamp(EXT)}); h=$(/system/bin/toybox head -c 0 -- /dev/null | /system/bin/toybox sha256sum); h=${{h%% *}}; test "$h" = {EMPTY}; '+
            '(set -C); '+line('APP_BASE' if app else 'SHELL_BASE',fields)+args)

def processes_script():
    return 'set -eu; '+context()+line('PS','self=%s')+' "$$"; '+f'/system/bin/toybox ps -u {UID} -o PID,PPID,UID,ARGS'

def create_stage_script():
    return ('set -eu; '+context(False)+role(EXT)+absent(STAGE)+f'umask 077; mkdir {STAGE}; '+role(STAGE)+
            f'm=$({stamp(STAGE)}); '+line('STAGE_CREATED',f'uid=%s|path={STAGE}|stamp=%s')+' "$u" "$m"')

def stage_access_script(app):
    return ('set -eu; '+context(app)+role(EXT)+role(STAGE)+f'test -r {STAGE}; test -w {STAGE}; test -x {STAGE}; '+absent(SOURCE)+
            line('APP_STAGE' if app else 'SHELL_STAGE',f'uid=%s|path={STAGE}')+' "$u"')

def proof_script(stage):
    path=SOURCE if stage else TARGET
    return ('set -eu; '+context()+role(EXT if stage else 'files')+role(STAGE if stage else DIRECTORY)+role(path,False)+
            f'a=$({stamp(path)}); n=$(/system/bin/toybox stat -c %s -- {path}); test "$n" = 256; '+
            f'h=$(/system/bin/toybox head -c 256 -- {path} | /system/bin/toybox sha256sum); h=${{h%% *}}; '+
            f'b=$({stamp(path)}); test "$a" = "$b"; '+line('STAGE_PROOF' if stage else 'INTERNAL_PROOF',f'uid=%s|pwd=%s|path={path}|before=%s|after=%s|sha=%s')+' "$u" "$p" "$a" "$b" "$h"')

def copy_script(expected_stamp):
    parse_stamp(expected_stamp,True)
    return ('set -eu; '+context()+role(EXT)+role(STAGE)+role(SOURCE,False)+
            f'a=$({stamp(SOURCE)}); test "$a" = {shlex.quote(expected_stamp)}; '+absent(DIRECTORY)+
            line('COPY_BEGIN',f'uid=%s|pwd=%s|pid=%s|source={SOURCE}|target={TARGET}')+' "$u" "$p" "$$"; '+
            f'umask 077; mkdir {DIRECTORY}; '+role(DIRECTORY)+absent(TARGET)+
            f'set -C; /system/bin/toybox head -c 256 -- {SOURCE} > {TARGET}; '+
            f'b=$({stamp(SOURCE)}); test "$a" = "$b"; n=$(/system/bin/toybox stat -c %s -- {TARGET}); test "$n" = 256; '+
            line('COPY_END',f'uid=%s|pwd=%s|pid=%s|source={SOURCE}|target={TARGET}|bytes=%s')+' "$u" "$p" "$$" "$n"')

def marker(raw,kind):
    lines=raw.decode('ascii','strict').splitlines()
    if len(lines)!=1:raise ValueError('ONE_EXACT_MARKER_REQUIRED')
    fields=lines[0].split('|')
    if fields[:2]!=['T4_'+kind,NONCE]:raise ValueError('MARKER_IDENTITY')
    result={}
    for field in fields[2:]:
        key,sep,value=field.partition('=')
        if not sep or key in result:raise ValueError('MARKER_FIELDS')
        result[key]=value
    return result

def parse_stamp(value,file=True,internal=False):
    if not re.fullmatch(r'\d+,\d+,\d+,\d+,[0-9a-fA-F]+,-?\d+',value):raise ValueError('STAT_FORMAT')
    dev,inode,size,uid,mode,mtime=value.split(',');mode=int(mode,16)
    if (mode&0o170000)!=(0o100000 if file else 0o040000) or mode&0o002:raise ValueError('FILE_ROLE_OR_WORLD_WRITABLE')
    if file and size!='256':raise ValueError('FILE_LENGTH')
    if internal and uid!=str(UID):raise ValueError('INTERNAL_OWNER')
    return dict(dev=dev,inode=inode,size=size,uid=uid,mode=mode,mtime=mtime)

def parse_base(raw,app):
    r=marker(raw,'APP_BASE' if app else 'SHELL_BASE');m=r.pop('stamp');parse_stamp(m,False)
    if r!=dict(uid=str(UID if app else 2000),base=EXT,**({'pwd':PWD} if app else {})):raise ValueError('BASE_CONTEXT')
    return dict(**r,stamp=m)

def parse_stage(raw,created=False,app=False):
    kind='STAGE_CREATED' if created else ('APP_STAGE' if app else 'SHELL_STAGE');r=marker(raw,kind)
    if created:parse_stamp(r.pop('stamp'),False)
    if r!=dict(uid=str(UID if app else 2000),path=STAGE):raise ValueError('STAGE_CONTEXT')
    return r

def parse_proof(raw,stage):
    r=marker(raw,'STAGE_PROOF' if stage else 'INTERNAL_PROOF')
    if set(r)!={'uid','pwd','path','before','after','sha'} or r['uid']!=str(UID) or r['pwd']!=PWD or r['path']!=(SOURCE if stage else TARGET) or r['sha']!=SHA or r['before']!=r['after']:raise ValueError('INDEPENDENT_PROOF')
    parse_stamp(r['before'],True,not stage);return r

def parse_copy(raw):
    lines=raw.splitlines()
    if len(lines)!=2:raise ValueError('COPY_END_NOT_OBSERVED')
    a=marker(lines[0],'COPY_BEGIN');b=marker(lines[1],'COPY_END')
    expected=dict(uid=str(UID),pwd=PWD,source=SOURCE,target=TARGET)
    pid=a.pop('pid','')
    if not pid.isdigit() or int(pid)<1 or b.pop('pid',None)!=pid or b.pop('bytes',None)!='256' or a!=expected or b!=expected:raise ValueError('COPY_CONTEXT_OR_COUNT')
    return dict(pid=pid,bytes=256,source=SOURCE,target=TARGET)

def check_processes(raw):
    lines=raw.decode('ascii','strict').splitlines()
    r=marker(lines[0].encode(),'PS');pid=r.get('self','')
    if set(r)!={'self'} or not pid.isdigit() or len(lines)<2 or lines[1].split()!=['PID','PPID','UID','ARGS']:raise ValueError('UID_SNAPSHOT_FORMAT')
    for line_value in lines[2:]:
        f=line_value.split(None,3)
        if len(f)!=4 or any(not x.isdigit() for x in f[:3]) or f[2]!=str(UID):raise ValueError('UID_SNAPSHOT_ROW')
        head=f[3].split()[0].rsplit('/',1)[-1]
        if f[0]!=pid and (head in {'cat','tee','sh','mksh','head','cp','dd'} or any(t in f[3] for t in ['E4AT1P','exec cat','tee files/e4_fixtures'])):raise ValueError('POSSIBLE_PRIOR_RECEIVER_NO_KILL')
    return 'ONE_UID_SNAPSHOT_NOT_ALL_RESOURCE_RETURN'
