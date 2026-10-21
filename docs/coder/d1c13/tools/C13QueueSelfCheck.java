package com.videokit.spike.c13;
import java.io.*;
import java.nio.*;
import java.util.concurrent.*;
public final class C13QueueSelfCheck {
    static int checks;static void yes(boolean value){if(!value)throw new AssertionError("case "+checks);checks++;}
    public static void main(String[] args)throws Exception {
        BoundedFrameQueue<Integer> q=new BoundedFrameQueue<>();q.offer(1,100);q.offer(2,100);yes(q.snapshot().queued==2 && q.snapshot().peak==2);try{q.offer(3,20);throw new AssertionError();}catch(IOException expected){yes(expected.getMessage().equals("PIPE_FRAME_QUEUE_FULL"));}yes(q.snapshot().offers==0);
        BoundedFrameQueue<Integer>.Lease held=q.take(100);yes(held.value()==1);yes(q.snapshot().consumers==1);q.cancel();yes(q.snapshot().queued==0);yes(!q.snapshot().released());held.close();held.close();yes(q.snapshot().released());
        BoundedFrameQueue<Integer> normal=new BoundedFrameQueue<>();normal.offer(1,100);normal.finish();try(BoundedFrameQueue<Integer>.Lease value=normal.take(100)){yes(value.value()==1);}yes(normal.take(100)==null);yes(normal.snapshot().released());
        BoundedFrameQueue<Integer> pending=new BoundedFrameQueue<>();pending.offer(1,100);pending.offer(2,100);ExecutorService thread=Executors.newSingleThreadExecutor();try{Future<?> offer=thread.submit(()->{try{pending.offer(3,500);throw new AssertionError();}catch(IOException expected){if(!expected.getMessage().equals("PIPE_CANCELLED"))throw new AssertionError(expected);}catch(InterruptedException error){throw new AssertionError(error);}});long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(1);while(pending.snapshot().offers==0 && System.nanoTime()<deadline)Thread.yield();yes(pending.snapshot().offers==1);pending.cancel();offer.get(1,TimeUnit.SECONDS);yes(pending.snapshot().released());}finally{thread.shutdownNow();}
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();BoundedOutputChannel out=new BoundedOutputChannel(bytes);ByteBuffer data=ByteBuffer.allocate(PipelineRules.MAX_OUTPUT);yes(out.write(data)==PipelineRules.MAX_OUTPUT);yes(out.bytes()==PipelineRules.MAX_OUTPUT);try{out.write(ByteBuffer.wrap(new byte[1]));throw new AssertionError();}catch(IOException expected){yes(expected.getMessage().equals("PIPE_OUTPUT_BYTE_BUDGET"));}yes(bytes.size()==PipelineRules.MAX_OUTPUT);out.close();yes(!out.isOpen());
        BoundedOutputChannel failed=new BoundedOutputChannel(new OutputStream(){public void write(int b)throws IOException{throw new IOException("partial");}public void write(byte[] b,int o,int n)throws IOException{throw new IOException("partial");}});try{failed.write(ByteBuffer.wrap(new byte[20000]));throw new AssertionError();}catch(IOException expected){checks++;}yes(failed.bytes()==16384);failed.close();
        BoundedOutputChannel close=new BoundedOutputChannel(new OutputStream(){public void write(int n){}public void close()throws IOException{throw new IOException("close failed");}});try{close.close();throw new AssertionError();}catch(IOException expected){checks++;}yes(close.isOpen());
        System.out.println("PASS "+checks+" queue-full/inflight-cancel/physical-wakeup/writer-cap/failed-close counterexamples; actual codec/FD/device NOT_RUN");
    }
}
