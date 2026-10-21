package com.videokit.fixturetool;
import java.io.IOException;import java.nio.file.*;import java.util.*;
import org.jcodec.containers.mp4.boxes.*;import org.jcodec.containers.mp4.BoxFactory;import org.jcodec.codecs.h264.mp4.AvcCBox;

/** Exact class-source assertions. The external controller also pins hashes and
 * exact helper/support class sets, so there is no second JCodec fallback. */
final class OriginFence03 {
 static final Path ROOT=Paths.get("D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_SIX01_QUALIFIER03_PREPARATION");
 static final Path FORK=Paths.get("D:/CodexProjects/VideoKit/docs/coder/d1jcodec-observation01/artifacts/jcodec-0.2.5-videokit-observation01.jar");
 static Map<String,Object> one(Class<?> type,Path expected)throws Exception {
  if(type.getProtectionDomain().getCodeSource()==null)throw new IOException("CODE_SOURCE_UNPROVEN");Path actual=Paths.get(type.getProtectionDomain().getCodeSource().getLocation().toURI()).toRealPath();
  if(!actual.equals(expected.toRealPath()))throw new IOException("EXACT_CODE_SOURCE_MISMATCH");return ReceiptJson.map("class",type.getName(),"actualCodeSource",actual.toString());
 }
 static Map<String,Object> metadata()throws Exception {
  if(!"0.2.5-videokit-observation01".equals(AvcCBox.class.getPackage().getImplementationVersion()))throw new IOException("FORK_VERSION_UNPROVEN");
  List<Object> found=new ArrayList<>();for(Class<?> type:new Class<?>[]{DataRefBox.class,SampleDescriptionBox.class,AvcCBox.class,AliasBox.class,UrlBox.class,FullBox.class,NodeBox.class,Header.class,BoxFactory.class,org.jcodec.common.io.SeekableByteChannel.class})found.add(one(type,FORK));
  for(Class<?> type:new Class<?>[]{WorkerDeadline.class,ReceiptJson.class})found.add(one(type,ROOT.resolve("support")));
  for(Class<?> type:new Class<?>[]{MetadataPolicy03.class,DataReferencePolicy03.class,OriginFence03.class})found.add(one(type,ROOT.resolve("helper-classes")));
  return ReceiptJson.map("scope","ACTUAL_METADATA_AND_SUPPORT_CODE_SOURCES_ONLY","forkVersion",AvcCBox.class.getPackage().getImplementationVersion(),"classes",found,"fullJcodecJarFallback",false);
 }
 static Map<String,Object> futureRuntime(Class<?>... actualMediaTypes)throws Exception {
  Map<String,Object> proof=metadata();List<Object> more=new ArrayList<>();for(Class<?> type:actualMediaTypes)more.add(one(type,FORK));proof.put("additionalActualRuntimeTypes",more);return proof;
 }
 private OriginFence03(){}
}
