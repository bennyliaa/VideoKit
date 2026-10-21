from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1]
# Metadata-only final review: expose volatile current IO phase and actual lowered test capacities.
p=B/'src/com/videokit/d1android/ScopeMeter.java';s=p.read_text().replace('root.put("inputLimit",INPUT)','root.put("inputLimit",inputLimit)').replace('root.put("outputLimit",OUTPUT)','root.put("outputLimit",outputLimit)');p.write_text(s,encoding='utf-8')
p=B/'instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java';s=p.read_text().replace('.put("stage",stage).put("currentCasePartial"','.put("stage",stage).put("currentIOPhase",ioPhase).put("currentCasePartial"');p.write_text(s,encoding='utf-8')
sources=sorted(p for n in ['src','android','upstream','instrumentation','app/src','instrumentation-assets','notice-assets','gradle'] for p in (B/n).rglob('*') if p.is_file())+[B/n for n in ['app/build.gradle.kts','app/gradle.lockfile','settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties']]
(B/'evidence/final-build-input-pins.json').write_text(json.dumps([{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],indent=2)+'\n',encoding='utf-8')
before=json.loads((B/'evidence/typed-001/source-pins.json').read_text());delta=[{'path':x['path'],'testedSha256':x['sha256'],'finalSha256':hashlib.sha256((B/x['path']).read_bytes()).hexdigest()} for x in before if hashlib.sha256((B/x['path']).read_bytes()).hexdigest()!=x['sha256']]
assert {x['path'] for x in delta}=={'src/com/videokit/d1android/ScopeMeter.java','instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java'}
(B/'evidence/post-typed-metadata-only-differences.json').write_text(json.dumps({'changes':delta,'scope':'Only receipt currentIOPhase and snapshot limit-value fields. No guard/counter/owner/journal/completion algorithm changed, typed36 not replayed. Full final Android compile covers these final field displays.','newTypedJvm':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('All final build inputs pinned; two final metadata display adjustments explicitly separated from typed36 source pins')
