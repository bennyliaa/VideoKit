package videokit.e1;

import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

/** Opt-in metadata-only probe of files created by check-java-bridge.py. */
public final class JavaBridgeProbe {
    static final List<String> checks=Collections.synchronizedList(new ArrayList<>());
    static void check(boolean value,String reason){if(!value)throw new IllegalStateException(reason);checks.add(reason);}
    static String json(Object value){
        if(value==null)return "null";if(value instanceof Number||value instanceof Boolean)return value.toString();
        if(value instanceof Map<?,?> map){List<String> rows=new ArrayList<>();for(var entry:map.entrySet())rows.add(json(entry.getKey().toString())+":"+json(entry.getValue()));return "{"+String.join(",",rows)+"}";}
        if(value instanceof Collection<?> list){List<String> rows=new ArrayList<>();for(Object item:list)rows.add(json(item));return "["+String.join(",",rows)+"]";}
        String text=value.toString();StringBuilder out=new StringBuilder("\"");
        for(char c:text.toCharArray()){if(c=='"'||c=='\\')out.append('\\').append(c);else if(c<32)out.append(String.format("\\u%04x",(int)c));else out.append(c);}return out.append('"').toString();
    }
    static Map<String,Object> probe(Path root,String mode)throws Exception {
        Path base=Path.of(JavaHelper.class.getProtectionDomain().getCodeSource().getLocation().toURI()).getParent().getParent();
        Path allowed=base.resolve("selfcheck").toRealPath();root=root.toAbsolutePath().normalize();
        check(root.equals(root.toRealPath())&&root.startsWith(allowed)&&root.getFileName().toString().startsWith("java-bridge-"),"OWNED_PROBE_ROOT_ONLY");
        Path input=root.resolve("L.bin"),decoy=root.resolve("C.bin");check(Files.size(input)==4096&&Files.size(decoy)==17,"OWNED_PROBE_FIXTURES_ONLY");
        CountDownLatch entered=new CountDownLatch(1),closeAttempted=new CountDownLatch(1),release=new CountDownLatch(1);
        JavaHelper.IdentityQuery real=JavaHelper.bridge(),query=real;
        if(mode.equals("field-missing"))query=JavaHelper.bridge("notAFileDescriptorField","GetFileInformationByHandle");
        if(mode.equals("field-type"))query=JavaHelper.bridge("fd","GetFileInformationByHandle");
        if(mode.equals("symbol-missing"))query=JavaHelper.bridge("handle","VideoKitDeliberatelyMissingIdentitySymbol");
        if(mode.equals("query-failure"))query=descriptor->{throw new JavaHelper.BridgeBlocked("SELF_OWNED_INJECTED_QUERY_FAILURE");};
        if(mode.equals("close-race"))query=descriptor->{entered.countDown();check(release.await(1,TimeUnit.SECONDS),"QUERY_GATE_DEADLINE");return real.inspect(descriptor);};
        JavaHelper.Handle handle=new JavaHelper.Handle(input,query);String receipt="";boolean positionUnchanged=false,closeBlocked=false;int distinctPathLength=0;
        Thread queryThread=null,closeThread=null;AtomicReference<Throwable> failure=new AtomicReference<>();
        try {
            if(mode.equals("close-race")) {
                AtomicReference<String> result=new AtomicReference<>();final JavaHelper.Handle raced=handle;
                queryThread=new Thread(()->{try{result.set(raced.openReceipt());}catch(Throwable error){failure.set(error);}},"E2A-owned-query");
                closeThread=new Thread(()->{closeAttempted.countDown();try{raced.begin(0,"none",false);}catch(Throwable error){failure.set(error);}},"E2A-owned-close");
                queryThread.start();check(entered.await(1,TimeUnit.SECONDS),"QUERY_THREAD_ENTERED");closeThread.start();check(closeAttempted.await(1,TimeUnit.SECONDS),"CLOSE_THREAD_ATTEMPTED");
                long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(1);
                while(closeThread.getState()!=Thread.State.BLOCKED&&closeThread.isAlive()&&System.nanoTime()<end)Thread.onSpinWait();
                closeBlocked=closeThread.getState()==Thread.State.BLOCKED&&raced.calls==0;check(closeBlocked,"CLOSE_MUST_WAIT_ON_ORIGINAL_HANDLE_MONITOR");
                release.countDown();queryThread.join(1500);closeThread.join(1500);
                check(!queryThread.isAlive()&&!closeThread.isAlive()&&failure.get()==null,"RACE_THREADS_ACTUALLY_JOINED");receipt=result.get();
            } else {
                long before=handle.file.getFilePointer();receipt=handle.openReceipt();positionUnchanged=before==handle.file.getFilePointer();
                if(mode.equals("path-separation")) {
                    // Deliberately compare unrelated path metadata; it is never
                    // supplied to the bridge. This is not a rename/replace claim.
                    distinctPathLength=(int)Files.size(decoy);check(distinctPathLength==17,"DECOY_PATH_METADATA");
                    check(handle.opened!=null&&handle.opened.lengthBytes().equals("4096"),"OPENED_DESCRIPTOR_NOT_DECOY_PATH");
                }
            }
            boolean blocked=Set.of("field-missing","field-type","symbol-missing","query-failure","blocked-flags").contains(mode);
            check(handle.identityStatus.equals(blocked?"BLOCKED_VERSION_NOT_PROVEN":"PROVEN"),"EXPECTED_IDENTITY_STATUS");
            check(receipt.split("\\|",-1).length==11&&handle.identityQueries==1,"ONE_QUERY_RECEIPT_HAS_ORIGINAL_PROOF");
            check(handle.reads==0&&handle.seeks==0,"NO_MEDIA_READ_OR_POSITION_MUTATION");
            if(!mode.equals("close-race")) {
                check(positionUnchanged&&handle.state.equals("OWNED_OPEN_RETRYABLE")&&handle.calls==0,"QUERY_RETAINS_OPEN_OWNER_AND_POSITION");
                check(handle.descriptor==handle.file.getFD()&&receipt.equals(handle.openReceipt())&&handle.identityQueries==1,"ORIGINAL_DESCRIPTOR_STRONG_REFERENCE_AND_NO_QUERY_REPLAY");
            }
            if(handle.state.equals("OWNED_OPEN_RETRYABLE"))handle.begin(handle.revision,"none",false);
            check(handle.state.equals("CLOSED_PROVEN")&&handle.calls==1,"ORIGINAL_HANDLE_CLOSE_RETURNED_ONCE");
            Map<String,Object> report=new LinkedHashMap<>();report.put("scope","SELF_OWNED_NON_MEDIA_JAVA_METADATA_PROBE");report.put("status","PASS");report.put("mode",mode);report.put("openReceipt",receipt);
            report.put("identityFailure",handle.identityFailure);report.put("identityAttempts",handle.identityQueries);report.put("nativeCloses",handle.calls);report.put("nativeReads",handle.reads);report.put("nativeSeeks",handle.seeks);report.put("positionUnchanged",positionUnchanged);report.put("closeWaitedForQuery",closeBlocked);report.put("unrelatedPathLength",distinctPathLength);report.put("threadsJoined",queryThread==null||!queryThread.isAlive()&&!closeThread.isAlive());
            report.put("pid",ProcessHandle.current().pid());report.put("javaRuntimeVersion",System.getProperty("java.runtime.version"));report.put("javaVendor",System.getProperty("java.vendor"));report.put("osArch",System.getProperty("os.arch"));report.put("inputFlags",java.lang.management.ManagementFactory.getRuntimeMXBean().getInputArguments());report.put("assertions",checks.size());report.put("checks",new ArrayList<>(checks));return report;
        } finally {
            release.countDown();if(queryThread!=null)queryThread.join(1500);if(closeThread!=null)closeThread.join(1500);
            if((queryThread==null||!queryThread.isAlive())&&(closeThread==null||!closeThread.isAlive())&&handle.state.equals("OWNED_OPEN_RETRYABLE"))handle.begin(handle.revision,"none",false);
        }
    }
    public static void main(String[] args)throws Exception {
        try{check(args.length==3&&args[0].equals("--owned-file-probe"),"EXPLICIT_OWNED_PROBE_REQUIRED");System.out.println(json(probe(Path.of(args[1]),args[2])));}
        catch(Exception error){System.out.println(json(Map.of("scope","SELF_OWNED_NON_MEDIA_JAVA_METADATA_PROBE","status","FAIL","error",error.getClass().getSimpleName()+":"+String.valueOf(error.getMessage()))));System.exit(2);}
    }
}
