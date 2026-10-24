package android.system;
/** Explicit JVM platform exception port only; real Android API is compiled separately. */
public final class ErrnoException extends Exception {public final int errno;public ErrnoException(String fn,int e){super(fn);errno=e;}}
