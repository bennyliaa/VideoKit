from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
for p in (B/'tools').glob('*'):
 if p.suffix not in ['.py','.ps1','.java'] or p.name=='finish_revision_setup.py':continue
 t=p.read_text(encoding='utf-8-sig').replace('docs/coder/d1e13j/','docs/coder/d1e13j-r1/').replace('D1-20261018-E13J-source.zip','D1-20261018-E13J-R1-source.zip').replace('e13j-freeze.json','e13j-r1-freeze.json').replace('D1_E13J_','D1_E13J_R1_').replace('D1_E13J_G_SUPPLEMENT_EVIDENCE','D1_E13J_R1_G_SUPPLEMENT_EVIDENCE').replace('e13j-g-readonly.once','e13j-r1-g-readonly.once').replace('E13J-SUPPLEMENT-ONCE','E13J-R1-SUPPLEMENT-ONCE');p.write_text(t,encoding='utf-8')
for role in ['CODER','TESTER']:
 p=R/'docs/milestones'/('D1_E13J_R1_'+role+'_REQUIREMENTS_V1.0.md');base=(R/'docs/milestones'/('D1_E13J_'+role+'_REQUIREMENTS_V1.0.md')).read_text();p.write_text('# E13J-R1 收尾补充（原需求全文附后）\n\n2026-10-18。首次J集中候选已冻结但尚未交审；收尾自核发现raw写失败可能令审账writer早于reader退出。保留J初版所有字节，在独立J-R1目录继续原三P1任务，仅修raw故障后审账writer等待原reader done，并新增生产IO故障后继续接收有限尾字节的审账回归。预算/权限/执行范围不变。由于实际生产源码变化额外一次host编译，不能说整个J批只有一次；本revision自身一次。旧I/J及三历史UNKNOWN冻结不动。\n\n'+base,encoding='utf-8')
print('R1 paths, separate documents and formal addenda prepared')
