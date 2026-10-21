package com.videokit.d1android;
import com.videokit.d1input.HostMp4Inspection;import androidx.media3.common.C;import java.io.*;
/** Compare ACTUAL Media3 output with frozen independent file facts, never fill observations. */
public final class QualifiedObservation {
 public static String csdHash(HostMp4Inspection.Track t)throws IOException {
  ByteArrayOutputStream out=new ByteArrayOutputStream();
  for(byte[] b:t.format.initializationData){if(b.length<5||b.length>65536-out.size()||b[0]!=0||b[1]!=0||b[2]!=0||b[3]!=1)throw new IOException("QUALIFIED_CSD_REPRESENTATION");out.write(b,0,b.length);}
  return VerifiedFixtureCopy.hash(out.toByteArray());
 }
 public static void require(HostMp4Inspection.Evidence e,boolean original)throws IOException {
  ExperimentContract.QualifiedFixture q=ExperimentContract.qualifiedFixture();
  if(e==null||!e.fullReadEof||!e.extractorEof||!e.sniffMatched||!e.peekReset||!e.endTracksObserved||!e.extractorReleaseReturned()||!e.dataSourceCloseReturned()||e.tracks.size()!=1)throw new IOException("QUALIFIED_OBSERVATION_INCOMPLETE");
  if(original&&(e.bytes!=q.bytes||!e.sha256.equals(q.sha256)))throw new IOException("QUALIFIED_FILE_MISMATCH");
  HostMp4Inspection.Track t=e.tracks.get(0);
  if(t.type!=C.TRACK_TYPE_VIDEO||!"video/avc".equals(t.format.sampleMimeType)||t.format.width!=256||t.format.height!=144||t.format.rotationDegrees!=0||t.format.drmInitData!=null||t.samples.size()!=6)throw new IOException("QUALIFIED_CAPTURE_FORMAT");
  if(!csdHash(t).equals(q.csdHashes.get(0)))throw new IOException("QUALIFIED_CSD_MISMATCH");
  for(int i=0;i<6;i++){HostMp4Inspection.Sample s=t.samples.get(i);if(s.timeUs!=q.pts.get(i)||!supportedFlags(s.flags,i)||s.size!=q.sizes.get(i)||!s.sha256.equals(q.sampleHashes.get(i)))throw new IOException("QUALIFIED_SAMPLE_MISMATCH");}
  if(e.durationUs!=1200000&&t.reportedDurationUs!=1200000)throw new IOException("ACTUAL_EOS_DURATION_NOT_PROVEN");
 }
 /** Raw extractor flags stay in receipts. LAST_SAMPLE is a Media3 marker, not a host key boolean. */
 public static boolean supportedFlags(int raw,int index){int allowed=C.BUFFER_FLAG_KEY_FRAME|C.BUFFER_FLAG_LAST_SAMPLE;return (raw&C.BUFFER_FLAG_KEY_FRAME)!=0&&(raw&~allowed)==0&&((raw&C.BUFFER_FLAG_LAST_SAMPLE)==0||index==5);}
 private QualifiedObservation(){}
}
