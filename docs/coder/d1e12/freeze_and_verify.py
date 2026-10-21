"""Local documentary byte audit; no project code, builds, device or media execution."""
from pathlib import Path
import hashlib,json,zipfile
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/coder/d1e12'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
    b=(ROOT/p).read_bytes();return {'path':p,'bytes':len(b),'sha256':sha(b)}
def check(row):
    actual=pin(row['path']);assert actual['bytes']==row['bytes'] and actual['sha256']==row['sha256'],row['path']
def write(p,v):
    (ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
inputs=json.loads((BASE/'input-pins.json').read_text(encoding='utf-8'))['inputs']
for r in inputs:
    check(r);assert (BASE/'reference'/r['path']).read_bytes()==(ROOT/r['path']).read_bytes(),r['path']
old=[('docs/coder/d1e11/evidence/e11-freeze.json','fd71fd2f3e696a144befb84307391f5f11c6b966dc068063d409c7df95f3eaa5',375),('docs/coder/d1e11/revision-r1/evidence/e11-final-freeze.json','2e1dcdcf212131952529e998da0f0cd1c14e10ca3eee912d1f897181b7cf81d3',65)]
frozen=[]
for p,h,n in old:
    assert pin(p)['sha256']==h,p
    rows=json.loads((ROOT/p).read_text(encoding='utf-8'))['immutableFiles'];assert len(rows)==n,(p,len(rows))
    for row in rows:check(row)
    frozen.append({'seal':pin(p),'verifiedRows':len(rows),'result':'UNCHANGED'})
reqs=json.loads((BASE/'requirement-rows.json').read_text(encoding='utf-8'))
assert len(reqs)==99 and len({r['id'] for r in reqs})==99
matrix=(ROOT/'docs/coder/D1_E12_REQUIREMENT_EVIDENCE_MATRIX_V1.0.md').read_text(encoding='utf-8')
for r in reqs:assert '| '+r['id']+' / U:'+str(r['line']) in matrix,r['id']
for i in range(1,12):assert '| J'+str(i).zfill(2)+' |' in matrix
audit={'schema':1,'atUtc':datetime.now(timezone.utc).isoformat(),'scope':'read-only local documentary hashing, not candidate tests','inputFiles':len(inputs),'rawReferenceCopies':len(inputs),'explicitRequirements':99,'P0':13,'J':11,'priorFreezes':frozen,'deviceCalls':0,'mediaProcessing':0,'builds':0,'candidateTestRuns':0,'result':'PASS_DOCUMENTARY_BYTE_AUDIT'}
write('docs/coder/d1e12/pre-freeze-audit.json',audit)
delivery='''# D1 E12 完整审计交付 V1.0

日期：2026-10-18。结果：完成本批只读审计及下一完整批次提案，交独立tester审查；不是D1整体验收通过。D1 NOT_PASSED / M0 NOT_STARTED。

交付主件：D1_E12_REQUIREMENT_EVIDENCE_MATRIX_V1.0.md、D1_E12_REMAINING_GATE_DECISION_V1.0.md、D1_E12_NEXT_BATCH_CODER_REQUIREMENTS_PROPOSAL_V1.0.md、D1_E12_NEXT_BATCH_TESTER_REQUIREMENTS_PROPOSAL_V1.0.md，均在docs/coder。正式E12双需求已保存docs/milestones。

矩阵逐条覆盖§26–31共99条具体要求，另列§28各里程碑、§30十份设计文档、原§4全部13项P0与J01–J11。31个精确原始输入及原字节副本、来源/行号索引与结构化行清单随包。含E11实际接受报告、独立静态审查、C13/C14与E6B历史证据及当前关键源码；不是全历史媒体/候选制品重打包。

有限关闭E6B-OBS-F01仅E11四独立host实际观察范围。保留历史AVI Before失败、C13 self signal0严格FAIL、外部raw11与另双槽系统11的独立含义，C14两项NOT_RUN及ordinary UNKNOWN。原7库/35Maven、FFmpeg8.0.3/Media3 1.9.3、许可/模型权利等均未由本批新增准入。

下一批建议以六个精确入口完成普通发送者拒绝及授权source资源生命周期，采用既有owner/监督机制、单次集中构建和不产生新输出的有限预算；提案不是派单。永久UNKNOWN无保管出口则BLOCKED，renderer/audio及独立Kit保留具体可行性缺口和后续阶段责任，不实现新安全模型、不启动M0。

本批核验：31个输入及副本一致，99条矩阵定位存在；E11基础375项、R1最终65项及两原封印逐字节不变（行数按各层分别记，不将重叠文件数相加冒充唯一数）。这仅是本地文件哈希审计，没有构建、候选自检、旧测试重跑、设备操作或媒体处理。

当前账本采用E11报告接受时点214483B/7R7S/reserved0；旧107218B/1011B前缀保持。未读取设备或宣称当前在线状态，未改账/产品/历史冻结件。

文档ZIP：docs/coder/D1-20261018-E12-audit.zip；外置封印：docs/coder/d1e12/e12-freeze.json；最终只读校验回执：docs/coder/D1_E12_FINAL_READONLY_VERIFICATION_V1.0.json。原ZIP和seal的精确SHA记录于包外回执，不使用自指封印。文档组装/封装脚本仅处理本地文字与文件字节，不导入或执行候选代码。

组装过程中一次标题正则将26.1误识为26而停止，已修正后完成；该本地文档工具错误不计产品FAIL或运行测试。早期检索遇到旧路径/输出截断后，采用实际定位与原文件pins，不推定缺失路径代表产品执行失败。下一批未开发，等待负责人审查和正式派发。
'''
(ROOT/'docs/coder/D1_E12_DELIVERY_V1.0.md').write_text(delivery,encoding='utf-8',newline='\n')
files=[p for p in BASE.rglob('*') if p.is_file() and p.name not in {'e12-freeze.json'}]
files += [p for p in (ROOT/'docs/coder').glob('D1_E12_*.md')]
files += [ROOT/'docs/milestones/D1_E12_CODER_REQUIREMENTS_V1.0.md',ROOT/'docs/milestones/D1_E12_TESTER_REQUIREMENTS_V1.0.md']
rel=sorted({p.relative_to(ROOT).as_posix() for p in files})
assert all('/build/' not in p and '/test_media/' not in p for p in rel)
archive='docs/coder/D1-20261018-E12-audit.zip'
assert not (ROOT/archive).exists(),'Do not overwrite a frozen archive'
with zipfile.ZipFile(ROOT/archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for p in rel:z.write(ROOT/p,p)
with zipfile.ZipFile(ROOT/archive) as z:
    assert sorted(z.namelist())==rel
    for p in rel:assert z.read(p)==(ROOT/p).read_bytes(),p
seal={'schema':1,'status':'FROZEN_E12_DOCUMENTARY_AUDIT_NOT_IMPLEMENTATION_AUTHORITY','atUtc':datetime.now(timezone.utc).isoformat(),'archive':pin(archive),'immutableFiles':[pin(p) for p in rel]+[pin(archive)],'priorFreezes':frozen,'exclusions':['docs/coder/d1e12/e12-freeze.json','docs/coder/D1_E12_FINAL_READONLY_VERIFICATION_V1.0.json','post-freeze handoff/notification receipt'],'noSelfHash':True}
write('docs/coder/d1e12/e12-freeze.json',seal)
for row in seal['immutableFiles']:check(row)
for row in inputs:check(row)
for p,h,n in old:
    assert pin(p)['sha256']==h
    for row in json.loads((ROOT/p).read_text(encoding='utf-8'))['immutableFiles']:check(row)
receipt={'schema':1,'result':'PASS_E12_READONLY_DOCUMENTARY_VERIFICATION','atUtc':datetime.now(timezone.utc).isoformat(),'archive':pin(archive),'externalSeal':pin('docs/coder/d1e12/e12-freeze.json'),'archiveEntries':len(rel),'immutableRows':len(seal['immutableFiles']),'inputFiles':len(inputs),'explicitRequirements':99,'P0':13,'J':11,'priorFreezes':frozen,'deviceCalls':0,'mediaProcessing':0,'builds':0,'candidateTests':0,'nextBatchImplementation':'NOT_STARTED','D1':'NOT_PASSED','M0':'NOT_STARTED'}
write('docs/coder/D1_E12_FINAL_READONLY_VERIFICATION_V1.0.json',receipt)
print(json.dumps(receipt,ensure_ascii=False))
