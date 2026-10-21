"""Copy only reviewed source/dependency inputs into the isolated feasibility candidate."""
from pathlib import Path
import re, shutil, hashlib, json
R=Path('D:/CodexProjects/VideoKit').resolve(); B=(R/'docs/coder/d1render01').resolve()
records=[]
def copy(src,dst):
    s=R/src;d=B/dst;d.parent.mkdir(parents=True,exist_ok=True)
    if d.exists():assert d.read_bytes()==s.read_bytes(), 'never overwrite edited candidate: '+dst
    else:shutil.copyfile(s,d)
    records.append({'source':src,'destination':dst,'sha256':hashlib.sha256(s.read_bytes()).hexdigest()})
C=R/'docs/coder/d1c14'
available={p.stem:p for folder in ['src','android'] for p in (C/folder/'com/videokit/spike/c14').glob('*.java')}
todo=['CpuTaskClient','CpuIsolatedService']; selected=set()
while todo:
    name=todo.pop()
    if name in selected:continue
    selected.add(name);t=available[name].read_text(encoding='utf-8-sig')
    todo.extend(n for n in available if n not in selected and re.search(r'\b'+re.escape(n)+r'\b',t))
for n in sorted(selected):
    src=available[n]
    # The revised bridge adds graceful original-executor termination without altering CPU protocol.
    f=R/'docs/coder/d1e13f/upstream-c14/src/com/videokit/spike/c14'/src.name
    if n in {'AsyncReadBridge','LeaseRegistry','HostFixtures','SourceAdmission'} and f.exists():src=f
    copy(src.relative_to(R).as_posix(),'upstream/com/videokit/spike/c14/'+src.name)
for n in ['E13SourceGroup']:
    copy('docs/coder/d1e13f/src/com/videokit/spike/e4/'+n+'.java','upstream/com/videokit/spike/e4/'+n+'.java')
for n in ['E13BindingOwner','E13FinishOwner','E13ReturnEvents','E13Stages']:
    copy('docs/coder/d1e13f/binding/com/videokit/spike/e4/'+n+'.java','upstream/com/videokit/spike/e4/'+n+'.java')
for n in ['gradlew.bat','gradle.properties','local.properties','build.gradle.kts','app/gradle.lockfile','gradle/libs.versions.toml','gradle/wrapper/gradle-wrapper.jar','gradle/wrapper/gradle-wrapper.properties']:
    copy('docs/coder/d1e13f/'+n,n)
for p in sorted((C/'native-libs/arm64-v8a').glob('*.so')):copy(p.relative_to(R).as_posix(),'native-libs/arm64-v8a/'+p.name)
for p in sorted((C/'notice-assets').rglob('*')):
    if p.is_file():copy(p.relative_to(R).as_posix(),'notice-assets/'+p.relative_to(C/'notice-assets').as_posix())
(B/'evidence').mkdir(exist_ok=True)
(B/'evidence/reused-inputs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cpu_source_files':len(selected),'reused_files':len(records),'native_rebuilds':0}))
