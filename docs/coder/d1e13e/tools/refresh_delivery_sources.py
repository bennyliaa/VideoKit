from pathlib import Path
import json,hashlib,difflib
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=R/'docs/coder/d1e13a';E=B/'evidence'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
rows=[]
for folder in ['src','android','upstream-c14/src','upstream-c14/android','binding','checks/com','app/src','fixture/src','tools']:
 for p in sorted((B/folder).rglob('*')):
  if not p.is_file() or p.suffix not in ['.java','.ps1','.py','.xml']:continue
  old=(R/'docs/coder/d1e13c/tools'/p.name) if p.name in ['E11DeploymentOnce.java','E13HostActivationSession.java'] and folder=='tools' else A/p.relative_to(B)
  before=pin(old) if old.exists() else None;after=pin(p);same=before and before['sha256']==after['sha256'];rows.append(dict(current=after,baseline=before,relationship='BYTE_IDENTICAL' if same else 'MODIFIED' if before else 'NEW_E13E'))
  if not same:
   q=E/'diffs'/p.relative_to(B);q=q.with_suffix(q.suffix+'.diff');q.parent.mkdir(parents=True,exist_ok=True);q.write_text(''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True) if old.exists() else [],p.read_text(encoding='utf-8-sig').splitlines(True),fromfile=before['path'] if before else '/dev/null',tofile=after['path'])),encoding='utf-8')
(E/'source-derivation.json').write_text(json.dumps(dict(files=rows,nativeBuilds=0),ensure_ascii=False,indent=2)+'\n')
p=R/'docs/coder/D1_E13E_SELF_CHECK_REPORT_V1.0.md';t=p.read_text();t=t.replace('## 保留的开发期失败与修正','outer-009针对最终实际observer再验：持久receipt的自身close为未证/null，console仅在实际metadata文件close后给全归还；原stdout文件不可用不覆盖，仍读完同一原进程。outer-008原Process自然结束后，console解析发现VoidTaskResult杂讯，源头[void]抑制并留原失败材料，不把它算设备或资源归还成功。\n\nr01-lock-010直接执行最终E9观察，实际stage sink与平台边界均不持E9CurrentObservation.class monitor；原ACTIVE登记/退回与无假grant同时验证。\n\n## 保留的开发期失败与修正');p.write_text(t,encoding='utf-8')
s=json.loads((E/'final-summary.json').read_text());s.update(finalHostCompile='host-006',actualAfter007=True,finalOuterReceipt='outer-009',realR01LockBoundary='r01-lock-010');(E/'final-summary.json').write_text(json.dumps(s,indent=2)+'\n')
print('final source catalog/diffs and accurate selfcheck boundary notes refreshed')
