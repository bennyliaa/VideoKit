package com.videokit.spike.e4;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** The original connection/dispatcher owner used by BOTH actual Android binding adapters.
 * bind(false) and SecurityException still require the original unbind exactly once.
 * The Port seam is the real Context adapter; JVM checks substitute only the platform call.
 */
public final class E13BindingOwner<C> {
    public interface Port<C> {boolean bind(C original)throws Exception;void unbind(C original)throws Exception;}
    private static final Set<E13BindingOwner<?>> OWNERS=ConcurrentHashMap.newKeySet();
    public final C original;
    public final String id=E13Stages.owner("binding");
    private final Port<C> port;
    private boolean bindEntered,bindReturned,accepted,closeRequested,unbindEntered,unbindReturned,unbindSucceeded;
    private String bindError="NONE",unbindError="NONE";
    private int callbacks,callbackEntered,callbackReturned,rejectedCallbacks;
    public E13BindingOwner(C original,Port<C> port){this.original=Objects.requireNonNull(original);this.port=Objects.requireNonNull(port);OWNERS.add(this);}
    public void bind(){
        synchronized(this){if(bindEntered || closeRequested)throw new IllegalStateException("E13_BIND_ONCE");bindEntered=true;}
        E13Stages.at(id,"BIND_ENTER","");
        try{boolean value=port.bind(original);synchronized(this){accepted=value;}}
        catch(Exception error){synchronized(this){bindError=error.getClass().getName();}}
        finally{synchronized(this){bindReturned=true;}E13Stages.at(id,"BIND_RETURN",state());continueClose();E13ReturnEvents.returned();}
    }
    public boolean callback(Runnable work){
        synchronized(this){callbackEntered++;if(closeRequested || unbindEntered){rejectedCallbacks++;callbackReturned++;return false;}callbacks++;}
        E13Stages.at(id,"CALLBACK_ENTER","");try{work.run();return true;}
        finally{synchronized(this){callbacks--;callbackReturned++;retireReturned();}E13Stages.at(id,"CALLBACK_RETURN",state());E13ReturnEvents.returned();}
    }
    public void close(){synchronized(this){closeRequested=true;}continueClose();}
    private void continueClose(){
        synchronized(this){
            if(!closeRequested || !bindReturned && bindEntered || unbindEntered)return;
            if(!bindEntered){retireReturned();return;}
            unbindEntered=true;
        }
        E13Stages.at(id,"UNBIND_ENTER","");try{port.unbind(original);synchronized(this){unbindSucceeded=true;}}
        catch(Exception error){synchronized(this){unbindError=error.getClass().getName();}}
        finally{synchronized(this){unbindReturned=true;retireReturned();}E13Stages.at(id,"UNBIND_RETURN",state());E13ReturnEvents.returned();}
    }
    private void retireReturned(){if(returned())OWNERS.remove(this);notifyAll();}
    public synchronized boolean permanentlyUnknown(){return unbindReturned&&!unbindSucceeded;}
    /** Original read-only ACK waits without holding the owner monitor; no retry or substitute close. */
    public synchronized void awaitOriginalReturnOrUnknown()throws InterruptedException{while(!returned()&&!permanentlyUnknown())wait();}
    public synchronized boolean returned(){return closeRequested && callbacks==0 && callbackEntered==callbackReturned && (!bindEntered || bindReturned && unbindEntered && unbindReturned && unbindSucceeded);}
    public synchronized boolean accepted(){return accepted;}
    public synchronized boolean bindReturned(){return bindReturned;}
    public synchronized String unbindError(){return unbindError;}
    public synchronized String bindError(){return bindError;}
    public synchronized String state(){return "bindEntered="+bindEntered+" bindReturned="+bindReturned+" bindAccepted="+accepted+" bindError="+bindError+" unbindEntered="+unbindEntered+" unbindReturned="+unbindReturned+" unbindSucceeded="+unbindSucceeded+" unbindError="+unbindError+" callbackInFlight="+callbacks+" callbackEntered="+callbackEntered+" callbackReturned="+callbackReturned+" callbackRejected="+rejectedCallbacks+" resourcesReturned="+returned();}
    public static boolean allReturned(){return OWNERS.isEmpty();}
    public static int retained(){return OWNERS.size();}
}
