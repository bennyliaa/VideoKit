package com.videokit.spike.e4;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Explicit fresh durability observation. It never appends R/S, repairs metadata, or changes an old outcome. */
public final class E5AFinalObservation implements E5AAdmission.Proof {
    public interface Platform extends E5N2Recovery.Platform {void requireRecoveryWriterDead(E5AOwner writer)throws Exception;}
    private static final Set<E5AFinalObservation> ACTIVE=ConcurrentHashMap.newKeySet();
    public static int retained(){return ACTIVE.size();}
    private final Path files,budget,out,archive;private final Platform platform;
    private final List<E4Owned<?>> holders=new ArrayList<>();private E4OutputBudget validation;
    private boolean used,completed,failed;private String stage="NEW",settlement="",hash="";private long length;
    public E5AFinalObservation(Path root,Platform p){files=root.toAbsolutePath().normalize();budget=files.resolve("e4a_output_budget");out=files.resolve("e4a_outputs");archive=budget.resolve("N2-e5-recovery");platform=p;}
    public Path budget(){return budget;}
    private <T>E4Owned<T> holder(Path p,E4Owned.Action<T> closer)throws IOException{if(holders.size()>=48)throw new IOException("E5A_OBSERVATION_HOLDER_BOUND");E4Owned<T> h=new E4Owned<>(p,closer);holders.add(h);return h;}
    private void directory(Path p)throws Exception{BasicFileAttributes a=Files.readAttributes(p,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);if(!a.isDirectory() || a.isSymbolicLink())throw new IOException("E5A_OBSERVATION_DIRECTORY_ROLE");}
    private byte[] read(Path p,int min,int max)throws Exception {
        BasicFileAttributes a=Files.readAttributes(p,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);if(!a.isRegularFile() || a.size()<min || a.size()>max)throw new IOException("E5A_OBSERVATION_METADATA_ROLE");
        E4Owned<InputStream> h=holder(p,InputStream::close);h.allocate(()->Files.newInputStream(p));try{ByteArrayOutputStream b=new ByteArrayOutputStream();byte[] buffer=new byte[512];int n;while((n=h.original().read(buffer))!=-1){if(b.size()+n>max)throw new IOException("E5A_OBSERVATION_METADATA_GREW");b.write(buffer,0,n);}if(b.size()<min)throw new IOException("E5A_OBSERVATION_METADATA_SHRANK");return b.toByteArray();}finally{h.close();}
    }
    private String ascii(Path p,int min,int max)throws Exception{return new String(read(p,min,max),StandardCharsets.US_ASCII);}
    private static void identity(byte[] raw)throws Exception {
        DataInputStream d=new DataInputStream(new ByteArrayInputStream(raw));
        if(!d.readUTF().equals("E4A_ORIGINAL_IDENTITY_V1") || !d.readUTF().equals(E5N2Recovery.BATCH) || !d.readUTF().equals(E5N2Recovery.BUDGET) || !d.readUTF().equals(E5N2Recovery.HEX) || d.readLong()!=E5N2Recovery.EPOCH || d.readLong()!=1 || !d.readUTF().equals(E5N2Recovery.SERVICE) || d.readInt()!=E5N2Recovery.UID || d.readInt()!=E5N2Recovery.UID || !d.readUTF().equals(E5N2Recovery.TASK) || d.read()!=-1)throw new IOException("E5A_OBSERVATION_ORIGINAL_IDENTITY");
    }
    private static String journal(byte[] bytes,int state)throws Exception {
        DataInputStream d=new DataInputStream(new ByteArrayInputStream(bytes));if(d.readInt()!=0x45344131 || !d.readUTF().equals(E5N2Recovery.TASK) || d.readInt()!=state)throw new IOException("E5A_OBSERVATION_JOURNAL");String epoch=d.readUTF();if(!UUID.fromString(epoch).toString().equals(epoch) || !d.readBoolean() || d.read()!=-1)throw new IOException("E5A_OBSERVATION_JOURNAL");return epoch;
    }
    private void metadata()throws Exception {
        if(Files.exists(budget.resolve("operation.pending"),LinkOption.NOFOLLOW_LINKS))throw new IOException("E5A_OBSERVATION_PENDING_OR_PARTIAL");
        byte[] before=read(archive.resolve("identity.before"),225,225);identity(before);if(!Arrays.equals(before,read(out.resolve(E5N2Recovery.TASK+".identity"),225,225)))throw new IOException("E5A_OBSERVATION_IDENTITY_CHANGED");
        if(!journal(read(archive.resolve("journal.before"),85,85),0).equals(E5N2Recovery.LEASE) || !ascii(archive.resolve("lease.before"),36,36).equals(E5N2Recovery.LEASE) || !ascii(archive.resolve("ledger.before"),192,192).equals(E5N2Recovery.ORIGINAL))throw new IOException("E5A_OBSERVATION_BEFORE_IMAGES");
        String fence=journal(read(out.resolve(E5N2Recovery.TASK+".journal"),85,85),2);if(fence.equals(E5N2Recovery.LEASE) || !ascii(out.resolve(E5N2Recovery.TASK+".lease"),36,36).equals(fence))throw new IOException("E5A_OBSERVATION_FENCE");
        String proof=ascii(archive.resolve("proof.txt"),1,2048);String[] lines=proof.split("\n");if(lines.length!=6 || !lines[0].equals("E5_N2_DEATH_FENCE_ABORT_V1") || !lines[3].equals("originalCloseACK=false") || !lines[4].equals("fence="+fence))throw new IOException("E5A_OBSERVATION_PROOF");
        for(int k=1;k<=2;k++){String[] p=lines[k].split(" ");if(p.length!=7 || !p[6].equals("absent=true"))throw new IOException("E5A_OBSERVATION_OLD_DEATH");new E5N2Recovery.Death(Integer.parseInt(p[0]),Integer.parseInt(p[1]),p[2],Long.parseLong(p[3]),Integer.parseInt(p[4]),Integer.parseInt(p[5]),true).verify(k==1?E5N2Recovery.HOST:E5N2Recovery.CODEC);}
        String[] s=lines[5].split(" ");if(s.length!=6 || !s[0].equals("S") || !s[1].equals(E5N2Recovery.TASK) || !s[2].equals("ABORTED") || !s[4].matches("[a-f0-9]{64}"))throw new IOException("E5A_OBSERVATION_SETTLEMENT");length=Long.parseLong(s[3]);hash=s[4];if(length<0 || length>2097152 || !E5N2Recovery.hex(MessageDigest.getInstance("SHA-256").digest((E5N2Recovery.CHAIN+" "+String.join(" ",Arrays.copyOf(s,5))).getBytes(StandardCharsets.US_ASCII))).equals(s[5]))throw new IOException("E5A_OBSERVATION_SETTLEMENT_CHAIN");settlement=lines[5]+"\n";
        if(!ascii(budget.resolve("ledger.bin"),1,131072).startsWith(E5N2Recovery.ORIGINAL+settlement) || !ascii(budget.resolve("identity.anchor"),36,36).equals(E5N2Recovery.BUDGET) || !ascii(budget.resolve("N2-e5-recovery.complete"),E5N2Recovery.COMPLETE.length(),E5N2Recovery.COMPLETE.length()).equals(E5N2Recovery.COMPLETE) || read(budget.resolve("operation.pending.N2-e5-aborted"),0,0).length!=0)throw new IOException("E5A_OBSERVATION_PARTIAL_COMPLETION");
    }
    private E4Owned<E4FencedTask.LeaseGuard> lock(Path p)throws Exception {E4Owned<E4FencedTask.LeaseGuard> h=holder(p,E4FencedTask.LeaseGuard::close);platform.lock(p,h);return h;}
    private void forceCurrent(Path p,int max,boolean output)throws Exception {
        BasicFileAttributes a=Files.readAttributes(p,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);if(!a.isRegularFile() || a.size()>max)throw new IOException("E5A_OBSERVATION_FORCE_ROLE");
        E4Owned<FileChannel> h=holder(p,c->platform.closeMetadata(p,c));h.allocate(()->FileChannel.open(p,StandardOpenOption.READ,StandardOpenOption.WRITE));
        try{platform.forceMetadata(p,h.original());if(output){MessageDigest sha=MessageDigest.getInstance("SHA-256");ByteBuffer b=ByteBuffer.allocate(65536);long n=0;while(h.original().read(b)!=-1){b.flip();n+=b.remaining();if(n>2097152)throw new IOException("E5A_OBSERVATION_OUTPUT_BOUND");sha.update(b);b.clear();}if(n!=length || !E5N2Recovery.hex(sha.digest()).equals(hash))throw new IOException("E5A_OBSERVATION_RETAINED_OUTPUT");}}
        finally{h.close();}
    }
    private boolean returned(){if(!platform.returned())return false;for(E4Owned<?> h:holders)if(!h.returned())return false;if(validation!=null)for(E4Owned<?> h:validation.originalHolders())if(!h.returned())return false;return true;}
    public boolean actualReturnProven(){return completed && !failed && returned() && !ACTIVE.contains(this);}
    public String observe(){
        synchronized(E5AFinalObservation.class){
            if(used || !ACTIVE.isEmpty() || E5N2Recovery.retainedOperations()!=0)return "BLOCKED E5A_PRIOR_OBSERVATION_OR_RECOVERY_PENDING";used=true;ACTIVE.add(this);
            E4Owned<E4FencedTask.LeaseGuard> owner=null,lease=null;
            try{
                stage="WRITER_DEATH";directory(files);directory(budget);directory(out);directory(archive);E5AOwner writer=E5AOwner.parse(read(archive.resolve("recovery.owner"),1,256));platform.requireRecoveryWriterDead(writer);
                stage="EXCLUSIVE_ORIGINAL_LEASES";owner=lock(out.resolve(E5N2Recovery.TASK+".owner"));lease=lock(out.resolve(E5N2Recovery.TASK+".lease"));
                stage="EXACT_SETTLED_STATE";metadata();validation=new E4OutputBudget(budget,E5N2Recovery.BUDGET,E5N2Recovery.TASK,E5N2Recovery.BATCH,p->{try{platform.sync(p);}catch(Exception e){throw new IOException(e);}});long[] accounting=validation.inspect();if(accounting[1]!=0)throw new IOException("E5A_OBSERVATION_NEW_RESERVATION_PENDING");
                stage="FRESH_FORCE_AND_ACTUAL_CLOSE";
                for(String name:new String[]{"identity.before","journal.before","lease.before","ledger.before","recovery.owner","proof.txt"})forceCurrent(archive.resolve(name),2048,false);
                for(String name:new String[]{"ledger.bin","identity.anchor","N2-e5-recovery.complete","operation.pending.N2-e5-aborted"})forceCurrent(budget.resolve(name),131072,false);
                for(String suffix:new String[]{".identity",".journal",".lease"})forceCurrent(out.resolve(E5N2Recovery.TASK+suffix),256,false);
                forceCurrent(out.resolve(E5N2Recovery.TASK+".mp4"),2097152,true);platform.sync(archive);platform.sync(out);platform.sync(budget);
                stage="FINAL_STATE_READBACK";metadata();
                stage="ACTUAL_LOCK_CLOSE";lease.close();owner.close();if(!returned())throw new IOException("E5A_OBSERVATION_OWNER_UNRETURNED");completed=true;return "FRESH_OBSERVATION_ADMITTED oldRecoveryResult=UNCHANGED oldSyncReturn=NOT_INFERRED oldCloseACK=false";
            }catch(Throwable failure){failed=true;return "BLOCKED "+stage+":"+E5Trace.safe(failure.getClass().getSimpleName()+":"+failure.getMessage());}
            finally{
                // Never release guards around an unreturned metadata/dir operation. The original operation stays reachable.
                boolean pending=false;for(E4Owned<?> h:holders)if(h!=owner && h!=lease && !h.returned())pending=true;if(!platform.returned())pending=true;if(validation!=null)for(E4Owned<?> h:validation.originalHolders())if(!h.returned())pending=true;
                if(!pending){if(lease!=null && (lease.state()==E4Owned.State.OPEN || lease.state()==E4Owned.State.READY))try{lease.close();}catch(Exception ignored){}if(owner!=null && (owner.state()==E4Owned.State.OPEN || owner.state()==E4Owned.State.READY))try{owner.close();}catch(Exception ignored){}}
                if(completed && returned()){ACTIVE.remove(this);E5AAdmission.fromObservation(this);}
                // A failed observation is never automatically retried in this process.
            }
        }
    }
}
