"""Add only artifact checksums already frozen and independently reviewed in E13F SBOM."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
R=Path('D:/CodexProjects/VideoKit').resolve();B=R/'docs/coder/d1render01'
baseline=R/'docs/coder/d1e13f/evidence/apk-delivery-final/sbom.json'
prior=json.loads((R/'docs/coder/d1-exit-readiness/evidence-index.json').read_text(encoding='utf-8'))['SBOM']
assert hashlib.sha256(baseline.read_bytes()).hexdigest()==prior['sha256']
N='https://schema.gradle.org/dependency-verification';q=lambda n:'{'+N+'}'+n
ET.register_namespace('',N);ET.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance')
p=B/'gradle/verification-metadata.xml';tree=ET.parse(p);root=tree.getroot();components=root.find(q('components'));added=[]
cache=Path('C:/Users/benny/.gradle/caches/modules-2/files-2.1')
for c in json.loads(baseline.read_text(encoding='utf-8-sig'))['components']:
    group,name,version=c.get('group'),c.get('name'),c.get('version')
    if not group:continue
    evidence=next((x['value'] for x in c.get('properties',[]) if x['name']=='cachedArtifactEvidence'),None)
    if evidence is None:continue
    for a in json.loads(evidence):
        source=cache/a['cacheRelative'];assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest()==a['sha256']
        component=next((x for x in components if x.get('group')==group and x.get('name')==name and x.get('version')==version),None)
        if component is None:component=ET.SubElement(components,q('component'),group=group,name=name,version=version)
        artifact=next((x for x in component if x.get('name')==a['name']),None)
        if artifact is None:artifact=ET.SubElement(component,q('artifact'),name=a['name'])
        values={x.get('value') for x in artifact.findall(q('sha256'))}
        if not values:
            ET.SubElement(artifact,q('sha256'),value=a['sha256'],origin='Frozen independently reviewed E13F SBOM; cached bytes rechecked')
            added.append({'coordinate':group+':'+name+':'+version,'artifact':a['name'],'sha256':a['sha256']})
        else:assert a['sha256'] in values
ET.indent(tree,space='   ');tree.write(p,encoding='UTF-8',xml_declaration=True)
out=B/'evidence/runtime-pin-merge.json';assert not out.exists();out.write_text(json.dumps({'baseline':prior,'added_existing_reviewed_artifact_hashes':added,'version_changes':0,'binary_downloads':0},indent=2),encoding='utf-8')
print(json.dumps({'added_existing_reviewed_hashes':len(added),'version_changes':0}))
