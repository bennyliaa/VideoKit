package com.videokit.spike.e4;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

/** Non-wait launcher; independent 5s broadcasts; original process/pipe/actor custody. */
public final class E9HostManager {
    private E9Registry registry;private E9Registry.Store store;private E9HostDeployment deploy;private E9DeploymentGate gate;private E9DeploymentGate.PackageInfo original;private Path root;
    private final E9PcSupervisor supervisor;private final E9HostDeployment.Processes commands;private final Map<Integer,Managed> actors=new LinkedHashMap<>();private Managed active;
    private volatile boolean failed,authorityCallActive=true;private long logBytes;
    private final class Managed {
        final int ordinal;final String handle,mode;final E9PcSupervisor.Remote remote;final E9Record request;private volatile E9Record latest;private int nextSeq=1;private boolean launchClientReturned;
        Managed(int ordinal,E9Record request,E9PcSupervisor.Remote remote,String mode)throws Exception{this.ordinal=ordinal;this.request=request;handle=request.get("handle");this.remote=remote;this.mode=mode;}
        E9Record snapshot()throws Exception{if(latest==null)throw new IOException("E9_NO_INDEPENDENT_STATUS_YET");return E9Record.parse(E9Record.unpack(latest.get("snapshot"),4096),4096);}
        E9Actor actor()throws Exception{snapshot();return new E9Actor(E9Record.parse(E9Record.unpack(latest.get("actor"),2048),2048));}
        byte[] proof()throws Exception{snapshot();return E9Record.unpack(latest.get("returned"),8192);}
        void adopt(CheckedFrame checked)throws Exception{if(checked.actor!=null)remote.bind(checked.actor);latest=checked.frame;}
    }
    public static final class CheckedFrame {public final E9Record frame;public final E9Actor actor;private CheckedFrame(E9Record frame,E9Actor actor){this.frame=frame;this.actor=actor;}}
    /** The actual manager's semantic validation runs inside the same original five-second response task. */
    public static CheckedFrame checkTransport(E9Record transport,E9Record request,int issuedSeq,E9Record previous,String mode)throws Exception{
        transport.exact("kind","snapshot","actor","returned","mode","pid","uid");if(!transport.get("kind").equals("transport")||!transport.get("uid").equals("10221")||!transport.get("mode").equals(mode)||!Set.of("REGISTERED_MIGRATION","READ_ONLY_IDENTITY").contains(mode))throw new IOException("E9_TRANSPORT_SCOPE");
        E9Record state=E9Record.parse(E9Record.unpack(transport.get("snapshot"),4096),4096);if(!state.get("handle").equals(request.get("handle"))||state.number("commandSeq",8)!=issuedSeq)throw new IOException("E9_TRANSPORT_HANDLE_OR_REQUEST");
        if(previous!=null&&(state.number("stateSeq",Integer.MAX_VALUE)<previous.number("stateSeq",Integer.MAX_VALUE)||state.number("commandSeq",8)<=previous.number("commandSeq",8)))throw new IOException("E9_TRANSPORT_REGRESSED_OR_REPLAYED");
        E9Actor actor=null;if(!transport.get("actor").equals("ABSENT")){actor=new E9Actor(E9Record.parse(E9Record.unpack(transport.get("actor"),2048),2048));for(String key:new String[]{"registry","migration","ordinal","attempt","handle","descriptor","app","test","environment"})if(!actor.record.get(key).equals(request.get(key)))throw new IOException("E9_TRANSPORT_ACTOR_REQUEST");if(actor.pid!=transport.number("pid",Integer.MAX_VALUE))throw new IOException("E9_TRANSPORT_PID");}
        return new CheckedFrame(transport,actor);
    }
    private static byte[] bounded(Path path,int max)throws Exception{if(Files.isSymbolicLink(path)||!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS)||Files.size(path)>max)throw new IOException("E9_PC_INPUT_ROLE_BOUND");return Files.readAllBytes(path);}
    private E9HostManager(E9Record config,E9PcSupervisor supervisor)throws Exception{
        this.supervisor=supervisor;commands=new E9HostDeployment.Processes(supervisor);supervisor.retainAuthority(this,this::custodialCleanup,()->!authorityCallActive&&(registry==null||registry.returned()));
        try{
            config.exact("kind","plan","planSha","authorization","review","registryPath","head","originalApp","originalTest","originalVersion","originalRole","originalAbi");if(!config.get("kind").equals("managerTrust"))throw new IOException("E9_MANAGER_TRUST_SCHEMA");
            E9Registry.Trust trust=new E9Registry.Trust(E9Record.unpack(config.get("plan"),8192),config.get("planSha"),config.get("authorization"),config.get("review"));if(!trust.environment.equals("DEVICE_HA1Q6WXR"))throw new IOException("E9_NO_SYNTHETIC_DEVICE_SESSION");
            root=Paths.get(config.get("registryPath")).toAbsolutePath().normalize();store=new E9Registry.Store(root,null);registry=new E9Registry(store,trust);if(config.get("head").equals("NEW"))registry.initialize();else registry.openKnownHead(config.get("head"));
            E9Record p=trust.plan;for(String k:new String[]{"originalApp","originalTest"})E9Record.digest(config.get(k));original=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",config.get("originalApp"),config.get("originalTest"),p.get("signer"),config.get("originalRole"),10221,10222,(int)config.number("originalVersion",Integer.MAX_VALUE),(int)config.number("originalAbi",1),false);
            E9DeploymentGate.PackageInfo candidate=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",p.get("app"),p.get("test"),p.get("signer"),"PREPARE",10221,10222,(int)p.number("version",Integer.MAX_VALUE),1,false);
            deploy=new E9HostDeployment(commands,Paths.get("D:/Android/SDK"),Paths.get("D:/Android/Android Studio/jbr"),original,candidate);gate=new E9DeploymentGate(deploy,deploy.adb(),"HA1Q6WXR");
        }finally{authorityCallActive=false;}
    }
    public static List<String> nonWaitingLaunch(String adb,E9Record request)throws Exception{return nonWaitingLaunch(adb,request,"REGISTERED_MIGRATION");}
    public static List<String> nonWaitingLaunch(String adb,E9Record request,String mode)throws Exception{if(!Set.of("READ_ONLY_IDENTITY","REGISTERED_MIGRATION").contains(mode))throw new IOException("E9_EXPLICIT_LAUNCH_MODE");return List.of(adb,"-s","HA1Q6WXR","shell","am","instrument","-r","-e","e9Case","legacyN2Migration","-e","e9Batch","D1-E9A-PREPARE-TABLET-20261018","-e","e9Mode",mode,"-e","e9Request",E9Record.pack(request.bytes()),"com.videokit.app.test/com.videokit.spike.e4.E9MigrationInstrumentation");}
    private void launch(E9Record c)throws Exception{
        String mode=c.fields().containsKey("mode")?c.get("mode"):"REGISTERED_MIGRATION";if(c.fields().containsKey("mode"))c.exact("kind","operation","ordinal","attempt","handle","bootKind","mode");else c.exact("kind","operation","ordinal","attempt","handle","bootKind");if(!Set.of("READ_ONLY_IDENTITY","REGISTERED_MIGRATION").contains(mode))throw new IOException("E9_LAUNCH_MODE");int n=(int)c.number("ordinal",2);if(active!=null&&!active.remote.returned())throw new IOException("E9_ORIGINAL_REMOTE_ACTOR_NOT_FINISHED");registry.allocate(n,c.get("attempt"),c.get("handle"));E9PcSupervisor.Remote remote=supervisor.reserveRemote(c.get("handle"));E9Record p=registry.trust.plan;
        String priorActor="ABSENT",priorEvidence="ABSENT",disposition="NONE";if(n==2){E9Actor old=registry.actor(1);priorActor=E9Record.pack(old.record.bytes());boolean dead=store.exists("actors/0001/termination.json");disposition=dead?"TERMINATED_WITHOUT_RETURN":"RETURNED_LATE_NONQUALIFIED";priorEvidence=E9Record.pack(store.read("actors/0001/"+(dead?"termination.json":"returned.json")));}
        E9Record request=new E9Record(E9Record.map("kind","identityRequest","registry",registry.trust.registry,"migration",registry.trust.migration,"ordinal",Integer.toString(n),"attempt",c.get("attempt"),"handle",c.get("handle"),"descriptor",E9LegacyProfile.proposal().hash(),"app",p.get("app"),"test",p.get("test"),"bootKind",c.get("bootKind"),"priorActor",priorActor,"priorEvidence",priorEvidence,"recoveryDisposition",disposition,"environment",registry.trust.environment),8192);
        active=new Managed(n,request,remote,mode);actors.put(n,active);supervisor.run("NONWAIT_LAUNCH",nonWaitingLaunch(deploy.adb(),request,mode),32768,E9PcSupervisor.CONTROL_NS,false);active.launchClientReturned=true;
    }
    public static List<String> broadcast(String adb,String handle,int seq,int state,String action){return new ArrayList<>(List.of(adb,"-s","HA1Q6WXR","shell","am","broadcast","-a","com.videokit.app.E9_MIGRATION_CONTROL","-p","com.videokit.app","--es","handle",handle,"--ei","seq",Integer.toString(seq),"--ei","state",Integer.toString(state),"--es","command",action));}
    public static E9Record broadcastFrame(byte[] raw)throws Exception{
        String text=new String(raw,StandardCharsets.US_ASCII);Matcher m=Pattern.compile("(?m)^Broadcast completed: result=([01]), data=\"E9:([A-Za-z0-9_-]+)\"\\r?$").matcher(text);if(!m.find())throw new IOException("E9_CONTROL_UNREACHABLE_OR_NO_VALID_FRAME_NO_REPLAY");int result=Integer.parseInt(m.group(1));E9Record frame=E9Record.parse(E9Record.unpack(m.group(2),8192),8192);if(m.find()||result!=1)throw new IOException("E9_CONTROL_REJECTED_NO_REPLAY");return frame;
    }
    private void control(String action,boolean custodial)throws Exception{
        if(active==null||!active.launchClientReturned)throw new IOException("E9_LAUNCH_NOT_CONFIRMED");if(action.equals("EXECUTE_COMMIT")&&!active.mode.equals("REGISTERED_MIGRATION"))throw new IOException("E9_READONLY_NO_COMMIT");int seq=active.nextSeq,state=action.equals("STATUS")?-1:(int)active.snapshot().number("stateSeq",Integer.MAX_VALUE);
        E9Record intent=new E9Record(E9Record.map("kind","control","seq",Integer.toString(seq),"command",action,"handle",active.handle,"intent",E9Record.sha((active.handle+":"+seq+":"+action+":"+state).getBytes(StandardCharsets.US_ASCII))),1024);registry.commandIntent(active.ordinal,intent);active.nextSeq++;
        List<String> argv=broadcast(deploy.adb(),active.handle,seq,state,action);
        if(action.equals("EXECUTE_COMMIT"))argv.addAll(List.of("--es","reserve",E9Record.pack(store.read("actors/000"+active.ordinal+"/reserve.json"))));
        if(action.equals("ACK_FINISH")){byte[] archived=store.read("actors/000"+active.ordinal+"/returned.json");if(!Arrays.equals(archived,active.proof()))throw new IOException("E9_ACK_EXACT_ARCHIVED_FRAME");argv.addAll(List.of("--es","archived",E9Record.sha(archived)));}
        Managed original=active;E9Record previous=original.latest==null?null:original.snapshot();
        CheckedFrame checked=(CheckedFrame)commands.controlResponse(argv,32768,custodial,raw->checkTransport(broadcastFrame(raw),original.request,seq,previous,original.mode));original.adopt(checked);System.out.write(checked.frame.bytes());
    }
    private byte[] evidenceCommand(List<String> argv,int max,boolean custodial)throws Exception{return supervisor.run("FINISH_EVIDENCE",argv,max,E9PcSupervisor.GENERAL_NS,custodial);}
    private void finishCapture(boolean custodial)throws Exception{
        E9Actor actor=active.actor();String ps=new String(evidenceCommand(List.of(deploy.adb(),"-s","HA1Q6WXR","shell","ps","-A","-o","PID,NAME"),65536,custodial),StandardCharsets.US_ASCII);for(String line:ps.split("\\r?\\n"))if(line.trim().matches(actor.pid+"\\s+.*"))throw new IOException("E9_ORIGINAL_PID_STILL_PRESENT");
        byte[] log=evidenceCommand(List.of(deploy.adb(),"-s","HA1Q6WXR","logcat","-d","-v","brief","-s","E9_MANAGED:I","ActivityManager:I","*:S"),1048576,custodial);if(logBytes+log.length>1048576)throw new IOException("E9_TOTAL_ORIGINAL_LOG_BOUND");logBytes+=log.length;
        Files.createDirectories(root.resolve("logs"));Files.write(root.resolve("logs/actor-000"+active.ordinal+".finish.log"),log,StandardOpenOption.CREATE_NEW);registry.captureNormalFinish(active.ordinal,log,true);active.remote.normalFinish(E9Record.parse(store.read("actors/000"+active.ordinal+"/returned.json"),8192),store.read("actors/000"+active.ordinal+"/finish.json"));
    }
    private void perform(E9Record c,boolean custodial)throws Exception{
        if(!c.get("kind").equals("managerCommand"))throw new IOException("E9_MANAGER_COMMAND_SCHEMA");
        switch(c.get("operation")){
            case "DEPLOY_PREPARE":c.exact("kind","operation","app","test");gate.deployPrepare(registry,Paths.get(c.get("app")),Paths.get(c.get("test")),original);break;
            case "LAUNCH":launch(c);break;
            case "POLL":c.exact("kind","operation");control("STATUS",custodial);break;
            case "RESERVE":c.exact("kind","operation","predecessorIntent");if(!active.mode.equals("REGISTERED_MIGRATION"))throw new IOException("E9_READONLY_NO_RESERVE");registry.reserve(active.actor(),active.proof(),c.get("predecessorIntent"));break;
            case "CONTROL":c.exact("kind","operation","command");control(c.get("command"),custodial);break;
            case "ARCHIVE_RETURN":c.exact("kind","operation");byte[] proof=active.proof();E9Record returned=E9Record.parse(proof,8192);if(returned.get("phase").equals("IDENTITY"))registry.captureIdentityForFinish(active.actor(),proof);else registry.captureReturned(active.ordinal,proof);break;
            case "CAPTURE_FINISH":c.exact("kind","operation");finishCapture(custodial);break;
            case "CAPTURE_TERMINATION":c.exact("kind","operation","probe");byte[] probe=bounded(Paths.get(c.get("probe")),4096);registry.captureTermination(1,probe);actors.get(1).remote.termination(probe);break;
            case "SEAL_FINAL":c.exact("kind","operation");System.out.write(registry.sealFinal().record.bytes());break;
            case "INSPECT":c.exact("kind","operation");System.out.println("knownHead="+registry.head()+" pcHandle="+supervisor.handle);break;
            default:throw new IOException("E9_UNKNOWN_MANAGER_OPERATION");
        }
    }
    private synchronized void operation(E9Record c)throws Exception{if(failed)throw new IOException("E9_MANAGER_PENDING_CUSTODIAL_CLEANUP_ONLY");authorityCallActive=true;try{perform(c,false);}catch(Exception|Error t){failed=true;supervisor.stopDependencies("MANAGER_OPERATION_FAILURE");throw t;}finally{authorityCallActive=false;}}
    private synchronized E9Record custodialCleanup(E9Record c)throws Exception{
        String action=c.get("operation");if(!Set.of("POLL","CONTROL","ARCHIVE_RETURN","CAPTURE_FINISH","CAPTURE_TERMINATION","INSPECT").contains(action)||action.equals("CONTROL")&&!Set.of("STATUS","ACK_FINISH","STOP_DEPENDENCIES").contains(c.get("command")))throw new IOException("E9_PC_CUSTODY_NO_NEW_WRITES_OR_FINAL");
        authorityCallActive=true;try{perform(c,true);return supervisor.status();}finally{authorityCallActive=false;}
    }
    public interface ConsoleCommands {void run(E9Record command)throws Exception;}
    /** Every console exit, including truncation/overflow/EOF, enters original custody. */
    public static void console(E9PcSupervisor supervisor,InputStream input,ConsoleCommands commands)throws Exception{
        try{for(String line;(line=E9PcSupervisor.consoleLine(input,16384))!=null;){E9Record c=E9Record.parse((line+"\n").getBytes(StandardCharsets.US_ASCII),16384);commands.run(c);}}
        catch(Exception|Error t){supervisor.stopDependencies("PC_CONSOLE_FAILURE");throw t;}
        finally{E9Record ack=supervisor.closeIngressAndSupervise();System.err.println("E9_PC_MAIN_EXIT_BOUNDARY "+new String(ack.bytes(),StandardCharsets.US_ASCII));}
    }
    public static void main(String[] args)throws Exception{
        if(args.length==0){System.out.println("INSPECT_ONLY: E9A PREPARE; no device calls. Future approved-session uses non-wait launch and independent 5-second broadcast status/control. No trusted configuration is supplied.");return;}
        if(args.length!=3||!args[0].equals("--approved-session"))throw new IOException("E9_APPROVED_SESSION_REQUIRED");E9Record.digest(args[2]);byte[] raw=bounded(Paths.get(args[1]),24576);if(!E9Record.sha(raw).equals(args[2]))throw new IOException("E9_MANAGER_CONFIG_PIN");E9Record config=E9Record.parse(raw,24576);
        E9PcSupervisor supervisor=new E9PcSupervisor("MIGRATION-MANAGER-"+UUID.randomUUID());supervisor.authorizeCleanup(args[2]);boolean consoleEntered=false;
        try{E9HostManager manager=new E9HostManager(config,supervisor);consoleEntered=true;console(supervisor,System.in,manager::operation);}
        finally{if(!consoleEntered){supervisor.stopDependencies("MANAGER_INITIALIZATION_FAILED");System.err.println(new String(supervisor.closeIngressAndSupervise().bytes(),StandardCharsets.US_ASCII));}}
    }
}
