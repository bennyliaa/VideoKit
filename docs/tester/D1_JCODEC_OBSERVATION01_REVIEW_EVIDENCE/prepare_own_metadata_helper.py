from pathlib import Path
import hashlib,json
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;OLD=R/'docs/coder/d1jcodec-observation01/checks/com/videokit/observation/MetadataObservationCheck.java'
b=OLD.read_bytes();assert hashlib.sha256(b).hexdigest()=='a4544d6bfc6ab15cfaffc05db7d0e12521878ead380c8e1dbd6ef48d661be6b1'
s=b.decode('utf8').replace('package com.videokit.observation;','package com.videokit.testerobs;').replace('MetadataObservationCheck','IndependentObservationCheck')
s=s.replace('static volatile Throwable failure;','static volatile Throwable failure;\n    static Thread originalWorker;static final List<Api> loaderOwners=new ArrayList<>();')
s=s.replace('final URLClassLoader loader;final Object factory;final Class<?> header;','URLClassLoader loader;Object factory;Class<?> header;final String path;boolean openEntered,openReturned,closeEntered,closeReturned;')
oldConstructor=next(x for x in s.splitlines() if 'Api(String path)' in x)
newConstructor='''        Api(String path)throws Exception{this.path=path;loaderOwners.add(this);openEntered=true;loader=new URLClassLoader(new URL[]{Paths.get(path).toUri().toURL()},ClassLoader.getPlatformClassLoader());header=Class.forName("org.jcodec.containers.mp4.boxes.Header",true,loader);Class<?> f=Class.forName("org.jcodec.containers.mp4.BoxFactory",true,loader);factory=f.getMethod("getDefault").invoke(null);openReturned=true;}'''
s=s.replace(oldConstructor,newConstructor)
oldBox=next(x for x in s.splitlines() if 'Object box(String fourcc)' in x)
s=s.replace(oldBox,'''        Object box(String fourcc)throws Exception{Object h=header.getConstructor(String.class).newInstance(fourcc);if(fourcc.equals("avcC"))return Class.forName("org.jcodec.codecs.h264.mp4.AvcCBox",true,loader).getConstructor(header).newInstance(h);return call(factory,"newBox",new Class<?>[]{header},h);}''')
s=s.replace('public void close()throws Exception{loader.close();}', '''public void close()throws Exception{need(Thread.currentThread()==originalWorker,"same original loader closer");if(closeEntered)return;if(loader==null){unknown=true;return;}closeEntered=true;loader.close();closeReturned=true;}
        Map<String,Object>owner(){return map("path",path,"registeredBeforeLoaderAllocation",true,"openEntered",openEntered,"openReturned",openReturned,"closeEntered",closeEntered,"sameOriginalCloseReturned",closeReturned,"sameOriginalWorkerCloser",true);}''')
s=s.replace('int before,after,limit,remaining;Map<String,Object>view;','int before,after,limit,remaining;Map<String,Object>view,raw;')
s=s.replace('"existingGetterView",view);','"existingGetterView",view,"originalObservation",raw);')
s=s.replace('r.view=a.originalView(box,type);return r;','r.view=a.originalView(box,type);r.raw=a.path.equals(FORK)?observation(box,type):null;return r;')
insert='''    static Map<String,Object> observation(Object box,String type)throws Exception {
        boolean complete=(Boolean)get(box,"hasOriginalParseObservation");Map<String,Object>m=map("observed",complete);
        if(complete){String[]names=type.equals("avcC")?new String[]{"getOriginalConfigurationVersion","getOriginalLengthSizeByte","getOriginalSpsCountByte","getOriginalPpsCountByte"}:new String[]{"getOriginalVersionFlagsWord","getOriginalVersion","getOriginalFlags","getOriginalDeclaredEntryCount"};for(String n:names)m.put(n,get(box,n));}return m;
    }
    static void readonlyObservation(Api base,Api fork,String type)throws Exception {
        byte[]bytes=type.equals("avcC")?avcc():parent(0xaabbccdd,-1,type.equals("dref")?"alis":"free");Object box=fork.box(type);ByteBuffer input=ByteBuffer.wrap(bytes);Outcome result=parse(fork,box,type,input);need(result.exception==null,"readonly observation precondition");int position=input.position();Map<String,Object>legacy=fork.originalView(box,type),first=observation(box,type),second=observation(box,type);need(first.equals(second)&&legacy.equals(fork.originalView(box,type))&&position==input.position(),"new getter mutated input or legacy state");cases++;System.out.println(json(map("case",type+"_readonly_observation_getters","result","PASS_NONMEDIA_METADATA","actual",first,"inputPositionBeforeAfter",position,"legacyUnchanged",true)));
    }
'''
s=s.replace('    static void unobserved(Object box,String type)',insert+'    static void unobserved(Object box,String type)')
s=s.replace('parentCase(base,fork,type,0,0,null,"empty_zero");','parentCase(base,fork,type,0,0,null,"empty_zero");parentCase(base,fork,type,0xff123456,0x80000000,null,"uint32_highbit_no_child_no_alloc");')
oldFresh='for(String type:new String[]{"dref","stsd","avcC"}){unobserved(fork.box(type),type);cases++;'
newFresh='for(String type:new String[]{"dref","stsd","avcC"}){Object oldBox=base.box(type),newBox=fork.box(type);need(oldBox.getClass().getClassLoader()==base.loader&&newBox.getClass().getClassLoader()==fork.loader,"per-type isolated loaders");need(oldBox.getClass().getName().equals(newBox.getClass().getName())&&(type.equals("avcC")?newBox.getClass().getName().equals("org.jcodec.codecs.h264.mp4.AvcCBox"):true),"actual mature type");System.out.println(json(map("classOrigins",type,"baseline",oldBox.getClass().getProtectionDomain().getCodeSource().getLocation().toString(),"fork",newBox.getClass().getProtectionDomain().getCodeSource().getLocation().toString(),"actualClass",newBox.getClass().getName())));unobserved(newBox,type);cases++;'
assert oldFresh in s;s=s.replace(oldFresh,newFresh)
s=s.replace('            need(payload<4096,"payload small");','            for(String type:new String[]{"dref","stsd","avcC"})readonlyObservation(base,fork,type);\n            need(cases==79&&payload<4096,"exact79cases payload small");')
mainAt=s.index('    public static void main(String[]args)')
s=s[:mainAt]+'''    public static void main(String[]args)throws Exception {
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
'''
assert 'Box$LeafBox' not in s and 'setAccessible(' not in s and 'getDeclaredField' not in s and 'private static void main' not in s
out=E/'IndependentObservationCheck.java';assert not out.exists();out.write_text(s,encoding='utf8')
(E/'own-helper-source-provenance.json').write_text(json.dumps(dict(base=str(OLD),baseSha256=hashlib.sha256(b).hexdigest(),newSource=str(out),newSha256=hashlib.sha256(out.read_bytes()).hexdigest(),independentChanges=['new tester package/name','avcC real public constructor in each isolated loader','registered-before-open original loader owners, guarded one close and actual close receipts even failure','original raw getter values included perparse receipt','per-type two true code origins','2 bounded uint32 boundary cases and3 readonlygetter cases;79 total','final summary before failed exit; original worker join/loader returns separately recorded'],coderSourceChanged=False,productionChanged=False,mediaReads=0),indent=2),encoding='utf8')
print('OWN_HELPER_SOURCE_PREPARED; javac/runtime0;79cases planned')
