"""Explicit externally pinned facts entry. Default denies; no qualification output."""
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
def fixture_guard(ticket):
 # Two exact original calls in this process. No arbitrary test shell or route.
 import subprocess,os,hashlib
 from fact_collector import FIXTURE_PY,B
 from fact_preauth import encode,sha
 original=subprocess.Popen;cwd=str(Path.cwd());env=sha(encode(dict(os.environ)));calls=[];events=[];expected=[None]
 scripts=[B/'selfchecks/route_fixture.py',B/'selfchecks/fact_fixture.py']
 argv=[[FIXTURE_PY,'-I','-X','utf8','-B',str(scripts[0]),str(Path(ticket.policy['evidenceRoot'])/'gate-context.json')],[FIXTURE_PY,'-I','-X','utf8','-B',str(scripts[1]),'COMPLETE']]
 def observe(event,args):
  if event!='subprocess.Popen':return
  try:events.append(dict(matches=expected[0] is not None and args[0] is None and args[1]==expected[0] and args[2] is None and args[3] is None))
  except BaseException:events.append(dict(matches=False))
 def construct(a,*pos,**kw):
  i=len(calls)
  if pos or i>=2 or a!=argv[i] or str(Path.cwd())!=cwd or sha(encode(dict(os.environ)))!=env or any(not x['matches'] for x in events):raise ValueError('FACT_ENTRY_FIXTURE_PROFILE')
  if set(kw)-{'stdin','stdout','stderr','shell'} or kw.get('shell',False) is not False or kw.get('stdin')!=subprocess.DEVNULL or kw.get('stdout')!=subprocess.PIPE or kw.get('stderr')!=subprocess.PIPE:raise ValueError('FACT_ENTRY_FIXTURE_STREAMS')
  # Gate constructor already pinned script; this additional recheck is charged.
  seal=json.loads(ticket.gate.source_read(B/'reference/runner-source-seal.json'))
  if sha(ticket.gate.source_read(scripts[i]))!=seal['sources'][scripts[i].relative_to(B).as_posix()]:raise ValueError('FACT_ENTRY_FIXTURE_SOURCE')
  expected[0]=subprocess.list2cmdline(a)
  try:p=original(a,**kw);calls.append(dict(argv=list(a),constructorReturned=True));return p
  finally:expected[0]=None
 sys.addaudithook(observe);subprocess.Popen=construct
 return original,calls,events
def main(argv=None):
 from fact_preauth import PreparedFacts,decode,encode
 from fact_collector import OwnedFactCapture,FIXTURE_PY,B
 p=argparse.ArgumentParser();p.add_argument('--template',required=True);p.add_argument('--approved-template-sha256',required=True);p.add_argument('--policy',required=True)
 a=p.parse_args(argv)
 def bounded(path):
  from entry_gates import no_links
  no_links(path)
  with Path(path).open('rb') as stream:raw=stream.read(16385)
  if len(raw)>16384:raise ValueError('FACT_ENTRY_INPUT_BOUND')
  return raw
 raw=bounded(a.template);policy_raw=bounded(a.policy);policy=decode(policy_raw)
 if policy_raw!=encode(policy):raise ValueError('FACT_ENTRY_POLICY_CANONICAL_BYTES')
 ticket=PreparedFacts(raw,a.approved_template_sha256,policy)
 guard=fixture_guard(ticket) if ticket.template['mode']=='OFFLINE_FIXTURE' else None
 c=OwnedFactCapture()
 try:
  g=ticket.prepare();binding=ticket.bind(g)
  fixture=[FIXTURE_PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'] if g.fixture else None
  receipt=ticket.receive(g,binding,c,fixture)
 except BaseException:
  import time
  if c.unknown:
   while True:time.sleep(.1) # retain actual unknown originals; no exit/retry/close
  g=ticket.gate
  if g is not None:
   if getattr(c,'bodyReturned',False):c.finish_after_original_collect_return(g)
   elif not c.entered and not g.released and g.lease is not None and not g.lease.closed:g.release()
  raise
 release=c.finish_after_original_collect_return(g)
 # This original call has returned to its caller. This process's own outer
 # return is still established by its external original waiter, never itself.
 out=dict(schema='GLOBAL_IDLE_FACT_ENTRY_RETURN_V2',receipt=receipt,release=release,binding=decode(binding),outerProcessReturnStillRequired=True,qualificationIssued=False,sourceBytes=g.source_bytes,sourceReads=g.source_reads,controlBytes=sum(x['bytes'] for x in g.events)+g.carry)
 if guard:
  import subprocess
  subprocess.Popen=guard[0];out['fixtureConstructorCalls']=guard[1];out['fixtureAudit']=guard[2]
 sys.stdout.buffer.write(encode(out));return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except ValueError as e:print(json.dumps(dict(status='REJECTED',reason=str(e))));raise SystemExit(2)
