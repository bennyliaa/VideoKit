package com.videokit.spike;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

public final class ContractProbe {
    private static int passed;
    private static void check(boolean ok, String name) {
        if (!ok) throw new AssertionError(name);
        passed++; System.out.println("PASS " + name);
    }
    private static void error(String code, Callable<?> action) throws Exception {
        try { action.call(); throw new AssertionError("Expected " + code); }
        catch (IOException e) { check(code.equals(e.getMessage()), code); }
    }
    static class MemoryHandle implements ReadBridge.Handle {
        final byte[] bytes = {1,2,3,4,5}; boolean closed; int closes; boolean unknown;
        public Long length() { return unknown ? null : (long)bytes.length; }
        public int readAt(long at, byte[] b, int off, int n) throws IOException {
            if (closed) throw new IOException("SESSION_RELEASED");
            if (at >= bytes.length) return -1;
            int result = Math.min(2, Math.min(n, bytes.length - (int)at));
            System.arraycopy(bytes, (int)at, b, off, result); return result;
        }
        public void close() { if (!closed) { closed=true; closes++; } }
    }
    static class FileHandle implements ReadBridge.Handle {
        final RandomAccessFile file; final long size;
        FileHandle(Path path) throws IOException { file=new RandomAccessFile(path.toFile(), "r"); size=file.length(); }
        public Long length() { return size; }
        public synchronized int readAt(long at, byte[] b, int off, int n) throws IOException {
            file.seek(at); return file.read(b,off,n);
        }
        public void close() throws IOException { file.close(); }
    }
    static class Output implements SinkTransaction.Sink {
        final Path path; final String fault; final byte[] expected; OutputStream stream;
        int ready, abort, open; boolean random=true;
        Output(Path p,String f,byte[] bytes) {path=p;fault=f;expected=bytes;}
        public boolean randomWrite() { return random; }
        public void open() throws IOException {open++;stream=Files.newOutputStream(path);if(fault.equals("open"))throw new IOException("open");}
        public void write(byte[] data) throws IOException {stream.write(data);if(fault.equals("write"))throw new IOException("OUTPUT_SPACE_INSUFFICIENT");}
        public void flush() throws IOException {if(fault.equals("flush"))throw new IOException("flush");stream.flush();}
        public void close() throws IOException {if(stream!=null)stream.close();if(fault.equals("close"))throw new IOException("close");}
        public boolean validateReopened() throws IOException {return !fault.equals("validate") && Arrays.equals(expected,Files.readAllBytes(path));}
        public String markReady() throws IOException {ready++;if(fault.equals("ready-response"))throw new IOException("SOURCE_TIMEOUT");return "opaque-output-token";}
        public void abort() throws IOException {abort++;Files.deleteIfExists(path);}
    }
    public static void main(String[] args) throws Exception {
        Path project=Path.of(args[0]);Path outputs=Path.of(args[1]);Files.createDirectories(outputs);
        MemoryHandle m=new MemoryHandle();ReadBridge bridge=new ReadBridge(m);
        check(bridge.open(0,-1)==5,"known length");byte[] data=new byte[9];
        check(bridge.read(data,2,5)==2 && data[2]==1,"short read and target offset");
        check(bridge.read(data,0,5)==2 && bridge.read(data,0,5)==1 && bridge.read(data,0,5)==-1,"short reads reach EOF");
        final ReadBridge knownBridge=bridge;
        error("INVALID_RANGE",()->knownBridge.open(-1,-1));error("INVALID_RANGE",()->knownBridge.open(6,-1));
        bridge.close();bridge.close();check(m.closes==1 && bridge.awaitDrained(100),"idempotent release and drained");
        error("SESSION_RELEASED",()->knownBridge.read(data,0,1));
        m=new MemoryHandle();m.unknown=true;bridge=new ReadBridge(m);check(bridge.open(0,-1)==-1,"unknown length");
        while(bridge.read(data,0,9)!=-1){}bridge.close();check(true,"unknown-length EOF");
        ReadBridge disconnected=new ReadBridge(new MemoryHandle(){ public int readAt(long p,byte[] b,int o,int n)throws IOException{throw new IOException("SOURCE_DISCONNECTED");}});
        disconnected.open(0,-1);error("SOURCE_DISCONNECTED",()->disconnected.read(data,0,1));disconnected.close();
        ReadBridge zero=new ReadBridge(new MemoryHandle(){public int readAt(long p,byte[] b,int o,int n){return 0;}});
        zero.open(0,-1);error("INVALID_READ_RESULT",()->zero.read(data,0,1));zero.close();
        Path large=project.resolve("test_media/03_large_files/large_video_over_2GiB.mkv");
        try(ReadBridge real=new ReadBridge(new FileHandle(large));RandomAccessFile reference=new RandomAccessFile(large.toFile(),"r")) {
            long at=(1L<<31)+12345;real.open(at,64);byte[] got=new byte[64],expected=new byte[64];
            check(real.read(got,0,64)==64,"actual file offset above 2GiB");reference.seek(at);reference.readFully(expected);
            check(Arrays.equals(got,expected),"large-offset bytes match independent seek");
        }
        CountDownLatch entered=new CountDownLatch(1),stop=new CountDownLatch(1);
        ReadBridge blocking=new ReadBridge(new ReadBridge.Handle(){
            public Long length(){return null;}
            public int readAt(long p,byte[] b,int o,int n)throws IOException{entered.countDown();try{stop.await();}catch(InterruptedException e){throw new IOException("CANCELLED");} b[o]=99;return 1;}
            public void close(){stop.countDown();}
        });blocking.open(0,-1);byte[] untouched={7};ExecutorService worker=Executors.newSingleThreadExecutor();
        Future<?> inFlight=worker.submit(()->{try{blocking.read(untouched,0,1);throw new AssertionError("stale result");}catch(IOException e){if(!e.getMessage().equals("CANCELLED"))throw new RuntimeException(e);}});
        check(entered.await(2,TimeUnit.SECONDS),"worker I/O starts");long cancelStart=System.nanoTime();blocking.close();
        check(blocking.awaitDrained(1000),"cancel drains cooperative transport");inFlight.get(2,TimeUnit.SECONDS);worker.shutdownNow();
        check(untouched[0]==7,"stale result cannot mutate caller buffer");System.out.println("METRIC cooperative_cancel_ms="+(System.nanoTime()-cancelStart)/1000000.0);
        byte[] payload=Files.readAllBytes(project.resolve("test_media/imgs_and_videos/videos/sample.mp4"));
        Output good=new Output(outputs.resolve("copy-success.mp4"),"",payload);new SinkTransaction().run(good,payload,true);
        check(good.ready==1 && good.abort==0,"closed reopened byte-identical sample becomes ready (copy only)");
        for(String fault:List.of("open","write","flush","close","validate")) {
            Output bad=new Output(outputs.resolve(fault+".tmp"),fault,payload);
            try {new SinkTransaction().run(bad,payload,true);throw new AssertionError(fault);}catch(IOException expected){}
            check(bad.ready==0 && bad.abort==1 && !Files.exists(bad.path),"sink fault "+fault+" aborts without ready");
        }
        Output insufficient=new Output(outputs.resolve("unsupported.tmp"),"",payload);insufficient.random=false;
        error("OUTPUT_CAPABILITY_UNSUPPORTED",()->new SinkTransaction().run(insufficient,payload,true));check(insufficient.open==0,"preflight before open");
        SinkTransaction cancelled=new SinkTransaction();Output cancel=new Output(outputs.resolve("cancel.tmp"),"",payload){public void write(byte[] b)throws IOException{super.write(b);cancelled.cancel();}};
        error("CANCELLED",()->cancelled.run(cancel,payload,true));check(cancel.ready==0 && cancel.abort==1,"cancel never ready");
        Output uncertain=new Output(outputs.resolve("ready-unknown.mp4"),"ready-response",payload);
        error("OUTPUT_READY_UNKNOWN",()->new SinkTransaction().run(uncertain,payload,true));
        check(uncertain.ready==1 && uncertain.abort==0,"lost ready response requires status reconciliation, never blind abort");
        System.out.println("RESULT passed="+passed+" failed=0; platform codecs, native crash and tracking NOT_RUN");
    }
}
