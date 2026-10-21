package com.videokit.spike.e4;
import java.io.*;import java.nio.*;import java.nio.channels.*;import java.nio.file.*;import java.util.*;
/** Fixed device/package custody slot shared by real public entries, independent of new UUIDs/PIDs. */
public final class E13PendingGuard implements AutoCloseable {
 static final String OLD_SCOPE="aeefe32f-816d-4c0b-aca7-16f76dbd45ff";
 private final Path root;private final String id;private boolean returned;
 private E13PendingGuard(Path root,String id){this.root=root;this.id=id;}
 public static E13PendingGuard enter(String scope,String method)throws Exception{return enter(E13GuardLocation.ROOT,E13GuardLocation.DISPOSITION_SHA,scope,method);}
 static E13PendingGuard enter(Path root,String dispositionSha,String scope,String method)throws Exception{
  E9Record.digest(scope);if(!method.equals("DEPLOY")&&!E13Selection.METHODS.contains(method))throw new IOException("E13_CUSTODY_ROLE");
  Files.createDirectories(root);for(Path p=root.toAbsolutePath();p!=null;p=p.getParent())if(Files.isSymbolicLink(p))throw new IOException("E13_CUSTODY_NO_SYMLINK");
  try(FileChannel channel=FileChannel.open(root.resolve("custody.lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE);FileLock lock=channel.tryLock()){
   if(lock==null)throw new IOException("E13_CUSTODY_BUSY_NO_CHILD");
   if(dispositionSha.equals("ABSENT"))throw new IOException("E13_ORIGINAL_E13C_PENDING_NO_CHILD");
   E9Record.digest(dispositionSha);Path approved=root.resolve("reviewed-original-disposition.json");byte[] bytes=Files.readAllBytes(approved);if(bytes.length>8192||!E9Record.sha(bytes).equals(dispositionSha))throw new IOException("E13_DISPOSITION_PIN");
   E9Record d=E9Record.parse(bytes,8192);d.exact("kind","originalScope","serial","packages","outcome","originalJavaReturn","caseEvidence","diagnosticDisposition","review","authorization");
   if(!d.get("kind").equals("e13ReviewedOriginalDisposition")||!d.get("originalScope").equals(OLD_SCOPE)||!d.get("serial").equals("HA1Q6WXR")||!d.get("packages").equals("com.videokit.app,com.videokit.app.test,com.videokit.e13.sender"))throw new IOException("E13_DISPOSITION_IDENTITY");
   if(!(d.get("outcome").equals("ORIGINAL_RETURNED")&&d.get("originalJavaReturn").equals("true")||d.get("outcome").equals("TERMINATED_WITHOUT_RETURN")&&d.get("originalJavaReturn").equals("false")))throw new IOException("E13_DISPOSITION_NOT_RETURN_ACK");
   for(String k:List.of("caseEvidence","diagnosticDisposition","review","authorization"))E9Record.digest(d.get(k));
   Path active=root.resolve("active.pointer");int history=0;try(DirectoryStream<Path> claims=Files.newDirectoryStream(root,"*.claim")){for(Path claim:claims){if(++history>32)throw new IOException("E13_CUSTODY_HISTORY_BOUND");String old=claim.getFileName().toString().replace(".claim","");E9Record.uuid(old);Path marker=root.resolve(old+".original-returned");if(!Files.isRegularFile(marker,LinkOption.NOFOLLOW_LINKS)||Files.size(marker)>1024)throw new IOException("E13_OTHER_SCOPE_PENDING_NO_CHILD");E9Record r=E9Record.parse(Files.readAllBytes(marker),1024);r.exact("kind","claim","claimSha","originalReturned");if(!r.get("kind").equals("e13OriginalReturned")||!r.get("claim").equals(old)||!r.get("claimSha").equals(E9Record.sha(Files.readAllBytes(claim)))||!r.get("originalReturned").equals("true"))throw new IOException("E13_PARTIAL_RETURN_MARKER_NO_CHILD");}}
   String id=UUID.randomUUID().toString();byte[] intent=new E9Record(E9Record.map("kind","e13PendingClaim","serial","HA1Q6WXR","packages",d.get("packages"),"scope",scope,"method",method,"claim",id,"disposition",dispositionSha,"state","ORIGINAL_PENDING"),4096).bytes();
   writeNew(root.resolve(id+".claim"),intent);Path temporary=root.resolve(id+".pointer");writeNew(temporary,(id+"\n").getBytes(java.nio.charset.StandardCharsets.US_ASCII));Files.move(temporary,active,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);return new E13PendingGuard(root,id);
  }catch(OverlappingFileLockException e){throw new IOException("E13_CUSTODY_BUSY_NO_CHILD",e);}
 }
 private static void writeNew(Path path,byte[] bytes)throws Exception{try(FileChannel f=FileChannel.open(path,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){ByteBuffer b=ByteBuffer.wrap(bytes);while(b.hasRemaining())if(f.write(b)<=0)throw new IOException("E13_CUSTODY_WRITE");f.force(true);}}
 /** Only called after SAME actual supervisor fully terminates. Missing/partial marker keeps the seal closed. */
 public synchronized void originalReturned(boolean actual)throws Exception{if(!actual||returned)throw new IOException("E13_CUSTODY_ORIGINAL_RETURN_REQUIRED");String digest=E9Record.sha(Files.readAllBytes(root.resolve(id+".claim")));writeNew(root.resolve(id+".original-returned"),new E9Record(E9Record.map("kind","e13OriginalReturned","claim",id,"claimSha",digest,"originalReturned","true"),1024).bytes());returned=true;}
 public void close(){/* lexical scope exit or an exception is NOT an original return ACK */}
}
