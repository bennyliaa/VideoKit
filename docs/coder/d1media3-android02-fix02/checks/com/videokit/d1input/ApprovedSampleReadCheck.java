package com.videokit.d1input;
import androidx.media3.extractor.DefaultExtractorInput;import androidx.media3.datasource.DataSpec;import com.videokit.spike.c14.AsyncReadBridge;
import java.io.*;import java.nio.file.*;import java.security.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
import static com.videokit.d1input.InputSinkCheck.*;
/** Original approved sample is READ ONLY; raw input verification does not parse or decode MP4. */
public final class ApprovedSampleReadCheck {
 public static void main(String[] args)throws Exception {
  Path original=Path.of(args[0]);String expected=args[1];need(Files.size(original)<=HostMp4Inspection.INPUT_LIMIT,"finite approved fixture");
  for(boolean unknown:new boolean[]{false,true}){
   AtomicInteger opens=new AtomicInteger(),closes=new AtomicInteger(),maxBlock=new AtomicInteger();
   AsyncReadBridge.Provider provider=c->{try{RandomAccessFile file=new RandomAccessFile(original.toFile(),"r");opens.incrementAndGet();return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
    public Long length(){try{return unknown?null:file.length();}catch(IOException e){throw new UncheckedIOException(e);}}
    public CompletionStage<Integer> readAt(long at,byte[] b,int off,int len,AsyncReadBridge.Cancellation token){try{need(len<=65536,"physical max block");maxBlock.accumulateAndGet(len,Math::max);file.seek(at);return CompletableFuture.completedFuture(file.read(b,off,len));}catch(IOException e){return failed(e);}}
    public CompletionStage<Void> closeAsync(){try{file.close();closes.incrementAndGet();return CompletableFuture.completedFuture(null);}catch(IOException e){return failed(e);}}
   });}catch(IOException e){return failed(e);}};
   HostInputFactory f=new HostInputFactory(7,8,"approved_sample_read_v1",provider,WORKER);HostDataSource ds=f.createDataSource();long len=ds.open(new DataSpec(f.uri()));DefaultExtractorInput input=new DefaultExtractorInput(ds,0,len);MessageDigest md=MessageDigest.getInstance("SHA-256");byte[] b=new byte[65536];long count=0;int n;
   try{while((n=input.read(b,0,b.length))!=-1){md.update(b,0,n);count+=n;}need(input.getPosition()==Files.size(original)&&count==Files.size(original),"actual real input position and full EOF");StringBuilder hash=new StringBuilder();for(byte v:md.digest())hash.append(String.format("%02x",v&255));need(expected.equals(hash.toString()),"original manifest hash verified");System.out.println("PASS APPROVED_SAMPLE_READ_ONLY unknownLength="+unknown+" bytes="+count+" sha256="+hash+" actualDefaultExtractorInput=true MP4_parse_decode=NOT_RUN");}finally{close(ds,f);}
   need(opens.get()==1&&closes.get()==1&&maxBlock.get()<=65536&&HostInputFactory.admittedSources()==0,"original handle/runtime returned");
  }
 }
}
