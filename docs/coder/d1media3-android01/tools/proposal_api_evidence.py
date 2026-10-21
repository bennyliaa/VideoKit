from pathlib import Path
import zipfile,hashlib,json
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/media3-android01-freeze.json').exists();D=B/'reference/generation-proposal-source'
with zipfile.ZipFile(D/'jcodec-0.2.5-sources.jar') as z:
 for n in ['org/jcodec/containers/mp4/muxer/MP4Muxer.java','org/jcodec/containers/mp4/muxer/CodecMP4MuxerTrack.java','org/jcodec/codecs/h264/encode/DumbRateControl.java','org/jcodec/common/model/Packet.java','org/jcodec/common/io/SeekableByteChannel.java']:(D/Path(n).name).write_bytes(z.read(n))
J=Path('D:/Android/Android Studio/jbr');files=[J/'release',J/'bin/java.exe',J/'bin/javac.exe'];rows=[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
(D/'proposed-compiler-identity.json').write_text(json.dumps({'proposalOnly':True,'alreadyUsedProjectJdk':True,'generationExecuted':False,'files':rows,'release':(J/'release').read_text()},indent=2));print(json.dumps(rows,indent=2))
