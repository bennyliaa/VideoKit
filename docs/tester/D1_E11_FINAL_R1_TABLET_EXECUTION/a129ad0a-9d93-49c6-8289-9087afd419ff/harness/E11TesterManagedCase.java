package com.videokit.spike.e4;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Tester adapter: exact reviewed case through UNCHANGED production supervisor. No close/kill/retry of Android. */
public final class E11TesterManagedCase {
 private static final class Custody {volatile boolean androidEntered,independentlyFinished;boolean returned(){return !androidEntered||independentlyFinished;}}
 private static byte[] read(Path p,int max)throws Exception{if(Files.isSymbolicLink(p)||!Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS)||Files.size(p)>max)throw new IOException("TESTER_INPUT_ROLE");return Files.readAllBytes(p);}
 public static void main(String[] argv)throws Exception{
  if(argv.length!=2)throw new IOException("TESTER_EXPLICIT_PINNED_CASE_ONLY");E9Record.digest(argv[1]);byte[] input=read(Paths.get(argv[0]),8192);if(!E9Record.sha(input).equals(argv[1]))throw new IOException("TESTER_COMMAND_PIN");E9Record c=E9Record.parse(input,8192);c.exact("kind","case","scope","app","test","mp4","avi","normalIndex");if(!c.get("kind").equals("e11TesterCase"))throw new IOException("TESTER_CASE_SCHEMA");
  Map<String,String> args=new TreeMap<>();args.put("class","com.videokit.spike.e4.E4DeviceTests#"+c.get("case"));args.put("e4Case",c.get("case"));args.put("e4Batch",E11Selection.BATCH);args.put("e4BudgetIdentity",E5N2Recovery.BUDGET);args.put("e5aObservation","REVIEWED_ORIGINAL_N2_SETTLEMENT");args.put("e5aSettlementReceiptSha256",E11Selection.FINAL_REVIEW);args.put("e11ScopeSha256",c.get("scope"));args.put("e11ReleaseAppSha256",c.get("app"));args.put("e11ReleaseTestSha256",c.get("test"));
  if(!c.get("mp4").equals("ABSENT"))args.put("e11Mp4Receipt",c.get("mp4"));if(!c.get("avi").equals("ABSENT"))args.put("e11AviReceipt",c.get("avi"));if(!c.get("normalIndex").equals("ABSENT"))args.put("e4NormalReceiptSha256",c.get("normalIndex"));E11Selection.require(args);
  List<String> command=new ArrayList<>(List.of("D:/Android/SDK/platform-tools/adb.exe","-s","HA1Q6WXR","shell","am","instrument","-w","-r"));for(Map.Entry<String,String> row:args.entrySet()){command.add("-e");command.add(row.getKey());command.add(row.getValue());}command.add("com.videokit.app.test/com.videokit.spike.e4.E11ActivationInstrumentation");
  E9PcSupervisor pc=new E9PcSupervisor("E11_CASE_"+c.get("case"));Custody custody=new Custody();pc.retainAuthority(custody,null,custody::returned);
  E9HostRegistry.boundary(pc,()->{
   custody.androidEntered=true;byte[] actual=pc.run("E11_REVIEWED_SINGLE_METHOD",command,1048576,E9PcSupervisor.GENERAL_NS,false);
   System.out.println("E11_ORIGINAL_CLIENT_RAW_BEGIN");System.out.write(actual);System.out.println("\nE11_ORIGINAL_CLIENT_RAW_END");System.out.flush();
   for(E9PcSupervisor.Operation op:pc.operations())System.out.write(op.status().bytes());System.out.write(pc.status().bytes());System.out.println("E11_WAIT_INDEPENDENT_ANDROID_FINISH raw="+E9Record.sha(actual));System.out.flush();
   String line=E9PcSupervisor.consoleLine(System.in,16384);if(line==null||!line.startsWith("CONFIRM_FINISH "))throw new IOException("TESTER_NO_ANDROID_FINISH_ACCEPTANCE");String[] fields=line.split(" ",3);if(fields.length!=3)throw new IOException("TESTER_FINISH_RECEIPT_SCHEMA");E9Record.digest(fields[2]);byte[] accepted=read(Paths.get(fields[1]),4096);if(!E9Record.sha(accepted).equals(fields[2]))throw new IOException("TESTER_FINISH_RECEIPT_PIN");E9Record proof=E9Record.parse(accepted,4096);proof.exact("kind","scope","case","raw","pid","normalFinishEvidence","independentAudit","disposition");
   if(!proof.get("kind").equals("e11IndependentFinishReview")||!proof.get("scope").equals(c.get("scope"))||!proof.get("case").equals(c.get("case"))||!proof.get("raw").equals(E9Record.sha(actual))||!Set.of("NORMAL_AND_OWNERS_RETURNED","KNOWN_FAILED_AND_OWNERS_RETURNED").contains(proof.get("disposition")))throw new IOException("TESTER_FINISH_SCOPE_OR_OWNERS_UNKNOWN");E9Record.digest(proof.get("normalFinishEvidence"));E9Record.digest(proof.get("independentAudit"));proof.number("pid",Integer.MAX_VALUE);
   custody.independentlyFinished=true;System.out.println("E11_INDEPENDENT_ANDROID_FINISH_ACCEPTED disposition="+proof.get("disposition"));System.out.flush();
  });
 }
}
