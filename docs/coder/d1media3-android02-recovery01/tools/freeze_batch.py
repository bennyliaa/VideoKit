from pathlib import Path
import datetime,json,hashlib,zipfile
from review_materials import B,R,E,MAIN,ZIP,SEAL,selected,sha,inputs
assert not SEAL.exists() and not ZIP.exists()
result=inputs();paths=selected();rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in paths:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None and len(z.namelist())==len(rows)
 for x in rows:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
archive={'path':ZIP.relative_to(R).as_posix(),'bytes':ZIP.stat().st_size,'sha256':sha(ZIP)}
seal={'frozenUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_BUILT_OFFLINE_WITH_KNOWN_OBSERVATION_GAPS_PENDING_REVIEW','files':rows,'archive':archive,'validation':result,'excludedInfrastructure':['.gradle','build','app/build except actual86 javac classes','recovery-gradle-home','offline-maven'],'exclusionNote':'Actual raw owner/client/daemon logs, strict metadata audit and source/classes/JAR/DEX/APKs preserved. Excluded cache/mirror are not results; verifier checks actual300 artifact pins against retained local mirror without mutation.','noExecutionPermitIssued':True}
SEAL.write_text(json.dumps(seal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'seal':str(SEAL),'sealSha256':sha(SEAL),'sealedFiles':len(rows),'archive':archive,'selectedBytes':sum(x['bytes'] for x in rows),'validation':result},ensure_ascii=False))
