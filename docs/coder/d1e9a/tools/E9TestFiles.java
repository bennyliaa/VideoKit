package com.videokit.spike.e4;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.concurrent.*;

/** Test-only platform substitution: real JVM files/locks; Android UID/dev-inode and directory fsync are shims. */
final class E9TestFiles implements E9CurrentObservation.Platform {
    interface Cut {void at(String op,String path)throws Exception;}
    static final class H extends E9OwnedFiles.Handle {FileChannel file;FileLock lock;DirectoryStream<Path> stream;boolean borrowed;H(Path p,E9OwnedFiles.Mode m){super(p,m);}}
    static final class G {Path path;FileChannel file;FileLock lock;}
    final Path root;Cut cut=(a,b)->{};final List<String> trace=new ArrayList<>();final List<H> nativeHandles=new ArrayList<>();final List<G> nativeGuards=new ArrayList<>();
    int opens,closes,writes,forces,syncs,locks,unlocks,guardCreates,readCalls;boolean idle=true,linkRole;String inodeChanged="";
    E9TestFiles(Path root){this.root=root.toAbsolutePath().normalize();}
    private String rel(Path p){return root.relativize(p.toAbsolutePath().normalize()).toString().replace('\\','/');}
    private synchronized void hit(String op,Path p)throws Exception{String path=rel(p);trace.add(op+":"+path);cut.at(op,path);}
    public void requireIdleOriginalHost()throws Exception{if(!idle)throw new IOException("TEST_CURRENT_HOST_NOT_IDLE");}
    public E9OwnedFiles.Handle allocate(Path p,E9OwnedFiles.Mode mode){H h=new H(p,mode);nativeHandles.add(h);return h;}
    public E5BFileId pathStat(Path p)throws Exception{
        hit("STAT",p);BasicFileAttributes a=Files.readAttributes(p,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);String name=rel(p);long inode=name.endsWith(E5N2Recovery.TASK+".owner")?20304:name.endsWith(E5N2Recovery.TASK+".lease")?20385:Math.abs((long)name.hashCode())+40000;
        if(name.equals(inodeChanged))inode++;int kind=a.isDirectory()?E5BFileId.DIRECTORY:a.isRegularFile()?E5BFileId.REGULAR:E5BFileId.LINK;if(linkRole&&!a.isDirectory())kind=E5BFileId.LINK;
        return new E5BFileId(64522,inode,a.isDirectory()?0:a.size(),10221,kind);
    }
    public E5BFileId handleStat(E9OwnedFiles.Handle handle)throws Exception{H h=(H)handle;if(h.file!=null&&!h.file.isOpen())throw new IOException("TEST_NATIVE_CLOSED");return pathStat(h.path);}
    public boolean exists(Path p)throws Exception{hit("EXISTS",p);return Files.exists(p,LinkOption.NOFOLLOW_LINKS);}
    public void directory(Path p)throws Exception{E5BFileId id=pathStat(p);if(id.kind!=E5BFileId.DIRECTORY)throw new IOException("TEST_DIRECTORY_ROLE");}
    public void mkdirNew(Path p)throws Exception{hit("MKDIR",p);Files.createDirectory(p);}
    public void open(E9OwnedFiles.Handle handle)throws Exception{
        H h=(H)handle;hit("OPEN_BEFORE",h.path);
        if(h.mode==E9OwnedFiles.Mode.DIRECTORY){h.openReturned=true;opens++;hit("OPEN_AFTER",h.path);return;}
        if(h.mode==E9OwnedFiles.Mode.LIST){h.stream=Files.newDirectoryStream(h.path);h.openReturned=true;opens++;hit("OPEN_AFTER",h.path);return;}
        for(G g:nativeGuards)if(h.path.equals(g.path)&&g.file!=null&&g.file.isOpen()){h.file=g.file;h.borrowed=true;h.openReturned=true;opens++;hit("OPEN_AFTER",h.path);return;}
        h.file=h.mode==E9OwnedFiles.Mode.CREATE?FileChannel.open(h.path,StandardOpenOption.CREATE_NEW,StandardOpenOption.READ,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS):FileChannel.open(h.path,StandardOpenOption.READ,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS);h.openReturned=true;opens++;hit("OPEN_AFTER",h.path);
        if(h.mode==E9OwnedFiles.Mode.LEDGER){hit("LEDGER_LOCK",h.path);h.lock=h.file.tryLock();if(h.lock==null)throw new IOException("TEST_LEDGER_BUSY");}
    }
    public byte[] read(E9OwnedFiles.Handle handle,int max)throws Exception{H h=(H)handle;hit("READ",h.path);readCalls++;byte[] raw=new byte[max+1];ByteBuffer b=ByteBuffer.wrap(raw);h.file.position(0);while(b.hasRemaining()){int n=h.file.read(b);if(n<0)break;if(n==0)throw new IOException("TEST_NO_READ_PROGRESS");}int n=b.position();if(n>max)throw new IOException("TEST_READ_BOUND");return Arrays.copyOf(raw,n);}
    public void write(E9OwnedFiles.Handle handle,byte[] data)throws Exception{H h=(H)handle;if(h.mode!=E9OwnedFiles.Mode.CREATE)throw new IOException("TEST_NO_LEGACY_WRITES");hit("WRITE",h.path);ByteBuffer b=ByteBuffer.wrap(data);while(b.hasRemaining())if(h.file.write(b)<=0)throw new IOException("TEST_WRITE_PROGRESS");writes++;}
    public void force(E9OwnedFiles.Handle handle)throws Exception{H h=(H)handle;hit(h.mode==E9OwnedFiles.Mode.DIRECTORY?"DIR_SYNC":"FORCE",h.path);if(h.file!=null)h.file.force(true);if(h.mode==E9OwnedFiles.Mode.DIRECTORY)syncs++;else forces++;}
    public List<String> entries(E9OwnedFiles.Handle handle,int max)throws Exception{H h=(H)handle;hit("LIST",h.path);List<String> n=new ArrayList<>();for(Path p:h.stream){if(n.size()>=max)throw new IOException("TEST_LIST_BOUND");n.add(p.getFileName().toString());}return n;}
    public void close(E9OwnedFiles.Handle handle)throws Exception{H h=(H)handle;hit("CLOSE_BEFORE",h.path);if(h.lock!=null&&h.lock.isValid())h.lock.release();if(h.stream!=null)h.stream.close();if(h.file!=null&&!h.borrowed)h.file.close();closes++;hit("CLOSE_AFTER",h.path);}
    public void existingGuard(Path path,E5BGuard.Role role,String fence,E5BFileId expected,E4Owned<E4FencedTask.LeaseGuard> holder)throws Exception{
        E5BGuard.existing(path,role,fence,expected,10221,new E5BGuard.IO<G>(){
            public G allocate(){G g=new G();nativeGuards.add(g);return g;}
            public E5BFileId pathStatNoFollow(Path p)throws Exception{return pathStat(p);}
            public void openExistingNoFollow(Path p,G g)throws Exception{g.path=p;hit("GUARD_OPEN",p);g.file=FileChannel.open(p,StandardOpenOption.READ,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS);}
            public void createNewNoFollow(Path p,G g)throws Exception{guardCreates++;throw new IOException("TEST_NEW_GUARD_FORBIDDEN");}
            public E5BFileId handleStat(G g)throws Exception{if(g.file==null||!g.file.isOpen())throw new IOException("TEST_GUARD_NOT_OPEN");return pathStat(g.path);}
            public byte[] readLease(G g)throws Exception{byte[] b=new byte[37];ByteBuffer buf=ByteBuffer.wrap(b);g.file.position(0);while(buf.hasRemaining()){int n=g.file.read(buf);if(n<0)break;if(n==0)throw new IOException("TEST_NO_PROGRESS");}return Arrays.copyOf(b,buf.position());}
            public void lock(G g)throws Exception{hit("GUARD_LOCK",g.path);g.lock=g.file.tryLock();if(g.lock==null)throw new IOException("TEST_GUARD_BUSY");locks++;}
            public void unlock(G g)throws Exception{hit("GUARD_UNLOCK_BEFORE",g.path);g.lock.release();unlocks++;hit("GUARD_UNLOCK_AFTER",g.path);}
            public void fence(G g,byte[] bytes)throws Exception{throw new IOException("TEST_OLD_FENCE_MUTATION_FORBIDDEN");}
            public void close(G g)throws Exception{hit("GUARD_CLOSE_BEFORE",g.path);if(g.file!=null)g.file.close();hit("GUARD_CLOSE_AFTER",g.path);}
        },holder);
    }
    /** Harness-only native teardown after all assertions; NEVER changes a production holder or supplies its ACK. */
    void closeNativeFacsimilesAfterAssertions(){for(H h:nativeHandles){try{if(h.stream!=null)h.stream.close();}catch(Exception ignored){}try{if(h.file!=null)h.file.close();}catch(Exception ignored){}}for(G g:nativeGuards)try{if(g.file!=null)g.file.close();}catch(Exception ignored){}}
    static void fixture(Path root,Path reference)throws Exception{
        Map<String,byte[]> old=hex(Files.readString(reference.resolve("03-post-abort-private-stdout.txt")));Map<String,byte[]> recent=hex(Files.readString(reference.resolve("normalMp4SixRealFrames-post-state-stdout.txt")));
        for(String rel:E9LegacyProfile.IMMUTABLE.keySet()){byte[] bytes=old.get("files/"+rel);if(bytes==null||!E9Record.sha(bytes).equals(E9LegacyProfile.IMMUTABLE.get(rel)))throw new IOException("TEST_REFERENCE_METADATA");put(root.resolve(rel),bytes);}
        put(root.resolve("e4a_output_budget/ledger.bin"),recent.get("files/e4a_output_budget/ledger.bin"));put(root.resolve("e4a_outputs/"+E5N2Recovery.TASK+".mp4"),new byte[0]);put(root.resolve("e4a_outputs/"+E5N2Recovery.TASK+".owner"),new byte[0]);
    }
    static Map<String,byte[]> hex(String text)throws Exception{Map<String,byte[]> result=new HashMap<>();java.util.regex.Matcher m=java.util.regex.Pattern.compile("HEX_BEGIN[|]([^\\r\\n]+)\\r?\\n(.*?)HEX_END",java.util.regex.Pattern.DOTALL).matcher(text);while(m.find()){String value=m.group(2).replaceAll("\\s","");if(value.length()%2!=0)throw new IOException("TEST_HEX");byte[] raw=new byte[value.length()/2];for(int i=0;i<raw.length;i++)raw[i]=(byte)Integer.parseInt(value.substring(i*2,i*2+2),16);result.put(m.group(1),raw);}return result;}
    static void put(Path p,byte[] bytes)throws Exception{if(bytes==null)throw new IOException("TEST_MISSING_REFERENCE");Files.createDirectories(p.getParent());Files.write(p,bytes,StandardOpenOption.CREATE_NEW);}
    static String uuid(String name){return UUID.nameUUIDFromBytes(("SYNTHETIC_E9_"+name).getBytes(StandardCharsets.US_ASCII)).toString();}
    static String digest(String name){return E9Record.sha(("SYNTHETIC_NOT_AN_APPROVAL_"+name).getBytes(StandardCharsets.US_ASCII));}
    static final class Clock implements E9MigrationRun.Clock {volatile long now;public long now(){return now;}}
    static final class Identity implements E9MigrationTransaction.IdentitySource {
        final E9Actor actor;final E4Owned<FileChannel> owned;final Path path;String recovery="NONE";boolean done;Throwable fail;Identity(E9Actor a,Path path){actor=a;this.path=path;owned=new E4Owned<>(path,FileChannel::close);}
        public E9Actor sample()throws Exception{try{owned.allocate(()->FileChannel.open(path,StandardOpenOption.READ));ByteBuffer bytes=ByteBuffer.allocate(2048);while(owned.original().read(bytes)>0){}byte[] raw=Arrays.copyOf(bytes.array(),bytes.position());E9Actor actual=new E9Actor(E9Record.parse(raw,2048));if(!actual.hash().equals(actor.hash()))throw new IOException("TEST_IDENTITY_INPUT");if(fail!=null){if(fail instanceof Exception)throw (Exception)fail;throw (Error)fail;}return actor;}finally{if(owned.state()==E4Owned.State.OPEN)owned.close();done=true;}}
        public boolean returned(){return done&&owned.returned();}public int owned(){return 1;}public String recoveryDigest(){return recovery;}
    }
}
