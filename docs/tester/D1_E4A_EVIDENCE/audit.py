"""Tester read-only frozen-file identity and finite source comparison; no runtime tests."""
from pathlib import Path
import hashlib,json,datetime
R=Path(__file__).resolve().parents[3]
E=Path(__file__).resolve().parent
B=R/'docs/coder/d1e4a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=B/'evidence/e4a-freeze.json'
assert sha(seal)=='a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d'
s=json.loads(seal.read_text(encoding='utf-8-sig'))
rows=s['immutableFiles']
for row in rows:
 p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
der=json.loads((B/'evidence/e4-derivation-map.json').read_text(encoding='utf-8-sig'))
unchanged=[];changed=[]
for row in der['files']:
 old=R/row['source'];new=R/row['destination']
 assert sha(old)==row['sourceSha256'] and sha(new)==row['sha256']
 (unchanged if old.read_bytes()==new.read_bytes() else changed).append(row['destination'])
old=R/'docs/coder/d1e4/evidence/e4-freeze.json'
assert sha(old)=='0940855c58ada5c2ce3b23e8bd4c63803016afeb4b563127f589a043847e0227'
c14=R/'docs/coder/d1c14/evidence/freeze-summary.json'
if c14.exists():assert sha(c14)=='880b38f3896df2f6bed2657d54c7fb8a954d3d05d8c730faf1b11278726e7155'
facts={'at':datetime.datetime.now().astimezone().isoformat(),'scope':'STATIC_READ_ONLY_NO_RUNTIME_TESTS','freezeSha256':sha(seal),'immutableFiles':len(rows),'allImmutableHashes':'PASS','sourceZip':s['sourceZip'],'byteIdenticalDerivatives':unchanged,'changedDerivatives':changed,'apks':s['facts']['apks'],'oldE4FreezeUnchanged':True,'oldC14FreezeChecked':c14.exists(),'inFlight':[]}
(E/'identity-audit.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'integrity':'PASS','immutableFiles':len(rows),'unchangedDerivatives':len(unchanged),'changedDerivatives':len(changed),'runtimeTests':0}))
