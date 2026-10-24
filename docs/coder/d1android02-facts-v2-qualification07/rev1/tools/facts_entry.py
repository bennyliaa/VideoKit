"""Explicit externally pinned facts entry. Default denies; no qualification output."""
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
def validate_fixture_call(expected,a,pos,kw,context_ok=True):
 import subprocess
 if pos or type(a) is not list or a!=expected or not context_ok:raise ValueError('FACT_ENTRY_FIXTURE_PROFILE_BEFORE_CONSTRUCTOR')
 if set(kw)-{'stdin','stdout','stderr','shell'} or kw.get('shell',False) is not False or kw.get('stdin')!=subprocess.DEVNULL or kw.get('stdout')!=subprocess.PIPE or kw.get('stderr')!=subprocess.PIPE:raise ValueError('FACT_ENTRY_FIXTURE_STREAMS_BEFORE_CONSTRUCTOR')
 return True

def fixture_guard(ticket,fixture_argv):
 import subprocess,os
 from fact_collector import FIXTURE_PY,B
 from fact_preauth import encode,sha
 original=subprocess.Popen;cwd=str(Path.cwd());env=sha(encode(dict(os.environ)));calls=[];events=[];expected=[None];admitted=set()
 scripts=[B/'selfchecks/route_fixture.py',B/'selfchecks/fact_fixture.py']
 argv=[[FIXTURE_PY,'-I','-X','utf8','-B',str(scripts[0]),str(Path(ticket.policy['evidenceRoot'])/'gate-context.json')],fixture_argv]
 def observe(event,args):
  if event=='subprocess.Popen':events.append(dict(matches=expected[0] is not None and args[0] is None and args[1]==expected[0] and args[2] is None and args[3] is None))
 def preflight(a,*pos,**kw):
  i=len(calls);g=ticket.gate
  try:
   if i>=2 or i in admitted:raise ValueError('FACT_ENTRY_FIXTURE_ONCE_BEFORE_CONSTRUCTOR')
   validate_fixture_call(argv[i],a,pos,kw,str(Path.cwd())==cwd and sha(encode(dict(os.environ)))==env and all(x['matches'] for x in events))
   seal=json.loads(g.source_read(B/'reference/runner-source-seal.json'))
   if sha(g.source_read(scripts[i]))!=seal['sources'][scripts[i].relative_to(B).as_posix()]:raise ValueError('FACT_ENTRY_FIXTURE_SOURCE_BEFORE_CONSTRUCTOR')
   # These journal writes and all validation occur before the callable that
   # can enter the original constructor is returned to the original owner.
   g.write('fixture-preconstructor-'+str(i)+'.json',encode(dict(stage='PRECONSTRUCTOR_ADMITTED',originalConstructorEntered=False,scope=g.scope,index=i,sourceReads=g.source_reads,sourceBytes=g.source_bytes,argv=a)))
  except BaseException as e:
   g.write('fixture-preconstructor-rejected-'+str(i)+'.json',encode(dict(stage='KNOWN_PRECONSTRUCTOR_REJECTION',originalConstructorEntered=False,scope=g.scope,index=i,reason=repr(e))))
   raise
  admitted.add(i);actual=list(a);options=dict(kw);command=subprocess.list2cmdline(actual)
  def start_original(mark_entered=None):
   # No guard, source read, budget decision or durable IO between this marker
   # and the saved original Popen. An exception after this point is UNKNOWN.
   if mark_entered is not None:mark_entered()
   expected[0]=command
   try:
    p=original(actual,**options);calls.append(dict(argv=list(actual),constructorReturned=True));return p
   finally:expected[0]=None
  return start_original
 def deny_unprepared(*a,**kw):raise ValueError('FACT_ENTRY_PREPARED_CONSTRUCTOR_REQUIRED')
 deny_unprepared.preflight=preflight
 sys.addaudithook(observe);subprocess.Popen=deny_unprepared
 return original,calls,events

