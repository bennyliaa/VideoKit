package com.videokit.spike.e4;

import java.io.*;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Windows-owned fixtures only. Real opened-handle volume/file IDs; never Android fstat/flock claims. */
public final class E5BGuardSelfCheck {
    static int assertions;static final int UID=E5N2Recovery.UID;
    static void ok(boolean v,String why){assertions++;if(!v)throw new AssertionError(why);}
    static final String[] VM={"-Dsun.nio.fs.ensureAccurateMetadata=true","--add-opens=java.base/sun.nio.fs=ALL-UNNAMED","--add-opens=java.base/sun.nio.ch=ALL-UNNAMED","--add-opens=java.base/java.io=ALL-UNNAMED"};
    static final class Descriptor {FileChannel channel;FileLock lock;}
    static final class IO implements E5BGuard.IO<Descriptor> {
        int existingOpens,creates,handleStats,closes;final List<Descriptor> descriptors=new ArrayList<>();
        public Descriptor allocate(){Descriptor d=new Descriptor();descriptors.add(d);return d;}
        static Object invoke(Object object,String name)throws Exception{Method m=object.getClass().getDeclaredMethod(name);m.setAccessible(true);return m.invoke(object);}
        static E5BFileId id(BasicFileAttributes a)throws Exception {
            int v=(Integer)invoke(a,"volSerialNumber"),hi=(Integer)invoke(a,"fileIndexHigh"),lo=(Integer)invoke(a,"fileIndexLow");boolean reparse=(Boolean)invoke(a,"isReparsePoint");
            int kind=reparse?E5BFileId.LINK:a.isRegularFile()?E5BFileId.REGULAR:a.isDirectory()?E5BFileId.DIRECTORY:E5BFileId.OTHER;
            return new E5BFileId(Integer.toUnsignedLong(v),(Integer.toUnsignedLong(hi)<<32)|Integer.toUnsignedLong(lo),a.size(),UID,kind);
        }
        public E5BFileId pathStatNoFollow(Path p)throws Exception{return id(Files.readAttributes(p,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS));}
        public void openExistingNoFollow(Path p,Descriptor d)throws Exception{existingOpens++;d.channel=FileChannel.open(p,StandardOpenOption.READ,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS);}
        public void createNewNoFollow(Path p,Descriptor d)throws Exception{creates++;d.channel=FileChannel.open(p,StandardOpenOption.CREATE_NEW,StandardOpenOption.READ,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS);}
        public E5BFileId handleStat(Descriptor d)throws Exception {
            handleStats++;Field f=d.channel.getClass().getDeclaredField("fd");f.setAccessible(true);FileDescriptor fd=(FileDescriptor)f.get(d.channel);Field h=FileDescriptor.class.getDeclaredField("handle");h.setAccessible(true);long handle=h.getLong(fd);
            Method read=Class.forName("sun.nio.fs.WindowsFileAttributes").getDeclaredMethod("readAttributes",long.class);read.setAccessible(true);return id((BasicFileAttributes)read.invoke(null,handle));
        }
        public byte[] readLease(Descriptor d)throws Exception{ByteBuffer b=ByteBuffer.allocate(37);while(b.hasRemaining()){int n=d.channel.read(b,b.position());if(n<=0)break;}return Arrays.copyOf(b.array(),b.position());}
        public void lock(Descriptor d)throws Exception{d.lock=d.channel.tryLock(4096,1,false);if(d.lock==null)throw new IOException("OUTPUT_WORKER_ACTIVE");}
        public void unlock(Descriptor d)throws Exception{if(d.lock!=null)d.lock.release();}
        public void close(Descriptor d)throws Exception{if(d.channel!=null){closes++;d.channel.close();}}
        public void fence(Descriptor d,byte[] bytes)throws Exception{d.channel.truncate(0);ByteBuffer b=ByteBuffer.wrap(bytes);while(b.hasRemaining())d.channel.write(b,b.position());d.channel.force(true);}
        boolean allClosed(){for(Descriptor d:descriptors)if(d.channel!=null && d.channel.isOpen())return false;return true;}
    }
    static final class Platform implements E5AFinalObservation.Platform {
        final IO io=new IO();final Path support;final boolean badCompletion;FileChannel unknown;final E5ADirectoryBarrier<FileChannel> dirs;int directoryNo;
        Platform(Path support,boolean bad)throws Exception {
            this.support=support;badCompletion=bad;Files.createDirectories(support);
            dirs=new E5ADirectoryBarrier<>(new E5ADirectoryBarrier.Operations<FileChannel>(){
                public FileChannel open(Path ignored)throws Exception{return FileChannel.open(support.resolve("dir-fd-"+(++directoryNo)),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE);}
                public void force(FileChannel c)throws Exception{c.force(true);}public void close(FileChannel c)throws Exception{c.close();}
            });
        }
        public E5N2Recovery.Death death(int pid){return new E5N2Recovery.Death(pid,UID,pid==E5N2Recovery.HOST?"com.videokit.app":"com.videokit.app:e4_codec",1792208963380L,13,0,true);}
        public E5AOwner recoveryOwner()throws Exception{return new E5AOwner(UUID.randomUUID().toString(),(int)ProcessHandle.current().pid(),UID,"com.videokit.app",System.currentTimeMillis());}
        public void existingGuard(Path p,E5BGuard.Role role,String epoch,E5BFileId expected,E4Owned<E4FencedTask.LeaseGuard> h)throws Exception{E5BGuard.existing(p,role,epoch,expected,UID,io,h);}
        public void sync(Path p)throws Exception{dirs.sync(p);}public boolean returned(){return dirs.returned();}
        public void closeMetadata(Path p,FileChannel c)throws Exception{if(badCompletion && p.getFileName().toString().equals("N2-e5-recovery.complete")){unknown=c;throw new IOException("OWNED_COMPLETION_CLOSE_UNKNOWN");}c.close();}
        public void requireRecoveryWriterDead(E5AOwner writer)throws Exception{if(ProcessHandle.of(writer.pid).map(ProcessHandle::isAlive).orElse(false))throw new IOException("OWNED_WRITER_STILL_ALIVE");}
    }
    static Path fixture(Path root)throws Exception {
        Path files=root.resolve("files"),o=files.resolve("e4a_outputs"),b=files.resolve("e4a_output_budget");Files.createDirectories(o);Files.createDirectory(b);
        try(DataOutputStream d=new DataOutputStream(Files.newOutputStream(o.resolve(E5N2Recovery.TASK+".identity"),StandardOpenOption.CREATE_NEW))){d.writeUTF("E4A_ORIGINAL_IDENTITY_V1");d.writeUTF(E5N2Recovery.BATCH);d.writeUTF(E5N2Recovery.BUDGET);d.writeUTF(E5N2Recovery.HEX);d.writeLong(E5N2Recovery.EPOCH);d.writeLong(1);d.writeUTF(E5N2Recovery.SERVICE);d.writeInt(UID);d.writeInt(UID);d.writeUTF(E5N2Recovery.TASK);}
        try(DataOutputStream d=new DataOutputStream(Files.newOutputStream(o.resolve(E5N2Recovery.TASK+".journal"),StandardOpenOption.CREATE_NEW))){d.writeInt(0x45344131);d.writeUTF(E5N2Recovery.TASK);d.writeInt(0);d.writeUTF(E5N2Recovery.LEASE);d.writeBoolean(true);}
        Files.writeString(o.resolve(E5N2Recovery.TASK+".lease"),E5N2Recovery.LEASE,StandardOpenOption.CREATE_NEW);Files.write(o.resolve(E5N2Recovery.TASK+".owner"),new byte[0],StandardOpenOption.CREATE_NEW);Files.write(o.resolve(E5N2Recovery.TASK+".mp4"),new byte[17],StandardOpenOption.CREATE_NEW);
        Files.writeString(b.resolve("identity.anchor"),E5N2Recovery.BUDGET,StandardOpenOption.CREATE_NEW);Files.writeString(b.resolve("ledger.bin"),E5N2Recovery.ORIGINAL,StandardOpenOption.CREATE_NEW);Files.write(b.resolve("operation.pending"),new byte[0],StandardOpenOption.CREATE_NEW);return files;
    }
    static String inventory(Path files)throws Exception {
        StringBuilder result=new StringBuilder();List<Path> nodes=new ArrayList<>();Files.walkFileTree(files,new java.nio.file.SimpleFileVisitor<Path>(){
            public FileVisitResult preVisitDirectory(Path p,BasicFileAttributes a){nodes.add(p);return FileVisitResult.CONTINUE;}public FileVisitResult visitFile(Path p,BasicFileAttributes a){nodes.add(p);return FileVisitResult.CONTINUE;}});nodes.sort(Comparator.comparing(Path::toString));IO io=new IO();
        for(Path p:nodes){E5BFileId id=io.pathStatNoFollow(p);result.append(files.relativize(p)).append(' ').append(id).append(' ').append(id.kind).append(' ').append(id.size);if(id.kind==E5BFileId.REGULAR)result.append(' ').append(E4Protocol.sha(Files.readAllBytes(p)));result.append('\n');}return result.toString();
    }
    static E4OutputBudget budget(Path files)throws Exception{return new E4OutputBudget(files.resolve("e4a_output_budget"),E5N2Recovery.BUDGET,UUID.randomUUID().toString(),E5N2Recovery.BATCH,p->{});}
    static void refuseReserve(Path files)throws Exception {byte[] before=Files.readAllBytes(files.resolve("e4a_output_budget/ledger.bin"));try{budget(files).reserve();throw new AssertionError("unexpected grant");}catch(IOException expected){ok(expected.getMessage().startsWith("E5A_INDEPENDENT_") || expected.getMessage().equals("E5_N2_RECOVERY_OWNER_OR_DURABILITY_PENDING"),"production reserve rejects missing live proof");}ok(Arrays.equals(before,Files.readAllBytes(files.resolve("e4a_output_budget/ledger.bin"))),"no new R/S");}
    static void child(String mode,Path root)throws Exception {
        Path files=root.resolve("files");Platform p=new Platform(root.resolve("support-"+mode),mode.equals("produce-close-unknown"));
        if(mode.startsWith("produce")){
            files=fixture(root);
            if(mode.startsWith("produce-missing")){
                Files.delete(files.resolve("e4a_outputs/"+E5N2Recovery.TASK+(mode.endsWith("owner")?".owner":".lease")));String before=inventory(files);E5N2Recovery rejected=new E5N2Recovery(files,p);E5N2Recovery.Result denied=rejected.execute(true);ok(denied.status.equals("BLOCKED") && !rejected.actualReturnProven(),"direct recovery missing original guard refused");ok(before.equals(inventory(files)) && p.io.creates==0,"recovery missing guard never created or changed original state");refuseReserve(files);System.out.println("{\"scope\":\"E5B_MISSING_RECOVERY_GUARD\",\"status\":\"PASS\",\"assertions\":"+assertions+"}");return;
            }
            E5N2Recovery op=new E5N2Recovery(files,p);E5N2Recovery.Result r=op.execute(true);ok(r.status.equals(p.badCompletion?"BLOCKED":"ABORTED_SETTLED"),"production recovery with original existing guards: "+r);ok(p.io.creates==0,"recovery never uses create guard entry");
            if(p.badCompletion){ok(p.unknown!=null && p.unknown.isOpen() && E5N2Recovery.retainedOperations()==1,"original completion close UNKNOWN retained");refuseReserve(files);}else ok(op.actualReturnProven() && p.io.allClosed(),"recovery all actual guard descriptors returned");
            System.out.println("{\"scope\":\"E5B_RECOVERY\",\"mode\":\""+mode+"\",\"status\":\""+r.status+"\",\"assertions\":"+assertions+"}");return;
        }
        String before=inventory(files);E5AFinalObservation op=new E5AFinalObservation(files,p);String observed=op.observe();boolean healthy=mode.equals("observe-healthy");
        ok(observed.startsWith(healthy?"FRESH_OBSERVATION_ADMITTED":"BLOCKED"),"direct production observation outcome: "+observed);ok(before.equals(inventory(files)),"all original paths/types/IDs/bytes unchanged");ok(p.io.creates==0,"observation no guard creation calls");ok(op.actualReturnProven()==healthy,"no live grant on rejected original resource");ok(p.io.allClosed(),"all allocated actual guard descriptors closed");
        if(healthy){ok(p.io.handleStats>0 && p.io.existingOpens==2,"actual opened-handle identity checks, two original guards");E4OutputBudget next=budget(files);next.reserve();next.finish(0,E4Protocol.sha(new byte[0]),"ABORTED");ok(next.finished(),"healthy original resources admit production reserve");}
        else {refuseReserve(files);if(mode.contains("replaced"))ok(p.io.handleStats>0,"replacement rejected against actual opened-handle ID");}
        System.out.println("{\"scope\":\"E5B_OBSERVATION\",\"mode\":\""+mode+"\",\"status\":\"PASS\",\"outcome\":\""+observed+"\",\"assertions\":"+assertions+",\"existingOpens\":"+p.io.existingOpens+",\"handleStats\":"+p.io.handleStats+",\"createCalls\":"+p.io.creates+"}");
    }
    static Process start(Path log,String mode,Path root)throws Exception {List<String> cmd=new ArrayList<>();cmd.add(Path.of(System.getProperty("java.home"),"bin/java.exe").toString());Collections.addAll(cmd,VM);cmd.addAll(List.of("-cp",System.getProperty("java.class.path"),E5BGuardSelfCheck.class.getName(),mode,root.toString()));return new ProcessBuilder(cmd).redirectErrorStream(true).redirectOutput(log.toFile()).start();}
    static void run(Path log,String mode,Path root)throws Exception {Process p=start(log,mode,root);ok(p.waitFor(15,TimeUnit.SECONDS),"own child bounded return");ok(p.exitValue()==0,"child "+mode+": "+Files.readString(log));}
    static void junction(Path link,Path target)throws Exception {Files.createDirectory(target);Process p=new ProcessBuilder("cmd.exe","/c","mklink","/J",link.toString(),target.toString()).redirectErrorStream(true).redirectOutput(link.getParent().getParent().resolve("junction-create.log").toFile()).start();if(!p.waitFor(5,TimeUnit.SECONDS) || p.exitValue()!=0)throw new IOException("OWNED_JUNCTION_UNAVAILABLE");}
    static void mutate(Path c,String mode)throws Exception {
        if(mode.startsWith("guard-record")){Path record=c.resolve("files/e4a_output_budget/N2-e5-recovery/guard.identity");if(mode.endsWith("missing")){Files.delete(record);return;}E5BFileId[] ids=E5BFileId.pair(E5N2Recovery.TASK,Files.readAllBytes(record));ids[0]=new E5BFileId(ids[0].device,ids[0].inode+1,0,UID,E5BFileId.REGULAR);Files.write(record,E5BFileId.pair(E5N2Recovery.TASK,ids[0],ids[1]));return;}
        Path o=c.resolve("files/e4a_outputs"),owner=o.resolve(E5N2Recovery.TASK+".owner"),lease=o.resolve(E5N2Recovery.TASK+".lease");Path p=mode.startsWith("owner")?owner:lease;
        if(mode.startsWith("missing")){Files.delete(mode.endsWith("owner")?owner:lease);return;}
        if(mode.endsWith("directory")){Files.delete(p);Files.createDirectory(p);return;}
        if(mode.endsWith("junction")){Files.delete(p);junction(p,c.resolve("link-target"));return;}
        if(mode.endsWith("replaced")){byte[] bytes=Files.readAllBytes(p);Files.move(p,p.resolveSibling(p.getFileName()+".original"));Files.write(p,bytes,StandardOpenOption.CREATE_NEW);return;}
        if(mode.equals("lease-fence")){Files.writeString(lease,UUID.randomUUID().toString());return;}
        int n=mode.startsWith("owner")?1:Integer.parseInt(mode.substring("lease-length-".length()));Files.write(p,new byte[n]);
    }
    static void normalTasks(Path root)throws Exception {
        Path dir=root.resolve("normal-output");Files.createDirectory(dir);IO io=new IO();E4FencedTask task=new E4FencedTask(dir,UUID.randomUUID().toString(),p->{},new E5BGuard.Policy<>(UID,io));task.initialize();task.issue();ok(task.workerLeaseClear(),"healthy live task original lease reopen");task.abortRetaining();task.close();ok(task.allReturned() && io.creates==2 && io.allClosed(),"new-task two creations are separate from later existing opens");
        Path d=root.resolve("missing-live-output");Files.createDirectory(d);IO test=new IO();E4FencedTask missing=new E4FencedTask(d,UUID.randomUUID().toString(),p->{},new E5BGuard.Policy<>(UID,test));missing.initialize();String epoch=missing.issue();Files.write(missing.authorizedOutput(),new byte[]{1,2,3});Files.delete(missing.authorizedLease());String before=inventory(d);try{missing.workerLeaseClear();throw new AssertionError("missing original lease accepted");}catch(IOException expected){ok(true,"existing lease absent refused");}try{missing.abortRetaining();throw new AssertionError("missing original lease repaired");}catch(IOException expected){ok(before.equals(inventory(d)),"abort refuses before journal mutation, never creates missing lease");}try{missing.ready(epoch,true);throw new AssertionError("missing lease READY accepted");}catch(IOException expected){ok(before.equals(inventory(d)),"READY refuses missing original lease without repairing or changing journal");}missing.close();ok(test.creates==2 && test.allClosed(),"normal missing relocks do not call creation");
    }
    static void deadline(Path root)throws Exception {
        ExecutorService owner=Executors.newSingleThreadExecutor();AtomicLong now=new AtomicLong(1000000000L);AtomicBoolean returned=new AtomicBoolean();CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);AtomicReference<E5ALifecycle<String>> ref=new AtomicReference<>();E5ALifecycle<String> life=new E5ALifecycle<>(owner,(n,r)->()->{},now::get,returned::get,()->ref.get().terminalReason(),r->{});ref.set(life);life.start();owner.execute(()->{life.cancel("ORIGINAL_FAIL");life.initialReturned(false,()->{entered.countDown();try{release.await();}catch(InterruptedException e){throw new RuntimeException(e);}},()->returned.set(true));});ok(entered.await(2,TimeUnit.SECONDS) && !life.future().isDone(),"original owner continuation not prematurely complete");long first=life.cancelAt();now.set(first+E5ALifecycle.CANCEL_NS+1);life.cancel("AGAIN");ok(life.cancelAt()==first,"absolute deadline not reset");release.countDown();ok(life.future().get(2,TimeUnit.SECONDS).equals("ORIGINAL_CANCEL_DEADLINE_PENDING"),"late timer still refuses late return qualification");owner.shutdown();ok(owner.awaitTermination(2,TimeUnit.SECONDS),"own original owner returned");
    }
    public static void main(String[] args)throws Exception {
        String mode=args[0];Path root=Path.of(args[1]);if(!mode.equals("all")){child(mode,root);return;}Files.createDirectory(root);
        String[] cases={"healthy","missing-owner","missing-lease","owner-directory","lease-directory","owner-length","lease-length-0","lease-length-35","lease-length-37","lease-fence","owner-replaced","lease-replaced","owner-junction","lease-junction","guard-record-missing","guard-record-replaced"};
        for(String c:cases){Path dir=root.resolve(c);Files.createDirectory(dir);run(dir.resolve("producer.log"),"produce",dir);if(!c.equals("healthy"))mutate(dir,c);run(dir.resolve("observation.log"),c.equals("healthy")?"observe-healthy":"observe-"+c,dir);if(c.endsWith("junction")){Path p=dir.resolve("files/e4a_outputs/"+E5N2Recovery.TASK+(c.startsWith("owner")?".owner":".lease"));Files.delete(p);}}
        for(String which:new String[]{"owner","lease"}){Path c=root.resolve("recovery-missing-"+which);Files.createDirectory(c);run(c.resolve("recovery.log"),"produce-missing-"+which,c);}
        Path late=root.resolve("close-unknown");Files.createDirectory(late);run(late.resolve("producer.log"),"produce-close-unknown",late);run(late.resolve("fresh-observation.log"),"observe-healthy",late);normalTasks(root);deadline(root);
        System.out.println("{\"scope\":\"E5B_DIRECT_PRODUCTION_GUARDS_LOCAL_ONLY\",\"status\":\"PASS_SUPPORTED_CASES\",\"assertions\":"+assertions+",\"cases\":16,\"realWindowsHandleIdentity\":true,\"trueSymbolicLink\":\"NOT_RUN_OS_PRIVILEGE_1314\",\"junctionReparseCases\":2,\"androidFstatFlock\":\"NOT_RUN\",\"deviceCalls\":0}");
    }
}
