"""Exact fixes and adjacent boundaries; expectations include the rejection layer."""
from fixture_inputs import qualification,context,text,record,service
def cases():
 out=[]
 def add(i,t,reason,status='BLOCKED_UNPROVEN',q=None):
  q=q or qualification();out.append(dict(id=i,text=t,qualification=q,context=context(t,q),expected=status,expectedReason=reason))
 for kind in ('APP','PERS'):
  base=record('com.fixture.bad','com.fixture.bad',10065,2,901,'bad003',kind)
  variants={'uid-space':base.replace('UID 10065','UID10065'),'uid-case':base.replace('UID 10065','uid 10065'),'star-space':base.replace('* UID','*UID'),'missing-star':base.replace('*'+kind+'* ','')}
  for variant,bad in variants.items():
   for place in ('prefix','between','tail','post-summary'):
    bg=record('com.fixture.bg','com.fixture.bg',10066,16,902,'bad004')
    body=bad+record() if place=='prefix' else record()+bad+bg if place=='between' else record()+bg+bad if place=='tail' else record()+'  UID states:\n      curProcState=0\n'+bad
    add('B01_'+kind+'_'+variant+'_'+place,text(home=body),'GLOBAL_PROCESS_HEADERS_UNPROVEN')
 add('B01_ORPHAN_PREFIX',text(home='    user #0 uid=10065\n    packageList={com.fixture.bad}\n    curProcState=2\n'+record()),'GLOBAL_PROCESS_HEADERS_UNPROVEN')
 for token in ('16.5','1.5','16.0','16e0','16x','0x10','016','16/2','16;','16 curProcState=2'):
  for which in ('home','cached'):
   t=text().replace('curProcState=2','curProcState='+token) if which=='home' else text(record('com.fixture.bg','com.fixture.bg',10065,16,901,'bad003').replace('curProcState=16','curProcState='+token))
   add('B02_'+which+'_'+token,t,'GLOBAL_PROCESS_STATE_UNPROVEN')
 # Canonical supported states retain their distinct policy semantics.
 for state in range(20):
  q=qualification();status='PASS';reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY';kind='APP';name='com.fixture.bg'
  if state in (0,1,4,5,6):
   kind='PERS';name='com.fixture.system:worker';service(q,state=state)
  elif state in (2,3):status='BLOCKED_OCCUPIED';reason='ENV_WAIT_FOREIGN_FOREGROUND'
  elif state in (9,11,12):status='BLOCKED_OCCUPIED';reason='ENV_WAIT_CONTENDING_OPERATION'
  pkg='com.fixture.system' if kind=='PERS' else 'com.fixture.bg'
  add('B02_SUPPORTED_'+str(state),text(record(name,pkg,10065,state,901,'bad003',kind)),reason,status,q)
 return out
