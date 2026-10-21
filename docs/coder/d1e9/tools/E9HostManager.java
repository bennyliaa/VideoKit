package com.videokit.spike.e4;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

/** Future approved PC session. No arguments = inspect only; no device process is created. */
public final class E9HostManager {
    private final E9Registry registry;private final E9Registry.Store store;private final E9HostDeployment.Processes commands=new E9HostDeployment.Processes();
    private final E9HostDeployment deploy;private final E9DeploymentGate gate;private final E9DeploymentGate.PackageInfo original;private final Path root;private Managed active;private long logBytes;private boolean failed;
    private final class Managed {
        final Process process;final Thread reader;final int ordinal;volatile E9Record latest;volatile Throwable error;volatile boolean returned;
        Managed(int n,List<String> args)throws Exception{
            ordinal=n;Path log=root.resolve("logs/actor-000"+n+".instrument.log");Files.createDirectories(log.getParent());
            E4Owned<OutputStream> output=new E4Owned<>(log,OutputStream::close);output.allocate(()->Files.newOutputStream(log,StandardOpenOption.CREATE_NEW));
            process=new ProcessBuilder(args).redirectErrorStream(true).start();
            reader=new Thread(()->{Throwable first=null;try(InputStream in=process.getInputStream()){
                ByteArrayOutputStream line=new ByteArrayOutputStream();for(int b;(b=in.read())!=-1;){synchronized(E9HostManager.this){if(++logBytes>1048576)throw new IOException("E9_ORIGINAL_LOG_BOUND");}output.original().write(b);if(line.size()>=16384)throw new IOException("E9_TRANSPORT_LINE_BOUND");if(b=='\n'){String value=line.toString(StandardCharsets.US_ASCII);line.reset();int at=value.indexOf("E9:");if(at>=0){String encoded=value.substring(at+3).trim();if(encoded.matches("[A-Za-z0-9_-]+"))accept(E9Record.parse(E9Record.unpack(encoded,8192),8192));}}else line.write(b);}
            }catch(Throwable t){first=t;error=t;}finally{try{output.close();}catch(Throwable t){if(first!=null)first.addSuppressed(t);else error=t;}returned=output.returned()&&error==null;}},"E9-PC-original-instrument-output");reader.setDaemon(true);reader.start();
        }
        void accept(E9Record transport)throws Exception{transport.exact("kind","snapshot","actor","returned","mode","pid","uid");if(!transport.get("kind").equals("transport")||!transport.get("uid").equals("10221")||!transport.get("mode").equals("REGISTERED_MIGRATION"))throw new IOException("E9_TRANSPORT_SCOPE");E9Record s=E9Record.parse(E9Record.unpack(transport.get("snapshot"),4096),4096);E9Record launch=launchRecord(ordinal);if(!s.get("handle").equals(launch.get("handle")))throw new IOException("E9_TRANSPORT_HANDLE");if(latest!=null){E9Record before=snapshot();if(s.number("stateSeq",Integer.MAX_VALUE)<before.number("stateSeq",Integer.MAX_VALUE))return;}latest=transport;}
        E9Record snapshot()throws Exception{if(error!=null||latest==null)throw new IOException("E9_ORIGINAL_TRANSPORT_NOT_AVAILABLE",error);return E9Record.parse(E9Record.unpack(latest.get("snapshot"),4096),4096);}
        E9Actor actor()throws Exception{snapshot();return new E9Actor(E9Record.parse(E9Record.unpack(latest.get("actor"),2048),2048));}
        byte[] proof()throws Exception{snapshot();return E9Record.unpack(latest.get("returned"),8192);}
    }
    private E9Record launchRecord(int ordinal)throws Exception{byte[] raw=store.read("actors/000"+ordinal+"/commands.jsonl");int at=0;while(at<raw.length&&raw[at]!='\n')at++;return E9Record.parse(Arrays.copyOf(raw,at+1),1024);}
    private static byte[] bounded(Path path,int max)throws Exception{if(Files.isSymbolicLink(path)||!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS)||Files.size(path)>max)throw new IOException("E9_PC_INPUT_ROLE_BOUND");return Files.readAllBytes(path);}
    private E9HostManager(E9Record config)throws Exception{
        config.exact("kind","plan","planSha","authorization","review","registryPath","head","originalApp","originalTest","originalVersion","originalRole","originalAbi");if(!config.get("kind").equals("managerTrust"))throw new IOException("E9_MANAGER_TRUST_SCHEMA");
        E9Registry.Trust trust=new E9Registry.Trust(E9Record.unpack(config.get("plan"),8192),config.get("planSha"),config.get("authorization"),config.get("review"));if(!trust.environment.equals("DEVICE_HA1Q6WXR"))throw new IOException("E9_NO_SYNTHETIC_DEVICE_SESSION");
        root=Paths.get(config.get("registryPath")).toAbsolutePath().normalize();store=new E9Registry.Store(root,null);registry=new E9Registry(store,trust);if(config.get("head").equals("NEW"))registry.initialize();else registry.openKnownHead(config.get("head"));
        E9Record p=trust.plan;for(String k:new String[]{"originalApp","originalTest"})E9Record.digest(config.get(k));original=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",config.get("originalApp"),config.get("originalTest"),p.get("signer"),config.get("originalRole"),10221,10222,(int)config.number("originalVersion",Integer.MAX_VALUE),(int)config.number("originalAbi",1),false);
        E9DeploymentGate.PackageInfo candidate=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",p.get("app"),p.get("test"),p.get("signer"),"PREPARE",10221,10222,(int)p.number("version",Integer.MAX_VALUE),1,false);
        deploy=new E9HostDeployment(commands,Paths.get("D:/Android/SDK"),Paths.get("D:/Android/Android Studio/jbr"),original,candidate);gate=new E9DeploymentGate(deploy,deploy.adb(),"HA1Q6WXR");
    }
    private void launch(E9Record c)throws Exception{
        c.exact("kind","operation","ordinal","attempt","handle","bootKind");int n=(int)c.number("ordinal",2);if(active!=null&&(!active.returned||active.process.isAlive()))throw new IOException("E9_ORIGINAL_MANAGER_PROCESS_NOT_RETURNED");registry.allocate(n,c.get("attempt"),c.get("handle"));E9Record p=registry.trust.plan;
        String priorActor="ABSENT",priorEvidence="ABSENT",disposition="NONE";if(n==2){E9Actor old=registry.actor(1);priorActor=E9Record.pack(old.record.bytes());boolean dead=store.exists("actors/0001/termination.json");disposition=dead?"TERMINATED_WITHOUT_RETURN":"RETURNED_LATE_NONQUALIFIED";priorEvidence=E9Record.pack(store.read("actors/0001/"+(dead?"termination.json":"returned.json")));}
        E9Record request=new E9Record(E9Record.map("kind","identityRequest","registry",registry.trust.registry,"migration",registry.trust.migration,"ordinal",Integer.toString(n),"attempt",c.get("attempt"),"handle",c.get("handle"),"descriptor",E9LegacyProfile.proposal().hash(),"app",p.get("app"),"test",p.get("test"),"bootKind",c.get("bootKind"),"priorActor",priorActor,"priorEvidence",priorEvidence,"recoveryDisposition",disposition,"environment",registry.trust.environment),8192);
        active=new Managed(n,List.of(deploy.adb(),"-s","HA1Q6WXR","shell","am","instrument","-w","-r","-e","e9Case","legacyN2Migration","-e","e9Batch","D1-E9-PREPARE-TABLET-20261018","-e","e9Mode","REGISTERED_MIGRATION","-e","e9Request",E9Record.pack(request.bytes()),"com.videokit.app.test/com.videokit.spike.e4.E9MigrationInstrumentation"));
    }
    private void control(E9Record c)throws Exception{
        c.exact("kind","operation","command");E9Record s=active.snapshot();String action=c.get("command");int seq=(int)s.number("commandSeq",8)+1,state=(int)s.number("stateSeq",Integer.MAX_VALUE);String h=s.get("handle");
        E9Record intent=new E9Record(E9Record.map("kind","control","seq",Integer.toString(seq),"command",action,"handle",h,"intent",c.hash()),1024);registry.commandIntent(active.ordinal,intent);
        List<String> argv=new ArrayList<>(List.of(deploy.adb(),"-s","HA1Q6WXR","shell","am","broadcast","-a","com.videokit.app.E9_MIGRATION_CONTROL","-p","com.videokit.app","--es","handle",h,"--ei","seq",Integer.toString(seq),"--ei","state",Integer.toString(state),"--es","command",action));
        if(action.equals("EXECUTE_COMMIT")){argv.addAll(List.of("--es","reserve",E9Record.pack(store.read("actors/000"+active.ordinal+"/reserve.json"))));}
        if(action.equals("ACK_FINISH")){byte[] archived=store.read("actors/000"+active.ordinal+"/returned.json");if(!Arrays.equals(archived,active.proof()))throw new IOException("E9_ACK_EXACT_ARCHIVED_FRAME");argv.addAll(List.of("--es","archived",E9Record.sha(archived)));}
        String raw=new String(commands.run(argv,32768),StandardCharsets.US_ASCII);Matcher m=Pattern.compile("E9:([A-Za-z0-9_-]+)").matcher(raw);if(!m.find())throw new IOException("E9_CONTROL_RESULT_UNKNOWN_NO_RETRY");active.accept(E9Record.parse(E9Record.unpack(m.group(1),8192),8192));
    }
    private void finishCapture()throws Exception{
        if(active==null||active.process.isAlive()||!active.returned||active.process.exitValue()!=0)throw new IOException("E9_ORIGINAL_INSTRUMENT_NOT_NORMALLY_RETURNED");
        E9Actor actor=active.actor();String ps=new String(commands.run(List.of(deploy.adb(),"-s","HA1Q6WXR","shell","ps","-A","-o","PID,NAME"),65536),StandardCharsets.US_ASCII);for(String line:ps.split("\\r?\\n"))if(line.trim().matches(actor.pid+"\\s+.*"))throw new IOException("E9_ORIGINAL_PID_STILL_PRESENT");
        byte[] log=commands.run(List.of(deploy.adb(),"-s","HA1Q6WXR","logcat","-d","-v","brief","-s","E9_MANAGED:I","ActivityManager:I","*:S"),1048576);synchronized(this){if(logBytes+log.length>1048576)throw new IOException("E9_TOTAL_ORIGINAL_LOG_BOUND");logBytes+=log.length;}
        Files.write(root.resolve("logs/actor-000"+active.ordinal+".finish.log"),log,StandardOpenOption.CREATE_NEW);registry.captureNormalFinish(active.ordinal,log,true);
    }
    private void operation(E9Record c)throws Exception{
        if(failed)throw new IOException("E9_MANAGER_FAILURE_ISOLATE_NO_RETRY");if(!c.get("kind").equals("managerCommand"))throw new IOException("E9_MANAGER_COMMAND_SCHEMA");
        switch(c.get("operation")){
            case "DEPLOY_PREPARE":c.exact("kind","operation","app","test");gate.deployPrepare(registry,Paths.get(c.get("app")),Paths.get(c.get("test")),original);break;
            case "LAUNCH":launch(c);break;
            case "POLL":c.exact("kind","operation");System.out.write(active.latest==null?new byte[0]:active.latest.bytes());break;
            case "RESERVE":c.exact("kind","operation","predecessorIntent");registry.reserve(active.actor(),active.proof(),c.get("predecessorIntent"));break;
            case "CONTROL":control(c);break;
            case "ARCHIVE_RETURN":c.exact("kind","operation");registry.captureReturned(active.ordinal,active.proof());break;
            case "CAPTURE_FINISH":c.exact("kind","operation");finishCapture();break;
            case "CAPTURE_TERMINATION":c.exact("kind","operation","probe");registry.captureTermination(1,bounded(Paths.get(c.get("probe")),4096));break;
            case "SEAL_FINAL":c.exact("kind","operation");System.out.write(registry.sealFinal().record.bytes());break;
            case "INSPECT":c.exact("kind","operation");System.out.println("knownHead="+registry.head()+" originalRegistryReturns="+registry.returned());break;
            default:throw new IOException("E9_UNKNOWN_MANAGER_OPERATION");
        }
    }
    public static void main(String[] args)throws Exception{
        if(args.length==0){System.out.println("INSPECT_ONLY: PREPARE; no device calls. Future approved session requires --approved-session trusted-config.json exact-config-sha256. No configuration/approval/catalog is supplied in E9.");return;}
        if(args.length!=3||!args[0].equals("--approved-session"))throw new IOException("E9_APPROVED_SESSION_REQUIRED");E9Record.digest(args[2]);byte[] raw=bounded(Paths.get(args[1]),24576);if(!E9Record.sha(raw).equals(args[2]))throw new IOException("E9_MANAGER_CONFIG_PIN");E9HostManager m=new E9HostManager(E9Record.parse(raw,24576));
        // Closing stdin never kills an actor or invents a finish. The PC process must remain available while it is active.
        BufferedReader input=new BufferedReader(new InputStreamReader(System.in,StandardCharsets.US_ASCII));for(String line;(line=input.readLine())!=null;){if(line.length()>16384)throw new IOException("E9_CONSOLE_BOUND");try{m.operation(E9Record.parse((line+"\n").getBytes(StandardCharsets.US_ASCII),16384));System.out.println("PC_COMMAND_RETURNED head="+m.registry.head());}catch(Throwable t){m.failed=true;System.err.println("E9_MANAGER_PENDING_ISOLATE "+t);}}
        if(m.active!=null&&m.active.process.isAlive()){System.err.println("E9_MANAGER_STDIN_CLOSED_WITH_ACTIVE_ORIGINAL_NO_KILL_NO_ACK");m.active.reader.join();}
    }
}
