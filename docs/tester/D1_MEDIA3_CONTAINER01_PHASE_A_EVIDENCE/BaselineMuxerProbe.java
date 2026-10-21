import com.videokit.d1input.*;import com.videokit.spike.c14.*;import androidx.media3.muxer.*;
import java.io.*;import java.nio.*;import java.util.concurrent.*;
/** Existing approved muxer only; no extractor execution or invented compressed AVC. */
public class BaselineMuxerProbe {
 static class MemoryHost implements HostOutput {
  ByteArrayOutputStream bytes=new ByteArrayOutputStream();int writes,closes,flushes,readyCalls,abortCalls,queryCalls;boolean closed;SinkCoordinator.HostState terminal=SinkCoordinator.HostState.WRITING;
  public String opaqueTask(){return "phaseA_existing_muxer_probe";}public Capabilities capabilities(){return new Capabilities(true,false,true,true,true);}
  public CompletionStage<Integer> writeAt(long p,byte[] b,int o,int n){if(p!=bytes.size()||n>65536)throw new AssertionError("bounded sequential write");writes++;bytes.write(b,o,n);return CompletableFuture.completedFuture(n);}
  public CompletionStage<Void> flush(){flushes++;return CompletableFuture.completedFuture(null);}public CompletionStage<Void> closeWriter(){closes++;closed=true;return CompletableFuture.completedFuture(null);}
  public boolean originalOperationsReturned(){return true;}public boolean writerOriginalsReturned(){return closed;}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){throw new AssertionError("no structure claim without fixture");}
  public CompletionStage<String> markReady(String id){readyCalls++;throw new AssertionError("phase A must not READY");}
  public CompletionStage<Void> abort(String id){abortCalls++;terminal=SinkCoordinator.HostState.ABORTED;return CompletableFuture.completedFuture(null);}
  public CompletionStage<SinkCoordinator.Status> query(String id){queryCalls++;return CompletableFuture.completedFuture(new SinkCoordinator.Status(terminal,null));}
 }
 static void bad(int track,int count,long last)throws Exception{try{E6Muxer.finish(null,track,count,last);throw new AssertionError("invalid E6 tuple accepted");}catch(IOException e){if(!e.getMessage().equals("E6_MUX_INCOMPLETE"))throw e;System.out.println("PASS frozen_E6_guard track="+track+" count="+count+" last="+last);}}
 public static void main(String[] args)throws Exception {
  System.out.println("ORIGIN E6="+E6Muxer.class.getProtectionDomain().getCodeSource().getLocation()+" muxer="+FragmentedMp4Muxer.class.getProtectionDomain().getCodeSource().getLocation());
  bad(-1,6,0);bad(0,5,0);bad(0,7,0);bad(0,6,-1);bad(0,6,2000001);
  MemoryHost h=new MemoryHost();TemporaryOutput s=new TemporaryOutput(h,false,()->{},500);FragmentedMp4Muxer original=null;String result="NOT_ATTEMPTED",close="NOT_CREATED";
  try{original=E6Muxer.create(s.channel());result="REAL_MUXER_CONSTRUCTOR_RETURNED_NO_TRACK_OR_SAMPLE";}
  catch(LinkageError e){result="HOST_PLATFORM_LINKAGE_BLOCKED "+e.getClass().getSimpleName()+":"+e.getMessage();}
  catch(Throwable e){result="REAL_MUXER_CONSTRUCTOR_FAILED "+e.getClass().getSimpleName()+":"+e.getMessage();}
  finally{
   if(original!=null){try{original.close();close="ORIGINAL_CLOSE_RETURNED_NO_TRACK";}catch(Throwable e){close="ORIGINAL_CLOSE_FAILED "+e.getClass().getSimpleName()+":"+e.getMessage();}}
   long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(2);while(!s.returned()){try{s.abort();}catch(IOException e){if(!e.getMessage().equals("OUTPUT_ORIGINAL_PENDING"))throw e;}if(System.nanoTime()>end)throw new AssertionError("same original owner pending");if(!s.returned())Thread.sleep(2);}
  }
  if(h.readyCalls!=0||!s.returned()||TemporaryOutput.retained()!=0||HostInputFactory.admittedSources()!=0||h.bytes.size()>TemporaryOutput.MAX_OUTPUT)throw new AssertionError("phase A boundary");
  System.out.println("RUNTIME "+result+" close="+close+" emittedBytes="+h.bytes.size()+" writes="+h.writes+" closes="+h.closes+" READY="+h.readyCalls+" COMMIT=NOT_RUN originalOwnerReturned="+s.returned());
  System.out.println("DONE phaseA_baseline_guardCases=5 realEncodedFixture=ABSENT realExtraction=NOT_RUN structureValidation=NOT_RUN sourceKeepers0 outputKeepers0");
 }
}
