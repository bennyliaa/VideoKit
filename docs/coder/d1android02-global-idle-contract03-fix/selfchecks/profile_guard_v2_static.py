"""STATIC DRAFT ONLY: not installed or executed in this batch.

Next exact scope must precheck an exact finite argv profile BEFORE calling the
original Popen constructor. A Windows audit tuple is an observation, not the
original argv list: applicationName may be None; commandLine is a string.
"""
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
def validate_before_constructor(argv,frozen_exact_argv_profiles):
 if type(argv) is not list or not argv or any(type(x) is not str for x in argv):raise ValueError('PROFILE_ARGV_TYPE_BEFORE_CONSTRUCTOR')
 if argv[0] not in (PY,PS) or tuple(argv) not in frozen_exact_argv_profiles:raise ValueError('PROFILE_EXACT_TUPLE_BEFORE_CONSTRUCTOR')
 return argv
def observe_audit_only(event,args,observations):
 if event=='subprocess.Popen':
  observations.append(dict(applicationName=args[0],commandLine=args[1],cwd=args[2],envExplicitlySupplied=args[3] is not None,kind='WINDOWS_PRE_CREATE_AUDIT_OBSERVATION_NOT_ARGV_OR_CLOSE_PROOF'))
if __name__=='__main__':raise SystemExit('STATIC_ONLY_NOT_APPROVED_OR_RUN; requires a new reviewed scope/profile before any constructor')
