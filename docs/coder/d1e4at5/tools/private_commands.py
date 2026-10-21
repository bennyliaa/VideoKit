"""Fixed private-only diagnostic and decoder probe with separate original pipeline endpoint returns."""
import hashlib
import re
import shlex

BATCH='D1-E4A-T5P-TABLET-20261017';NONCE='E4T5P_TABLET_20261017_ONCE';SERIAL='HA1Q6WXR'
UID=10221;PWD='/data/user/0/com.videokit.app';PACKAGE='com.videokit.app'
DIRECTORY='files/e4_diag_T5P_TABLET_20261017_once';TARGET=DIRECTORY+'/payload256.bin'
SHA=hashlib.sha256(bytes(range(256))).hexdigest();STAT='%d,%i,%s,%u,%f,%Y'

def argv(adb,script,stdin=False):
    return [str(adb),'-s',SERIAL,'shell',* ([] if stdin else ['-n']),'-T','-e','none','run-as',PACKAGE,'sh','-c',shlex.quote(script)]
def context():return f'u=$(id -u); p=$(pwd); test "$u" = {UID}; test "$p" = {PWD}; test -d files; test ! -L files; '
def absent(path):return f'test ! -e {path}; test ! -L {path}; '
def marker(kind,fields):return f'printf "T5_{kind}|{NONCE}|{fields}\\n"'
def context_script():return 'set -eu; '+context()+absent(DIRECTORY)+marker('CONTEXT','uid=%s|pwd=%s')+' "$u" "$p"'

def decoder_probe_script():
    # FD3 bypasses command substitution so original endpoint rc markers never contaminate the one-byte decode.
    return ('set -eu; '+context()+'set +e; exec 3>&1; '+
        'o=$( { printf AA==; r=$?; '+marker('PROBE_RC','stage=printf|rc=%s')+' "$r" >&3; exit "$r"; } | '+
        '{ /system/bin/toybox base64 -d; r=$?; '+marker('PROBE_RC','stage=decoder|rc=%s')+' "$r" >&3; exit "$r"; } | '+
        '{ /system/bin/toybox od -An -tx1; r=$?; '+marker('PROBE_RC','stage=od|rc=%s')+' "$r" >&3; exit "$r"; } ); '+
        'r=$?; exec 3>&-; f=$?; '+marker('PROBE','uid=%s|pwd=%s|pipelineRc=%s|fd3CloseRc=%s|hex=%s')+' "$u" "$p" "$r" "$f" "$o"')

def processes_script():return 'set -eu; '+context()+marker('PS','self=%s')+' "$$"; '+f'/system/bin/toybox ps -u {UID} -o PID,PPID,UID,ARGS'
def mkdir_script():return 'set -eu; '+context()+absent(DIRECTORY)+f'umask 077; mkdir {DIRECTORY}; test -d {DIRECTORY}; test ! -L {DIRECTORY}; '+marker('DIRECTORY',f'path={DIRECTORY}')
def receiver_script():
    return ('set -eu; '+context()+f'test -d {DIRECTORY}; test ! -L {DIRECTORY}; '+absent(TARGET)+
        marker('BEGIN',f'uid=%s|pwd=%s|pid=%s|path={TARGET}')+' "$u" "$p" "$$"; umask 077; set -C; '+
        f'if /system/bin/toybox base64 -d > {TARGET}; then d=0; else d=$?; fi; '+marker('DECODE','rc=%s')+' "$d"; '+
        'if test "$d" != 0; then exit "$d"; fi; '+
        f'if n=$(/system/bin/toybox stat -c %s -- {TARGET}); then s=0; else s=$?; fi; '+
        marker('END',f'uid=%s|pwd=%s|pid=%s|path={TARGET}|decoderRc=%s|statRc=%s|bytes=%s')+' "$u" "$p" "$$" "$d" "$s" "$n"; test "$s" = 0; test "$n" = 256')
def proof_script():
    return ('set -eu; '+context()+f'test -d {DIRECTORY}; test ! -L {DIRECTORY}; test -f {TARGET}; test ! -L {TARGET}; '+
        f'a=$(/system/bin/toybox stat -c {STAT} -- {TARGET}); n=$(/system/bin/toybox stat -c %s -- {TARGET}); test "$n" = 256; '+
        f'h=$(/system/bin/toybox head -c 256 -- {TARGET} | /system/bin/toybox sha256sum); h=${{h%% *}}; b=$(/system/bin/toybox stat -c {STAT} -- {TARGET}); test "$a" = "$b"; '+
        marker('PROOF',f'uid=%s|pwd=%s|path={TARGET}|bytes=%s|sha=%s|before=%s|after=%s')+' "$u" "$p" "$n" "$h" "$a" "$b"')

