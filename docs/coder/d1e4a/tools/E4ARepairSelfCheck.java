package com.videokit.spike.e4;

import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Executes production file authority, persistent budget, original-owner and CONTROL return helpers. */
public final class E4ARepairSelfCheck {
    private static int assertions;private static final List<Object> RETAINED=new ArrayList<>();
    private static final String ID="11111111-1111-1111-1111-111111111111",BATCH="D1-E4A-owned-local-0001";
    private interface Checked {void run()throws Exception;}
    private static void check(boolean value,String why){assertions++;if(!value)throw new AssertionError(why);}
    private static IOException rejects(String code,Checked action)throws Exception{try{action.run();}catch(IOException failure){check(failure.getMessage().startsWith(code),"expected "+code+" actual "+failure);return failure;}throw new AssertionError("missing "+code);}
    private static String id(){return UUID.randomUUID().toString();}
    private static String hash(Path path)throws Exception{MessageDigest digest=MessageDigest.getInstance("SHA-256");try(InputStream in=Files.newInputStream(path)){byte[] b=new byte[65536];long total=0;int n;while((n=in.read(b))!=-1){total+=n;if(total>2097152)throw new IOException("LOCAL_FILE_BOUND");digest.update(b,0,n);}}StringBuilder text=new StringBuilder();for(byte b:digest.digest())text.append(String.format(Locale.ROOT,"%02x",b&255));return text.toString();}
    private static E4OutputBudget budget(Path path){try{return new E4OutputBudget(path,ID,id(),BATCH,p->{});}catch(IOException e){throw new AssertionError(e);}}
    private static final class Guard implements E4FencedTask.LeaseGuard {
        RandomAccessFile file;final Path path;int closes;boolean throwClose;CountDownLatch closeEntered,closeRelease;
        Guard(Path path){this.path=path;}
        public void fence(String epoch)throws IOException{file.setLength(0);file.write(epoch.getBytes(java.nio.charset.StandardCharsets.US_ASCII));file.getFD().sync();}
        public void close()throws IOException{closes++;if(closeEntered!=null){closeEntered.countDown();try{if(!closeRelease.await(2,TimeUnit.SECONDS))throw new IOException("LOCAL_BARRIER_TIMEOUT");}catch(InterruptedException e){throw new IOException(e);}}if(throwClose)throw new IOException("FAKE_CLOSE_FAILURE");if(file!=null)file.close();}
    }
    private static E4FencedTask.LeasePolicy policy(){return (path,holder)->{Guard guard=new Guard(path);holder.allocate(()->guard);holder.initialize(g->guard.file=new RandomAccessFile(path.toFile(),"rw"));};}
    private static void retainedFailureAndBudget(Path root)throws Exception{
        Path outputs=root.resolve("retained");String taskId=id();E4OutputBudget book=new E4OutputBudget(root.resolve("ledger"),ID,taskId,BATCH,p->{});book.reserve();
        E4FencedTask task=new E4FencedTask(outputs,taskId,p->{},policy());task.initialize();task.issue();byte[] partial={1,2,3,4,5,6,7};Files.write(task.authorizedOutput(),partial,StandardOpenOption.TRUNCATE_EXISTING);
        String before=hash(task.authorizedOutput());check(task.abortRetaining()==E4FencedTask.State.ABORTED,"durable abort");task.close();
        check(Files.exists(task.authorizedOutput()),"abort retained original failed output");check(Files.size(task.authorizedOutput())==7,"retained exact length");check(before.equals(hash(task.authorizedOutput())),"retained exact digest");check(task.allReturned(),"actual file/guard closes returned");
        book.finish(7,before,"ABORTED");check(book.finished(),"settled only after task close");
        check(book.originalHolders().size()==5,"marker anchor read and ledger owners explicitly registered");
        check(book.originalHolders().get(0).original() instanceof java.nio.channels.FileChannel,"original CREATE_NEW channel retained after close");
        check(book.originalHolders().stream().allMatch(E4Owned::returned),"all original metadata owners actually closed before settlement");
        long[] recovered=budget(root.resolve("ledger")).inspect();check(recovered[0]==7 && recovered[1]==0 && recovered[2]==1,"new holder sees cumulative failure consumption");
        E4OutputBudget next=budget(root.resolve("ledger"));next.reserve();long[] during=next.inspect();check(during[0]==7 && during[1]==2097152,"next reservation retains previous actual bytes");
        rejects("E4A_PRIOR_HOST_PENDING",()->budget(root.resolve("ledger")).reserve());check(Files.exists(task.authorizedOutput()),"cross-holder refusal does not delete output");RETAINED.add(next);
    }
    private static void cumulativeCannotRefund(Path root)throws Exception{
        Path directory=root.resolve("nonrefund");Path output=root.resolve("budget-owned.bin");Files.write(output,new byte[1048577]);String digest=hash(output);
        E4OutputBudget first=budget(directory);first.reserve();first.finish(Files.size(output),digest,"ABORTED");
        Path secondOutput=root.resolve("budget-owned-second.bin");Files.write(secondOutput,new byte[1048577]);E4OutputBudget second=budget(directory);second.reserve();second.finish(Files.size(secondOutput),hash(secondOutput),"ABORTED");
        // Explicit counterexample: deletion of an unrelated OWNED dummy artifact must not refund credit.
        Files.delete(secondOutput);long[] after=budget(directory).inspect();check(after[0]==2097154 && after[1]==0,"deleted dummy still consumed across new host holder");
        rejects("E4A_OUTPUT_CUMULATIVE_BUDGET",()->budget(directory).reserve());check(!Files.exists(secondOutput) && Files.exists(output),"refusal cannot be based on directory stock");
        Path unknown=root.resolve("unknown-budget");E4OutputBudget pending=budget(unknown);pending.reserve();
        rejects("E4A_PRIOR_HOST_PENDING",()->budget(unknown).reserve());check(Files.exists(unknown.resolve("operation.pending")),"pending marker survives holder loss");RETAINED.add(pending);
    }
    private static void persistenceRefuses(Path root)throws Exception{
        Path dir=root.resolve("persist-failure");E4OutputBudget broken=new E4OutputBudget(dir,ID,id(),BATCH,p->{},phase->{if(phase.equals("APPEND"))throw new IOException("FAKE_PERSIST_FAILURE");});
        rejects("FAKE_PERSIST_FAILURE",broken::reserve);check(broken.unknown(),"original persistence failure sticky");check(Files.exists(dir.resolve("operation.pending")),"unknown init remains marked");
        rejects("E4A_PRIOR_HOST_PENDING",()->budget(dir).reserve());
        Path stable=root.resolve("missing-ledger");E4OutputBudget done=budget(stable);done.reserve();Path small=root.resolve("tiny.bin");Files.write(small,new byte[]{42});done.finish(1,hash(small),"READY");Files.delete(stable.resolve("ledger.bin"));
        rejects("E4A_BUDGET_INITIALIZATION_UNKNOWN",()->budget(stable).reserve());check(Files.exists(stable.resolve("identity.anchor")),"missing ledger cannot become fresh budget");
        Path corrupt=root.resolve("torn-ledger");E4OutputBudget clean=budget(corrupt);clean.reserve();clean.finish(1,hash(small),"ABORTED");Files.write(corrupt.resolve("ledger.bin"),new byte[]{'x'},StandardOpenOption.APPEND);
        rejects("E4A_BUDGET_TORN_OR_WRONG_HEADER",()->budget(corrupt).reserve());
    }
    private static void acquireFailures(Path root)throws Exception{
        for(boolean failClose:new boolean[]{false,true}){
            Path file=root.resolve("acquire-"+failClose+".owner");Guard guard=new Guard(file);guard.throwClose=failClose;
            E4Owned<E4FencedTask.LeaseGuard> holder=new E4Owned<>(file,E4FencedTask.LeaseGuard::close);RETAINED.add(holder);
            check(holder.original()==null && holder.state()==E4Owned.State.EMPTY,"holder registered before any allocation");holder.allocate(()->guard);
            IOException init=rejects("FAKE_ACQUIRE_FAILURE",()->holder.initialize(g->{guard.file=new RandomAccessFile(file.toFile(),"rw");check(holder.original()==guard,"actual guard reachable before acquire");throw new IOException("FAKE_ACQUIRE_FAILURE");}));
            check(holder.original()==guard && guard.file!=null,"original FD owner retained");check(holder.firstFailure()==init,"original acquire exception retained");check(guard.closes==1,"one actual cleanup attempt");
            if(failClose){check(holder.state()==E4Owned.State.UNKNOWN && holder.closeFailure()!=null && init.getSuppressed().length==1,"both failures retained");rejects("E4A_ORIGINAL_CLOSE_UNPROVEN",holder::close);check(guard.closes==1,"unknown close not retried");}
            else check(holder.returned(),"successful actual close proves return despite init failure");
        }
    }
    private static void initializationHandoff(Path root)throws Exception{
        for(boolean failClose:new boolean[]{false,true}){
            AtomicReference<Guard> allocated=new AtomicReference<>();E4FencedTask task=new E4FencedTask(root.resolve("sync-"+failClose),id(),p->{throw new IOException("FAKE_DIRECTORY_SYNC");},(path,holder)->{Guard g=new Guard(path);g.throwClose=failClose;allocated.set(g);holder.allocate(()->g);holder.initialize(owner->g.file=new RandomAccessFile(path.toFile(),"rw"));});
            RETAINED.add(task);check(task.originalHolders().size()==1 && task.originalHolders().get(0).original()==null,"task owner registered before initialize");
            IOException failure=rejects("FAKE_DIRECTORY_SYNC",task::initialize);Guard original=allocated.get();check(original!=null && task.originalHolders().get(0).original()==original,"failed task still reaches original guard and FD");check(task.firstFailure()==failure,"original sync exception retained");
            if(failClose){check(!task.allReturned() && task.originalHolders().get(0).state()==E4Owned.State.UNKNOWN,"unknown guard not replaced by empty sink");check(failure.getSuppressed().length==1,"sync plus original close failure");rejects("E4A_ORIGINAL_CLOSE_UNPROVEN",task::close);check(original.closes==1,"failed init owner never retried");}
            else check(task.allReturned(),"failed sync with actual successful close returns all owners");
        }
        CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);AtomicReference<Guard> allocated=new AtomicReference<>();
        E4FencedTask task=new E4FencedTask(root.resolve("blocked-close"),id(),p->{throw new IOException("FAKE_DIRECTORY_SYNC");},(path,holder)->{Guard g=new Guard(path);g.closeEntered=entered;g.closeRelease=release;allocated.set(g);holder.allocate(()->g);holder.initialize(owner->g.file=new RandomAccessFile(path.toFile(),"rw"));});RETAINED.add(task);
        AtomicReference<Throwable> result=new AtomicReference<>();Thread thread=new Thread(()->{try{task.initialize();}catch(Throwable e){result.set(e);}},"owned-init-close-barrier");thread.start();
        try{check(entered.await(2,TimeUnit.SECONDS),"actual initializer cleanup entered");check(task.originalHolders().get(0).original()==allocated.get(),"closing original still externally reachable");check(task.originalHolders().get(0).state()==E4Owned.State.CLOSING && !task.allReturned(),"unreturned close never credited");}finally{release.countDown();}
        thread.join(2000);check(!thread.isAlive() && result.get() instanceof IOException,"original init failure returns only after close");check(task.allReturned(),"real close return changes proof");
    }
    private static void controlBarrier()throws Exception{
        E4ReturnGate gate=new E4ReturnGate();gate.admit();AtomicInteger completed=new AtomicInteger();CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);
        Thread control=new Thread(()->gate.runAdmitted(()->{entered.countDown();try{if(!release.await(2,TimeUnit.SECONDS))throw new AssertionError("barrier timeout");}catch(InterruptedException e){throw new AssertionError(e);}},()->{if(gate.claimFinish())completed.incrementAndGet();}),"actual-control-return-barrier");control.start();
        try{check(entered.await(2,TimeUnit.SECONDS),"accepted original CONTROL entered");gate.ownerReturned();check(gate.inFlight()==1 && !gate.drained(),"owner return cannot erase CONTROL");check(!gate.claimFinish() && completed.get()==0,"PENDING before actual return");}finally{release.countDown();}
        control.join(2000);check(!control.isAlive(),"original CONTROL returned");check(gate.inFlight()==0 && gate.drained() && completed.get()==1,"last actual return publishes unique completion");check(!gate.claimFinish(),"query cannot publish twice");rejects("E4A_CONTROL_AFTER_OWNER",gate::admit);
    }
    public static void main(String[] args)throws Exception{
        if(args.length==2 && args[0].equals("--restore-check")){
            Path root=Paths.get(args[1]);long[] state=budget(root.resolve("cross-process")).inspect();check(state[0]==11 && state[1]==0 && state[2]==1,"new JVM reconstructs monotonic actual consumption without static state");check(!Files.exists(root.resolve("cross-process-dummy.bin")),"restored budget independent of deleted own dummy");
            System.out.println("{\"scope\":\"E4A_REPAIR_FILES_OWNERSHIP_CONTROL_ONLY\",\"result\":\"PASS\",\"assertions\":"+assertions+",\"phase\":\"NEW_JVM_RESTORE\",\"androidCodec\":\"NOT_RUN\",\"binderIsolation\":\"NOT_RUN\"}");return;
        }
        if(args.length!=1)throw new IOException("OWNED_ROOT_REQUIRED");Path root=Paths.get(args[0]);Files.createDirectory(root);
        retainedFailureAndBudget(root);cumulativeCannotRefund(root);persistenceRefuses(root);acquireFailures(root);initializationHandoff(root);controlBarrier();
        Path cross=root.resolve("cross-process-dummy.bin");Files.write(cross,new byte[11]);E4OutputBudget durable=budget(root.resolve("cross-process"));durable.reserve();durable.finish(11,hash(cross),"ABORTED");Files.delete(cross);
        System.out.println("{\"scope\":\"E4A_REPAIR_FILES_OWNERSHIP_CONTROL_ONLY\",\"result\":\"PASS\",\"assertions\":"+assertions+",\"androidCodec\":\"NOT_RUN\",\"binderIsolation\":\"NOT_RUN\",\"realMedia\":\"NOT_READ\",\"retainedUnknownOwners\":"+RETAINED.size()+"}");
    }
}
