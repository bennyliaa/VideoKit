"""Mode-specific ADB argument adapter and a fixed 256-byte, separately authorized diagnostic."""
from dataclasses import dataclass
import re
import shlex

PACKAGE='com.videokit.app'
HISTORY=(
 'files/e4_fixtures/basic.mp4',
 'files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep',
 'files/e4_fixtures/.basic.E4AT1P_TABLET_20261017_once.part',
)
@dataclass(frozen=True)
class Context:
    uid:int=10221
    pwd:str='/data/user/0/com.videokit.app'
    directory:str='files/e4_diag_T2P_TABLET_20261017_once'
    nonce:str='E4T2P_TABLET_20261017_ONCE'
    @property
    def target(self):return self.directory+'/payload256.bin'
    def validate(self):
        if type(self.uid) is not int or self.uid<1 or '\n' in self.pwd or '|' in self.pwd:raise ValueError('CONTEXT_ROLE')
        if not re.fullmatch(r'files/e4_diag_[A-Za-z0-9_]{8,80}',self.directory) or not re.fullmatch('[A-Za-z0-9_]{8,80}',self.nonce):raise ValueError('FIXED_NEW_DIAGNOSTIC_SCOPE')

def run_as_argv(adb,serial,mode,script):
    if serial!='HA1Q6WXR' or mode not in {'shell','exec-in','exec-out'}:raise ValueError('ONE_TABLET_AND_KNOWN_MODE_ONLY')
    # shell joins raw argv; legacy exec escapes subsequent argv itself. Never prequote the latter.
    argument=shlex.quote(script) if mode=='shell' else script
    flags=['-T','-e','none'] if mode=='shell' else []
    return [str(adb),'-s',serial,mode,*flags,'run-as',PACKAGE,'sh','-c',argument]

def adb_escape(value):return "'"+value.replace("'","'\\''")+"'"

def model_service(argv):
    """Independent source-backed client string construction model; not execution of installed ADB."""
    mode=argv[3];args=argv[4:]
    if mode=='shell':
        if args[:3]==['-T','-e','none']:args=args[3:]
        return ' '.join(args)
    if mode in {'exec-in','exec-out'}:return args[0]+''.join(' '+adb_escape(arg) for arg in args[1:])
    raise ValueError('MODEL_MODE')

def identity(c):
    c.validate()
    return f'u=$(id -u); p=$(pwd); test "$u" = {c.uid}; test "$p" = {shlex.quote(c.pwd)}; test -d files; test ! -L files'

def preflight_script(c):
    return f'set -eu; u=$(id -u); p=$(pwd); printf "E4T2_CONTEXT|{c.nonce}|uid=%s|pwd=%s\\n" "$u" "$p"; test "$u" = {c.uid}; test "$p" = {shlex.quote(c.pwd)}; test -d files; test ! -L files'

def process_script(c):
    return f'set -eu; {identity(c)}; printf "E4T2_PS|{c.nonce}|self=%s\\n" "$$"; /system/bin/toybox ps -u {c.uid} -o PID,PPID,UID,ARGS'

def history_script(c):
    pieces=[f'set -eu; {identity(c)}']
    for path in HISTORY:
        p=shlex.quote(path)
        # No -L: leaf metadata only. No media content open/hash, no globs or recursive listing.
        pieces.append(f'if m=$(/system/bin/toybox stat -c "%u|%s|%i|%f|%Y" -- {p} 2>&1); then printf "E4T2_LSTAT|{path}|rc=0|%s\\n" "$m"; else r=$?; printf "E4T2_LSTAT|{path}|rc=%s|%s\\n" "$r" "$m"; fi')
    return '; '.join(pieces)

def mkdir_script(c):
    d=shlex.quote(c.directory)
    return f'set -eu; {identity(c)}; test ! -e {d}; test ! -L {d}; umask 077; mkdir {d}; printf "E4T2_DIRECTORY|{c.nonce}|path={c.directory}\\n"'

def receiver_script(c):
    c.validate();d=shlex.quote(c.directory);t=shlex.quote(c.target)
    return (f'set -eu; u=$(id -u); p=$(pwd); '
        f'printf "E4T2_BEGIN|{c.nonce}|uid=%s|pid=%s|pwd=%s|path={c.target}\\n" "$u" "$$" "$p"; '
        f'test "$u" = {c.uid}; test "$p" = {shlex.quote(c.pwd)}; test -d files; test ! -L files; '
        f'test -d {d}; test ! -L {d}; test ! -e {t}; test ! -L {t}; umask 077; set -C; '
        f'cat > {t}; n=$(/system/bin/toybox stat -c %s -- {t}); test "$n" = 256; '
        f'printf "E4T2_END|{c.nonce}|uid=%s|pid=%s|pwd=%s|path={c.target}|bytes=%s\\n" "$u" "$$" "$p" "$n"')

def independent_script(c):
    t=shlex.quote(c.target)
    return (f'set -eu; {identity(c)}; test -f {t}; test ! -L {t}; n=$(/system/bin/toybox stat -c %s -- {t}); '
        f'test "$n" = 256; h=$(/system/bin/toybox sha256sum -- {t}); h=${{h%% *}}; '
        f'printf "E4T2_PROOF|{c.nonce}|uid=%s|pwd=%s|path={c.target}|bytes=%s|sha=%s\\n" "$u" "$p" "$n" "$h"')

def parse_line(line,kind,c):
    fields=line.split('|')
    if len(fields)<3 or fields[:2]!=[kind,c.nonce]:raise ValueError('REMOTE_MARKER_MISSING_OR_WRONG')
    result={}
    for field in fields[2:]:
        key,sep,value=field.partition('=')
        if not sep or key in result:raise ValueError('REMOTE_MARKER_FIELDS')
        result[key]=value
    return result

def parse_receiver(raw,c):
    lines=raw.decode('utf-8','strict').splitlines()
    if len(lines)!=2:raise ValueError('REMOTE_EXECUTION_NOT_FULLY_OBSERVED')
    begin=parse_line(lines[0],'E4T2_BEGIN',c);end=parse_line(lines[1],'E4T2_END',c)
    if set(begin)!={'uid','pid','pwd','path'} or set(end)!={'uid','pid','pwd','path','bytes'}:raise ValueError('REMOTE_MARKER_SHAPE')
    for proof in [begin,end]:
        if proof['uid']!=str(c.uid) or proof['pwd']!=c.pwd or proof['path']!=c.target or not proof['pid'].isdigit() or int(proof['pid'])<1:raise ValueError('REMOTE_ACTUAL_CONTEXT_MISMATCH')
    if begin['pid']!=end['pid'] or end['bytes']!='256':raise ValueError('REMOTE_RECEIVER_COUNT_OR_INSTANCE')
    return dict(begin=begin,end=end,source='original receiver stdout, not host submittedBytes')

def parse_independent(raw,c,expected_sha):
    lines=raw.decode('utf-8','strict').splitlines()
    if len(lines)!=1:raise ValueError('INDEPENDENT_PROOF_SHAPE')
    proof=parse_line(lines[0],'E4T2_PROOF',c)
    if set(proof)!={'uid','pwd','path','bytes','sha'} or proof!={'uid':str(c.uid),'pwd':c.pwd,'path':c.target,'bytes':'256','sha':expected_sha}:raise ValueError('INDEPENDENT_CONTEXT_LENGTH_OR_SHA_MISMATCH')
    return proof
