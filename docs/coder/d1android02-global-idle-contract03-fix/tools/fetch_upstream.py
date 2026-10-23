"""Read only fixed-tag AOSP material; never imports or executes fetched text."""
from pathlib import Path
import urllib.request,json,hashlib,base64
B=Path(__file__).resolve().parents[1];R=B/'reference/upstream';R.mkdir(parents=True,exist_ok=True)
requests=[
 ('base-app-tree','frameworks/base','core/java/android/app/','JSON'),
 ('native-binder-tree','frameworks/native','libs/binder/','JSON'),
 ('native-header','frameworks/native','libs/binder/include_activitymanager/binder/ActivityManager.h','TEXT'),
 ('permission-tree','packages/modules/Permission','','JSON'),
 ('permission-role','packages/modules/Permission','service/java/com/android/server/role/RoleShellCommand.java','TEXT'),
 ('permission-role-manager','packages/modules/Permission','service/java/com/android/server/role/RoleManagerShellCommand.java','TEXT'),
 ('base-role-tree','frameworks/base','services/core/java/com/android/server/role/','JSON'),
 ('base-enum','frameworks/base','core/java/android/app/ProcessStateEnum.aidl','TEXT')]
rows=[]
for name,repo,path,fmt in requests:
 url=f'https://android.googlesource.com/platform/{repo}/+/android-12.0.0_r1/{path}?format={fmt}'
 try:
  with urllib.request.urlopen(url,timeout=15) as f:data=f.read(1048577)
  if len(data)>1048576:raise ValueError('READ_BOUND')
  if fmt=='TEXT':
   content=base64.b64decode(data,validate=False);file=R/(name+'.txt');file.write_bytes(content)
   row=dict(name=name,url=url,status=200,bytes=len(content),sha256=hashlib.sha256(content).hexdigest())
  else:
   file=R/(name+'.json');file.write_bytes(data);j=json.loads(data.decode().removeprefix(")]}'\n"));row=dict(name=name,url=url,status=200,id=j.get('id'),entries=[x['name'] for x in j.get('entries',[])])
 except Exception as e:row=dict(name=name,url=url,error=str(e))
 rows.append(row)
(R/'fetch-round01.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows))
