package com.videokit.spike.e4;

import java.io.*;
import java.nio.channels.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.*;

/** Synthetic private files and model drivers only. Never codec, Binder, device, or old media evidence. */
public final class E5SelfCheck {
    static int assertions;
    static void ok(boolean value,String why){assertions++;if(!value)throw new AssertionError(why);}
    interface Checked {void run()throws Exception;}
    static void rejects(String code,Checked c)throws Exception {try{c.run();throw new AssertionError("missing refusal "+code);}catch(IOException e){ok(e.getMessage().startsWith(code),"exact refusal "+e.getMessage());}}
    static void callbacks()throws Exception {
        ok(E5CallbackGate.synchronous(0),"ordinary sync");ok(E5CallbackGate.synchronous(2|16),"framework sync metadata flags accepted");ok(!E5CallbackGate.synchronous(1|16),"ONEWAY rejected");
        E5CallbackGate g=new E5CallbackGate();E5CallbackGate.Call started=g.enter("STARTED");ok(g.inFlight()==1 && !g.startProven(),"signal before original ACK cannot admit source");
        AtomicReference<Throwable> rejected=new AtomicReference<>();Thread other=new Thread(()->{try{started.returned(true);}catch(Throwable e){rejected.set(e);}});other.start();other.join(1000);ok(rejected.get() instanceof IOException && g.inFlight()==1,"different thread cannot return original call");
        started.returned(true);ok(g.startProven() && g.returned()==1,"actual original ACK admits start");rejects("E5_CALLBACK_ORIGINAL_RETURN_REQUIRED",()->started.returned(true));
        E5CallbackGate.Call next=g.enter("FRAME_CONSUMED");g.cancel();ok(g.inFlight()==1 && !g.startProven(),"cancel does not deduct active callback");next.returned(true);ok(g.inFlight()==0 && g.startAckReturned() && !g.startProven(),"late original return drains but never revives cancelled task");
        E5CallbackGate failed=new E5CallbackGate();E5CallbackGate.Call bad=failed.enter("STARTED");bad.returned(false);ok(failed.ackFailed() && failed.inFlight()==0 && !failed.startProven(),"bad ACK is returned failure, never fake in-flight or READY");rejects("E5_CALLBACK_ADMISSION_REFUSED",()->failed.enter("FAILED"));
        E5CallbackGate late=new E5CallbackGate();E5CallbackGate.Call call=late.enter("STARTED");late.cancel();call.returned(true);ok(late.startAckReturned() && !late.startProven(),"ACK after cancellation remains factual but cannot admit");
        E5Trace trace=new E5Trace();trace.failure("OWNER_EXCEPTION");for(int i=0;i<200;i++)trace.event("QUERY_"+i,"中文 "+i);ok(trace.rows().size()==64 && trace.dropped()==137 && trace.first().equals("OWNER_EXCEPTION"),"finite metadata retains first cause");ok(trace.tail().contains("QUERY_199") && trace.tail().length()<1400,"latest bounded phase evidence survives polling");
    }
    static void negotiation()throws Exception {
        E4EncoderNegotiation.Descriptor d=new E4EncoderNegotiation.Descriptor("test.codec","test.codec",true,false,false,true,new int[]{21,19},new int[]{1,1});List<E4EncoderNegotiation.Candidate> plan=E4EncoderNegotiation.plan(List.of(d));
        class Driver implements E4EncoderNegotiation.Driver {
            boolean capabilityThrows,configureThrows,closeUnknown,live;int creates,closes;AtomicBoolean cancel=new AtomicBoolean();
            public boolean supported(E4EncoderNegotiation.Candidate c)throws Exception{if(capabilityThrows)throw new IOException("CAPABILITY_OWNER_EXCEPTION");return true;}
            public void create(E4EncoderNegotiation.Candidate c){creates++;live=true;}
            public void configure(E4EncoderNegotiation.Candidate c)throws Exception{if(configureThrows)throw new IOException("CONFIGURE_OWNER_EXCEPTION");}
            public void start(E4EncoderNegotiation.Candidate c){cancel.set(true);}
            public void release()throws Exception{closes++;if(closeUnknown)throw new IOException("ORIGINAL_CLOSE_UNKNOWN");live=false;}
            public boolean released(){return !live;}
            public void event(String s,E4EncoderNegotiation.Candidate c,Throwable e,String o,boolean f){}
            void run()throws Exception{new E4EncoderNegotiation(this,cancel::get,System::nanoTime).run(plan);}
        }
        Driver cap=new Driver();cap.capabilityThrows=true;rejects("PIPE_ENCODER_CAPABILITY_FAILED",cap::run);ok(cap.creates==0,"STARTED-before-capability-error never creates or admits frames");
        Driver close=new Driver();close.configureThrows=true;close.closeUnknown=true;rejects("PIPE_ENCODER_CONFIGURE_FAILED",close::run);ok(close.creates==1 && close.closes==1 && close.live,"original unknown close forbids fallback candidate");
        Driver late=new Driver();rejects("PIPE_CANCELLED",late::run);ok(late.creates==1 && late.closes==1 && !late.live,"owner returns after cancel; original resource actually closes once");
    }
    static Path fixture(Path root,String name,int bytes)throws Exception {
        Path f=root.resolve(name);Files.createDirectories(f.resolve("e4a_outputs"));Files.createDirectory(f.resolve("e4a_output_budget"));Path o=f.resolve("e4a_outputs"),b=f.resolve("e4a_output_budget");
        try(DataOutputStream d=new DataOutputStream(Files.newOutputStream(o.resolve(E5N2Recovery.TASK+".identity"),StandardOpenOption.CREATE_NEW))){d.writeUTF("E4A_ORIGINAL_IDENTITY_V1");d.writeUTF(E5N2Recovery.BATCH);d.writeUTF(E5N2Recovery.BUDGET);d.writeUTF(E5N2Recovery.HEX);d.writeLong(E5N2Recovery.EPOCH);d.writeLong(1);d.writeUTF(E5N2Recovery.SERVICE);d.writeInt(E5N2Recovery.UID);d.writeInt(E5N2Recovery.UID);d.writeUTF(E5N2Recovery.TASK);}
        try(DataOutputStream d=new DataOutputStream(Files.newOutputStream(o.resolve(E5N2Recovery.TASK+".journal"),StandardOpenOption.CREATE_NEW))){d.writeInt(0x45344131);d.writeUTF(E5N2Recovery.TASK);d.writeInt(0);d.writeUTF(E5N2Recovery.LEASE);d.writeBoolean(true);}
        Files.write(o.resolve(E5N2Recovery.TASK+".lease"),E5N2Recovery.LEASE.getBytes(StandardCharsets.US_ASCII),StandardOpenOption.CREATE_NEW);Files.write(o.resolve(E5N2Recovery.TASK+".owner"),new byte[0],StandardOpenOption.CREATE_NEW);Files.write(o.resolve(E5N2Recovery.TASK+".mp4"),new byte[bytes],StandardOpenOption.CREATE_NEW);
        Files.write(b.resolve("ledger.bin"),E5N2Recovery.ORIGINAL.getBytes(StandardCharsets.US_ASCII),StandardOpenOption.CREATE_NEW);Files.write(b.resolve("identity.anchor"),E5N2Recovery.BUDGET.getBytes(StandardCharsets.US_ASCII),StandardOpenOption.CREATE_NEW);Files.write(b.resolve("operation.pending"),new byte[0],StandardOpenOption.CREATE_NEW);return f;
    }
    static class Model implements E5N2Recovery.Platform {
        public E5AOwner recoveryOwner()throws Exception{return new E5AOwner(UUID.randomUUID().toString(),(int)ProcessHandle.current().pid(),E5N2Recovery.UID,"com.videokit.app",System.currentTimeMillis());}
        boolean deathMissing,busy,closeUnknown,failAfterFence;int fences,closes;
        public E5N2Recovery.Death death(int pid)throws Exception{if(deathMissing)throw new IOException("MISSING_ACTUAL_EXIT_RECORD");return new E5N2Recovery.Death(pid,E5N2Recovery.UID,pid==E5N2Recovery.HOST?"com.videokit.app":"com.videokit.app:e4_codec",1792208963380L,13,0,true);}
        public void sync(Path p)throws Exception{if(failAfterFence && fences>0)throw new IOException("MODELED_DIRECTORY_SYNC_FAILURE");}
        public boolean returned(){return true;}
        public void lock(Path p,E4Owned<E4FencedTask.LeaseGuard> h)throws Exception {
            class Guard implements E4FencedTask.LeaseGuard {RandomAccessFile file;FileLock lock;
                public void fence(String epoch)throws IOException{fences++;file.setLength(0);file.write(epoch.getBytes(StandardCharsets.US_ASCII));file.getFD().sync();}
                public void close()throws IOException{closes++;if(closeUnknown)throw new IOException("MODELED_CLOSE_UNKNOWN");if(lock!=null)lock.release();if(file!=null)file.close();}}
            Guard g=new Guard();h.allocate(()->g);h.initialize(x->{g.file=new RandomAccessFile(p.toFile(),"rw");if(busy || closeUnknown)throw new IOException("MODELED_LEASE_BUSY");g.lock=g.file.getChannel().tryLock(4096,1,false);if(g.lock==null)throw new IOException("MODELED_LEASE_BUSY");});
        }
    }
    static void recovery(Path root,String mode)throws Exception {
        if(mode.equals("close-unknown")){Path f=fixture(root,"unknown",0);Model p=new Model();p.closeUnknown=true;E5N2Recovery.Result r=new E5N2Recovery(f,p).execute(true);ok(r.status.equals("BLOCKED") && E5N2Recovery.retainedOperations()==1,"original unknown handle remains strongly retained");ok(Files.readString(f.resolve("e4a_output_budget/ledger.bin")).equals(E5N2Recovery.ORIGINAL) && Files.exists(f.resolve("e4a_output_budget/operation.pending")),"empty output never auto-refunds with unknown owner");rejects("E5_N2_RECOVERY_OWNER_OR_DURABILITY_PENDING",()->new E4OutputBudget(f.resolve("e4a_output_budget"),E5N2Recovery.BUDGET,UUID.randomUUID().toString(),E5N2Recovery.BATCH,pth->{}).reserve());return;}
        if(mode.equals("durability-unknown")){Path f=fixture(root,"durability",0);Model p=new Model();p.failAfterFence=true;E5N2Recovery.Result r=new E5N2Recovery(f,p).execute(true);ok(r.status.equals("BLOCKED") && E5N2Recovery.retainedOperations()==1,"failed durable journal keeps recovery poison even after handles return");ok(Files.exists(f.resolve("e4a_output_budget/operation.pending")),"partial fence cannot clear marker");return;}
        Path missing=fixture(root,"missing-death",0);Model noDeath=new Model();noDeath.deathMissing=true;E5N2Recovery.Result denied=new E5N2Recovery(missing,noDeath).execute(true);ok(denied.status.equals("BLOCKED") && noDeath.fences==0,"no death evidence: no fence/refund");ok(Files.readString(missing.resolve("e4a_output_budget/ledger.bin")).equals(E5N2Recovery.ORIGINAL),"original R preserved");
        Path busy=fixture(root,"busy",0);Model noLease=new Model();noLease.busy=true;ok(new E5N2Recovery(busy,noLease).execute(true).status.equals("BLOCKED") && noLease.fences==0 && E5N2Recovery.retainedOperations()==0,"known closed busy lock is refused without poisoning or mutation");
        Path query=fixture(root,"query",0);Model qp=new Model();ok(new E5N2Recovery(query,qp).execute(false).status.equals("QUERY_ELIGIBLE") && qp.fences==0,"QUERY cannot mutate or hash output");
        for(int bytes:new int[]{0,17}){
            Path f=fixture(root,"proved-"+bytes,bytes);Model p=new Model();E5N2Recovery.Result r=new E5N2Recovery(f,p).execute(true);ok(r.status.equals("ABORTED_SETTLED") && r.bytes==bytes && !r.oldCloseAck,"all independent proof permits actual retained-byte accounting: "+r);ok(p.fences==1 && p.closes==2 && E5N2Recovery.retainedOperations()==0,"both actual model locks close before marker archival");
            Path b=f.resolve("e4a_output_budget");ok(!Files.exists(b.resolve("operation.pending")) && Files.exists(b.resolve("operation.pending.N2-e5-aborted")),"marker archived, not deleted");ok(Files.readString(b.resolve("N2-e5-recovery.complete")).equals(E5N2Recovery.COMPLETE),"completion binds exact original task and budget");String ledger=Files.readString(b.resolve("ledger.bin"));ok(ledger.startsWith(E5N2Recovery.ORIGINAL) && ledger.contains(" ABORTED "+bytes+" "),"original ledger preserved plus exactly one S");
            ok(Files.size(f.resolve("e4a_outputs/"+E5N2Recovery.TASK+".mp4"))==bytes && Files.exists(f.resolve("e4a_output_budget/N2-e5-recovery/journal.before")),"retained output and original before-image preserved");
            ok(new E5N2Recovery(f,new Model()).execute(true).status.equals("BLOCKED") && Files.readString(b.resolve("ledger.bin")).equals(ledger),"repeated recovery cannot append another settlement");
            long[] accounting=new E4OutputBudget(b,E5N2Recovery.BUDGET,UUID.randomUUID().toString(),E5N2Recovery.BATCH,pth->{}).inspect();ok(accounting[0]==bytes && accounting[1]==0 && accounting[2]==1,"production ledger parser recognizes actual cumulative consumption");
            try(java.nio.file.DirectoryStream<Path> entries=Files.newDirectoryStream(f.resolve("e4a_outputs"))){int count=0;for(Path entry:entries){if(!Files.isRegularFile(entry))throw new AssertionError("normal output flat-file admission would fail");count++;}ok(count==5,"recovery archive does not add a forbidden directory to normal output inventory");}
            E4OutputBudget next=new E4OutputBudget(b,E5N2Recovery.BUDGET,UUID.randomUUID().toString(),E5N2Recovery.BATCH,pth->{});next.reserve();next.finish(0,E4Protocol.sha(new byte[0]),"ABORTED");ok(next.finished(),"normal persistent budget can reserve and settle after complete N2 recovery");ledger=Files.readString(b.resolve("ledger.bin"));
            Files.move(b.resolve("N2-e5-recovery.complete"),b.resolve("test-only-withheld-completion"));
            rejects("E5_N2_RECOVERY_COMPLETION_UNPROVEN",()->new E4OutputBudget(b,E5N2Recovery.BUDGET,UUID.randomUUID().toString(),E5N2Recovery.BATCH,pth->{}).reserve());
            ok(Files.readString(b.resolve("ledger.bin")).equals(ledger),"completion absence cannot reserve a fresh output or duplicate settlement");
        }
    }
    public static void main(String[] args)throws Exception {
        Path root=Path.of(args[0]);Files.createDirectory(root);String mode=args.length>1?args[1]:"main";
        if(mode.equals("main")){callbacks();negotiation();}recovery(root,mode);
        System.out.println("{\"scope\":\"E5_JVM_SYNTHETIC_ONLY\",\"mode\":\""+mode+"\",\"status\":\"PASS\",\"assertions\":"+assertions+",\"retainedOperations\":"+E5N2Recovery.retainedOperations()+",\"androidCodec\":\"NOT_RUN\",\"binder\":\"NOT_RUN\"}");
    }
}
