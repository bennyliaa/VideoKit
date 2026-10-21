package com.videokit.spike.c14;
import android.os.ParcelFileDescriptor;
import android.system.Os;
import androidx.media3.muxer.*;
import androidx.media3.common.Format;
import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.security.*;
import java.util.concurrent.*;
/** Host-authorized fMP4/video-only adapter using the existing FencedTask and SinkCoordinator protocol. */
final class PipelineOutputSink implements SinkCoordinator.Host {
    static void preflightDirectory(Path directory)throws IOException{Files.createDirectories(directory);long bytes=0;int tasks=0;try(java.util.stream.Stream<Path> entries=Files.list(directory)){for(Path entry:(Iterable<Path>)entries::iterator){String name=entry.getFileName().toString();if(Files.isSymbolicLink(entry))throw new IOException("PIPE_OUTPUT_LINK_REJECTED");if(name.endsWith(".journal"))tasks++;if(name.endsWith(".mp4"))bytes=Math.addExact(bytes,Files.size(entry));}}if(tasks>=24 || bytes>4194304L-PipelineRules.MAX_OUTPUT)throw new IOException("PIPE_OUTPUT_DIRECTORY_BUDGET");}
    final FencedTask task;private final String id;private String epoch;
    private FileOutputStream stream;private ParcelFileDescriptor sync,leaseDescriptor;private AndroidLease.WorkerLease lease;private BoundedOutputChannel channel;private FragmentedMp4Muxer muxer;
    private boolean opened;private volatile boolean channelClosed=true,syncClosed=true,leaseClosed=true,ownerClosed,flushed,muxerClosed;private PipelineValidationReceipt receipt;
    private final String fault;int hits;private long samples;private long last=-1;
    PipelineOutputSink(Path directory,String id,String fault)throws IOException{this.id=id;this.fault=fault;task=new FencedTask(directory,id,IsolatedExportController::syncDirectory,AndroidLease::exclusive);}
    synchronized void open()throws IOException{
        if(opened)throw new IOException("PIPE_OUTPUT_REOPEN");opened=true;epoch=task.issue();
        leaseDescriptor=ParcelFileDescriptor.open(task.authorizedLease().toFile(),ParcelFileDescriptor.MODE_READ_ONLY);leaseClosed=false;lease=AndroidLease.WorkerLease.acquire(leaseDescriptor,epoch);
        channelClosed=false;stream=new FileOutputStream(task.authorizedOutput().toFile());syncClosed=false;sync=ParcelFileDescriptor.dup(stream.getFD());
        channel=new BoundedOutputChannel(new OutputStream(){public void write(int b)throws IOException{if(fault.equals("write")){hits++;throw new IOException("PIPE_SINK_WRITE");}stream.write(b);}public void write(byte[] b,int o,int n)throws IOException{if(fault.equals("write")){hits++;throw new IOException("PIPE_SINK_WRITE");}stream.write(b,o,n);}public void close()throws IOException{stream.close();channelClosed=true;}});
        muxer=new FragmentedMp4Muxer.Builder(channel).setFragmentDurationMs(200).setSampleCopyingEnabled(true).build();
    }
    int addTrack(Format format)throws IOException{if(!"video/avc".equals(format.sampleMimeType) || format.width!=256 || format.height!=144 || format.rotationDegrees!=0)throw new IOException("PIPE_OUTPUT_TRACK");return muxer.addTrack(format);}
    void sample(int track,ByteBuffer data,android.media.MediaCodec.BufferInfo info)throws Exception{
        if(info.size<1 || info.size>PipelineRules.MAX_SAMPLE || samples>=PipelineRules.FRAMES || info.presentationTimeUs<0 || info.presentationTimeUs>PipelineRules.MAX_RELATIVE_US || (last>=0 && info.presentationTimeUs<=last))throw new IOException("PIPE_OUTPUT_SAMPLE_BUDGET_OR_PTS");
        muxer.writeSampleData(track,data,new androidx.media3.muxer.BufferInfo(info.presentationTimeUs,info.size,info.flags));samples++;last=info.presentationTimeUs;
    }
    boolean finishWriter(){
        try{if(muxer!=null && !muxerClosed){muxer.close();muxerClosed=true;}if(fault.equals("flush")){hits++;throw new IOException("PIPE_SINK_FLUSH");}if(sync!=null){Os.fsync(sync.getFileDescriptor());flushed=true;}}
        catch(Exception error){EncoderDiagnostics.event("MUX",null,error,"FINALIZE_FAILED",false,0,0,false,writerReleased());StageLog.failure("PIPE_OUTPUT_FINALIZE_FAILED",error);}
        finally{closeHandles();}
        return muxerClosed && flushed && writerReleased() && samples==PipelineRules.FRAMES;
    }
    boolean closeHandles(){
        if(!channelClosed)try{if(channel!=null)channel.close();else if(stream!=null){stream.close();channelClosed=true;}}catch(Exception error){StageLog.failure("PIPE_OUTPUT_CLOSE_UNPROVEN",error);}
        if(!syncClosed)try{sync.close();syncClosed=true;}catch(Exception error){StageLog.failure("PIPE_SYNC_CLOSE_UNPROVEN",error);}
        if(channelClosed && syncClosed && !leaseClosed)try{if(lease!=null)lease.close();if(leaseDescriptor!=null)leaseDescriptor.close();leaseClosed=true;}catch(Exception error){StageLog.failure("PIPE_LEASE_CLOSE_UNPROVEN",error);}
        return writerReleased();
    }
    synchronized boolean writerReleased(){return channelClosed && syncClosed && leaseClosed;}
    long bytes()throws IOException{return Files.exists(task.authorizedOutput())?Files.size(task.authorizedOutput()):0;}
    String digest()throws IOException{long size=bytes();if(size<1 || size>PipelineRules.MAX_OUTPUT)throw new IOException("PIPE_OUTPUT_SIZE");try(InputStream in=Files.newInputStream(task.authorizedOutput())){MessageDigest digest=MessageDigest.getInstance("SHA-256");byte[] buffer=new byte[65536];int n;long read=0;while((n=in.read(buffer))!=-1){read+=n;if(read>PipelineRules.MAX_OUTPUT)throw new IOException("PIPE_OUTPUT_SIZE");digest.update(buffer,0,n);}StringBuilder out=new StringBuilder();for(byte b:digest.digest())out.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return out.toString();}catch(NoSuchAlgorithmException error){throw new AssertionError(error);}}
    AsyncReadBridge.Provider validationSource()throws IOException{if(!writerReleased() || !flushed || !muxerClosed || !task.workerLeaseClear())throw new IOException("PIPE_OUTPUT_STILL_WRITING");return HostFixtures.file(task.authorizedOutput());}
    void corruptForTest()throws IOException{if(fault.equals("validate")){hits++;try(java.nio.channels.FileChannel f=java.nio.channels.FileChannel.open(task.authorizedOutput(),StandardOpenOption.WRITE)){f.truncate(Math.max(1,bytes()/2));f.force(true);}}}
    void accept(PipelineValidationReceipt proof)throws IOException{if(proof==null || !writerReleased() || !flushed || !proof.sha.equals(digest()) || proof.bytes!=bytes())throw new IOException("PIPE_OUTPUT_RECEIPT_MISMATCH");receipt=proof;}
    private void id(String requested)throws IOException{if(!id.equals(requested))throw new IOException("OUTPUT_TASK_MISMATCH");}
    public synchronized CompletionStage<String> markReady(String requested){try{id(requested);if(task.query()==FencedTask.State.READY)return CompletableFuture.completedFuture(task.token());if(receipt==null || !writerReleased())throw new IOException("PIPE_OUTPUT_NOT_VALIDATED");String token=task.ready(epoch,true);if(fault.equals("ready-response")){hits++;return HostFixtures.failed(new IOException("OUTPUT_READY_UNKNOWN"));}return CompletableFuture.completedFuture(token);}catch(IOException error){return HostFixtures.failed(error);}}
    public synchronized CompletionStage<SinkCoordinator.Status>query(String requested){try{id(requested);FencedTask.State state=task.query();return CompletableFuture.completedFuture(new SinkCoordinator.Status(state==FencedTask.State.READY?SinkCoordinator.HostState.READY:state==FencedTask.State.ABORTED?SinkCoordinator.HostState.ABORTED:SinkCoordinator.HostState.WRITING,state==FencedTask.State.READY?task.token():null));}catch(IOException error){return HostFixtures.failed(error);}}
    public synchronized CompletionStage<Void>abort(String requested){try{id(requested);if(!writerReleased())throw new IOException("PIPE_OUTPUT_WRITER_UNPROVEN");task.abort();return CompletableFuture.completedFuture(null);}catch(IOException error){return HostFixtures.failed(error);}}
    boolean closeOwner(){if(!ownerClosed)try{task.close();ownerClosed=true;}catch(IOException error){StageLog.failure("PIPE_OUTPUT_OWNER_UNPROVEN",error);}return ownerClosed;}
}
