package com.videokit.d1input;
import android.net.Uri;import androidx.media3.datasource.*;import java.io.*;import java.util.concurrent.atomic.AtomicBoolean;

/** Real Media3 DataSource. Synchronous methods require a worker; cancel is metadata-only intent.
 * Provider writes go to the original bridge private buffer and then this range scratch, never a late caller buffer. */
public final class HostDataSource implements DataSource {
 private final java.util.List<TransferListener> listeners=new java.util.ArrayList<>(4);private DataSpec activeSpec;
 private final HostInputFactory owner;private final AtomicBoolean cancelled=new AtomicBoolean();private volatile HostInputFactory.Range range;
 private volatile Uri uri;private boolean opening,started,reading,eof;private long serial,position,remaining;
 HostDataSource(HostInputFactory owner){this.owner=owner;}
 public synchronized void addTransferListener(TransferListener l){java.util.Objects.requireNonNull(l);if(listeners.contains(l))return;if(listeners.size()>=4)throw new IllegalStateException("FINITE_TRANSFER_LISTENER_BUDGET");listeners.add(l);}
 private void transferInitializing(DataSpec s){for(TransferListener l:java.util.List.copyOf(listeners))l.onTransferInitializing(this,s,false);}
 private void transferStarted(DataSpec s){activeSpec=s;for(TransferListener l:java.util.List.copyOf(listeners))l.onTransferStart(this,s,false);}
 private void bytesTransferred(int n){for(TransferListener l:java.util.List.copyOf(listeners))l.onBytesTransferred(this,activeSpec,false,n);}
 private void transferEnded(){DataSpec s=activeSpec;activeSpec=null;for(TransferListener l:java.util.List.copyOf(listeners))l.onTransferEnd(this,s,false);}
 public long open(DataSpec spec)throws IOException {
  owner.worker.requireWorker();long ticket;
  synchronized(this){if(opening||started||range!=null)throw new IOException("SOURCE_ALREADY_OPEN");if(!owner.opaqueUri.equals(spec.uri)||spec.httpMethod!=DataSpec.HTTP_METHOD_GET||spec.httpBody!=null||!spec.httpRequestHeaders.isEmpty())throw new IOException("OPAQUE_READ_ONLY_SOURCE_REQUIRED");if(spec.position<0||spec.length< -1)throw bounds();try{Math.addExact(spec.uriPositionOffset,spec.position);if(spec.length>=0)Math.addExact(spec.position,spec.length);}catch(ArithmeticException e){throw bounds();}opening=true;cancelled.set(false);ticket=++serial;}
  HostInputFactory.Range r=null;
  try{transferInitializing(spec);r=owner.range();synchronized(this){if(ticket!=serial||cancelled.get())throw new IOException("CANCELLED");range=r;}long length=r.consumer.open(r.group.identity,spec.position,spec.length);
   synchronized(this){if(ticket!=serial||cancelled.get())throw new IOException("CANCELLED");position=spec.position;remaining=length;eof=length==0;opening=false;started=true;uri=owner.opaqueUri;transferStarted(spec);return spec.length>=0?spec.length:length;}
  }catch(Throwable failure){if(r!=null)r.consumer.close();synchronized(this){if(serial==ticket){opening=false;range=null;uri=null;if(started){started=false;try{transferEnded();}catch(Throwable ignored){}}}}if(failure instanceof DataSourceException)throw (DataSourceException)failure;IOException mapped=Failures.io(failure,"SOURCE_IO_FAILED");if("INVALID_RANGE".equals(mapped.getMessage()))throw bounds();throw mapped;}
 }
 public int read(byte[] target,int offset,int length)throws IOException {
  owner.worker.requireWorker();java.util.Objects.checkFromIndexSize(offset,length,target.length);HostInputFactory.Range r;long ticket;int count;
  synchronized(this){if(!started||cancelled.get())throw new IOException("SOURCE_NOT_OPEN");if(length==0)return 0;if(eof||remaining==0)return -1;if(reading)throw new IOException("READ_IN_FLIGHT");if(position==Long.MAX_VALUE)throw bounds();count=(int)Math.min(65536L,Math.min(length,Long.MAX_VALUE-position));reading=true;r=range;ticket=serial;}
  byte[] scratch=new byte[count];
  try{int n=r.consumer.read(r.group.identity,scratch,0,count);synchronized(this){if(ticket!=serial||!started||cancelled.get())throw new IOException("CANCELLED");if(n<0){eof=true;return -1;}if(remaining>=0&&n>remaining)throw new IOException("INVALID_READ_RESULT");System.arraycopy(scratch,0,target,offset,n);position=Math.addExact(position,n);if(remaining>=0)remaining-=n;bytesTransferred(n);return n;}}
  catch(Throwable failure){throw Failures.io(failure,"SOURCE_IO_FAILED");}finally{synchronized(this){if(serial==ticket)reading=false;}}
 }
 public Uri getUri(){return uri;}
 public void cancel(){cancelled.set(true);HostInputFactory.Range r=range;if(r!=null)r.consumer.close();}
 public void close()throws IOException {owner.worker.requireWorker();cancel();synchronized(this){serial++;opening=false;reading=false;range=null;uri=null;if(started){started=false;try{transferEnded();}catch(Throwable failure){throw Failures.io(failure,"SOURCE_IO_FAILED");}}}}
 private static DataSourceException bounds(){return new DataSourceException("INVALID_RANGE",DataSourceException.POSITION_OUT_OF_RANGE);}
}
