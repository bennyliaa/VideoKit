package com.videokit.spike.e4;

import java.io.IOException;

/** Register this holder in its original owner BEFORE calling allocate or any platform open. */
public final class E4Owned<T> {
    public enum State { EMPTY, ALLOCATING, OPEN, INITIALIZING, READY, CLOSING, CLOSED, UNKNOWN }
    public interface Allocate<T> { T run() throws Exception; }
    public interface Action<T> { void run(T resource) throws Exception; }
    public final Object parameters;
    private final Action<T> closer;
    private volatile T resource;
    private volatile State state=State.EMPTY;
    private volatile Throwable firstFailure,closeFailure;
    private boolean closeAttempted;
    public E4Owned(Object parameters,Action<T> closer){this.parameters=parameters;this.closer=closer;}
    public void allocate(Allocate<T> action)throws Exception{
        synchronized(this){if(state!=State.EMPTY)throw new IOException("E4A_ALLOCATE_ONCE");state=State.ALLOCATING;}
        try{resource=action.run();if(resource==null)throw new IOException("E4A_NULL_RESOURCE");state=State.OPEN;}
        catch(Exception failure){firstFailure=failure;state=State.UNKNOWN;throw failure;}
    }
    public void initialize(Action<T> action)throws Exception{
        synchronized(this){if(state!=State.OPEN)throw new IOException("E4A_INITIALIZE_STATE");state=State.INITIALIZING;}
        try{action.run(resource);state=State.READY;}
        catch(Exception failure){firstFailure=failure;try{close();}catch(Exception cleanup){failure.addSuppressed(cleanup);}throw failure;}
    }
    public void close()throws Exception{
        synchronized(this){
            if(state==State.CLOSED)return;
            if(closeAttempted || resource==null || state==State.ALLOCATING)throw new IOException("E4A_ORIGINAL_CLOSE_UNPROVEN",closeFailure);
            closeAttempted=true;state=State.CLOSING;
        }
        try{closer.run(resource);state=State.CLOSED;}
        catch(Exception failure){closeFailure=failure;if(firstFailure==null)firstFailure=failure;state=State.UNKNOWN;throw failure;}
    }
    public T original(){return resource;}
    public State state(){return state;}
    public boolean returned(){return state==State.CLOSED;}
    public Throwable firstFailure(){return firstFailure;}
    public Throwable closeFailure(){return closeFailure;}
}
