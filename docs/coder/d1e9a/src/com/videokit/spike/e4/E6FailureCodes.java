package com.videokit.spike.e4;
import com.videokit.spike.c14.CpuDiagnostics;
import com.videokit.spike.c14.E6NativeDiagnostic;
/** Bounded first-cause traversal. Suppressed cleanup errors cannot replace the primary diagnosis. */
public final class E6FailureCodes {
    public static String safe(Throwable error){
        for(int i=0;i<8 && error!=null;i++,error=error.getCause()){
            String code=error instanceof CpuDiagnostics.Failure?((CpuDiagnostics.Failure)error).code:error.getMessage();
            if(code!=null && code.matches("[A-Z][A-Z0-9_]{0,95}"))return code;
        }return "E4_HOST_OPERATION_FAILED";
    }
    public static E6NativeDiagnostic diagnostic(Throwable error){
        for(int i=0;i<8 && error!=null;i++,error=error.getCause()){if(error instanceof com.videokit.spike.c14.E6AFailure)return ((com.videokit.spike.c14.E6AFailure)error).snapshot;if(error instanceof CpuDiagnostics.Failure)return ((CpuDiagnostics.Failure)error).nativeDiagnostic;}
        return null;
    }
    private E6FailureCodes(){}
}
