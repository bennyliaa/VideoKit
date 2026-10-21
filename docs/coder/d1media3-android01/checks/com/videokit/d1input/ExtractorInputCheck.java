package com.videokit.d1input;
import androidx.media3.extractor.DefaultExtractorInput;import androidx.media3.datasource.DataSpec;
import java.io.*;import java.util.*;import java.util.concurrent.atomic.*;
import static com.videokit.d1input.InputSinkCheck.*;
/** Executes the REAL DefaultExtractorInput through real DataSource/readAt. These
 * raw non-media fixtures prove reading boundaries, NEVER MP4 structure validity. */
public final class ExtractorInputCheck {
 static void basics()throws Exception {
  Source s=new Source(7L);s.chunk=3;HostInputFactory f=factory(s);HostDataSource ds=f.createDataSource();long n=ds.open(new DataSpec(f.uri()));DefaultExtractorInput input=new DefaultExtractorInput(ds,0,n);byte[] b=new byte[7];
  input.readFully(b,0,7);for(int i=0;i<7;i++)need(b[i]==value(i),"actual exact bytes");need(input.getPosition()==7&&input.getLength()==7&&!input.readFully(new byte[1],0,1,true),"real input EOF and length");need(s.offsets.equals(List.of(0L,3L,6L)),"real readAt shortread offsets");close(ds,f);pass("M01_REAL_DefaultExtractorInput_shortread_known_EOF");
  s=new Source(null);s.chunk=2;f=factory(s);ds=f.createDataSource();n=ds.open(new DataSpec(f.uri()));input=new DefaultExtractorInput(ds,0,n);need(input.getLength()==-1,"unknown remains unknown");try{input.readFully(new byte[6],0,6);throw new AssertionError("truncation accepted");}catch(EOFException expected){}close(ds,f);pass("M02_REAL_DefaultExtractorInput_unknown_truncated_readFully");
 }
 static void seek()throws Exception {
  Source s=new Source(7L);HostInputFactory f=factory(s);HostDataSource ds=f.createDataSource();ds.open(new DataSpec(f.uri()));DefaultExtractorInput input=new DefaultExtractorInput(ds,0,7);byte[] b=new byte[1];input.readFully(b,0,1);ds.close();long n=ds.open(new DataSpec(f.uri(),5,-1));input=new DefaultExtractorInput(ds,5,5+n);input.readFully(b,0,1);need(b[0]==value(5)&&input.getPosition()==6&&input.getLength()==7,"same admitted source actual range reopen");ds.close();int opens=s.opens.get();HostDataSource d=ds;HostInputFactory ff=f;rejected(()->d.open(new DataSpec(ff.uri(),Long.MAX_VALUE,2)),"INVALID_RANGE");need(s.opens.get()==opens,"overflow before host open");close(ds,f);pass("M03_REAL_DefaultExtractorInput_position_reopen_NOT_SeekMap");
 }
 static void cancel()throws Exception {
  Source s=new Source(7L);s.holdRead=true;s.holdClose=true;HostInputFactory f=factory(s);HostDataSource ds=f.createDataSource();ds.open(new DataSpec(f.uri()));DefaultExtractorInput input=new DefaultExtractorInput(ds,0,7);byte[] target=new byte[]{9,9};AtomicReference<Throwable> error=new AtomicReference<>();Thread original=new Thread(()->{try{input.readFully(target,0,2);}catch(Throwable e){error.set(e);}},"container-real-input-caller");original.start();await(()->s.delayed!=null);ds.close();original.join(3000);need(!original.isAlive()&&error.get() instanceof IOException,"actual synchronous original caller joined");need(!f.originalsReturned()&&target[0]==9,"same bridge original delayed; caller buffer untouched");s.completeRead(2);need(!f.originalsReturned(),"close original remains pending");s.closeAck.complete(null);f.close();need(f.awaitOriginalReturns(5000)&&Arrays.equals(target,new byte[]{9,9}),"original read/close/runtime workers joined");pass("M04_REAL_DefaultExtractorInput_cancel_late_originals");
 }
 static void admissionAndHostBoundary()throws Exception {
  Source s=new Source(7L);HostInputFactory f=factory(s);
  rejected(()->HostMp4Inspection.inspect(f,HostMp4Inspection.Container.MP4,false,-1,false),"MP4_CAPABILITY_UNSUPPORTED");
  rejected(()->HostMp4Inspection.inspect(f,null,true,-1,false),"MP4_CAPABILITY_UNSUPPORTED");
  rejected(()->HostMp4Inspection.inspect(f,HostMp4Inspection.Container.MP4,true,2000001,false),"MP4_SEEK_BOUNDS");
  need(s.opens.get()==0,"capability before source creation/open or actual parser construction");f.close();need(f.awaitOriginalReturns(5000),"admission owner returned");pass("M05_MP4_capability_scope_seek_rejection_before_open");
  MemSink h=new MemSink();TemporaryOutput output=new TemporaryOutput(h,false,WORKER,500);output.channel().write(java.nio.ByteBuffer.wrap(new byte[]{1,3,5,7}));output.channel().close();output.finishWriter();
  try{output.inspectHostMp4Structure(HostMp4Inspection.Container.FRAGMENTED_MP4);throw new AssertionError("non-media host fixture accepted");}catch(IOException expected){need(!output.validationAcknowledged()&&!output.readyAcknowledged()&&!output.committed()&&h.readies==0&&h.commits==0,"platform/structure failure never grants isolated validation/READY/COMMIT");System.out.println("OBSERVE actual host inspection failure="+expected.getMessage()+"; MP4 structure runtime remains NOT_RUN on baseline JDK");}
  rejected(output::markReady,"OUTPUT_NOT_VALIDATABLE");need(output.abort()&&output.returned(),"same host/observer/coordinator originals joined");pass("M06_actual_host_inspection_failure_no_READY_originals_return");
 }
 static void cumulativeBudget()throws Exception {
  Source s=new Source(HostMp4Inspection.INPUT_LIMIT+1);HostInputFactory f=factory(s);HostDataSource ds=f.createDataSource();long len=ds.open(new DataSpec(f.uri()));HostMp4Inspection.Reader reader=new HostMp4Inspection.Reader(ds);DefaultExtractorInput input=new DefaultExtractorInput(reader,0,len);byte[] block=new byte[65536];
  try{for(int i=0;i<128;i++)need(input.read(block,0,block.length)==65536,"bounded genuine input chunk");int calls=s.offsets.size();rejected(()->input.read(block,0,1),"MP4_INPUT_BYTE_BUDGET");need(reader.readBytes==8388608&&input.getPosition()==8388608&&s.offsets.size()==calls&&calls==128,"no speculative byte/host call after cumulative8MiB");}finally{close(ds,f);}pass("M07_cumulative8MiB_rejected_BEFORE_next_original_read");
 }
 public static void main(String[] args)throws Exception{
  System.out.println("REAL_EXTRACTOR_INPUT_ORIGIN="+DefaultExtractorInput.class.getProtectionDomain().getCodeSource().getLocation());System.out.println("ADAPTER_ORIGIN="+HostMp4Inspection.class.getProtectionDomain().getCodeSource().getLocation());basics();seek();cancel();admissionAndHostBoundary();cumulativeBudget();need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0,"actual keepers zero");System.out.println("DONE seven boundary groups; real MP4 parse/mux/decode=NOT_RUN; raw read fixtures not media validation");
 }
}
