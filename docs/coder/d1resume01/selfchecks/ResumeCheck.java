package com.videokit.spike.e4;
import java.io.*;import java.nio.file.*;import java.nio.charset.StandardCharsets;import java.util.*;
/** Local filesystem and scripted port fixtures only. No SDK, Android, socket or process dispatch. */
public final class ResumeCheck {
 static final String METHOD="ordinarySenderCannotBindCodec",SCOPE="a".repeat(64);
 static Path root;static int assertions;
 interface Checked {void run()throws Exception;}
 static void check(boolean ok,String why){assertions++;if(!ok)throw new AssertionError(why);}
 static void denied(String reason,Checked action)throws Exception{try{action.run();throw new AssertionError("expected "+reason);}catch(IOException failure){check(failure.getMessage().contains(reason),failure.toString());}}
 static byte[] canonical(Map<String,String> fields)throws Exception{return new E9Record(fields,8192).bytes();}
 static Map<String,String> disposition()throws Exception{return new TreeMap<>(E9Record.parse(Files.readAllBytes(root.resolve("reviewed-original-disposition.json")),8192).fields());}
 static Path fixture(String name,Map<String,String> fields)throws Exception{Path p=root.resolve(name);Files.createDirectory(p);Files.write(p.resolve("reviewed-original-disposition.json"),canonical(fields));return p;}
 static String digest(Path p)throws Exception{return E9Record.sha(Files.readAllBytes(p.resolve("reviewed-original-disposition.json")));}
 static E13PendingGuard enter(Path p,String scope)throws Exception{return E13PendingGuard.enter(p,digest(p),scope,METHOD);}
 static Map<String,String> scope(){E9DeploymentGate.PackageInfo p=E9DeploymentGate.e13eInstalledPredecessor();return E9Record.map("kind","e13DispatchScope","batch",E13Selection.BATCH,"scopeId","04267931-b5b6-47ce-a187-60e10a20a482","sourceAcceptance",E9DeploymentGate.E13E_SOURCE_DEPLOYMENT,"sourceApp",p.appSha,"sourceTest",p.testSha,"app","b".repeat(64),"test","c".repeat(64),"fixture","d".repeat(64),"fixtureSigner","e".repeat(64),"sourceReview","f".repeat(64),"methods",METHOD,"budget","source4096/read65536/open8/close16/process43/text3145728/output0");}
 static void guardChecks()throws Exception {
  Map<String,String> good=disposition();Path accepted=fixture("terminated-false",good);E13PendingGuard first=enter(accepted,SCOPE);
  check(first!=null,"typed administrative termination accepted");
  denied("E13_CASE_ALREADY_ENTERED_NO_CHILD",()->enter(accepted,SCOPE));
  denied("E13_OTHER_SCOPE_PENDING_NO_CHILD",()->enter(accepted,"b".repeat(64)));
  Path claim;try(var files=Files.list(accepted)){claim=files.filter(p->p.toString().endsWith(".claim")).findFirst().orElseThrow();}
  String id=claim.getFileName().toString().replace(".claim","");
  Files.write(accepted.resolve(id+".original-returned"),new E9Record(E9Record.map("kind","e13OriginalReturned","claim",id,"claimSha",E9Record.sha(Files.readAllBytes(claim)),"originalReturned","true","pcHandle","11111111-1111-4111-8111-111111111111","pcPid","1","pcThreadJoined","true"),1024).bytes());
  denied("E13_CASE_ALREADY_ENTERED_NO_CHILD",()->enter(accepted,SCOPE));
  check(enter(accepted,"b".repeat(64))!=null,"distinct scope only after synthetic fixture return marker");
  Path badPin=fixture("bad-pin",good);denied("E13_DISPOSITION_PIN",()->E13PendingGuard.enter(badPin,"0".repeat(64),SCOPE,METHOD));
  Map<String,String> wrong=new TreeMap<>(good);wrong.put("originalJavaReturn","true");Path p=fixture("termination-true",wrong);denied("E13_DISPOSITION_NOT_RETURN_ACK",()->enter(p,SCOPE));
  wrong=new TreeMap<>(good);wrong.put("outcome","ORIGINAL_RETURNED");Path q=fixture("returned-false",wrong);denied("E13_DISPOSITION_NOT_RETURN_ACK",()->enter(q,SCOPE));
  wrong=new TreeMap<>(good);wrong.put("serial","OTHER");Path s=fixture("wrong-serial",wrong);denied("E13_DISPOSITION_IDENTITY",()->enter(s,SCOPE));
  wrong=new TreeMap<>(good);wrong.put("originalScope","22222222-2222-4222-8222-222222222222");Path o=fixture("wrong-original-scope",wrong);denied("E13_DISPOSITION_IDENTITY",()->enter(o,SCOPE));
  wrong=new TreeMap<>(good);wrong.put("review","NOT_REVIEWED");Path r=fixture("bad-review-digest",wrong);denied("E9_DIGEST",()->enter(r,SCOPE));
  wrong=new TreeMap<>(good);wrong.put("extra","true");Path e=fixture("extra-field",wrong);denied("E9_RECORD_SCHEMA",()->enter(e,SCOPE));
  wrong=new TreeMap<>(good);wrong.put("outcome","ORIGINAL_RETURNED");wrong.put("originalJavaReturn","true");check(enter(fixture("historical-normal-pair-fixture-only",wrong),SCOPE)!=null,"normal pair schema retained, fixture only");
  Map<String,String> select=scope();check(E13HostActivationSession.scope(canonical(select)).get("methods").equals(METHOD),"single selection accepted");
  select.put("methods",String.join(",",new TreeSet<>(E13Selection.METHODS)));Map<String,String> all=select;denied("E13_SCOPE_BINDING",()->E13HostActivationSession.scope(canonical(all)));
  select=scope();select.put("budget","source4096/read65536/open8/close16/process51/text2097152/output0");Map<String,String> old=select;denied("E13_SCOPE_BINDING",()->E13HostActivationSession.scope(canonical(old)));
  Path sf=root.resolve("local-scope.json");Files.write(sf,canonical(scope()));String scopeHash=E9Record.sha(Files.readAllBytes(sf));
  for(String method:E13Selection.METHODS)if(!method.equals(METHOD))denied("E13_EXACT_CASE",()->E13HostCase.main(new String[]{sf.toString(),scopeHash,method}));
  check(E13HostRuntime.caseCommand(SCOPE,METHOD).contains("com.videokit.spike.e4.E13DeviceTests#"+METHOD),"exact argv selection");
 }
 static final class Scripted implements E9HostDeployment.Commands {
  final Path app,test,fixture;final String appHash,testHash,fixtureHash;int installs,calls;String oldApp="1".repeat(64),oldTest="2".repeat(64),signer="5".repeat(64),fixtureSigner="6".repeat(64);
  Scripted()throws Exception{app=root.resolve("fake-app.apk");test=root.resolve("fake-test.apk");fixture=root.resolve("fake-fixture.apk");Files.writeString(app,"LOCAL_FAKE_APP");Files.writeString(test,"LOCAL_FAKE_TEST");Files.writeString(fixture,"LOCAL_FAKE_FIXTURE");appHash=E9Record.sha(Files.readAllBytes(app));testHash=E9Record.sha(Files.readAllBytes(test));fixtureHash=E9Record.sha(Files.readAllBytes(fixture));}
  public byte[] run(List<String> a,int max)throws Exception {
   calls++;System.out.println("TRACE "+calls+" "+max+" "+Base64.getUrlEncoder().withoutPadding().encodeToString(String.join("\n",a).getBytes(StandardCharsets.UTF_8)));
   String result;
   if(a.contains("badging")){String file=a.get(a.size()-1);result="package: name='"+(file.equals(app.toString())?"com.videokit.app":file.equals(test.toString())?"com.videokit.app.test":"com.videokit.e13.sender")+"' versionCode='"+(file.equals(fixture.toString())?3:19)+"'\n";}
   else if(a.contains("xmltree"))result="videokit.e9.role \"ACTIVATION\" videokit.e9.gateAbi\n";
   else if(a.contains("--print-certs"))result="Signer #1 certificate SHA-256 digest: "+(a.get(a.size()-1).equals(fixture.toString())?fixtureSigner:signer)+"\n";
   else if(a.contains("install")){installs++;result="Success\n";}
   else if(a.contains("run-as"))result=a.contains("com.videokit.app.test")?"10222:4741\n":"10221:6972\n";
   else if(a.contains("path"))result="package:/data/app/"+a.get(a.size()-1)+"/base.apk\n";
   else if(a.contains("sha256sum")){String path=a.get(a.size()-1);String h=path.contains("com.videokit.e13.sender")?(installs==3?fixtureHash:"868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8"):path.contains("com.videokit.app.test")?(installs>=2?testHash:oldTest):(installs>=1?appHash:oldApp);result=h+"  "+path+"\n";}
   else if(a.contains("dumpsys")){String pkg=a.get(a.size()-1);result="userId="+(pkg.equals("com.videokit.app")?10221:pkg.equals("com.videokit.app.test")?10222:10228)+"\nversionCode="+(installs>=2?19:17)+" \n";}
   else if(a.contains("list"))result="package:com.videokit.e13.sender\n";
   else if(a.contains("ps"))result="PID UID NAME\n";
   else throw new AssertionError("unmodeled command "+a);
   byte[] raw=result.getBytes(StandardCharsets.UTF_8);check(raw.length<=max,"scripted output bound");return raw;
  }
 }
 static void deploymentTrace()throws Exception{
  Scripted f=new Scripted();E9DeploymentGate.PackageInfo original=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",f.oldApp,f.oldTest,f.signer,"ACTIVATION",10221,10222,17,1,false),target=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",f.appHash,f.testHash,f.signer,"ACTIVATION",10221,10222,19,1,false);
  E9HostDeployment p=new E9HostDeployment(f,Paths.get("D:/Android/SDK"),Paths.get("D:/Android/Android Studio/jbr"),original,target);
  p.requireE11DataIdentity();check(p.inspectArtifacts(f.app,f.test).version==19,"scripted artifact identity");check(p.installed().version==17,"scripted predecessor");
  String adb=p.adb();p.dispatch(List.of(adb,"-s","HA1Q6WXR","install","-r",f.app.toAbsolutePath().toString()));p.dispatch(List.of(adb,"-s","HA1Q6WXR","install","-r",f.test.toAbsolutePath().toString()));check(p.installed().version==19,"scripted target");
  p.requireE11DataIdentity();p.deployE13Fixture(f.fixture,f.fixtureHash,f.fixtureSigner);check(f.calls==35,"exact deployment children");
 }
 public static void main(String[] args)throws Exception{root=Paths.get(args[0]);Files.createDirectory(root);Files.copy(Paths.get(args[1]),root.resolve("reviewed-original-disposition.json"));guardChecks();deploymentTrace();System.out.println("PASS_RESUME_OFFLINE assertions="+assertions+" sdkCalls=0 childProcesses=0 originalCustodyRootAccesses=0");}
}
