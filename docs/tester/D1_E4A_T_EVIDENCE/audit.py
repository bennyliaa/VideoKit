"""Static frozen hash audit; no imports of transfer/fake runners and no subprocesses."""
from pathlib import Path
import hashlib,json,datetime,zipfile
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent;B=R/'docs/coder/d1e4at'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=B/'evidence/transfer-freeze.json';assert sha(p)=='3b650fd8f14956216e9fa5c9f43ebe916e5b832980a6e450515275e09425902a'
s=json.loads(p.read_text());rows=s['immutable']
for r in rows:
 p=R/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
assert sha(R/'docs/coder/d1e4a/evidence/e4a-freeze.json')=='a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d'
assert sha(R/'docs/tester/D1_E4A_N_DEVICE_TEST_REPORT_V1.0.md')=='37530ab70ade2b7bad5e5b144d3a9cab51b0a9986649c9172c996a237c7a250d'
manifest=json.loads((R/s['manifest']['path']).read_text());expected={r['path']:r for r in manifest['files']}
with zipfile.ZipFile(R/s['sourceZip']['path']) as z:
 assert len(z.namelist())==len(expected) and set(z.namelist())==set(expected)
 for name,r in expected.items():
  data=z.read(name);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
facts={'at':datetime.datetime.now().astimezone().isoformat(),'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'sourceZip':s['sourceZip'],'productAndPriorReportUnchanged':True,'scope':'STATIC_ONLY_NO_ADB_MEDIA_FAKE_OR_GRADLE','finding':{'id':'E4AT-F01','priority':'P1','file':'docs/coder/d1e4at/tools/exact_process.py','lines':[62,76,77,78,110,111,112,113,114,115,136],'condition':'stdin.close raises; stdin_closed=False, source_closed=True, writer_returned=True, exit_observed=True, drains returned, all original threads ended','actualStaticOutcome':'status NOT_ADMITTED but ownership RETURNED; _release_if_returned discards original Job from _OWNERS; subsequent _reserve allowed','expected':'UNKNOWN_RETAINED with original Job/process/stdin/source/parameters reachable; no next admission','evidenceKind':'STATIC_PREDICATE_AND_CALL_CHAIN_NOT_EXECUTED_FAULT'},'inFlight':[]}
(E/'identity-and-finding-audit.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'blockingFindings':1}))
