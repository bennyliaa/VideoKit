package com.videokit.d1android;
import java.io.IOException;import java.util.*;
/** Registered by the Job BEFORE allocation. Holds the SAME returned object through every failure. */
public final class OriginalOwner<T> {
 public interface Allocate<T>{T run()throws Exception;}
 public interface Action<T>{void run(T original)throws Exception;}
 public interface Value<T,V>{V run(T original)throws Exception;}
 public enum State{EMPTY,ALLOCATING,OPEN,CALLING,CLOSING,CLOSED,UNKNOWN}
 private final String kind;private final Action<T> closer;private T original;private Allocate<T> allocationIntent;private State state=State.EMPTY;
 private boolean closeEntered,allocationUnknown;private String firstFailure,operation="NONE";private long calls,closeCalls;
 public OriginalOwner(String kind,Action<T> closer){this.kind=kind;this.closer=closer;}
 private void failure(String op){if(firstFailure==null)firstFailure=op+"_FAILED";}
 public void allocate(Allocate<T> action)throws IOException{
  synchronized(this){if(state!=State.EMPTY)throw new IOException("ORIGINAL_ALLOCATE_ONCE");allocationIntent=action;state=State.ALLOCATING;operation="ALLOCATE";}
  try{T value=action.run();synchronized(this){original=value;if(value==null)throw new IOException("ORIGINAL_NULL_ALLOCATION");state=State.OPEN;operation="NONE";}}
  catch(Throwable e){synchronized(this){allocationUnknown=true;state=State.UNKNOWN;failure("ALLOCATE");}throw io(e,"ORIGINAL_ALLOCATION_UNKNOWN");}
 }
 public <V>V call(String op,Value<T,V> action)throws IOException{
  T resource;synchronized(this){if(state!=State.OPEN||closeEntered||firstFailure!=null)throw new IOException("ORIGINAL_OPERATION_PENDING");resource=original;state=State.CALLING;operation=op;calls++;}
  try{return action.run(resource);}catch(Throwable e){synchronized(this){failure(op);}throw io(e,"ORIGINAL_OPERATION_FAILED");}
  finally{synchronized(this){if(state==State.CALLING)state=State.OPEN;operation="NONE";}}
 }
 /** One original close admission. Unknown/throwing close is retained, never replayed. */
 public boolean closeOnce()throws IOException {
  T resource;synchronized(this){if(state==State.EMPTY||state==State.CLOSED)return true;if(closeEntered||state!=State.OPEN)return false;closeEntered=true;closeCalls++;resource=original;state=State.CLOSING;operation="CLOSE";}
  try{closer.run(resource);synchronized(this){state=State.CLOSED;operation="NONE";}return true;}
  catch(Throwable e){synchronized(this){state=State.UNKNOWN;failure("CLOSE");}throw io(e,"ORIGINAL_CLOSE_UNKNOWN");}
 }
 public synchronized boolean returned(){return !allocationUnknown&&(state==State.EMPTY||state==State.CLOSED);}
 public synchronized boolean adopted(){return original!=null;}
 public synchronized boolean closeEntered(){return closeEntered;}
 public synchronized T original(){return original;}
 public synchronized Map<String,Object> snapshot(){Map<String,Object> m=new LinkedHashMap<>();m.put("kind",kind);m.put("state",state.name());m.put("operation",operation);m.put("adopted",original!=null);m.put("allocationIntentRetained",allocationIntent!=null);m.put("allocationUnknown",allocationUnknown);m.put("firstFailure",firstFailure==null?"NONE":firstFailure);m.put("calls",calls);m.put("closeCalls",closeCalls);m.put("closeEntered",closeEntered);m.put("returned",returned());return Collections.unmodifiableMap(m);}
 private static IOException io(Throwable e,String fallback){return e instanceof IOException?(IOException)e:new IOException(fallback,e);}
}
