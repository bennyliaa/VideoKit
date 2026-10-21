package com.videokit.spike.e4;
import java.io.*;import java.nio.file.*;import java.util.*;import java.util.concurrent.*;
/** Minimal socket-wire adaptation of E13F archive; one writer and the same E4Owned close contract. */
final class E13IArchive {
 interface IO{OutputStream open(Path p)throws Exception;}
 final Path root;final IO io;final ArrayBlockingQueue<byte[]> queue=new ArrayBlockingQueue<>(8);final List<E4Owned<OutputStream>> files=new CopyOnWriteArrayList<>();
 volatile boolean intentReturned,done,eof,bodyReturned,failed;volatile int exit=-999,offered,written;volatile Thread writer;volatile String failure="NONE";private E4Owned<OutputStream> raw;
 E13IArchive(Path p,IO i){root=p;io=i;}E13IArchive(Path p){this(p,f->Files.newOutputStream(f,StandardOpenOption.CREATE_NEW));}
 E4Owned<OutputStream> open(String n)throws Exception{E4Owned<OutputStream> f=new E4Owned<>(root.resolve(n),OutputStream::close);files.add(f);f.allocate(()->io.open(root.resolve(n)));return f;}
 void fixed(String n,String value)throws Exception{byte[] b=value.getBytes(java.nio.charset.StandardCharsets.UTF_8);if(b.length>1024)throw new IOException("I_METADATA_BOUND");E4Owned<OutputStream> f=open(n);try{f.original().write(b);}finally{f.close();}}
 void start(String intent)throws Exception{writer=new Thread(()->write(intent),"I-original-wire-writer");writer.setDaemon(true);writer.start();long d=System.nanoTime()+2_000_000_000L;while(!intentReturned&&!failed&&System.nanoTime()<d)Thread.sleep(2);if(!intentReturned)throw new IOException("I_INTENT_UNRETURNED_NO_CONNECT");}
 synchronized void append(byte[] b,int n){if(failed)return;if(offered+n>E13ISocket.WIRE_CAP||!queue.offer(Arrays.copyOf(b,n))){failed=true;failure="WIRE_ARCHIVE_BOUND_OR_WRITER_PENDING";return;}offered+=n;}
 void end(boolean actualEof,int code){eof=actualEof;exit=code;done=true;}
 void write(String intent){try{Files.createDirectories(root);fixed("intent.txt",intent);raw=open("original.wire");intentReturned=true;for(;;){byte[] b=queue.poll(20,TimeUnit.MILLISECONDS);if(b!=null){raw.original().write(b);written+=b.length;}if(done&&queue.isEmpty())break;}}catch(Throwable t){failed=true;failure=t.getClass().getName();}finally{if(raw!=null)try{raw.close();}catch(Throwable t){failed=true;failure="RAW_CLOSE_UNKNOWN";}try{fixed("facts.txt","eof="+eof+" protocolExit="+exit+" offered="+offered+" written="+written+" failed="+failed+" failure="+failure+" writerThreadReturned=false factsOwnCloseNotProven=true\n");}catch(Throwable t){failed=true;failure="FACTS_PERSISTENCE_UNKNOWN";}bodyReturned=true;try{E13ReturnEvents.returned();}catch(Throwable t){failed=true;failure="TAIL_NOTIFICATION_FAILED";}}}
 boolean resourcesReturned(){Thread t=writer;if(t==null||t==Thread.currentThread()||t.isAlive()||!bodyReturned)return false;try{t.join();}catch(InterruptedException e){Thread.currentThread().interrupt();return false;}for(E4Owned<?> f:files)if(!f.returned())return false;return true;}
}
