package com.videokit.spike.e4;

import android.app.Service;
import android.app.Application;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.os.Binder;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Parcel;
import android.os.ParcelFileDescriptor;
import android.os.Process;
import android.os.RemoteException;
import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

/** Same-UID crash boundary, never a permission or RCE sandbox. Must be exported=false. */
public final class E4CodecService extends Service {
    private final String instance=UUID.randomUUID().toString();
    private final E4Broker broker=new E4Broker();
    private final Map<String,Session> sessions=new LinkedHashMap<>();
    private final Semaphore ingress=new Semaphore(1);
    private HandlerThread ownerThread;private Handler owner;
    private volatile boolean ownerReady,destroyed;
    private volatile Session current;
    private volatile boolean admissionUnknown;
    private final List<Object> rejectedOwners=new ArrayList<>();
    private String nextFault="";
    private E4Protocol.Identity nextFaultIdentity;private int nextFaultPid;
    private static final Set<String> FAULTS=Set.of("capability-deny","configure-first","close-unproven","owner-pause","self-kill-arm","self-kill-commit","native-segv-arm","native-segv-commit");

    private final Binder endpoint=new Binder(){
        @Override protected boolean onTransact(int code,Parcel data,Parcel reply,int flags)throws RemoteException {
            if((flags&IBinder.FLAG_ONEWAY)!=0 || reply==null)throw new SecurityException("E4_SYNCHRONOUS_REQUEST_REQUIRED");
            if(code==INTERFACE_TRANSACTION){reply.writeString(E4CodecWire.DESCRIPTOR);return true;}
            int callerUid=Binder.getCallingUid(),callerPid=Binder.getCallingPid();
            if(callerUid!=Process.myUid())throw new SecurityException("E4_CALLER_UID");
            if(code<E4CodecWire.HELLO || code>E4CodecWire.DEBUG)return super.onTransact(code,data,reply,flags);
            data.enforceInterface(E4CodecWire.DESCRIPTOR);
            if(data.dataSize()>E4CodecWire.MAX_PARCEL)throw new SecurityException("E4_PARCEL_BUDGET");
            if(admissionUnknown){reply.writeNoException();reply.writeBundle(code==E4CodecWire.HELLO?hello():status("PENDING","E4_REJECTED_GRANT_CLOSE_UNPROVEN"));return true;}
            if(!ingress.tryAcquire()){reply.writeNoException();reply.writeBundle(status("BUSY","E4_INGRESS_BUSY"));return true;}
            Bundle request=null;boolean adopted=false,closedRejected=false;
            try{
                request=data.readBundle(E4CodecWire.class.getClassLoader());
                if(request!=null && request.hasFileDescriptors() && code!=E4CodecWire.BEGIN){retainRejected(request);throw new IOException("E4_ONLY_BEGIN_ACCEPTS_DESCRIPTORS");}
                E4CodecWire.keys(request,code);
                if(data.dataAvail()!=0)throw new IOException("E4_TRAILING_PARCEL");
                Bundle result;
                if(code==E4CodecWire.HELLO)result=hello();
                else{
                    E4Protocol.Identity id=E4CodecWire.identity(request);verify(id,callerUid);
                    if(code==E4CodecWire.BEGIN){result=begin(id,request,callerPid);adopted=result.getBoolean("descriptorAdopted");}
                    else if(code==E4CodecWire.DEBUG)result=debug(id,request.getString("fault"),request.getString("armToken"),callerPid);
                    else{
                        Session s=exact(id,callerPid);
                        if(code==E4CodecWire.FRAME)result=frame(s,request,callerUid);
                        else if(code==E4CodecWire.FINISH){broker.endFrames(callerUid,id);s.inputDone=true;schedule(s);result=snapshot(s,"FINISH_ADMITTED");}
                        else if(code==E4CodecWire.CANCEL){cancel(s);result=snapshot(s,"CANCEL_PENDING");}
                        else result=snapshot(s,s.callbackUnknown?"PENDING":s.callbackGate.ackFailed()?"FAILED":s.finished && s.closed?"ENCODED_AWAITING_ISOLATED_VALIDATION":"SNAPSHOT");
                    }
                }
                if(code==E4CodecWire.BEGIN && !adopted){closedRejected=true;boolean proven=closeRejected(request);if(!proven)result=status("PENDING","E4_REJECTED_GRANT_CLOSE_UNPROVEN");result.putBoolean("rejectedGrantCloseProven",proven);}
                reply.writeNoException();reply.writeBundle(result);return true;
            }catch(Exception error){
                boolean rejectedProven=false;
                if(code==E4CodecWire.BEGIN && !adopted && request!=null){closedRejected=true;
                    if("E4_UNKNOWN_FIELD".equals(error.getMessage()) && request.hasFileDescriptors())retainRejected(request);
                    rejectedProven=closeRejected(request);
                }
                Bundle rejected=status(admissionUnknown?"PENDING":"REJECTED",admissionUnknown?"E4_REJECTED_GRANT_CLOSE_UNPROVEN":E4Encoder.safeError(error));
                if(code==E4CodecWire.BEGIN)rejected.putBoolean("rejectedGrantCloseProven",rejectedProven);
                reply.writeNoException();reply.writeBundle(rejected);return true;
            }
            finally{
                if(code==E4CodecWire.BEGIN && !adopted && !closedRejected && request!=null)closeRejected(request);
                ingress.release();
            }
        }
    };
    @Override public void onCreate(){super.onCreate();if(!Application.getProcessName().endsWith(":e4_codec"))throw new IllegalStateException("E4_DEDICATED_PROCESS_REQUIRED");ownerThread=new HandlerThread("videokit-e4-codec-owner");ownerThread.setUncaughtExceptionHandler((thread,error)->{ownerReady=false;Session s=current;if(s!=null){s.error="E4_OWNER_THREAD_DIED";s.trace.failure(s.error);notify(s,snapshot(s,"PENDING"));}});ownerThread.start();owner=new Handler(ownerThread.getLooper());owner.post(()->ownerReady=true);}
    @Override public IBinder onBind(Intent intent){return endpoint;}
    @Override public void onDestroy(){destroyed=true;ownerReady=false;Session s=current;if(s!=null)cancel(s);if(owner!=null)owner.post(()->{if(s!=null)cleanup(s);ownerThread.quitSafely();});super.onDestroy();}

