from pathlib import Path
import urllib.request,urllib.error,json,hashlib,datetime,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parents[1];D=B/'evidence/official-added-dependencies';D.mkdir(exist_ok=False)
items=[('androidx.media3','media3-datasource','1.9.3'),('androidx.media3','media3-database','1.9.3'),('androidx.exifinterface','exifinterface','1.3.6')];rows=[]
for g,a,v in items:
 for extension in ['pom','module']:
  name=f'{a}-{v}.{extension}';url='https://dl.google.com/dl/android/maven2/'+g.replace('.','/')+'/'+a+'/'+v+'/'+name
  try:
   with urllib.request.urlopen(url,timeout=30) as r:
    data=r.read(131073);assert len(data)<=131072;record={'requestedUrl':url,'finalUrl':r.url,'status':r.status,'headers':dict(r.headers),'retrievedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
   (D/name).write_bytes(data)
   if extension=='module':
    original=B/'offline-maven'/g.replace('.','/')/a/v/name;assert original.read_bytes()==data;record['matchesExistingVerificationPinnedModule']=True
    artifact=next(x for variant in json.loads(data)['variants'] for x in variant.get('files',[]) if x['name']==f'{a}-{v}.aar');aar=original.parent/artifact['name'];assert hashlib.sha256(aar.read_bytes()).hexdigest()==artifact['sha256'];record['officialModuleAarHashMatchesExistingPinnedBinary']=True
   else:
    ns={'m':'http://maven.apache.org/POM/4.0.0'};root=ET.fromstring(data);record['licenses']=[{'name':x.findtext('m:name',namespaces=ns),'url':x.findtext('m:url',namespaces=ns)} for x in root.findall('m:licenses/m:license',ns)]
   rows.append(record)
  except Exception as error:
   rows.append({'requestedUrl':url,'retrievedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FAILED','exceptionType':type(error).__name__});(D/'receipt.json').write_text(json.dumps({'records':rows,'result':'BLOCKED_SOURCE_VERIFICATION','binaryDownloads':0},indent=2),encoding='utf-8');raise
(D/'receipt.json').write_text(json.dumps({'result':'OFFICIAL_FIXED_METADATA_MATCHES_EXISTING_PINS_PENDING_INDEPENDENT_REVIEW','records':rows,'binaryDownloads':0,'newVersionDownloads':0,'metadataAddedToBuildMirror':False,'purpose':'Exact required datasource/database/exif official identity and license difference; no POM checks disabled'},ensure_ascii=False,indent=2),encoding='utf-8')
print('OFFICIAL_FIXED_POM_MODULE_METADATA_COMPLETE; binaries downloaded=0')
