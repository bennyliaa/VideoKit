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
    private final Port<C> port;
    private boolean bindEntered,bindReturned,accepted,closeRequested,unbindEntered,unbindReturned,unbindSucceeded;
    private String bindError="NONE",unbindError="NONE";
    private int callbacks,callbackEntered,callbackReturned,rejectedCallbacks;
    public E13BindingOwner(C original,Port<C> port){this.original=Objects.requireNonNull(original);this.port=Objects.requireNonNull(port);OWNERS.add(this);}
    public void bind(){
        synchronized(this){if(bindEntered || closeRequested)throw new IllegalStateException("E13_BIND_ONCE");bindEntered=true;}
        try{boolean value=port.bind(original);synchronized(this){accepted=value;}}
        catch(Exception error){synchronized(this){bindError=error.getClass().getName();}}
        finally{synchronized(this){bindReturned=true;}continueClose();}
    }
    public boolean callback(Runnable work){
        synchronized(this){callbackEntered++;if(closeRequested || unbindEntered){rejectedCallbacks++;callbackReturned++;return false;}callbacks++;}
        try{work.run();return true;}
        finally{synchronized(this){callbacks--;callbackReturned++;retireReturned();}}
    }
    public void close(){synchronized(this){closeRequested=true;}continueClose();}
    private void continueClose(){
        synchronized(this){
            if(!closeRequested || !bindReturned && bindEntered || unbindEntered)return;
            if(!bindEntered){retireReturned();return;}
            unbindEntered=true;
        }
        try{port.unbind(original);synchronized(this){unbindSucceeded=true;}}
        catch(Exception error){synchronized(this){unbindError=error.getClass().getName();}}
        finally{synchronized(this){unbindReturned=true;retireReturned();}}
    }
    private void retireReturned(){if(returned())OWNERS.remove(this);}
    public synchronized boolean returned(){return closeRequested && callbacks==0 && callbackEntered==callbackReturned && (!bindEntered || bindReturned && unbindEntered && unbindReturned && unbindSucceeded);}
    public synchronized boolean accepted(){return accepted;}
    public synchronized boolean bindReturned(){return bindReturned;}
    public synchronized String unbindError(){return unbindError;}
    public synchronized String bindError(){return bindError;}
    public synchronized String state(){return "bindEntered="+bindEntered+" bindReturned="+bindReturned+" bindAccepted="+accepted+" bindError="+bindError+" unbindEntered="+unbindEntered+" unbindReturned="+unbindReturned+" unbindSucceeded="+unbindSucceeded+" unbindError="+unbindError+" callbackInFlight="+callbacks+" callbackEntered="+callbackEntered+" callbackReturned="+callbackReturned+" callbackRejected="+rejectedCallbacks+" resourcesReturned="+returned();}
    public static boolean allReturned(){return OWNERS.isEmpty();}
    public static int retained(){return OWNERS.size();}
}
