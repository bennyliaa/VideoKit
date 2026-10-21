package com.videokit.spike.e4;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
/** Minimal v15->v16 adapter on the original registry/once/port/supervisor. No new authority. */
public final class E13HostActivationSession {
    public static byte[] pinned(Path p,String sha,int max)throws Exception {
        E9Record.digest(sha);if(Files.isSymbolicLink(p)||!Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS)||Files.size(p)>max)throw new IOException("E13_PINNED_FILE_ROLE");byte[] b=Files.readAllBytes(p);if(!E9Record.sha(b).equals(sha))throw new IOException("E13_PINNED_BYTES");return b;
    }
    public static E9Record scope(byte[] raw)throws Exception {
        E9Record s=E9Record.parse(raw,8192);s.exact("kind","batch","scopeId","sourceAcceptance","sourceApp","sourceTest","app","test","fixture","fixtureSigner","sourceReview","methods","budget");
        E9DeploymentGate.PackageInfo old=E9DeploymentGate.acceptedE11Source();
        if(!s.get("kind").equals("e13DispatchScope") || !s.get("batch").equals(E13Selection.BATCH) || !s.get("sourceAcceptance").equals(E9DeploymentGate.E13_SOURCE_ACCEPTANCE) || !s.get("sourceApp").equals(old.appSha)||!s.get("sourceTest").equals(old.testSha)||!s.get("methods").equals(String.join(",",new TreeSet<>(E13Selection.METHODS))) || !s.get("budget").equals("source4096/read65536/open8/close16/process48/text2097152/output0"))throw new IOException("E13_SCOPE_BINDING");
        E9Record.uuid(s.get("scopeId"));for(String k:List.of("app","test","fixture","fixtureSigner","sourceReview"))E9Record.digest(s.get(k));if(s.get("fixtureSigner").equals(old.signer))throw new IOException("E13_FIXTURE_SIGNER");return s;
    }
    public static void main(String[] a)throws Exception {
        if(a.length==0){System.out.println("INSPECT_ONLY E13: no real scope/once/device dispatch supplied");return;}
        if(a.length!=8 || !a[0].equals("--approved-e13-deploy"))throw new IOException("E13_EXACT_DEPLOY_ARGUMENTS");
        E9PcSupervisor supervisor=new E9PcSupervisor("E13-ACTIVATION-"+UUID.randomUUID());
        E9HostRegistry.boundary(supervisor,()->{
            E9Record c=E9Record.parse(pinned(Paths.get(a[1]),a[2],24576),24576);
            c.exact("kind","plan","planSha","authorization","review","registryPath","head","dispatchRecord","scopePath","scopeSha");
            if(!c.get("kind").equals("e13ActivationTrust"))throw new IOException("E13_CONFIG_SCHEMA");
            E9Record scope=scope(pinned(Paths.get(c.get("scopePath")),c.get("scopeSha"),8192));
            E9Record release=E9Record.parse(pinned(Paths.get(a[3]),a[4],8192),8192);
            for(String k:List.of("app","test","sourceReview","sourceAcceptance"))if(!release.get(k).equals(scope.get(k)))throw new IOException("E13_RELEASE_SCOPE_PAIR");
            E9Registry.Trust trust=new E9Registry.Trust(E9Record.unpack(c.get("plan"),8192),c.get("planSha"),c.get("authorization"),c.get("review"));
            if(!trust.environment.equals("DEVICE_HA1Q6WXR"))throw new IOException("E13_REAL_REGISTRY_REQUIRED");
            E9Registry registry=E9HostActivationSession.openReviewedRegistry(supervisor,Paths.get(c.get("registryPath")),trust,c.get("head"),null);
            Path once=Paths.get(c.get("dispatchRecord")).toAbsolutePath().normalize(),root=Paths.get(c.get("registryPath")).toAbsolutePath().normalize();
            if(!Paths.get(c.get("dispatchRecord")).isAbsolute()||once.startsWith(root)||!once.getFileName().toString().equals("e13-activation-deployment.once"))throw new IOException("E13_NEW_FIXED_ONCE_REQUIRED");
            new E11DeploymentOnce(once,supervisor).record(new E9Record(E9Record.map("kind","e13ActivationDispatchIntent","config",a[2],"release",a[4],"scope",c.get("scopeSha"),"sourceAcceptance",E9DeploymentGate.E13_SOURCE_ACCEPTANCE,"pcHandle",supervisor.handle,"state","RESERVED_OUTCOME_NOT_ASSUMED"),4096).bytes());
            E9DeploymentGate.PackageInfo target=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",release.get("app"),release.get("test"),release.get("signer"),"ACTIVATION",10221,10222,16,1,false);
            E9HostDeployment.Processes originals=new E9HostDeployment.Processes(supervisor);int[] operations={0},remainingText={524288};
            E9HostDeployment.Commands bounded=(command,max)->{if(operations[0]>=32||remainingText[0]<1)throw new IOException("E13_DEPLOY_PROCESS_TEXT_BUDGET");operations[0]++;byte[] result=originals.run(command,Math.min(max,remainingText[0]));remainingText[0]-=result.length;return result;};
            E9HostDeployment port=new E9HostDeployment(bounded,Paths.get("D:/Android/SDK"),Paths.get("D:/Android/Android Studio/jbr"),E9DeploymentGate.acceptedE11Source(),target);
            port.requireE11DataIdentity();new E9DeploymentGate(port,port.adb(),"HA1Q6WXR").deployE13Detached(registry,release,a[4],c.get("scopeSha"),Paths.get(a[5]),Paths.get(a[6]));port.requireE11DataIdentity();port.deployE13Fixture(Paths.get(a[7]),scope.get("fixture"),scope.get("fixtureSigner"));
            System.err.println("E13_DEPLOY_BUDGET operations="+operations[0]+" textBytes="+(524288-remainingText[0]));
        });
    }
    private E13HostActivationSession(){}
}
