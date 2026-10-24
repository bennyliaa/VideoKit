from pathlib import Path
import hashlib,json,zipfile,ast
R=Path(__file__).resolve().parent;P=R.parent;report=P/'D1_FACTS_V2_QUALIFICATION07_PHASE_A_REPORT_V1.0.md'
cases=[
('S01','patch命中0次或非预期多次在资源前拒绝；单空格/双空格/CRLF差异不静默通过'),
('S02','AST按权威分类所有费用修改：统一收费或准确既有票据/seed；裸child计数不能遗漏事件'),
('S03','每行scope/index/path/kind/amount/owner/阶段准确，合计次数字节与事件长度一致；不能只比总额'),
('S04','RAW/COMPLETE/LIVE各建完整图，route_fixture及win32_route子自身显式读取各预留一次'),
('S05','entry raw采用、父raw、子raw分别记账；子预留不是实际子read/close返回'),
('S06','64与65读、256MiB边界及+1，USED/claim/Popen前总准入；读前拒绝不额外开源文件'),
('S07','runtime16预留和seed携入一次；actual/close/fixedHelperReturned分开，不补写未证返回'),
('S08','LIVE known/unknown native量、source_reserved_unknown准确记录，未知保留不退款不补绿'),
('S09','原Gate/Runner SourceBudget ticket及PS delta同scope/版本/权威并回，保持原caps不双收费'),
('S10','最终实际事件分块和summary可靠落盘；拒绝/失败原exit/输出先保留，不拿计划冒实测'),
('P01','最终31/23或其正式新集合、Runner SOURCE_FILES/PS srcKeys/policy/所有具名消费点闭包一致'),
('P02','GICollector/GIFactPlan及GIV2Adapter/Capture/Origin取最终生产者bytes；过期pin资源前拒绝'),
('P03','V1与V2共同Expanded02路径都验collector pin；两条合法链与错误来源负例独立验收'),
('P04','qualification_reference与实际内联副本及容量合并值同步，不能只验独立参考文件'),
('P05','不盲替换SDK/ABI/产品/历史proof摘要，修改依赖后重算gate/seal/policy并再核闭包'),
('B01','正式B绑定最终07新根/API/参数/枚举/预算后验原receipt同fileId、控制容量、生产正负链'),
('B02','18辅助及当前V1必要回归按准确理由/布尔/原输出验收，不执行无意义全组合'),
('B03','前置已知拒绝/真实original进入后未知准确分层，不据空PID释放，不查改旧对象')]
(R/'oracle.json').write_text(json.dumps({'status':'PLANNED_NOT_RUN','priorPreparation':'05 independent driver A and prior planned cases remain frozen, not executed','cases':[{'id':i,'criterion':s,'status':'PLANNED_NOT_RUN'} for i,s in cases]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda b:hashlib.sha256(b).hexdigest()
zpath=P.parent/'coder/d1android02-facts-v2-qualification06/QUALIFICATION06-frozen.zip'
assert sha(zpath.read_bytes())=='250c98231da3df0ae87e9f99f733e030a15de6d25c0ec8adf4a3531e3e4e4fd5'
with zipfile.ZipFile(zpath) as z:
 for f in (R/'sealed-code').rglob('*'):
  if f.is_file():assert f.read_bytes()==z.read(f.relative_to(R/'sealed-code').as_posix())
for f in R.rglob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
rows=[]
for f in sorted([report]+[f for f in R.rglob('*') if f.is_file() and f.name not in ('manifest.json','freeze.json','send-receipt.json')]):
 b=f.read_bytes();rows.append({'path':f.relative_to(P).as_posix(),'bytes':len(b),'sha256':sha(b)})
m={'scope':'QUALIFICATION07_PHASE_A_STATIC_ONLY','files':rows,'count':len(rows),'bytes':sum(x['bytes'] for x in rows),'exclusions':['manifest.json','freeze.json','send-receipt.json'],'productCalls':0}
(R/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bad=[x['path'] for x in rows if sha((P/x['path']).read_bytes())!=x['sha256']]
out={'count':len(rows),'bytes':m['bytes'],'bad':bad,'reportSha256':sha(report.read_bytes()),'manifestSha256':sha((R/'manifest.json').read_bytes()),'result':'STATIC_A_COMPLETE_NOT_RUNTIME_PASS','oracleCases':len(cases),'autoB':False}
(R/'freeze.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
