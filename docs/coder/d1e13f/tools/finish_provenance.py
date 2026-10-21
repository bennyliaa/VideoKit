"""Retain final fixture bytecode and every delivered source difference, without rerunning tests."""
from pathlib import Path
import json,hashlib,difflib
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';OLD=R/'docs/coder/d1e13e'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (E/'e13f-freeze.json').exists()
out=[]
for label in ['public-008','join-orders-009']:
 for p in sorted((B/'.checks'/label).rglob('*.class')):
  q=E/'test-fixture-class-bytes'/label/p.relative_to(B/'.checks'/label);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());out.append(pin(q))
write(E/'test-fixture-class-manifest.json',dict(status='RETAINED_ACTUAL_TEST_FIXTURE_BYTES',files=out,notProductionJar=True,rerun=False))
sources=[]
for folder in ['src','android','upstream-c14/src','upstream-c14/android','binding','checks/com','app/src','fixture/src','selfchecks','tools']:
 sources += [p for p in (B/folder).rglob('*') if p.is_file() and p.suffix in ['.java','.py','.ps1','.xml']]
sources += [p for root in [B,B/'app',B/'fixture'] for p in root.iterdir() if p.is_file() and p.suffix in ['.kts','.lockfile','.properties']]
rows=[]
for p in sorted(set(sources)):
 old=OLD/p.relative_to(B);before=pin(old) if old.is_file() else None;after=pin(p);same=before and before['sha256']==after['sha256'];rows.append(dict(current=after,baseline=before,relationship='BYTE_IDENTICAL' if same else 'MODIFIED' if before else 'NEW_E13F'))
 if not same:
  q=E/'diffs'/p.relative_to(B);q=q.with_suffix(q.suffix+'.diff');q.parent.mkdir(parents=True,exist_ok=True);q.write_text(''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True) if old.is_file() else [],p.read_text(encoding='utf-8-sig').splitlines(True),fromfile=before['path'] if before else '/dev/null',tofile=after['path'])),encoding='utf-8')
write(E/'source-derivation.json',dict(files=rows,baseline='FROZEN_E13E',nativeBuilds=0))
print('Retained',len(out),'actual fixture classes and',len(rows),'final source/config pins; tests not rerun')
