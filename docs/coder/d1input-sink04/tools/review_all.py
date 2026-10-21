from pathlib import Path
import json,hashlib,subprocess,sys,re,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2].resolve();match=re.fullmatch(r'd1input-sink([0-9]{2})',B.name);assert match,'CANDIDATE_REQUIRED'
assert len(sys.argv)==3 and sys.argv[1]=='--output','USAGE_--output_NEW_ABSOLUTE_REVIEW_CHILD'
root=R/'docs/tester'/('D1_INPUT_SINK'+match.group(1)+'_REVIEW_EVIDENCE');assert root.resolve()==root,'REVIEW_ROOT_REDIRECTION_REJECTED'
raw=Path(sys.argv[2]);assert raw.is_absolute() and raw.drive.casefold()==B.drive.casefold(),'ABSOLUTE_LOCAL_REVIEW_PATH_REQUIRED';D=raw.resolve()
try:relative=D.relative_to(root)
except ValueError:raise AssertionError('INDEPENDENT_TESTER_ROOT_ONLY') from None
assert relative.parts,'NEW_REVIEW_SUBDIRECTORY_REQUIRED'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=B/'evidence'/('input-sink'+match.group(1)+'-freeze.json')
if seal.exists():
 frozen=json.loads(seal.read_text());assert all((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'] for x in frozen['files']),'FROZEN_CANDIDATE_MISMATCH'
D.mkdir(parents=True,exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin');P=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe');jar=B/('artifacts/input-sink'+match.group(1)+'-classes.jar');runs=[]
def run(name,argv,mode):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(D/(name+'.stdout')).write_bytes(p.stdout);(D/(name+'.stderr')).write_bytes(p.stderr);receipt={'argv':argv,'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':p.returncode,'originalProcessReturned':True,'mode':mode,'productionJarFirst':mode=='production','jarSha256':sha(jar),'frozenCandidate':seal.exists()};(D/(name+'.json')).write_text(json.dumps(receipt,indent=2),encoding='utf-8');runs.append({'name':name,'exitCode':p.returncode,'mode':mode});print(name,'exit',p.returncode,flush=True);assert p.returncode==0,(name,p.stderr.decode('utf-8','replace'))
run('documented-entry',[str(P),'-X','utf8','-B',str(B/'tools/local_check.py'),'--review-output',str(D/'source')],'compile-and-source-core')
C=D/'source/classes';deps=sorted((B/'deps').glob('*.jar'));source=';'.join(map(str,[C]+deps));prod=str(jar)+';'+source
plan=[('original17','ReturnBoundaryCheck',[]),('tester12','IndependentFixCheck',[]),('readback','ReadbackReturnCheck',[]),('latecancel','LateCancellationRegression',[]),('input','InputExceptionCheck',[])]+[('cancel-'+p,'CancellationRegression',[p]) for p in ['WRITE','FLUSH','CLOSE','REOPEN','VALIDATE','COMMIT']]+[('history-'+p,'AbortHistoryRegression',[p]) for p in ['ABORT','QUERY','ABORT_ERROR']]+[('matrix','ExceptionMatrixCheck',[]),('independent-authority','IndependentAuthorityCheck',[]),('independent-cancel','IndependentCancellationCheck',[]),('results','HostResultCheck',[]),('transitions','TransitionCheck',[]),('query-original','QueryResultRegression',[])]
for mode,cp in [('source',source),('production',prod)]:
 if mode=='production':
  fixture=D/'production-core';fixture.mkdir();run('core-production',[str(J/'java.exe'),'-Xmx256m','-cp',cp,'com.videokit.d1input.InputSinkCheck',str(fixture)],mode)
 for name,cls,args in plan:run(name+'-'+mode,[str(J/'java.exe'),'-Xmx256m','-cp',cp,'com.videokit.d1input.'+cls]+args,mode)
summary={'candidate':B.name,'frozenCandidate':seal.exists(),'sealSha256':sha(seal) if seal.exists() else None,'toolSha256':sha(Path(__file__)),'entryToolSha256':sha(B/'tools/local_check.py'),'productionJarSha256':sha(jar),'sourcePinsSha256':sha(D/'source/source-pins.json'),'runs':runs,'allOriginalProcessesReturned':True,'independentVerdict':'NOT_IMPLIED_BY_RUNNING_CODER_CHECKS','preFreezeRun':'CODER_SELF_CHECK' if not seal.exists() else None,'deviceSdkFieldOperations':0}
(D/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print('READ_ONLY_REVIEW_EXECUTION_COMPLETE; independent verdict not implied',flush=True)
