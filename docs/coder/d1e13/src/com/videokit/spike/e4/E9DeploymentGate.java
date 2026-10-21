package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.file.Path;
import java.util.*;

/** Actual install dispatch guard; exact bytes/source-reviewed pair, never merely a high version or ABI string. */
public final class E9DeploymentGate {
    public static final class PackageInfo {
        public final String appId,testId,appSha,testSha,signer,role;public final int appUid,testUid,version,abi;public final boolean relatedProcessPresent;
        public PackageInfo(String appId,String testId,String appSha,String testSha,String signer,String role,int appUid,int testUid,int version,int abi,boolean live){this.appId=appId;this.testId=testId;this.appSha=appSha;this.testSha=testSha;this.signer=signer;this.role=role;this.appUid=appUid;this.testUid=testUid;this.version=version;this.abi=abi;relatedProcessPresent=live;}
    }
    public interface Port {
        byte[] artifact(Path file,int max)throws Exception;
        PackageInfo inspectArtifacts(Path app,Path test)throws Exception;
        PackageInfo installed()throws Exception;
        void dispatch(List<String> argv)throws Exception;
    }
    private final Port port;private final String adb,serial;private int dispatches;
    public E9DeploymentGate(Port port,String adb,String serial)throws IOException{if(!serial.equals("HA1Q6WXR")||!adb.endsWith("adb.exe"))throw new IOException("E9_DEPLOY_TARGET");this.port=port;this.adb=adb;this.serial=serial;}
    public int dispatches(){return dispatches;}
    public static final String E13_SOURCE_ACCEPTANCE="60eb18e88e346e49ec34491083f2b67da21670d7cd5fde40ce3b72ba8246b635";
    public static PackageInfo acceptedE11Source(){return new PackageInfo("com.videokit.app","com.videokit.app.test","2f323c16e896b0535e80cccce05bbcf3051224f0add279a51392312083e89f48","e644dce77be6ccb0e7f99d82f2479fc92238aad682bb022bb95835fc015d0bfb","5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f","ACTIVATION",10221,10222,15,1,false);}
    /** Exact accepted ACTIVATION predecessor, not the historical PREPARE in registry.trust.plan. */
    public void deployE13Detached(E9Registry registry,E9Record release,String approvedSha,String scopeSha,Path app,Path test)throws Exception {
        registry.requireDeploymentQuiet();E9Record.digest(approvedSha);E9Record.digest(scopeSha);
        if(!release.hash().equals(approvedSha))throw new IOException("E13_RELEASE_NOT_PINNED");
        release.exact("kind","head","catalog","app","test","signer","role","abi","version","sourceReview","environment","sourceAcceptance","scope");
        PackageInfo source=acceptedE11Source();
        if(!release.get("kind").equals("activationRelease") || !release.get("head").equals(registry.head()) || !release.get("catalog").equals(registry.finalCatalog().record.hash()) || !release.get("environment").equals(registry.trust.environment) || !release.get("sourceAcceptance").equals(E13_SOURCE_ACCEPTANCE) || !release.get("scope").equals(scopeSha) || !release.get("signer").equals(source.signer) || release.number("version",Integer.MAX_VALUE)!=16)throw new IOException("E13_EXACT_SOURCE_SCOPE_TARGET");
        deploy(release,app,test,source,"ACTIVATION");
    }
    public void deployPrepare(E9Registry registry,Path app,Path test,PackageInfo expectedInstalled)throws Exception{registry.requireDeploymentQuiet();deploy(registry.trust.plan,app,test,expectedInstalled,"PREPARE");}
    public void deployActivation(E9Registry registry,E9Record approvedRelease,Path app,Path test)throws Exception{
        registry.requireDeploymentQuiet();if(!Arrays.equals(approvedRelease.bytes(),registry.readActivationRelease().bytes()))throw new IOException("E9_RELEASE_NOT_IN_APPROVED_STORE");E9Catalog catalog=registry.finalCatalog();if(!approvedRelease.get("head").equals(registry.head())||!approvedRelease.get("catalog").equals(catalog.record.hash())||!approvedRelease.get("role").equals("ACTIVATION"))throw new IOException("E9_DEPLOY_FINAL_CATALOG_BINDING");
        E9Record previous=registry.trust.plan;PackageInfo expected=new PackageInfo("com.videokit.app","com.videokit.app.test",previous.get("app"),previous.get("test"),previous.get("signer"),"PREPARE",10221,10222,(int)previous.number("version",Integer.MAX_VALUE),1,false);
        deploy(approvedRelease,app,test,expected,"ACTIVATION");
    }
    /** Same trusted pinned-release boundary, but no record is created in the accepted final registry. */
    public void deployActivationDetached(E9Registry registry,E9Record release,String approvedReleaseSha,Path app,Path test)throws Exception{
        registry.requireDeploymentQuiet();E9Record.digest(approvedReleaseSha);if(!release.hash().equals(approvedReleaseSha))throw new IOException("E11_RELEASE_NOT_PINNED");
        release.exact("kind","head","catalog","app","test","signer","role","abi","version","sourceReview","environment");
        E9Catalog catalog=registry.finalCatalog();E9Record previous=registry.trust.plan;
        if(!release.get("kind").equals("activationRelease")||!release.get("head").equals(registry.head())||!release.get("catalog").equals(catalog.record.hash())||!release.get("role").equals("ACTIVATION")||!release.get("abi").equals("1")||!release.get("environment").equals(registry.trust.environment)||!release.get("signer").equals(previous.get("signer"))||release.number("version",Integer.MAX_VALUE)<=previous.number("version",Integer.MAX_VALUE))throw new IOException("E11_DETACHED_RELEASE_SCOPE");
        E9Record.digest(release.get("sourceReview"));E9Record.digest(release.get("app"));E9Record.digest(release.get("test"));
        PackageInfo expected=new PackageInfo("com.videokit.app","com.videokit.app.test",previous.get("app"),previous.get("test"),previous.get("signer"),"PREPARE",10221,10222,(int)previous.number("version",Integer.MAX_VALUE),1,false);
        deploy(release,app,test,expected,"ACTIVATION");
    }
    private void deploy(E9Record approved,Path app,Path test,PackageInfo expected,String phase)throws Exception{
        if(dispatches!=0)throw new IOException("E9_DEPLOY_ONCE_NO_RETRY");
        if(!E9Record.sha(port.artifact(app,33554432)).equals(approved.get("app"))||!E9Record.sha(port.artifact(test,33554432)).equals(approved.get("test")))throw new IOException("E9_ARTIFACT_NOT_IN_APPROVED_BYTE_ALLOWLIST");
        PackageInfo candidate=port.inspectArtifacts(app,test);int version=(int)approved.number("version",Integer.MAX_VALUE);
        if(!approved.get("role").equals(phase)||!approved.get("abi").equals("1"))throw new IOException("E9_SOURCE_APPROVED_PHASE_REQUIRED");E9Record.digest(approved.get("sourceReview"));
        check(candidate,approved.get("app"),approved.get("test"),approved.get("signer"),phase,version,1,false);
        PackageInfo current=port.installed();check(current,expected.appSha,expected.testSha,expected.signer,expected.role,expected.version,expected.abi,true);
        if(version<=current.version)throw new IOException("E9_NO_DOWNGRADE_OR_SAME_VERSION_REINSTALL");
        // The caller cannot supply -d, uninstall, clear, force-stop or arbitrary shell text.
        dispatches++;port.dispatch(List.of(adb,"-s",serial,"install","-r",app.toAbsolutePath().toString()));
        dispatches++;port.dispatch(List.of(adb,"-s",serial,"install","-r",test.toAbsolutePath().toString()));
        check(port.installed(),approved.get("app"),approved.get("test"),approved.get("signer"),phase,version,1,true);
    }
    private static void check(PackageInfo actual,String app,String test,String signer,String role,int version,int abi,boolean idle)throws IOException{
        if(actual==null||!actual.appId.equals("com.videokit.app")||!actual.testId.equals("com.videokit.app.test")||!actual.appSha.equals(app)||!actual.testSha.equals(test)||!actual.signer.equals(signer)||!actual.role.equals(role)||actual.version!=version||actual.abi!=abi||actual.appUid!=10221||actual.testUid!=10222||idle&&actual.relatedProcessPresent)throw new IOException("E9_DEPLOY_INSTALLED_IDENTITY_OR_ROLE");
    }
}
