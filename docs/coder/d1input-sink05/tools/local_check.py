from pathlib import Path
import hashlib,json,subprocess,sys,datetime,re
B=Path(__file__).resolve().parents[1]
match=re.fullmatch(r'd1input-sink([0-9]{2})',B.name);assert match,'CANDIDATE_DIRECTORY_REQUIRED'
number=match.group(1);project=B.parents[2].resolve();reviewRoot=project/'docs/tester'/('D1_INPUT_SINK'+number+'_REVIEW_EVIDENCE')
assert reviewRoot.resolve()==reviewRoot,'REVIEW_ROOT_REDIRECTION_REJECTED'
seal=B/'evidence'/('input-sink'+number+'-freeze.json')
assert len(sys.argv)>=2,'ATTEMPT_OR_REVIEW_OUTPUT_REQUIRED'
if sys.argv[1]=='--print-review-root':
 print(reviewRoot);sys.exit(0)
review=sys.argv[1]=='--review-output'
if review:
 assert len(sys.argv)==3,'REVIEW_OUTPUT_ARGUMENT_REQUIRED'
 raw=Path(sys.argv[2]);assert raw.is_absolute() and raw.drive.casefold()==B.drive.casefold(),'ABSOLUTE_LOCAL_REVIEW_PATH_REQUIRED'
 D=raw.resolve()
 try:relative=D.relative_to(reviewRoot)
 except ValueError:raise AssertionError('INDEPENDENT_TESTER_ROOT_ONLY') from None
 assert relative.parts,'NEW_REVIEW_SUBDIRECTORY_REQUIRED'
else:
 assert len(sys.argv)==2 and re.fullmatch(r'[0-9]{3}',sys.argv[1]),'LOCAL_ATTEMPT_REQUIRED'
 assert not seal.exists(),'FROZEN_USE_INDEPENDENT_REVIEW_OUTPUT'
 D=B/'evidence'/('local-'+sys.argv[1])
sources=sorted(p for folder in ['src','upstream','checks','platform-fixtures'] for p in (B/folder).rglob('*.java'))
sources.append(B/'android/com/videokit/d1input/PlatformOutputErrors.java')
pins=[{'path':p.relative_to(B).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]
if review and seal.exists():
 frozen={x['path']:x['sha256'] for x in json.loads(seal.read_text())['files']}
 for p in pins:assert frozen[(B/p['path']).relative_to(project).as_posix()]==p['sha256'],'FROZEN_SOURCE_MISMATCH'
D.mkdir(parents=True,exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin')
(D/'source-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
(D/'review-context.json').write_text(json.dumps({'candidate':B.name,'candidateFrozen':seal.exists(),'reviewMode':review,'allowedReviewRoot':str(reviewRoot),'output':str(D),'scope':'JDK-only execution; no independent verdict implied; unfrozen run is coder self-check'},indent=2),encoding='utf-8')
classes=D/'classes';classes.mkdir();args=D/'javac.args';args.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources),encoding='utf-8')
cp=';'.join(p.as_posix() for p in sorted((B/'deps').glob('*.jar')))
def run(name,argv):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(D/(name+'.stdout')).write_bytes(p.stdout);(D/(name+'.stderr')).write_bytes(p.stderr);(D/(name+'.json')).write_text(json.dumps({'argv':argv,'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':p.returncode,'originalProcessReturned':True},indent=2),encoding='utf-8');print(p.stdout.decode('utf-8',errors='replace'));print(p.stderr.decode('utf-8',errors='replace'));assert p.returncode==0
run('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(classes),'@'+str(args)])
run('checks',[str(J/'java.exe'),'-Xmx256m','-cp',str(classes)+';'+cp,'com.videokit.d1input.InputSinkCheck',str(D)])

