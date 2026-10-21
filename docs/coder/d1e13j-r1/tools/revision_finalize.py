from pathlib import Path
import json,hashlib,difflib
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';J=R/'docs/coder/d1e13j'
assert not (E/'e13j-r1-freeze.json').exists(),'FINAL_R1_ALREADY_FROZEN'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
old=J/'tools/E13JArchive.java';new=B/'tools/E13JArchive.java';diff=E/'diffs/R1-vs-initial-J-archive.diff';diff.write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile=old.relative_to(R).as_posix(),tofile=new.relative_to(R).as_posix())),encoding='utf-8')
record=dict(status='R1_FINAL_SELECTED_INITIAL_J_IMMUTABLE',reason='Self-review found raw write exception could terminate audit writer before subsequent admitted RX; R1 catches raw write fault inside writer loop and preserves audit until original reader done.',initialJSeal=pin(J/'evidence/e13j-freeze.json'),initialJZip=pin(R/'docs/coder/D1-20261018-E13J-source.zip'),initialSource=pin(old),finalSource=pin(new),diff=pin(diff),additionalTest='host-001/AUDIT_AFTER_RAW_FAILURE',initialProductionCompiles=1,revisionProductionCompiles=1,totalJProductionCompiles=2,sameSourceMechanicalRebuilds=0)
(E/'revision-history.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='2026-10-18 J-R1最终增补：本文件仅属最终R1，旧J首次包/源码/四文档/外seal保持不变且尚未另交审。收尾自核发现raw写异常可能令审账writer先退出，故真实源码修正为raw失败仅停raw写，审账writer继续等待同reader done，再写准确终止快照。新增AUDIT_AFTER_RAW_FAILURE真实生产回归验证原raw故障后仍准入的有限后续RX进入最终cw/in，未用harness额外facts。最终为10个有限组（原9＋新增1）及3父故障组；本revision一次host编译，整个J阶段两次，因实际源码变化而非同源机械重建。旧J算第十三组既有seal，均逐字节保持。\n\n'
for stem in ['FIXED_SOCKET_DELIVERY','IMPLEMENTATION_CONTRACT','SELF_CHECK_REPORT','E13G_SUPPLEMENT_PLAN']:
 p=R/'docs/coder'/('D1_E13J_R1_'+stem+'_V1.0.md');t=p.read_text();i=t.index('\n\n')+2;t=t[:i]+note+t[i:];t=t.replace('十二组','十三组').replace('9个直接有限组','10个直接有限组').replace('9组：OK','10组（含新增raw故障后RX审账）：OK');p.write_text(t,encoding='utf-8')
latest='> 2026-10-18 E13J-R1最终安排：收尾自核补齐raw写失败后审账writer须等原reader结束的边界；初版J保持冻结，R1实际源修正后额外必要编译一次，最终10组有限验证及3父诊断故障组通过，完整冻结交审。整个J阶段两次生产编译，不是同源重复。预算/审批ABSENT/三历史UNKNOWN/真实5037、设备、旧handle零操作保持，用户持续授权已存在；D1未过/M0未启，T07未派。\n\n'
for rel in ['docs/MILESTONE_COORDINATION_V1.0.md','docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md']:
 p=R/rel;t=p.read_text(encoding='utf-8');i=t.index('\n')+1;p.write_text(t[:i]+'\n'+latest+t[i:].lstrip('\n'),encoding='utf-8');(B/'reference'/p.name).write_bytes(p.read_bytes())
print('Final R1 selection, preserved initial seal and extra source/test reason documented')
