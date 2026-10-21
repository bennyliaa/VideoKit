package com.videokit.fixturetool;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import org.jcodec.codecs.h264.H264Encoder;
import org.jcodec.codecs.h264.H264Utils;
import org.jcodec.codecs.h264.mp4.AvcCBox;
import org.jcodec.common.*;
import org.jcodec.common.model.*;
import org.jcodec.common.model.Packet.FrameType;
import org.jcodec.containers.mp4.Brand;
import org.jcodec.containers.mp4.boxes.VideoSampleEntry;
import org.jcodec.containers.mp4.muxer.AbstractMP4MuxerTrack;
import org.jcodec.containers.mp4.muxer.MP4Muxer;

/** FUTURE GENERATION ONLY. Compilation/package review is not permission to run
 * Main or initialize an encoder. No library/Android self-tests in this build. */
public final class SixFrameDriver {
    static final long INPUT_MAX = 8L*1024*1024, DEADLINE_MS = 60000;
    static final int SAMPLE_MAX = 262144, CSD_MAX = 65536;
    static final Path ROOT = Paths.get("D:/CodexProjects/VideoKit/docs/coder/d1fixture-six01").toAbsolutePath().normalize();
    static final Path DIRECTORY = ROOT.resolve("new-output"), OUTPUT = DIRECTORY.resolve("avc6-candidate.mp4");
    private static final AtomicReference<Job> ORIGINAL = new AtomicReference<>();

    /** Registered on Job before a native handle is allocated; never swapped. */
    static final class FileOwner implements AttemptBudgetChannel.NativePort {
        private final Job job;
        private volatile String state = "REGISTERED_NOT_ALLOCATED";
        private FileChannel handle;
        private volatile boolean closeAttempted, closeReturned, forceAttempted, forceReturned;
        private volatile long finalSize = -1, readCalls, readBytes, eofCalls;
        private final boolean reader;
        FileOwner(Job job, boolean reader) { this.job=job;this.reader=reader; }
        void open() throws IOException {
            job.requireOriginalWorker();job.checkAdmission();
            if(!state.equals("REGISTERED_NOT_ALLOCATED"))throw new IOException("OWNER_ALREADY_USED");
            state="OPEN_CALL_ENTERED";
            try {
                handle = reader ? FileChannel.open(OUTPUT,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)
                    : FileChannel.open(OUTPUT,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS);
                state="OPEN_RETURNED";job.nativeOpened();
            } catch(Throwable e) {state="OPEN_UNKNOWN";job.fail("ORIGINAL_OPEN_UNKNOWN");throw new IOException("ORIGINAL_OPEN_UNKNOWN",e);}
        }
        boolean usable(){return state.equals("OPEN_RETURNED")&&!closeAttempted;}
        int writeOnce(ByteBuffer data)throws IOException {job.requireOriginalWorker();if(reader||!usable())throw new IOException("ORIGINAL_NOT_WRITABLE");return handle.write(data);}
        int readOnce(ByteBuffer data)throws IOException {job.requireOriginalWorker();if(!reader||!usable())throw new IOException("ORIGINAL_NOT_READABLE");readCalls++;int n=handle.read(data);if(n>0)readBytes+=n;if(n==-1)eofCalls++;return n;}
        long position()throws IOException {job.requireOriginalWorker();return handle.position();}
        void position(long p)throws IOException {job.requireOriginalWorker();handle.position(p);}
        long size()throws IOException {job.requireOriginalWorker();return handle.size();}
        void forceOriginal()throws IOException {
            job.requireOriginalWorker();job.checkAdmission();
            if(reader||!usable()||forceAttempted)throw new IOException("ORIGINAL_FORCE_NOT_ADMITTED");
            forceAttempted=true;handle.force(true);forceReturned=true;
        }
        void captureSize()throws IOException {job.requireOriginalWorker();finalSize=handle.size();}
        void closeOriginalOnce()throws IOException {
            job.requireOriginalWorker();
            if(state.equals("REGISTERED_NOT_ALLOCATED"))return;
            if(closeAttempted)return; // no repeated native close, including UNKNOWN
            if(!state.equals("OPEN_RETURNED"))return; // allocation result unknown: retain
            closeAttempted=true;state="CLOSE_CALL_ENTERED";
            try {handle.close();closeReturned=true;state="CLOSE_RETURNED";job.nativeClosed();}
            catch(Throwable e){state="CLOSE_UNKNOWN";job.fail("ORIGINAL_CLOSE_UNKNOWN");throw new IOException("ORIGINAL_CLOSE_UNKNOWN",e);}
        }
        boolean returned(){return state.equals("REGISTERED_NOT_ALLOCATED")||closeReturned;}
        public int nativeWrite(ByteBuffer b)throws IOException{return writeOnce(b);}
        public long nativePosition()throws IOException{return position();}
        public void nativeSeek(long n)throws IOException{position(n);}
        public long nativeSize()throws IOException{return size();}
        public void nativeForce()throws IOException{forceOriginal();}
        public void nativeCloseOnce()throws IOException{closeOriginalOnce();}
        public boolean nativeUsable(){return usable();}
        public boolean originalReturned(){return returned();}
        Map<String,Object> receipt(){return ReceiptJson.map("ownerRegisteredBeforeOpen",true,"reader",reader,"state",state,
            "forceAttempted",forceAttempted,"forceReturned",forceReturned,"closeAttempted",closeAttempted,
            "sameOriginalCloseReturned",closeReturned,"finalSizeObservedBeforeClose",finalSize,"nativeReadCalls",readCalls,"nativeReadBytes",readBytes,"nativeEofCalls",eofCalls);}
    }

