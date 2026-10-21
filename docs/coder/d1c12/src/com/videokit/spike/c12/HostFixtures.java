package com.videokit.spike.c12;

import java.io.*;
import java.nio.charset.*;
import java.nio.file.*;
import java.util.concurrent.*;

/** Host/test adapter; paths never appear in SDK source descriptors or broker parcels. */
public final class HostFixtures {
    public static AsyncReadBridge.Provider file(Path path){return cancel->{
        try{if(cancel.cancelled())throw new IOException("CANCELLED");return CompletableFuture.completedFuture(new FileHandle(path));}
        catch(IOException e){return failed(e);}
    };}
    static <T>CompletableFuture<T> failed(Throwable e){CompletableFuture<T> f=new CompletableFuture<>();f.completeExceptionally(e);return f;}
    private static final class FileHandle implements AsyncReadBridge.Handle {
        private final RandomAccessFile file;private final long length;private boolean closed;
        FileHandle(Path path)throws IOException{file=new RandomAccessFile(path.toFile(),"r");length=file.length();}
        public Long length(){return length;}
        public synchronized CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){
            try{if(closed || c.cancelled())throw new IOException("CANCELLED");file.seek(p);return CompletableFuture.completedFuture(file.read(b,o,n));}catch(IOException e){return failed(e);}
        }
        public synchronized CompletionStage<Void> closeAsync(){try{if(!closed){closed=true;file.close();}return CompletableFuture.completedFuture(null);}catch(IOException e){return failed(e);}}
    }
    public static AsyncReadBridge.Provider srt(Path path){return srt(path,stage->{});}
    public static AsyncReadBridge.Provider srt(Path path,java.util.function.Consumer<String> log){return cancel->{
        try{
            log.accept("SUBTITLE_OPEN_BEGIN");if(cancel.cancelled())throw new IOException("CANCELLED");if(Files.size(path)>1024*1024)throw new IOException("SUBTITLE_SIZE_EXCEEDED");
            byte[] raw=Files.readAllBytes(path);if(cancel.cancelled())throw new IOException("CANCELLED");log.accept("SUBTITLE_BYTES_READ");String text;
            try{text=StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(java.nio.ByteBuffer.wrap(raw)).toString();}
            catch(CharacterCodingException e){log.accept("SUBTITLE_GB18030_DECODE");text=Charset.forName("GB18030").newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(java.nio.ByteBuffer.wrap(raw)).toString();}
            if(text.startsWith("\ufeff"))text=text.substring(1);
            byte[] utf8=text.getBytes(StandardCharsets.UTF_8);
            if(utf8.length>3*1024*1024)throw new IOException("SUBTITLE_SIZE_EXCEEDED");
            log.accept("SUBTITLE_UTF8_READY");return CompletableFuture.completedFuture(memory(utf8));
        }catch(IOException e){return failed(e);}
    };}
    public static AsyncReadBridge.Handle memory(byte[] bytes){return new AsyncReadBridge.Handle(){
        private boolean closed;public Long length(){return (long)bytes.length;}
        public synchronized CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){
            if(closed || c.cancelled())return failed(new IOException("CANCELLED"));if(p>=bytes.length)return CompletableFuture.completedFuture(-1);
            int count=Math.min(n,bytes.length-(int)p);System.arraycopy(bytes,(int)p,b,o,count);return CompletableFuture.completedFuture(count);
        }
        public synchronized CompletionStage<Void> closeAsync(){closed=true;return CompletableFuture.completedFuture(null);}
    };}
}
