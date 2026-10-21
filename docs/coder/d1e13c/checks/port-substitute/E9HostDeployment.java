package com.videokit.spike.e4;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.regex.*;

/** PC implementation of the production dispatch port. Never invoked by the local build/check batch. */
public final class E9HostDeployment implements E9DeploymentGate.Port {
    public interface Commands {byte[] run(List<String> args,int max)throws Exception;}
    /** Shared original process owner; all main-method exits must call closeSession(). */
    public static final class Processes implements Commands {
        public final E9PcSupervisor supervisor;
        public Processes()throws Exception{this(new E9PcSupervisor("DEPLOYMENT-"+UUID.randomUUID()));}
        public Processes(E9PcSupervisor supervisor){this.supervisor=Objects.requireNonNull(supervisor);}
        public byte[] run(List<String> args,int max)throws Exception{return supervisor.run("GENERAL",args,max,E9PcSupervisor.GENERAL_NS,false);}
        public byte[] runControl(List<String> args,int max,boolean cleanup)throws Exception{return supervisor.run("CONTROL",args,max,E9PcSupervisor.CONTROL_NS,cleanup);}
        public E9Record controlFrame(List<String> args,int max,boolean cleanup)throws Exception{return (E9Record)supervisor.runDecoded("CONTROL",args,max,E9PcSupervisor.CONTROL_NS,cleanup,E9HostManager::broadcastFrame);}
        public Object controlResponse(List<String> args,int max,boolean cleanup,E9PcSupervisor.Decoder handler)throws Exception{return supervisor.runDecoded("CONTROL",args,max,E9PcSupervisor.CONTROL_NS,cleanup,handler);}
        public E9Record closeSession()throws Exception{return supervisor.closeIngressAndSupervise();}
    }
    private final Commands commands;private final E9DeploymentGate.PackageInfo candidate;private final String adb,aapt,java,signerJar;private final Map<String,E9DeploymentGate.PackageInfo> known=new HashMap<>();private boolean failed;private int installs;
    public E9HostDeployment(Commands commands,Path sdk,Path jdk,E9DeploymentGate.PackageInfo original,E9DeploymentGate.PackageInfo candidate){
        this.commands=Objects.requireNonNull(commands);this.candidate=candidate;adb=sdk.resolve("platform-tools/adb.exe").toString();aapt=sdk.resolve("build-tools/36.0.0/aapt.exe").toString();java=jdk.resolve("bin/java.exe").toString();signerJar=sdk.resolve("build-tools/36.0.0/lib/apksigner.jar").toString();known.put(original.appSha+":"+original.testSha,original);known.put(candidate.appSha+":"+candidate.testSha,candidate);
    }
    public String adb(){return adb;}
    public void requireE11DataIdentity()throws Exception {
        if(!adb("shell","run-as","com.videokit.app","stat","-c","%u:%i",".").trim().equals("10221:6972") || !adb("shell","run-as","com.videokit.app.test","stat","-c","%u:%i",".").trim().equals("10222:4741"))throw new IOException("E13_ORIGINAL_DATA_IDENTITY");
    }
    /** Fixed different-signer Debug fixture, only after its absence was actually observed. */
    public void deployE13Fixture(Path file,String hash,String signer)throws Exception {
        E9Record.digest(hash);E9Record.digest(signer);
        if(signer.equals(candidate.signer)||!E9Record.sha(artifact(file,33554432)).equals(hash))throw new IOException("E13_FIXTURE_ALLOWLIST");
        String badging=new String(run(List.of(aapt,"dump","badging",file.toString()),65536),StandardCharsets.UTF_8);
        if(!match(badging,"(?m)^package: name='([^']+)'").equals("com.videokit.e13.sender") || !match(badging,"versionCode='([0-9]+)'").equals("1") || !certificate(file).equals(signer))throw new IOException("E13_FIXTURE_IDENTITY");
        if(!adb("shell","pm","list","packages","com.videokit.e13.sender").trim().isEmpty())throw new IOException("E13_FIXTURE_ALREADY_INSTALLED_NO_RETRY");
        String result=new String(run(List.of(adb,"-s","HA1Q6WXR","install",file.toAbsolutePath().toString()),32768),StandardCharsets.UTF_8);
        if(!result.matches("(?s).*\\bSuccess\\s*"))throw new IOException("E13_FIXTURE_INSTALL_NOT_SUCCESS");
        if(!installedHash(remoteApk("com.videokit.e13.sender")).equals(hash))throw new IOException("E13_FIXTURE_INSTALLED_HASH");
        String dump=adb("shell","dumpsys","package","com.videokit.e13.sender");int uid=Integer.parseInt(match(dump,"(?m)^\\s*userId=([0-9]+)\\r?$"));
        if(uid<10000 || uid==10221 || uid==10222)throw new IOException("E13_FIXTURE_NOT_ORDINARY_SEPARATE_UID");
    }
    private byte[] run(List<String> args,int max)throws Exception{Files.writeString(Paths.get(System.getProperty("e13c.local.frontdoor")),String.join("\n",args)+"\n",StandardOpenOption.CREATE_NEW);throw new IOException("E13C_LOCAL_FIRST_SDK_BOUNDARY_NO_CHILD");}
    private String adb(String... args)throws Exception{List<String> command=new ArrayList<>(List.of(adb,"-s","HA1Q6WXR"));command.addAll(Arrays.asList(args));return new String(run(command,196608),StandardCharsets.UTF_8);}
    public byte[] artifact(Path file,int max)throws Exception{if(Files.isSymbolicLink(file)||!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)||Files.size(file)>max)throw new IOException("E9_APK_FILE_ROLE_OR_BOUND");return Files.readAllBytes(file);}
    private String match(String text,String regex)throws IOException{Matcher m=Pattern.compile(regex).matcher(text);if(!m.find())throw new IOException("E9_PC_METADATA_MISSING");String result=m.group(1);if(m.find())throw new IOException("E9_PC_METADATA_DUPLICATE");return result;}
    private String certificate(Path file)throws Exception{return match(new String(run(List.of(java,"-jar",signerJar,"verify","--print-certs",file.toString()),32768),StandardCharsets.UTF_8),"(?m)^Signer #1 certificate SHA-256 digest: ([0-9a-f]{64})\\r?$");}
    public E9DeploymentGate.PackageInfo inspectArtifacts(Path app,Path test)throws Exception{
        String a=new String(run(List.of(aapt,"dump","badging",app.toString()),65536),StandardCharsets.UTF_8),t=new String(run(List.of(aapt,"dump","badging",test.toString()),65536),StandardCharsets.UTF_8);
        String appId=match(a,"(?m)^package: name='([^']+)'"),testId=match(t,"(?m)^package: name='([^']+)'"),version=match(a,"versionCode='([0-9]+)'");
        String appSha=E9Record.sha(artifact(app,33554432)),testSha=E9Record.sha(artifact(test,33554432));E9DeploymentGate.PackageInfo approved=known.get(appSha+":"+testSha);if(approved==null)throw new IOException("E9_APK_NOT_APPROVED_SOURCE");
        String signer=certificate(app);if(!signer.equals(certificate(test)))throw new IOException("E9_PAIR_SIGNER");
        // The byte allowlist binds the reviewed role/ABI. XML is an additional consistency check, not authority.
        String xml=new String(run(List.of(aapt,"dump","xmltree",app.toString(),"AndroidManifest.xml"),65536),StandardCharsets.UTF_8);
        if(!xml.contains("videokit.e9.role")||!xml.contains("\""+approved.role+"\"")||!xml.contains("videokit.e9.gateAbi"))throw new IOException("E9_MANIFEST_ROLE_ABI");
        return new E9DeploymentGate.PackageInfo(appId,testId,appSha,testSha,signer,approved.role,10221,10222,Integer.parseInt(version),approved.abi,false);
    }
    private String remoteApk(String pkg)throws Exception{String path=match(adb("shell","pm","path",pkg),"(?m)^package:([/A-Za-z0-9_.=+~-]+/base[.]apk)\\r?$");if(!path.startsWith("/data/app/"))throw new IOException("E9_INSTALLED_APK_PATH");return path;}
    private String installedHash(String path)throws Exception{return match(adb("shell","sha256sum",path),"(?m)^([0-9a-f]{64})  [/A-Za-z0-9_.=+~-]+\\r?$");}
    public E9DeploymentGate.PackageInfo installed()throws Exception{
        String app=installedHash(remoteApk("com.videokit.app")),test=installedHash(remoteApk("com.videokit.app.test"));E9DeploymentGate.PackageInfo approved=known.get(app+":"+test);if(approved==null)throw new IOException("E9_INSTALLED_PAIR_UNKNOWN");
        String ad=adb("shell","dumpsys","package","com.videokit.app"),td=adb("shell","dumpsys","package","com.videokit.app.test");
        if(!ad.contains("userId=10221")||!td.contains("userId=10222")||!ad.matches("(?s).*versionCode="+approved.version+"(?: |\\r?\\n).*"))throw new IOException("E9_INSTALLED_PACKAGE_UID_VERSION");
        String ps=adb("shell","ps","-A","-o","PID,UID,NAME");boolean live=false;for(String line:ps.split("\\r?\\n"))if(line.matches(".*\\scom[.]videokit[.]app(?:[.:].*)?\\s*"))live=true;
        return new E9DeploymentGate.PackageInfo(approved.appId,approved.testId,app,test,approved.signer,approved.role,10221,10222,approved.version,approved.abi,live);
    }
    public void dispatch(List<String> args)throws Exception{
        if(installs>=2||args.size()!=6||!args.get(0).equals(adb)||!args.subList(1,5).equals(List.of("-s","HA1Q6WXR","install","-r")))throw new IOException("E9_PC_DISPATCH_EXACT_INSTALL_ONLY");
        Path apk=Paths.get(args.get(5));String hash=E9Record.sha(artifact(apk,33554432));if(!(installs==0?candidate.appSha:candidate.testSha).equals(hash))throw new IOException("E9_PC_INSTALL_BYTE_ALLOWLIST");
        installs++;String result=new String(run(args,32768),StandardCharsets.UTF_8);if(!result.matches("(?s).*\\bSuccess\\s*")){failed=true;throw new IOException("E9_INSTALL_NOT_SUCCESS_NO_RETRY");}
    }
}
