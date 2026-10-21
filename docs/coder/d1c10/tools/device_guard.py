"""Pure parsing plus explicit future tester preflight. No device operation at import."""
import re
PACKAGE='com.videokit.app'
SERVICE='com.videokit.spike.c10.CpuIsolatedService'
class EnvironmentBlocked(RuntimeError):pass
def installed_state(dump,user):
 match=re.search(r'^\s*User '+str(user)+r':([^\r\n]+)',dump,re.M)
 if not match:raise EnvironmentBlocked('ENVIRONMENT_UNKNOWN_USER_STATE')
 line=match.group(1)
 state=re.search(r'\benabled=(\d+)\b',line)
 if not state:raise EnvironmentBlocked('ENVIRONMENT_UNKNOWN_ENABLED_STATE')
 if int(state.group(1)) not in (0,1):raise EnvironmentBlocked('ENVIRONMENT_APP_DISABLED_MANUAL_ENABLE_REQUIRED')
 if 'installed=true' not in line or 'hidden=true' in line or 'suspended=true' in line:raise EnvironmentBlocked('ENVIRONMENT_APP_UNAVAILABLE')
 return int(state.group(1))
def require_ready(serial,checked):
 """checked must fail on command exit/timeout; verify actual state, never issue pm enable."""
 user_text=checked(['shell','am','get-current-user']).strip()
 if not re.fullmatch(r'\d{1,5}',user_text):raise EnvironmentBlocked('ENVIRONMENT_UNKNOWN_CURRENT_USER')
 user=int(user_text);dump=checked(['shell','dumpsys','package',PACKAGE]);state=installed_state(dump,user)
 visible=checked(['shell','cmd','package','query-services','--brief','--user',str(user),'-n',PACKAGE+'/'+SERVICE])
 component=PACKAGE+'/'+SERVICE
 if component not in [line.strip() for line in visible.splitlines()] or re.search(r'Exception|\bError\b|Unknown command|denied',visible,re.I):raise EnvironmentBlocked('ENVIRONMENT_CPU_SERVICE_NOT_VISIBLE')
 return {'serial':serial,'user':user,'appEnabledSetting':state,'cpuServiceVisible':True,'policy':'READ_ONLY_NO_ENABLE_NO_CLEAR_NO_UNINSTALL'}
