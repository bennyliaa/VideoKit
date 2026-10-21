import pathlib,subprocess,json,datetime
R=pathlib.Path(__file__).resolve().parents[3];E=pathlib.Path(__file__).resolve().parent
ADB=r'D:\Android\SDK\platform-tools\adb.exe'
for label,serial in [('phone','U4999DLBNRR89DOR'),('tablet','HA1Q6WXR')]:
 O=E/label/'admitted-transport';O.mkdir(parents=True,exist_ok=False)
 commands=[('model',['shell','getprop','ro.product.model']),('api',['shell','getprop','ro.build.version.sdk']),('abi',['shell','getprop','ro.product.cpu.abilist']),('user',['shell','am','get-current-user']),('space',['shell','df','-k','/data']),('packages',['shell','pm','list','packages','-U','com.videokit']),('app-package',['shell','dumpsys','package','com.videokit.app']),('test-package',['shell','dumpsys','package','com.videokit.app.test']),('private-state',['shell','run-as','com.videokit.app','sh','-c','pwd; ls -lan files cache; for d in files/e4a_outputs files/e4a_output_budget files/e4_outputs files/e4_fixtures; do echo "$d"; ls -lan "$d"; done; if [ -f files/e4a_output_budget/identity.anchor ]; then cat files/e4a_output_budget/identity.anchor; fi'])]
 results=[]
 for name,args in commands:
  p=subprocess.run([ADB,'-s',serial]+args,capture_output=True,timeout=30)
  (O/(name+'.txt')).write_bytes(p.stdout+p.stderr)
  results.append({'name':name,'exit':p.returncode,'bytes':len(p.stdout)+len(p.stderr)})
  if p.returncode and name=='model':raise RuntimeError('TRANSPORT_UNAVAILABLE_STOP')
 (O/'preflight-commands.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 print(label,json.dumps(results),flush=True)
