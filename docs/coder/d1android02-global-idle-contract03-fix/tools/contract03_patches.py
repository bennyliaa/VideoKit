"""Minimal source assembly substitutions; never invoked by runtime owners."""
def replace(s,a,b):
 if a not in s:raise ValueError('CONTRACT03_SOURCE_EXPECTED:'+a[:90])
 return s.replace(a,b)
def gate_patch(s):
 a=s.index('def fixture_root_allowed(path):');z=s.index('\ndef stable(',a)
 s=s[:a]+'''def fixture_root_allowed(path):
 try:
  if not isinstance(path,(str,Path)):return False
  raw=str(path)
  if any(x in ('.','..') for x in raw.replace('\\\\','/').split('/')):return False
  p=Path(path)
  if not p.is_absolute() or p.drive.casefold()!=BASE.drive.casefold() or p.absolute()!=p.resolve():return False
  no_links(p)
  roots=(BASE/'selfchecks/work',Path('D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/fixtures'))
  return any(p!=root and p.is_relative_to(root) for root in roots)
 except (ValueError,OSError):return False
''' +s[z:]
 return replace(s,'not fixture_root_allowed(self.root)','not fixture_root_allowed(p[\'evidenceRoot\'])')
def runner_patch(s):
 s=replace(s,'from entry_gates import ', 'from entry_gates import fixture_root_allowed,')
 lines=s.splitlines(True)
 for i,line in enumerate(lines):
  if 'allowed=self.home.is_relative_to(' in line:lines[i]='   allowed=fixture_root_allowed(p[\'home\'])\n'
 return ''.join(lines)
def owner_patch(s):
 s=replace(s,'BASE=Path(__file__)','from entry_gates import fixture_root_allowed\nBASE=Path(__file__)')
 lines=s.splitlines(True)
 for i,line in enumerate(lines):
  if "raise ValueError('EXACT_FIXTURE_ROOT')" in line and 'startswith' in line:lines[i]="   if not fixture_root_allowed(p['evidenceRoot']):raise ValueError('EXACT_FIXTURE_ROOT')\n"
 return ''.join(lines)
