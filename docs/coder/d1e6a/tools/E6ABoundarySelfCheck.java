package com.videokit.spike.c14;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import com.videokit.spike.e4.*;

/** Executes actual adapter ownership/receipt and diagnostic receive methods; only platform operations are simulated. */
public final class E6ABoundarySelfCheck {
    static final String TASK="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",SHA="1".repeat(64);
    static final long[] TIMELINE={0,200000,400000,600000,800000,1000000};
    static int assertions,cases;
    static void check(boolean v){assertions++;if(!v)throw new AssertionError();}
    static void pass(String id){cases++;System.out.println("CASE "+id+" PASS platform=SIMULATED boundary=PRODUCTION");}
    static final class State implements E6ADiagnosticInbox.State {
        int stage=5,mode=11,frames=6;boolean revoked;
        public int pid(){return 12345;}public int uid(){return 99066;}public String task(){return TASK;}public long epoch(){return 12;}
        public boolean revoked(){return revoked;}public int stage(){return stage;}public int mode(){return mode;}public int frames(){return frames;}
    }
    interface Build {E6NativeDiagnostic get()throws Exception;}
    static E6NativeDiagnostic ok(long last)throws IOException{return new E6NativeDiagnostic(0,0,5,0,6,6,6,1,1,1,last,1,64);}
    static E6ADiagnosticInbox.Payload payload(Build d,boolean trailing){return new E6ADiagnosticInbox.Payload(){public E6NativeDiagnostic parse()throws Exception{return d.get();}public void end()throws Exception{if(trailing)throw new IOException("CPU_TRAILING_DATA");}};}
    static E6NativeDiagnostic receive(E6ADiagnosticInbox inbox,Build d)throws Exception{return inbox.receive(12345,99066,TASK,12,256,payload(d,false));}
    interface Run {void run()throws Exception;}
    static void rejects(Run r,String code)throws Exception{try{r.run();throw new AssertionError("unexpected success");}catch(IOException e){check(code.equals(e.getMessage()));}}
    static List<byte[]> thumbs(){List<byte[]> out=new ArrayList<>();for(int i=0;i<6;i++){byte[] b=new byte[144];Arrays.fill(b,(byte)(i*30));out.add(b);}return out;}
    static final class Owner implements E4CpuAdapter.ValidationOwner,PipelineValidationReceipt.View {
        final State state=new State();final E6ADiagnosticInbox inbox=new E6ADiagnosticInbox(state);final CpuLifecycle life=new CpuLifecycle();
        final List<CpuTaskClient.VerifyFrame> frames=new ArrayList<>();Throwable nativeFailure,stopFailure,closeFailure;boolean stopResult=true,done=true;int starts,stops,closes,retains;
        Owner()throws Exception{
            Constructor<CpuTaskClient.VerifyFrame> c=CpuTaskClient.VerifyFrame.class.getDeclaredConstructor(long.class,long.class,int.class,int.class,int.class,byte[].class,byte[].class);c.setAccessible(true);
            List<byte[]> thumbs=thumbs();for(int i=0;i<6;i++)frames.add(c.newInstance(TIMELINE[i],TIMELINE[i],1,1000000,0,new byte[32],thumbs.get(i)));
        }
        public String task(){return TASK;}
        public void startAndAwait(long[] t)throws Exception{
            starts++;PipelineRules.timeline(t);
            if(nativeFailure!=null){state.frames=5;E6NativeDiagnostic d=receive(inbox,()->new E6NativeDiagnostic(3,134,5,0,6,6,5,0,0,0,1041667,1,64));throw CpuDiagnostics.nativeFailure(d);}
            receive(inbox,()->ok(1000000));
        }
        public E6NativeDiagnostic snapshot(){return inbox.snapshot();}
        public boolean stop()throws Exception{stops++;if(stopFailure!=null)throw (Exception)stopFailure;if(stopResult){life.death();life.sourceReleased(true);life.releaseSlot();}return stopResult;}
        public void close()throws Exception{closes++;if(closeFailure!=null)throw (Exception)closeFailure;}
        public void retain(){retains++;}public PipelineValidationReceipt.View view(){return this;}
        public int workerPid(){return 12345;}public int workerUid(){return 99066;}public boolean verificationDone(){return done;}public boolean orientationVerified(){return true;}
        public CpuLifecycle.Snapshot lifecycle(){return life.snapshot();}public int unresolvedWorkers(){return 0;}public List<CpuTaskClient.VerifyFrame> verificationFrames(){return frames;}
    }
    static E6AFailure failed(Owner owner,List<byte[]> source,Callable<String> digest,String expected)throws Exception{
        try{E4CpuAdapter.validate(owner,TIMELINE,source,SHA,64,digest);throw new AssertionError("validation passed");}
        catch(E6AFailure f){
            check(expected.equals(f.getMessage()));check(f.scope.equals("VALIDATOR") && f.mode==11 && f.task.equals(TASK));
            check(f.snapshot==owner.inbox.snapshot() && f.snapshot!=null);check(f.getCause()==f.primary);check(owner.stops==1 && owner.closes==1);check(f.safe().length()<1400);
            E6ADiagnosticState report=new E6ADiagnosticState();report.validatorEnter();report.failure(f);check(report.validator().contains("primary="+expected));check(report.validator().contains("background={code="));return f;
        }
    }
    static void postFailures()throws Exception{
        Owner o=new Owner();IOException digest=new IOException("E6A_TEST_DIGEST_FAILED");E6AFailure f=failed(o,thumbs(),()->{throw digest;},digest.getMessage());
        check(f.primary==digest && f.phase.equals("DIGEST") && f.snapshot.code().equals("E6_NATIVE_OK"));pass("F01_DIGEST_FIRST_ERROR_WITH_NATIVE_OK");
        o=new Owner();f=failed(o,thumbs(),()->"2".repeat(64),"PIPE_OUTPUT_VERIFICATION_UNPROVEN");check(f.phase.equals("RECEIPT"));pass("F01_ACTUAL_RECEIPT_DIGEST_MISMATCH");
        o=new Owner();o.done=false;failed(o,thumbs(),()->SHA,"PIPE_OUTPUT_VERIFICATION_UNPROVEN");pass("F01_ACTUAL_RECEIPT_INCOMPLETE");
        o=new Owner();List<byte[]> wrong=thumbs();Collections.reverse(wrong);failed(o,wrong,()->SHA,"PIPE_OUTPUT_CONTENT_ERROR");pass("F01_ACTUAL_CONTENT_FAILURE");
        o=new Owner();List<byte[]> shortThumb=thumbs();shortThumb.set(5,new byte[143]);failed(o,shortThumb,()->SHA,"PIPE_THUMB_LENGTH");pass("F01_ACTUAL_THUMBNAIL_FAILURE");
        o=new Owner();o.stopResult=false;f=failed(o,thumbs(),()->SHA,"E4_VALIDATOR_CLOSE_UNPROVEN");check(f.phase.equals("STOP") && o.retains==1);pass("F01_FALSE_STOP_RETAINS_NATIVE_OK");
        o=new Owner();IOException stop=new IOException("E6A_TEST_STOP_FAILED");o.stopFailure=stop;f=failed(o,thumbs(),()->SHA,stop.getMessage());check(f.primary==stop && o.retains==1);pass("F01_THROWING_STOP_EXACT_FIRST");
        o=new Owner();IOException close=new IOException("E6A_TEST_CLOSE_FAILED");o.closeFailure=close;f=failed(o,thumbs(),()->SHA,close.getMessage());check(f.primary==close && f.phase.equals("CLOSE") && o.retains==1);pass("F01_CLOSE_RETAINS_NATIVE_OK");
        o=new Owner();o.nativeFailure=new IOException();o.stopFailure=stop;o.closeFailure=close;f=failed(o,thumbs(),()->SHA,"E6_NATIVE_PTS");
        check(f.primary instanceof CpuDiagnostics.Failure && f.phase.equals("NATIVE") && f.cleanup.size()==2 && f.cleanup.get(0)==stop && f.cleanup.get(1)==close && f.getSuppressed().length==2 && o.retains==1);pass("F01_NATIVE_FIRST_TWO_CLEANUP_FAILURES");
        o=new Owner();E4CpuAdapter.Verification v=E4CpuAdapter.validate(o,TIMELINE,thumbs(),SHA,64,()->SHA);check(v.frames==6 && v.fullEof && v.sourceClosed && v.originalDeath && v.slotReleased && o.retains==0);
        E6ADiagnosticState report=new E6ADiagnosticState();report.sourceEnter();report.sourceSuccess("b".repeat(32),"code=E6_NATIVE_OK accepted=0");report.validatorEnter();report.validatorSuccess(v.task,v.nativeDiagnostic);check(report.source().contains("scope=SOURCE task="+"b".repeat(32)+" mode=10 phase=FRAME_ACCEPTED") && report.validator().contains("scope=VALIDATOR task="+TASK+" mode=11"));check(report.validator().contains("phase=VERIFIED") && report.validator().contains("code=E6_NATIVE_OK"));pass("F01_F02_VALIDATOR_SUCCESS_KEPT");
    }
    static void sourceFailure()throws Exception{
        State state=new State();state.mode=10;state.stage=4;state.frames=0;E6ADiagnosticInbox inbox=new E6ADiagnosticInbox(state);
        E6NativeDiagnostic d=receive(inbox,()->new E6NativeDiagnostic(5,122,4,-1094995529,0,0,0,0,0,0,-1,1,64));CpuDiagnostics.Failure original=CpuDiagnostics.nativeFailure(d);
        AtomicInteger stopped=new AtomicInteger(),closed=new AtomicInteger();
        AsyncReadBridge.Provider provider=token->{throw new AssertionError("source content must not open");};
        E4CpuAdapter adapter=new E4CpuAdapter(new android.content.Context(),provider,2);E6ADiagnosticState report=new E6ADiagnosticState();report.sourceEnter();
        try{adapter.next(1,new E4CpuAdapter.SourceOwner(){public String task(){return TASK;}public E4CpuAdapter.Sample read(int n)throws Exception{throw original;}public E6NativeDiagnostic snapshot(){return inbox.snapshot();}public boolean stop(){stopped.incrementAndGet();return true;}public void close(){closed.incrementAndGet();}public void cancel(){}});throw new AssertionError();}
        catch(E6AFailure f){report.failure(f);check(f.primary==original && f.snapshot==d && f.scope.equals("SOURCE") && f.mode==10 && f.phase.equals("READ"));check(report.validator().equals("NOT_STARTED"));check(report.source().contains("scope=SOURCE") && report.source().contains("mode=10") && report.source().contains("E6_NATIVE_DEMUX"));check(E6FailureCodes.safe(f).equals("E6_NATIVE_DEMUX"));}
        check(stopped.get()==1 && closed.get()==1 && adapter.sourceClosed());adapter.close();pass("F02_ACTUAL_SOURCE_FAILURE_VALIDATOR_NOT_STARTED");
    }
    static void ownershipWindows()throws Exception{
        Owner owner=new Owner();try{E4CpuAdapter.validate(owner,new long[]{1,2,3,4,5,6},thumbs(),SHA,64,()->SHA);throw new AssertionError();}
        catch(E6AFailure f){check(f.getMessage().equals("PIPE_OUTPUT_TIMELINE") && f.phase.equals("TIMELINE") && f.snapshot==null && f.safe().contains("start=NOT_STARTED"));check(owner.starts==0 && owner.stops==1 && owner.closes==1 && owner.retains==0);}pass("F01_INVALID_TIMELINE_OWNED_RESOURCE_CLEANUP");
        AsyncReadBridge.Provider provider=token->{throw new AssertionError("no source read");};E4CpuAdapter adapter=new E4CpuAdapter(new android.content.Context(),provider,2);adapter.cancel();AtomicInteger reads=new AtomicInteger(),closes=new AtomicInteger();
        try{adapter.next(1,new E4CpuAdapter.SourceOwner(){public String task(){return TASK;}public E4CpuAdapter.Sample read(int n){reads.incrementAndGet();throw new AssertionError();}public E6NativeDiagnostic snapshot(){return null;}public boolean stop(){return true;}public void close(){closes.incrementAndGet();}public void cancel(){}});throw new AssertionError();}
        catch(E6AFailure f){check(f.scope.equals("SOURCE") && f.getMessage().equals("E4_SOURCE_SEQUENCE_OR_PENDING") && f.phase.equals("BEFORE_READ") && f.snapshot==null && f.safe().contains("start=NOT_STARTED"));check(reads.get()==0 && closes.get()==1 && adapter.sourceClosed());}adapter.close();pass("F02_CANCEL_BETWEEN_CREATION_AND_READ_CLOSES_OWNER");
    }
    static void receiver()throws Exception{
        State state=new State();E6ADiagnosticInbox inbox=new E6ADiagnosticInbox(state);AtomicInteger parses=new AtomicInteger();
        Build valid=()->{parses.incrementAndGet();return ok(1000000);};
        rejects(()->inbox.receive(1,99066,TASK,12,256,payload(valid,false)),"CPU_BROKER_IDENTITY");
        rejects(()->inbox.receive(12345,1,TASK,12,256,payload(valid,false)),"CPU_BROKER_IDENTITY");
        rejects(()->inbox.receive(12345,99066,"b".repeat(32),12,256,payload(valid,false)),"CPU_BROKER_IDENTITY");
        rejects(()->inbox.receive(12345,99066,TASK,13,256,payload(valid,false)),"CPU_BROKER_IDENTITY");
        rejects(()->inbox.receive(12345,99066,TASK,12,1025,payload(valid,false)),"CPU_PARCEL_BUDGET");
        state.revoked=true;rejects(()->receive(inbox,valid),"CPU_BROKER_IDENTITY");state.revoked=false;check(parses.get()==0 && inbox.snapshot()==null);pass("F03_ACTUAL_RECEIVE_AUTH_SIZE_REVOKED_BEFORE_PARSE");
        rejects(()->receive(inbox,()->new E6NativeDiagnostic(10,1,5,0,0,0,0,0,0,0,0,0,0)),"E6_NATIVE_DIAG_PROTOCOL");check(inbox.snapshot()==null);pass("F03_INVALID_FIELDS_DO_NOT_CLAIM_SLOT");
        rejects(()->inbox.receive(12345,99066,TASK,12,256,payload(valid,true)),"CPU_TRAILING_DATA");check(inbox.snapshot()==null);pass("F03_TRAILING_DOES_NOT_CLAIM_SLOT");
        rejects(()->receive(inbox,()->new E6NativeDiagnostic(0,0,4,0,6,6,6,1,1,1,1000000,1,64)),"E6_NATIVE_DIAG_PHASE");check(inbox.snapshot()==null);pass("F03_STAGE_DOES_NOT_CLAIM_SLOT");
        rejects(()->receive(inbox,()->new E6NativeDiagnostic(3,134,5,0,6,6,5,0,0,0,1041667,1,64)),"E6_NATIVE_DIAG_PHASE");check(inbox.snapshot()==null);pass("F03_FRAME_COUNT_DOES_NOT_CLAIM_SLOT");
        E6NativeDiagnostic first=receive(inbox,valid);rejects(()->receive(inbox,()->ok(1000001)),"E6_NATIVE_DIAG_ONCE");check(inbox.snapshot()==first);pass("F03_FIRST_VALID_AFTER_INVALID_RETAINED");
        State raceState=new State();E6ADiagnosticInbox race=new E6ADiagnosticInbox(raceState);int threads=16;ExecutorService pool=Executors.newFixedThreadPool(threads);CountDownLatch ready=new CountDownLatch(threads),go=new CountDownLatch(1);AtomicInteger wins=new AtomicInteger(),rejected=new AtomicInteger();AtomicReference<E6NativeDiagnostic> winner=new AtomicReference<>();List<Future<?>> futures=new ArrayList<>();
        for(int i=0;i<threads;i++){final int id=i;futures.add(pool.submit(()->{ready.countDown();try{if(!go.await(5,TimeUnit.SECONDS))throw new AssertionError();E6NativeDiagnostic d=receive(race,()->ok(1000000+id));wins.incrementAndGet();winner.set(d);}catch(IOException e){if(!e.getMessage().equals("E6_NATIVE_DIAG_ONCE"))throw new RuntimeException(e);rejected.incrementAndGet();}catch(Exception e){throw new RuntimeException(e);}}));}
        check(ready.await(5,TimeUnit.SECONDS));go.countDown();for(Future<?> f:futures)f.get(5,TimeUnit.SECONDS);pool.shutdown();check(pool.awaitTermination(5,TimeUnit.SECONDS));check(wins.get()==1 && rejected.get()==15 && race.snapshot()==winner.get());
        E6NativeDiagnostic saved=race.snapshot();rejects(()->receive(race,valid),"E6_NATIVE_DIAG_ONCE");check(race.snapshot()==saved);pass("F03_16_DIRECT_PRODUCTION_RECEIVERS_ONE_WIN_15_REJECT");
    }
    public static void main(String[] args)throws Exception{postFailures();sourceFailure();ownershipWindows();receiver();System.out.println("PASS production_boundary_cases="+cases+" assertions="+assertions+" Android_Binder_JNI=NOT_RUN media_reads=0");}
}
