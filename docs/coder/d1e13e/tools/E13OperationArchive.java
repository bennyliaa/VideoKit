package com.videokit.spike.e4;
import java.io.*;import java.nio.file.*;import java.util.*;import java.util.concurrent.*;
/** The original reader offers bounded blocks; this original writer owns all file calls. No replacement reader. */
public final class E13OperationArchive {
 public interface IO {OutputStream open(Path p)throws Exception;}
 private static final Set<E13OperationArchive> OWNERS=ConcurrentHashMap.newKeySet();
 private final ArrayBlockingQueue<byte[]> queue=new ArrayBlockingQueue<>(8);private final Path root;private final int cap;private final IO io;
 private volatile boolean eof,readerDone,writerReturned,failed,intentReturned,processStartReturned,exitObserved,pidRecorded;private volatile long childPid=-1,writerCallAt;private volatile int exit=-999;private int offered,written;private volatile String failure="NONE";private E4Owned<OutputStream> originalFile;private Thread writer;
 private final List<E4Owned<OutputStream>> files=new CopyOnWriteArrayList<>();
 public final String operation;
 public E13OperationArchive(Path root,String op,int cap){this(root,op,cap,p->Files.newOutputStream(p,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE));}
 E13OperationArchive(Path root,String op,int cap,IO io){this.root=root.resolve(op);operation=op;this.cap=cap;this.io=io;OWNERS.add(this);}
 public void start(String label,List<String> argv)throws Exception{writer=new Thread(()->write(label,argv),"e13-original-archive-"+operation);writer.setDaemon(true);writer.start();long end=System.nanoTime()+2000000000L;while(!intentReturned&&!failed&&System.nanoTime()<end)Thread.sleep(2);if(!intentReturned){failed=true;failure="ARCHIVE_INTENT_PENDING_OR_FAILED";readerDone=true;throw new IOException(failure);}}
 public void started(long pid){childPid=pid;processStartReturned=true;}
 public synchronized void append(byte[] b,int n){if(failed)return;if(offered+n>cap||writerCallAt!=0&&System.nanoTime()-writerCallAt>2000000000L||!queue.offer(Arrays.copyOf(b,n))){failed=true;failure="ARCHIVE_BOUND_OR_WRITE_PENDING";return;}offered+=n;}
 public void eof(){eof=true;}public void readerDone(){readerDone=true;}public void processExit(int code){exit=code;exitObserved=true;}
 private E4Owned<OutputStream> open(String name)throws Exception{E4Owned<OutputStream> f=new E4Owned<>(root.resolve(name),OutputStream::close);files.add(f);f.allocate(()->io.open(root.resolve(name)));return f;}
 private void fixed(String name,String text)throws Exception{byte[] bytes=text.getBytes(java.nio.charset.StandardCharsets.UTF_8);if(bytes.length>4096)throw new IOException("ARCHIVE_FIXED_RECORD_BOUND");E4Owned<OutputStream> f=open(name);try{f.original().write(bytes);}finally{f.close();}}
 private void write(String label,List<String> argv){
  try{Files.createDirectories(root);fixed("intent.txt","operation="+operation+"\nlabel="+label+"\nmaxRaw="+cap+"\nargv="+String.join("\n",argv)+"\n");originalFile=open("original.raw");intentReturned=true;
   for(;;){if(processStartReturned&&!pidRecorded){fixed("original-process.txt","operation="+operation+" childPid="+childPid+" actualStartReturned=true\n");pidRecorded=true;}byte[] b=queue.poll(20,TimeUnit.MILLISECONDS);if(b!=null){writerCallAt=System.nanoTime();originalFile.original().write(b);written+=b.length;writerCallAt=0;}if(readerDone&&queue.isEmpty()&&(exitObserved||failed&&!processStartReturned))break;}
  }catch(Throwable t){failed=true;failure=t.getClass().getName();}
  finally{if(originalFile!=null)try{originalFile.close();}catch(Throwable t){failed=true;failure="ARCHIVE_CLOSE_UNKNOWN";}
   try{fixed("archive-facts.txt",state());}catch(Throwable t){failed=true;failure="ARCHIVE_FACT_PERSISTENCE_FAILED";}
   writerReturned=true;if(resourcesReturned())OWNERS.remove(this);
   E13ReturnEvents.returned();
  }
 }
 public boolean resourcesReturned(){if(!writerReturned)return false;for(E4Owned<?> f:files)if(!f.returned())return false;return true;}public boolean failed(){return failed;}
 public String state(){return "operation="+operation+" startReturned="+processStartReturned+" childPid="+childPid+" originalExitObserved="+exitObserved+" originalExit="+exit+" readerEof="+eof+" readerDone="+readerDone+" offered="+offered+" written="+written+" archiveWriterReturned="+writerReturned+" archiveFilesReturned="+resourcesReturned()+" archiveFailed="+failed+" failure="+failure;}
}
