package com.videokit.spike.c13;
import java.io.*;
import java.nio.*;
import java.nio.channels.*;
/** Sequential hard byte cap includes muxer headers/finalization, not only encoded samples. */
public final class BoundedOutputChannel implements WritableByteChannel {
    private final OutputStream stream;private boolean open=true;private long bytes;private final byte[] scratch=new byte[16384];
    public BoundedOutputChannel(OutputStream stream){this.stream=stream;}
    public synchronized int write(ByteBuffer input)throws IOException{if(!open)throw new ClosedChannelException();int count=input.remaining();if(count>PipelineRules.MAX_OUTPUT-bytes)throw new IOException("PIPE_OUTPUT_BYTE_BUDGET");while(input.hasRemaining()){int n=Math.min(input.remaining(),scratch.length);input.get(scratch,0,n);bytes+=n;stream.write(scratch,0,n);}return count;}
    public synchronized long bytes(){return bytes;}public synchronized boolean isOpen(){return open;}
    public synchronized void close()throws IOException{if(open){stream.close();open=false;}}
}
