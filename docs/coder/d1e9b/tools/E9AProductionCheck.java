package com.videokit.spike.e4;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.lang.reflect.Field;
import java.util.*;
import java.util.concurrent.*;

/** Direct production PC supervisor/Processes/console and current-grant checks; no Android process. */
public final class E9AProductionCheck {
    interface Call {void run()throws Exception;}
    static int assertions;static Path out,reference;static String javaExe,classpath;
    static void ok(boolean v){assertions++;if(!v)throw new AssertionError("assertion="+assertions);}
    static void reject(Call c)throws Exception{boolean no=false;try{c.run();}catch(Exception e){no=true;}ok(no);}
    static List<String> child(String mode,Path release,Path ready){return List.of(javaExe,"-cp",classpath,E9AProductionCheck.class.getName(),"CHILD",mode,release.toString(),ready.toString());}
    static void until(CallCondition condition,long millis)throws Exception{long stop=System.nanoTime()+millis*1000000;while(!condition.get()){if(System.nanoTime()-stop>=0)throw new IOException("FINITE_TEST_WAIT");Thread.sleep(10);}}
    interface CallCondition {boolean get()throws Exception;}
    static E9Record query(E9PcSupervisor s,String command)throws Exception{return query(s.port,s.handle,command);}
    static E9Record query(int port,String handle,String command)throws Exception{return E9PcClient.command(port,handle,command,null);}
    static E9Record operation(int port,String handle,String id)throws Exception{return E9PcClient.command(port,handle,"OP",id);}
    static void childMain(String mode,Path release,Path ready)throws Exception{
        Files.writeString(ready,"actualChildPid="+ProcessHandle.current().pid()+"\n",StandardCharsets.US_ASCII,StandardOpenOption.CREATE_NEW);
        if(mode.equals("SHORT_RESPONSE")){E9Record frame=new E9Record(E9Record.map("kind","transport"),1024);System.out.println("Broadcast completed: result=1, data=\"E9:"+E9Record.pack(frame.bytes())+"\"");System.out.flush();return;}
        if(mode.equals("EARLY_EOF"))System.out.close();
        else{System.out.println("CHILD_READY");if(mode.equals("OUTPUT_BOUND"))System.out.print("X".repeat(131072));System.out.flush();}
        long end=System.nanoTime()+15_000_000_000L;while(!Files.exists(release)&&System.nanoTime()-end<0)Thread.sleep(10);
        // Fixture's own normal finite exit, not a kill/close receipt supplied by the controller.
        if(!Files.exists(release))throw new IOException("TEST_CHILD_SELF_FUSE");
    }
    static void fixtureMain(String mode,Path base)throws Exception{
        Path release=base.resolve("release"),ready=base.resolve("child-ready");boolean[] fault={false};
        E9PcSupervisor owner=new E9PcSupervisor("REAL_PC_FIXTURE_"+mode,(point,id)->{if(mode.equals("READER_ERROR")&&point.equals("READ_AFTER")&&!fault[0]){fault[0]=true;throw new IOException("INJECTED_READ_PLATFORM_EXCEPTION");}
            if(mode.equals("CLOSE_LATCH")&&point.equals("STDOUT_CLOSE_BEFORE")){Files.writeString(base.resolve("close-entered"),id,StandardOpenOption.CREATE_NEW);long end=System.nanoTime()+10_000_000_000L;while(!Files.exists(base.resolve("close-release"))&&System.nanoTime()-end<0)Thread.sleep(10);if(!Files.exists(base.resolve("close-release")))throw new IOException("FINITE_CLOSE_LATCH");}
            if(mode.equals("CLOSE_UNKNOWN")&&point.equals("STDOUT_CLOSE_AFTER"))throw new IOException("PLATFORM_CLOSE_RESULT_UNKNOWN_AFTER_NATIVE_CLOSE");});
        Files.write(base.resolve("supervisor.json"),owner.status().bytes(),StandardOpenOption.CREATE_NEW);Throwable failure=null;long begin=System.nanoTime();
        try{if(mode.equals("CONTROL5"))new E9HostDeployment.Processes(owner).runControl(child(mode,release,ready),32768,false);else owner.run("FAULT_FIXTURE",child(mode,release,ready),mode.equals("OUTPUT_BOUND")?32:32768,800_000_000L,false);}
        catch(Throwable t){failure=t;}
        try{E9HostManager.console(owner,System.in,c->{throw new IOException("NO_CONSOLE_BUSINESS_IN_FIXTURE");});}catch(Throwable t){if(failure==null)failure=t;else failure.addSuppressed(t);}
        E9PcSupervisor.Operation op=owner.operations().get(0);Files.write(base.resolve("main-returned.json"),new E9Record(E9Record.map("kind","mainFixtureBoundary","pc",E9Record.pack(owner.status().bytes()),"operation",op.id,"operationState",E9Record.pack(op.status().bytes()),"elapsedNanos",Long.toString(System.nanoTime()-begin)),16384).bytes(),StandardOpenOption.CREATE_NEW);
        if(failure!=null)throw new IOException("FIXTURE_EXPECTED_NONQUALIFIED",failure);
    }
    static final class Capture implements Runnable {
        final InputStream in;final Path path;volatile Throwable failure;Capture(InputStream in,Path path){this.in=in;this.path=path;}
        public void run(){try(InputStream original=in;OutputStream file=Files.newOutputStream(path,StandardOpenOption.CREATE_NEW)){byte[] b=new byte[2048];int total=0;for(int n;(n=original.read(b))!=-1;){total+=n;if(total>131072)throw new IOException("TEST_PIPE_CAPTURE_BOUND");file.write(b,0,n);}}catch(Throwable t){failure=t;}}
    }
    static void processBoundary(String mode)throws Exception{
        Path base=out.resolve(mode);Files.createDirectories(base);List<String> argv=List.of(javaExe,"-cp",classpath,E9AProductionCheck.class.getName(),"MANAGER_FIXTURE",mode,base.toString());
        Files.writeString(base.resolve("argv.txt"),String.join("\n",argv)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
        Process manager=new ProcessBuilder(argv).start();Capture output=new Capture(manager.getInputStream(),base.resolve("stdout.txt")),error=new Capture(manager.getErrorStream(),base.resolve("stderr.txt"));Thread readOut=new Thread(output,"test-original-manager-out"),readErr=new Thread(error,"test-original-manager-err");readOut.start();readErr.start();
        try{
            until(()->Files.exists(base.resolve("child-ready")),4000);ok(manager.isAlive());
            if(mode.equals("CONSOLE_OVERFLOW"))manager.getOutputStream().write("X".repeat(17000).getBytes(StandardCharsets.US_ASCII));
            if(mode.equals("CONSOLE_TRUNCATED"))manager.getOutputStream().write("{\"e9\":1".getBytes(StandardCharsets.US_ASCII));
            manager.getOutputStream().close();until(()->Files.exists(base.resolve("main-returned.json")),8000);Thread.sleep(100);
            E9Record info=E9Record.parse(Files.readAllBytes(base.resolve("supervisor.json")),4096),boundary=E9Record.parse(Files.readAllBytes(base.resolve("main-returned.json")),16384);int port=(int)info.number("port",65535);String handle=info.get("handle");
            ok(manager.isAlive());E9Record state=query(port,handle,"STATUS");ok(state.get("ingressClosed").equals("true"));ok(state.number("liveProcesses",96)==1);ok(state.number("unreturnedOperations",96)==1);ok(state.get("dependenciesStopped").equals("true"));
            E9Record op=operation(port,handle,boundary.get("operation"));ok(op.get("verdict").equals("PENDING"));ok(op.get("processAlive").equals("true"));ok(op.get("allReturned").equals("false"));
            if(mode.equals("EARLY_EOF")||mode.equals("READER_ERROR")||mode.equals("OUTPUT_BOUND")){ok(op.get("readerReturned").equals("true"));ok(op.get("stdout").equals("CLOSED"));}
            if(mode.equals("CONTROL5")){ok(op.number("budgetNanos",Long.MAX_VALUE)==E9PcSupervisor.CONTROL_NS);long elapsed=boundary.number("elapsedNanos",Long.MAX_VALUE);ok(elapsed>=5_000_000_000L&&elapsed<6_500_000_000L);}
            Files.writeString(base.resolve("release"),"fixture normal exit now permitted",StandardCharsets.US_ASCII,StandardOpenOption.CREATE_NEW);
            if(mode.equals("CLOSE_LATCH")||mode.equals("CLOSE_UNKNOWN")){
                if(mode.equals("CLOSE_LATCH"))until(()->Files.exists(base.resolve("close-entered")),2000);
                until(()->operation(port,handle,boundary.get("operation")).get("exitObserved").equals("true"),2000);E9Record closing=operation(port,handle,boundary.get("operation"));ok(!closing.get("processAlive").equals("true"));ok(closing.get("allReturned").equals("false"));ok(manager.isAlive());
                if(mode.equals("CLOSE_LATCH")){ok(closing.get("stdout").equals("CLOSING"));Files.writeString(base.resolve("close-release"),"actual close may now run",StandardOpenOption.CREATE_NEW);}
                else{
                    ok(closing.get("stdout").equals("UNKNOWN"));Files.write(base.resolve("unknown-hold-before-fixture-teardown.json"),closing.bytes(),StandardOpenOption.CREATE_NEW);
                    ok(manager.descendants().filter(ProcessHandle::isAlive).allMatch(d->d.info().command().map(command->Paths.get(command).getFileName().toString().equalsIgnoreCase("conhost.exe")).orElse(false)));Files.write(base.resolve("fixture-teardown.json"),new E9Record(E9Record.map("kind","testFixtureTeardown","managerPid",Long.toString(manager.pid()),"originalCloseAck","false","productionExitAllowed","false","originalChildProcessExited","true","remainingChildren","ONLY_WINDOWS_CONSOLE_HOST_ALLOWED","reason","END_FINITE_UNKNOWN_HOLD_TEST_NOT_A_CLOSE_RECEIPT"),2048).bytes(),StandardOpenOption.CREATE_NEW);
                    // Test-controller cleanup ONLY after proving production refuses exit and all test children exited.
                    // No kill exists in the production owner; no original holder is marked CLOSED by this cleanup.
                    manager.destroyForcibly();
                }
            }
            ok(manager.waitFor(5000,TimeUnit.MILLISECONDS));ok(manager.exitValue()!=0);readOut.join(1000);readErr.join(1000);ok(!readOut.isAlive()&&!readErr.isAlive()&&output.failure==null&&error.failure==null);
            String log=Files.readString(base.resolve("stderr.txt"));ok(log.contains("E9_PC_ISOLATION_ACCEPTED")&&log.contains(handle));if(mode.equals("CLOSE_UNKNOWN"))ok(!log.contains("E9_PC_CLOSED"));else ok(log.contains("E9_PC_CLOSED"));
        }finally{
            if(!Files.exists(base.resolve("release")))Files.writeString(base.resolve("release"),"fixture failure teardown permits only real normal exit",StandardCharsets.US_ASCII,StandardOpenOption.CREATE_NEW);
            try{manager.getOutputStream().close();}catch(Exception ignored){}
            if(mode.equals("CLOSE_LATCH")&&!Files.exists(base.resolve("close-release")))Files.writeString(base.resolve("close-release"),"failure fixture releases only actual original close",StandardOpenOption.CREATE_NEW);
            manager.waitFor(17000,TimeUnit.MILLISECONDS);readOut.join(1000);readErr.join(1000);
        }
    }
    static E9ProductionSelfCheck.Fixture fixture(String name)throws Exception{return new E9ProductionSelfCheck.Fixture(name);}
    static void transport()throws Exception{
        E9Record dummy=new E9Record(E9Record.map("kind","identityRequest","handle",E9TestFiles.uuid("transport")),1024);List<String> launch=E9HostManager.nonWaitingLaunch("adb.exe",dummy);ok(!launch.contains("-w")&&launch.contains("-r"));ok(launch.contains("com.videokit.app.test/com.videokit.spike.e4.E9MigrationInstrumentation"));
        E9ProductionSelfCheck.Fixture f=fixture("transport");E9ProductionSelfCheck.ActorRun a=f.actor(1,"NONE");a.run.identify();
        E9Record snapshot=a.run.observeStatus(a.actor.handle,1);ok(snapshot.number("statuses",3)==1&&snapshot.number("commandSeq",8)==1);
        E9Record frame=new E9Record(E9Record.map("kind","transport","snapshot",E9Record.pack(snapshot.bytes()),"actor",E9Record.pack(a.actor.record.bytes()),"returned",E9Record.pack(a.run.returnProof().bytes()),"mode","REGISTERED_MIGRATION","pid",Integer.toString(a.actor.pid),"uid","10221"),8192);
        byte[] response=("Broadcasting: Intent {...}\nBroadcast completed: result=1, data=\"E9:"+E9Record.pack(frame.bytes())+"\"\n").getBytes(StandardCharsets.US_ASCII);ok(E9HostManager.broadcastFrame(response).hash().equals(frame.hash()));
        ok(E9HostManager.checkTransport(frame,a.actor.record,1,null,"REGISTERED_MIGRATION").actor.hash().equals(a.actor.hash()));
        reject(()->E9HostManager.checkTransport(frame,a.actor.record,1,snapshot,"REGISTERED_MIGRATION"));
        reject(()->E9HostManager.checkTransport(frame,E9ProductionSelfCheck.changed(a.actor.record,"handle",E9TestFiles.uuid("wrong-handle"),2048),1,null,"REGISTERED_MIGRATION"));
        reject(()->E9HostManager.checkTransport(frame,a.actor.record,1,null,"READ_ONLY_IDENTITY"));
        E9Record readOnly=E9ProductionSelfCheck.changed(frame,"mode","READ_ONLY_IDENTITY",8192);ok(E9HostManager.checkTransport(readOnly,a.actor.record,1,null,"READ_ONLY_IDENTITY").actor.hash().equals(a.actor.hash()));
        ok(E9HostManager.nonWaitingLaunch("adb.exe",dummy,"READ_ONLY_IDENTITY").contains("READ_ONLY_IDENTITY"));
        reject(()->E9HostManager.broadcastFrame("Broadcast completed: result=0\n".getBytes()));reject(()->E9HostManager.broadcastFrame(Arrays.copyOf(response,response.length-5)));reject(()->E9HostManager.broadcastFrame((new String(response,StandardCharsets.US_ASCII)+new String(response,StandardCharsets.US_ASCII)).getBytes(StandardCharsets.US_ASCII)));
        a.run.observeStatus(a.actor.handle,2);a.run.observeStatus(a.actor.handle,3);reject(()->a.run.observeStatus(a.actor.handle,4));
        List<String> query=E9HostManager.broadcast("adb.exe",a.actor.handle,1,-1,"STATUS");ok(query.contains("-1")&&!query.contains("-w"));f.oldUnchanged();
    }
    static void statusGap()throws Exception{
        E9ProductionSelfCheck.Fixture f=fixture("status-gap");E9ProductionSelfCheck.ActorRun a=f.actor(1,"NONE");a.run.identify();a.run.closeUnstartedWriteIngress();
        reject(()->a.run.observeStatus(a.actor.handle,Integer.MIN_VALUE));E9Record before=a.run.snapshot();ok(before.number("requests",8)==0);
        E9Record s=a.run.observeStatus(a.actor.handle,2);ok(s.number("requests",8)==2&&s.number("statuses",3)==2);ok(s.get("safe").equals("true"));a.run.observeStatus(a.actor.handle,3);reject(()->a.run.observeStatus(a.actor.handle,4));ok(a.io.writes==0);
    }
    static void identityCleanup()throws Exception{
        E9ProductionSelfCheck.Fixture f=fixture("identity-cleanup");E9ProductionSelfCheck.ActorRun a=f.actor(1,"NONE");a.run.identify();a.run.closeUnstartedWriteIngress();a.run.observeStatus(a.actor.handle,1);
        f.registry.captureIdentityForFinish(a.actor,a.run.returnProof().bytes());a.ack();f.registry.captureNormalFinish(1,a.systemLog.getBytes(StandardCharsets.UTF_8),true);ok(a.finishes==1&&a.io.writes==0);
        E9PcSupervisor pc=new E9PcSupervisor("IDENTITY_CLEANUP");pc.retainAuthority(f,null,f.registry::returned);E9PcSupervisor.Remote remote=pc.reserveRemote(a.actor.handle);remote.bind(a.actor);remote.normalFinish(a.run.returnProof(),f.store.read("actors/0001/finish.json"));ok(pc.closeIngressAndSupervise().get("kind").equals("pcClosed"));until(pc::terminated,1000);
        reject(f.registry::sealFinal);reject(()->f.registry.allocate(2,E9TestFiles.uuid("no-migration"),E9TestFiles.uuid("no-migration-handle")));f.oldUnchanged();
    }
    static void noReplay()throws Exception{
        E9ProductionSelfCheck.Fixture f=fixture("no-replay");E9ProductionSelfCheck.ActorRun a=f.actor(1,"NONE");
        E9Record execute=new E9Record(E9Record.map("kind","control","seq","1","command","EXECUTE_COMMIT","handle",a.actor.handle,"intent",E9TestFiles.digest("one-execute")),1024);f.registry.commandIntent(1,execute);
        reject(()->f.registry.commandIntent(1,E9ProductionSelfCheck.changed(execute,"seq","2",1024)));
        E9Record ack=new E9Record(E9Record.map("kind","control","seq","2","command","ACK_FINISH","handle",a.actor.handle,"intent",E9TestFiles.digest("one-ack")),1024);f.registry.commandIntent(1,ack);reject(()->f.registry.commandIntent(1,E9ProductionSelfCheck.changed(ack,"seq","3",1024)));ok(a.io.writes==0);
    }
    static void decodeDeadline()throws Exception{
        Path release=out.resolve("unused-release"),ready=out.resolve("decode-ready");E9PcSupervisor pc=new E9PcSupervisor("DECODE_DEADLINE",(point,id)->{if(point.equals("DECODE_BEFORE"))Thread.sleep(5500);});
        long start=System.nanoTime();reject(()->new E9HostDeployment.Processes(pc).controlFrame(child("SHORT_RESPONSE",release,ready),32768,false));long elapsed=System.nanoTime()-start;ok(elapsed>=5_000_000_000L&&elapsed<6_500_000_000L);E9PcSupervisor.Operation op=pc.operations().get(0);E9Record s=op.status();ok(s.get("decodeEntered").equals("true"));ok(s.get("decodeReturned").equals("false"));ok(!op.resourcesReturned());pc.closeIngressAndSupervise();until(op::resourcesReturned,3000);ok(op.status().get("verdict").equals("PENDING"));until(pc::terminated,3000);
    }
    static void grant()throws Exception{
        E9ProductionSelfCheck.Fixture f=fixture("grant");E9Catalog c=f.complete();E9TestFiles io=new E9TestFiles(f.device);E9ProductionSelfCheck.IO.add(io);E9CurrentObservation o=new E9CurrentObservation(f.device,E9Catalog.fromTrustedRelease(c.record.bytes(),c.record.hash(),"SYNTHETIC_LOCAL"),io);
        ok(o.observe().startsWith("FRESH_E9"));E5AAdmission.requireCurrent();ok(o.actualReturnProven());ok(o.observe().startsWith("BLOCKED"));reject(E5AAdmission::requireCurrent);f.oldUnchanged();
    }
    static long epoch()throws Exception{Field f=E5AAdmission.class.getDeclaredField("observationEpoch");f.setAccessible(true);synchronized(E5AAdmission.class){return f.getLong(null);}}
    static void concurrentGrant()throws Exception{
        E9ProductionSelfCheck.Fixture f=fixture("concurrent");E9Catalog c=f.complete();E9Catalog.Trusted trust=E9Catalog.fromTrustedRelease(c.record.bytes(),c.record.hash(),"SYNTHETIC_LOCAL");E9TestFiles first=new E9TestFiles(f.device),second=new E9TestFiles(f.device);E9ProductionSelfCheck.IO.add(first);E9ProductionSelfCheck.IO.add(second);
        CountDownLatch inside=new CountDownLatch(1),release=new CountDownLatch(1);first.cut=(point,path)->{if(point.equals("GUARD_CLOSE_BEFORE")&&path.endsWith(".owner")){inside.countDown();if(!release.await(3,TimeUnit.SECONDS))throw new IOException("FINITE_GRANT_LATCH");}};
        E9CurrentObservation a=new E9CurrentObservation(f.device,trust,first),b=new E9CurrentObservation(f.device,trust,second);String[] result=new String[2];Thread one=new Thread(()->result[0]=a.observe()),two=new Thread(()->result[1]=b.observe());one.start();ok(inside.await(2,TimeUnit.SECONDS));long old=epoch();two.start();until(()->epoch()>old,1000);reject(E5AAdmission::requireCurrent);release.countDown();one.join(2000);two.join(2000);ok(!one.isAlive()&&!two.isAlive());ok(result[0].contains("SUPERSEDED"));ok(result[1].startsWith("FRESH_E9"));E5AAdmission.requireCurrent();ok(b.observe().startsWith("BLOCKED"));reject(E5AAdmission::requireCurrent);
    }
    static void remote()throws Exception{
        E9ProductionSelfCheck.Fixture f=fixture("remote");E9ProductionSelfCheck.ActorRun a=f.actor(1,"NONE");E9PcSupervisor pc=new E9PcSupervisor("REMOTE_LIFETIME");pc.retainAuthority(f,null,f.registry::returned);E9PcSupervisor.Remote original=pc.reserveRemote(a.actor.handle);original.bind(a.actor);boolean executed=false,finished=false;
        try{
            pc.run("LAUNCHER_ONLY",List.of(javaExe,"-version"),32768,E9PcSupervisor.CONTROL_NS,false);ok(pc.status().number("unresolvedActors",2)==1);
            a.identifyAndBind("NONE");a.run.execute();executed=true;ok(a.runSafe());
            E9Record ack=pc.closeIngressAndSupervise();ok(ack.get("kind").equals("pcIsolationAck"));ok(!pc.terminated());ok(query(pc,"STATUS").number("unresolvedActors",2)==1);
            a.archiveAndFinish();finished=true;original.normalFinish(a.run.returnProof(),f.store.read("actors/0001/finish.json"));until(pc::terminated,2000);ok(pc.operations().get(0).resourcesReturned());
        }finally{
            if(!executed){a.identifyAndBind("NONE");a.run.execute();}if(!finished)a.archiveAndFinish();
            if(!original.returned())original.normalFinish(a.run.returnProof(),f.store.read("actors/0001/finish.json"));pc.closeIngressAndSupervise();until(pc::terminated,3000);
        }
    }
    static void custodyPin()throws Exception{
        E9ProductionSelfCheck.Fixture f=fixture("custody-pin");E9ProductionSelfCheck.ActorRun a=f.actor(1,"NONE");a.run.identify();a.run.closeUnstartedWriteIngress();f.registry.captureIdentityForFinish(a.actor,a.run.returnProof().bytes());
        E9PcSupervisor pc=new E9PcSupervisor("CUSTODY_PIN");int[] calls={0};pc.retainAuthority(f,c->{calls[0]++;return pc.status();},f.registry::returned);pc.authorizeCleanup(f.plan.hash());E9PcSupervisor.Remote remote=pc.reserveRemote(a.actor.handle);remote.bind(a.actor);
        try{ok(pc.closeIngressAndSupervise().get("kind").equals("pcIsolationAck"));String command=E9Record.pack(new E9Record(E9Record.map("kind","managerCommand","operation","INSPECT"),1024).bytes());
            ok(E9PcClient.command(pc.port,pc.handle,"CLEANUP",E9TestFiles.digest("wrong-pin")+":"+command).get("kind").equals("pcRejected"));ok(calls[0]==0);
            ok(E9PcClient.command(pc.port,pc.handle,"CLEANUP",f.plan.hash()+":"+command).get("kind").equals("pcSupervisor"));ok(calls[0]==1);
        }finally{a.ack();f.registry.captureNormalFinish(1,a.systemLog.getBytes(StandardCharsets.UTF_8),true);remote.normalFinish(a.run.returnProof(),f.store.read("actors/0001/finish.json"));pc.closeIngressAndSupervise();until(pc::terminated,2000);}
        reject(f.registry::sealFinal);
    }
    static void lateVerdict()throws Exception{
        Path release=out.resolve("late-release"),ready=out.resolve("late-ready");E9PcSupervisor pc=new E9PcSupervisor("LATE_RESPONSE");
        try{reject(()->new E9HostDeployment.Processes(pc).runControl(child("CONTROL5",release,ready),32768,false));E9PcSupervisor.Operation op=pc.operations().get(0);ok(op.status().get("verdict").equals("PENDING"));Files.writeString(release,"real normal exit",StandardOpenOption.CREATE_NEW);until(op::resourcesReturned,3000);ok(op.status().get("verdict").equals("PENDING"));ok(op.status().get("allReturned").equals("true"));reject(()->pc.run("NO_RETRY",List.of(javaExe,"-version"),32768,E9PcSupervisor.CONTROL_NS,false));}
        finally{if(!Files.exists(release))Files.writeString(release,"fixture teardown",StandardOpenOption.CREATE_NEW);pc.closeIngressAndSupervise();until(pc::terminated,3000);}
    }
    public static void main(String[] args)throws Exception{
        javaExe=Paths.get(System.getProperty("java.home"),"bin","java.exe").toString();classpath=System.getProperty("java.class.path");
        if(args[0].equals("CHILD")){childMain(args[1],Paths.get(args[2]),Paths.get(args[3]));return;}if(args[0].equals("MANAGER_FIXTURE")){fixtureMain(args[1],Paths.get(args[2]));return;}
        String which=args[0];out=Paths.get(args[1]);reference=Paths.get(args[2]);Files.createDirectories(out);E9ProductionSelfCheck.output=out;E9ProductionSelfCheck.reference=reference;E9ProductionSelfCheck.selected="E9A-"+which;
        try{switch(which){case "TRANSPORT":transport();break;case "STATUS_GAP":statusGap();break;case "IDENTITY_CLEANUP":identityCleanup();break;case "NO_REPLAY":noReplay();break;case "DECODE_DEADLINE":decodeDeadline();break;case "GRANT":grant();break;case "CONCURRENT_GRANT":concurrentGrant();break;case "REMOTE":remote();break;case "CUSTODY_PIN":custodyPin();break;case "LATE_VERDICT":lateVerdict();break;default:processBoundary(which);}
            boolean realPC=!Set.of("TRANSPORT","STATUS_GAP","IDENTITY_CLEANUP","NO_REPLAY","GRANT","CONCURRENT_GRANT","CUSTODY_PIN").contains(which);
            System.out.println("PASS production_e9a="+which+" assertions="+(assertions+E9ProductionSelfCheck.assertions)+" boundaryAssertions="+assertions+" sharedFixtureAssertions="+E9ProductionSelfCheck.assertions+" realPCProcess="+realPC+" deviceCalls=0");
        }finally{int i=0;for(E9TestFiles io:E9ProductionSelfCheck.IO){Files.write(out.resolve("metadata-platform-"+i+++".txt"),io.trace,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);io.closeNativeFacsimilesAfterAssertions();}}
    }
}
