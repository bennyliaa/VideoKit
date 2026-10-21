package com.videokit.spike.c14;
import java.io.IOException;
import java.util.concurrent.*;
/** Stable public diagnosis; original local type survives without paths, credentials or remote objects. */
public final class CpuDiagnostics {
    public static final class Failure extends IOException {
        public final String code,phase,category,originalType;public E6NativeDiagnostic nativeDiagnostic;
        Failure(String code,String phase,String category,String type){super(code);this.code=code;this.phase=phase;this.category=category;originalType=type;}
    }
    public static Failure failure(String fallback,String phase,Throwable error){
        for(int n=0;n<8 && (error instanceof ExecutionException || error instanceof CompletionException) && error.getCause()!=null;n++)error=error.getCause();
        if(error instanceof Failure)return (Failure)error;
        String message=error==null?null:error.getMessage();
        String code=message!=null && message.matches("(?:CPU|SOURCE|ENVIRONMENT)_[A-Z_0-9]{1,64}")?message:fallback;
        String category=error instanceof TimeoutException?"TIMEOUT":error instanceof SecurityException?"SECURITY":error==null?"LOCAL":error.getClass().getSimpleName().equals("DeadObjectException")?"PEER_DEAD":error instanceof IOException?"IO":"LOCAL";
        return new Failure(code,phase,category,error==null?"NONE":error.getClass().getName());
    }
    public static Failure nativeFailure(E6NativeDiagnostic d){
        Failure f=new Failure(d.code(),"NATIVE_STAGE_"+d.stage,"NATIVE","NONE");f.nativeDiagnostic=d;return f;
    }
    public interface Action {void run()throws Throwable;}
    public static int workerCategory(Throwable error){return error instanceof LinkageError?1:error instanceof IOException && "CPU_NATIVE_REJECTED".equals(error.getMessage())?2:error instanceof IOException || error instanceof RuntimeException?3:4;}
    public static void preserving(Action body,Action cleanup)throws Throwable {
        Throwable primary=null;try{body.run();}catch(Throwable error){primary=error;}
        try{cleanup.run();}catch(Throwable cleanupError){if(primary==null)primary=cleanupError;else if(primary!=cleanupError)primary.addSuppressed(cleanupError);}
        if(primary!=null)throw primary;
    }
    private CpuDiagnostics(){}
}
