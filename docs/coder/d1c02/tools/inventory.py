"""Read-only local evidence; never uploads or writes into test_media."""
import hashlib, json, struct, sys, re
from pathlib import Path
from PIL import Image

root = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2]).resolve()
media = root / 'test_media'
claims = {}
for manifest in media.rglob('*MANIFEST.json'):
    payload = json.loads(manifest.read_text(encoding='utf-8-sig'))
    for entry in payload['files']:
        claims[(manifest.parent / entry['file']).resolve()] = {'entry': entry, 'source': payload.get('source')}
for manifest in media.rglob('video_manifest.json'):
    payload = json.loads(manifest.read_text(encoding='utf-8-sig'))
    for entry in payload['files']:
        claims[(manifest.parent / entry['file']).resolve()] = {'entry': entry, 'source': {k:v for k,v in payload.items() if k!='files'}}

def signature(b):
    if b.startswith(b'\xff\xd8\xff'): return 'JPEG'
    if b.startswith(b'\x89PNG\r\n\x1a\n'): return 'PNG'
    if b.startswith((b'GIF87a',b'GIF89a')): return 'GIF'
    if b.startswith(b'BM'): return 'BMP'
    if b[:4]==b'RIFF': return b[8:12].decode('ascii',errors='replace').strip()
    if b[:4]==b'\x1aE\xdf\xa3': return 'EBML (Matroska/WebM candidate)'
    if b[4:8]==b'ftyp': return 'ISO-BMFF brand='+b[8:12].decode('ascii',errors='replace')
    if len(b)>384 and all(b[x]==0x47 for x in (0,188,376)): return 'MPEG-TS 188-byte signature'
    if len(b)>388 and all(b[x]==0x47 for x in (4,196,388)): return 'M2TS 192-byte signature'
    return 'EMPTY' if not b else 'UNRECOGNIZED'

def mp4_tracks(path):
    # Locate moov by top-level box sizes; skip mdat without downloading/decoding it.
    with path.open('rb') as f:
        size=path.stat().st_size; pos=0; moov=None
        while pos+8<=size:
            f.seek(pos); header=f.read(16); n,kind=struct.unpack('>I4s',header[:8]); head=8
            if n==1: n=struct.unpack('>Q',header[8:16])[0];head=16
            if n==0:n=size-pos
            if n<head or pos+n>size: raise ValueError('invalid top-level box')
            if kind==b'moov':
                if n>16*1024*1024:raise ValueError('moov exceeds probe budget')
                f.seek(pos+head);moov=f.read(n-head);break
            pos+=n
        if moov is None:raise ValueError('moov absent')
    def boxes(b):
        at=0
        while at+8<=len(b):
            n,k=struct.unpack('>I4s',b[at:at+8])
            if n<8 or at+n>len(b):break
            yield k,b[at+8:at+n];at+=n
    tracks=[]
    for k,trak in boxes(moov):
        if k!=b'trak':continue
        row={}
        def walk(b):
            for kind,body in boxes(b):
                if kind in (b'mdia',b'minf',b'stbl'):walk(body)
                elif kind==b'hdlr' and len(body)>=12 and 'handler' not in row:row['handler']=body[8:12].decode('ascii',errors='replace')
                elif kind==b'stsd' and len(body)>=16:row['sample_entry']=body[12:16].decode('ascii',errors='replace')
                elif kind==b'mdhd' and len(body)>=24:
                    if body[0]==0:scale,dur=struct.unpack('>II',body[12:20])
                    elif body[0]==1 and len(body)>=32:scale=struct.unpack('>I',body[20:24])[0];dur=struct.unpack('>Q',body[24:32])[0]
                    else:continue
                    row['duration_seconds']=dur/scale if scale else None
        walk(trak);tracks.append(row)
    return tracks