    private Bundle hello(){Bundle b=status(admissionUnknown?"PENDING":ownerReady && !destroyed?"OWNER_READY":"NOT_READY",admissionUnknown?"E4_REJECTED_GRANT_CLOSE_UNPROVEN":"");b.putString("serviceInstance",instance);b.putBoolean("ownerReady",ownerReady && !destroyed && !admissionUnknown);b.putBoolean("admissionUnknown",admissionUnknown);synchronized(rejectedOwners){b.putInt("rejectedGrantOwners",rejectedOwners.size());}return b;}
    private void verify(E4Protocol.Identity id,int uid)throws IOException {
        id.requireHost(uid);
        if(id.hostUid!=Process.myUid() || id.serviceUid!=Process.myUid() || !instance.equals(id.serviceInstance))throw new IOException("E4_INSTANCE_OR_UID");
    }
    private Session exact(E4Protocol.Identity id,int pid)throws IOException {
        Session s; synchronized(sessions){s=sessions.get(id.key());}
        if(s==null || !s.id.matches(id) || s.hostPid!=pid || s!=current)throw new IOException("E4_ORIGINAL_HOST_OR_OLD_GENERATION");return s;
    }
    private Bundle begin(E4Protocol.Identity id,Bundle b,int hostPid)throws Exception {
        if(!ownerReady || destroyed)return status("NOT_READY","E4_OWNER_NOT_READY");
        Session old=current;
        if(old!=null && (!old.closed || old.callbackInFlight.get()!=0 || old.callbackUnknown))return status("PENDING","E4_ENCODER_SLOT_HELD");
        if(nextFaultIdentity!=null && (!nextFaultIdentity.matches(id) || nextFaultPid!=hostPid))throw new IOException("E4_DEBUG_PLAN_IDENTITY");
        synchronized(sessions){if(sessions.size()>=16)throw new IOException("E4_SESSION_HISTORY_BUDGET");}
        ParcelFileDescriptor sink=b.getParcelable("sink"),lease=b.getParcelable("lease");IBinder callback=b.getBinder("callback");
        if(sink==null || lease==null || callback==null || !callback.isBinderAlive())throw new IOException("E4_BEGIN_GRANT_MISSING");
        E4CodecSink output=new E4CodecSink(sink,lease,b.getString("leaseEpoch"));
        broker.create(id);Session s=new Session(id,hostPid,callback,output,nextFault);s.trace.event("BEGIN_ADMITTED","hostPid="+hostPid+";codecPid="+Process.myPid());nextFault="";nextFaultIdentity=null;nextFaultPid=0;
        callback.linkToDeath(s.death,0);
        synchronized(sessions){sessions.put(id.key(),s);current=s;}
        Bundle result;
        if(!owner.post(()->open(s))){s.error="E4_OWNER_POST_FAILED";result=snapshot(s,"PENDING");}
        else result=snapshot(s,"ADMITTED");
        result.putBoolean("descriptorAdopted",true);return result;
    }
    private Bundle frame(Session s,Bundle b,int uid)throws Exception {
        if(s.cancelled.get() || !s.started || !s.openReturned || !s.callbackGate.startProven() || s.closed)throw new IOException("E4_FRAME_TASK_NOT_ACTIVE");
        byte[] pixels=b.getByteArray("rgba");
        E4Protocol.Frame frame=new E4Protocol.Frame(s.id,b.getInt("sequence"),b.getLong("ptsUs"),b.getInt("width"),b.getInt("height"),b.getInt("stride"),b.getInt("rotation"),pixels);
        broker.offer(uid,s.id,frame);schedule(s);Bundle result=snapshot(s,"FRAME_ACCEPTED");result.putInt("sequence",frame.sequence);return result;
    }
    private Bundle debug(E4Protocol.Identity id,String fault,String token,int pid)throws Exception {
        if((getApplicationInfo().flags&ApplicationInfo.FLAG_DEBUGGABLE)==0)throw new IOException("E4_DEBUG_DISABLED");
        if(fault==null || !FAULTS.contains(fault))throw new IOException("E4_DEBUG_FAULT_NOT_ALLOWED");
        if(fault.startsWith("self-kill-") || fault.startsWith("native-segv-")){
            Session s=exact(id,pid);
            if(!s.started || s.closed || s.cancelled.get())throw new IOException("E4_DEBUG_NOT_ACTIVE");
            String kind=fault.startsWith("native-segv-")?"native-segv":"self-kill";
            if(fault.endsWith("-arm")){
                if(s.deathToken!=null)throw new IOException("E4_DEBUG_ALREADY_ARMED");
                s.deathKind=kind;s.deathToken=UUID.randomUUID().toString();Bundle b=snapshot(s,"DEBUG_DEATH_ARMED");b.putString("armToken",s.deathToken);return b;
            }
            if(token==null || !token.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))throw new IOException("E4_DEBUG_ARM_TOKEN");
            if(s.deathToken==null || !s.deathToken.equals(token) || !kind.equals(s.deathKind))throw new IOException("E4_DEBUG_ARM_TOKEN");
            s.deathToken=null;
            // Only the current service process can be targeted; no PID or native signal is fabricated.
            owner.postDelayed(()->{
                if(current!=s || !s.started || s.closed || s.cancelled.get() || !instance.equals(s.id.serviceInstance))return;
                notify(s,snapshot(s,"DEBUG_DEATH_ENTERED"));
                if(current!=s || s.closed || s.cancelled.get())return;
                if(kind.equals("native-segv"))com.videokit.spike.c14.E4DebugFaultBoundary.selfSegv();
                else Process.killProcess(Process.myPid());
            },250);
            return snapshot(s,"DEBUG_DEATH_COMMITTED");
        }
        if(current!=null && !current.closed)throw new IOException("E4_DEBUG_PLAN_REQUIRES_IDLE");
        if(nextFaultIdentity!=null)throw new IOException("E4_DEBUG_PLAN_ALREADY_ARMED");
        nextFault=fault;nextFaultIdentity=id;nextFaultPid=pid;return status("DEBUG_PLAN_ARMED","");
    }
    private void open(Session s){
        s.openEntered=true;s.trace.event("OWNER_OPEN_ENTER","pid="+Process.myPid());
        try{
            if(s.fault.equals("owner-pause")){long stop=System.nanoTime()+2000000000L;while(System.nanoTime()<stop && !s.cancelled.get())Thread.sleep(10);}
            s.sinkLease=broker.registerResource(s.id,E4Broker.ResourceKind.SINK,s.sink,()->{if(!s.sink.close())throw new IOException("E4_SINK_CLOSE_UNPROVEN");});
            s.encoder=new E4Encoder(broker,s.id,s.sink,s.cancelled::get,s.fault,(phase,outcome,error)->{
                s.diagnosticEvents++;s.trace.event(phase,outcome+"="+error); // Metadata never synchronously calls host from codec negotiation.
            });
            s.encoderLease=broker.registerResource(s.id,E4Broker.ResourceKind.ENCODER,s.encoder,()->{if(!s.encoder.close())throw new IOException("E4_CODEC_CLOSE_UNPROVEN");});
            if(s.cancelled.get())throw new IOException("E4_CANCELLED");s.encoder.open();
            if(s.cancelled.get())throw new IOException("E4_CANCELLED");broker.serviceReady(Process.myUid(),s.id,true);s.started=true;notify(s,snapshot(s,"STARTED"));
        }catch(Throwable error){if(s.encoder!=null)s.encoder.recordFailure(error);s.error=E4Encoder.safeError(error);if(s.firstError.isEmpty())s.firstError=s.error;s.trace.failure(s.firstError);s.capabilityBlocked="PIPE_CAPABILITY_UNSUPPORTED".equals(s.error);cleanup(s);}
        finally{s.openReturned=true;s.trace.event("OWNER_OPEN_RETURN","started="+s.started+";ack="+s.callbackGate.startProven());}
    }
    private void schedule(Session s){if(s.scheduled.compareAndSet(false,true))if(!owner.post(()->drain(s))){s.scheduled.set(false);s.error="E4_OWNER_POST_FAILED";cancel(s);}}
    private void drain(Session s){
        try{
            if(s.closed || !s.started)return;
            while(!s.cancelled.get()){
                E4Broker.FrameLease lease=broker.poll(s.id);if(lease==null)break;
                Throwable failure=null;try{s.encoder.frame(lease.frame());lease.encodedAndClose();notify(s,snapshot(s,"FRAME_CONSUMED"));}
                catch(Throwable error){failure=error;throw error;}
                finally{try{lease.close();}catch(Exception cleanup){if(failure!=null)failure.addSuppressed(cleanup);else throw cleanup;}}
            }
            if(s.cancelled.get()){cleanup(s);return;}
            E4Broker.Snapshot q=broker.snapshot(s.id);
            if(s.inputDone && q.queued==0 && q.inFlight==0 && q.encoded==6){
                s.encoder.finish();s.encoderLease.close();s.sinkLease.close();
                broker.codecFinished(Process.myUid(),s.id,s.sink.bytes());s.finished=true;
                s.closed=notify(s,snapshot(s,"ENCODED_AWAITING_ISOLATED_VALIDATION"));if(s.closed)unlink(s);
            }
        }catch(Throwable error){if(s.encoder!=null)s.encoder.recordFailure(error);s.error=E4Encoder.safeError(error);if(s.firstError.isEmpty())s.firstError=s.error;cleanup(s);}
        finally{
            s.scheduled.set(false);
            try{E4Broker.Snapshot p=broker.snapshot(s.id);if(!s.closed && !s.cancelled.get() && (p.queued>0 || s.inputDone && p.encoded==6))schedule(s);}catch(Exception ignored){}
        }
    }
    private void cancel(Session s){s.cancelled.set(true);s.callbackGate.cancel();s.trace.event("CANCEL_REQUEST","actualInFlight="+s.callbackInFlight.get());try{broker.cancel(s.id.hostUid,s.id);}catch(Exception ignored){}if(owner!=null)owner.post(()->cleanup(s));}
    private void cleanup(Session s){
        if(s.cleanupAttempted || s.finished)return;s.cleanupAttempted=true;s.cancelled.set(true);s.callbackGate.cancel();s.trace.event("CLEANUP_ENTER","");
        // Capability refusal has no admitted frames; close the real owners before calling it rejected.
        if(!s.capabilityBlocked)try{broker.cancel(s.id.hostUid,s.id);}catch(Exception ignored){}
        try{if(s.encoderLease!=null)s.encoderLease.close();}catch(Exception error){s.cleanupError="E4_CODEC_CLOSE_UNPROVEN";s.error=s.cleanupError;}
        try{if(s.sinkLease!=null)s.sinkLease.close();else if(!s.sink.close()){s.cleanupError="E4_SINK_CLOSE_UNPROVEN";s.error=s.cleanupError;}}catch(Exception error){s.cleanupError="E4_SINK_CLOSE_UNPROVEN";s.error=s.cleanupError;}
        try{
            E4Broker.Snapshot proof=broker.snapshot(s.id);
            if(s.capabilityBlocked && proof.resourcesReleased())broker.serviceReady(Process.myUid(),s.id,false);
            proof=broker.snapshot(s.id);boolean released=proof.resourcesReleased() && s.sink.released() && (s.encoder==null || s.encoder.released());
            String status=!released?"PENDING":s.capabilityBlocked?"CAPABILITY_BLOCKED":s.error.isEmpty()?"CANCELLED":"FAILED";
            boolean acknowledged=notify(s,snapshot(s,status));s.closed=released && !s.callbackUnknown && s.callbackInFlight.get()==0; // ACK rejection is failure, but a returned call is not still in flight.
            s.trace.event("CLEANUP_RETURN","released="+released+";terminalAck="+acknowledged);
            if(s.closed)unlink(s);
        }catch(Exception error){s.cleanupError="E4_CLEANUP_PROOF_PENDING";s.error=s.cleanupError;notify(s,snapshot(s,"PENDING"));}
    }
    private Bundle snapshot(Session s,String status){
        Bundle b=E4CodecWire.identity(s.id);b.putAll(status(status,s.error));b.putString("firstError",s.firstError);b.putBoolean("ownerReady",ownerReady && !destroyed);
        E4Encoder e=s.encoder;b.putInt("attempts",e==null?0:e.attempts());b.putInt("inputs",e==null?0:e.inputs());b.putInt("outputs",e==null?0:e.outputs());
        b.putString("codecName",e==null?"NONE":e.codecName());b.putInt("nativeCalls",(e==null?0:e.nativeCalls())+s.sink.activeCalls());b.putBoolean("encoderReleased",e==null || e.released());
        if(e!=null)b.putAll(e.diagnostics());
        b.putBoolean("sinkReleased",s.sink.released());b.putBoolean("leaseReleased",s.sink.leaseReleased());b.putLong("bytes",s.sink.bytes());b.putBoolean("fsynced",s.sink.flushed());
        b.putBoolean("imageHeld",e!=null && e.imageHeld());b.putBoolean("rgbaHeld",e!=null && e.rgbaHeld());b.putBoolean("yuvHeld",e!=null && e.yuvHeld());b.putBoolean("creating",e!=null && e.creating());
        b.putInt("callbackInFlight",s.callbackInFlight.get());b.putBoolean("callbackUnknown",s.callbackUnknown);
        b.putBoolean("startAckReturned",s.callbackGate.startAckReturned());b.putBoolean("callbackAckFailed",s.callbackGate.ackFailed());
        b.putInt("callbackEntered",s.callbackGate.entered());b.putInt("callbackReturned",s.callbackGate.returned());b.putString("callbackError",s.callbackError);
        b.putBoolean("ownerOpenEntered",s.openEntered);b.putBoolean("ownerOpenReturned",s.openReturned);b.putString("cleanupError",s.cleanupError);
        b.putString("stage",s.trace.phase());b.putLong("stageAtMs",s.trace.phaseAtMs());b.putString("stageTail",s.trace.tail());b.putInt("stageDropped",s.trace.dropped());
        b.putBoolean("startProven",s.openReturned && s.started && s.callbackGate.startProven() && !s.cancelled.get() && e!=null && e.selected() && e.encoderStarted() && s.sink.opened());
        try{E4Broker.Snapshot p=broker.snapshot(s.id);b.putString("resourceState",p.state.name());b.putInt("queued",p.queued);b.putInt("inFlight",p.inFlight);b.putInt("liveResources",p.liveResources);b.putInt("unknownResources",p.unknownResources);b.putInt("queuePeak",p.peakQueued);b.putBoolean("framesReleased",p.queued==0 && p.inFlight==0);}
        catch(Exception error){b.putString("resourceState","UNKNOWN");b.putBoolean("framesReleased",false);}
        return b;
    }
    private Bundle status(String status,String error){Bundle b=new Bundle();b.putString("status",status);b.putString("error",error);b.putInt("pid",Process.myPid());b.putInt("uid",Process.myUid());return b;}
    private boolean notify(Session s,Bundle event){
        if(s.callbackUnknown || s.callbackGate.ackFailed())return false;
        E5CallbackGate.Call original;
        try{original=s.callbackGate.enter(event.getString("status",""));}
        catch(Exception refused){s.callbackError="E5_CALLBACK_ADMISSION_REFUSED";if(s.firstError.isEmpty())s.firstError=s.callbackError;return false;}
        s.callbackInFlight.incrementAndGet();s.callbackEvent=event;boolean acknowledged=false;
        event.putInt("callbackInFlight",s.callbackInFlight.get());event.putBoolean("callbackUnknown",false);
        s.trace.event("CALLBACK_ENTER",event.getString("status",""));
        try{E4CodecWire.callback(s.callback,event);acknowledged=true;return true;}
        catch(Throwable failed){s.callbackError=E5Trace.safe(failed.getClass().getName()+":"+E4Encoder.safeError(failed));if(s.firstError.isEmpty())s.firstError="E5_CALLBACK_ACK_FAILED";s.trace.failure(s.firstError);if(!s.finished)cancel(s);return false;}
        finally{
            try{original.returned(acknowledged);}catch(Exception invalid){s.callbackUnknown=true;}
            int pending=s.callbackInFlight.decrementAndGet();if(pending==0 && !s.callbackUnknown)s.callbackEvent=null;
            s.trace.event("CALLBACK_RETURN","ack="+acknowledged+";inFlight="+pending);
        }
    }
    private void unlink(Session s){if(!s.unlinked){s.unlinked=true;s.callback.unlinkToDeath(s.death,0);}}
    private void retainRejected(Object owner){synchronized(rejectedOwners){admissionUnknown=true;if(rejectedOwners.size()<4)rejectedOwners.add(owner);}}
    private boolean closeRejected(Bundle b){
        if(b==null)return true;boolean clean=true;
        for(String field:new String[]{"sink","lease"}){
            ParcelFileDescriptor fd=null;
            try{fd=b.getParcelable(field);if(fd!=null)fd.close();}
            catch(Exception error){clean=false;retainRejected(fd==null?b:fd);}
        }
        return clean && !admissionUnknown;
    }
    private final class Session {
        final E4Protocol.Identity id;final int hostPid;final IBinder callback;final E4CodecSink sink;final String fault;
        final AtomicBoolean cancelled=new AtomicBoolean(),scheduled=new AtomicBoolean();final IBinder.DeathRecipient death;
        final E5CallbackGate callbackGate=new E5CallbackGate();final E5Trace trace=new E5Trace();
        volatile boolean openEntered,openReturned;volatile String callbackError="",cleanupError="";
        final AtomicInteger callbackInFlight=new AtomicInteger();volatile boolean callbackUnknown;volatile Bundle callbackEvent;
        volatile E4Encoder encoder;E4Broker.ResourceLease sinkLease,encoderLease;
        volatile boolean started,inputDone,closed,finished;boolean cleanupAttempted,capabilityBlocked,unlinked;int diagnosticEvents;volatile String error="",firstError="";String deathKind,deathToken;
        Session(E4Protocol.Identity id,int hostPid,IBinder callback,E4CodecSink sink,String fault){this.id=id;this.hostPid=hostPid;this.callback=callback;this.sink=sink;this.fault=fault;death=()->cancel(this);}
    }
}
