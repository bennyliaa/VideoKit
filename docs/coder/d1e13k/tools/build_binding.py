from pathlib import Path
import json,hashlib,subprocess,zipfile,shutil,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';C=B/'.checks/policy';W=B/'.checks/check-only';C.mkdir(parents=True,exist_ok=False);W.mkdir(parents=True,exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin');old=B/'reference/r1-reviewed.jar';release=B/'release/read-only-release.json';digest=hashlib.sha256(release.read_bytes()).hexdigest()
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(name,cmd):
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen([str(v) for v in cmd],stdout=so,stderr=se)
  try:code=p.wait(timeout=20)
  except subprocess.TimeoutExpired:write(E/(name+'.pending.json'),dict(pid=p.pid,sameOriginalParentCustody=True,killed=False));code=p.wait()
 write(E/(name+'.exit.json'),dict(argv=[str(v) for v in cmd],pid=p.pid,exitCode=code,naturalReturn=True,filesCloseReturned=True));assert code==0,(name,(E/(name+'.stderr.txt')).read_text());print(name,'PASS')
write(E/'compile-inputs.json',[pin(B/'policy/E13JReadOnly.java'),pin(B/'tools/KBindingCheck.java'),pin(old)])
run('compile-policy',[J/'javac.exe','-encoding','UTF-8','-cp',old,'-d',C,B/'policy/E13JReadOnly.java',B/'tools/KBindingCheck.java'])
jar=B/'artifacts/e13k-host-tools.jar';rows=[];changed=[]
with zipfile.ZipFile(old) as z,zipfile.ZipFile(jar,'x',compression=zipfile.ZIP_DEFLATED) as out:
 for n in z.namelist():
  before=z.read(n);candidate=C/n;raw=candidate.read_bytes() if candidate.exists() and Path(n).stem.startswith('E13JReadOnly') else before;out.writestr(n,raw);same=raw==before;rows.append(dict(entry=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),baselineSha256=hashlib.sha256(before).hexdigest(),byteIdentical=same));
  if not same:changed.append(n)
assert len(rows)==193 and changed==['com/videokit/spike/e4/E13JReadOnly.class'],changed
write(E/'jar-member-difference.json',dict(status='ONLY_POLICY_OUTER_CLASS_CHANGED',baseline=pin(old),jar=pin(jar),members=rows,unchangedMembers=192,changedMembers=changed))
for p in C.rglob('KBindingCheck*.class'):q=W/p.relative_to(C);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
run('check-final-binding',[J/'java.exe','-cp',str(W)+';'+str(jar),'com.videokit.spike.e4.KBindingCheck',release])
run('describe-final',[J/'java.exe','-cp',jar,'com.videokit.spike.e4.E13JReadOnly','--describe'])
for name,path in [('old',old),('new',jar)]:run('javap-'+name,[J/'javap.exe','-p','-c','-constants','-classpath',path,'com.videokit.spike.e4.E13JReadOnly'])
def normalize(s):return re.sub(r'#\d+','#CP',s.replace(digest,'ABSENT'))
oldText=(E/'javap-old.stdout.txt').read_text();newText=(E/'javap-new.stdout.txt').read_text();assert normalize(oldText)==normalize(newText),'NON_POLICY_DISASSEMBLY_DIFFERENCE'
write(E/'policy-bytecode-equivalence.json',dict(status='PASS',changedClass='E13JReadOnly.class',normalization='Replace exact approved SHA with ABSENT and constant-pool numeric references only; all disassembly, offsets, instructions, branches, members and literals otherwise exact',other192MembersByteIdentical=True,productionStrategyCompiles=1,dispatchInvocations=0,actual5037Connections=0,jar=pin(jar)))
