package com.videokit.spike.c14;
import java.io.*;
import java.util.*;
/** Constructed only from a completed, actually released isolated verification task and sealed output. */
final class PipelineValidationReceipt {
    final String sha;final long bytes;final int pid,uid,frames;final String task;final boolean fullEof,sourceClosed,originalDeath,slotReleased;
    interface View {String task();int workerPid();int workerUid();boolean verificationDone();boolean orientationVerified();CpuLifecycle.Snapshot lifecycle();int unresolvedWorkers();List<CpuTaskClient.VerifyFrame> verificationFrames();}
    static View view(CpuTaskClient v){return new View(){public String task(){return v.task;}public int workerPid(){return v.workerPid();}public int workerUid(){return v.workerUid();}public boolean verificationDone(){return v.verificationDone();}public boolean orientationVerified(){return v.orientationVerified();}public CpuLifecycle.Snapshot lifecycle(){return v.lifecycle();}public int unresolvedWorkers(){return v.unresolvedWorkers();}public List<CpuTaskClient.VerifyFrame> verificationFrames(){return v.verificationFrames();}};}
    private PipelineValidationReceipt(String sha,long bytes,View verifier,CpuLifecycle.Snapshot state){this.sha=sha;this.bytes=bytes;pid=verifier.workerPid();uid=verifier.workerUid();task=verifier.task();frames=verifier.verificationFrames().size();fullEof=verifier.verificationDone();sourceClosed=state.sourceReleased;originalDeath=state.actualDeath;slotReleased=state.slotReleased;}
    static PipelineValidationReceipt prove(CpuTaskClient verifier,List<byte[]> source,String before,String after,long bytes)throws IOException{return prove(view(verifier),source,before,after,bytes);}
    static PipelineValidationReceipt prove(View verifier,List<byte[]> source,String before,String after,long bytes)throws IOException{
        CpuLifecycle.Snapshot state=verifier.lifecycle();
        if(!verifier.verificationDone() || !verifier.orientationVerified() || !state.actualDeath || !state.slotReleased || !state.sourceReleased || state.pendingCalls!=0 || state.stopPending || verifier.unresolvedWorkers()!=0 || bytes<1 || bytes>PipelineRules.MAX_OUTPUT || !before.equals(after))throw new IOException("PIPE_OUTPUT_VERIFICATION_UNPROVEN");
        List<byte[]> decoded=new ArrayList<>();for(CpuTaskClient.VerifyFrame frame:verifier.verificationFrames())decoded.add(frame.thumb());PipelineRules.content(source,decoded);
        double max=0,change=0,outChange=0;for(int i=0;i<source.size();i++){double error=PipelineRules.error(source.get(i),decoded.get(i));max=Math.max(max,error);for(int j=0;j<source.size();j++){change=Math.max(change,PipelineRules.error(source.get(i),source.get(j)));outChange=Math.max(outChange,PipelineRules.error(decoded.get(i),decoded.get(j)));}CpuTaskClient.VerifyFrame frame=verifier.verificationFrames().get(i);StageLog.event("PIPE_CONTENT_FRAME","sequence="+(i+1)+" verifier_task="+verifier.task()+" pts_us="+frame.pts+" decoded_rgba_sha="+frame.sha+" luma_mae="+error);}
        StageLog.event("PIPE_VISUAL_CHECK","frames="+source.size()+" max_luma_mae="+max+" source_distinction="+change+" output_distinction="+outChange+" full_eof=true audio_present=false");
        return new PipelineValidationReceipt(before,bytes,verifier,state);
    }
}
