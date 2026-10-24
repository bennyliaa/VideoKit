"""One frozen argv factory shared by actual calls and their pre-constructor gate."""
from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parents[1]/'coder/d1android02-facts-v2-qualification07/rev2'
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
def facts_argv(plan):
 f=plan['facts'];r=Path(f['root'])
 return [PY,'-I','-X','utf8','-B',str(H/'tools/facts_entry.py'),'--template',str(r/'template.json'),'--approved-template-sha256',f['templateSha256'],'--policy',str(r/'policy.json'),'--fixture-raw-file',str(r/'fixture-facts.raw'),'--fixture-raw-sha256',f['rawSha256']]
def review_argv(plan,label):
 d=plan['targets'][label]
 return [PY,'-I','-X','utf8','-B',str(R/'offline_reviewer.py'),'--request',d['request'],'--reply-root',d['reply']]
def aux_argv(plan,label):
 script={'budget':'budget_models.ps1','v1':'review_semantics.ps1'}[label];w=Path(plan['work'])
 if label=='budget':
  from independent_driver import build_budget_spec
  return list(build_budget_spec(R,w).argv)
 return [PS,'-NoProfile','-NonInteractive','-File',str(H/'selfchecks'/script),'-InputFile',str(w/(label+'-input.json')),'-OutputFile',str(w/(label+'-result.json'))]

BUDGET_CASES=['no-original-authority', 'fixed-file-positive', 'same-global-authority-after-reload', 'reinitialize-same-context', 'wrong-hash-charged-and-close', 'wrong-identity-charged-and-close', 'no-read-after-four-consumes', 'reload-keeps-rejection-budget', 'cap-before-open:baseGateBytes', 'cap-before-open:baseGateReads', 'cap-before-open:baseRunnerBytes', 'cap-before-open:baseRunnerReads', 'base-missing-not-default-zero', 'wrong-ticket-scope', 'base-bool', 'zero-reservation', 'real-issued-wire-with-explicit-synthetic-ticket', 'duplicate-initialize-after-full-reference']
