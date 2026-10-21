package com.videokit.fixturetool;
import java.io.IOException;import java.nio.ByteBuffer;import java.util.*;
import org.jcodec.containers.mp4.BoxFactory;import org.jcodec.containers.mp4.boxes.*;import org.jcodec.codecs.h264.mp4.AvcCBox;

/** Bounded own metadata constructions through mature parse, no media parser. */
public final class Qualifier03PolicyCheck {
 static int cases,payload;static long start;static List<Object> receipts=new ArrayList<>();static Map<String,Object> lastObservation;
 interface Action {Map<String,Object> run()throws Exception;}
 static void guard(){long elapsed=System.nanoTime()-start;if(elapsed<0||elapsed>=5000000000L)throw new AssertionError("POLICY_WINDOW_UNKNOWN");}
 static ByteBuffer buffer(int n){if(n<0||payload>6144-n)throw new AssertionError("POLICY_PAYLOAD_LIMIT");payload+=n;return ByteBuffer.allocate(n);}
 static void positive(String name,Action action)throws Exception{guard();Map<String,Object> actual=action.run();Map<String,Object> r=ReceiptJson.map("case",name,"result","PASS_POLICY_ACCEPT","actual",actual);receipts.add(r);System.out.println(ReceiptJson.json(r));cases++;}
 static void negative(String name,String expected,Action action)throws Exception{guard();lastObservation=null;try{action.run();throw new AssertionError("UNSAFE_ACCEPT_"+name);}catch(IOException e){if(!expected.equals(e.getMessage()))throw new AssertionError("WRONG_POLICY_REJECTION_"+name+"_"+e.getMessage(),e);Map<String,Object> r=ReceiptJson.map("case",name,"result","PASS_POLICY_REJECT","actualReason",e.getMessage(),"actualPartialObservation",lastObservation);receipts.add(r);System.out.println(ReceiptJson.json(r));cases++;}}
 static AliasBox alias(int version,int flags){AliasBox b=AliasBox.createSelfRef();b.setVersion((byte)version);b.setFlags(flags);return b;}
 static UrlBox url(int flags,String value){UrlBox u=UrlBox.createUrlBox(value);u.setFlags(flags);return u;}
 static Box free(){return Box.createLeafBox(Header.createHeader("free",8),buffer(0));}
 static NodeBox parent(String kind,int word,int declared,int tail,Box...children)throws Exception {
  ByteBuffer input=buffer(128);input.putInt(word).putInt(declared);for(Box child:children)child.write(input);for(int j=0;j<tail;j++)input.put((byte)7);input.flip();
  NodeBox parsed=(NodeBox)BoxFactory.getDefault().newBox(Header.createHeader(kind,input.remaining()+8));parsed.parse(input);return parsed;
 }
 static DataRefBox dref(int word,int declared,int tail,Box...children)throws Exception{return (DataRefBox)parent("dref",word,declared,tail,children);}
 static SampleDescriptionBox stsd(int word,int declared,int tail,Box...children)throws Exception{return (SampleDescriptionBox)parent("stsd",word,declared,tail,children);}
 static Map<String,Object> checkD(DataRefBox b,short index)throws Exception{Map<String,Object> m=ReceiptJson.map();lastObservation=m;DataReferencePolicy03.inspect(b,index,m);return m;}
 static Map<String,Object> checkS(SampleDescriptionBox b)throws Exception{Map<String,Object> m=ReceiptJson.map();lastObservation=m;MetadataPolicy03.stsd(b,m);return m;}
 static Map<String,Object> checkA(AvcCBox b)throws Exception{Map<String,Object> m=ReceiptJson.map();lastObservation=m;MetadataPolicy03.avcc(b,m);return m;}
 static AvcCBox avcc(int version,int lengthByte,int spsByte,int tail)throws Exception {
  // Only own finite metadata with the previously frozen approved CSD payloads;
  // not bytes read from MP4, no effective media/decoder validity claim.
  int[] known={1,66,0,40,255,225,0,8,103,66,0,40,244,8,9,136,1,0,4,104,206,56,128};ByteBuffer input=buffer(known.length+tail);for(int j=0;j<known.length;j++)input.put((byte)(j==0?version:j==4?lengthByte:j==5?spsByte:known[j]));for(int j=0;j<tail;j++)input.put((byte)7);input.flip();AvcCBox b=new AvcCBox(Header.createHeader("avcC",8+input.remaining()));b.parse(input);return b;
 }
 public static Map<String,Object> runCases()throws Exception {
  start=System.nanoTime();Map<String,Object> origins=OriginFence03.metadata();System.out.println(ReceiptJson.json(ReceiptJson.map("actualClassOrigins",origins)));
  positive("dref_alias_original_and_child",()->checkD(dref(0,1,0,alias(0,1)),(short)1));
  positive("dref_url_original_and_child",()->checkD(dref(0,1,0,url(1,null)),(short)1));
  // This is only the stsd original-header policy: the full checker separately
  // requires real VideoSampleEntry avc1/256x144/dref1; it is never removed.
  positive("stsd_original_header_only_one_actual_entry",()->checkS(stsd(0,1,0,free())));
  positive("avcc_original_raw_and_actual_counts",()->checkA(avcc(1,255,225,0)));
  negative("dref_unparsed_builder","DREF_HEADER_NOT_OBSERVED",()->checkD(DataRefBox.createDataRefBox(),(short)1));
  negative("stsd_unparsed_builder","STSD_HEADER_NOT_OBSERVED",()->checkS(SampleDescriptionBox.createSampleDescriptionBox(new SampleEntry[0])));
  negative("avcc_unparsed_builder","AVCC_HEADER_NOT_OBSERVED",()->checkA(AvcCBox.createEmpty()));
  negative("dref_unknown_original_version","DREF_ORIGINAL_VERSION_FLAGS_REJECTED",()->checkD(dref(0x01000000,1,0,alias(0,1)),(short)1));
  negative("dref_unknown_original_flags","DREF_ORIGINAL_VERSION_FLAGS_REJECTED",()->checkD(dref(3,1,0,alias(0,1)),(short)1));
  negative("dref_raw_declared_zero_actual_one","DREF_ORIGINAL_COUNT_REJECTED",()->checkD(dref(0,0,0,alias(0,1)),(short)1));
  negative("dref_uint32_max_actual_one","DREF_ORIGINAL_COUNT_REJECTED",()->checkD(dref(0,-1,0,alias(0,1)),(short)1));
  negative("dref_duplicate_actual_entries","DREF_ORIGINAL_COUNT_REJECTED",()->checkD(dref(0,2,0,alias(0,1),url(1,null)),(short)1));
  negative("dref_original_unconsumed_tail","DREF_BODY_OR_TAIL_REJECTED",()->checkD(dref(0,1,1,alias(0,1)),(short)1));
  negative("dref_index_zero","DREF_UNIQUE_ENTRY_AND_INDEX_UNPROVEN",()->checkD(dref(0,1,0,alias(0,1)),(short)0));
  negative("dref_external_url","DREF_VERSION_OR_FLAGS_NOT_ADMITTED",()->checkD(dref(0,1,0,url(0,"file:///external")),(short)1));
  negative("dref_selfref_url_with_ignored_tail","DREF_BODY_OR_TRAILING_DATA_UNPROVEN",()->checkD(dref(0,1,0,url(1,"file:///external")),(short)1));
  negative("dref_child_unknown_version","DREF_VERSION_OR_FLAGS_NOT_ADMITTED",()->checkD(dref(0,1,0,alias(1,1)),(short)1));
  negative("dref_child_unknown_flags","DREF_VERSION_OR_FLAGS_NOT_ADMITTED",()->checkD(dref(0,1,0,alias(0,3)),(short)1));
  negative("dref_unknown_child_type","DREF_TYPED_SEMANTIC_API_UNPROVEN",()->checkD(dref(0,1,0,free()),(short)1));
  DataRefBox leaf=dref(0,1,0,alias(0,1));leaf.getBoxes().set(0,Box.createLeafBox(Header.createHeader("alis",12),buffer(4)));
  negative("dref_untyped_alis_leaf","DREF_TYPED_SEMANTIC_API_UNPROVEN",()->checkD(leaf,(short)1));
  DataRefBox failedD=dref(0,1,0,alias(0,1));try{failedD.parse(buffer(0));}catch(RuntimeException expected){}negative("dref_failed_reparse_not_observed","DREF_HEADER_NOT_OBSERVED",()->checkD(failedD,(short)1));
  negative("stsd_unknown_original_version","STSD_ORIGINAL_VERSION_FLAGS_REJECTED",()->checkS(stsd(0x01000000,1,0,free())));
  negative("stsd_unknown_original_flags","STSD_ORIGINAL_VERSION_FLAGS_REJECTED",()->checkS(stsd(7,1,0,free())));
  negative("stsd_raw_declared_zero_actual_one","STSD_ORIGINAL_COUNT_REJECTED",()->checkS(stsd(0,0,0,free())));
  negative("stsd_duplicate_actual_entries","STSD_ORIGINAL_COUNT_REJECTED",()->checkS(stsd(0,2,0,free(),free())));
  negative("stsd_unconsumed_tail","STSD_BODY_OR_TAIL_REJECTED",()->checkS(stsd(0,1,1,free())));
  SampleDescriptionBox failedS=stsd(0,1,0,free());try{failedS.parse(buffer(0));}catch(RuntimeException expected){}negative("stsd_failed_reparse_not_observed","STSD_HEADER_NOT_OBSERVED",()->checkS(failedS));
  negative("avcc_unknown_configuration_version","AVCC_CONFIG_VERSION_REJECTED",()->checkA(avcc(7,255,225,0)));
  negative("avcc_bad_length_reserved","AVCC_LENGTH_OR_RESERVED_REJECTED",()->checkA(avcc(1,19,225,0)));
  negative("avcc_bad_sps_reserved","AVCC_SPS_RESERVED_REJECTED",()->checkA(avcc(1,255,33,0)));
  negative("avcc_unconsumed_extension_tail","AVCC_BODY_OR_TAIL_REJECTED",()->checkA(avcc(1,255,225,1)));
  AvcCBox sps=avcc(1,255,225,0);sps.getSpsList().clear();negative("avcc_declared_vs_actual_sps","AVCC_ORIGINAL_COUNTS_REJECTED",()->checkA(sps));
  AvcCBox pps=avcc(1,255,225,0);pps.getPpsList().clear();negative("avcc_declared_vs_actual_pps","AVCC_ORIGINAL_COUNTS_REJECTED",()->checkA(pps));
  AvcCBox failedA=avcc(1,255,225,0);try{failedA.parse(buffer(0));}catch(RuntimeException expected){}negative("avcc_failed_reparse_not_observed","AVCC_HEADER_NOT_OBSERVED",()->checkA(failedA));
  guard();if(cases!=34||payload+2048>8192)throw new AssertionError("EXACT34_POLICY_8K");
  return ReceiptJson.map("status","QUALIFIER03_FINITE_POLICY_CHECKS_COMPLETE_NOT_MEDIA","cases",cases,"explicitMetadataPayloadBytes",payload,"matureScratchAllowance",2048,"metadataByteLimit",8192,"actualClassOrigins",origins,"mediaReads",0,"actualQualifierInvocations",0,"rawPolicyResultsScope","FINITE_ORIGINAL_METADATA_AND_TYPED_CHILD_NOT_TRACK_OR_DECODE");
 }
 private Qualifier03PolicyCheck(){}
}
