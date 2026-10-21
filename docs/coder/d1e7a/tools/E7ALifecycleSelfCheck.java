package com.videokit.spike.e4;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;

/** Executes the exact managed Job and finish-ACK decision. Only clock/platform operations are substituted. */
public final class E7ALifecycleSelfCheck {
    static int cases,assertions;
    static final String HANDLE="a6f76397-95ba-49b9-aee1-a3cdfbd74c84";
    static final class Clock implements E7ADiagnosticRun.Clock {volatile long time;public long now(){return time;}}
    static final class Ops implements E7ADiagnosticRun.Operations<Object> {
        String block="",fail="";boolean error,interrupted,setInterruptOnRead;int opened,closed,reads,histories,procs;
        final CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);
        final Object resource=new Object();
        void step(String stage)throws Exception{
            if(block.equals(stage)){entered.countDown();if(!release.await(2,TimeUnit.SECONDS))throw new IOException("FINITE_TEST_BARRIER_TIMEOUT");}
            if(fail.equals(stage)){if(interrupted)throw new InterruptedException();if(error)throw new AssertionError("INJECTED_ERROR");throw new IOException("INJECTED_FAILURE");}
        }
        public void preflight()throws Exception{step("PREFLIGHT");}
        public Object open()throws Exception{opened++;step("OPEN");return resource;}
        public void readAndVerify(Object value)throws Exception{ok(value==resource);reads++;step("READ");if(setInterruptOnRead)Thread.currentThread().interrupt();}
        public void close(Object value)throws Exception{ok(value==resource);step("CLOSE");closed++;}
        public void afterClose()throws Exception{ok(closed==1);step("AFTER_CLOSE");}
        public String diagnose()throws Exception{
            E5AOwner owner=new E5AOwner("8c6673b7-38a5-4a24-838d-ca8466d8b75f",4869,10221,"com.videokit.app",1792224193301L);
            return E7WriterDeathGate.inspect(owner,1792224194301L,new E7WriterDeathGate.Port(){
                public List<E7WriterDeathGate.Exit> history(int pid,int max)throws Exception{histories++;step("HISTORY");return List.of(new E7WriterDeathGate.Exit(4869,10221,"com.videokit.app",1792224193337L,10,0));}
                public E7WriterDeathGate.Proc proc(int pid)throws Exception{procs++;step("PROC");return E7WriterDeathGate.Proc.ABSENT;}
            }).record();
        }
    }
    static final class Fixture {
        final Clock clock=new Clock();final Ops ops=new Ops();int finishes;boolean finishThrows;
        final E7ADiagnosticRun<Object> run=new E7ADiagnosticRun<>(HANDLE,clock,ops,s->{ok(s.safeToFinish);ok(s.operationsReturned);ok(ops.opened==0||ops.closed==1);finishes++;if(finishThrows)throw new IOException("PLATFORM_FINISH_THROW");});
        void sync(){run.beginLaunch();run.run();}
        Thread async()throws Exception{run.beginLaunch();Thread t=new Thread(run);t.start();ok(ops.entered.await(1,TimeUnit.SECONDS));return t;}
        boolean ack(){E7ADiagnosticRun.Snapshot s=run.snapshot();return run.acknowledgeFinish(s.handle,s.sequence);}
    }
    static synchronized void ok(boolean value){assertions++;if(!value)throw new AssertionError("case="+cases+" assertion="+assertions);}
    static void finishThread(Fixture f,Thread t)throws Exception{f.ops.release.countDown();t.join(1000);ok(!t.isAlive());}
    public static void main(String[] args)throws Exception{
        cases++;Fixture f=new Fixture();f.sync();ok(f.run.snapshot().verdict.equals("QUALIFIED_DIAGNOSTIC"));ok(f.run.snapshot().holder.equals("CLOSED"));ok(f.finishes==0);ok(f.ack());ok(f.finishes==1);ok(!f.ack());ok(f.ops.histories==1&&f.ops.procs==1);
        cases++;f=new Fixture();f.ops.fail="PREFLIGHT";f.sync();ok(f.run.snapshot().holder.equals("EMPTY"));ok(f.run.snapshot().verdict.equals("FAILED"));ok(f.ack());ok(f.ops.opened==0);
        for(String stage:new String[]{"READ","AFTER_CLOSE"}){cases++;f=new Fixture();f.ops.fail=stage;f.sync();ok(f.run.snapshot().verdict.equals("FAILED"));ok(f.run.snapshot().safeToFinish);ok(f.ops.closed==1);ok(f.ack());}
        for(String stage:new String[]{"PREFLIGHT","OPEN","READ","CLOSE","AFTER_CLOSE","HISTORY","PROC"}){
            cases++;f=new Fixture();f.ops.block=stage;Thread t=f.async();
            ok(!f.run.snapshot().operationsReturned);ok(!f.run.snapshot().safeToFinish);ok(f.finishes==0);
            f.clock.time=E7ADiagnosticRun.QUALIFICATION_NS;f.run.deadline();
            ok(f.run.snapshot().verdict.equals("PENDING"));ok(!f.ack());ok(f.finishes==0);ok(t.isAlive());
            finishThread(f,t);ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.run.snapshot().safeToFinish);ok(f.ack());ok(f.finishes==1);ok(f.ops.opened==1&&f.ops.closed==1);ok(f.ops.histories<=1&&f.ops.procs<=1);
        }
        cases++;f=new Fixture();f.ops.fail="CLOSE";f.sync();ok(f.run.snapshot().operationsReturned);ok(f.run.snapshot().holder.equals("UNKNOWN"));ok(f.run.snapshot().verdict.equals("PENDING"));ok(!f.run.snapshot().safeToFinish);ok(!f.ack());ok(f.finishes==0);ok(f.ops.closed==0);
        for(boolean error:new boolean[]{false,true}){cases++;f=new Fixture();f.ops.fail="OPEN";f.ops.error=error;f.sync();ok(f.run.snapshot().holder.equals(error?"ALLOCATING":"UNKNOWN"));ok(f.run.snapshot().verdict.equals("PENDING"));ok(!f.ack());ok(f.finishes==0&&f.ops.closed==0&&f.ops.opened==1);}
        cases++;f=new Fixture();f.ops.block="OPEN";Thread allocating=f.async();ok(f.run.snapshot().holder.equals("ALLOCATING"));ok(!f.ack());ok(f.finishes==0);finishThread(f,allocating);ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.ack());
        cases++;f=new Fixture();f.ops.fail="READ";f.ops.interrupted=true;f.sync();ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.ops.closed==1);ok(f.ack());
        cases++;f=new Fixture();f.ops.fail="READ";f.ops.error=true;f.sync();ok(f.run.snapshot().verdict.equals("FAILED"));ok(f.ops.closed==1);ok(f.ack());
        cases++;f=new Fixture();f.ops.fail="READ";f.ops.block="CLOSE";Thread closing=f.async();f.clock.time=E7ADiagnosticRun.QUALIFICATION_NS;f.run.deadline();ok(f.run.snapshot().holder.equals("CLOSING"));ok(!f.ack());finishThread(f,closing);ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.ack());
        cases++;f=new Fixture();f.ops.block="READ";Thread late=f.async();f.clock.time=E7ADiagnosticRun.QUALIFICATION_NS+1;finishThread(f,late);ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.run.snapshot().safeToFinish);ok(f.ack());
        cases++;f=new Fixture();f.clock.time=E7ADiagnosticRun.QUALIFICATION_NS;f.sync();ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.ack());
        cases++;f=new Fixture();f.clock.time=E7ADiagnosticRun.QUALIFICATION_NS-1;f.sync();ok(f.run.snapshot().verdict.equals("QUALIFIED_DIAGNOSTIC"));f.clock.time+=100;f.run.deadline();ok(f.run.snapshot().verdict.equals("QUALIFIED_DIAGNOSTIC"));ok(f.ack());
        cases++;f=new Fixture();ok(!f.run.snapshot().safeToFinish);ok(!f.ack());ok(f.finishes==0);f.run.abortBeforeLaunch();ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.ack());ok(f.ops.opened==0);
        cases++;f=new Fixture();f.run.beginLaunch();f.run.controlFault();ok(f.run.snapshot().phase.equals("LAUNCH_WINDOW"));ok(!f.ack());ok(f.finishes==0);f.run.run();ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.ack());
        cases++;f=new Fixture();f.sync();E7ADiagnosticRun.Snapshot stale=f.run.snapshot();ok(!f.run.acknowledgeFinish("00000000-0000-0000-0000-000000000000",stale.sequence));f.run.stopDependencies();ok(!f.run.acknowledgeFinish(HANDLE,stale.sequence));ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.ack());
        cases++;f=new Fixture();f.sync();f.finishThrows=true;ok(!f.ack());ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.finishes==1);ok(!f.ack());ok(f.finishes==1);
        cases++;f=new Fixture();f.run.abortBeforeLaunch();ok(f.run.snapshot().verdict.equals("FAILED"));ok(f.ack());ok(f.ops.opened==0);
        cases++;f=new Fixture();f.sync();f.run.run();ok(f.ops.opened==1&&f.ops.closed==1);ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.ack());
        cases++;f=new Fixture();f.ops.block="READ";f.ops.setInterruptOnRead=true;Thread interrupted=f.async();finishThread(f,interrupted);ok(f.run.snapshot().verdict.equals("PENDING"));ok(f.ops.closed==1);ok(f.ack());
        System.out.println("actual_job_finish_cases="+cases+" assertions="+assertions+" deadlineNs=10000000000 wrongEarlyFinishes=0 unexpectedReopens=0 nativeDeviceCalls=0");
    }
}