def main(argv=None):
 from fact_preauth import PreparedFacts,decode,encode,sha
 from fact_collector import OwnedFactCapture,FIXTURE_PY,B
 p=argparse.ArgumentParser();p.add_argument('--template',required=True);p.add_argument('--approved-template-sha256',required=True);p.add_argument('--policy',required=True);p.add_argument('--fixture-raw-file');p.add_argument('--fixture-raw-sha256')
 a=p.parse_args(argv)
 def bounded(path):
  from entry_gates import no_links
  no_links(path)
  with Path(path).open('rb') as stream:raw=stream.read(16385)
  if len(raw)>16384:raise ValueError('FACT_ENTRY_INPUT_BOUND')
  return raw
 raw=bounded(a.template);policy_raw=bounded(a.policy);policy=decode(policy_raw)
 if policy_raw!=encode(policy):raise ValueError('FACT_ENTRY_POLICY_CANONICAL_BYTES')
 fixture_argv=[FIXTURE_PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'] if policy.get('mode')=='OFFLINE_FIXTURE' else None
 fixture_raw=None
 if a.fixture_raw_file is not None or a.fixture_raw_sha256 is not None:
  if fixture_argv is None or type(a.fixture_raw_sha256) is not str or a.fixture_raw_file!=str(Path(policy['evidenceRoot']).parent.parent/'fixture-facts.raw'):raise ValueError('FACT_ENTRY_RAW_FIXTURE_ONLY')
  from entry_gates import no_links
  from fact_collector import facts,sha
  no_links(a.fixture_raw_file)
  with Path(a.fixture_raw_file).open('rb') as f:fixture_raw=f.read(139265)
  if not 1<=len(fixture_raw)<=139264 or sha(fixture_raw)!=a.fixture_raw_sha256:raise ValueError('FACT_ENTRY_RAW_BOUND_OR_HASH')
  facts(fixture_raw)
  fixture_argv=fixture_argv[:6]+['RAW_FILE',a.fixture_raw_file,a.fixture_raw_sha256]
 ticket=PreparedFacts(raw,a.approved_template_sha256,policy,fixture_raw)

 guard=fixture_guard(ticket,fixture_argv) if ticket.template['mode']=='OFFLINE_FIXTURE' else None
 c=OwnedFactCapture()
 try:
  g=ticket.prepare();binding=ticket.bind(g)
  fixture=fixture_argv
  receipt=ticket.receive(g,binding,c,fixture)
  # Compare all actually charged reads/reservations before releasing the same
  # original claim. Chunked evidence stays under the existing 16384 file cap.
  chunks=[]
  for n in range(0,len(g.source_events),12):
   name='fact-source-ledger-'+str(n//12)+'.json';data=encode(dict(scope=g.scope,rows=g.source_events[n:n+12]));g.write(name,data);chunks.append(dict(path=str(g.root/name),bytes=len(data),sha256=sha(data)))
  g.write('fact-source-summary.json',encode(dict(schema='FACT_COMPLETE_SOURCE_ACTUAL06_V1',scope=g.scope,sourceReads=g.source_reads,sourceBytes=g.source_bytes,plannedReads=ticket.sourcePlan['sourceReads'],plannedBytes=ticket.sourcePlan['sourceBytes'],admittedBeforeUsed=ticket.admittedBeforeUsed,chunks=chunks,originalFactsBodyReturned=c.bodyReturned,originalClaimReleaseStillRequired=True)))
  if g.source_reads!=ticket.sourcePlan['sourceReads'] or g.source_bytes!=ticket.sourcePlan['sourceBytes'] or len(g.source_events)!=len(ticket.sourcePlan['rows']):raise ValueError('FACT_COMPLETE_SOURCE_PLAN_ACTUAL_MISMATCH')
 except BaseException:
  import time
  if c.unknown:
   while True:time.sleep(.1) # retain actual unknown originals; no exit/retry/close
  g=ticket.gate
  if g is not None:
   if getattr(c,'bodyReturned',False):
    rejected_release=c.finish_after_original_collect_return(g);g.write('facts-known-rejection-release.json',encode(dict(originalRelease=rejected_release,originalFactsBodyReturned=True,constructorEntered=c.entered,knownRejection=True)))
   elif not c.entered and not g.released and g.lease is not None and not g.lease.closed:
    rejected_release=g.release();g.write('facts-known-rejection-release.json',encode(dict(originalRelease=rejected_release,originalConstructorEntered=False,knownRejection=True)))
  raise
 release=c.finish_after_original_collect_return(g)
 # This original call has returned to its caller. This process's own outer
 # return is still established by its external original waiter, never itself.
 out=dict(schema='GLOBAL_IDLE_FACT_ENTRY_RETURN_V2',receipt=receipt,release=release,binding=decode(binding),outerProcessReturnStillRequired=True,qualificationIssued=False,sourceBytes=g.source_bytes,sourceReads=g.source_reads,controlBytes=sum(x['bytes'] for x in g.events)+g.carry)

 if guard:
  import subprocess
  subprocess.Popen=guard[0];out['fixtureConstructorCalls']=guard[1];out['fixtureAudit']=guard[2]
 from facts_contract import encode_entry
 sys.stdout.buffer.write(encode_entry(out,g,bytes(c.buf[0])));return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except ValueError as e:print(json.dumps(dict(status='REJECTED',reason=str(e))));raise SystemExit(2)
