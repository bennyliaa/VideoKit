package com.videokit.fixturetool;
import java.io.IOException;import java.nio.ByteBuffer;import java.util.*;
import org.jcodec.containers.mp4.boxes.*;import org.jcodec.codecs.h264.mp4.AvcCBox;

/** Policies over ORIGINAL parse observations, never a parser or writer. */
final class MetadataPolicy03 {
 static void need(boolean b,String s)throws IOException{if(!b)throw new IOException(s);}
 static void parent(NodeBox box,int word,int version,int flags,long declared,String kind,Map<String,Object> out)throws IOException {
  int actual=box.getBoxes().size();out.put("source","0.2.5-videokit-observation01 ORIGINAL_PARSE_ONLY");out.put("observed",true);out.put("fourcc",box.getFourcc());out.put("rawVersionFlagsWord",word);out.put("version",version);out.put("flags",flags);out.put("declaredCountUnsigned",declared);out.put("actualParsedChildren",actual);
  need(box.getFourcc().equals(kind.toLowerCase(Locale.ROOT))&&version==(word>>>24)&&flags==(word&0xffffff)&&version==0&&flags==0,kind+"_ORIGINAL_VERSION_FLAGS_REJECTED");
  need(declared==1&&actual==1&&declared==actual,kind+"_ORIGINAL_COUNT_REJECTED");
  long body=8;for(Box child:box.getBoxes()){need(child!=null&&child.getHeader()!=null&&child.getHeader().getSize()>=8,kind+"_CHILD_HEADER_UNPROVEN");body=Math.addExact(body,child.getHeader().getSize());}
  out.put("actualHeaderBodyBytes",box.getHeader().getBodySize());out.put("bodyFromActualChildrenAndOriginalPrefix",body);
  need(box.getHeader().headerSize()==8&&box.getHeader().getBodySize()==body,kind+"_BODY_OR_TAIL_REJECTED");
 }
 static void dref(DataRefBox refs,Map<String,Object> out)throws IOException {
  need(refs!=null&&refs.hasOriginalParseObservation(),"DREF_HEADER_NOT_OBSERVED");parent(refs,refs.getOriginalVersionFlagsWord(),refs.getOriginalVersion(),refs.getOriginalFlags(),refs.getOriginalDeclaredEntryCount(),"DREF",out);
 }
 static void stsd(SampleDescriptionBox stsd,Map<String,Object> out)throws IOException {
  need(stsd!=null&&stsd.hasOriginalParseObservation(),"STSD_HEADER_NOT_OBSERVED");parent(stsd,stsd.getOriginalVersionFlagsWord(),stsd.getOriginalVersion(),stsd.getOriginalFlags(),stsd.getOriginalDeclaredEntryCount(),"STSD",out);
 }
 static void avcc(AvcCBox box,Map<String,Object> out)throws IOException {
  need(box!=null&&box.hasOriginalParseObservation(),"AVCC_HEADER_NOT_OBSERVED");
  int cfg=box.getOriginalConfigurationVersion(),rawLength=box.getOriginalLengthSizeByte(),rawSps=box.getOriginalSpsCountByte(),declSps=rawSps&31,declPps=box.getOriginalPpsCountByte();
  List<ByteBuffer>sps=box.getSpsList(),pps=box.getPpsList();out.put("source","0.2.5-videokit-observation01 ORIGINAL_PARSE_ONLY");out.put("observed",true);out.put("configurationVersion",cfg);out.put("rawLengthSizeByte",rawLength);out.put("lengthReservedHigh6",rawLength>>>2);out.put("actualNalLengthSize",box.getNalLengthSize());out.put("rawSpsCountByte",rawSps);out.put("spsReservedHigh3",rawSps>>>5);out.put("declaredSpsCount",declSps);out.put("declaredPpsCount",declPps);out.put("actualSpsCount",sps==null?null:sps.size());out.put("actualPpsCount",pps==null?null:pps.size());
  need(cfg==1,"AVCC_CONFIG_VERSION_REJECTED");need((rawLength&252)==252&&(rawLength&3)+1==box.getNalLengthSize()&&box.getNalLengthSize()==4,"AVCC_LENGTH_OR_RESERVED_REJECTED");need((rawSps&224)==224,"AVCC_SPS_RESERVED_REJECTED");
  need(sps!=null&&pps!=null&&declSps>0&&declPps>0&&declSps<=16&&declPps<=16&&declSps==sps.size()&&declPps==pps.size(),"AVCC_ORIGINAL_COUNTS_REJECTED");
  long body=7,payload=0;for(List<ByteBuffer> list:Arrays.asList(sps,pps))for(ByteBuffer b:list){need(b!=null&&b.remaining()>0&&b.remaining()<=65536-payload,"AVCC_CSD_PAYLOAD_LIMIT");payload+=b.remaining();body+=3L+b.remaining();}
  out.put("actualHeaderBodyBytes",box.getHeader().getBodySize());out.put("bodyFromObservedCountsAndActualPayloads",body);out.put("actualCsdPayloadBytes",payload);
  need(box.getHeader().headerSize()==8&&box.getHeader().getBodySize()==body,"AVCC_BODY_OR_TAIL_REJECTED");
 }
 private MetadataPolicy03(){}
}
