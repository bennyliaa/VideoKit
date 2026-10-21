package com.videokit.spike.c14;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import com.videokit.spike.e4.E6FailureCodes;
public final class E6DiagnosisSelfCheck {
    static int count;
    static void check(boolean value){if(!value)throw new AssertionError();count++;}
    interface Op {void run()throws Throwable;}
    static void rejects(Op op)throws Throwable{try{op.run();throw new AssertionError();}catch(IOException expected){count++;}}
    public static void main(String[] args)throws Throwable{
        E6NativeDiagnostic d=new E6NativeDiagnostic(3,134,5,0,6,6,5,0,0,0,1041667,2,53651);
        CpuDiagnostics.Failure f=CpuDiagnostics.nativeFailure(d);Throwable wrapped=new ExecutionException(new CompletionException(f));
        check("E6_NATIVE_PTS".equals(E6FailureCodes.safe(wrapped)));check(E6FailureCodes.diagnostic(wrapped)==d);check(d.safe().contains("decoded=6 accepted=5"));
        check(E6FailureCodes.safe(new IOException("D:/private/source.mp4 credentials")).equals("E4_HOST_OPERATION_FAILED"));
        rejects(()->new E6NativeDiagnostic(10,1,5,0,6,6,5,0,0,0,0,1,1));
        rejects(()->new E6NativeDiagnostic(3,0,5,0,6,6,5,0,0,0,0,1,1));
        rejects(()->new E6NativeDiagnostic(3,1,5,0,6,5,6,0,0,0,0,1,1));
        rejects(()->new E6NativeDiagnostic(3,1,5,0,6,6,5,0,0,0,0,8193,1));
        rejects(()->new E6NativeDiagnostic(3,1,5,0,6,6,5,2,0,0,0,1,1));
        try{CpuDiagnostics.preserving(()->{throw wrapped;},()->{throw new IOException("E4_CLEANUP_PENDING");});throw new AssertionError();}
        catch(ExecutionException original){check(original==wrapped && original.getSuppressed().length==1);check(E6FailureCodes.safe(original).equals("E6_NATIVE_PTS"));}
        List<byte[]> source=new ArrayList<>(),decoded=new ArrayList<>();for(int i=0;i<6;i++){byte[] a=new byte[144];Arrays.fill(a,(byte)(i*30));source.add(a);decoded.add(a.clone());}
        PipelineRules.content(source,decoded);check(true);
        rejects(()->PipelineRules.content(source,decoded.subList(0,5)));
        List<byte[]> wrong=new ArrayList<>(decoded);Collections.reverse(wrong);rejects(()->PipelineRules.content(source,wrong));
        List<byte[]> flat=new ArrayList<>();for(int i=0;i<6;i++)flat.add(new byte[144]);rejects(()->PipelineRules.content(flat,flat));
        long[] timeline={0,208333,416667,625000,833333,1000000};PipelineRules.timeline(timeline);check(true);
        rejects(()->PipelineRules.timeline(new long[]{0,208333,416667,625000,833333,833333}));
        System.out.println("PASS diagnostic/host first cause/cleanup and unchanged content/timeline cases="+count);
    }
}