    static final class Job implements Runnable,AttemptBudgetChannel.Owner {
        final String scope;
        // These are the original owners, registered before worker/native creation.
        final FileOwner writer = new FileOwner(this,false), reader = new FileOwner(this,true);
        final AttemptBudgetChannel channel = new AttemptBudgetChannel(this);
        final WorkerDeadline waitState = new WorkerDeadline(System::nanoTime,DEADLINE_MS*1000000L);
        final List<Map<String,Object>> samples = new ArrayList<>();
        final List<Map<String,Object>> csd = new ArrayList<>();
        volatile Thread worker;
        volatile Object encoderOriginal, muxerOriginal;
        volatile boolean stopped, deadlineUnknown, bodyReturned, joined;
        volatile boolean rootCreated, directoryCreated, muxFinishReturned, outputReadOnly;
        volatile boolean encoderCreationReturned, muxCreationReturned, allocationUnknown;
        volatile boolean rawFileEof, packetDurationObserved;
        volatile String firstError, phase="REGISTERED", outputSha256;
        volatile long inputReserved, inputReturned, payloadBytes, rawOutputBytes, rawCsdObservedBytes;
        volatile int nativeOwnersLive, nativeOwnersPeak;
        volatile long actualTrackDurationUnits = -1;
        Job(String scope){this.scope=scope;}
        public synchronized void fail(String code){if(firstError==null)firstError=code;stopped=true;}
        synchronized void deadline(){deadlineUnknown=true;waitState.forceUnknown();fail("DEADLINE_UNKNOWN_ORIGINAL_RETURN_PENDING");}
        synchronized void nativeOpened(){nativeOwnersLive++;nativeOwnersPeak=Math.max(nativeOwnersPeak,nativeOwnersLive);}
        synchronized void nativeClosed(){nativeOwnersLive--;}
        public void requireOriginalWorker()throws IOException {if(Thread.currentThread()!=worker)throw new IOException("ORIGINAL_WORKER_REQUIRED");}
        public void checkAdmission()throws IOException {if(stopped)throw new IOException("ADMISSION_CLOSED");}
        public AttemptBudgetChannel.NativePort nativePort(){return writer;}
        synchronized void reserveInput(int n)throws IOException {
            checkAdmission();if(n<0||inputReserved>INPUT_MAX-n){fail("INPUT_CUMULATIVE_LIMIT");throw new IOException("INPUT_CUMULATIVE_LIMIT");}inputReserved+=n;
        }
        boolean resourcesReturned(){return bodyReturned&&writer.returned()&&reader.returned();}
        private void prepareDirectory()throws IOException {
            checkAdmission();Path parent=ROOT.getParent();
            for(Path p=parent;p!=null;p=p.getParent()) {
                BasicFileAttributes a=Files.readAttributes(p,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
                if(!a.isDirectory()||a.isSymbolicLink()||a.isOther()||!p.toRealPath().equals(p))throw new IOException("CANONICAL_PARENT_REQUIRED");
            }
            // Fresh exclusive root, no fallback/reuse of any existing run folder.
            phase="ROOT_CREATE_ENTERED";Files.createDirectory(ROOT);rootCreated=true;checkAdmission();
            phase="DIRECTORY_CREATE_ENTERED";Files.createDirectory(DIRECTORY);directoryCreated=true;checkAdmission();
            if(!DIRECTORY.toRealPath().equals(DIRECTORY))throw new IOException("CANONICAL_NEW_DIRECTORY_REQUIRED");
        }
        private void frameEvidence(int i,VideoEncoder.EncodedFrame encoded)throws IOException {
            ByteBuffer raw=encoded.getData().duplicate();int size=raw.remaining();
            if(size<1||size>SAMPLE_MAX||payloadBytes>6L*SAMPLE_MAX-size||!encoded.isKeyFrame())throw new IOException("ACTUAL_AU_BOUND_OR_KEYFLAG");
            List<Map<String,Object>> nals=new ArrayList<>();
            List<ByteBuffer> units=H264Utils.splitFrame(raw.duplicate());
            if(units.size()>64)throw new IOException("NAL_OBSERVATION_LIMIT");
            boolean idr=false;
            for(ByteBuffer nal:units){
                if(!nal.hasRemaining())throw new IOException("EMPTY_NAL");
                int type=nal.get(nal.position())&31;idr|=type==5;
                if(type==7||type==8){rawCsdObservedBytes+=nal.remaining()+4;if(rawCsdObservedBytes>CSD_MAX)throw new IOException("RAW_CSD_CUMULATIVE_LIMIT");}
                nals.add(ReceiptJson.map("type",type,"bytes",nal.remaining(),"sha256",ReceiptJson.hash(nal)));
            }
            if(!idr)throw new IOException("ACTUAL_IDR_REQUIRED");
            payloadBytes+=size;
            samples.add(ReceiptJson.map("index",i,"ptsUnits",i,"timescale",5,"durationUnits",1,"ptsUs",i*200000L,
                "isKeyframe",encoded.isKeyFrame(),"actualIdrNalObserved",idr,"rawEncoderAnnexBBytes",size,
                "rawEncoderAnnexBSha256",ReceiptJson.hash(raw),"nals",nals,
                "actualExtractorRepresentation","NOT_RUN_REQUIRES_LATER_QUALIFICATION"));
        }
        private void csdEvidence(AbstractMP4MuxerTrack track)throws IOException {
            if(track.getEntries().size()!=1||!(track.getEntries().get(0) instanceof VideoSampleEntry))throw new IOException("ONE_VIDEO_ENTRY_REQUIRED");
            AvcCBox box=H264Utils.parseAVCC((VideoSampleEntry)track.getEntries().get(0));
            if(box==null||box.getNalLengthSize()!=4)throw new IOException("ACTUAL_AVCC_REQUIRED");
            int total=0;
            for(List<ByteBuffer> group:Arrays.asList(box.getSpsList(),box.getPpsList())) {
                if(group.isEmpty()||group.size()>16)throw new IOException("CSD_COUNT_LIMIT");
                String kind=group==box.getSpsList()?"SPS_PAYLOAD_WITHOUT_NAL_HEADER":"PPS_PAYLOAD_WITHOUT_NAL_HEADER";
                for(ByteBuffer b:group) {
                    total+=b.remaining()+5;
                    if(b.remaining()<1||total>CSD_MAX)throw new IOException("CSD_CUMULATIVE_LIMIT");
                    csd.add(ReceiptJson.map("kind",kind,"bytes",b.remaining(),"hex",ReceiptJson.hex(ReceiptJson.bytes(b)),"sha256",ReceiptJson.hash(b)));
                }
            }
            ByteBuffer annex=H264Utils.saveCodecPrivate(box.getSpsList(),box.getPpsList());
            if(annex.remaining()>CSD_MAX)throw new IOException("CSD_ANNEXB_LIMIT");
            csd.add(ReceiptJson.map("kind","LIBRARY_CONVERTED_ANNEXB_FROM_REAL_MUX_TRACK_AVCC","bytes",annex.remaining(),
                "hex",ReceiptJson.hex(ReceiptJson.bytes(annex)),"sha256",ReceiptJson.hash(annex),"nalLengthSize",box.getNalLengthSize(),
                "containerReopenOrMedia3Qualified",false));
        }
        private void outputDigest()throws Exception {
            checkAdmission();if(!writer.closeReturned)throw new IOException("WRITER_ORIGINAL_CLOSE_REQUIRED");
            if(!OUTPUT.toFile().setReadOnly())throw new IOException("READONLY_REQUIRED");outputReadOnly=true;
            reader.open();MessageDigest digest=MessageDigest.getInstance("SHA-256");byte[] block=new byte[AttemptBudgetChannel.BLOCK];
            try {
                long expected=reader.size();if(expected<1||expected>AttemptBudgetChannel.MAX_ATTEMPT)throw new IOException("OUTPUT_FILE_SIZE_LIMIT");
                long read=0;
                for(;;) {
                    int want=(int)Math.min(block.length,Math.max(1,expected-read));reserveInput(want);
                    int n=reader.readOnce(ByteBuffer.wrap(block,0,want));
                    if(n==-1){rawFileEof=true;break;}
                    if(n<1||n>want||read>expected-n)throw new IOException("OUTPUT_DIGEST_PROGRESS_OR_SIZE");
                    digest.update(block,0,n);read+=n;inputReturned+=n;
                }
                if(read!=expected)throw new IOException("OUTPUT_TRUNCATED");rawOutputBytes=read;outputSha256=ReceiptJson.hex(digest.digest());
            } finally {reader.closeOriginalOnce();}
        }
        @Override public void run() {
            try {
                prepareDirectory();phase="WRITER_OPEN";writer.open();checkAdmission();
                phase="ENCODER_CREATE";H264Encoder encoder=H264Encoder.createH264Encoder();encoderOriginal=encoder;encoderCreationReturned=true;
                encoder.setKeyInterval(1);encoder.setMotionSearchRange(0);checkAdmission();
                phase="MUX_CREATE";MP4Muxer mux=MP4Muxer.createMP4Muxer(channel,Brand.MP4);muxerOriginal=mux;muxCreationReturned=true;checkAdmission();
                MuxerTrack track=mux.addVideoTrack(Codec.H264,VideoCodecMeta.createSimpleVideoCodecMeta(new Size(256,144),ColorSpace.YUV420J));
                for(int i=0;i<6;i++) {
                    checkAdmission();phase="ENCODE_FRAME_"+i;reserveInput(55296);
                    Picture picture=Picture.create(256,144,ColorSpace.YUV420J);byte[][] planes=picture.getData();
                    if(planes.length!=3||planes[0].length!=36864||planes[1].length!=9216||planes[2].length!=9216)throw new IOException("YUV_LAYOUT");
                    for(int y=0;y<144;y++)for(int x=0;x<256;x++)planes[0][y*256+x]=(byte)((16+16*((x/16+y/16+i)%14))-128);
                    Arrays.fill(planes[1],(byte)0);Arrays.fill(planes[2],(byte)0);inputReturned+=55296;
                    VideoEncoder.EncodedFrame encoded=encoder.encodeFrame(picture,ByteBuffer.allocate(SAMPLE_MAX));checkAdmission();frameEvidence(i,encoded);
                    phase="ADD_FRAME_"+i;
                    // CodecMP4MuxerTrack performs wipePSinplace and encodeMOVPacket
                    // exactly once. Raw AnnexB was observed BEFORE this mutation.
                    track.addFrame(Packet.createPacket(encoded.getData(),i,5,1,i,FrameType.KEY,null));
                }
                checkAdmission();phase="MUX_FINISH";mux.finish();muxFinishReturned=true;
                AbstractMP4MuxerTrack actual=(AbstractMP4MuxerTrack)track;actualTrackDurationUnits=actual.getTrackTotalDuration();
                if(actualTrackDurationUnits!=6)throw new IOException("ACTUAL_TRACK_DURATION_UNITS");packetDurationObserved=true;
                csdEvidence(actual);checkAdmission();phase="WRITER_FORCE";channel.forceOriginal();writer.finalSize=channel.size();
                phase="WRITER_CLOSE";channel.close();checkAdmission();
                phase="READONLY_DIGEST";outputDigest();phase="GENERATION_BODY_COMPLETE_NOT_QUALIFIED";
            } catch(Throwable error) {if(phase.equals("ENCODER_CREATE")&&!encoderCreationReturned||phase.equals("MUX_CREATE")&&!muxCreationReturned)allocationUnknown=true;fail("GENERATION_API_OR_BUDGET_FAILED");}
            finally {
                // Same original worker, no concurrent close and no second native
                // close after CLOSE_UNKNOWN/OPEN_UNKNOWN. Unknown owners retained.
                try {reader.closeOriginalOnce();}catch(Throwable error){fail("READER_CLOSE_UNKNOWN");}
                try {channel.close();}catch(Throwable error){fail("WRITER_CLOSE_UNKNOWN");}
                bodyReturned=true;
                // Same worker, after every cleanup call and body state adoption.
                // This completion point is not substituted for actual Thread.join.
                waitState.bodyCompletedByOriginal();
            }
        }
        Map<String,Object> receipt(boolean pending) {
            String status=deadlineUnknown?"UNKNOWN_DEADLINE_NO_SUCCESS_UPGRADE":firstError!=null?"FAILED_OR_UNKNOWN":
                joined&&resourcesReturned()&&waitState.timelyAndJoined()?"GENERATED_CANDIDATE_NOT_QUALIFIED":"UNKNOWN_ORIGINAL_RETURN_PENDING";
            Map<String,Object> base=ReceiptJson.map("tool","D1_FIXTURE_TOOL02_FIX","scopeLabelNotAuthorization",scope,"status",status,
                "firstError",firstError,"phase",phase,"deadlineMs",DEADLINE_MS,"admissionClosed",stopped,
                "deadlineUnknownSticky",deadlineUnknown,"workerBodyCleanupCompleted",bodyReturned,"sameWorkerExternallyJoined",joined,
                "originalResourceOwnersReturned",resourcesReturned(),"writer",writer.receipt(),"reader",reader.receipt(),
                "directoryCreatedByThisRun",directoryCreated,"rootCreatedByThisRun",rootCreated,"directoryDeleted",false,
                "unknownOwnersStronglyRetained",!resourcesReturned()||!joined||deadlineUnknown||allocationUnknown,"allocationUnknown",allocationUnknown,"encoderCreationReturned",encoderCreationReturned,"muxCreationReturned",muxCreationReturned,"sourceOwnersMax",2,"nativeOwnersLive",nativeOwnersLive,"nativeOwnersPeak",nativeOwnersPeak,"queue",0,
                "inputAttemptedReserved",inputReserved,"inputActuallyObserved",inputReturned,"outputBudget",channel.receipt(!pending&&joined),
                "muxFinishReturned",muxFinishReturned,"outputReadOnly",outputReadOnly,"wholeOutputEof",rawFileEof,
                "outputBytes",rawOutputBytes,"outputSha256",outputSha256,"packetTimescaleDeclared",5,
                "actualMuxTrackDurationUnits",actualTrackDurationUnits,"packetDurationObserved",packetDurationObserved,"rawCsdObservedCumulativeBytes",rawCsdObservedBytes,
                "expectedPacketEndUs",1200000,"actualIndependentContainerDuration","NOT_RUN",
                "e6EmptyEosWritten",false,"futureRemuxEmptyEosUs",1200000,"qualifiedFixture",false,"media3Qualification","NOT_RUN",
                "platformIsolationOrPlayback","NOT_RUN","noForceKillInterruptSecondCloseOrRefund",true);
            // At the deadline the worker may still be mutating ArrayLists. Pending
            // receipt deliberately contains only volatile/locked owner fields.
            base.put("workerDeadline",waitState.receipt());
            if(!pending&&joined){base.put("sixRawEncoderSamples",samples);base.put("actualMuxTrackCsd",csd);}
            return base;
        }
    }

