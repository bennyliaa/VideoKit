"""Fixed-spec parameterization of the reviewed T6 receiver; cooperative mv-n plus independent inode/SHA."""
from dataclasses import dataclass
import re
import t6_protocol as p

BATCH=p.BATCH;NONCE=p.NONCE;TEMP_DIR=p.DIRECTORY;FIXTURES='files/e4_fixtures';MARGIN=67108864

@dataclass(frozen=True)
class Spec:
    alias:str
    source:str
    bytes:int
    sha256:str
    encodedBytes:int
    temp:str
    final:str
    transferSeconds:int
    hashSeconds:int
    def validate(self):
        if self.alias not in {'basic.mp4','subtitle.avi'} or self.temp!=TEMP_DIR+'/'+self.alias+'.part' or self.final!=FIXTURES+'/'+self.alias or type(self.bytes) is not int or self.bytes<=0 or self.encodedBytes!=4*((self.bytes+2)//3) or self.encodedBytes>1073741824 or not re.fullmatch('[0-9a-f]{64}',self.sha256) or not 0<self.transferSeconds<=600 or not 0<self.hashSeconds<=120:raise ValueError('FIXED_SPEC_ROLE')

def parent_guard():return f'test -d {FIXTURES}; test ! -L {FIXTURES}; test -r {FIXTURES}; test -w {FIXTURES}; test -x {FIXTURES}; '
def space_tail():return f'/system/bin/toybox df -k {FIXTURES}'
def admission_script(specs):
    return 'set -eu; '+p.context()+parent_guard()+p.absent(TEMP_DIR)+''.join(p.absent(s.final) for s in specs)+p.marker('ADMISSION',f'uid=%s|pwd=%s|parent={FIXTURES}')+' "$u" "$p"; '+space_tail()
def file_guard_script(s):
    s.validate()
    return 'set -eu; '+p.context()+parent_guard()+f'test -d {TEMP_DIR}; test ! -L {TEMP_DIR}; '+p.absent(s.temp)+p.absent(s.final)+p.marker('FILE_GUARD',f'uid=%s|pwd=%s|alias={s.alias}|temp={s.temp}|final={s.final}')+' "$u" "$p"; '+space_tail()
def receiver_script(s):
    s.validate()
    text=p.receiver_script().replace(p.TARGET,s.temp).replace('test "$n" = 256',f'test "$n" = {s.bytes}')
    return text.replace('umask 077; set -C;',parent_guard()+p.absent(s.final)+'umask 077; set -C;')
def proof_script(s,final=False):
    s.validate();path=s.final if final else s.temp
    text=p.proof_script().replace(p.TARGET,path).replace('test "$n" = 256',f'test "$n" = {s.bytes}').replace('head -c 256',f'head -c {s.bytes}')
    if final:text=text.replace('set -eu; ','set -eu; '+parent_guard()+f'test -d {TEMP_DIR}; test -r {TEMP_DIR}; test -x {TEMP_DIR}; '+p.absent(s.temp),1)
    return text
def stamp(value,expected_bytes=None,require_uid=True):
    if not re.fullmatch(r'\d+,\d+,\d+,\d+,[0-9a-fA-F]+,-?\d+',value):raise ValueError('STAT_FORMAT')
    dev,inode,n,uid,mode,mtime=value.split(',');mode=int(mode,16)
    if mode&0o170000!=0o100000 or mode&0o002 or (require_uid and uid!=str(p.UID)) or (expected_bytes is not None and n!=str(expected_bytes)):raise ValueError('FILE_ROLE_OR_COUNT')
    return dict(dev=dev,inode=inode,bytes=n,uid=uid,mode=mode,mtime=mtime)
def publish_script(s,expected_stamp):
    s.validate()
    # This builder formats an already admitted fingerprint; parse_proof is the production UID/mode gate.
    if not re.fullmatch(r'\d+,\d+,'+str(s.bytes)+r',\d+,[0-9a-fA-F]+,-?\d+',expected_stamp):raise ValueError('PUBLISH_FINGERPRINT')
    pieces=expected_stamp.split(',');identity=dict(dev=pieces[0],uid=pieces[3])
    return ('set -eu; '+p.context()+parent_guard()+f'test -d {TEMP_DIR}; test ! -L {TEMP_DIR}; test -r {TEMP_DIR}; test -w {TEMP_DIR}; test -x {TEMP_DIR}; '+
        f'test -f {s.temp}; test ! -L {s.temp}; '+p.absent(s.final)+
        f'a=$(/system/bin/toybox stat -c {p.STAT} -- {s.temp}); test "$a" = {expected_stamp}; '+
        f'd=$(/system/bin/toybox stat -c %d -- {FIXTURES}); test "$d" = {identity["dev"]}; '+
        f'o=$(/system/bin/toybox stat -c %u -- {FIXTURES}); test "$o" = {identity["uid"]}; '+
        f'if /system/bin/toybox mv -n -- {s.temp} {s.final}; then r=0; else r=$?; fi; '+
        p.marker('PUBLISH_ATTEMPT',f'alias={s.alias}|mvRc=%s')+' "$r"; test "$r" = 0; '+
        p.absent(s.temp)+f'test -f {s.final}; test ! -L {s.final}; b=$(/system/bin/toybox stat -c {p.STAT} -- {s.final}); test "$a" = "$b"; '+
        p.marker('PUBLISHED',f'uid=%s|pwd=%s|alias={s.alias}|temp={s.temp}|final={s.final}|tempAbsent=1|stamp=%s')+' "$u" "$p" "$b"')
def parse_space(raw,kind,expected,required_bytes):
    lines=raw.decode('ascii','strict').splitlines()
    if len(lines)<3 or p.parse_line(lines[0],kind)!=expected:raise ValueError('ORIGINAL_ADMISSION_CONTEXT')
    h=lines[1].split()
    if h[:5]!=['Filesystem','1K-blocks','Used','Available','Use%']:raise ValueError('DF_HEADER_FORMAT')
    fields=' '.join(lines[2:]).split()
    if len(fields)!=6 or any(not x.isdigit() for x in fields[1:4]) or not re.fullmatch(r'\d+%',fields[4]):raise ValueError('DF_ROW_FORMAT')
    need=(required_bytes+MARGIN+5+1023)//1024;available=int(fields[3])
    if available<need:raise ValueError('INSUFFICIENT_SPACE_NO_DELETE')
    return dict(availableKiB=available,requiredKiB=need,remainingRawBytes=required_bytes,marginBytes=MARGIN,history='Existing usage remains occupied; no historical deletion or duplicate free-space credit')
def parse_receiver(raw,s):
    r=p.receiver_observation(raw)
    if set(r)!={'BEGIN','DECODE','END'} or r['DECODE']!={'rc':'0'}:raise ValueError('ORIGINAL_DECODER_RETURN')
    pid=r['BEGIN'].get('pid','');expected=dict(uid=str(p.UID),pwd=p.PWD,pid=pid,path=s.temp)
    if not pid.isdigit() or int(pid)<1 or r['BEGIN']!=expected or r['END']!={**expected,'decoderRc':'0','statRc':'0','bytes':str(s.bytes)}:raise ValueError('RECEIVER_CONTEXT_OR_COUNT')
    return r
def parse_proof(raw,s,final=False,expected_stamp=None):
    r=p.one(raw,'PROOF');path=s.final if final else s.temp
    if set(r)!={'uid','pwd','path','bytes','sha','before','after'} or r['uid']!=str(p.UID) or r['pwd']!=p.PWD or r['path']!=path or r['bytes']!=str(s.bytes) or r['sha']!=s.sha256 or r['before']!=r['after']:raise ValueError('INDEPENDENT_RAW_PROOF')
    stamp(r['before'],s.bytes)
    if final and r['before']!=expected_stamp:raise ValueError('RENAME_IDENTITY_CHANGED')
    return r
def parse_publish(raw,s,expected_stamp):
    lines=raw.decode('ascii','strict').splitlines()
    if len(lines)!=2 or p.parse_line(lines[0],'PUBLISH_ATTEMPT')!={'alias':s.alias,'mvRc':'0'}:raise ValueError('ORIGINAL_MV_RETURN')
    r=p.parse_line(lines[1],'PUBLISHED')
    if r!=dict(uid=str(p.UID),pwd=p.PWD,alias=s.alias,temp=s.temp,final=s.final,tempAbsent='1',stamp=expected_stamp):raise ValueError('PUBLICATION_NOT_PROVEN')
    return r
