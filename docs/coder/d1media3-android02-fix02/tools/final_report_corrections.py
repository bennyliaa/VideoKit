from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
owner=json.loads((E/'typed-001/typed-owner.json').read_text());main=R/'docs/coder/D1_MEDIA3_ANDROID02_FIX02_DELIVERY_V1.0.md';s=main.read_text();s=s.replace('UTC04:23:42.681485前后详原owner至04:23:42.908277','UTC'+owner['startUtc'].split('T')[1].split('+')[0]+'至'+owner['endUtc'].split('T')[1].split('+')[0]);
if '官方文档网页只读核对' not in s:s=s.replace('公开API依据见','已另作官方文档网页只读核对，非构建/依赖下载联网；公开API依据见')
main.write_text(s,encoding='utf-8')
p=B/'tools/prepare_delivery.py';s=p.read_text().replace('UTC04:23:42.681485前后详原owner至04:23:42.908277','UTC04:23:42.426171至04:23:42.908277');p.write_text(s,encoding='utf-8')
typed={x['path']:x for x in json.loads((E/'typed-001/source-pins.json').read_text())};rows=[]
for rel in ['src/com/videokit/d1android/ScopeMeter.java','instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java']:
 data=(B/rel).read_text()
 if rel.endswith('ScopeMeter.java'):data=data.replace('root.put("inputLimit",inputLimit)','root.put("inputLimit",INPUT)').replace('root.put("outputLimit",outputLimit)','root.put("outputLimit",OUTPUT)')
 else:data=data.replace('.put("stage",stage).put("currentIOPhase",ioPhase).put("currentCasePartial"','.put("stage",stage).put("currentCasePartial"')
 candidates=[data.encode('utf-8'),data.replace('\n','\r\n').encode('utf-8')];matches=[raw for raw in candidates if hashlib.sha256(raw).hexdigest()==typed[rel]['sha256']];assert len(matches)==1
 p=E/'reconstructed-typed-sources'/rel;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(matches[0]);rows.append({'path':p.relative_to(B).as_posix(),'sha256':sha(p),'matchedActualCompilePin':True,'provenance':'RECONSTRUCTED by reversing exactly two declared display-field adjustments with LF/CRLF selected solely by original compile hash; not falsely claimed contemporaneous file copy.'})
(E/'reconstructed-typed-sources.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
identity={'path':main.relative_to(R).as_posix(),'bytes':main.stat().st_size,'sha256':sha(main)};(E/'main-report-identity.json').write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8');p=E/'delivery-summary.json';v=json.loads(p.read_text());v['mainReport']=identity;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'mainReport':identity,'reconstructedSourceFiles':len(rows)},ensure_ascii=False))
