from pathlib import Path
import zipfile,hashlib,json,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/media3-android01-freeze.json').exists();D=B/'reference/generation-proposal-source';src=D/'jcodec-0.2.5-sources.jar';data=src.read_bytes();assert hashlib.sha1(data).hexdigest()==(D/'jcodec-0.2.5-sources.jar.sha1').read_text().strip()
with zipfile.ZipFile(src) as z:
 assert not any(n.endswith(('.class','.so','.dll','.exe')) for n in z.namelist());selected=['org/jcodec/codecs/h264/H264Encoder.java','org/jcodec/codecs/h264/H264Utils.java','org/jcodec/common/model/Picture.java','org/jcodec/common/VideoEncoder.java','org/jcodec/api/SequenceEncoder.java','org/jcodec/api/transcode/SinkImpl.java']
 for name in selected:
  if name in z.namelist():(D/Path(name).name).write_bytes(z.read(name))
 print('SOURCE_ONLY',len(z.namelist()),'entries; no executable classes/native; SHA256',hashlib.sha256(data).hexdigest())
root=ET.parse(D/'jcodec-0.2.5.pom').getroot();ns={'m':'http://maven.apache.org/POM/4.0.0'};licenses=[{c.tag.split('}')[-1]:c.text for c in x} for x in root.findall('m:licenses/m:license',ns)];deps=[{c.tag.split('}')[-1]:c.text for c in x} for x in root.findall('m:dependencies/m:dependency',ns)]
record={'proposalOnly':True,'currentExecutionAuthorized':False,'coordinate':'org.jcodec:jcodec:0.2.5','officialBase':'https://repo.maven.apache.org/maven2/org/jcodec/jcodec/0.2.5/','sourceArchiveBytes':len(data),'sourceArchiveSha256':hashlib.sha256(data).hexdigest(),'sourceArchiveOfficialSha1':hashlib.sha1(data).hexdigest(),'executableEntries':0,'licenses':licenses,'declaredDependencies':deps,'binaryEncoderDownloaded':False,'addedToGradleOrAPK':False,'builtOrLoadedOrEncoded':False,'futureToolBinaryHash':'NOT_BUILT_NOT_INVENTED; exact approved source/compiler recipe must be built and frozen in a later authorized batch before generation'}
(D/'proposal-source-identity.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(record,ensure_ascii=False,indent=2))
