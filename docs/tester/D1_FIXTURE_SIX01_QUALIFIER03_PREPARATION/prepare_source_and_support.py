from pathlib import Path
import json,hashlib,zipfile,ast,struct
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;PRE=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER02_FIX_PREPARATION';OLD=R/'docs/coder/d1fixture-tool02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=PRE/'review-evidence-manifest.json';assert sha(manifest)=='2a0a2f9143121a1b1be9221f6f01d2960f2f3a926884bf8841f09336098da90e'
m=json.loads(manifest.read_text());assert sha(R/m['report'])==m['reportSha256']
for x in m['evidenceFiles']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
jar=OLD/'artifacts/videokit-fixture-tool02.jar';assert sha(jar)=='c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd'
SUP=E/'support';SUP.mkdir(exist_ok=False)
tree=ast.parse((R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent_static_audit.py').read_text());fs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='classInfo'];exec(compile(ast.Module(body=fs,type_ignores=[]),'static_class_parser_only','exec'))
rows=[]
with zipfile.ZipFile(jar) as z:
 names=[n for n in z.namelist() if n.endswith('.class') and any(n==f'com/videokit/fixturetool/{base}.class' or n.startswith(f'com/videokit/fixturetool/{base}$') for base in ['WorkerDeadline','ReceiptJson'])]
 assert set(names)=={'com/videokit/fixturetool/WorkerDeadline.class','com/videokit/fixturetool/ReceiptJson.class'}
 for n in names:
  b=z.read(n);p=SUP/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);info=classInfo(b);assert info['major']==55 and info['sourceFile'] in ['WorkerDeadline.java','ReceiptJson.java'];src=OLD/'driver/com/videokit/fixturetool'/info['sourceFile'];rows.append(dict(path=str(p),jarEntry=n,bytes=len(b),sha256=sha(p),classInfo=info,sourcePath=str(src),sourceSha256=sha(src)))
assert not list(SUP.rglob('*.java')) and len(list(SUP.rglob('*.class')))==2
policy=(PRE/'DataReferencePolicy.java').read_text().replace('DataReferencePolicy','DataReferencePolicy03')
policy=policy.replace('  out.put("drefContainerVersionFlagsAndDeclaredCount","UNPROVEN_DATAREFBOX_API_DISCARDS_ORIGINAL_FIELDS");','  Map<String,Object> original=ReceiptJson.map();out.put("originalDrefHeader",original);MetadataPolicy03.dref(refs,original);')
at=policy.index(' static void requireOriginalContainerMetadata');end=policy.index(' private DataReferencePolicy03()',at);policy=policy[:at]+policy[end:]
policy=policy.replace('JCodec0.2.5 DataBoxes/AliasBox/UrlBox/FullBox/Header APIs','0.2.5-videokit-observation01 original-parent + typed-child APIs')
(E/'DataReferencePolicy03.java').write_text(policy,encoding='utf8')
source=(PRE/'Six01ContainerQualifier02.java').read_text().replace('Six01ContainerQualifier02','Six01ContainerQualifier03').replace('SIX01_QUALIFIER02_FIX_PREPARED_WHOLE_METADATA_BLOCKED','SIX01_QUALIFIER03_PREPARED_NO_EXECUTION_AUTHORITY').replace('six01-qualifier02-original-readonly','six01-qualifier03-original-readonly')
source=source.replace('DataReferencePolicy.inspect','DataReferencePolicy03.inspect')
start=source.index('    // Mandatory original dref container');end=source.index('    AvcCBox avcc=',start);source=source[:start]+source[end:]
source=source.replace('volatile Map<String,Object> dataReferenceObservation;','volatile Map<String,Object> dataReferenceObservation;volatile Map<String,Object> metadataObservation;Map<String,Object> classOrigins;')
needle='    SampleEntry[] entries=track.getSampleEntries();'
source=source.replace(needle,'    metadataObservation=map();Map<String,Object> stsdObservation=map();metadataObservation.put("originalStsdHeader",stsdObservation);MetadataPolicy03.stsd(NodeBox.findFirstPath(trak,SampleDescriptionBox.class,Box.path("mdia.minf.stbl.stsd")),stsdObservation);\n'+needle)
needle='List<Map<String,Object>> config=csd(avcc);'
source=source.replace(needle,'Map<String,Object> avccObservation=map();metadataObservation.put("originalAvccHeader",avccObservation);MetadataPolicy03.avcc(avcc,avccObservation);List<Map<String,Object>> config=csd(avcc);')
source=source.replace('"framework","JCodec0.2.5 createRawMP4Demuxer"','"framework","JCodec0.2.5-videokit-observation01 createRawMP4Demuxer"')
source=source.replace('r.put("actualDataReferenceChildObservation",dataReferenceObservation);','r.put("actualDataReferenceChildObservation",dataReferenceObservation);r.put("actualOriginalMetadataObservation",metadataObservation);r.put("actualCodeSourceProof",classOrigins);')
source=source.replace('Job j=new Job(args[2].substring(8),args[0].substring(18),bytes);','Map<String,Object> sources=OriginFence03.futureRuntime(MP4Demuxer.class,MP4DemuxerTrack.class,MP4Util.class,H264Utils.class,NALUnit.class);Job j=new Job(args[2].substring(8),args[0].substring(18),bytes);j.classOrigins=sources;')
assert 'DataReferencePolicy.require' not in source and 'DataReferencePolicy.inspect' not in source and source.count('MetadataPolicy03.stsd(')==source.count('MetadataPolicy03.avcc(')==1 and source.count('OriginFence03.futureRuntime(')==1
(E/'Six01ContainerQualifier03.java').write_text(source,encoding='utf8')
(E/'support-and-source-provenance.json').write_text(json.dumps(dict(originalJarSha256=sha(jar),supportExactClassSet=rows,noJcodecOrJaadOrDriverClassesExtracted=True,supportRecompiled=False,baseHelperPath=str(PRE/'Six01ContainerQualifier02.java'),baseHelperSha256=sha(PRE/'Six01ContainerQualifier02.java'),newHelperSha256=sha(E/'Six01ContainerQualifier03.java'),newDrefPolicySha256=sha(E/'DataReferencePolicy03.java'),oldSourcesModified=False,mediaReads=0),indent=2),encoding='utf8')
print('SUPPORT2_EXTRACTED_EXACT; checker03 source prepared without compilation/media')
