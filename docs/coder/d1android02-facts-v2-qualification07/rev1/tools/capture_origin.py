"""Minimal original-Capture event records in the trusted Python host.
Not protection against arbitrary mutation of this module's private memory.
"""
import os,threading,subprocess,json,hashlib
from types import MappingProxyType
ORIGINAL_POPEN_TYPE=subprocess.Popen
_RECORDS={}
def fail(code):raise ValueError(code)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def before_constructor(c,journal):
 from evidence_io import Journal
 if type(journal) is not Journal:fail('CAPTURE_ORIGIN_JOURNAL_SOURCE')
 if c in _RECORDS:fail('CAPTURE_ORIGIN_CONSTRUCTOR_ONCE')
def before_launch(c):
 r=_RECORDS.get(c)
 if r is None or r['phase']!='CONSTRUCTED' or r['owner']!=(os.getpid(),threading.get_ident()):fail('CAPTURE_ORIGIN_LAUNCH_ONCE')
 r['phase']='LAUNCH_ENTERED'
def constructed(c):
 if c in _RECORDS:fail('CAPTURE_ORIGIN_DUPLICATE_CONSTRUCTOR')
 _RECORDS[c]=dict(owner=(os.getpid(),threading.get_ident()),phase='CONSTRUCTED',plan=json.dumps(c.plan,sort_keys=True),journal=c.journal,control=c.control,original=None,closed=0,eof=[False,False])
def started(c,p):
 r=_RECORDS.get(c)
 if r is None or r['phase']!='LAUNCH_ENTERED' or type(p) is not ORIGINAL_POPEN_TYPE or r['owner']!=(os.getpid(),threading.get_ident()):fail('CAPTURE_ORIGIN_START')
 r.update(phase='STARTED',original=p,stdout=p.stdout,stderr=p.stderr,handle=p._handle,argv=tuple(c.plan['argv']))
def threads(c):
 r=_RECORDS[c];r.update(readers=tuple(c.readers),waiter=c.waiter)
def eof(c,i):_RECORDS[c]['eof'][i]=True
def completed(c):
 r=_RECORDS[c]
 if r['phase']!='STARTED' or r['original'] is not c.original or r['closed'] or not all(r['eof']) or not r['stdout'].closed or not r['stderr'].closed or c.wait_fact.get('returned') is not True or any(t.is_alive() for t in r['readers']) or r['waiter'].is_alive() or not r['journal'].returned() or not r['control'].returned():fail('CAPTURE_ORIGIN_COMPLETE')
 files=tuple(x['originalFile'] for x in r['journal'].files)
 if len(files)<3 or not all(f.closed for f in files):fail('CAPTURE_ORIGIN_JOURNAL_RETURN')
 r.update(phase='COMPLETED',closed=1,stdoutBytes=bytes(c.buffers[0]),stderrBytes=bytes(c.buffers[1]),identity=json.dumps(c.identity,sort_keys=True),exitCode=c.exit_code,wait=dict(c.wait_fact),counts=tuple(c.counts),facts=dict(c.facts),failure=c.failure,journalFiles=files)
def require(c):
 r=_RECORDS.get(c)
 if r is None or r['phase']!='COMPLETED':fail('V2_CAPTURE_CONSTRUCTION_PROVENANCE')
 if r['owner']!=(os.getpid(),threading.get_ident()) or r['original'] is not getattr(c,'original',None) or type(c.original) is not ORIGINAL_POPEN_TYPE or r['journal'] is not getattr(c,'journal',None) or r['control'] is not getattr(c,'control',None):fail('V2_CAPTURE_ORIGINAL_OBJECT')
 if c.plan is None or json.dumps(c.plan,sort_keys=True)!=r['plan'] or json.dumps(c.identity,sort_keys=True)!=r['identity'] or tuple(c.readers)!=r['readers'] or c.waiter is not r['waiter'] or c.original.stdout is not r['stdout'] or c.original.stderr is not r['stderr'] or c.original._handle is not r['handle']:fail('V2_CAPTURE_ORIGINAL_BINDING')
 if not c.returned or c.failure!=r['failure'] or json.dumps(c.wait_fact,sort_keys=True)!=json.dumps(r['wait'],sort_keys=True) or json.dumps(c.counts)!=json.dumps(list(r['counts'])) or json.dumps(c.facts,sort_keys=True)!=json.dumps(r['facts'],sort_keys=True) or bytes(c.buffers[0])!=r['stdoutBytes'] or bytes(c.buffers[1])!=r['stderrBytes'] or not r['journal'].returned() or tuple(x['originalFile'] for x in r['journal'].files)!=r['journalFiles'] or not all(f.closed for f in r['journalFiles']) or not r['control'].returned() or any(t.is_alive() for t in r['readers']) or r['waiter'].is_alive() or not r['stdout'].closed or not r['stderr'].closed:fail('V2_CAPTURE_COMPLETION_BINDING')
 if r['exitCode']!=0 or r['failure'] is not None or c.pipe_amount_unknown:fail('V2_CAPTURE_UNQUALIFIED')
 return MappingProxyType(r)
