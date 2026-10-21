from pathlib import Path
import hashlib,json,re,shutil,xml.etree.ElementTree as ET,collections
B=Path(__file__).resolve().parents[1];E=B/'evidence';D=E/'actual-consumption';D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pins={};oldpins={}
for path,dest in [(B/'gradle/verification-metadata.xml',pins),(B.parent/'d1render01/gradle/verification-metadata.xml',oldpins)]:
 root=ET.parse(path).getroot()
 for c in root.iter():
  if c.tag.split('}')[-1]!='component':continue
  for a in c:
   values={x.get('value') for x in a if x.tag.split('}')[-1]=='sha256'}
   dest[(c.get('group'),c.get('name'),c.get('version'),a.get('name'))]=values
seen={};operations=E/'build-main-005/consumption.jsonl'
for line in operations.read_text(encoding='utf-8').splitlines():
 row=json.loads(line)
 if row['name']!='Dependency verification':continue
 m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',row['progressName']);assert m,row
 artifact,g,a,v=m.groups();key=(g,a,v,artifact);p=B/'offline-maven'/g.replace('.','/')/a/v/artifact;assert p.is_file(),key
 h=sha(p);assert h in pins[key],key
 kind='module' if artifact.endswith('.module') else 'pom' if artifact.endswith('.pom') else 'binary'
 record={'coordinate':f'{g}:{a}:{v}','artifact':artifact,'kind':kind,'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':h,'pinClass':'HISTORICAL_RENDER01_PIN' if h in oldpins.get(key,set()) else 'NEW_PENDING_INDEPENDENT_REVIEW','verificationEventId':row['id']}
 if kind!='binary':
  target=D/'metadata'/g.replace('.','/')/a/v/artifact;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);record['reviewCopy']=target.relative_to(B).as_posix()
 seen[key]=record
records=sorted(seen.values(),key=lambda x:(x['coordinate'],x['artifact']));assert records
metadata=[x for x in records if x['kind']!='binary'];edges=[];ns={'m':'http://maven.apache.org/POM/4.0.0'}
for r in metadata:
 if r['kind']!='pom':continue
 root=ET.parse(B/r['path']).getroot();props={c.tag.split('}')[-1]:c.text for c in root.findall('m:properties/*',ns)}
 def val(e,n):
  t=e.findtext('m:'+n,default='',namespaces=ns).strip()
  for k,v in props.items():t=t.replace('${'+k+'}',v or '')
  return t
 parent=root.find('m:parent',ns)
 if parent is not None:edges.append({'from':r['coordinate'],'relation':'parent','declaredTarget':':'.join(val(parent,n) for n in ['groupId','artifactId','version'])})
 for dep in root.findall('m:dependencyManagement/m:dependencies/m:dependency',ns):
  if val(dep,'type')=='pom' and val(dep,'scope')=='import':edges.append({'from':r['coordinate'],'relation':'importBOM','declaredTarget':':'.join(val(dep,n) for n in ['groupId','artifactId','version'])})
actualCoords={r['coordinate'] for r in metadata}
for x in edges:x['targetObservedInVerification']=x['declaredTarget'] in actualCoords
dump(D/'artifacts.json',records);dump(D/'parent-bom-declarations.json',edges)
summary={'result':'PASS_ACTUAL_STRICT_VERIFICATION_EVENT_INVENTORY','buildAttempt':'005','buildExitCode':json.loads((E/'build-main-005/receipt.json').read_text(encoding='utf-8-sig'))['exitCode'],'operationLogSha256':sha(operations),'counts':dict(collections.Counter(x['kind'] for x in records)),'actualArtifacts':len(records),'actualMetadata':len(metadata),'declaredParentOrBOMEdges':len(edges),'observedPluginMarkers':[r['coordinate'] for r in metadata if '.gradle.plugin' in r['coordinate']],'actualGuavaNewParentConsumed':any(r['coordinate']=='com.google.guava:guava-parent:33.3.1-android' for r in metadata),'newPinAdmission':'PENDING_INDEPENDENT_REVIEW; official source and separate strict parent probe','unusedFoojayConsumed':any('foojay' in r['coordinate'] for r in records),'binaryOrVersionDownloads':0,'method':'Gradle 9.5 actual Dependency verification operation progress names; successful strict build. POM declarations are separately labelled, not assumed consumed; module-first resolution can omit POM parents.','verificationMode':'strict','verifyMetadata':True}
assert summary['buildExitCode']==0 and not summary['unusedFoojayConsumed'];dump(D/'summary.json',summary);print(json.dumps(summary,indent=2))
