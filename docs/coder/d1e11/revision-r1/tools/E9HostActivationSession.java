package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;

/** Separate future release stage; shares the complete E9 registry, catalog, phase and deployment implementation. */
public final class E9HostActivationSession {
    private static byte[] read(Path p,int max)throws Exception{if(Files.isSymbolicLink(p)||!Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS)||Files.size(p)>max)throw new IOException("E9_APPROVED_FILE_ROLE");return Files.readAllBytes(p);}
    private static E9Registry open(String path,String pin,E9PcSupervisor supervisor)throws Exception{
        E9Record.digest(pin);byte[] raw=read(Paths.get(path),24576);if(!E9Record.sha(raw).equals(pin))throw new IOException("E9_FINAL_TRUST_PIN");E9Record c=E9Record.parse(raw,24576);if(c.fields().containsKey("dispatchRecord"))c.exact("kind","plan","planSha","authorization","review","registryPath","head","dispatchRecord");else c.exact("kind","plan","planSha","authorization","review","registryPath","head");if(!c.get("kind").equals("activationTrust"))throw new IOException("E9_FINAL_TRUST_SCHEMA");
        E9Registry.Trust t=new E9Registry.Trust(E9Record.unpack(c.get("plan"),8192),c.get("planSha"),c.get("authorization"),c.get("review"));if(!t.environment.equals("DEVICE_HA1Q6WXR"))throw new IOException("E9_SYNTHETIC_RELEASE_FORBIDDEN");
        return openReviewedRegistry(supervisor,Paths.get(c.get("registryPath")),t,c.get("head"),null);
    }
    public static E9Registry openReviewedRegistry(E9PcSupervisor supervisor,Path path,E9Registry.Trust trust,String head,E9Registry.Cut cut)throws Exception{
        E9Registry registry=E9HostRegistry.create(supervisor,path,trust,cut).registry;registry.openKnownHead(head);registry.requireDeploymentQuiet();registry.finalCatalog();return registry;
    }
    public static void main(String[] args)throws Exception{
        if(args.length==0){System.out.println("INSPECT_ONLY: future independently approved activation stage; no config, real H_actor, APK or device calls are supplied by E9.");return;}
        if(!(args.length==4&&args[0].equals("--approved-export"))&&!(args.length==7&&args[0].equals("--approved-deploy")))throw new IOException("E9_SEPARATE_REVIEWED_RELEASE_STAGE_REQUIRED");
        E9PcSupervisor supervisor=new E9PcSupervisor("ACTIVATION-ENTRY-"+UUID.randomUUID());
        E9HostRegistry.boundary(supervisor,()->{
        E9Registry registry=open(args[1],args[2],supervisor);
        if(args[0].equals("--approved-export")){E9ActivationPolicyExport.export(registry,Paths.get(args[3]));return;}
        byte[] raw=read(Paths.get(args[3]),8192);E9Record.digest(args[4]);if(!E9Record.sha(raw).equals(args[4]))throw new IOException("E9_APPROVED_RELEASE_BYTES");E9Record release=E9Record.parse(raw,8192);
        // A pinned persistent dispatch record restores the old CREATE_NEW replay barrier, outside
        // the immutable final registry. Copying this config/release cannot choose a fresh record path.
        byte[] configBytes=read(Paths.get(args[1]),24576);if(!E9Record.sha(configBytes).equals(args[2]))throw new IOException("E9_FINAL_TRUST_PIN");E9Record config=E9Record.parse(configBytes,24576);config.exact("kind","plan","planSha","authorization","review","registryPath","head","dispatchRecord");
        Path oncePath=Paths.get(config.get("dispatchRecord")).toAbsolutePath().normalize(),originalRoot=Paths.get(config.get("registryPath")).toAbsolutePath().normalize();if(!Paths.get(config.get("dispatchRecord")).isAbsolute()||oncePath.startsWith(originalRoot))throw new IOException("E11_ONCE_MUST_BE_PINNED_OUTSIDE_FINAL_REGISTRY");
        E11DeploymentOnce once=new E11DeploymentOnce(oncePath,supervisor);
        once.record(new E9Record(E9Record.map("kind","activationDispatchIntent","config",args[2],"release",args[4],"head",registry.head(),"catalog",registry.finalCatalog().record.hash(),"registry",registry.trust.registry,"pcHandle",supervisor.handle,"state","RESERVED_OUTCOME_NOT_ASSUMED"),4096).bytes());
        // The independently approved release is detached; final registry/events/head stay immutable.
        // A dispatch/unknown installation still consumes this original session; there is no retry.
        E9Record p=registry.trust.plan;
        E9DeploymentGate.PackageInfo previous=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",p.get("app"),p.get("test"),p.get("signer"),"PREPARE",10221,10222,(int)p.number("version",Integer.MAX_VALUE),1,false);
        E9DeploymentGate.PackageInfo candidate=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",release.get("app"),release.get("test"),release.get("signer"),"ACTIVATION",10221,10222,(int)release.number("version",Integer.MAX_VALUE),1,false);
        E9HostDeployment.Processes processes=new E9HostDeployment.Processes(supervisor);
        E9HostDeployment port=new E9HostDeployment(processes,Paths.get("D:/Android/SDK"),Paths.get("D:/Android/Android Studio/jbr"),previous,candidate);new E9DeploymentGate(port,port.adb(),"HA1Q6WXR").deployActivationDetached(registry,release,args[4],Paths.get(args[5]),Paths.get(args[6]));
        });
    }
    private E9HostActivationSession(){}
}
