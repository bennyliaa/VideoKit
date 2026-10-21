import device_guard as guard
checks=0
def reject(action):
 global checks
 try:action();raise AssertionError('unsafe preflight accepted')
 except guard.EnvironmentBlocked:checks+=1
for state in (2,3,4):reject(lambda:guard.installed_state('User 0: installed=true hidden=false suspended=false enabled='+str(state),0))
reject(lambda:guard.installed_state('User 0: installed=true enabled=0',10))
reject(lambda:guard.installed_state('User 0: installed=true',0))
reject(lambda:guard.installed_state('User 0: installed=true hidden=true enabled=0',0))
reject(lambda:guard.installed_state('User 0: installed=true suspended=true enabled=1',0))
reject(lambda:guard.installed_state('User 0: installed=false enabled=0',0))
assert guard.installed_state('User 0: installed=true hidden=false suspended=false enabled=0',0)==0;checks+=1
calls=[]
def disabled(args):
 calls.append(args)
 return '0' if args[1]=='am' else 'User 0: installed=true enabled=2'
reject(lambda:guard.require_ready('FAKE_SERIAL',disabled));assert len(calls)==2;checks+=1
def command_failed(args):raise guard.EnvironmentBlocked('COMMAND_EXIT_NONZERO')
reject(lambda:guard.require_ready('FAKE_SERIAL',command_failed))
def missing(args):return '0' if args[1]=='am' else 'User 0: installed=true enabled=0' if args[1]=='dumpsys' else 'No services found'
reject(lambda:guard.require_ready('FAKE_SERIAL',missing))
def ready(args):return '0' if args[1]=='am' else 'User 0: installed=true enabled=1' if args[1]=='dumpsys' else guard.PACKAGE+'/'+guard.SERVICE
assert guard.require_ready('FAKE_SERIAL',ready)['cpuServiceVisible'];checks+=1
def fake_error(args):return '0' if args[1]=='am' else 'User 0: installed=true enabled=1' if args[1]=='dumpsys' else 'SecurityException querying '+guard.PACKAGE+'/'+guard.SERVICE
reject(lambda:guard.require_ready('FAKE_SERIAL',fake_error))
def error_and_component(args):return '0' if args[1]=='am' else 'User 0: installed=true enabled=1' if args[1]=='dumpsys' else 'Error: denied\n'+guard.PACKAGE+'/'+guard.SERVICE
reject(lambda:guard.require_ready('FAKE_SERIAL',error_and_component))
print('PASS',checks,'pure environment/failed-exit/hard-stop checks; NO ADB OR DEVICE COMMANDS')
