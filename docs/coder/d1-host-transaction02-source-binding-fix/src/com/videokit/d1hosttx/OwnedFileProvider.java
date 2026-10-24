package com.videokit.d1hosttx;

import com.videokit.spike.c14.AsyncReadBridge;
import java.io.*;import java.nio.*;import java.nio.channels.*;import java.nio.file.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;

/** Real readAt/file handles behind the original bridge, shared per-source read gate. */
public final class OwnedFileProvider implements AsyncReadBridge.Provider {
 private final Path file;private final FileIdentity fileIdentity;private final List<Handle> originals=new CopyOnWriteArrayList<>();private final AtomicBoolean reading=new AtomicBoolean();
 public final CountDownLatch readEntered=new CountDownLatch(1),allowLateRead=new CountDownLatch(1);private final boolean holdRead;
 public volatile long readRequested,readActual;public volatile boolean unknown;public volatile int closeCalls;
 public OwnedFileProvider(Path p,boolean hold)throws IOException{this(p,hold,FileIdentity.capture(p));}
 OwnedFileProvider(Path p,boolean hold,FileIdentity originalIdentity)throws IOException{file=p;fileIdentity=originalIdentity;fileIdentity.requireSame(p);holdRead=hold;}
 public CompletionStage<AsyncReadBridge.Handle> open(AsyncReadBridge.Cancellation cancel){
  if(originals.size()>=2)return failed("SOURCE_RESOURCE_EXHAUSTED");
  Handle h=new Handle();originals.add(h);
  try{fileIdentity.requireSame(file);h.original=FileChannel.open(file,StandardOpenOption.READ);fileIdentity.requireSame(file);return CompletableFuture.completedFuture(h);}
  catch(Throwable e){unknown=true;return failed("SOURCE_IO_FAILED");}
 }
 final class Handle implements AsyncReadBridge.Handle {
  FileChannel original;boolean closeEntered,closeReturned;CompletableFuture<Void> closeResult;
  public Long length(){try{return original.size();}catch(IOException e){return null;}}
  public CompletionStage<Integer> readAt(long at,byte[] b,int off,int count,AsyncReadBridge.Cancellation cancel){
   if(count<1||count>65536||at<0||!reading.compareAndSet(false,true))return failed("READ_IN_FLIGHT");
   try{readRequested+=count;int n=original.read(ByteBuffer.wrap(b,off,count),at);if(n>0)readActual+=n;readEntered.countDown();
    if(holdRead&&!allowLateRead.await(3000,TimeUnit.MILLISECONDS)){unknown=true;return failed("SOURCE_ORIGINAL_PENDING");}
    return CompletableFuture.completedFuture(n);
   }catch(Throwable e){unknown=true;return failed("SOURCE_IO_FAILED");}finally{reading.set(false);}
  }
  public synchronized CompletionStage<Void> closeAsync(){
   if(closeEntered)return closeResult;closeEntered=true;closeCalls++;closeResult=new CompletableFuture<>();
   try{original.close();closeReturned=true;closeResult.complete(null);}catch(Throwable e){unknown=true;closeResult.completeExceptionally(e);}return closeResult;
  }
 }
 public boolean originalsReturned(){return !unknown&&!reading.get()&&originals.stream().allMatch(h->h.closeReturned);}
 public int opened(){return originals.size();}
 public void requireOriginalFile(Path actual)throws IOException {if(!file.equals(actual))throw new IOException("SOURCE_IDENTITY_REJECTED");fileIdentity.requireSame(actual);}
 public void requireMovedOriginal(Path actual)throws IOException {fileIdentity.requireSame(actual);}
 private static <T>CompletableFuture<T> failed(String code){CompletableFuture<T> f=new CompletableFuture<>();f.completeExceptionally(new IOException(code));return f;}
}
