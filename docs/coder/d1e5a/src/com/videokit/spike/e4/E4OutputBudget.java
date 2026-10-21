package com.videokit.spike.e4;

import java.io.*;
import java.nio.channels.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** Persistent cooperative execution budget. Output deletion never changes these append-only facts. */
public final class E4OutputBudget {
    public static final long TOTAL=4194304,SINGLE=2097152;
    public static final int RECORDS=128,METADATA=131072;
    public interface Hook {void beforeSync(String phase)throws IOException;}
    private final Path directory,ledger,anchor,pending;private final String identity,task,batch;
    private final E4FencedTask.DirectorySync sync;private final Hook hook;
    private final List<E4Owned<?>> owners=new ArrayList<>();
    private boolean reserved,ownsPending;private volatile boolean finished,unknown;
    public E4OutputBudget(Path directory,String identity,String task,String batch,E4FencedTask.DirectorySync sync)throws IOException{this(directory,identity,task,batch,sync,p->{});}
    public E4OutputBudget(Path directory,String identity,String task,String batch,E4FencedTask.DirectorySync sync,Hook hook)throws IOException{
        uuid(identity);uuid(task);if(!batch.matches("D1-E4A-[A-Za-z0-9-]{8,80}"))throw new IOException("E4A_BATCH_REQUIRED");
        this.directory=directory;ledger=directory.resolve("ledger.bin");anchor=directory.resolve("identity.anchor");pending=directory.resolve("operation.pending");this.identity=identity;this.task=task;this.batch=batch;this.sync=sync;this.hook=hook;
    }
    private static void uuid(String id)throws IOException{if(id==null || !id.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))throw new IOException("E4A_BUDGET_IDENTITY_REQUIRED");}
    private <T>E4Owned<T> register(E4Owned<T> holder)throws IOException{if(owners.size()>=8)throw new IOException("E4A_BUDGET_OWNER_LIMIT");owners.add(holder);return holder;}
    private void createRegistered(Path path,byte[] bytes,String phase)throws Exception{
        E4Owned<FileChannel> holder=register(new E4Owned<>(path,FileChannel::close));
        holder.allocate(()->FileChannel.open(path,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE));
        holder.initialize(channel->{if(bytes!=null){ByteBuffer data=ByteBuffer.wrap(bytes);while(data.hasRemaining())if(channel.write(data)<=0)throw new IOException("E4A_METADATA_WRITE");}hook.beforeSync(phase);channel.force(true);});holder.close();
    }
    private void verifyAnchor()throws Exception{
        if(Files.size(anchor)!=36)throw new IOException("E4A_BUDGET_ANCHOR_MISMATCH");
        E4Owned<InputStream> holder=register(new E4Owned<>(anchor,InputStream::close));holder.allocate(()->Files.newInputStream(anchor));
        byte[] raw=new byte[36];holder.initialize(input->{new DataInputStream(input).readFully(raw);if(input.read()!=-1)throw new IOException("E4A_BUDGET_ANCHOR_GREW");});holder.close();
        if(!identity.equals(new String(raw,StandardCharsets.US_ASCII)))throw new IOException("E4A_BUDGET_ANCHOR_MISMATCH");
    }
    private static final class Handle {
        RandomAccessFile file;FileLock lock;
        void close()throws Exception{
            Exception first=null;if(lock!=null)try{lock.release();}catch(Exception e){first=e;}
            if(file!=null)try{file.close();}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}if(first!=null)throw first;
        }
    }
    private E4Owned<Handle> open()throws Exception{
        if(unknown)throw new IOException("E4A_BUDGET_UNKNOWN_NO_RETRY");
        if(Files.exists(pending) && !ownsPending)throw new IOException("E4A_PRIOR_HOST_PENDING");
        Files.createDirectories(directory);if(Files.isSymbolicLink(directory) || Files.isSymbolicLink(ledger) || Files.isSymbolicLink(anchor))throw new IOException("E4A_BUDGET_LINK");
        boolean haveAnchor=Files.exists(anchor),haveLedger=Files.exists(ledger);
        if(haveAnchor && !haveLedger || !haveAnchor && haveLedger)throw new IOException("E4A_BUDGET_INITIALIZATION_UNKNOWN");
        if(!haveAnchor){
            if(!ownsPending)throw new IOException("E4A_BUDGET_NOT_INITIALIZED");
            // CREATE_NEW marker precedes ledger creation; a partial initializer is never a fresh budget.
            createRegistered(anchor,identity.getBytes(StandardCharsets.US_ASCII),"ANCHOR");sync.sync(directory);
        }else{
            verifyAnchor();
        }
        E4Owned<Handle> holder=register(new E4Owned<>(ledger,Handle::close));holder.allocate(Handle::new);
        holder.initialize(handle->{handle.file=new RandomAccessFile(ledger.toFile(),"rw");try{handle.lock=handle.file.getChannel().tryLock();}catch(OverlappingFileLockException busy){throw new IOException("E4A_BUDGET_BUSY",busy);}if(handle.lock==null)throw new IOException("E4A_BUDGET_BUSY");});
        if(!haveAnchor){
            try{if(holder.original().file.length()!=0)throw new IOException("E4A_BUDGET_INIT_RACE");appendRaw(holder.original().file,header());sync.sync(directory);}
            catch(Exception failure){try{holder.close();}catch(Exception cleanup){failure.addSuppressed(cleanup);}throw failure;}
        }
        return holder;
    }
    private String header(){return "E4A1 "+identity+" 4194304 2097152 128\n";}
    private static String sha(byte[] data)throws Exception{StringBuilder text=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(data))text.append(String.format(Locale.ROOT,"%02x",b&255));return text.toString();}
    private static final class Entry {final String batch;Long length;String hash,state;Entry(String b){batch=b;}}
    private static final class Log {Map<String,Entry> entries=new LinkedHashMap<>();String chain;int events;long consumed,reserved;}
    private Log read(RandomAccessFile file)throws Exception{
        long size=file.length();if(size<1 || size>METADATA)throw new IOException("E4A_BUDGET_METADATA_BOUND");byte[] raw=new byte[(int)size];file.seek(0);file.readFully(raw);
        String text=new String(raw,StandardCharsets.US_ASCII);if(!text.endsWith("\n") || !text.startsWith(header()))throw new IOException("E4A_BUDGET_TORN_OR_WRONG_HEADER");
        Log log=new Log();log.chain=sha(header().getBytes(StandardCharsets.US_ASCII));
        String tail=text.substring(header().length());if(!tail.isEmpty())for(String line:tail.split("\n")){
            if(++log.events>RECORDS*2)throw new IOException("E4A_BUDGET_EVENT_LIMIT");int cut=line.lastIndexOf(' ');if(cut<0)throw new IOException("E4A_BUDGET_RECORD_INVALID");String payload=line.substring(0,cut),hash=line.substring(cut+1);
            if(!sha((log.chain+" "+payload).getBytes(StandardCharsets.US_ASCII)).equals(hash))throw new IOException("E4A_BUDGET_CHAIN_INVALID");log.chain=hash;
            String[] p=payload.split(" ");if(p.length==3 && p[0].equals("R")){
                uuid(p[1]);if(!p[2].matches("D1-E4A-[A-Za-z0-9-]{8,80}") || log.entries.size()>=RECORDS || log.entries.put(p[1],new Entry(p[2]))!=null)throw new IOException("E4A_BUDGET_RESERVATION_INVALID");
            }else if(p.length==5 && p[0].equals("S")){
                Entry entry=log.entries.get(p[1]);long bytes=Long.parseLong(p[3]);if(entry==null || entry.length!=null || bytes<0 || bytes>SINGLE || !p[4].matches("[a-f0-9]{64}") || !Set.of("READY","ABORTED").contains(p[2]))throw new IOException("E4A_BUDGET_SETTLEMENT_INVALID");entry.length=bytes;entry.hash=p[4];entry.state=p[2];
            }else throw new IOException("E4A_BUDGET_RECORD_INVALID");
        }
        for(Entry entry:log.entries.values())if(entry.length==null)log.reserved+=SINGLE;else log.consumed+=entry.length;
        if(log.consumed+log.reserved>TOTAL)throw new IOException("E4A_BUDGET_OVERDRAWN");return log;
    }
    private void appendRaw(RandomAccessFile file,String line)throws Exception{if(file.length()+line.length()>METADATA)throw new IOException("E4A_BUDGET_METADATA_BOUND");file.seek(file.length());file.write(line.getBytes(StandardCharsets.US_ASCII));hook.beforeSync("APPEND");file.getFD().sync();}
    private void append(RandomAccessFile file,Log log,String payload)throws Exception{appendRaw(file,payload+" "+sha((log.chain+" "+payload).getBytes(StandardCharsets.US_ASCII))+"\n");}
    public synchronized void reserve()throws Exception{
        if(E5N2Recovery.retainedOperations()!=0 || E5AFinalObservation.retained()!=0)throw new IOException("E5_N2_RECOVERY_OWNER_OR_DURABILITY_PENDING");
        E5AAdmission.require(directory,identity);
        Path recovered=directory.resolve("N2-e5-recovery");
        if(Files.exists(recovered,LinkOption.NOFOLLOW_LINKS)){
            Path completed=directory.resolve("N2-e5-recovery.complete"),archived=directory.resolve("operation.pending.N2-e5-aborted");
            if(!Files.isRegularFile(completed,LinkOption.NOFOLLOW_LINKS) || Files.size(completed)!=E5N2Recovery.COMPLETE.length() || !Files.isRegularFile(archived,LinkOption.NOFOLLOW_LINKS) || Files.size(archived)!=0)throw new IOException("E5_N2_RECOVERY_COMPLETION_UNPROVEN");
            E4Owned<InputStream> proof=register(new E4Owned<>(completed,InputStream::close));proof.allocate(()->Files.newInputStream(completed));byte[] raw=new byte[E5N2Recovery.COMPLETE.length()];
            try{new DataInputStream(proof.original()).readFully(raw);if(proof.original().read()!=-1 || !E5N2Recovery.COMPLETE.equals(new String(raw,StandardCharsets.US_ASCII)))throw new IOException("E5_N2_RECOVERY_COMPLETION_MISMATCH");}finally{proof.close();}
        }
        if(reserved || finished || unknown)throw new IOException("E4A_BUDGET_SINGLE_RESERVATION");E4Owned<Handle> handle=null;Exception primary=null;
        try{Files.createDirectories(directory);if(Files.exists(pending))throw new IOException("E4A_PRIOR_HOST_PENDING");createRegistered(pending,null,"PENDING");ownsPending=true;sync.sync(directory);handle=open();Log log=read(handle.original().file);if(log.reserved!=0)throw new IOException("E4A_PRIOR_RESERVATION_PENDING");if(log.entries.size()>=RECORDS || log.entries.containsKey(task) || log.consumed>TOTAL-SINGLE)throw new IOException("E4A_OUTPUT_CUMULATIVE_BUDGET");append(handle.original().file,log,"R "+task+" "+batch);}
        catch(Exception failure){primary=failure;unknown=true;throw failure;}
        finally{if(handle!=null)try{handle.close();}catch(Exception failure){unknown=true;if(primary!=null)primary.addSuppressed(failure);else throw failure;}}
        reserved=true;
    }
    /** Only original drained session can settle. A restored host never reconstructs an old ticket. */
    public synchronized void finish(long length,String hash,String state)throws Exception{
        if(!reserved || finished || unknown || length<0 || length>SINGLE || hash==null || !hash.matches("[a-f0-9]{64}") || !Set.of("READY","ABORTED").contains(state))throw new IOException("E4A_BUDGET_SETTLEMENT_REJECTED");
        E4Owned<Handle> handle=null;Exception primary=null;
        try{handle=open();Log log=read(handle.original().file);Entry entry=log.entries.get(task);if(entry==null || entry.length!=null || !entry.batch.equals(batch))throw new IOException("E4A_ORIGINAL_RESERVATION_MISMATCH");append(handle.original().file,log,"S "+task+" "+state+" "+length+" "+hash);}
        catch(Exception failure){primary=failure;unknown=true;throw failure;}
        finally{if(handle!=null)try{handle.close();}catch(Exception failure){unknown=true;if(primary!=null)primary.addSuppressed(failure);else throw failure;}}
        // Only after durable settlement AND original lock/file closes returned. No failure path unlinks it.
        try{Files.delete(pending);sync.sync(directory);ownsPending=false;finished=true;}catch(Exception failure){unknown=true;throw failure;}
    }
    public synchronized long[] inspect()throws Exception{
        E4Owned<Handle> handle=open();try{Log log=read(handle.original().file);return new long[]{log.consumed,log.reserved,log.entries.size()};}finally{handle.close();}
    }
    public boolean finished(){return finished;}
    public boolean unknown(){return unknown;}
    public List<E4Owned<?>> originalHolders(){return Collections.unmodifiableList(owners);}
}