def ebml_tracks(path):
    with path.open('rb') as f:b=f.read(2*1024*1024)
    def vint(at,keep=False):
        first=b[at];length=1
        while length<=8 and not(first & (1<<(8-length))):length+=1
        if length>8 or at+length>len(b):raise ValueError('invalid EBML vint')
        value=int.from_bytes(b[at:at+length],'big')
        return value if keep else value & ((1<<(7*length))-1),length
    def children(start,end):
        while start<end:
            identifier,n=vint(start,True);size,m=vint(start+n);body=start+n+m;stop=body+size
            if stop>end:raise ValueError('truncated EBML metadata')
            yield identifier,body,stop;start=stop
    at=-1
    while True:
        at=b.find(b'\x16\x54\xae\x6b',at+1)
        if at<0:raise ValueError('Tracks not in bounded prefix')
        size,n=vint(at+4);start=at+4+n
        if start+size<=len(b):
            try:
                if any(key==0xae for key,_,_ in children(start,start+size)):break
            except (ValueError,IndexError):pass
    tracks=[]
    for identifier,body,stop in children(start,start+size):
        if identifier!=0xae:continue
        row={}
        for key,a,z in children(body,stop):
            val=b[a:z]
            if key==0x83:row['type']={1:'video',2:'audio',17:'subtitle'}.get(int.from_bytes(val,'big'),'other')
            if key==0x86:row['codec_id']=val.decode('ascii',errors='replace')
            if key==0x22b59c:row['language']=val.decode('ascii',errors='replace')
            if key==0xe0:
                for k,x,y in children(a,z):
                    if k in (0xb0,0xba):row['width' if k==0xb0 else 'height']=int.from_bytes(b[x:y],'big')
        tracks.append(row)
    return tracks

def avi_tracks(path):
    with path.open('rb') as f:b=f.read(1024*1024)
    def chunks(start,end):
        while start+8<=end:
            kind=b[start:start+4];size=int.from_bytes(b[start+4:start+8],'little');body=start+8;stop=body+size
            if stop>end:break
            yield kind,body,stop;start=stop+(size&1)
    tracks=[];metadata={}
    def walk(start,end):
        for kind,a,z in chunks(start,end):
            if kind==b'LIST' and b[a:a+4]==b'strl':
                row={}
                for k,x,y in chunks(a+4,z):
                    body=b[x:y]
                    if k==b'strh' and len(body)>=36:
                        row['type']=body[:4].decode('ascii',errors='replace');row['handler']=body[4:8].decode('ascii',errors='replace')
                        scale,rate,_,length=struct.unpack('<IIII',body[20:36]);row['duration_seconds']=length*scale/rate if rate else None
                    if k==b'strf' and row.get('type')=='vids' and len(body)>=20:
                        row['width'],row['height']=struct.unpack('<ii',body[4:12]);row['compression']=body[16:20].decode('ascii',errors='replace')
                    if k==b'strf' and row.get('type')=='auds' and len(body)>=16:
                        tag,ch,rate=struct.unpack('<HHI',body[:8]);row.update(wave_format_tag=hex(tag),channels=ch,sample_rate=rate)
                tracks.append(row)
            elif kind==b'LIST' and b[a:a+4] in (b'hdrl',b'odml'):walk(a+4,z)
            elif kind==b'avih' and z-a>=40:
                usec,_,_,_,frames=struct.unpack('<IIIII',b[a:a+20]);metadata['duration_seconds']=usec*frames/1e6
    # Read only the header LIST; never descend into movi frame payloads.
    walk(12,len(b));return {'tracks':tracks,'metadata':metadata}

