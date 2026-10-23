"""Actual serialized proposals only. This module has no execution entry."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
def proposals(work_root=None):
    # Inactive example root, not created, not an execution scope or authority.
    cwd=str(Path(work_root) if work_root is not None else ROOT/'FUTURE_VALIDATION_NOT_CREATED')
    env={'SystemRoot':'C:\\Windows','WINDIR':'C:\\Windows','TEMP':cwd,'TMP':cwd}
    rows=[]
    for profile,exe,argv in (
      ('python_ok',PY,[PY,'-I','-X','utf8','-B',str(ROOT/'owned_child.py'),'ok']),
      ('powershell_ok',PS,[PS,'-NoProfile','-NonInteractive','-File',str(ROOT/'owned_child.ps1')]),
      ('python_fail',PY,[PY,'-I','-X','utf8','-B',str(ROOT/'owned_child.py'),'fail'])):
        rows.append({'schema':'OWNED_CAPTURE_PLAN_V1','profile':profile,'executable':exe,'argv':argv,'commandLine':subprocess.list2cmdline(argv),'cwd':cwd,'env':dict(env),'shell':False,'closeFds':True})
    return rows
