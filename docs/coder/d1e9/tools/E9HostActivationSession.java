package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;

/** Separate future release stage; shares the complete E9 registry, catalog, phase and deployment implementation. */
public final class E9HostActivationSession {
    private static byte[] read(Path p,int max)throws Exception{if(Files.isSymbolicLink(p)||!Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS)||Files.size(p)>max)throw new IOException("E9_APPROVED_FILE_ROLE");return Files.readAllBytes(p);}
    private static E9Registry open(String path,String pin)throws Exception{
        E9Record.digest(pin);byte[] raw=read(Paths.get(path),24576);if(!E9Record.sha(raw).equals(pin))throw new IOException("E9_FINAL_TRUST_PIN");E9Record c=E9Record.parse(raw,24576);c.exact("kind","plan","planSha","authorization","review","registryPath","head");if(!c.get("kind").equals("activationTrust"))throw new IOException("E9_FINAL_TRUST_SCHEMA");
        E9Registry.Trust t=new E9Registry.Trust(E9Record.unpack(c.get("plan"),8192),c.get("planSha"),c.get("authorization"),c.get("review"));if(!t.environment.equals("DEVICE_HA1Q6WXR"))throw new IOException("E9_SYNTHETIC_RELEASE_FORBIDDEN");
        E9Registry registry=new E9Registry(new E9Registry.Store(Paths.get(c.get("registryPath")),null),t);registry.openKnownHead(c.get("head"));registry.requireDeploymentQuiet();registry.finalCatalog();return registry;
    }
    public static void main(String[] args)throws Exception{
        if(args.length==0){System.out.println("INSPECT_ONLY: future independently approved activation stage; no config, real H_actor, APK or device calls are supplied by E9.");return;}
        if(args.length==4&&args[0].equals("--approved-export")){E9ActivationPolicyExport.export(open(args[1],args[2]),Paths.get(args[3]));return;}
        if(args.length!=7||!args[0].equals("--approved-deploy"))throw new IOException("E9_SEPARATE_REVIEWED_RELEASE_STAGE_REQUIRED");
        E9Registry registry=open(args[1],args[2]);byte[] raw=read(Paths.get(args[3]),8192);E9Record.digest(args[4]);if(!E9Record.sha(raw).equals(args[4]))throw new IOException("E9_APPROVED_RELEASE_BYTES");E9Record release=E9Record.parse(raw,8192);
        // CREATE_NEW precedes dispatch. This CLI never retries an existing release/unknown installation.
        registry.recordActivationRelease(release);E9Record p=registry.trust.plan;
        E9DeploymentGate.PackageInfo previous=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",p.get("app"),p.get("test"),p.get("signer"),"PREPARE",10221,10222,(int)p.number("version",Integer.MAX_VALUE),1,false);
        E9DeploymentGate.PackageInfo candidate=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",release.get("app"),release.get("test"),release.get("signer"),"ACTIVATION",10221,10222,(int)release.number("version",Integer.MAX_VALUE),1,false);
        E9HostDeployment port=new E9HostDeployment(new E9HostDeployment.Processes(),Paths.get("D:/Android/SDK"),Paths.get("D:/Android/Android Studio/jbr"),previous,candidate);new E9DeploymentGate(port,port.adb(),"HA1Q6WXR").deployActivation(registry,release,Paths.get(args[5]),Paths.get(args[6]));
    }
    private E9HostActivationSession(){}
}