    private static void emit(Map<String,Object> value) {
        try {System.out.println(ReceiptJson.json(value));}
        catch(Throwable error){System.out.println("{\"status\":\"UNKNOWN_RECEIPT_LIMIT_OR_EMISSION_FAILURE\",\"qualifiedFixture\":false}");}
    }
    public static void main(String[] args)throws Exception {
        if(args.length!=2||!args[0].equals("--generate-six")||!args[1].matches("--scope=D1GEN01-[A-Z0-9_-]{1,32}"))
            throw new IllegalArgumentException("EXACT_REVIEWED_GENERATION_ARGUMENTS_REQUIRED");
        Job job=new Job(args[1].substring(8));
        if(!ORIGINAL.compareAndSet(null,job))throw new IllegalStateException("ORIGINAL_JOB_RETAINED");
        Thread worker=new Thread(job,"videokit-fixture-six-original");job.worker=worker;worker.setDaemon(false);
        job.waitState.begin(worker);
        try {worker.start();job.waitState.awaitBodyWindow();}
        catch(InterruptedException e){job.deadline();emit(job.receipt(true));return;}
        catch(Throwable error){job.fail("ORIGINAL_WORKER_START_OR_JOIN_UNKNOWN");emit(job.receipt(true));return;}
        if(job.waitState.observeUnknown()) {
            job.deadline();emit(job.receipt(true));
        }
        // Always join the same original, even if it completed before observation.
        try {job.waitState.joinSameOriginal();}
        catch(InterruptedException e){job.deadline();emit(job.receipt(true));return;}
        if(job.waitState.observeUnknown())job.deadline();
        job.joined=true;emit(job.receipt(false));
        if(!job.deadlineUnknown&&!job.allocationUnknown&&job.resourcesReturned()&&job.waitState.timelyAndJoined())ORIGINAL.compareAndSet(job,null);
    }
    private SixFrameDriver() { }
}
