"""Default inspect. Explicit reproduction reads only the one authorized failed export, max53652 bytes."""
from pathlib import Path
import argparse,json,struct,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
P=R/'docs/tester/D1_E6_OUTPUT_EVIDENCE/failed-output-53651.mp4';SHA='20ad48067b3293aa9e6b8f3eacc7543e29edcda8ab19c15cbe438d55c995b6dd'
def analyze():
 output=B/'evidence/export-analysis-reproduction.json'
 if output.exists():raise RuntimeError('REPRODUCTION_ONCE_CONSUMED')
 with P.open('rb') as f:raw=f.read(53652)
 assert len(raw)==53651 and hashlib.sha256(raw).hexdigest()==SHA
 count=0;runs=[];timebase=[];tfdt=0
 def visit(start,end,depth=0):
  nonlocal count,tfdt
  assert depth<=8
  while start<end:
   assert end-start>=8;size,kind=struct.unpack_from('>I4s',raw,start);assert 8<=size<=end-start
   count+=1;assert count<=64;stop=start+size
   if kind in [b'moov',b'trak',b'mdia',b'minf',b'stbl',b'moof',b'traf',b'mvex']:visit(start+8,stop,depth+1)
   if kind==b'mdhd':assert raw[start+8]==0;timebase.append(struct.unpack_from('>I',raw,start+20)[0])
   if kind==b'tfdt':tfdt+=1
   if kind==b'trun':
    flags=int.from_bytes(raw[start+9:start+12],'big');assert flags==0x701
    n,offset=struct.unpack_from('>Ii',raw,start+12);assert n<=6 and size==20+12*n
    runs.append([struct.unpack_from('>III',raw,start+20+12*i)[0] for i in range(n)])
   start=stop
 visit(0,len(raw));assert timebase==[90000] and [len(r) for r in runs]==[5,1] and tfdt==0
 at=0;pts=[]
 for run in runs:
  for duration in run:pts.append(round(at*1000000/90000));at+=duration
 assert pts==[0,208333,416667,625000,833333,1041667]
 result=dict(status='PASS',exportBytes=len(raw),exportSha256=SHA,readBytes=len(raw),boxes=count,trunDurations=runs,timebase=90000,tfdtCount=0,inferredPtsUs=pts,expectedLastPtsUs=1000000,deviationUs=41667,mutation=False,scope='Container timestamp reproduction only; no decode/Android execution')
 with output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--analyze-once',action='store_true');a=p.parse_args()
 if a.analyze_once:analyze()
 else:print(json.dumps(dict(mode='INSPECT',authorizedExport=str(P),expectedBytes=53651,expectedSha256=SHA,reads=0,reproduction='Explicit --analyze-once only; not part of readonly freeze verification')))
