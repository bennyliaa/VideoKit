package com.videokit.spike.c14;

import android.media.MediaExtractor;
import android.media.MediaFormat;
import android.os.ParcelFileDescriptor;
import android.system.Os;
import android.util.AtomicFile;
import androidx.media3.common.C;
import androidx.media3.muxer.*;
import androidx.media3.common.Format;
import androidx.media3.common.Metadata;
import com.google.common.collect.ImmutableList;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.util.concurrent.*;

/** Host-owned temporary target; no source path/URI is accepted here. Debug-only local host. */
public final class AuthorizedSink implements SinkCoordinator.Host {
    private final File temporary;private final String taskId;private FileOutputStream stream;
    private final AtomicFile journal;
    private ParcelFileDescriptor syncDescriptor;
    private boolean opened,closed,validated;private SinkCoordinator.HostState state=SinkCoordinator.HostState.WRITING;
    private final java.util.concurrent.atomic.AtomicInteger hits=new java.util.concurrent.atomic.AtomicInteger();private volatile String hitStage="";
    private long bytes;private int flushes;private volatile String fault="";
    public AuthorizedSink(File explicitlyAuthorizedTemporary,String taskId)throws IOException{temporary=explicitlyAuthorizedTemporary;this.taskId=taskId;journal=new AtomicFile(new File(temporary.getPath()+".task"));
        if(journal.getBaseFile().exists() || new File(journal.getBaseFile().getPath()+".bak").exists())try(DataInputStream input=new DataInputStream(journal.openRead())){if(input.readInt()!=0x564b4431 || !taskId.equals(input.readUTF()))throw new IOException("OUTPUT_TASK_MISMATCH");int ordinal=input.readInt();if(ordinal<0 || ordinal>=SinkCoordinator.HostState.values().length)throw new IOException("OUTPUT_JOURNAL_INVALID");state=SinkCoordinator.HostState.values()[ordinal];}
        else persist(state);
    }
    private void persist(SinkCoordinator.HostState next)throws IOException{FileOutputStream raw=null;try{raw=journal.startWrite();DataOutputStream data=new DataOutputStream(raw);data.writeInt(0x564b4431);data.writeUTF(taskId);data.writeInt(next.ordinal());data.flush();journal.finishWrite(raw);}catch(IOException e){if(raw!=null)journal.failWrite(raw);throw new IOException("OUTPUT_JOURNAL_FAILED");}}
    public synchronized void inject(String stage){fault=stage;}
    private synchronized void id(String id)throws IOException{if(!taskId.equals(id))throw new IOException("OUTPUT_TASK_MISMATCH");}
    public Muxer.Factory muxers(){return new Muxer.Factory(){
        public Muxer create(String ignoredPath)throws MuxerException{
            StageLog.event("HOST_MUXER_CREATE_BEGIN","");
            synchronized(AuthorizedSink.this){
                if(opened || state!=SinkCoordinator.HostState.WRITING)throw new MuxerException("OUTPUT_REOPEN_REJECTED",new IOException());
                opened=true;
                try{stream=new FileOutputStream(temporary);syncDescriptor=ParcelFileDescriptor.dup(stream.getFD());Muxer actual=new Mp4Muxer.Builder(stream).build();return new Muxer(){
                    public int addTrack(Format f)throws MuxerException{StageLog.event("HOST_MUXER_TRACK","mime="+f.sampleMimeType+" width="+f.width+" height="+f.height);int id=actual.addTrack(f);if("video/avc".equals(f.sampleMimeType))actual.addMetadataEntry(new androidx.media3.container.Mp4OrientationData(f.rotationDegrees));return id;}
                    public void writeSampleData(int track,ByteBuffer data,BufferInfo info)throws MuxerException{if(fault.equals("write")){hitStage="write";hits.incrementAndGet();throw new MuxerException("D1_INJECTED_OUTPUT_WRITE",new IOException("D1_INJECTED_OUTPUT_WRITE"));}actual.writeSampleData(track,data,info);bytes+=info.size;}
                    public void addMetadataEntry(Metadata.Entry entry){if(MuxerUtil.isMetadataSupported(entry))actual.addMetadataEntry(entry);else StageLog.event("MUXER_UNSUPPORTED_METADATA_IGNORED",entry.getClass().getSimpleName());}
                    public void close()throws MuxerException{
                        try{actual.close();
                            if(fault.equals("flush")){hitStage="flush";hits.incrementAndGet();throw new IOException("D1_INJECTED_OUTPUT_FLUSH");}
                            Os.fsync(syncDescriptor.getFileDescriptor());
                            synchronized(AuthorizedSink.this){flushes++;closed=true;}
                        }catch(Exception e){throw new MuxerException("OUTPUT_FINALIZE_FAILED",e);}
                        finally{try{if(syncDescriptor!=null)syncDescriptor.close();}catch(IOException ignored){}}
                    }
                };}catch(IOException e){throw new MuxerException("OUTPUT_OPEN_FAILED",e);}
            }
        }
        public ImmutableList<String>getSupportedSampleMimeTypes(int type){return type==C.TRACK_TYPE_VIDEO?ImmutableList.of("video/avc"):type==C.TRACK_TYPE_AUDIO?ImmutableList.of("audio/mp4a-latm"):ImmutableList.of();}
        public boolean supportsWritingNegativeTimestampsInEditList(){return true;}
    };}
    /** Independent track checks plus actual full video decoder drain. */
    public synchronized boolean validate(long expectedDurationMs)throws IOException{
        if(!closed || state!=SinkCoordinator.HostState.WRITING)return false;
        if(fault.equals("validate")){hitStage="validate";hits.incrementAndGet();return false;}
        try(FileInputStream input=new FileInputStream(temporary)){validated=AndroidOutputValidator.validate(input.getFD(),expectedDurationMs);return validated;}
    }
    public int injectionHits(){return hits.get();}public String injectionStage(){return hitStage;}
    public synchronized CompletionStage<String> markReady(String id){
        try{id(id);if(state==SinkCoordinator.HostState.READY)return CompletableFuture.completedFuture("opaque-output-"+taskId);if(state==SinkCoordinator.HostState.ABORTED)throw new IOException("CANCELLED");if(!validated || !closed)throw new IOException("OUTPUT_NOT_VALIDATED");persist(SinkCoordinator.HostState.READY);state=SinkCoordinator.HostState.READY;
            if(fault.equals("ready-response"))return HostFixtures.failed(new IOException("response lost"));return CompletableFuture.completedFuture("opaque-output-"+taskId);
        }catch(IOException e){return HostFixtures.failed(e);}
    }
    public synchronized CompletionStage<SinkCoordinator.Status>query(String id){try{id(id);return CompletableFuture.completedFuture(new SinkCoordinator.Status(state,state==SinkCoordinator.HostState.READY?"opaque-output-"+taskId:null));}catch(IOException e){return HostFixtures.failed(e);}}
    public synchronized CompletionStage<Void>abort(String id){
        try{id(id);if(state==SinkCoordinator.HostState.READY)return CompletableFuture.completedFuture(null);
            if(stream!=null)stream.close();if(syncDescriptor!=null)syncDescriptor.close();Files.deleteIfExists(temporary.toPath());persist(SinkCoordinator.HostState.ABORTED);state=SinkCoordinator.HostState.ABORTED;return CompletableFuture.completedFuture(null);
        }catch(IOException e){return HostFixtures.failed(e);}
    }
    public synchronized long bytes(){return bytes;}public synchronized int flushes(){return flushes;}
    public synchronized boolean ready(){return state==SinkCoordinator.HostState.READY;}
    String authorizedBackendPath(){return temporary.getAbsolutePath();}
}
