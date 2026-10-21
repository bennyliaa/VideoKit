package com.videokit.fixturetool;
import java.io.IOException;import java.util.Map;
import org.jcodec.containers.mp4.boxes.*;

/** Typed mature-box semantics only. No byte parsing, serialization of file
 * objects, library/factory changes or inference from generation receipts. */
final class DataReferencePolicy03 {
 static void need(boolean b,String reason)throws IOException{if(!b)throw new IOException(reason);}
 static void inspect(DataRefBox refs,short index,Map<String,Object> out)throws IOException {
  out.put("criterionSource","0.2.5-videokit-observation01 original-parent + typed-child APIs");
  out.put("sampleEntryDataReferenceIndex",(int)index);
  out.put("parsedEntryCount",refs==null?null:refs.getBoxes().size());
  Map<String,Object> original=ReceiptJson.map();out.put("originalDrefHeader",original);MetadataPolicy03.dref(refs,original);
  need(refs!=null&&"dref".equals(refs.getFourcc())&&refs.getBoxes().size()==1&&index==1,"DREF_UNIQUE_ENTRY_AND_INDEX_UNPROVEN");
  Box child=refs.getBoxes().get(0);need(child!=null&&child.getHeader()!=null,"DREF_CHILD_HEADER_UNPROVEN");
  String type=child.getFourcc();out.put("actualChildFourcc",type);out.put("actualChildClass",child.getClass().getName());
  out.put("actualChildHeaderBytes",child.getHeader().headerSize());out.put("actualChildBodyBytes",child.getHeader().getBodySize());
  out.put("actualDrefBodyBytes",refs.getHeader().getBodySize());
  need(("alis".equals(type)&&child.getClass()==AliasBox.class)||("url ".equals(type)&&child.getClass()==UrlBox.class),"DREF_TYPED_SEMANTIC_API_UNPROVEN");
  FullBox full=(FullBox)child;out.put("childVersion",(int)full.getVersion());out.put("childFlags",full.getFlags());
  need(full.getVersion()==0&&full.getFlags()==1,"DREF_VERSION_OR_FLAGS_NOT_ADMITTED");
  need(child.getHeader().headerSize()==8&&child.getHeader().getBodySize()==4&&refs.getHeader().headerSize()==8&&refs.getHeader().getBodySize()==8+child.getHeader().getSize(),"DREF_BODY_OR_TRAILING_DATA_UNPROVEN");
  if(child instanceof AliasBox){AliasBox alias=(AliasBox)child;out.put("matureAliasIsSelfRef",alias.isSelfRef());out.put("aliasFileName",alias.getFileName());out.put("aliasExtrasCount",alias.getExtras()==null?null:alias.getExtras().size());out.put("aliasRecordSize",alias.getRecordSize());
   need(alias.isSelfRef()&&alias.getFileName()==null&&alias.getExtras()==null&&alias.getRecordSize()==0,"EXTERNAL_ALIAS_OR_INFORMATION_UNPROVEN");
  }else{String url=((UrlBox)child).getUrl();out.put("actualUrl",url);need(url==null,"EXTERNAL_URL_FORBIDDEN");}
  out.put("childSelfContainedSemantics","PROVEN_IN_RESTRICTED_VERSION0_FLAGS1_EXACT_BODY4_SCOPE");
 }
 private DataReferencePolicy03(){}
}
