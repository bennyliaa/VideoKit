package com.videokit.fixturetool;
import java.io.IOException;import java.nio.ByteBuffer;import java.util.*;
import org.jcodec.containers.mp4.BoxFactory;import org.jcodec.containers.mp4.boxes.*;

/** One finite in-memory semantic test. Never references qualifier or media. */
public final class DataReferenceSemanticCheck {
 static long allocated,started;static int checks;static volatile Throwable failure;static volatile boolean bodyReturned,unknown;
 static ByteBuffer buffer(int n){if(n<0||allocated>4096-n)throw new AssertionError("NONMEDIA_4K_LIMIT");allocated+=n;return ByteBuffer.allocate(n);}
 static void guard(){if(System.nanoTime()-started>=5000000000L){unknown=true;throw new AssertionError("SEMANTIC_5S_UNKNOWN");}}
 static AliasBox alias(){AliasBox b=AliasBox.createSelfRef();b.getHeader().setBodySize(4);return b;}
 static UrlBox url(){UrlBox b=UrlBox.createUrlBox(null);b.setFlags(1);b.getHeader().setBodySize(4);return b;}
 static DataRefBox ref(Box child){DataRefBox b=DataRefBox.createDataRefBox();if(child!=null)b.add(child);b.getHeader().setBodySize(8+(child==null?0:(int)child.getHeader().getSize()));return b;}
 static void positive(String name,DataRefBox refs,short index)throws Exception{guard();Map<String,Object> m=ReceiptJson.map();DataReferencePolicy.inspect(refs,index,m);if(!"PROVEN_IN_RESTRICTED_VERSION0_FLAGS1_EXACT_BODY4_SCOPE".equals(m.get("childSelfContainedSemantics")))throw new AssertionError("MISSING_ACTUAL_PROOF");checks++;System.out.println(ReceiptJson.json(ReceiptJson.map("case",name,"result","PASS_ACCEPT_CHILD_SEMANTICS_ONLY","actual",m)));}
 static void negative(String name,DataRefBox refs,short index,String expected)throws Exception{guard();Map<String,Object> m=ReceiptJson.map();try{DataReferencePolicy.inspect(refs,index,m);throw new AssertionError("UNSAFE_ACCEPT_"+name);}catch(IOException e){if(!expected.equals(e.getMessage()))throw new AssertionError("WRONG_REJECTION_"+name+"_"+e.getMessage());checks++;System.out.println(ReceiptJson.json(ReceiptJson.map("case",name,"result","PASS_REJECT","actualReason",e.getMessage(),"actual",m)));}}
 static DataRefBox roundTripOwnObject(Box child)throws Exception{DataRefBox source=ref(child);ByteBuffer bytes=buffer(64);source.write(bytes);bytes.flip();Box parsed=NodeBox.parseChildBox(bytes,BoxFactory.getDefault());if(!(parsed instanceof DataRefBox)||bytes.hasRemaining())throw new AssertionError("MATURE_MINIMAL_FACTORY_NOT_EXACT");return (DataRefBox)parsed;}
 static void mandatoryGap(String name,Box child)throws Exception{guard();Map<String,Object> m=ReceiptJson.map();DataReferencePolicy.inspect(ref(child),(short)1,m);try{DataReferencePolicy.requireOriginalContainerMetadata(m);throw new AssertionError("WHOLE_METADATA_FALSE_PASS");}catch(IOException e){if(!"DREF_CONTAINER_ORIGINAL_HEADER_METADATA_UNPROVEN".equals(e.getMessage()))throw e;checks++;System.out.println(ReceiptJson.json(ReceiptJson.map("case",name,"result","PASS_MANDATORY_WHOLE_QUALIFICATION_BLOCKED","actualReason",e.getMessage(),"actual",m)));}}
 static void runCases()throws Exception {
  positive("selfref_alias_object",ref(alias()),(short)1);positive("selfref_url_object",ref(url()),(short)1);
  positive("mature_factory_own_alias",roundTripOwnObject(alias()),(short)1);positive("mature_factory_own_url",roundTripOwnObject(url()),(short)1);
  negative("missing_dref",null,(short)1,"DREF_UNIQUE_ENTRY_AND_INDEX_UNPROVEN");negative("empty_dref",ref(null),(short)1,"DREF_UNIQUE_ENTRY_AND_INDEX_UNPROVEN");
  DataRefBox duplicate=ref(alias());duplicate.add(url());negative("duplicate_entries",duplicate,(short)1,"DREF_UNIQUE_ENTRY_AND_INDEX_UNPROVEN");
  negative("index_zero",ref(alias()),(short)0,"DREF_UNIQUE_ENTRY_AND_INDEX_UNPROVEN");negative("index_two",ref(alias()),(short)2,"DREF_UNIQUE_ENTRY_AND_INDEX_UNPROVEN");negative("index_negative",ref(alias()),(short)-1,"DREF_UNIQUE_ENTRY_AND_INDEX_UNPROVEN");
  AliasBox external=alias();external.setFlags(0);negative("nonselfref_alias_flags",ref(external),(short)1,"DREF_VERSION_OR_FLAGS_NOT_ADMITTED");
  UrlBox extUrl=UrlBox.createUrlBox("file:///not-admitted");extUrl.setFlags(0);extUrl.getHeader().setBodySize(4);negative("external_url",ref(extUrl),(short)1,"DREF_VERSION_OR_FLAGS_NOT_ADMITTED");
  UrlBox contradictory=UrlBox.createUrlBox("file:///not-admitted");contradictory.setFlags(1);contradictory.getHeader().setBodySize(4);negative("selfref_flag_with_external_url",ref(contradictory),(short)1,"EXTERNAL_URL_FORBIDDEN");
  AliasBox v=alias();v.setVersion((byte)1);negative("unknown_version_alias",ref(v),(short)1,"DREF_VERSION_OR_FLAGS_NOT_ADMITTED");
  UrlBox u=url();u.setVersion((byte)1);negative("unknown_version_url",ref(u),(short)1,"DREF_VERSION_OR_FLAGS_NOT_ADMITTED");
  AliasBox flags=alias();flags.setFlags(3);negative("unknown_alias_flags",ref(flags),(short)1,"DREF_VERSION_OR_FLAGS_NOT_ADMITTED");
  UrlBox uf=url();uf.setFlags(257);negative("unknown_url_flags",ref(uf),(short)1,"DREF_VERSION_OR_FLAGS_NOT_ADMITTED");
  AliasBox tail=alias();tail.getHeader().setBodySize(5);negative("alias_tail",ref(tail),(short)1,"DREF_BODY_OR_TRAILING_DATA_UNPROVEN");
  UrlBox ut=url();ut.getHeader().setBodySize(5);negative("url_tail",ref(ut),(short)1,"DREF_BODY_OR_TRAILING_DATA_UNPROVEN");
  DataRefBox dt=ref(alias());dt.getHeader().setBodySize(21);negative("dref_tail",dt,(short)1,"DREF_BODY_OR_TRAILING_DATA_UNPROVEN");
  AliasBox missing=AliasBox.createSelfRef();negative("body_size_information_missing",ref(missing),(short)1,"DREF_BODY_OR_TRAILING_DATA_UNPROVEN");
  Box leaf=Box.createLeafBox(Header.createHeader("alis",12),buffer(4));negative("untyped_alis_leaf",ref(leaf),(short)1,"DREF_TYPED_SEMANTIC_API_UNPROVEN");
  AliasBox cios=new AliasBox(Header.createHeader("cios",12));cios.setFlags(1);negative("unknown_alias_fourcc",ref(cios),(short)1,"DREF_TYPED_SEMANTIC_API_UNPROVEN");
  UrlBox mismatch=new UrlBox(Header.createHeader("alis",12));mismatch.setFlags(1);negative("type_fourcc_mismatch",ref(mismatch),(short)1,"DREF_TYPED_SEMANTIC_API_UNPROVEN");
  mandatoryGap("selfref_alias_does_not_prove_container_header",alias());mandatoryGap("selfref_url_does_not_prove_container_header",url());
  guard();if(checks!=26||allocated>4096)throw new AssertionError("EXACT_26_CASES_4K");
 }
 public static void main(String[] args)throws Exception {if(args.length!=0)throw new IllegalArgumentException("NO_ARGS");started=System.nanoTime();Thread original=new Thread(()->{try{runCases();}catch(Throwable e){failure=e;}finally{bodyReturned=true;}},"qualifier02-original-nonmedia-semantics");original.setDaemon(false);original.start();original.join(5000);if(original.isAlive()){unknown=true;System.out.println("UNKNOWN same original semantic worker retained; no interrupt or retry");original.join();}long elapsed=System.nanoTime()-started;if(elapsed>=5000000000L)unknown=true;System.out.println(ReceiptJson.json(ReceiptJson.map("summary","QUALIFIER02_NONMEDIA_SEMANTICS","checks",checks,"allocatedExplicitPayloadBytes",allocated,"actualOriginalWorkerJoined",true,"bodyReturned",bodyReturned,"unknownSticky",unknown,"elapsedNanos",elapsed,"mediaReads",0,"helperRuntimeCalls",0,"containerHeaderMetadata","UNPROVEN_NOT_TESTED_BY_OWN_SERIALIZED_OBJECTS")));if(failure!=null)throw new AssertionError("ORIGINAL_SEMANTIC_FAILURE",failure);if(unknown||!bodyReturned)throw new AssertionError("ORIGINAL_UNKNOWN");}
 private DataReferenceSemanticCheck(){}
}
