from pathlib import Path
import struct,zipfile,json,hashlib
E=Path(__file__).resolve().parent;B=Path('D:/CodexProjects/VideoKit/docs/coder/d1media3-android02')
def parse(b):
 assert b[:4]==b'\xca\xfe\xba\xbe';n=struct.unpack_from('>H',b,8)[0];cp=[None]*n;p=10;i=1
 while i<n:
  t=b[p];p+=1
  if t==1:l=struct.unpack_from('>H',b,p)[0];p+=2;cp[i]=('utf8',b[p:p+l].decode('utf8'));p+=l
  elif t==3:cp[i]=('int',struct.unpack_from('>i',b,p)[0]);p+=4
  elif t in [4]:cp[i]=('other',);p+=4
  elif t in [5,6]:cp[i]=('other',);p+=8;i+=1
  elif t in [7,8,16,19,20]:cp[i]=(t,struct.unpack_from('>H',b,p)[0]);p+=2
  elif t in [9,10,11,12,17,18]:cp[i]=(t,*struct.unpack_from('>HH',b,p));p+=4
  elif t==15:cp[i]=(t,b[p],struct.unpack_from('>H',b,p+1)[0]);p+=3
  else:raise AssertionError(t)
  i+=1
 def resolve(i):
  x=cp[i]
  if x[0] in ['utf8','int']:return x[1]
  if x[0] in [7,8]:return resolve(x[1])
  if x[0]==12:return str(resolve(x[1]))+str(resolve(x[2]))
  if x[0] in [9,10,11]:return str(resolve(x[1]))+'.'+str(resolve(x[2]))
  return str(x)
 p+=6;count=struct.unpack_from('>H',b,p)[0];p+=2+2*count;fields={};methods={}
 for kind in ['field','method']:
  count=struct.unpack_from('>H',b,p)[0];p+=2
  for _ in range(count):
   flags,name,desc,ac=struct.unpack_from('>HHHH',b,p);p+=8;key=resolve(name)+resolve(desc);attrs={}
   for __ in range(ac):
    ai,length=struct.unpack_from('>HI',b,p);p+=6;data=b[p:p+length];p+=length;attrs[resolve(ai)]=data
   if kind=='field' and 'ConstantValue' in attrs:fields[resolve(name)]=resolve(struct.unpack('>H',attrs['ConstantValue'])[0])
   if kind=='method' and 'Code' in attrs:
    data=attrs['Code'];length=struct.unpack_from('>I',data,4)[0];code=data[8:8+length];ins=[];pc=0
    while pc<len(code):
     op=code[pc];size=1
     if op in [0x10,0x12,0xa9,0xbc] or 0x15<=op<=0x19 or 0x36<=op<=0x3a:size=2
     elif op in [0x11,0x13,0x14,0x84,0xbb,0xbd,0xc0,0xc1,0xc6,0xc7] or 0x99<=op<=0xa8 or 0xb2<=op<=0xb8:size=3
     elif op in [0xb9,0xba,0xc8,0xc9]:size=5
     elif op==0xc5:size=4
     elif op==0xc4:size=6 if code[pc+1]==0x84 else 4
     elif op==0xaa:
      at=(pc+4)&~3;low,high=struct.unpack_from('>ii',code,at+4);size=at-pc+12+4*(high-low+1)
     elif op==0xab:
      at=(pc+4)&~3;pairs=struct.unpack_from('>i',code,at+4)[0];size=at-pc+8+8*pairs
     row=dict(pc=pc,opcode=hex(op),bytes=code[pc:pc+size].hex())
     if op==0x12:row['constantPoolValue']=resolve(code[pc+1])
     elif op in [0x13,0x14,0xbb,0xbd,0xc0,0xc1] or 0xb2<=op<=0xb9:row['constantPoolValue']=resolve(struct.unpack_from('>H',code,pc+1)[0])
     ins.append(row);pc+=size
    assert pc==len(code);methods[key]=dict(codeSha256=hashlib.sha256(code).hexdigest(),instructions=ins)
 return fields,methods
targets=[('media3-common.jar','androidx/media3/common/C.class'),('media3-extractor.jar','androidx/media3/extractor/mp4/TrackSampleTable.class'),('media3-extractor.jar','androidx/media3/extractor/mp4/Mp4Extractor.class')];out=[]
for jar,entry in targets:
 with zipfile.ZipFile(B/'deps'/jar) as z:b=z.read(entry)
 fields,methods=parse(b)
 selected={k:v for k,v in methods.items() if k.startswith('<init>') and 'TrackSampleTable' in entry or k.startswith('readSample(') and 'Mp4Extractor.class' in entry}
 out.append(dict(jar=jar,entry=entry,sha256=hashlib.sha256(b).hexdigest(),constants={k:v for k,v in fields.items() if 'BUFFER_FLAG' in k},methods=selected))
(E/'media3-extractor-flags-static-bytecode.json').write_text(json.dumps(dict(analysis='STATIC_JVM_CLASS_BYTES_ONLY_NO_LIBRARY_LOADING_OR_MEDIA_PARSER',classes=out),indent=2),encoding='utf8')
for x in out:
 print(x['entry'],x['constants'])
 for name,m in x['methods'].items():
  ins=m['instructions'];hits=[j for j,row in enumerate(ins) if row.get('constantPoolValue')==536870912 or 'flags[I' in str(row.get('constantPoolValue')) or 'sampleMetadata(' in str(row.get('constantPoolValue'))]
  for j in hits:print(name,ins[max(0,j-4):j+5])
