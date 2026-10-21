package com.videokit.fixturetool;
import java.io.*;
import java.nio.*;
import java.nio.channels.SeekableByteChannel;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Authorized non-media original memory-port/clock/worker tests only. */
public final class FixtureToolFixCheck {
    static final byte[] BYTES=new byte[32];
    static int groups,allocated=32;
    static long requested,written;
    static boolean stopped;
    static final List<Object> RETAINED_EXPECTED_MEMORY_UNKNOWN=new ArrayList<>();
    interface Checked {void run()throws Exception;}
    static void need(boolean b,String m){if(!b)throw new AssertionError(m);}
    static long number(Map<String,Object> m,String k){return ((Number)m.get(k)).longValue();}
    static void rejected(Checked action)throws Exception{try{action.run();}catch(Exception expected){return;}throw new AssertionError("expected rejection");}
    static ByteBuffer data(int n){ByteBuffer b=ByteBuffer.wrap(BYTES);b.limit(n);return b;}
    static void group(String name,Checked action)throws Exception {
        need(!stopped,"batch admission closed");long start=System.nanoTime();
        try{action.run();need(System.nanoTime()-start<5000000000L,"group5s observation exceeded");groups++;System.out.println("PASS "+name);}
        catch(Throwable error){stopped=true;throw error;}
    }
    static void joinOriginal(Thread t)throws Exception {
        t.join(5000);
        if(t.isAlive()){stopped=true;RETAINED_EXPECTED_MEMORY_UNKNOWN.add(t);t.join();throw new AssertionError("original joined late; no further admission");}
        t.join(); // same real original, even after bounded wait
    }
    static final class Gate {
        final CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);
        void originalTail()throws IOException {entered.countDown();try{if(!release.await(2,TimeUnit.SECONDS))throw new IOException("CONTROLLED_GATE_OBSERVATION_TIMEOUT");}catch(InterruptedException e){throw new IOException("EXTERNAL_INTERRUPTION",e);}}
        void awaitEntered()throws Exception{need(entered.await(2,TimeUnit.SECONDS),"same original entered gate");}
        void open(){release.countDown();}
    }
    static final class MemoryPort implements SeekableByteChannel,AttemptBudgetChannel.NativePort {
        final byte[] storage=new byte[1024];
        volatile long pos,size;
        volatile boolean open=true,closeEntered,closeReturned,closeThrows;
        int writes,seeks,forces,closes;int[] plan=new int[0];
        String gateOperation;Gate nativeGate;
        MemoryPort(){allocated+=storage.length;}
        void tail(String op)throws IOException{if(op.equals(gateOperation)&&nativeGate!=null)nativeGate.originalTail();}
        @Override public int write(ByteBuffer b)throws IOException {
            int want=b.remaining();requested+=want;need(requested<=65536,"physical memory payload cap");int step=writes++;
            int n=step<plan.length?plan[step]:want;
            if(n==Integer.MIN_VALUE){if(want>0){storage[(int)pos++]=b.get();size=Math.max(size,pos);written++;}throw new IOException("CONTROLLED_UNCERTAIN_AFTER_PHYSICAL1");}
            if(n<0||n>want)return n;
            if(pos>storage.length-n)throw new IOException("MEMORY_RANGE");
            for(int i=0;i<n;i++)storage[(int)pos++]=b.get();size=Math.max(size,pos);written+=n;tail("WRITE");return n;
        }
        @Override public long position()throws IOException{long n=pos;tail("POSITION");return n;}
        @Override public SeekableByteChannel position(long n)throws IOException{if(n<0)throw new IOException("NEGATIVE");pos=n;seeks++;tail("SEEK");return this;}
        @Override public long size()throws IOException{long n=size;tail("SIZE");return n;}
        @Override public int read(ByteBuffer b)throws IOException{throw new IOException("NO_INPUT");}
        @Override public SeekableByteChannel truncate(long n)throws IOException{throw new IOException("NO_TRUNCATE");}
        @Override public boolean isOpen(){return open;}
        @Override public void close()throws IOException{nativeCloseOnce();}
        public int nativeWrite(ByteBuffer b)throws IOException{return write(b);}
        public long nativePosition()throws IOException{return position();}
        public void nativeSeek(long n)throws IOException{position(n);}
        public long nativeSize()throws IOException{return size();}
        public void nativeForce()throws IOException{forces++;tail("FORCE");}
        public void nativeCloseOnce()throws IOException{if(closeEntered)return;closeEntered=true;closes++;open=false;tail("CLOSE");if(closeThrows)throw new IOException("CONTROLLED_CLOSE_UNKNOWN");closeReturned=true;}
        public boolean nativeUsable(){return open&&!closeEntered;}
        public boolean originalReturned(){return closeReturned;}
    }
    static final class TestOwner implements AttemptBudgetChannel.Owner {
        final MemoryPort port;Thread original;volatile String first;String adoptionOperation;Gate adoptionGate;
        TestOwner(MemoryPort p){port=p;}
        void bind(Thread t){need(original==null,"no original replacement");original=t;}
        public void requireOriginalWorker()throws IOException{if(Thread.currentThread()!=original)throw new IOException("ORIGINAL_WORKER_REQUIRED");}
        public void checkAdmission()throws IOException{if(first!=null)throw new IOException("ADMISSION_CLOSED");}
        public synchronized void fail(String s){if(first==null)first=s;}
        public AttemptBudgetChannel.NativePort nativePort(){return port;}
        public void afterNativeReturn(String s)throws IOException{if(s.equals(adoptionOperation)&&adoptionGate!=null)adoptionGate.originalTail();}
    }
    static AttemptBudgetChannel direct(MemoryPort p,long prior){TestOwner o=new TestOwner(p);o.bind(Thread.currentThread());return new AttemptBudgetChannel(o,prior);}
    static void arithmetic()throws Exception {
        MemoryPort p=new MemoryPort();p.plan=new int[]{3,7};AttemptBudgetChannel c=direct(p,0);
        try{need(c.write(data(10))==10,"fully drains partial");Map<String,Object> r=c.receipt(true);need(number(r,"attemptedBytes")==17&&number(r,"acknowledgedLowerBound")==10,"17/10");
            c.setPosition(0);need(c.write(data(8))==8,"header8");r=c.receipt(true);need(number(r,"attemptedBytes")==25&&number(r,"acknowledgedLowerBound")==18&&number(r,"actualPhysicalExtent")==10&&number(r,"actualPhysicalPosition")==8,"25/18 extent10 pos8");
        }finally{c.close();}need(p.closes==1,"single original close");
    }
    static void exceptional()throws Exception {
        MemoryPort p=new MemoryPort();p.plan=new int[]{3,Integer.MIN_VALUE};AttemptBudgetChannel c=direct(p,0);
        try{rejected(()->c.write(data(10)));Map<String,Object> r=c.receipt(true);need(number(r,"attemptedBytes")==17&&number(r,"acknowledgedLowerBound")==3&&"UNKNOWN".equals(r.get("actualPhysicalPosition")),"unknown lastAck3");need(p.pos==4,"controlled actual extra1 not falsely adopted");rejected(()->c.write(data(1)));need(p.writes==2,"no retry after unknown");}finally{c.close();}
    }
    static void invalidNative(int value)throws Exception {MemoryPort p=new MemoryPort();p.plan=new int[]{value};AttemptBudgetChannel c=direct(p,0);try{rejected(()->c.write(data(10)));need(p.writes==1&&number(c.receipt(false),"attemptedBytes")==10,"no spin or refund");}finally{c.close();}}
    static void empty()throws Exception {MemoryPort p=new MemoryPort();AttemptBudgetChannel c=direct(p,0);try{need(c.write(data(0))==0&&p.writes==0&&number(c.receipt(false),"attemptedBytes")==0,"empty no native");}finally{c.close();}}
    static void exactCap()throws Exception {MemoryPort p=new MemoryPort();AttemptBudgetChannel c=direct(p,AttemptBudgetChannel.MAX_ATTEMPT-8);try{need(c.write(data(8))==8,"exact cap");rejected(()->c.write(data(1)));need(p.writes==1&&number(c.receipt(false),"attemptedBytes")==AttemptBudgetChannel.MAX_ATTEMPT,"next1 rejected before native");}finally{c.close();}}
    static void ranges()throws Exception {MemoryPort p=new MemoryPort();AttemptBudgetChannel c=direct(p,0);try{rejected(()->c.setPosition(-1));rejected(()->c.setPosition(Long.MAX_VALUE));need(p.seeks==0,"invalid seek native0");c.setPosition(AttemptBudgetChannel.MAX_ATTEMPT);rejected(()->c.write(data(1)));need(p.writes==0,"range cap before native no expansion");}finally{c.close();}}
    static void capacity()throws Exception {MemoryPort p=new MemoryPort();AttemptBudgetChannel c=direct(p,0);try{for(int i=0;i<512;i++)c.write(data(1));rejected(()->c.write(data(1)));need(p.writes==512,"event cap before native");}finally{c.close();}need(p.closes==1&&((List<?>)c.receipt(true).get("nativeOperationEvents")).size()==512,"cap cannot prevent original cleanup");}
    static void guarded()throws Exception {
        MemoryPort p=new MemoryPort();AttemptBudgetChannel c=direct(p,0);AtomicReference<Throwable> result=new AtomicReference<>();
        Thread wrong=new Thread(()->{try{c.write(data(1));}catch(Throwable e){result.set(e);}},"fix02-wrong-caller");
        try{wrong.start();joinOriginal(wrong);need(result.get() instanceof IOException&&p.writes==0,"wrong caller before native");rejected(()->c.read(data(1)));rejected(()->c.truncate(0));}finally{joinOriginal(wrong);c.close();}
    }
    static void snapshot(String op)throws Exception {
        MemoryPort p=new MemoryPort();TestOwner o=new TestOwner(p);AttemptBudgetChannel c=new AttemptBudgetChannel(o);
        Gate nativeGate=new Gate(),adoptionGate=new Gate();p.gateOperation=op;p.nativeGate=nativeGate;o.adoptionOperation=op;o.adoptionGate=adoptionGate;
        AtomicReference<Throwable> error=new AtomicReference<>();
        Thread worker=new Thread(()->{try{
            if(!op.equals("WRITE"))c.write(data(4));
            switch(op){case "WRITE":c.write(data(10));break;case "SEEK":c.setPosition(0);break;case "FORCE":c.forceOriginal();break;case "POSITION":c.position();break;case "SIZE":c.size();break;case "CLOSE":c.close();break;default:throw new AssertionError(op);}
        }catch(Throwable t){error.set(t);}finally{try{c.close();}catch(Throwable t){error.compareAndSet(null,t);}}},"fix02-original-"+op);o.bind(worker);
        try{worker.start();nativeGate.awaitEntered();Map<String,Object> first=c.receipt(true);
            need(number(first,"nativeInFlight")==1&&number(first,"resultAdoptionPending")==1,"native still in original call");
            need("UNKNOWN".equals(first.get("actualPhysicalPosition"))&&"UNKNOWN".equals(first.get("actualPhysicalExtent")),"pending native actual UNKNOWN");
            long last=op.equals("WRITE")?0:4;need(number(first,"lastAcknowledgedLogicalPosition")==last,"lastAck separated");
            nativeGate.open();adoptionGate.awaitEntered();Map<String,Object> second=c.receipt(true);
            need(number(second,"nativeInFlight")==0&&number(second,"resultAdoptionPending")==1,"original native returned, original callback still pending");
            need("UNKNOWN".equals(second.get("actualPhysicalPosition"))&&"UNKNOWN".equals(second.get("actualPhysicalExtent")),"unadopted actual UNKNOWN");
            need(number(second,"lastAcknowledgedLogicalPosition")==last&&!second.containsKey("nativeOperationEvents"),"no live list exposure");
            // First captured snapshot remains immutable after later native/adoption facts.
            need(number(first,"nativeInFlight")==1,"old scalar snapshot detached");
        }finally{nativeGate.open();adoptionGate.open();joinOriginal(worker);}
        need(error.get()==null,"same original operation success: "+error.get());Map<String,Object> fin=c.receipt(true);
        need(number(fin,"nativeInFlight")==0&&number(fin,"resultAdoptionPending")==0&&p.closes==1,"same originals returned once");
        need(!"UNKNOWN".equals(fin.get("actualPhysicalPosition")),"final known only after adoption");
    }
    static void detachedEvents()throws Exception {MemoryPort p=new MemoryPort();AttemptBudgetChannel c=direct(p,0);try{c.write(data(1));Map<String,Object> r=c.receipt(true);((Map<?,?>)((List<?>)r.get("nativeOperationEvents")).get(0)).clear();need(!((Map<?,?>)((List<?>)c.receipt(true).get("nativeOperationEvents")).get(0)).isEmpty(),"no event map alias");}finally{c.close();}}
    static void closeUnknown()throws Exception {MemoryPort p=new MemoryPort();p.closeThrows=true;AttemptBudgetChannel c=direct(p,0);try{c.write(data(1));rejected(c::close);c.close();need(p.closes==1&&"UNKNOWN".equals(c.receipt(false).get("actualPhysicalPosition")),"unknown close never second native");RETAINED_EXPECTED_MEMORY_UNKNOWN.add(c);}finally{c.close();}}
    static void clockCase(long start,long finish,long observed,long duration,boolean unknown)throws Exception {
        AtomicLong clock=new AtomicLong(start);WorkerDeadline d=new WorkerDeadline(clock::get,duration);AtomicReference<Throwable> error=new AtomicReference<>();
        Thread worker=new Thread(()->{try{clock.set(finish);d.bodyCompletedByOriginal();}catch(Throwable t){error.set(t);}},"fix02-clock-original");d.begin(worker);
        try{worker.start();joinOriginal(worker);clock.set(observed);d.joinSameOriginal();need(error.get()==null,"original completion");need(d.observeUnknown()==unknown&&d.timelyAndJoined()==!unknown,"deadline completion decision");}finally{joinOriginal(worker);}
    }
    static void lateGap()throws Exception {
        AtomicLong clock=new AtomicLong(0);WorkerDeadline d=new WorkerDeadline(clock::get,100);Gate gate=new Gate();
        Thread worker=new Thread(()->{try{gate.originalTail();d.bodyCompletedByOriginal();}catch(Exception e){throw new AssertionError(e);}},"fix02-late-gap-original");d.begin(worker);
        try{worker.start();gate.awaitEntered();worker.join(1);need(worker.isAlive(),"timed join returned while original pending");
            clock.set(101);gate.open();joinOriginal(worker);clock.set(102);d.joinSameOriginal();need(d.observeUnknown()&&!d.timelyAndJoined(),"late completion before observer still UNKNOWN");
        }finally{gate.open();joinOriginal(worker);}
    }
    static void markerNotJoin()throws Exception {
        AtomicLong clock=new AtomicLong(0);WorkerDeadline d=new WorkerDeadline(clock::get,100);Gate tail=new Gate();
        Thread worker=new Thread(()->{clock.set(90);d.bodyCompletedByOriginal();try{tail.originalTail();}catch(Exception e){throw new AssertionError(e);}},"fix02-marker-tail-original");d.begin(worker);
        try{worker.start();tail.awaitEntered();need(!d.timelyAndJoined()&&worker.isAlive(),"marker is not actual return");clock.set(200);}finally{tail.open();d.joinSameOriginal();joinOriginal(worker);}
        need(d.timelyAndJoined(),"timely completion plus later actual external join; observation time not completion time");
    }
    static void trueDeadline()throws Exception {
        WorkerDeadline d=new WorkerDeadline(System::nanoTime,20000000);Gate gate=new Gate();
        Thread worker=new Thread(()->{try{gate.originalTail();d.bodyCompletedByOriginal();}catch(Exception e){throw new AssertionError(e);}},"fix02-real-clock-original");d.begin(worker);
        try{worker.start();gate.awaitEntered();d.awaitBodyWindow();need(d.observeUnknown()&&!d.timelyAndJoined(),"actual20ms window no false return");}finally{gate.open();d.joinSameOriginal();joinOriginal(worker);}
        need(d.observeUnknown()&&!d.timelyAndJoined(),"real late return cannot upgrade");
    }
    static void stickyDeadline()throws Exception {AtomicLong clock=new AtomicLong(0);WorkerDeadline d=new WorkerDeadline(clock::get,100);Gate gate=new Gate();Thread t=new Thread(()->{try{gate.originalTail();d.bodyCompletedByOriginal();}catch(Exception e){throw new AssertionError(e);}},"fix02-sticky-original");d.begin(t);try{t.start();gate.awaitEntered();clock.set(100);need(d.observeUnknown(),"equal unknown before complete");clock.set(101);}finally{gate.open();d.joinSameOriginal();joinOriginal(t);}need(d.observeUnknown(),"sticky after same original returns");}
    public static void main(String[] args)throws Exception {
        need(args.length==0,"no dynamic test selection");
        System.out.println("ORIGIN channel="+AttemptBudgetChannel.class.getProtectionDomain().getCodeSource().getLocation()+" deadline="+WorkerDeadline.class.getProtectionDomain().getCodeSource().getLocation()+" test="+FixtureToolFixCheck.class.getProtectionDomain().getCodeSource().getLocation());
        long start=System.nanoTime();
        group("EX01_EX02_partial_header_attempt25_return18_extent10_position8",FixtureToolFixCheck::arithmetic);
        group("EX03_exception_after_partial_unknown_no_retry",FixtureToolFixCheck::exceptional);
        group("EX05_zero_native_no_spin",()->invalidNative(0));group("negative_native_rejected",()->invalidNative(-1));group("oversized_native_rejected",()->invalidNative(99));
        group("EX06_empty_no_native",FixtureToolFixCheck::empty);group("EX04_exact16MiB_meter_then1_before_native",FixtureToolFixCheck::exactCap);
        group("negative_overflow_seek_and_no_expansion",FixtureToolFixCheck::ranges);group("512_event_cap_still_original_close",FixtureToolFixCheck::capacity);
        group("original_worker_read_truncate_guards",FixtureToolFixCheck::guarded);
        for(String op:new String[]{"WRITE","SEEK","FORCE","POSITION","SIZE","CLOSE"})group("B01_"+op+"_in_native_and_returned_unadopted_snapshot",()->snapshot(op));
        group("detached_event_maps",FixtureToolFixCheck::detachedEvents);group("close_unknown_never_second_close",FixtureToolFixCheck::closeUnknown);
        group("B02_actual_timedjoin_gap_late_completion",FixtureToolFixCheck::lateGap);
        group("timely_completion_late_observation",()->clockCase(0,90,200,100,false));
        group("equal_deadline_is_late",()->clockCase(0,100,100,100,true));
        group("completion_marker_is_not_original_join",FixtureToolFixCheck::markerNotJoin);
        group("actual_monotonic20ms_timeout_then_original_return",FixtureToolFixCheck::trueDeadline);
        group("nanoTime_wrap_timely",()->clockCase(Long.MAX_VALUE-5,Long.MIN_VALUE+3,Long.MIN_VALUE+4,10,false));
        group("nanoTime_wrap_equal_late",()->clockCase(Long.MAX_VALUE-5,Long.MIN_VALUE+4,Long.MIN_VALUE+4,10,true));
        group("clock_regression_unknown",()->clockCase(10,9,11,100,true));
        group("observer_clock_regression_after_completion_unknown",()->clockCase(0,90,80,100,true));
        group("observed_unknown_sticky_after_return",FixtureToolFixCheck::stickyDeadline);
        group("deadline_range_and_wrong_completion_guards",()->{rejected(()->new WorkerDeadline(System::nanoTime,0));rejected(()->new WorkerDeadline(System::nanoTime,Long.MAX_VALUE));WorkerDeadline d=new WorkerDeadline(System::nanoTime,100);rejected(d::bodyCompletedByOriginal);});
        need(System.nanoTime()-start<60000000000L,"whole batch60s");need(allocated<=32768&&requested<=32768&&written<=32768,"per-path payload allocation/IO bounded, two paths fit64KiB");
        System.out.println("DONE groups="+groups+" allocatedPayloadBytes="+allocated+" nativeRequestedPayloadBytes="+requested+" nativeReturnedOrControlledPhysicalPayloadBytes="+written+" expectedRetainedMemoryUnknown="+RETAINED_EXPECTED_MEMORY_UNKNOWN.size()+" allStartedWorkersJoined=true generationMain_JobRun_encoder_muxer_media=NOT_RUN");
    }
}
