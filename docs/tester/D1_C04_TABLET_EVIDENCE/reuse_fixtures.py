import hashlib,json,pathlib,subprocess
BASE=pathlib.Path(__file__).resolve().parent
ADB=r'D:\Android\SDK\platform-tools\adb.exe'
def run(args):
 p=subprocess.run([ADB,'-s','HA1Q6WXR','shell','run-as','com.videokit.app']+args,capture_output=True,timeout=180)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 return p.stdout.decode().strip()
records=json.loads((BASE.parent/'D1_TABLET_C03_EVIDENCE/fixture-hash-check.json').read_text())
print(records[0],flush=True)
for r in records:
 alias=r.get('alias',r.get('name'))
 expected=r.get('sourceSha256',r.get('expectedSha256',r.get('sha256')))
 # Exact source records use source/remote fields; retain their expected digest.
 if expected is None: expected=r['sourceHash']
 old='files/d1_c03_fixtures/'+alias
 actual=run(['sha256sum',old]).split()[0];assert actual==expected
 print('C03_SOURCE_VERIFIED '+alias,flush=True)
run(['mkdir','files/d1_c04_fixtures'])
verified=[]
for r in records:
 alias=r.get('alias',r.get('name'));old='files/d1_c03_fixtures/'+alias;new='files/d1_c04_fixtures/'+alias
 expected=run(['sha256sum',old]).split()[0]
 run(['cp',old,new]);actual=run(['sha256sum',new]).split()[0];assert actual==expected
 size=int(run(['stat','-c','%s',new]))
 verified.append(dict(alias=alias,bytes=size,sourcePrivatePath=old,destinationPrivatePath=new,sha256=actual,hashMatch=True))
 print('C04_COPY_VERIFIED '+alias,flush=True)
(BASE/'fixture-hash-check.json').write_text(json.dumps(verified,indent=2),encoding='utf-8')
