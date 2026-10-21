package com.videokit.testerobs;
import java.nio.*;
import java.nio.file.*;
import java.net.*;
import java.lang.reflect.*;
import java.util.*;

/** One JVM, isolated original/patched metadata classes. Reflection invokes only
 * public mature APIs/new getters; no field access, setAccessible or state edits. */
public final class IndependentObservationCheck {
    static final String ROOT="D:/CodexProjects/VideoKit/docs/coder/";
    static final String BASE=ROOT+"d1fixture-tool02/artifacts/videokit-fixture-tool02.jar";
    static final String FORK=ROOT+"d1jcodec-observation01/artifacts/jcodec-0.2.5-videokit-observation01.jar";
    static volatile boolean stopped,bodyComplete,unknown;
    static volatile long endNano;
    static long startNano;
    static volatile Throwable failure;
    static Thread originalWorker;static final List<Api> loaderOwners=new ArrayList<>();
    static int cases,payload;
    static final long MAX_NANOS=5000000000L;
    static void need(boolean v,String m){if(!v)throw new AssertionError(m);}
    static void admission(){long elapsed=System.nanoTime()-startNano;if(stopped||elapsed<0||elapsed>=MAX_NANOS){unknown=true;stopped=true;throw new IllegalStateException("METADATA_ADMISSION_CLOSED");}}
    static byte[] allocate(int n){payload+=n;need(payload<=4096,"explicit payload allocation bound");return new byte[n];}
    static byte[] copy(byte[] src){byte[] b=allocate(src.length);System.arraycopy(src,0,b,0,src.length);return b;}
    static Object call(Object o,String name,Class<?>[] types,Object... args)throws Exception {
        try{return o.getClass().getMethod(name,types).invoke(o,args);}
        catch(InvocationTargetException e){Throwable t=e.getCause();if(t instanceof Exception)throw (Exception)t;if(t instanceof Error)throw (Error)t;throw new AssertionError(t);}
    }
    static Object get(Object o,String name)throws Exception{return call(o,name,new Class<?>[0]);}
    static String json(Object x){
        if(x==null)return "null";if(x instanceof Number||x instanceof Boolean)return x.toString();
        if(x instanceof Map){StringBuilder s=new StringBuilder("{");for(Map.Entry<?,?>e:((Map<?,?>)x).entrySet()){if(s.length()>1)s.append(',');s.append(json(e.getKey())).append(':').append(json(e.getValue()));}return s.append('}').toString();}
        if(x instanceof Iterable){StringBuilder s=new StringBuilder("[");for(Object e:(Iterable<?>)x){if(s.length()>1)s.append(',');s.append(json(e));}return s.append(']').toString();}
        return "\""+x.toString().replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r")+"\"";
    }
    static Map<String,Object> map(Object...pairs){Map<String,Object>m=new LinkedHashMap<>();for(int i=0;i<pairs.length;i+=2)m.put((String)pairs[i],pairs[i+1]);return m;}
    static final class Api implements AutoCloseable {
        URLClassLoader loader;Object factory;Class<?> header;final String path;boolean openEntered,openReturned,closeEntered,closeReturned;
        Api(String path)throws Exception{this.path=path;loaderOwners.add(this);openEntered=true;loader=new URLClassLoader(new URL[]{Paths.get(path).toUri().toURL()},ClassLoader.getPlatformClassLoader());header=Class.forName("org.jcodec.containers.mp4.boxes.Header",true,loader);Class<?> f=Class.forName("org.jcodec.containers.mp4.BoxFactory",true,loader);factory=f.getMethod("getDefault").invoke(null);openReturned=true;}
        Object box(String fourcc)throws Exception{Object h=header.getConstructor(String.class).newInstance(fourcc);if(fourcc.equals("avcC"))return Class.forName("org.jcodec.codecs.h264.mp4.AvcCBox",true,loader).getConstructor(header).newInstance(h);return call(factory,"newBox",new Class<?>[]{header},h);}
        Object withoutFactory(String type)throws Exception{String name=type.equals("dref")?"DataRefBox":"SampleDescriptionBox";return Class.forName("org.jcodec.containers.mp4.boxes."+name,true,loader).getConstructor(header).newInstance(header.getConstructor(String.class).newInstance(type));}
        Map<String,Object> originalView(Object box,String type)throws Exception {
            if(type.equals("avcC")) {
                List<?>sps=(List<?>)get(box,"getSpsList"),pps=(List<?>)get(box,"getPpsList");
                List<String>s=new ArrayList<>(),p=new ArrayList<>();for(Object b:sps)s.add(hex((ByteBuffer)b));for(Object b:pps)p.add(hex((ByteBuffer)b));
                return map("profile",get(box,"getProfile"),"compat",get(box,"getProfileCompat"),"level",get(box,"getLevel"),"nalLengthSize",get(box,"getNalLengthSize"),"spsPayloads",s,"ppsPayloads",p);
            }
            List<?>children=(List<?>)get(box,"getBoxes");List<Object>views=new ArrayList<>();
            for(Object child:children){String c=(String)get(child,"getFourcc");Map<String,Object>v=map("class",child.getClass().getName(),"fourcc",c);
                if(c.equals("alis")||c.equals("url ")){v.put("version",get(child,"getVersion"));v.put("flags",get(child,"getFlags"));if(c.equals("alis")){v.put("selfRef",get(child,"isSelfRef"));v.put("fileName",get(child,"getFileName"));v.put("recordSize",get(child,"getRecordSize"));}else v.put("url",get(child,"getUrl"));}views.add(v);}
            return map("actualChildCount",children.size(),"children",views);
        }
        public void close()throws Exception{need(Thread.currentThread()==originalWorker,"same original loader closer");if(closeEntered)return;if(loader==null){unknown=true;return;}closeEntered=true;loader.close();closeReturned=true;}
        Map<String,Object>owner(){return map("path",path,"registeredBeforeLoaderAllocation",true,"openEntered",openEntered,"openReturned",openReturned,"closeEntered",closeEntered,"sameOriginalCloseReturned",closeReturned,"sameOriginalWorkerCloser",true);}
    }
    static String hex(ByteBuffer b){ByteBuffer d=b.duplicate();StringBuilder s=new StringBuilder();while(d.hasRemaining()){int v=d.get()&255;s.append(Character.forDigit(v>>>4,16)).append(Character.forDigit(v&15,16));}return s.toString();}
    static final class Outcome {
        String exception,beforeOrder,afterOrder;int before,after,limit,remaining;Map<String,Object>view,raw;
        Map<String,Object>data(){return map("exceptionClass",exception,"inputBefore",before,"inputAfter",after,"limit",limit,"remaining",remaining,"byteOrderBefore",beforeOrder,"byteOrderAfter",afterOrder,"existingGetterView",view,"originalObservation",raw);}
    }
    static Outcome parse(Api a,Object box,String type,ByteBuffer input)throws Exception {
        admission();Outcome r=new Outcome();r.before=input.position();r.limit=input.limit();r.beforeOrder=input.order().toString();
        try{call(box,"parse",new Class<?>[]{ByteBuffer.class},input);}catch(Exception e){r.exception=e.getClass().getName();}
        r.after=input.position();r.remaining=input.remaining();r.afterOrder=input.order().toString();r.view=a.originalView(box,type);r.raw=a.path.equals(FORK)?observation(box,type):null;return r;
    }
    static Map<String,Object> observation(Object box,String type)throws Exception {
        boolean complete=(Boolean)get(box,"hasOriginalParseObservation");Map<String,Object>m=map("observed",complete);
        if(complete){String[]names=type.equals("avcC")?new String[]{"getOriginalConfigurationVersion","getOriginalLengthSizeByte","getOriginalSpsCountByte","getOriginalPpsCountByte"}:new String[]{"getOriginalVersionFlagsWord","getOriginalVersion","getOriginalFlags","getOriginalDeclaredEntryCount"};for(String n:names)m.put(n,get(box,n));}return m;
    }
    static void readonlyObservation(Api base,Api fork,String type)throws Exception {
        byte[]bytes=type.equals("avcC")?avcc():parent(0xaabbccdd,-1,type.equals("dref")?"alis":"free");Object box=fork.box(type);ByteBuffer input=ByteBuffer.wrap(bytes);Outcome result=parse(fork,box,type,input);need(result.exception==null,"readonly observation precondition");int position=input.position();Map<String,Object>legacy=fork.originalView(box,type),first=observation(box,type),second=observation(box,type);need(first.equals(second)&&legacy.equals(fork.originalView(box,type))&&position==input.position(),"new getter mutated input or legacy state");cases++;System.out.println(json(map("case",type+"_readonly_observation_getters","result","PASS_NONMEDIA_METADATA","actual",first,"inputPositionBeforeAfter",position,"legacyUnchanged",true)));
    }
    static void unobserved(Object box,String type)throws Exception {
        need(Boolean.FALSE.equals(get(box,"hasOriginalParseObservation")),"no false observed state");
        String[]names=type.equals("avcC")?new String[]{"getOriginalConfigurationVersion","getOriginalLengthSizeByte","getOriginalSpsCountByte","getOriginalPpsCountByte"}:new String[]{"getOriginalVersionFlagsWord","getOriginalVersion","getOriginalFlags","getOriginalDeclaredEntryCount"};
        for(String n:names){try{get(box,n);}catch(IllegalStateException expected){continue;}throw new AssertionError("unobserved getter leaked "+n);}
    }
    static void row(String name,Outcome base,Outcome fork)throws Exception {
        need(Objects.equals(base.exception,fork.exception)&&base.after==fork.after&&base.before==fork.before&&base.limit==fork.limit&&base.remaining==fork.remaining&&base.beforeOrder.equals(fork.beforeOrder)&&base.afterOrder.equals(fork.afterOrder)&&base.view.equals(fork.view),"baseline semantics differ "+name+" "+base.data()+" / "+fork.data());
        cases++;System.out.println(json(map("case",name,"result","PASS_NONMEDIA_METADATA","baseline",base.data(),"fork",fork.data())));
    }
    static byte[] parent(int word,int count,String child)throws Exception {
        int n=child==null?8:child.equals("free")?16:20;ByteBuffer b=ByteBuffer.wrap(allocate(n));b.putInt(word).putInt(count);
        if(child!=null){b.putInt(n-8);for(int i=0;i<4;i++)b.put((byte)child.charAt(i));if(!child.equals("free"))b.putInt(1);}return b.array();
    }
    static void parentCase(Api base,Api fork,String type,int word,int count,String child,String label)throws Exception {
        byte[]bytes=parent(word,count,child);Object ob=base.box(type),of=fork.box(type);
        Outcome a=parse(base,ob,type,ByteBuffer.wrap(bytes)),b=parse(fork,of,type,ByteBuffer.wrap(bytes));row(type+"_"+label,a,b);
        need(a.exception==null&&Boolean.TRUE.equals(get(of,"hasOriginalParseObservation")),"normal parse completion");
        need(((Number)get(of,"getOriginalVersionFlagsWord")).intValue()==word&&((Number)get(of,"getOriginalVersion")).intValue()==(word>>>24)&&((Number)get(of,"getOriginalFlags")).intValue()==(word&0xffffff)&&((Number)get(of,"getOriginalDeclaredEntryCount")).longValue()==(count&0xffffffffL),"raw original words preserved");
    }
    static void parentFailures(Api base,Api fork,String type)throws Exception {
        byte[]good=parent(0,1,type.equals("dref")?"alis":"free");
        for(int n=0;n<8;n++){
            Object ob=base.box(type),of=fork.box(type);parse(base,ob,type,ByteBuffer.wrap(good));parse(fork,of,type,ByteBuffer.wrap(good));
            ByteBuffer x=ByteBuffer.wrap(good).limit(n),y=ByteBuffer.wrap(good).limit(n);Outcome a=parse(base,ob,type,x),b=parse(fork,of,type,y);row(type+"_reparse_truncated_"+n,a,b);need(a.exception!=null,"safe truncated header exception");unobserved(of,type);
        }
        byte[]tail=allocate(good.length+3);System.arraycopy(good,0,tail,0,good.length);tail[tail.length-1]=7;
        Object ob=base.box(type),of=fork.box(type);Outcome a=parse(base,ob,type,ByteBuffer.wrap(tail)),b=parse(fork,of,type,ByteBuffer.wrap(tail));row(type+"_original_unconsumed_tail",a,b);need(b.after==good.length&&Boolean.TRUE.equals(get(of,"hasOriginalParseObservation")),"observed means parse returned, not strict full-buffer conformance");
    }
    static byte[] avcc(){
        // Metadata-only construction using already frozen generator CSD payloads.
        // Prefix is a test record, not raw bytes claimed from any MP4 file.
        int[]v={1,66,0,40,255,225,0,8,103,66,0,40,244,8,9,136,1,0,4,104,206,56,128};byte[]b=allocate(v.length);for(int i=0;i<v.length;i++)b[i]=(byte)v[i];return b;
    }
    static void avccCase(Api base,Api fork,byte[]bytes,int cfg,int length,int sps,int pps,String name)throws Exception {
        Object ob=base.box("avcC"),of=fork.box("avcC");Outcome a=parse(base,ob,"avcC",ByteBuffer.wrap(bytes)),b=parse(fork,of,"avcC",ByteBuffer.wrap(bytes));row("avcC_"+name,a,b);need(a.exception==null&&Boolean.TRUE.equals(get(of,"hasOriginalParseObservation")),"avcC observed after original completion");
        need(((Number)get(of,"getOriginalConfigurationVersion")).intValue()==cfg&&((Number)get(of,"getOriginalLengthSizeByte")).intValue()==length&&((Number)get(of,"getOriginalSpsCountByte")).intValue()==sps&&((Number)get(of,"getOriginalPpsCountByte")).intValue()==pps,"actual consumed bytes retained");
    }
    static void repeated(Api base,Api fork,String type)throws Exception {
        byte[]first=type.equals("avcC")?avcc():parent(0,1,type.equals("dref")?"alis":"free");
        byte[]second=type.equals("avcC")?copy(first):parent(0x02000003,7,type.equals("dref")?"url ":"free");if(type.equals("avcC")){second[0]=7;second[4]=19;second[5]=33;}
        Object ob=base.box(type),of=fork.box(type);parse(base,ob,type,ByteBuffer.wrap(first));parse(fork,of,type,ByteBuffer.wrap(first));
        row(type+"_second_success_keeps_legacy_append",parse(base,ob,type,ByteBuffer.wrap(second)),parse(fork,of,type,ByteBuffer.wrap(second)));
        need(Boolean.TRUE.equals(get(of,"hasOriginalParseObservation")),"repeat observation");
        if(type.equals("avcC")){need(((List<?>)get(of,"getSpsList")).size()==2&&((Number)get(of,"getOriginalSpsCountByte")).intValue()==33,"SPS original declaration not accumulated list");}
        else need(((List<?>)get(of,"getBoxes")).size()==2&&((Number)get(of,"getOriginalDeclaredEntryCount")).longValue()==7,"new declared count versus accumulated children");
    }
    static void writeIsNotObservation(Api base,Api fork,String type)throws Exception {
        admission();
        Object ob=base.box(type),of=fork.box(type);ByteBuffer x=ByteBuffer.wrap(allocate(64)),y=ByteBuffer.wrap(allocate(64));
        Object eb=get(ob,"estimateSize"),ef=get(of,"estimateSize");call(ob,"write",new Class<?>[]{ByteBuffer.class},x);call(of,"write",new Class<?>[]{ByteBuffer.class},y);
        need(eb.equals(ef)&&x.position()==y.position(),"original estimate/write consumption");x.flip();y.flip();need(x.equals(y),"unchanged mature write bytes of OWN minimal in-memory object");unobserved(of,type);
        cases++;System.out.println(json(map("case",type+"_own_builder_write_not_original_observation","result","PASS_NONMEDIA_METADATA","writeBytes",x.remaining(),"usedAsOriginalHeaderGolden",false)));
    }
    static void runAll(long start)throws Exception {
        try(Api base=new Api(BASE);Api fork=new Api(FORK)) {
            System.out.println(json(map("origin","isolated-public-api-only","baseline",base.box("dref").getClass().getProtectionDomain().getCodeSource().getLocation().toString(),"fork",fork.box("dref").getClass().getProtectionDomain().getCodeSource().getLocation().toString())));
            need(base.box("dref").getClass().getClassLoader()==base.loader&&fork.box("dref").getClass().getClassLoader()==fork.loader&&base.loader!=fork.loader,"two actual isolated origins");
            for(String type:new String[]{"dref","stsd","avcC"}){Object oldBox=base.box(type),newBox=fork.box(type);need(oldBox.getClass().getClassLoader()==base.loader&&newBox.getClass().getClassLoader()==fork.loader,"per-type isolated loaders");need(oldBox.getClass().getName().equals(newBox.getClass().getName())&&(type.equals("avcC")?newBox.getClass().getName().equals("org.jcodec.codecs.h264.mp4.AvcCBox"):true),"actual mature type");System.out.println(json(map("classOrigins",type,"baseline",oldBox.getClass().getProtectionDomain().getCodeSource().getLocation().toString(),"fork",newBox.getClass().getProtectionDomain().getCodeSource().getLocation().toString(),"actualClass",newBox.getClass().getName())));unobserved(newBox,type);cases++;System.out.println(json(map("case",type+"_new_instance_unobserved","result","PASS_NONMEDIA_METADATA")));}
            for(String type:new String[]{"dref","stsd"}){
                need(!stopped&&System.nanoTime()-start<MAX_NANOS,"admission window");
                parentCase(base,fork,type,0,0,null,"empty_zero");parentCase(base,fork,type,0xff123456,0x80000000,null,"uint32_highbit_no_child_no_alloc");parentCase(base,fork,type,0,1,type.equals("dref")?"alis":"free","one_child");
                parentCase(base,fork,type,0xaabbccdd,0xffffffff,type.equals("dref")?"url ":"free","unknown_vf_unsigned_count_mismatch");
                parentCase(base,fork,type,0x01000002,0,type.equals("dref")?"alis":"free","declared_zero_actual_one");parentFailures(base,fork,type);
            }
            byte[]normal=avcc();avccCase(base,fork,normal,1,255,225,1,"known_metadata");
            byte[]unknown=copy(normal);unknown[0]=7;unknown[4]=19;unknown[5]=33;avccCase(base,fork,unknown,7,19,33,1,"unknown_version_reserved_not_normalized");
            for(int n=0;n<normal.length;n++){
                need(!stopped&&System.nanoTime()-start<MAX_NANOS,"parse admission closed");Object ob=base.box("avcC"),of=fork.box("avcC");parse(base,ob,"avcC",ByteBuffer.wrap(normal));parse(fork,of,"avcC",ByteBuffer.wrap(normal));
                Outcome a=parse(base,ob,"avcC",ByteBuffer.wrap(normal).limit(n)),b=parse(fork,of,"avcC",ByteBuffer.wrap(normal).limit(n));row("avcC_reparse_truncated_"+n,a,b);need(a.exception!=null,"truncated metadata fail");unobserved(of,"avcC");
            }
            byte[]bad=copy(normal);bad[8]=0;Object ob=base.box("avcC"),of=fork.box("avcC");parse(base,ob,"avcC",ByteBuffer.wrap(normal));parse(fork,of,"avcC",ByteBuffer.wrap(normal));Outcome a=parse(base,ob,"avcC",ByteBuffer.wrap(bad)),b=parse(fork,of,"avcC",ByteBuffer.wrap(bad));row("avcC_original_header_check_exception_unchanged",a,b);need(a.exception!=null,"original checkState remains");unobserved(of,"avcC");
            for(int at:new int[]{6,17}){byte[]signed=copy(normal);signed[at]=(byte)128;signed[at+1]=0;ob=base.box("avcC");of=fork.box("avcC");Outcome sa=parse(base,ob,"avcC",ByteBuffer.wrap(signed)),sf=parse(fork,of,"avcC",ByteBuffer.wrap(signed));row("avcC_original_signed_short_"+at,sa,sf);need(sa.exception!=null,"signed original short failure preserved");unobserved(of,"avcC");}
            byte[]partial=allocate(2);partial[0]=7;partial[1]=99;ob=base.box("avcC");of=fork.box("avcC");parse(base,ob,"avcC",ByteBuffer.wrap(normal));parse(fork,of,"avcC",ByteBuffer.wrap(normal));row("avcC_failed_reparse_legacy_profile_partial_assignment",parse(base,ob,"avcC",ByteBuffer.wrap(partial)),parse(fork,of,"avcC",ByteBuffer.wrap(partial)));need(((Number)get(of,"getProfile")).intValue()==99,"legacy profile not reset");unobserved(of,"avcC");
            // Nonzero caller position/read-only slices preserve actual consumption.
            byte[]pref=allocate(normal.length+4);System.arraycopy(normal,0,pref,2,normal.length);ByteBuffer x=ByteBuffer.wrap(pref).position(2).limit(normal.length+2).asReadOnlyBuffer(),y=ByteBuffer.wrap(pref).position(2).limit(normal.length+2).asReadOnlyBuffer();
            ob=base.box("avcC");of=fork.box("avcC");row("avcC_offset_readonly",parse(base,ob,"avcC",x),parse(fork,of,"avcC",y));need(Boolean.TRUE.equals(get(of,"hasOriginalParseObservation")),"readonly parse observations");
            ob=base.box("avcC");of=fork.box("avcC");row("avcC_byte_order_not_forced",parse(base,ob,"avcC",ByteBuffer.wrap(normal).order(ByteOrder.LITTLE_ENDIAN)),parse(fork,of,"avcC",ByteBuffer.wrap(normal).order(ByteOrder.LITTLE_ENDIAN)));
            byte[]tail=allocate(normal.length+2);System.arraycopy(normal,0,tail,0,normal.length);ob=base.box("avcC");of=fork.box("avcC");row("avcC_unconsumed_tail_original_semantics",parse(base,ob,"avcC",ByteBuffer.wrap(tail)),parse(fork,of,"avcC",ByteBuffer.wrap(tail)));
            // Existing builder APIs must not fabricate original parse provenance.
            Object db=fork.box("dref").getClass().getMethod("createDataRefBox").invoke(null);unobserved(db,"dref");cases++;System.out.println(json(map("case","dref_builder_unobserved","result","PASS_NONMEDIA_METADATA")));
            Class<?>sample=Class.forName("org.jcodec.containers.mp4.boxes.SampleEntry",false,fork.loader);Object array=Array.newInstance(sample,0);Object sb=fork.box("stsd").getClass().getMethod("createSampleDescriptionBox",array.getClass()).invoke(null,array);unobserved(sb,"stsd");cases++;System.out.println(json(map("case","stsd_builder_unobserved","result","PASS_NONMEDIA_METADATA")));
            Object ab=fork.box("avcC").getClass().getMethod("createAvcCBox",int.class,int.class,int.class,int.class,List.class,List.class).invoke(null,66,0,40,4,new ArrayList<>(),new ArrayList<>());unobserved(ab,"avcC");cases++;System.out.println(json(map("case","avcC_builder_unobserved","result","PASS_NONMEDIA_METADATA")));
            Object empty=fork.box("avcC").getClass().getMethod("createEmpty").invoke(null);unobserved(empty,"avcC");cases++;System.out.println(json(map("case","avcC_createEmpty_unobserved","result","PASS_NONMEDIA_METADATA")));
            for(String type:new String[]{"dref","stsd","avcC"}){repeated(base,fork,type);writeIsNotObservation(base,fork,type);}
            for(String type:new String[]{"dref","stsd"}){byte[]input=parent(0,1,type.equals("dref")?"alis":"free");Object ub=base.withoutFactory(type),uf=fork.withoutFactory(type);Outcome old=parse(base,ub,type,ByteBuffer.wrap(input)),patched=parse(fork,uf,type,ByteBuffer.wrap(input));row(type+"_original_child_missing_factory_exception",old,patched);need(old.exception!=null,"original child exception");unobserved(uf,type);}
            byte[]firstAlias=parent(0,1,"alis");ByteBuffer failedChild=ByteBuffer.wrap(allocate(32));failedChild.putInt(0).putInt(2);
            for(int flags:new int[]{1,0})failedChild.putInt(12).put((byte)'a').put((byte)'l').put((byte)'i').put((byte)'s').putInt(flags);
            Object db0=base.box("dref"),df0=fork.box("dref");parse(base,db0,"dref",ByteBuffer.wrap(firstAlias));parse(fork,df0,"dref",ByteBuffer.wrap(firstAlias));
            Outcome da=parse(base,db0,"dref",failedChild.duplicate().flip()),df=parse(fork,df0,"dref",failedChild.duplicate().flip());row("dref_partial_child_append_then_bounded_alias_failure",da,df);need(da.exception!=null&&((List<?>)get(df0,"getBoxes")).size()==2,"legacy successful child append before failure retained");unobserved(df0,"dref");
            for(String type:new String[]{"dref","stsd","avcC"})readonlyObservation(base,fork,type);
            need(cases==79&&payload<4096,"exact79cases payload small");
        }
    }
    public static void main(String[]args)throws Exception {
        need(args.length==0,"no selection/media arguments");long start=System.nanoTime();startNano=start;
        Thread worker=new Thread(()->{try{runAll(start);}catch(Throwable t){failure=t;stopped=true;}finally{for(Api api:loaderOwners){try{api.close();}catch(Throwable t){unknown=true;if(failure==null)failure=t;}}bodyComplete=true;endNano=System.nanoTime();}},"independent-observation01-original-metadata-worker");originalWorker=worker;worker.setDaemon(false);worker.start();worker.join(5000);
        if(worker.isAlive()){unknown=true;stopped=true;System.out.println(json(map("status","UNKNOWN_ORIGINAL_WORKER_PENDING")));}
        worker.join();long elapsed=endNano-start;if(elapsed<0||elapsed>=MAX_NANOS)unknown=true;
        List<Object>owners=new ArrayList<>();boolean closed=loaderOwners.size()==2;for(Api api:loaderOwners){owners.add(api.owner());closed&=api.openReturned&&api.closeReturned;}need(payload+2048<=8192,"8KiB payload allowance");
        boolean success=bodyComplete&&!unknown&&failure==null&&closed&&cases==79;
        System.out.println(json(map("status",success?"INDEPENDENT_METADATA_PARSE_COMPLETE_NOT_MEDIA_QUALIFICATION":"INDEPENDENT_METADATA_FAILED_OR_UNKNOWN_NO_RETRY","cases",cases,"explicitBytePayload",payload,"matureHeaderScratchAllowance",2048,"metadataLimit",8192,"bodyElapsedNanos",elapsed,"sameOriginalWorkerJoined",true,"workerBodyComplete",bodyComplete,"unknownSticky",unknown,"originalLoaderOwners",owners,"twoOriginalLoadersCloseReturned",closed,"failureClass",failure==null?null:failure.getClass().getName(),"failureMessage",failure==null?null:String.valueOf(failure.getMessage()),"mediaReads",0,"encoderDecoderDemuxMuxerMainRuns",0,"reflectionUse","public API invocation only, no fields/setAccessible/state edits")));
        if(!success)throw new AssertionError("Independent original metadata test failed; no retry",failure);
    }
}