def srt_probe(path):
    raw=path.read_bytes();encoding=None
    for candidate in ('utf-8-sig','gb18030'):
        try:text=raw.decode(candidate);encoding=candidate;break
        except UnicodeDecodeError:pass
    if encoding is None:raise ValueError('unsupported text encoding')
    intervals=[];invalid=0
    for block in re.split(r'\r?\n\s*\r?\n',text.strip()):
        match=re.search(r'(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})',block)
        if not match:invalid+=1;continue
        values=list(map(int,match.groups()))
        if any(values[i]>59 for i in (1,2,5,6)):invalid+=1;continue
        times=[((values[i]*60+values[i+1])*60+values[i+2])*1000+values[i+3] for i in (0,4)]
        if times[1]<times[0]:invalid+=1
        intervals.append(times)
    out_of_order=sum(intervals[i][0]<intervals[i-1][0] for i in range(1,len(intervals)))
    overlaps=sum(intervals[i][0]<intervals[i-1][1] for i in range(1,len(intervals)))
    matches=[p.name for p in path.parent.glob('*.avi') if path.name.startswith(p.stem+'.')]
    return {'encoding_strict_decode':encoding,'cue_count':len(intervals),'invalid_blocks':invalid,'out_of_order_starts':out_of_order,'overlapping_adjacent_cues':overlaps,'first_start_ms':min((x[0] for x in intervals),default=None),'last_end_ms':max((x[1] for x in intervals),default=None),'same_basename_video_candidates':matches,'playback_render_and_sync':'NOT_RUN; parsing timestamps does not establish dialogue synchronization'}

rows=[]
for path in sorted(media.rglob('*')):
    if not path.is_file():continue
    h=hashlib.sha256()
    with path.open('rb') as f:
        head=f.read(1024);h.update(head)
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    row={'relative_path':str(path.relative_to(media)).replace('\\','/'),'bytes':path.stat().st_size,'sha256':h.hexdigest(),'signature':signature(head)}
    claim=claims.get(path.resolve())
    if claim:
        row['provided_manifest_claim']=claim
        entry=claim['entry'];row['manifest_hash_match']=entry['sha256']==row['sha256'];row['manifest_length_match']=entry['bytes']==row['bytes']
    else:row['provenance']='User-provided for local testing; original rights/creator not established'
    if path.suffix.lower() in ('.jpg','.jpeg','.png','.bmp','.gif','.webp','.avif','.heic','.heif'):
        try:
            with Image.open(path) as im:
                row['image_probe']={'format':im.format,'size':list(im.size),'frames':getattr(im,'n_frames',1),'mode':im.mode,'exif_orientation':im.getexif().get(274)}
                for frame in range(getattr(im,'n_frames',1)):im.seek(frame);im.load()
                row['local_decode']='PASS (desktop Pillow only)'
        except Exception as e:row['local_decode']='NOT_RUN/UNSUPPORTED_OR_INVALID: '+type(e).__name__
    if head[4:8]==b'ftyp' and path.suffix.lower() in ('.mp4','.mov','.m4v'):
        try:row['local_track_probe']=mp4_tracks(path);row['probe_scope']='ISO-BMFF metadata only; no decoder validation'
        except Exception as e:row['local_track_probe_error']=str(e)
    if head[:4]==b'\x1aE\xdf\xa3':
        try:row['local_track_probe']=ebml_tracks(path);row['probe_scope']='EBML Tracks in bounded 2MiB prefix; no decoder validation'
        except Exception as e:row['local_track_probe_error']=str(e)
    if head[:4]==b'RIFF' and head[8:12]==b'AVI ':
        try:row['local_track_probe']=avi_tracks(path);row['probe_scope']='bounded AVI header only; no video/audio decoder validation'
        except Exception as e:row['local_track_probe_error']=str(e)
    if path.suffix.lower()=='.srt':
        try:row['subtitle_probe']=srt_probe(path)
        except Exception as e:row['subtitle_probe_error']=str(e)
    row['android_decode']='NOT_RUN'
    rows.append(row)
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps({'scope':'local read-only inventory, no ffmpeg integration','files':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print('files',len(rows),'manifest_matches',sum(r.get('manifest_hash_match',False) for r in rows),'mismatches',[r['relative_path'] for r in rows if r.get('manifest_hash_match') is False])
