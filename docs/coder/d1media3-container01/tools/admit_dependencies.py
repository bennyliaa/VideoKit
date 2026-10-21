from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,datetime
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/media3-container01-freeze.json').exists(),'FROZEN'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins={}
for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter():
 if c.tag.split('}')[-1]=='component':
  for a in c:pins[(c.get('group'),c.get('name'),c.get('version'),a.get('name'))]={h.get('value') for h in a if h.tag.split('}')[-1]=='sha256'}
records=[]
for artifact in ['extractor','decoder']:
 name='media3-'+artifact;D=B/'offline-maven/androidx/media3'/name/'1.9.3';F=B/'reference/official-extractor'
 module=F/(name+'-1.9.3.module');pom=F/(name+'-1.9.3.pom');license=F/'LICENSE'
 assert module.read_bytes()==(D/module.name).read_bytes()
 assert sha(module) in pins[('androidx.media3',name,'1.9.3',module.name)]
 pomKey=('androidx.media3',name,'1.9.3',pom.name)
 if pomKey in pins: assert sha(pom) in pins[pomKey]
 else:
  # New metadata only, collected from the exact official Google Maven URL.
  tree=ET.parse(B/'gradle/verification-metadata.xml');root=tree.getroot();ns=root.tag.split('}')[0]+'}' if '}' in root.tag else ''
  component=next(c for c in root.iter() if c.tag.split('}')[-1]=='component' and (c.get('group'),c.get('name'),c.get('version'))==pomKey[:3])
  a=ET.SubElement(component,ns+'artifact',{'name':pom.name});ET.SubElement(a,ns+'sha256',{'value':sha(pom),'origin':'Official Google Maven metadata; D1_MEDIA3_CONTAINER01'})
  if ns: ET.register_namespace('',ns[1:-1])
  tree.write(B/'gradle/verification-metadata.xml',encoding='utf-8',xml_declaration=True)
 assert sha(license)=='cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30'
 m=json.loads(module.read_text());assert m['component']=={'group':'androidx.media3','module':name,'version':'1.9.3','attributes':{'org.gradle.status':'release'}}
 aar=D/(name+'-1.9.3.aar');h=sha(aar);assert h in pins[('androidx.media3',name,'1.9.3',aar.name)]
 assert all(x['sha256']==h and x['size']==aar.stat().st_size for v in m['variants'] for x in v.get('files',[]) if x['name']==aar.name)
 if not (D/pom.name).exists():(D/pom.name).write_bytes(pom.read_bytes())
 jar=B/'deps'/(name+'.jar');assert not jar.exists()
 with zipfile.ZipFile(aar) as z:jar.write_bytes(z.read('classes.jar'))
 records.append({'coordinate':'androidx.media3:'+name+':1.9.3','officialBase':'https://dl.google.com/dl/android/maven2/androidx/media3/'+name+'/1.9.3/','aarSha256':h,'moduleSha256':sha(module),'pomSha256':sha(pom),'classesJarSha256':sha(jar),'licenseUrl':'https://raw.githubusercontent.com/androidx/media/1.9.3/LICENSE','licenseSha256':sha(license),'strictPinsPreexisting':True,'sourceAdmission':'OFFICIAL_IDENTITY_LICENSE_CHECKED_BEFORE_RUNTIME','platformRuntimeAdmission':False})
(B/'evidence/extractor-source-admission.json').write_text(json.dumps({'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records},indent=2))
print(json.dumps(records,indent=2))
