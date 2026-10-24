"""Declared legal wire bytes, using the frozen independent B construction."""
def legal_raw(fc,target_bytes=None,packages=2):
 role='ROLE STATE (dumpsys role):\n{\n user_states={\n user_id=0\n version=1\n packages_hash=FIXTURE_HASH\n roles={\n name=android.app.role.HOME\n holders=com.zui.launcher\n }\n }\n}\n'
 system=['package:com.zui.launcher uid:10012']+['package:com.fixture.p'+str(i).zfill(3)+'x'*40+' uid:'+str(10100+i) for i in range(packages-1)]
 values=['TB138FC\n','31\n','SYNTHETIC_FIXTURE_FIRMWARE_API31\n','0\n','\n'.join(system)+'\n',role,'com.zui.launcher/.Launcher\n']
 def wire(v):
  raw=b'GI_FACTS_V1\n'
  for (name,_),value in zip(fc.QUERIES,v):
   b=value.encode();raw+=('GI_ITEM|'+name+'|0|1000|1000|'+str(len(b))+'\n').encode()+b+b'\n'
  return raw+b'GI_FACTS_END\n'
 if target_bytes is not None:
  pad=target_bytes-len(wire(values))
  if pad<0:raise ValueError('FIXTURE_TARGET_TOO_SMALL')
  for _ in range(8):
   values[5]=role.replace('\n{','\n'+' '*pad+'{',1);n=len(wire(values));pad+=target_bytes-n
   if n==target_bytes:break
 raw=wire(values)
 if target_bytes is not None:assert len(raw)==target_bytes
 assert all(len(x.encode())<=131072 for x in values)
 parsed=fc.facts(raw);assert len(parsed['systemPackages'])==packages and len(raw)<=139264
 return raw
