package com.videokit.spike.e4;

import android.app.Application;
import android.content.Context;
import android.os.Bundle;
import android.os.Process;
import android.system.*;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.Test;
import java.io.*;
import java.lang.reflect.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;
import static org.junit.Assert.*;

/** One fresh app-private root; production observation LOCK boundary only, never observe()/recovery. */
public final class E5CGuardFixtureTests {
    public static final String ROOT="e5c_guard_fixture_20261017_once";
    public static final String BATCH="D1-E5C-GUARD-LINK-TABLET-20261017";
    private static final Set<Run> RETAINED=ConcurrentHashMap.newKeySet();
    private static boolean consumed;
    private static synchronized void consume(){if(consumed)throw new IllegalStateException("E5C_PROCESS_ONCE");consumed=true;}
    private static void require(boolean ok,String text)throws IOException{if(!ok)throw new IOException(text);}

    @Test public void isolatedOriginalInodeSymlinks()throws Exception {
        final long start=System.nanoTime();
        Bundle args=InstrumentationRegistry.getArguments();
        assertEquals("isolatedOriginalInodeSymlinks",args.getString("e5cCase"));
        assertEquals(BATCH,args.getString("e5cBatch"));
        assertEquals("FORMAL_DEBUG_FIXTURE_ONLY",args.getString("e5cRun"));
        Context c=InstrumentationRegistry.getInstrumentation().getTargetContext();
        assertTrue(BuildConfig.DEBUG);assertEquals("com.videokit.app",c.getPackageName());
        assertEquals("com.videokit.app",Application.getProcessName());assertEquals(E5N2Recovery.UID,Process.myUid());
        assertEquals(0,E4Session.retainedSessions());assertEquals(0,E4Session.reservedEncoderSlots());
        assertEquals(0,E5N2Recovery.retainedOperations());assertEquals(0,E5AFinalObservation.retained());
        consume();final Run run=new Run(c,start);RETAINED.add(run);
        ExecutorService worker=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"e5c-fixture-original-owner");t.setDaemon(true);return t;});
        Future<String> f=worker.submit(run::execute);worker.shutdown(); // No interrupt, cancellation, replacement closer, or timeout cleanup.
        try {
            long remaining=E5CFixtureBounds.DEADLINE_NS-(System.nanoTime()-start);
            if(remaining<=0)throw new TimeoutException();
            String result=f.get(remaining,TimeUnit.NANOSECONDS);
            if(System.nanoTime()-start>=E5CFixtureBounds.DEADLINE_NS)throw new TimeoutException();
            run.log(result);assertEquals("E5C_LOCK_BOUNDARY_PASS",result);
        }catch(TimeoutException e){
            run.hostTimedOut=true;run.log("E5C_PENDING stage="+run.stage+" actualReturn=UNKNOWN rootRetained=true noCancel=true");
            fail("E5C_PENDING method deadline; original owner and resources retained");
        }
    }

    private static final class Run {
        final Context context;final long start;final Path root;
        final List<E4Owned<?>> io=new CopyOnWriteArrayList<>();
        final List<E5AFinalObservation> observers=new CopyOnWriteArrayList<>();
        volatile String stage="NEW";volatile boolean hostTimedOut;int logBytes,events;
        Method lock;Field holders,grant;Object beforeGrant;
        Run(Context c,long s){context=c;start=s;root=c.getFilesDir().toPath().resolve(ROOT).toAbsolutePath().normalize();}
        void tick(){E5CFixtureBounds.deadline(start,System.nanoTime());}
        synchronized void log(String line)throws IOException{
            require(line.length()<=4096 && events<64,"E5C_LOG_EVENT_BOUND");
            String text=line+"\n";int n=text.getBytes(StandardCharsets.UTF_8).length;
            require(logBytes<=E5CFixtureBounds.LOG-n,"E5C_LOG_BOUND");logBytes+=n;events++;
            Bundle b=new Bundle();b.putString("stream",text);InstrumentationRegistry.getInstrumentation().sendStatus(0,b);
        }
        String execute()throws Exception {
            try {
                tick();stage="FIXED_REFLECTION_SIGNATURE";
                lock=E5AFinalObservation.class.getDeclaredMethod("lock",Path.class,E5BGuard.Role.class,String.class,E5BFileId.class);
                require(lock.getDeclaringClass()==E5AFinalObservation.class && Modifier.isPrivate(lock.getModifiers()) && lock.getReturnType()==E4Owned.class,"E5C_BOUNDARY_SIGNATURE");lock.setAccessible(true);
                holders=E5AFinalObservation.class.getDeclaredField("holders");holders.setAccessible(true);
                grant=E5AAdmission.class.getDeclaredField("grant");grant.setAccessible(true);beforeGrant=grant.get(null);require(beforeGrant==null,"E5C_PRIOR_LIVE_GRANT");
                stage="CREATE_EXCLUSIVE_ROOT";tick();Files.createDirectory(root);Os.chmod(root.toString(),0700);tick();
                log("E5C_SCOPE productionObservationLockBoundary=true metadata=ASSUMED_SYNTHETIC_NOT_EXECUTED death=ASSUMED_SYNTHETIC_NOT_EXECUTED fullObserve=NOT_RUN originalN2=NOT_RUN root="+ROOT);
                fixture("healthy",null);fixture("owner_symlink",E5BGuard.Role.OWNER);fixture("lease_symlink",E5BGuard.Role.LEASE);
                stage="FINAL_ACTUAL_RETURN";tick();require(grant.get(null)==beforeGrant,"E5C_LIVE_GRANT_CHANGED");
                for(E5AFinalObservation o:observers)require(!o.actualReturnProven(),"E5C_FULL_OBSERVATION_CLAIM");
                require(allClosed(),"E5C_ORIGINAL_CLOSE_UNKNOWN");snapshot(root);tick();
                require(!hostTimedOut,"E5C_HOST_DEADLINE_PENDING");return "E5C_LOCK_BOUNDARY_PASS";
            }catch(Throwable failure){
                // Keep this Run, original observer holders, root, and late worker reachable. Never retry UNKNOWN.
                log("E5C_BLOCKED stage="+stage+" type="+failure.getClass().getSimpleName()+" actualReturn="+(allClosed()?"CLOSED":"UNKNOWN")+" rootRetained=true");
                if(failure instanceof Exception)throw (Exception)failure;throw new RuntimeException(failure);
            }
        }
        <T>E4Owned<T> own(Object parameters,E4Owned.Action<T> closer)throws IOException{
            require(io.size()<128,"E5C_IO_HOLDER_BOUND");E4Owned<T> h=new E4Owned<>(parameters,closer);io.add(h);return h;
        }
        void write(Path p,byte[] bytes)throws Exception {
            tick();require(bytes.length<=E5CFixtureBounds.FILE,"E5C_WRITE_BOUND");
            E4Owned<FileChannel> h=own(p,FileChannel::close);
            h.allocate(()->FileChannel.open(p,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS));
            try{ByteBuffer b=ByteBuffer.wrap(bytes);while(b.hasRemaining()){tick();require(h.original().write(b)>0,"E5C_WRITE_STALLED");}h.original().force(true);}finally{h.close();}tick();
        }
        String digest(Path p,long size)throws Exception {
            require(size<=E5CFixtureBounds.FILE,"E5C_READ_BOUND");E4Owned<FileChannel> h=own(p,FileChannel::close);
            h.allocate(()->FileChannel.open(p,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS));
            try{MessageDigest md=MessageDigest.getInstance("SHA-256");ByteBuffer b=ByteBuffer.allocate(1024);long n=0;int count;
                while((count=h.original().read(b))!=-1){tick();require(count>0,"E5C_READ_STALLED");n+=count;require(n<=size,"E5C_FILE_GREW");b.flip();md.update(b);b.clear();}
                require(n==size,"E5C_FILE_SHRANK");return E5N2Recovery.hex(md.digest());
            }finally{h.close();}
        }
        Map<String,String> snapshot(Path startPath)throws Exception {
            require(startPath.startsWith(root),"E5C_PATH_ESCAPE");Map<String,String> result=new TreeMap<>();E5CFixtureBounds bound=new E5CFixtureBounds();
            Files.walkFileTree(startPath,EnumSet.noneOf(FileVisitOption.class),4,new SimpleFileVisitor<Path>(){
                private void capture(Path p)throws IOException{try{
                    tick();require(p.toAbsolutePath().normalize().startsWith(root),"E5C_PATH_ESCAPE");StructStat s=Os.lstat(p.toString());
                    boolean regular=OsConstants.S_ISREG(s.st_mode),dir=OsConstants.S_ISDIR(s.st_mode),link=OsConstants.S_ISLNK(s.st_mode);
                    require(regular||dir||link,"E5C_WRONG_NODE_ROLE");String target=link?Os.readlink(p.toString()):"";require(target.length()<=128,"E5C_LINK_BOUND");
                    bound.add(regular?s.st_size:link?target.getBytes(StandardCharsets.UTF_8).length:0);
                    String hash=regular?digest(p,s.st_size):target;
                    result.put(root.relativize(p).toString(),s.st_dev+":"+s.st_ino+":"+s.st_uid+":"+s.st_mode+":"+(regular?s.st_size:0)+":"+hash);
                }catch(Exception e){throw new IOException("E5C_SNAPSHOT",e);}}
                @Override public FileVisitResult preVisitDirectory(Path p,BasicFileAttributes a)throws IOException{capture(p);return FileVisitResult.CONTINUE;}
                @Override public FileVisitResult visitFile(Path p,BasicFileAttributes a)throws IOException{capture(p);return FileVisitResult.CONTINUE;}
                @Override public FileVisitResult visitFileFailed(Path p,IOException e)throws IOException{throw e;}
            });return result;
        }
        @SuppressWarnings("unchecked") List<E4Owned<?>> originalHolders(E5AFinalObservation o)throws Exception{return (List<E4Owned<?>>)holders.get(o);}
        boolean allClosed(){try{for(E4Owned<?> h:io)if(!h.returned())return false;for(E5AFinalObservation o:observers)for(E4Owned<?> h:originalHolders(o))if(!h.returned())return false;return true;}catch(Exception e){return false;}}
        void closeOriginal(E5AFinalObservation o)throws Exception {
            List<E4Owned<?>> list=originalHolders(o);Exception failure=null;
            for(int i=list.size()-1;i>=0;i--){E4Owned<?> h=list.get(i);
                E5BAndroidGuardIO.Descriptor d=null;FileDescriptor duplicateFd=null;
                if(h.original()!=null){Field field=E5BGuard.class.getDeclaredField("descriptor");field.setAccessible(true);d=(E5BAndroidGuardIO.Descriptor)field.get(h.original());if(d.duplicate!=null)duplicateFd=d.duplicate.getFileDescriptor();}
                if(h.state()==E4Owned.State.OPEN || h.state()==E4Owned.State.READY)try{h.close();}catch(Exception e){failure=e;}
                boolean noFd=d==null || (d.raw==null && d.duplicate==null);
                boolean fdClosed=noFd || (d.raw!=null && d.rawCloseAttempted && !d.raw.valid() && d.duplicate!=null && d.duplicateCloseAttempted && duplicateFd!=null && !duplicateFd.valid());
                log("E5C_ACTUAL_FD allocation="+(noFd?"NONE_PREOPEN_REJECTION":"RAW_AND_DUP")+" close="+(fdClosed?"CLOSED":"UNKNOWN"));
                if(!fdClosed && failure==null)failure=new IOException("E5C_ACTUAL_FD_CLOSE_UNKNOWN");
                log("E5C_GUARD_CLOSE parameter="+((Path)h.parameters).getFileName()+" state="+h.state()+" returned="+h.returned());
                if(!h.returned() && failure==null)failure=new IOException("E5C_GUARD_CLOSE_UNKNOWN");
            }if(failure!=null)throw failure;
        }
        void invoke(E5AFinalObservation o,Path p,E5BGuard.Role role,String epoch,E5BFileId id)throws Throwable{
            tick();try{lock.invoke(o,p,role,epoch,id);}catch(InvocationTargetException e){throw e.getCause();}tick();
        }
        void linkOriginal(Path source,E5BFileId expected)throws Exception {
            Path target=source.resolveSibling(source.getFileName()+".original-target");String oldHash=digest(source,expected.size);
            Files.move(source,target);Os.symlink(target.getFileName().toString(),source.toString());tick();
            StructStat l=Os.lstat(source.toString()),follow=Os.stat(source.toString()),t=Os.lstat(target.toString());
            require(OsConstants.S_ISLNK(l.st_mode) && Os.readlink(source.toString()).equals(target.getFileName().toString()),"E5C_REAL_SYMLINK_UNPROVEN");
            require(OsConstants.S_ISREG(t.st_mode) && expected.device==t.st_dev && expected.inode==t.st_ino && expected.uid==t.st_uid && expected.size==t.st_size && follow.st_dev==t.st_dev && follow.st_ino==t.st_ino,"E5C_ORIGINAL_INODE_CHANGED");
            require(oldHash.equals(digest(target,t.st_size)),"E5C_ORIGINAL_BYTES_CHANGED");
            log("E5C_TRUE_SYMLINK path="+source.getFileName()+" readlink="+Os.readlink(source.toString())+" kind=S_IFLNK originalDev="+t.st_dev+" originalInode="+t.st_ino+" bytes="+t.st_size+" sha256="+oldHash);
        }
        void noFollowProbe(Path link)throws Exception {
            E5BAndroidGuardIO actual=new E5BAndroidGuardIO();E4Owned<E5BAndroidGuardIO.Descriptor> h=own(link,actual::close);
            h.allocate(actual::allocate);boolean eloop=false;
            try{h.initialize(d->actual.openExistingNoFollow(link,d));}catch(ErrnoException e){require(e.errno==OsConstants.ELOOP,"E5C_UNEXPECTED_OPEN_ERRNO");eloop=true;}
            finally{if(h.state()==E4Owned.State.OPEN || h.state()==E4Owned.State.READY)h.close();}
            require(eloop && h.returned(),"E5C_NOFOLLOW_ELOOP_OR_CLOSE_UNPROVEN");log("E5C_RAW_NOFOLLOW errno=ELOOP actualClose="+h.state());
        }
        void fixture(String name,E5BGuard.Role bad)throws Exception {
            stage=name;tick();Path dir=root.resolve(name);Files.createDirectory(dir);String task=UUID.randomUUID().toString(),epoch=UUID.randomUUID().toString();
            Path owner=dir.resolve(task+".owner"),lease=dir.resolve(task+".lease");
            write(owner,new byte[0]);write(lease,epoch.getBytes(StandardCharsets.US_ASCII));
            write(dir.resolve("own-identity.txt"),("E5C_SYNTHETIC_IDENTITY "+task+"\n").getBytes(StandardCharsets.US_ASCII));
            write(dir.resolve("own-ledger.txt"),("E5C_SYNTHETIC_LEDGER_V1 "+UUID.randomUUID()+" R_count=0 S_count=0\n").getBytes(StandardCharsets.US_ASCII));
            write(dir.resolve("own-payload.bin"),"e5c-own-bytes-only".getBytes(StandardCharsets.US_ASCII));
            E5BAndroidGuardIO actual=new E5BAndroidGuardIO();E5BFileId ownerId=actual.pathStatNoFollow(owner),leaseId=actual.pathStatNoFollow(lease);
            if(bad!=null)linkOriginal(bad==E5BGuard.Role.OWNER?owner:lease,bad==E5BGuard.Role.OWNER?ownerId:leaseId);
            Map<String,String> before=snapshot(dir);
            if(bad!=null)noFollowProbe(bad==E5BGuard.Role.OWNER?owner:lease);
            E5N2RecoveryAndroid adapter=new E5N2RecoveryAndroid(context);
            E5AFinalObservation.Platform limited=new E5AFinalObservation.Platform(){
                public void existingGuard(Path p,E5BGuard.Role role,String fence,E5BFileId expected,E4Owned<E4FencedTask.LeaseGuard> holder)throws Exception{
                    require((p.equals(owner)&&role==E5BGuard.Role.OWNER&&fence==null&&expected==ownerId)||(p.equals(lease)&&role==E5BGuard.Role.LEASE&&epoch.equals(fence)&&expected==leaseId),"E5C_ONLY_OWN_GUARDS");
                    adapter.existingGuard(p,role,fence,expected,holder);
                }
                public E5N2Recovery.Death death(int pid)throws Exception{throw new IOException("E5C_DEATH_DISABLED");}
                public void requireRecoveryWriterDead(E5AOwner w)throws Exception{throw new IOException("E5C_WRITER_DEATH_DISABLED");}
                public E5AOwner recoveryOwner()throws Exception{throw new IOException("E5C_RECOVERY_DISABLED");}
                public void sync(Path p)throws Exception{throw new IOException("E5C_SYNC_DISABLED");}
                public void forceMetadata(Path p,FileChannel f)throws Exception{throw new IOException("E5C_METADATA_DISABLED");}
                public void closeMetadata(Path p,FileChannel f)throws Exception{throw new IOException("E5C_METADATA_DISABLED");}
                public boolean returned(){return adapter.returned();}
            };
            E5AFinalObservation observation=new E5AFinalObservation(dir,limited);observers.add(observation);Throwable rejected=null;
            try{invoke(observation,owner,E5BGuard.Role.OWNER,null,ownerId);invoke(observation,lease,E5BGuard.Role.LEASE,epoch,leaseId);}
            catch(Throwable e){rejected=e;}finally{closeOriginal(observation);}
            if(bad==null)require(rejected==null,"E5C_HEALTHY_LOCK_FAILED");
            else {require(originalHolders(observation).size()==(bad==E5BGuard.Role.OWNER?1:2),"E5C_REJECTION_STAGE");require(rejected instanceof IOException && "E5B_EXISTING_GUARD_ROLE_LENGTH_UID".equals(rejected.getMessage()),"E5C_EXPECTED_LINK_ROLE_REJECTION");}
            require(before.equals(snapshot(dir)),"E5C_FIXTURE_CHANGED_DURING_BOUNDARY");require(grant.get(null)==beforeGrant,"E5C_GRANT_CHANGED");tick();
            log("E5C_CASE "+name+" result="+(bad==null?"HEALTHY_TWO_LOCKS_CLOSED":"TRUE_SYMLINK_REJECTED")+" metadataBytes=UNCHANGED R_count=0 S_count=0 liveGrant=false actualReturn=CLOSED fullObserve=NOT_RUN");
        }
    }
}
