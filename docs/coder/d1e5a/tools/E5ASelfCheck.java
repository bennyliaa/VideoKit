package com.videokit.spike.e4;

import java.io.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Direct production recovery/admission/lifecycle paths with owned files and real JVM processes/threads. */
public final class E5ASelfCheck {
    static int assertions;
    static void ok(boolean b,String why){assertions++;if(!b)throw new AssertionError(why);}
    static void waitFile(Path p)throws Exception {long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(10);while(!Files.exists(p)){if(System.nanoTime()>end)throw new IOException("TEST_COORDINATION_TIMEOUT");Thread.sleep(5);}}
    static final class Platform extends E5SelfCheck.Model implements E5AFinalObservation.Platform {
        final Path root;final String mode;final E5ADirectoryBarrier<FileChannel> dirs;final Map<FileChannel,Integer> numbers=new IdentityHashMap<>();int opens;
        Platform(Path root,String mode)throws Exception {
            this.root=root;this.mode=mode;Path descriptors=root.resolve("test-descriptors-"+UUID.randomUUID());Files.createDirectory(descriptors);
            dirs=new E5ADirectoryBarrier<>(new E5ADirectoryBarrier.Operations<FileChannel>(){
                public FileChannel open(Path ignored)throws Exception{int n=++opens;FileChannel c=FileChannel.open(descriptors.resolve("fd-"+n),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE);numbers.put(c,n);return c;}
                public void force(FileChannel c)throws Exception{if(numbers.get(c)==7){if(mode.equals("dir-force"))throw new IOException("INJECTED_LAST_DIR_FORCE");if(mode.equals("dir-force-held"))hold(c);}c.force(true);}
                public void close(FileChannel c)throws Exception{if(numbers.get(c)==7){if(mode.equals("dir-close"))throw new IOException("INJECTED_LAST_DIR_CLOSE");if(mode.equals("dir-close-held"))hold(c);}c.close();}
            });
        }
        void hold(FileChannel channel)throws Exception {if(!channel.isOpen() || E5N2Recovery.retainedOperations()!=1)throw new AssertionError("original pending descriptor must be reachable and open");Files.writeString(root.resolve("fault-entered"),"originalDescriptorOpen="+channel.isOpen()+" activeRecovery="+E5N2Recovery.retainedOperations(),StandardOpenOption.CREATE_NEW);waitFile(root.resolve("release-original-call"));}
        public void sync(Path p)throws Exception {dirs.sync(p);}
        public boolean returned(){return dirs.returned();}
        public void forceMetadata(Path p,FileChannel c)throws Exception {
            if(p.getFileName().toString().equals("N2-e5-recovery.complete") && mode.equals("completion-force"))throw new IOException("INJECTED_COMPLETION_FORCE_AFTER_CONTENT_VISIBLE");c.force(true);
        }
        public void closeMetadata(Path p,FileChannel c)throws Exception {
            if(p.getFileName().toString().equals("N2-e5-recovery.complete")){if(mode.equals("completion-close"))throw new IOException("INJECTED_COMPLETION_CLOSE");if(mode.equals("completion-close-held"))hold(c);}c.close();
        }
        public void requireRecoveryWriterDead(E5AOwner writer)throws Exception {
            if(writer.pid==(int)ProcessHandle.current().pid() || ProcessHandle.of(writer.pid).map(ProcessHandle::isAlive).orElse(false))throw new IOException("ACTUAL_LOCAL_WRITER_PROCESS_STILL_ALIVE");
            // Local ProcessHandle is actual local death evidence, not Android ApplicationExitInfo or an old close ACK.
        }
    }
    static E4OutputBudget budget(Path files)throws Exception{return new E4OutputBudget(files.resolve("e4a_output_budget"),E5N2Recovery.BUDGET,UUID.randomUUID().toString(),E5N2Recovery.BATCH,p->{});}
    static void writer(Path root,String mode)throws Exception {
        Path files=E5SelfCheck.fixture(root,"case",17);Platform p=new Platform(files,mode);E5N2Recovery op=new E5N2Recovery(files,p);E5N2Recovery.Result r=op.execute(true);
        ok(Files.readString(files.resolve("e4a_output_budget/N2-e5-recovery.complete")).equals(E5N2Recovery.COMPLETE),"complete bytes genuinely visible at late fault");
        boolean success=mode.equals("healthy") || mode.endsWith("-held");ok(r.status.equals(success?"ABORTED_SETTLED":"BLOCKED"),"late fault actual result "+r);
        ok(op.actualReturnProven()==success,"grant only after actual final force/close/sync returns");
        if(success){E4OutputBudget next=budget(files);next.reserve();next.finish(0,E4Protocol.sha(new byte[0]),"ABORTED");ok(next.finished(),"fully returned same-process production reserve admitted");}
        else{ok(E5N2Recovery.retainedOperations()==1,"late failure retains original operation");try{budget(files).reserve();throw new AssertionError("same-host late failure admitted");}catch(IOException expected){ok(expected.getMessage().equals("E5_N2_RECOVERY_OWNER_OR_DURABILITY_PENDING"),"same-host original pending operation refused");}}
        System.out.println("{\"scope\":\"E5A_LATE_WRITER\",\"mode\":\""+mode+"\",\"result\":\""+r.status+"\",\"assertions\":"+assertions+",\"retainedOriginalOperations\":"+E5N2Recovery.retainedOperations()+"}");
    }
    static void newHost(Path files,boolean observe,boolean expectLive)throws Exception {
        byte[] before=Files.readAllBytes(files.resolve("e4a_output_budget/ledger.bin"));
        if(observe){Platform p=new Platform(files,"fresh-observer");String result=new E5AFinalObservation(files,p).observe();
            if(expectLive){ok(result.startsWith("BLOCKED WRITER_DEATH"),"independent observation refuses actually living recovery writer: "+result);}
            else{ok(result.startsWith("FRESH_OBSERVATION_ADMITTED"),"explicit fresh observation after actual writer death: "+result);E4OutputBudget b=budget(files);b.reserve();b.finish(0,E4Protocol.sha(new byte[0]),"ABORTED");ok(b.finished(),"production reserve only after fresh actual observer returned");}
        }else{try{budget(files).reserve();throw new AssertionError("new host accepted visible completion");}catch(IOException expected){ok(expected.getMessage().equals("E5A_INDEPENDENT_FINAL_OBSERVATION_REQUIRED"),"new-host completion never self-proves");}ok(Arrays.equals(before,Files.readAllBytes(files.resolve("e4a_output_budget/ledger.bin"))),"new host refused before appending any new R");}
        System.out.println("{\"scope\":\"E5A_NEW_HOST\",\"observe\":"+observe+",\"expectedLive\":"+expectLive+",\"assertions\":"+assertions+",\"status\":\"PASS\"}");
    }
    static Process child(Path log,String... args)throws Exception {
        List<String> cmd=new ArrayList<>();cmd.add(Path.of(System.getProperty("java.home"),"bin","java.exe").toString());cmd.add("-cp");cmd.add(System.getProperty("java.class.path"));cmd.add(E5ASelfCheck.class.getName());Collections.addAll(cmd,args);return new ProcessBuilder(cmd).redirectErrorStream(true).redirectOutput(log.toFile()).start();
    }
    static void ended(Process p,Path log)throws Exception {ok(p.waitFor(15,TimeUnit.SECONDS),"bounded owned JVM returned "+log);ok(p.exitValue()==0,"owned JVM check failed "+Files.readString(log));}
    static void lateCases(Path root)throws Exception {
        for(String mode:new String[]{"healthy","completion-force","completion-close","completion-close-held","dir-force","dir-force-held","dir-close","dir-close-held"}){
            Path c=root.resolve(mode);Files.createDirectory(c);Path log=c.resolve("writer.log");Process writer=child(log,"writer",c.toString(),mode);Path files=c.resolve("case");
            if(mode.endsWith("-held")){
                waitFile(files.resolve("fault-entered"));ok(writer.isAlive(),"original force/close still actually unreturned");ok(Files.readString(files.resolve("fault-entered")).equals("originalDescriptorOpen=true activeRecovery=1"),"actual original descriptor and operation remain strongly reachable while unreturned");
                Path denied=c.resolve("new-host-while-held.log");ended(child(denied,"reserve",files.toString()),denied);
                Path alive=c.resolve("observer-while-held.log");ended(child(alive,"observe-live",files.toString()),alive);
                Files.write(files.resolve("release-original-call"),new byte[0],StandardOpenOption.CREATE_NEW);
            }
            ended(writer,log);Path denied=c.resolve("new-host-after-exit.log");ended(child(denied,"reserve",files.toString()),denied);
            if(mode.equals("healthy")){
                Path lost=c.resolve("no-recovery-markers");Files.createDirectories(lost.resolve("e4a_output_budget"));for(String name:new String[]{"ledger.bin","identity.anchor"})Files.copy(files.resolve("e4a_output_budget").resolve(name),lost.resolve("e4a_output_budget").resolve(name));Path cold=c.resolve("new-host-without-markers.log");ended(child(cold,"reserve",lost.toString()),cold);
            }
            Path fresh=c.resolve("fresh-observation.log");ended(child(fresh,"observe-dead",files.toString()),fresh);
            ok(Files.size(files.resolve("e4a_outputs/"+E5N2Recovery.TASK+".mp4"))==17,"actual retained output unchanged across independent observation");
            String ledger=Files.readString(files.resolve("e4a_output_budget/ledger.bin"));ok(ledger.split("S "+E5N2Recovery.TASK+" ABORTED ",-1).length==2,"one original settlement, no repeated S");
        }
    }
    static final class Clock implements E5ALifecycle.Scheduler {
        final AtomicLong now=new AtomicLong(1000000000L);final List<Job> jobs=new ArrayList<>();
        static final class Job{long at;Runnable call;boolean cancelled;Job(long t,Runnable r){at=t;call=r;}}
        public synchronized E5ALifecycle.Ticket after(long n,Runnable r){Job j=new Job(now.get()+n,r);jobs.add(j);return ()->{synchronized(Clock.this){j.cancelled=true;}};}
        void advance(long time){now.set(time);for(int n=0;n<100;n++){Job due=null;synchronized(this){for(Job j:jobs)if(!j.cancelled && j.at<=time && (due==null || j.at<due.at))due=j;if(due!=null)due.cancelled=true;}if(due==null)return;due.call.run();}throw new AssertionError("timer schedule was not bounded");}
    }
    static final class Outcome {final String status,error,reason;final boolean released;Outcome(String s,String e,String r,boolean b){status=s;error=e;reason=r;released=b;}}
    static void lifecycle(Path root,String mode)throws Exception {
        Path c=root.resolve(mode);Files.createDirectory(c);Clock clock=new Clock();ThreadPoolExecutor owner=new ThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(2),r->new Thread(r,"original-owner-"+mode));
        CountDownLatch closeEntered=new CountDownLatch(1),releaseClose=new CountDownLatch(mode.equals("control")?0:1),finalReturned=new CountDownLatch(1),controlEntered=new CountDownLatch(1),releaseControl=new CountDownLatch(1);
        E4Owned<FileChannel> resource=new E4Owned<>(c.resolve("retained.bin"),f->{closeEntered.countDown();releaseClose.await();f.close();});resource.allocate(()->FileChannel.open(c.resolve("retained.bin"),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE));resource.original().write(ByteBuffer.wrap(new byte[]{1,2,3}));resource.original().force(true);
        E4OutputBudget b=new E4OutputBudget(c.resolve("budget"),UUID.randomUUID().toString(),UUID.randomUUID().toString(),"D1-E4A-E5A-LIFECYCLE-20261017",p->{});b.reserve();E4ReturnGate control=new E4ReturnGate();AtomicBoolean ownerDone=new AtomicBoolean();AtomicInteger settlements=new AtomicInteger();AtomicReference<Thread> firstThread=new AtomicReference<>(),lastThread=new AtomicReference<>();String first="E4_REMOTE_PENDING";
        AtomicReference<E5ALifecycle<Outcome>> ref=new AtomicReference<>();E5ALifecycle<Outcome> life=new E5ALifecycle<>(owner,clock,clock.now::get,()->ownerDone.get() && resource.returned() && control.drained() && b.finished(),()->{boolean released=ownerDone.get() && resource.returned() && control.drained() && b.finished();String reason=ref.get().terminalReason();return new Outcome(released && !reason.equals("ORIGINAL_CANCEL_DEADLINE_PENDING")?"ABORTED":"PENDING",first,reason,released);},reason->{});ref.set(life);
        Runnable settle=()->{if(control.claimFinish())try{b.finish(3,E4Protocol.sha(new byte[]{1,2,3}),"ABORTED");settlements.incrementAndGet();}catch(Exception e){throw new RuntimeException(e);}life.resourcesChanged();};
        Thread controlThread=null;if(mode.equals("control")){control.admit();controlThread=new Thread(()->control.runAdmitted(()->{controlEntered.countDown();try{releaseControl.await();}catch(InterruptedException e){throw new RuntimeException(e);}},settle),"original-control");controlThread.start();ok(controlEntered.await(2,TimeUnit.SECONDS),"actual original CONTROL entered");}
        life.start();owner.execute(()->{firstThread.set(Thread.currentThread());life.cancel(first);life.initialReturned(false,()->{try{resource.close();}catch(Exception e){throw new RuntimeException(e);}},()->{lastThread.set(Thread.currentThread());ownerDone.set(true);control.ownerReturned();settle.run();finalReturned.countDown();});});
        ok(closeEntered.await(2,TimeUnit.SECONDS),"same original-owner queued continuation really entered original close");long at=life.cancelAt();clock.advance(at+TimeUnit.SECONDS.toNanos(6));
        ok(!life.future().isDone(),"initial PENDING cannot complete Future/test while original window remains");CompletableFuture<Outcome> clientView=life.future();clientView.cancel(true);ok(!life.future().isDone(),"cancelling an outward await view cannot cancel the internal terminal barrier");ok(Files.exists(c.resolve("budget/operation.pending")),"original R/marker remains before actual return");
        AtomicReference<Outcome> exitResult=new AtomicReference<>();Thread instrumentExit=new Thread(()->exitResult.set(life.terminalBeforeExit()),"instrumentation-terminal-exit");instrumentExit.start();instrumentExit.interrupt();instrumentExit.join(20);ok(instrumentExit.isAlive(),"interrupted await/exit cannot end instrumentation before actual return or original deadline");
        if(mode.equals("deadline")){
            clock.advance(at+E5ALifecycle.CANCEL_NS-1);ok(!life.future().isDone(),"same original absolute deadline not early");life.cancel("ANOTHER_AWAIT");ok(life.cancelAt()==at,"another await/close cannot reset first cancel clock");clock.advance(at+E5ALifecycle.CANCEL_NS);
            Outcome r=life.future().get(2,TimeUnit.SECONDS);ok(r.status.equals("PENDING") && !r.released && r.reason.equals("ORIGINAL_CANCEL_DEADLINE_PENDING"),"absolute deadline terminal reports actual UNKNOWN");ok(!resource.returned() && life.finishes()==0 && settlements.get()==0,"deadline never decrements active owner or settles");
            releaseClose.countDown();ok(finalReturned.await(2,TimeUnit.SECONDS),"controlled late return after recorded deadline");ok(life.future().get()==r && !r.released,"late actual completion never upgrades original deadline result");
        }else if(mode.equals("late-timer")){
            clock.now.set(at+E5ALifecycle.CANCEL_NS+1);releaseClose.countDown();Outcome expired=life.future().get(2,TimeUnit.SECONDS);ok(expired.status.equals("PENDING") && expired.reason.equals("ORIGINAL_CANCEL_DEADLINE_PENDING") && expired.released,"late scheduler dispatch cannot qualify actual resources returned after absolute cutoff");
        }else if(mode.equals("control")){
            ok(finalReturned.await(2,TimeUnit.SECONDS) && resource.returned() && control.inFlight()==1,"owner really returned while original CONTROL still active");ok(!life.future().isDone() && settlements.get()==0,"no early terminal or S before original CONTROL finally");releaseControl.countDown();controlThread.join(2000);
        }else{releaseClose.countDown();}
        instrumentExit.join(2000);ok(!instrumentExit.isAlive() && exitResult.get()!=null,"all instrumentation exit paths share actual-return/deadline gate");Outcome r=life.future().get(2,TimeUnit.SECONDS);
        if(!mode.equals("deadline") && !mode.equals("late-timer"))ok(r.status.equals("ABORTED") && r.released && r.error.equals(first) && r.reason.equals("ACTUAL_OWNERS_RETURNED"),"late return within original window settles failure, never READY");
        ok(firstThread.get()==lastThread.get() && life.continuations()==1 && life.finishes()==1 && life.ownerReturnProven() && settlements.get()==1,"same actual owner queue, unique finalizer and original S");owner.shutdown();ok(owner.awaitTermination(2,TimeUnit.SECONDS),"own test executor returned after actual original operations");
    }
    public static void main(String[] args)throws Exception {
        String mode=args[0];Path root=Path.of(args[1]);
        if(mode.equals("writer")){writer(root,args[2]);return;}
        if(mode.equals("reserve") || mode.startsWith("observe-")){newHost(root,!mode.equals("reserve"),mode.equals("observe-live"));return;}
        Files.createDirectory(root);lateCases(root);for(String s:new String[]{"late-return","deadline","late-timer","control"})lifecycle(root,s);
        System.out.println("{\"scope\":\"E5A_PRODUCTION_RECOVERY_ADMISSION_LIFECYCLE_LOCAL_ONLY\",\"assertions\":"+assertions+",\"status\":\"PASS\",\"lateCases\":8,\"androidCodec\":\"NOT_RUN\",\"androidDirectoryFsync\":\"NOT_RUN\",\"realMediaReads\":0}");
    }
}
