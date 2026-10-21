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
    /** No shell interpolation; bounded merged output. A timeout is retained, never killed/retried. */
    public static final class Processes implements Commands {
        private final List<Process> retained=new ArrayList<>();private boolean uncertain;
        public synchronized byte[] run(List<String> args,int max)throws Exception{
            if(uncertain)throw new IOException("E9_PC_PROCESS_UNCERTAIN");
            Process p=new ProcessBuilder(args).redirectErrorStream(true).start();retained.add(p);
            ByteArrayOutputStream bytes=new ByteArrayOutputStream();Throwable[] failure={null};
            Thread reader=new Thread(()->{try(InputStream in=p.getInputStream()){byte[] b=new byte[4096];for(int n;(n=in.read(b))!=-1;){if(bytes.size()+n>max)throw new IOException("E9_PC_OUTPUT_BOUND");bytes.write(b,0,n);}}catch(Throwable t){failure[0]=t;}},"E9-PC-original-output");reader.setDaemon(true);reader.start();
            if(!p.waitFor(55,TimeUnit.SECONDS)){uncertain=true;throw new IOException("E9_PC_PROCESS_TIMEOUT_RETAINED_NO_KILL");}
            reader.join(1000);if(reader.isAlive()||failure[0]!=null){uncertain=true;throw new IOException("E9_PC_OUTPUT_RETURN_UNKNOWN",failure[0]);}
            if(p.exitValue()!=0){uncertain=true;throw new IOException("E9_PC_NONZERO_NO_RETRY:"+p.exitValue());}retained.remove(p);return bytes.toByteArray();
        }
    }
    private final Commands commands;private final E9DeploymentGate.PackageInfo candidate;private final String adb,aapt,java,signerJar;private final Map<String,E9DeploymentGate.PackageInfo> known=new HashMap<>();private boolean failed;private int installs;
    public E9HostDeployment(Commands commands,Path sdk,Path jdk,E9DeploymentGate.PackageInfo original,E9DeploymentGate.PackageInfo candidate){
        this.commands=Objects.requireNonNull(commands);this.candidate=candidate;adb=sdk.resolve("platform-tools/adb.exe").toString();aapt=sdk.resolve("build-tools/36.0.0/aapt.exe").toString();java=jdk.resolve("bin/java.exe").toString();signerJar=sdk.resolve("build-tools/36.0.0/lib/apksigner.jar").toString();known.put(original.appSha+":"+original.testSha,original);known.put(candidate.appSha+":"+candidate.testSha,candidate);
    }
    public String adb(){return adb;}
    private byte[] run(List<String> args,int max)throws Exception{if(failed)throw new IOException("E9_PC_PORT_FAILED_NO_RETRY");try{return commands.run(args,max);}catch(Exception e){failed=true;throw e;}}
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