def parse_line(line,kind):
    f=line.split('|')
    if f[:2]!=['T5_'+kind,NONCE]:raise ValueError('MARKER_IDENTITY')
    out={}
    for field in f[2:]:
        k,s,v=field.partition('=')
        if not s or k in out:raise ValueError('MARKER_FIELD')
        out[k]=v
    return out
def one(raw,kind):
    lines=raw.decode('ascii','strict').splitlines()
    if len(lines)!=1:raise ValueError('ONE_MARKER')
    return parse_line(lines[0],kind)
def parse_probe(raw):
    lines=raw.decode('ascii','strict').splitlines();stages={};proof=None
    if len(lines)!=4:raise ValueError('PROBE_ENDPOINTS_MISSING')
    for line in lines:
        if line.startswith('T5_PROBE_RC|'):
            r=parse_line(line,'PROBE_RC')
            if set(r)!={'stage','rc'} or r['stage'] in stages:raise ValueError('PROBE_DUPLICATE')
            stages[r['stage']]=r['rc']
        else:
            if proof is not None:raise ValueError('PROBE_DUPLICATE_RESULT')
            proof=parse_line(line,'PROBE')
    if stages!={'printf':'0','decoder':'0','od':'0'} or proof is None or set(proof)!={'uid','pwd','pipelineRc','fd3CloseRc','hex'} or proof['uid']!=str(UID) or proof['pwd']!=PWD or proof['pipelineRc']!='0' or proof['fd3CloseRc']!='0' or proof['hex'].strip()!='00':raise ValueError('DECODER_ONE_BYTE_COMPATIBILITY_REFUSED')
    return dict(originalEndpointRc=stages,proof=proof)
def receiver_observation(raw):
    out={}
    for line in raw.decode('ascii','strict').splitlines():
        kind=line.split('|',1)[0].removeprefix('T5_')
        if kind not in {'BEGIN','DECODE','END'} or kind in out:raise ValueError('RECEIVER_MARKER_SHAPE')
        out[kind]=parse_line(line,kind)
    return out
def parse_receiver(raw):
    r=receiver_observation(raw)
    if set(r)!={'BEGIN','DECODE','END'} or r['DECODE']!={'rc':'0'}:raise ValueError('ORIGINAL_DECODER_RETURN_MISSING_OR_NONZERO')
    begin=r['BEGIN'];end=r['END'];pid=begin.get('pid','')
    expected=dict(uid=str(UID),pwd=PWD,pid=pid,path=TARGET)
    if not pid.isdigit() or int(pid)<1 or begin!=expected or end!={**expected,'decoderRc':'0','statRc':'0','bytes':'256'}:raise ValueError('RECEIVER_CONTEXT_OR_COUNT')
    return r
def parse_proof(raw):
    r=one(raw,'PROOF')
    if set(r)!={'uid','pwd','path','bytes','sha','before','after'} or r['uid']!=str(UID) or r['pwd']!=PWD or r['path']!=TARGET or r['bytes']!='256' or r['sha']!=SHA or r['before']!=r['after']:raise ValueError('INDEPENDENT_PROOF')
    if not re.fullmatch(r'\d+,\d+,256,10221,[0-9a-fA-F]+,-?\d+',r['before']):raise ValueError('ORIGINAL_STAT')
    mode=int(r['before'].split(',')[4],16)
    if mode&0o170000!=0o100000 or mode&0o002:raise ValueError('INTERNAL_FILE_ROLE')
    return r
def check_processes(raw):
    lines=raw.decode('ascii','strict').splitlines();r=parse_line(lines[0],'PS');pid=r.get('self','')
    if set(r)!={'self'} or not pid.isdigit() or len(lines)<2 or lines[1].split()!=['PID','PPID','UID','ARGS']:raise ValueError('UID_PS_FORMAT')
    for line in lines[2:]:
        f=line.split(None,3)
        if len(f)!=4 or any(not x.isdigit() for x in f[:3]) or f[2]!=str(UID):raise ValueError('UID_PS_ROW')
        head=f[3].split()[0].rsplit('/',1)[-1]
        if f[0]!=pid and (head in {'cat','tee','sh','mksh','head','cp','dd','base64'} or any(t in f[3] for t in ['E4AT1P','exec cat','tee files/e4_fixtures'])):raise ValueError('POSSIBLE_PRIOR_RECEIVER_NO_SIGNAL')
    return 'ONE_UID_SNAPSHOT_NOT_ALL_RESOURCE_RETURN'
