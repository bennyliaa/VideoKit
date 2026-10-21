package com.videokit.d1android;
import java.io.IOException;import java.util.*;
/** Exact benign experiment inputs; no external path/URL, encoder selection or execution permit. */
public final class ExperimentContract {
 public static final String APP="com.videokit.d1media3.android01",TEST=APP+".test",PROCESS=APP+":media3";
 public static final String RUNNER=TEST+".Media3Instrumentation",VERSION="D1-MEDIA3-ANDROID01-READY";
 public static final String SAMPLE_SHA="720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9";
 public static final int SAMPLE_BYTES=349102,RECEIPT_UTF8_MAX=262144;
 public static final long METHOD_DEADLINE_MS=60000;
 public enum Method {
  inspectKnown(65536,false,-1),inspectShort3(3,false,-1),inspectUnknown(65536,true,-1),inspectSeek1s(65536,false,1000000),preopenAdmission(65536,false,-1),muxQualified(65536,false,-1);
  public final int chunk;public final boolean unknown;public final long seekUs;
  Method(int c,boolean u,long s){chunk=c;unknown=u;seekUs=s;}
 }
 public static Method admit(Map<String,String> args)throws IOException {
  if(!args.keySet().equals(Set.of("case","fixtureSha256","runId"))||!SAMPLE_SHA.equals(args.get("fixtureSha256"))||args.get("runId")==null||!args.get("runId").matches("D1MA01-[A-Z0-9_-]{1,32}"))throw new IOException("EXPERIMENT_ARGUMENT_REJECTED");
  try{return Method.valueOf(args.get("case"));}catch(RuntimeException bad){throw new IOException("EXPERIMENT_METHOD_REJECTED");}
 }
 /** Empty registry is deliberate: approved320x180+AAC cannot be used as AVC6.
  * A future reviewed candidate must embed its exact qualified manifest and asset;
  * runtime arguments cannot register a fixture. No hashes/CSD are invented here. */
 public static final class QualifiedFixture {
  public final String asset,sha256;public final int bytes;public final List<String> csdHashes,sampleHashes;public final List<Integer> sizes,flags;public final List<Long> pts;
  private QualifiedFixture(String asset,String sha,int bytes,List<String> csd,List<String> hashes,List<Integer> sizes,List<Integer> flags,List<Long> pts){
   if(!"qualified-six-avc.mp4".equals(asset)||sha==null||!sha.matches("[0-9a-f]{64}")||SAMPLE_SHA.equals(sha)||bytes<1||bytes>8388608||csd.isEmpty()||hashes.size()!=6||sizes.size()!=6||flags.size()!=6||pts.size()!=6)throw new IllegalArgumentException("QUALIFIED_MANIFEST_INCOMPLETE");
   for(int i=0;i<6;i++)if(pts.get(i)!=i*200000L||sizes.get(i)<1||sizes.get(i)>262144||!hashes.get(i).matches("[0-9a-f]{64}"))throw new IllegalArgumentException("QUALIFIED_MANIFEST_INVALID");
   for(String hash:csd)if(!hash.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("QUALIFIED_CSD_INVALID");
   this.asset=asset;sha256=sha;this.bytes=bytes;csdHashes=List.copyOf(csd);sampleHashes=List.copyOf(hashes);this.sizes=List.copyOf(sizes);this.flags=List.copyOf(flags);this.pts=List.copyOf(pts);
  }
 }
 private static final QualifiedFixture QUALIFIED=null;
 public static QualifiedFixture qualifiedFixture(){return QUALIFIED;}
 private ExperimentContract(){}
}
