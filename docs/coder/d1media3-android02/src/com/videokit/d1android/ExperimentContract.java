package com.videokit.d1android;
import java.io.IOException;import java.util.*;
/** Exact benign experiment inputs; no external path/URL, encoder selection or execution permit. */
public final class ExperimentContract {
 public static final String APP="com.videokit.d1media3.android02",TEST=APP+".test",PROCESS=APP+":media3";
 public static final String RUNNER=TEST+".Media3Instrumentation",VERSION="D1-MEDIA3-ANDROID02-CONTAINER";
 public static final String SAMPLE_SHA="720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9";
 public static final int SAMPLE_BYTES=349102,RECEIPT_UTF8_MAX=262144;
 public static final long METHOD_DEADLINE_MS=60000;
 public enum Method {
  inspectKnown(65536,false,-1),inspectShort3(3,false,-1),inspectUnknown(65536,true,-1),inspectSeek1s(65536,false,1000000),preopenAdmission(65536,false,-1),muxQualified(65536,false,-1),rejectFixture(65536,false,-1),cancelLateRead(65536,false,-1),writerPending(65536,false,-1),bbbObserve(65536,false,-1);
  public final int chunk;public final boolean unknown;public final long seekUs;
  Method(int c,boolean u,long s){chunk=c;unknown=u;seekUs=s;}
 }
 public static Method admit(Map<String,String> args)throws IOException {
  if(!args.keySet().equals(Set.of("case","fixtureSha256","runId"))||!QUALIFIED.sha256.equals(args.get("fixtureSha256"))||args.get("runId")==null||!args.get("runId").matches("D1MA02-[A-Z0-9_-]{1,32}"))throw new IOException("EXPERIMENT_ARGUMENT_REJECTED");
  try{return Method.valueOf(args.get("case"));}catch(RuntimeException bad){throw new IOException("EXPERIMENT_METHOD_REJECTED");}
 }
 /** Only the exact independently qualified synthetic asset is registered. BBB remains observation-only. */
 public static final class QualifiedFixture {
  public final String asset,sha256;public final int bytes;public final List<String> csdHashes,sampleHashes;public final List<Integer> sizes,flags;public final List<Long> pts;
  private QualifiedFixture(String asset,String sha,int bytes,List<String> csd,List<String> hashes,List<Integer> sizes,List<Integer> flags,List<Long> pts){
   if(!"qualified-six-avc.mp4".equals(asset)||sha==null||!sha.matches("[0-9a-f]{64}")||SAMPLE_SHA.equals(sha)||bytes<1||bytes>8388608||csd.isEmpty()||hashes.size()!=6||sizes.size()!=6||flags.size()!=6||pts.size()!=6)throw new IllegalArgumentException("QUALIFIED_MANIFEST_INCOMPLETE");
   for(int i=0;i<6;i++)if(pts.get(i)!=i*200000L||sizes.get(i)<1||sizes.get(i)>262144||!hashes.get(i).matches("[0-9a-f]{64}"))throw new IllegalArgumentException("QUALIFIED_MANIFEST_INVALID");
   for(String hash:csd)if(!hash.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("QUALIFIED_CSD_INVALID");
   this.asset=asset;sha256=sha;this.bytes=bytes;csdHashes=List.copyOf(csd);sampleHashes=List.copyOf(hashes);this.sizes=List.copyOf(sizes);this.flags=List.copyOf(flags);this.pts=List.copyOf(pts);
  }
 }
 private static final QualifiedFixture QUALIFIED=new QualifiedFixture("qualified-six-avc.mp4","19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c",8849,
  List.of("f6dcad95142c58fce67217fc175449c88b9c697f07db35952c617a66199e75a8"),
  List.of("299447d41af824c07d904ddf424063922e4546edb29d01b0b32e4f3a4e84433f","05f0f4e598823343f8d021b3aa2c62c1a6ca5e9e6446e46b3eff737a3f44709c","01905769af8def741f27e914901dd27767e0faa351874cbb0d9b75bb6d7df2dc","21ab0d10a58ca53b72c1a01eb5ca9014094ca1afd63011e861973ebf27d14032","71c19f10000d2fa907b705369e2c55e147702a841eda326cdcd5ba6feedddaae","ba1f530d497d0c40a9402768be6a0dfcd3ba19b690b5a561218ddf8e5a3f3500"),
  List.of(1340,1340,1340,1340,1340,1340),List.of(1,1,1,1,1,1),List.of(0L,200000L,400000L,600000L,800000L,1000000L));
 public static QualifiedFixture qualifiedFixture(){return QUALIFIED;}
 private ExperimentContract(){}
}
