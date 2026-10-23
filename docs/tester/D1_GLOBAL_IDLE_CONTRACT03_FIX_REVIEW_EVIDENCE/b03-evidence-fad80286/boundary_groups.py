from pathlib import Path
import copy
def root_negatives(ns,W,save):
 rows=[]
 base=W.parents[0]
 samples=[('outside',W.parents[2]/'outside-b03'/W.name/'h','FIXTURE_HOME'),('prefix',Path(str(base)+'-other')/W.name/'h','FIXTURE_HOME'),('old-root',ns['B'].parent/'d1android02-global-idle-contract02-revision02/selfchecks/work/new-b03-test/h','FIXTURE_HOME'),('dot-alias',None,'CANONICAL_OUTPUT_PATH_REQUIRED')]
 for name,target,expected in samples:
  f,p=ns['permit']('root-'+name);old=p['home'];new=str(target.resolve()) if target is not None else old+'\\.\\'
  def repl(x):
   if type(x) is dict:return {k:repl(v) for k,v in x.items()}
   if type(x) is list:return [repl(v) for v in x]
   if type(x) is str:return x.replace(old,new)
   return x
  p=repl(p);args=ns['inputs'](f,p)
  try:
   r=ns['construct'](args);r.run();actual='ACCEPTED'
  except ValueError as e:actual=str(e)
  passed=actual==expected and not Path(p['home']).exists()
  rows.append(dict(name=name,home=new,expected=expected,actual=actual,passed=passed,originalGateEntered=False))
 save(W/'root-negatives.json',rows)
 assert all(x['passed'] for x in rows),rows
 return rows
