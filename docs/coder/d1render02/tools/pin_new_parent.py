from pathlib import Path
import xml.etree.ElementTree as E
import hashlib,json
B=Path(__file__).resolve().parents[1];P=B/'gradle/verification-metadata.xml';N='https://schema.gradle.org/dependency-verification';q=lambda s:'{'+N+'}'+s
E.register_namespace('',N);E.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance');t=E.parse(P);root=t.getroot()
root.find(q('configuration')+'/'+q('verify-metadata')).text='true'
components=root.find(q('components'));g='com.google.guava';n='guava-parent';v='33.3.1-android';file=n+'-'+v+'.pom'
c=next((x for x in components if x.get('group')==g and x.get('name')==n and x.get('version')==v),None)
if c is None:c=E.SubElement(components,q('component'),group=g,name=n,version=v)
assert not any(x.get('name')==file for x in c)
a=E.SubElement(c,q('artifact'),name=file);h='6e11986ea7250b51f847157e2dc937f32a306804dfce0007a5e81ddb9b95c579'
source=B/'evidence/guava-official-source'/file;assert hashlib.sha256(source.read_bytes()).hexdigest()==h
E.SubElement(a,q('sha256'),value=h,origin='NEW RENDER02 official fixed-version Maven Central evidence; independent admission PENDING')
E.indent(t,space='   ');t.write(P,encoding='UTF-8',xml_declaration=True)
(B/'evidence/new-metadata-pin.json').write_text(json.dumps({'coordinate':g+':'+n+':'+v,'artifact':file,'sha256':h,'sourceReceipt':'evidence/guava-official-source/source-receipt.json','classification':'NEW_EVIDENCE_NOT_HISTORICAL_APPROVAL','independentAdmission':'PENDING_TESTER_REVIEW','verifyMetadata':True,'binaryOrVersionChanges':0},indent=2),encoding='utf-8')
print('metadata=true; new fixed-version provenance pin recorded, independent review pending')
