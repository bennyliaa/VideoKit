package com.videokit.spike.e4;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Actual shared production pre-wire boundary/Registry/Run, original Process/decoder and main exit boundary. */
public final class E10AProductionCheck {
    interface Call {void run()throws Exception;}static int assertions;static String mode;static Path out;static boolean pending;
    static void ok(boolean v){assertions++;if(!v)throw new AssertionError(mode+" assertion="+assertions);}
    static void reject(Call call)throws Exception{boolean denied=false;try{call.run();}catch(Exception expected){denied=true;}ok(denied);}
    static E9Record changed(E9Record r,String k,String v,int max)throws Exception{Map<String,String> m=new TreeMap<>(r.fields());m.put(k,v);return new E9Record(m,max);}
    static final class Driver {
        final E9ProductionSelfCheck.Fixture f;final E9ProductionSelfCheck.ActorRun actor;final E9PcSupervisor supervisor;final E9PcSupervisor.Remote remote;final E9HostDeployment.Processes processes;final E9Record request;
        E9Record latest;int seq=1,wires;boolean custody;byte[] originalIdentity,identify,reserve;
        Driver()throws Exception{
            f=new E9ProductionSelfCheck.Fixture(mode);actor=f.actor(1,"NONE");supervisor=new E9PcSupervisor(mode);supervisor.retainRegistry(f.store);supervisor.retainRegistryAuthority(f.registry);supervisor.retainAuthority(this,null,()->{try{return actor.runSafe()&&f.registry.returned();}catch(Exception unknown){return false;}});processes=new E9HostDeployment.Processes(supervisor);remote=supervisor.reserveRemote(actor.actor.handle);
            Map<String,String> r=new TreeMap<>();for(String k:new String[]{"registry","migration","ordinal","attempt","handle","descriptor","app","test","environment"})r.put(k,actor.actor.record.get(k));request=new E9Record(r,8192);actor.run.identify();originalIdentity=actor.run.returnProof().bytes();control("STATUS");
        }
        E9HostManager.PreparedControl prepare(String action,byte[] proof)throws Exception{return E9HostManager.prepareControl(f.registry,f.store,1,actor.actor.handle,"REGISTERED_MIGRATION",seq,latest,proof,action);}
        void control(String action)throws Exception{
            E9HostManager.PreparedControl p=prepare(action,action.equals("ACK_FINISH")?actor.run.returnProof().bytes():null);seq++;wires++;
            List<String> wire=p.arguments("NOT_A_DEVICE_EXECUTABLE",actor.actor.handle);Files.writeString(out.resolve("wire-"+wires+".txt"),String.join("\n",wire)+"\n",StandardOpenOption.CREATE_NEW);
            switch(action){case "STATUS":actor.run.observeStatus(actor.actor.handle,p.seq);break;case "STOP_DEPENDENCIES":actor.run.stop(actor.actor.handle,p.seq,p.state);break;
                case "EXECUTE_COMMIT":actor.run.bindAndReserve(E9Record.unpack(p.reserve,4096),actor.actor.handle,p.seq,p.state);actor.run.execute();break;
                case "ACK_FINISH":ok(actor.run.acknowledgeFinish(actor.actor.handle,p.seq,p.state,p.archived));break;default:throw new AssertionError();}
            String returned="ABSENT";try{returned=E9Record.pack(actor.run.returnProof().bytes());}catch(IOException unknown){}
            E9Record transport=new E9Record(E9Record.map("kind","transport","snapshot",E9Record.pack(actor.run.snapshot().bytes()),"actor",E9Record.pack(actor.actor.record.bytes()),"returned",returned,"mode","REGISTERED_MIGRATION","pid",Integer.toString(actor.actor.pid),"uid","10221"),8192);
            List<String> argv=List.of(Paths.get(System.getProperty("java.home"),"bin/java.exe").toString(),"-cp",System.getProperty("java.class.path"),E10AProductionCheck.class.getName(),"CHILD_RESPONSE",E9Record.pack(transport.bytes()));Files.writeString(out.resolve("child-"+wires+".argv.txt"),String.join("\n",argv)+"\n",StandardOpenOption.CREATE_NEW);
            E9HostManager.CheckedFrame checked=(E9HostManager.CheckedFrame)processes.controlResponse(argv,32768,custody,raw->{Files.write(out.resolve("child-"+wires+".stdout.txt"),raw,StandardOpenOption.CREATE_NEW);return E9HostManager.checkTransport(E9HostManager.broadcastFrame(raw),request,p.seq,latest,"REGISTERED_MIGRATION");});latest=E9Record.parse(E9Record.unpack(checked.frame.get("snapshot"),4096),4096);if(checked.actor!=null)remote.bind(checked.actor);
            Files.write(out.resolve("frame-"+wires+".json"),checked.frame.bytes(),StandardOpenOption.CREATE_NEW);
        }
        void bind()throws Exception{f.registry.reserve(actor.actor,actor.run.returnProof().bytes(),"NONE");identify=f.store.read("actors/0001/identify.json");reserve=f.store.read("actors/0001/reserve.json");}
        void archive()throws Exception{byte[] proof=actor.run.returnProof().bytes();E9Record r=E9Record.parse(proof,8192);if(r.get("phase").equals("IDENTITY"))f.registry.captureIdentityForFinish(actor.actor,proof);else f.registry.captureReturned(1,proof);}
        void noIntentChange(Call failure)throws Exception{byte[] commands=f.store.read("actors/0001/commands.jsonl"),proof=actor.run.returnProof().bytes();int oldWires=wires,oldSeq=seq;reject(failure);ok(Arrays.equals(commands,f.store.read("actors/0001/commands.jsonl")));ok(Arrays.equals(proof,actor.run.returnProof().bytes()));ok(oldWires==wires&&oldSeq==seq);ok(f.store.returned()&&f.store.usable());}
        void finish()throws Exception{control("ACK_FINISH");ok(actor.finishes==1);f.registry.captureNormalFinish(1,actor.systemLog.getBytes(StandardCharsets.UTF_8),true);remote.normalFinish(E9Record.parse(f.store.read("actors/0001/returned.json"),8192),f.store.read("actors/0001/finish.json"));}
        void end(boolean unknown)throws Exception{
            f.oldUnchanged();for(E9PcSupervisor.Operation o:supervisor.operations())ok(o.resourcesReturned()&&!o.processAlive());
            if(unknown){ok(supervisor.closeIngressAndSupervise().get("kind").equals("pcIsolationAck"));ok(!supervisor.terminated());pending=true;}
            else {E9HostRegistry.boundary(supervisor,()->E9HostManager.console(supervisor,new ByteArrayInputStream(new byte[0]),c->{throw new AssertionError("NO_DEVICE_CONSOLE_COMMAND");}));long end=System.nanoTime()+5_000_000_000L;while(!supervisor.terminated()&&System.nanoTime()<end)Thread.sleep(10);ok(supervisor.terminated());}
            Files.write(out.resolve("final-supervisor.json"),supervisor.status().bytes(),StandardOpenOption.CREATE_NEW);
        }
    }
    static void boundCancel()throws Exception{
        Driver d=new Driver();d.bind();
        if(mode.equals("BOUND_NOT_STOPPED")){reject(d::archive);ok(!d.f.store.exists("actors/0001/returned.json"));}
        d.control("STOP_DEPENDENCIES");ok(d.actor.run.snapshot().get("verdict").equals("PENDING"));ok(!Arrays.equals(d.originalIdentity,d.actor.run.returnProof().bytes()));
        if(mode.equals("BOUND_WRONG_ACTOR")){E9Actor wrong=new E9Actor(changed(d.actor.actor.record,"start","999999",2048));reject(()->d.f.registry.captureIdentityForFinish(wrong,d.actor.run.returnProof().bytes()));}
        if(mode.equals("BOUND_WRONG_RESERVE")||mode.equals("BOUND_WRONG_HEAD")||mode.equals("BOUND_WRONG_PLAN")){
            String rel=mode.equals("BOUND_WRONG_RESERVE")?"actors/0001/reserve.json":mode.equals("BOUND_WRONG_PLAN")?"prepare-deployment.json":"registry.events.jsonl";Path file=d.f.store.root.resolve(rel);byte[] original=Files.readAllBytes(file);byte[] corrupt;
            if(rel.endsWith(".jsonl"))corrupt=(new String(original,StandardCharsets.US_ASCII)+"\n").getBytes(StandardCharsets.US_ASCII);
            else {E9Record old=E9Record.parse(original,8192);corrupt=changed(old,rel.contains("reserve")?"preparePlan":"sourceReview",E9TestFiles.digest("WRONG_SCOPE"),8192).bytes();}
            // Controlled corruption/restore of SYNTHETIC fixture ONLY, never production repair.
            Files.write(file,corrupt,StandardOpenOption.TRUNCATE_EXISTING);reject(d::archive);ok(!d.f.store.exists("actors/0001/returned.json"));Files.write(file,original,StandardOpenOption.TRUNCATE_EXISTING);
        }
        d.archive();ok(Arrays.equals(d.identify,d.f.store.read("actors/0001/identify.json")));ok(Arrays.equals(d.reserve,d.f.store.read("actors/0001/reserve.json")));ok(Arrays.equals(d.actor.run.returnProof().bytes(),d.f.store.read("actors/0001/returned.json")));ok(d.actor.io.writes==0&&d.actor.files.registered()==0);ok(!d.actor.run.snapshot().get("executeReserved").equals("true"));
        d.noIntentChange(()->d.prepare("STOP_DEPENDENCIES",null));d.noIntentChange(()->d.prepare("EXECUTE_COMMIT",null));d.noIntentChange(()->d.prepare("ACK_FINISH",d.originalIdentity));d.noIntentChange(d::archive);
        reject(d.f.registry::sealFinal);reject(()->d.f.registry.allocate(2,E9TestFiles.uuid("forbidden-actor2"),E9TestFiles.uuid("forbidden-handle2")));
        d.finish();d.noIntentChange(()->d.prepare("ACK_FINISH",d.actor.run.returnProof().bytes()));ok(d.actor.finishes==1);d.end(false);
    }
    static void commitCases()throws Exception{
        Driver d=new Driver();d.bind();
        if(mode.equals("FAILED_RETURN"))d.actor.io.cut=(op,path)->{if(op.equals("WRITE")&&path.endsWith("0001.intent"))throw new IOException("ACTUAL_SYNTHETIC_WRITE_FAILURE");};
        if(mode.equals("UNKNOWN_COMMIT_CLOSE"))d.actor.io.cut=(op,path)->{if(op.equals("CLOSE_AFTER")&&path.endsWith("0001.intent"))throw new IOException("ORIGINAL_NATIVE_CLOSE_NO_JAVA_ACK");};
        d.control("EXECUTE_COMMIT");
        if(mode.equals("UNKNOWN_COMMIT_CLOSE")){ok(!d.actor.runSafe());ok(!d.actor.files.returned());reject(d.actor.run::returnProof);reject(()->d.f.registry.captureIdentityForFinish(d.actor.actor,d.originalIdentity));reject(d::archive);ok(!d.f.store.exists("actors/0001/returned.json"));d.end(true);return;}
        byte[] r0=d.actor.run.returnProof().bytes();ok(d.actor.runSafe());if(mode.equals("FAILED_RETURN")){ok(d.actor.run.returnProof().get("verdict").equals("FAILED"));ok(d.actor.run.returnProof().get("device").equals("ABSENT"));}
        d.noIntentChange(()->d.prepare("STOP_DEPENDENCIES",null));d.archive();d.noIntentChange(()->d.prepare("STOP_DEPENDENCIES",null));d.noIntentChange(()->d.prepare("ACK_FINISH",d.originalIdentity));d.noIntentChange(d::archive);ok(Arrays.equals(r0,d.f.store.read("actors/0001/returned.json")));d.finish();d.noIntentChange(()->d.prepare("ACK_FINISH",r0));ok(Arrays.equals(r0,d.actor.run.returnProof().bytes()));if(mode.equals("FAILED_RETURN"))reject(d.f.registry::sealFinal);d.end(false);
    }
    static void execIntent()throws Exception{
        Driver d=new Driver();d.bind();d.prepare("EXECUTE_COMMIT",null); // Original durable intent; deliberately no wire delivery.
        E9Record s=d.actor.run.snapshot();d.actor.run.stop(d.actor.actor.handle,2,(int)s.number("stateSeq",Integer.MAX_VALUE));
        // Actual stopped Run still cannot erase the previously registered unknown EXEC obligation.
        reject(d::archive);ok(!d.f.store.exists("actors/0001/returned.json"));ok(d.actor.io.writes==0);ok(Arrays.equals(d.identify,d.f.store.read("actors/0001/identify.json")));ok(Arrays.equals(d.reserve,d.f.store.read("actors/0001/reserve.json")));d.end(true);
    }
    static void consoleCustody()throws Exception{
        Driver d=new Driver();d.bind();d.control("EXECUTE_COMMIT");d.archive();byte[] r0=d.actor.run.returnProof().bytes(),commands=d.f.store.read("actors/0001/commands.jsonl");int seq=d.seq;
        E9Record stop=new E9Record(E9Record.map("kind","managerCommand","operation","CONTROL","command","STOP_DEPENDENCIES"),1024);
        reject(()->E9HostManager.console(d.supervisor,new ByteArrayInputStream(stop.bytes()),c->{d.prepare(c.get("command"),null);}));
        ok(d.supervisor.status().get("ingressClosed").equals("true"));ok(d.supervisor.status().get("dependenciesStopped").equals("true"));ok(!d.supervisor.terminated());ok(d.seq==seq);ok(Arrays.equals(commands,d.f.store.read("actors/0001/commands.jsonl")));ok(Arrays.equals(r0,d.actor.run.returnProof().bytes()));
        d.custody=true;d.finish();ok(Arrays.equals(r0,d.f.store.read("actors/0001/returned.json")));d.end(false);
    }
    public static void main(String[] args)throws Exception{
        if(args[0].equals("CHILD_RESPONSE")){System.out.println("Broadcast completed: result=1, data=\"E9:"+args[1]+"\"");return;}
        mode=args[0];out=Paths.get(args[1]);Files.createDirectories(out);E9ProductionSelfCheck.output=out;E9ProductionSelfCheck.reference=Paths.get(args[2]);E9ProductionSelfCheck.selected=mode;
        if(mode.equals("CONSOLE_REJECT_THEN_CUSTODIAL_ACK"))consoleCustody();else if(mode.equals("EXEC_INTENT_ISOLATION"))execIntent();else if(mode.equals("POSTARCHIVE_STOP")||mode.equals("TERMINAL_PREARCHIVE_STOP")||mode.equals("FAILED_RETURN")||mode.equals("UNKNOWN_COMMIT_CLOSE"))commitCases();else boundCancel();
        String result="{\"status\":\"PASS_FINITE_LOCAL_SCOPE\",\"assertions\":"+assertions+",\"sharedFixtureAssertions\":"+E9ProductionSelfCheck.assertions+",\"productionExitAllowed\":"+!pending+",\"originalCloseAck\":"+!pending+"}\n";Files.writeString(out.resolve("result.json"),result,StandardOpenOption.CREATE_NEW);System.out.println(mode+" "+result);
    }
}

