package com.videokit.spike.e4;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Finite cuts on the original production Store, entry boundary, listener and ProcessBuilder. */
public final class E9BProductionCheck {
    interface Test {void run()throws Exception;}
    interface Condition {boolean get()throws Exception;}
    static Path out;static int checks;static String mode;static boolean pending;
    static void ok(boolean v){checks++;if(!v)throw new AssertionError(mode+" assertion="+checks);}
    static void until(Condition c)throws Exception{long stop=System.nanoTime()+8_000_000_000L;while(!c.get()){if(System.nanoTime()>stop)throw new IOException("FINITE_TEST_WAIT");Thread.sleep(10);}}
    static void rejected(Test t)throws Exception{boolean failed=false;try{t.run();}catch(Exception|Error expected){failed=true;}ok(failed);}
    static void status(Path path,E9PcSupervisor s)throws Exception{Files.write(path,s.status().bytes(),StandardOpenOption.CREATE_NEW);}
    static void end(E9PcSupervisor s,boolean unknown)throws Exception{
        E9Record ack=s.closeIngressAndSupervise();ok(ack.get("kind").equals(unknown?"pcIsolationAck":"pcClosed"));
        if(unknown){pending=true;ok(!s.terminated());ok(s.status().get("allOriginalsReturned").equals("false")||s.status().get("listenerReturned").equals("false"));}
        else until(s::terminated);
        status(out.resolve("final-supervisor.json"),s);
    }
    static void walks()throws Exception{
        E9PcSupervisor s=new E9PcSupervisor(mode);Path root=out.resolve("real-walk-root");Files.createDirectories(root);
        CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);AtomicInteger closes=new AtomicInteger();
        E9Registry.Cut cut=(op,path)->{
            if(op.equals("WALK_CLOSE_BEFORE"))closes.incrementAndGet();
            if(mode.equals("WALK_ALLOCATE")&&op.equals("WALK_ALLOCATE_ENTER")||mode.startsWith("WALK_CLOSE_LATCH")&&op.equals("WALK_CLOSE_BEFORE")){
                entered.countDown();if(!release.await(8,TimeUnit.SECONDS))throw new IOException("FINITE_WALK_LATCH");}
            if(mode.equals("WALK_ALLOCATE_UNKNOWN")&&op.equals("WALK_ALLOCATE_ENTER"))throw new IOException("ALLOCATION_NOT_RETURNED");
            if(mode.equals("WALK_ITERATOR_UNKNOWN")&&op.equals("WALK_ITERATOR"))throw new IOException("ITERATOR_FAILED");
            if(mode.equals("WALK_READ_EXCEPTION")&&op.equals("WALK_READ"))throw new IOException("REAL_WALK_READ_EXCEPTION");
            if(mode.equals("WALK_CLOSE_LATCH_EXCEPTION")&&op.equals("WALK_ITERATE"))throw new IOException("REAL_WALK_ITERATE_EXCEPTION");
            if(mode.equals("WALK_CLOSE_LATCH_ERROR")&&op.equals("WALK_ITERATE"))throw new AssertionError("REAL_WALK_ITERATE_ERROR");
            if((mode.equals("WALK_CLOSE_UNKNOWN")||mode.equals("WALK_ITERATOR_UNKNOWN"))&&op.equals("WALK_CLOSE_AFTER"))throw new IOException("NATIVE_STREAM_CLOSED_NO_JAVA_ACK");
            if(mode.equals("WALK_CLOSE_ERROR")&&op.equals("WALK_CLOSE_AFTER"))throw new AssertionError("NATIVE_STREAM_CLOSED_ERROR");
        };
        E9Registry.Store store=new E9Registry.Store(root,cut);s.retainRegistry(store);AtomicReference<Throwable> error=new AtomicReference<>();
        Thread task=new Thread(()->{try{store.checkTotal();}catch(Exception|Error e){error.set(e);}},"real-original-walk");task.start();
        if(mode.equals("WALK_ALLOCATE")||mode.startsWith("WALK_CLOSE_LATCH")){
            ok(entered.await(5,TimeUnit.SECONDS));ok(!store.returned());ok(store.registered()==1);ok(store.highWater()==1);
            ok(store.originalStates().equals(mode.equals("WALK_ALLOCATE")?"ALLOCATING":"CLOSING"));
            ok(s.closeIngressAndSupervise().get("kind").equals("pcIsolationAck"));ok(!s.terminated());status(out.resolve("inflight-supervisor.json"),s);release.countDown();
        }
        task.join(8000);ok(!task.isAlive());boolean unknown=Set.of("WALK_ALLOCATE_UNKNOWN","WALK_CLOSE_UNKNOWN","WALK_ITERATOR_UNKNOWN","WALK_CLOSE_ERROR").contains(mode);
        if(unknown){ok(!store.returned());ok(!store.usable());ok(store.registered()==1);ok(store.originalStates().equals(mode.equals("WALK_CLOSE_ERROR")?"CLOSING":"UNKNOWN"));rejected(store::checkTotal);ok(store.walkRegistrations()==1);ok(closes.get()==(mode.equals("WALK_ALLOCATE_UNKNOWN")?0:1));end(s,true);}
        else{ok(store.returned());ok(store.registered()==0);ok(closes.get()==1);if(!mode.equals("WALK_NORMAL")&&!mode.equals("WALK_ALLOCATE"))ok(error.get()!=null&&!store.usable());until(()->!s.status().get("allOriginalsReturned").equals("false"));if(s.status().get("ingressClosed").equals("true")){until(s::terminated);status(out.resolve("final-supervisor.json"),s);}else end(s,false);}
    }
    static void entry()throws Exception{
        E9ProductionSelfCheck.output=out;E9ProductionSelfCheck.selected=mode;E9ProductionSelfCheck.reference=Paths.get(System.getProperty("reference"));
        E9ProductionSelfCheck.Fixture f=new E9ProductionSelfCheck.Fixture("entry-fixture",null,!mode.equals("MANAGER_INIT_UNKNOWN"));
        boolean releaseCase=mode.equals("ACTIVATION_RELEASE_UNKNOWN"),known=mode.equals("EXPORT_SYNTHETIC_REJECTED");
        E9Catalog catalog=(releaseCase||known)?f.complete():null;AtomicBoolean enabled=new AtomicBoolean(!releaseCase);AtomicInteger closeCalls=new AtomicInteger();
        E9Registry.Cut cut=(op,path)->{if(enabled.get()&&op.equals(mode.equals("ACTIVATION_FILE_UNKNOWN")?"CLOSE_AFTER":"WALK_CLOSE_AFTER")){closeCalls.incrementAndGet();throw new IOException("ORIGINAL_ENTRY_CLOSE_UNKNOWN");}};
        E9PcSupervisor s=new E9PcSupervisor(mode);AtomicBoolean after=new AtomicBoolean();
        rejected(()->E9HostRegistry.boundary(s,()->{
            if(mode.startsWith("MANAGER")){E9HostManager.prepareRegistry(s,f.store.root,f.trust,mode.equals("MANAGER_INIT_UNKNOWN")?"NEW":f.registry.head(),cut);}
            else{
                E9Registry registry=E9HostActivationSession.openReviewedRegistry(s,f.store.root,f.trust,f.registry.head(),known?null:cut);
                if(releaseCase){enabled.set(true);registry.recordActivationRelease(E9ProductionSelfCheck.activationRelease(f,catalog));}
                else E9ActivationPolicyExport.export(registry,out.resolve("must-not-export.json"));
            }after.set(true);
        }));
        ok(!after.get());ok(s.operations().isEmpty());ok(s.status().get("unresolvedActors").equals("0"));ok(!Files.exists(out.resolve("must-not-export.json")));
        if(known){ok(closeCalls.get()==0);ok(s.status().get("registryReturned").equals("true"));until(s::terminated);status(out.resolve("final-supervisor.json"),s);}
        else{ok(closeCalls.get()==1);ok(s.status().get("registryReturned").equals("false"));ok(s.status().get("registryOwned").equals("1"));end(s,true);}
    }
    static E9Record query(E9PcSupervisor s)throws Exception{return E9PcClient.command(s.port,s.handle,"STATUS",null);}
    static void accepts()throws Exception{
        boolean unknown=mode.contains("LISTENER_UNKNOWN"),process=mode.endsWith("PROCESS"),walk=mode.equals("ACCEPT_WALK");
        AtomicInteger listenerClose=new AtomicInteger();CountDownLatch unprocessed=new CountDownLatch(1),release=new CountDownLatch(1);AtomicInteger actualSockets=new AtomicInteger();
        E9PcSupervisor s=new E9PcSupervisor(mode,(point,id)->{
            if(point.equals("LISTENER_CLOSE_BEFORE")){listenerClose.incrementAndGet();if(mode.contains("UNKNOWN_BEFORE"))throw new IOException("LISTENER_CLOSE_NOT_RETURNED");}
            if(point.equals("LISTENER_CLOSE_AFTER")&&unknown)throw new IOException("REAL_LISTENER_CLOSED_NO_JAVA_ACK");
            if(point.equals("ACCEPT_UNPROCESSED")){int n=actualSockets.incrementAndGet();if(n==128&&mode.equals("ACCEPT_UNPROCESSED")){unprocessed.countDown();if(!release.await(8,TimeUnit.SECONDS))throw new IOException("FINITE_ACCEPT_LATCH");}}
        });
        Thread work=null;Path signal=out.resolve("child-release");CountDownLatch walkEntered=new CountDownLatch(1),walkRelease=new CountDownLatch(1);
        if(process){String java=Paths.get(System.getProperty("java.home"),"bin/java.exe").toString();List<String> argv=List.of(java,"-cp",System.getProperty("java.class.path"),E9BProductionCheck.class.getName(),"CHILD",signal.toString());Files.writeString(out.resolve("child-argv.txt"),String.join("\n",argv));work=new Thread(()->{try{s.run("REAL_CHILD",argv,32768,400_000_000L,false);}catch(Exception expected){}});work.start();until(()->!s.operations().isEmpty()&&s.operations().get(0).processAlive());}
        if(walk){Path root=out.resolve("real-walk-root");Files.createDirectories(root);E9Registry.Store store=new E9Registry.Store(root,(op,path)->{if(op.equals("WALK_CLOSE_BEFORE")){walkEntered.countDown();if(!walkRelease.await(8,TimeUnit.SECONDS))throw new IOException("FINITE_ACCEPT_WALK_LATCH");}});s.retainRegistry(store);work=new Thread(()->{try{store.checkTotal();}catch(Exception e){throw new RuntimeException(e);}});work.start();ok(walkEntered.await(5,TimeUnit.SECONDS));}
        int serial=mode.equals("ACCEPT_CONCURRENT")?126:127;for(int i=0;i<serial;i++)ok(query(s).get("kind").equals("pcSupervisor"));
        List<Thread> requests=new ArrayList<>();AtomicInteger replies=new AtomicInteger();int clients=mode.equals("ACCEPT_CONCURRENT")?4:1;
        for(int i=0;i<clients;i++){Thread t=new Thread(()->{try{if(query(s).get("kind").equals("pcSupervisor"))replies.incrementAndGet();}catch(Exception expected){}});requests.add(t);t.start();}
        if(mode.equals("ACCEPT_UNPROCESSED")){ok(unprocessed.await(5,TimeUnit.SECONDS));ok(s.status().get("accepted").equals("128"));ok(actualSockets.get()==128);ok(!s.status().get("allOriginalsReturned").equals("true"));status(out.resolve("accepted-unprocessed.json"),s);release.countDown();}
        for(Thread t:requests){t.join(6500);ok(!t.isAlive());}ok(replies.get()==128-serial);until(()->s.status().get("accepted").equals("128"));ok(s.status().get("acceptReservations").equals("0"));ok(listenerClose.get()==1);ok(s.status().get("admissionExhausted").equals("true"));
        // A queued TCP handshake is not an accept. No 129th application accept/handler is permitted.
        for(int i=0;i<3;i++)rejected(()->{try(Socket extra=new Socket()){extra.connect(new InetSocketAddress("127.0.0.1",s.port),200);extra.setSoTimeout(200);extra.getOutputStream().write(("STATUS "+s.handle+"\n").getBytes(StandardCharsets.US_ASCII));if(extra.getInputStream().read()!=-1)throw new AssertionError("UNEXPECTED_129TH_HANDLER");throw new EOFException("NO_129TH_REPLY");}});ok(s.status().get("accepted").equals("128"));ok(actualSockets.get()==128);ok(listenerClose.get()==1);
        if(process||walk){ok(s.closeIngressAndSupervise().get("kind").equals("pcIsolationAck"));ok(!s.terminated());ok(s.status().get("allOriginalsReturned").equals("false"));status(out.resolve("exhausted-original-inflight.json"),s);if(process)Files.writeString(signal,"NORMAL_CHILD_RETURN");else walkRelease.countDown();work.join(8000);ok(!work.isAlive());if(unknown){until(()->s.operations().get(0).resourcesReturned());end(s,true);}else{until(s::terminated);status(out.resolve("final-supervisor.json"),s);}}
        else end(s,unknown);
    }
    static void acceptFailure()throws Exception{
        CountDownLatch entered=new CountDownLatch(1);E9PcSupervisor s=new E9PcSupervisor(mode,(point,id)->{if(point.equals("ACCEPT_BEFORE")){entered.countDown();throw new IOException("REAL_ACCEPT_PLATFORM_FAILURE_NO_RETURN");}});
        ok(entered.await(5,TimeUnit.SECONDS));until(()->s.status().get("accepted").equals("1"));
        Thread boundary=new Thread(()->{try{E9HostRegistry.boundary(s,()->{});}catch(Exception e){throw new RuntimeException(e);}},"actual-entry-blocked-on-accept-unknown");boundary.start();
        Thread.sleep(300);ok(boundary.isAlive());ok(!s.terminated());ok(s.status().get("allOriginalsReturned").equals("false"));ok(s.status().get("acceptReservations").equals("0"));
        try(Socket client=new Socket()){client.connect(new InetSocketAddress("127.0.0.1",s.port),200);client.setSoTimeout(200);client.getOutputStream().write(("STATUS "+s.handle+"\n").getBytes(StandardCharsets.US_ASCII));rejected(()->{if(client.getInputStream().read()!=-1)throw new AssertionError("ACCEPT_AFTER_UNKNOWN");throw new EOFException();});}
        ok(s.status().get("accepted").equals("1"));status(out.resolve("final-supervisor.json"),s);pending=true;
    }
    public static void main(String[] args)throws Exception{
        if(args[0].equals("CHILD")){long end=System.nanoTime()+15_000_000_000L;while(!Files.exists(Paths.get(args[1]))&&System.nanoTime()<end)Thread.sleep(10);if(!Files.exists(Paths.get(args[1])))throw new IOException("FINITE_CHILD_FUSE");System.out.println("ACTUAL_NORMAL_CHILD_EXIT");return;}
        mode=args[0];out=Paths.get(args[1]);Files.createDirectories(out);
        if(mode.equals("ACCEPT_EXCEPTION"))acceptFailure();else if(mode.startsWith("WALK"))walks();else if(mode.startsWith("ACCEPT"))accepts();else entry();
        String result="{\"status\":\"PASS_FINITE_LOCAL_SCOPE\",\"assertions\":"+checks+",\"productionExitAllowed\":"+!pending+",\"originalCloseAck\":"+!pending+",\"sharedFixtureAssertions\":"+E9ProductionSelfCheck.assertions+"}\n";
        Files.writeString(out.resolve("result.json"),result,StandardOpenOption.CREATE_NEW);System.out.println(mode+" "+result);
    }
}
