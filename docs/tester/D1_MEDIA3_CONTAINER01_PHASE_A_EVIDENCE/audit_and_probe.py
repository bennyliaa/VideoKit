from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,subprocess,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink05';E=Path(__file__).resolve().parent;J=Path('D:/Android/Android Studio/jbr/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
seal=B/'evidence/input-sink05-freeze.json';assert sha(seal)=='ec7e5e9a8f38d2d1fe531592117f5db0a6d3481cd3ff89536d985f9dae173d96'
for row in load(seal)['files']:assert sha(R/row['path'])==row['sha256']
report=R/'docs/tester/D1_INPUT_SINK05_FIX_REVIEW_REPORT_V1.0.md';assert sha(report)=='6cd4621901dddcc9ad7d11ddca4248eaac2a1ae7e45513ca257a35055f1b6973'
sourceInputs=load(B/'evidence/final-source-dependency-inputs.json');inputMap={x['path']:x for x in sourceInputs}
for row in sourceInputs:assert sha(B/row['path'])==row['sha256']
snapshots=[]
for p in [R/'docs/milestones/D1_MEDIA3_CONTAINER01_TESTER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_MEDIA3_CONTAINER01_CODER_REQUIREMENTS_V1.0.md',B/'upstream/com/videokit/spike/c14/E6Muxer.java',B/'src/com/videokit/d1input/MatureMuxerBinding.java',B/'src/com/videokit/d1input/TemporaryOutput.java',B/'src/com/videokit/d1input/HostDataSource.java',B/'src/com/videokit/d1input/HostInputFactory.java']:
 snapshots.append(dict(path=p.relative_to(R).as_posix(),sha256=sha(p),bytes=p.stat().st_size));d=E/'source-snapshots'/p.name;d.parent.mkdir(exist_ok=True);d.write_bytes(p.read_bytes())
(E/'source-pins.json').write_text(json.dumps(snapshots,indent=2),encoding='utf8')
pins={}
for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter():
 if c.tag.split('}')[-1]=='component':
  coord=':'.join(c.get(k) for k in ['group','name','version'])
  for a in c:
   if a.tag.split('}')[-1]=='artifact':pins[(coord,a.get('name'))]={x.get('value') for x in a if x.tag.split('}')[-1]=='sha256'}
L=E/'static-libs';L.mkdir(exist_ok=False);libs=[]
for module in ['common','container','decoder','extractor','muxer']:
 name='media3-'+module;folder=B/'offline-maven/androidx/media3'/name/'1.9.3';aar=folder/(name+'-1.9.3.aar');meta=folder/(name+'-1.9.3.module');coord='androidx.media3:'+name+':1.9.3'
 assert sha(aar) in pins[(coord,aar.name)] and sha(meta) in pins[(coord,meta.name)]
 for p in [aar,meta]:assert sha(p)==inputMap[p.relative_to(B).as_posix()]['sha256']
 m=load(meta);declared={f['name']:f['sha256'] for v in m['variants'] for f in v.get('files',[]) if f['name'].endswith('.aar')};assert declared[aar.name]==sha(aar)
 dest=L/(name+'.jar')
 with zipfile.ZipFile(aar) as z:dest.write_bytes(z.read('classes.jar'));licenseNames=[n for n in z.namelist() if any(s in n.upper() for s in ['LICENSE','NOTICE'])]
 libs.append(dict(coordinate=coord,source=aar.relative_to(R).as_posix(),aarSha256=sha(aar),moduleSha256=sha(meta),classesJarSha256=sha(dest),officialPomInFrozenMirror=(folder/(name+'-1.9.3.pom')).exists(),inRuntime15=module in ['common','container','muxer'],runtimeUse='ALREADY_ADMITTED_BASELINE' if module in ['common','container','muxer'] else 'STATIC_ABI_ONLY_NEW_USE_REVIEW_PENDING',aarLicenseEntries=licenseNames))
(E/'sealed-library-identities.json').write_text(json.dumps(libs,indent=2),encoding='utf8')
def run(name,argv):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);(E/(name+'.stdout')).write_bytes(p.stdout);(E/(name+'.stderr')).write_bytes(p.stderr);(E/(name+'.json')).write_text(json.dumps(dict(argv=argv,startUtc=start,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exitCode=p.returncode,originalProcessReturned=True),indent=2),encoding='utf8');assert p.returncode==0,p.stderr.decode('utf8','replace');return p
staticCP=';'.join(str(p) for p in sorted(L.glob('*.jar')))+ ';'+str(B/'deps/media3-datasource.jar')
api=['androidx.media3.datasource.DataSource','androidx.media3.datasource.DataSpec','androidx.media3.extractor.Extractor','androidx.media3.extractor.ExtractorInput','androidx.media3.extractor.DefaultExtractorInput','androidx.media3.extractor.ExtractorOutput','androidx.media3.extractor.TrackOutput','androidx.media3.extractor.SeekMap','androidx.media3.extractor.PositionHolder','androidx.media3.extractor.mp4.Mp4Extractor','androidx.media3.extractor.mp4.FragmentedMp4Extractor','androidx.media3.muxer.FragmentedMp4Muxer','androidx.media3.muxer.FragmentedMp4Muxer$Builder','androidx.media3.muxer.BufferInfo']
for i,cls in enumerate(api):run('abi-'+str(i).zfill(2),[str(J/'javap.exe'),'-classpath',staticCP,'-public','-constants',cls])
run('muxer-bytecode',[str(J/'javap.exe'),'-classpath',staticCP,'-c','-p','androidx.media3.muxer.FragmentedMp4Muxer'])
C=E/'probe-classes';C.mkdir(exist_ok=False);prod=B/'artifacts/input-sink05-classes.jar';cp=';'.join([str(C),str(prod)]+[str(p) for p in sorted((B/'deps').glob('*.jar'))])
# Existing frozen Android URI JVM port only; no new platform or Media3 standins.
run('probe-compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),str(E/'BaselineMuxerProbe.java'),str(B/'platform-fixtures/android/net/Uri.java')])
p=run('probe-runtime',[str(J/'java.exe'),'-Xmx128m','-cp',cp,'BaselineMuxerProbe']);print(p.stdout.decode('utf8','replace'))
(E/'phase-a-audit.json').write_text(json.dumps(dict(result='FROZEN_BASELINE_REVIEW_COMPLETE',baselineSealSha256=sha(seal),baselineReportSha256=sha(report),frozenFilesVerified=828,inputPinsVerified=len(sourceInputs),abiClasses=len(api),extractorExecuted=False,GradleSdkDeviceNetworkCalls=0,noFloatingCandidateRead=True),indent=2),encoding='utf8');print('PASS identity/real ABI inspection; new extractor NOT EXECUTED; phase A only')
