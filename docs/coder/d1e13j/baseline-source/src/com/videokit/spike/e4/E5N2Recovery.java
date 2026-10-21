package com.videokit.spike.e4;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** One original N2 incident only. No arbitrary task, budget, PID, path, or caller-supplied proof. */
public final class E5N2Recovery implements E5AAdmission.Proof {
    public static final String TASK="86cafdb3-0fc4-447d-920b-b19c884bf494",HEX="86cafdb30fc4447d920bb19c884bf494";
    public static final String BUDGET="730a73e1-50e1-4198-a515-047104f00e31",BATCH="D1-E4A-N2-TABLET-20261017";
    public static final String SERVICE="775a5ee9-fff3-4340-a03b-97751099c0c4",LEASE="a256356e-361b-47a0-b2e9-32dce4ccea8e";
    public static final long EPOCH=5131975343750146374L;
    public static final int HOST=24853,CODEC=24873,UID=10221;
    public static final String HEADER="E4A1 "+BUDGET+" 4194304 2097152 128\n";
    public static final String CHAIN="6660cfb1b19dee6ced8fb9427d6605eb394ba9ecd9ab5931905a9a8727ffd026";
    public static final String ORIGINAL=HEADER+"R "+TASK+" "+BATCH+" "+CHAIN+"\n";
    public static final String COMPLETE="E5_N2_ABORTED_SETTLED "+TASK+" "+BUDGET+"\n";
    private static final Set<E5N2Recovery> ACTIVE=ConcurrentHashMap.newKeySet();
    private static final Object SERIAL=new Object();
    public static int retainedOperations(){return ACTIVE.size();}
    public interface Platform {
        Death death(int pid)throws Exception;
        void existingGuard(Path path,E5BGuard.Role role,String epoch,E5BFileId expected,E4Owned<E4FencedTask.LeaseGuard> holder)throws Exception;
        void sync(Path directory)throws Exception;
        boolean returned();
        E5AOwner recoveryOwner()throws Exception;
        default void forceMetadata(Path path,FileChannel channel)throws Exception {channel.force(true);}
        default void closeMetadata(Path path,FileChannel channel)throws Exception {channel.close();}
    }
    public static final class Death {
        public final int pid,uid,reason,status;public final long timestamp;public final String process;public final boolean absent;
        public Death(int p,int u,String n,long t,int r,int s,boolean a){pid=p;uid=u;process=n;timestamp=t;reason=r;status=s;absent=a;}
        void verify(int expected)throws IOException {
            String name=expected==HOST?"com.videokit.app":"com.videokit.app:e4_codec";
            if(pid!=expected || uid!=UID || !name.equals(process) || timestamp<1792208947872L || timestamp>1792208970000L || reason<=0 || !absent)throw new IOException("E5_N2_DEATH_UNPROVEN");
        }
        String record(){return pid+" "+uid+" "+process+" "+timestamp+" "+reason+" "+status+" absent="+absent;}
    }
    public static final class Result {
        public final String status,detail,sha;public final long bytes;public final boolean oldCloseAck=false;
        Result(String s,String d,long n,String h){status=s;detail=d;bytes=n;sha=h;}
        public String toString(){return status+" "+detail+" retainedBytes="+bytes+" sha="+sha+" originalCloseACK=false retainedOperations="+retainedOperations();}
    }
    private final Path files,out,budget,archive;private final Platform platform;
    private final List<E4Owned<?>> holders=new ArrayList<>();private boolean used,mutated,poisoned,completed;private String stage="NEW";
    private byte[] originalJournal,originalIdentity;private Death host,codec;
    public E5N2Recovery(Path files,Platform platform){this.files=files.toAbsolutePath().normalize();out=this.files.resolve("e4a_outputs");budget=this.files.resolve("e4a_output_budget");archive=budget.resolve("N2-e5-recovery");this.platform=Objects.requireNonNull(platform);}
    private Path role(Path p,long min,long max)throws Exception {
        BasicFileAttributes a=Files.readAttributes(p,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
        if(!a.isRegularFile() || a.isSymbolicLink() || a.size()<min || a.size()>max)throw new IOException("E5_N2_FILE_ROLE_OR_BOUND");return p;
    }
    private void directory(Path p)throws Exception {BasicFileAttributes a=Files.readAttributes(p,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);if(!a.isDirectory() || a.isSymbolicLink())throw new IOException("E5_N2_DIRECTORY_ROLE");}
    private <T>E4Owned<T> holder(Path p,E4Owned.Action<T> close)throws IOException {if(holders.size()>=32)throw new IOException("E5_N2_OWNER_BOUND");E4Owned<T> h=new E4Owned<>(p,close);holders.add(h);return h;}
    private byte[] read(Path p,int min,int max)throws Exception {
        role(p,min,max);E4Owned<InputStream> h=holder(p,InputStream::close);h.allocate(()->Files.newInputStream(p,LinkOption.NOFOLLOW_LINKS));
        try{ByteArrayOutputStream b=new ByteArrayOutputStream();byte[] buffer=new byte[512];int n;while((n=h.original().read(buffer))!=-1){if(b.size()+n>max)throw new IOException("E5_N2_METADATA_GREW");b.write(buffer,0,n);}if(b.size()<min)throw new IOException("E5_N2_METADATA_SHRANK");return b.toByteArray();}finally{h.close();}
    }
    private void writeNew(Path p,byte[] raw)throws Exception {
        E4Owned<FileChannel> h=holder(p,c->platform.closeMetadata(p,c));h.allocate(()->FileChannel.open(p,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE));
        try{ByteBuffer b=ByteBuffer.wrap(raw);while(b.hasRemaining())if(h.original().write(b)<=0)throw new IOException("E5_N2_WRITE");platform.forceMetadata(p,h.original());}finally{h.close();}
    }
    private void originals()throws Exception {
        directory(files);directory(out);directory(budget);
        originalIdentity=read(out.resolve(TASK+".identity"),225,225);DataInputStream i=new DataInputStream(new ByteArrayInputStream(originalIdentity));
        if(!"E4A_ORIGINAL_IDENTITY_V1".equals(i.readUTF()) || !BATCH.equals(i.readUTF()) || !BUDGET.equals(i.readUTF()) || !HEX.equals(i.readUTF()) || i.readLong()!=EPOCH || i.readLong()!=1 || !SERVICE.equals(i.readUTF()) || i.readInt()!=UID || i.readInt()!=UID || !TASK.equals(i.readUTF()) || i.read()!=-1)throw new IOException("E5_N2_IDENTITY_MISMATCH");
        originalJournal=read(out.resolve(TASK+".journal"),85,85);DataInputStream j=new DataInputStream(new ByteArrayInputStream(originalJournal));
        if(j.readInt()!=0x45344131 || !TASK.equals(j.readUTF()) || j.readInt()!=0 || !LEASE.equals(j.readUTF()) || !j.readBoolean() || j.read()!=-1)throw new IOException("E5_N2_WRITING_MISMATCH_NO_REPEAT");
        if(!LEASE.equals(new String(read(out.resolve(TASK+".lease"),36,36),StandardCharsets.US_ASCII)) || !BUDGET.equals(new String(read(budget.resolve("identity.anchor"),36,36),StandardCharsets.US_ASCII)))throw new IOException("E5_N2_ANCHOR_OR_LEASE");
        if(!ORIGINAL.equals(new String(read(budget.resolve("ledger.bin"),1,131072),StandardCharsets.US_ASCII)))throw new IOException("E5_N2_LEDGER_NOT_ORIGINAL_NO_DUPLICATE_SETTLEMENT");
        role(budget.resolve("operation.pending"),0,0);role(out.resolve(TASK+".owner"),0,0);role(out.resolve(TASK+".mp4"),0,2097152);
        host=platform.death(HOST);host.verify(HOST);codec=platform.death(CODEC);codec.verify(CODEC);
    }
    private E4Owned<E4FencedTask.LeaseGuard> lock(Path p,E5BGuard.Role role,String epoch)throws Exception {E4Owned<E4FencedTask.LeaseGuard> h=holder(p,E4FencedTask.LeaseGuard::close);platform.existingGuard(p,role,epoch,null,h);return h;}
    private boolean returned(){if(!platform.returned())return false;for(E4Owned<?> h:holders)if(!h.returned())return false;return true;}
    public Path budget(){return budget;}
    public boolean actualReturnProven(){return completed && !poisoned && returned() && !ACTIVE.contains(this);}
    public Result execute(boolean abort) {
        try{E9Phase.rejectLegacyRecovery();}catch(IOException disabled){return new Result("BLOCKED","E9_LEGACY_RECOVERY_ENTRY_DISABLED",-1,"UNKNOWN");}
        synchronized(SERIAL){
            if(used || !ACTIVE.isEmpty())return new Result("BLOCKED","E5_N2_SINGLE_OPERATION_OR_UNKNOWN_OWNER",-1,"UNKNOWN");used=true;ACTIVE.add(this);
            E4Owned<E4FencedTask.LeaseGuard> owner=null,lease=null;E4Owned<Ledger> ledger=null;long n=-1;String digest="UNKNOWN";
            try{
                stage="ORIGINAL_METADATA_AND_DEATH";originals();if(!platform.returned())throw new IOException("E5_N2_PLATFORM_OWNER_PENDING");if(!abort)return new Result("QUERY_ELIGIBLE","Exact original metadata and both death records verified; exclusive leases/FD settlement still untested",-1,"NOT_READ");
                stage="EXCLUSIVE_OWNER";owner=lock(out.resolve(TASK+".owner"),E5BGuard.Role.OWNER,null);stage="EXCLUSIVE_LEASE";lease=lock(out.resolve(TASK+".lease"),E5BGuard.Role.LEASE,LEASE);
                // Recheck under both actual original locks, not a boolean supplied by the caller.
                stage="RECHECK_UNDER_LEASES";originals();
                stage="LEDGER_LOCK";ledger=holder(budget.resolve("ledger.bin"),Ledger::close);ledger.allocate(Ledger::new);final E4Owned<Ledger> lh=ledger;
                ledger.initialize(l->{l.file=FileChannel.open(budget.resolve("ledger.bin"),StandardOpenOption.READ,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS);l.lock=l.file.tryLock();if(l.lock==null)throw new IOException("E5_N2_LEDGER_BUSY");if(l.file.size()!=ORIGINAL.length())throw new IOException("E5_N2_LEDGER_SIZE_CHANGED");byte[] b=new byte[(int)l.file.size()];E4OutputBudget.readFully(l.file,b);if(!ORIGINAL.equals(new String(b,StandardCharsets.US_ASCII)))throw new IOException("E5_N2_LEDGER_RACE");});
                // CREATE_NEW archive guards against repetition/partial recovery. Preserve original metadata verbatim.
                stage="PRESERVE_BEFORE_IMAGES";Files.createDirectory(archive);platform.sync(budget);writeNew(archive.resolve("identity.before"),originalIdentity);writeNew(archive.resolve("journal.before"),originalJournal);writeNew(archive.resolve("lease.before"),LEASE.getBytes(StandardCharsets.US_ASCII));writeNew(archive.resolve("ledger.before"),ORIGINAL.getBytes(StandardCharsets.US_ASCII));writeNew(archive.resolve("recovery.owner"),platform.recoveryOwner().bytes());writeNew(archive.resolve("guard.identity"),E5BFileId.pair(TASK,owner.original().fileId(),lease.original().fileId()));platform.sync(archive);
                stage="FENCE_AND_DURABLE_ABORT";String fence=UUID.randomUUID().toString();mutated=true;lease.original().fence(fence);persist(1,fence);persist(2,fence);
                if(!fence.equals(new String(read(out.resolve(TASK+".lease"),36,36),StandardCharsets.US_ASCII)))throw new IOException("E5_N2_FENCE_READBACK");
                DataInputStream aborted=new DataInputStream(new ByteArrayInputStream(read(out.resolve(TASK+".journal"),85,85)));
                if(aborted.readInt()!=0x45344131 || !TASK.equals(aborted.readUTF()) || aborted.readInt()!=2 || !fence.equals(aborted.readUTF()) || !aborted.readBoolean() || aborted.read()!=-1)throw new IOException("E5_N2_ABORT_READBACK");
                stage="RETAINED_OUTPUT_HASH";E4Owned<InputStream> input=holder(out.resolve(TASK+".mp4"),InputStream::close);input.allocate(()->Files.newInputStream(out.resolve(TASK+".mp4")));
                MessageDigest sha=MessageDigest.getInstance("SHA-256");n=0;
                try{byte[] b=new byte[65536];int r;while((r=input.original().read(b))!=-1){n+=r;if(n>2097152)throw new IOException("E5_N2_RETAINED_OUTPUT_BOUND");sha.update(b,0,r);}}finally{input.close();}
                if(Files.size(out.resolve(TASK+".mp4"))!=n)throw new IOException("E5_N2_OUTPUT_CHANGED");digest=hex(sha.digest());
                String payload="S "+TASK+" ABORTED "+n+" "+digest;String settlement=payload+" "+hex(MessageDigest.getInstance("SHA-256").digest((CHAIN+" "+payload).getBytes(StandardCharsets.US_ASCII)))+"\n";
                String proof="E5_N2_DEATH_FENCE_ABORT_V1\n"+host.record()+"\n"+codec.record()+"\noriginalCloseACK=false\nfence="+fence+"\n"+settlement;
                writeNew(archive.resolve("proof.txt"),proof.getBytes(StandardCharsets.US_ASCII));platform.sync(archive);
                owner.original().verifyExisting();lease.original().verifyExisting();stage="APPEND_SETTLEMENT";lh.original().file.position(lh.original().file.size());E4OutputBudget.writeFully(lh.original().file,settlement.getBytes(StandardCharsets.US_ASCII));lh.original().file.force(true);
                byte[] settled=new byte[ORIGINAL.length()+settlement.length()];lh.original().file.position(0);E4OutputBudget.readFully(lh.original().file,settled);if(lh.original().file.size()!=settled.length || !(ORIGINAL+settlement).equals(new String(settled,StandardCharsets.US_ASCII)))throw new IOException("E5_N2_SETTLEMENT_READBACK");
                stage="CLOSE_ACTUAL_RECOVERY_OWNERS";ledger.close();owner.original().verifyExisting();lease.original().verifyExisting();lease.close();owner.close();
                if(!returned())throw new IOException("E5_N2_ORIGINAL_RECOVERY_OWNER_UNRETURNED");
                // Only durable S + ABORTED + both exclusive fences + all actual closes admit marker archival.
                stage="ARCHIVE_PENDING_MARKER";Files.move(budget.resolve("operation.pending"),budget.resolve("operation.pending.N2-e5-aborted"),StandardCopyOption.ATOMIC_MOVE);platform.sync(budget);
                stage="DURABLE_COMPLETION";writeNew(budget.resolve("N2-e5-recovery.complete"),COMPLETE.getBytes(StandardCharsets.US_ASCII));platform.sync(budget);
                if(!returned())throw new IOException("E5_N2_DIRECTORY_OWNER_UNRETURNED");
                completed=true;
                return new Result("ABORTED_SETTLED","Death proof is distinct from original protocol ACK; original output retained; actual consumption appended",n,digest);
            }catch(Throwable failure){poisoned=mutated;return new Result("BLOCKED",stage+":"+E5Trace.safe(failure.getClass().getSimpleName()+":"+failure.getMessage())+"; mutated="+mutated,n,digest);}
            finally{
                for(int k=holders.size()-1;k>=0;k--){E4Owned<?> h=holders.get(k);if(h.state()==E4Owned.State.OPEN || h.state()==E4Owned.State.READY)try{h.close();}catch(Exception ignored){}}
                if(returned() && !poisoned)ACTIVE.remove(this);
                if(completed && !ACTIVE.contains(this))E5AAdmission.fromRecovery(this);
            }
        }
    }
    private void persist(int state,String fence)throws Exception {
        ByteArrayOutputStream b=new ByteArrayOutputStream();DataOutputStream d=new DataOutputStream(b);d.writeInt(0x45344131);d.writeUTF(TASK);d.writeInt(state);d.writeUTF(fence);d.writeBoolean(true);d.flush();
        Path temp=out.resolve(TASK+".e5-journal-"+state+".tmp");writeNew(temp,b.toByteArray());Files.move(temp,out.resolve(TASK+".journal"),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);platform.sync(out);
    }
    static String hex(byte[] bytes){StringBuilder b=new StringBuilder();for(byte v:bytes)b.append(String.format(Locale.ROOT,"%02x",v&255));return b.toString();}
    private static final class Ledger {FileChannel file;FileLock lock;void close()throws Exception{Exception e=null;if(lock!=null)try{lock.release();}catch(Exception x){e=x;}if(file!=null)try{file.close();}catch(Exception x){if(e==null)e=x;else e.addSuppressed(x);}if(e!=null)throw e;}}
}
