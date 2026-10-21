package com.videokit.d1input;
import com.videokit.d1android.*;import androidx.media3.datasource.DataSpec;
import java.io.*;import java.nio.file.*;import java.util.*;import static com.videokit.d1input.InputSinkCheck.*;
/** JDK checks of real shared admission/copy/identity code only. Instrumentation,
 * Android FD/fsync and real MP4 parsing are NOT executed or replaced here. */
public final class AndroidReadyCheck {
 static int cases;static void ok(String name){cases++;System.out.println("PASS android_ready_host "+name);}
 static Map<String,String> args(String method){return new HashMap<>(Map.of("case",method,"fixtureSha256",ExperimentContract.SAMPLE_SHA,"runId","D1MA01-HOSTCHECK-001"));}
 static void policy()throws Exception{
  for(ExperimentContract.Method m:ExperimentContract.Method.values())need(ExperimentContract.admit(args(m.name()))==m,"exact method admitted");
  for(String bad:new String[]{"class","path","uri","encoder"}){Map<String,String> a=args("inspectKnown");a.put(bad,"/not/allowed");rejected(()->ExperimentContract.admit(a),"EXPERIMENT_ARGUMENT_REJECTED");}
  Map<String,String> badHash=args("inspectKnown");badHash.put("fixtureSha256","0".repeat(64));rejected(()->ExperimentContract.admit(badHash),"EXPERIMENT_ARGUMENT_REJECTED");Map<String,String> last=args("inspectKnown");last.put("runId","../old-scope");rejected(()->ExperimentContract.admit(last),"EXPERIMENT_ARGUMENT_REJECTED");rejected(()->ExperimentContract.admit(args("decodeAndPlay")),"EXPERIMENT_METHOD_REJECTED");
  need(ExperimentContract.qualifiedFixture()==null,"approved read sample cannot obtain encoded fixture registration");need(ExperimentContract.METHOD_DEADLINE_MS==60000&&ExperimentContract.RECEIPT_UTF8_MAX==262144,"frozen method and receipt caps");ok("exact_arguments_no_path_encoder_playback_or_runtime_fixture_registration");
 }
 interface Wrap {InputStream open(InputStream original)throws Exception;}
 static void copy(Path original,Path out,Wrap wrap,String hash,String rejectedCode)throws Exception{
  final int[] writes={0};try(InputStream in=wrap.open(Files.newInputStream(original));OutputStream target=new FilterOutputStream(Files.newOutputStream(out,StandardOpenOption.CREATE_NEW)){public void write(byte[] b,int o,int n)throws IOException{need(n>0&&n<=65536,"actual copy writes bounded");out.write(b,o,n);writes[0]+=n;}}){
   try{VerifiedFixtureCopy.Receipt r=VerifiedFixtureCopy.copy(in,target,ExperimentContract.SAMPLE_BYTES,hash,()->false);need(rejectedCode==null&&r.fullEof&&r.bytes==349102&&r.sha256.equals(ExperimentContract.SAMPLE_SHA),"actual approved copy full EOF/hash");}catch(IOException e){need(rejectedCode!=null&&rejectedCode.equals(e.getMessage()),"copy reject:"+e.getMessage());}
  }need(writes[0]<=349102&&Files.size(out)<=349102,"no byte written beyond exact input scope");
 }
 static void copier(Path original,Path dir)throws Exception{
  copy(original,dir.resolve("known.bin"),in->in,ExperimentContract.SAMPLE_SHA,null);
  copy(original,dir.resolve("short.bin"),in->new FilterInputStream(in){public int read(byte[] b,int o,int n)throws IOException{return super.read(b,o,Math.min(7,n));}},ExperimentContract.SAMPLE_SHA,null);ok("approved_actual349102B_known_and_short7_copy_fullEOF_hash");
  copy(original,dir.resolve("truncated.bin"),in->new FilterInputStream(in){long remaining=349101;public int read(byte[] b,int o,int n)throws IOException{if(remaining==0)return -1;int got=super.read(b,o,(int)Math.min(n,remaining));if(got>0)remaining-=got;return got;}},ExperimentContract.SAMPLE_SHA,"FIXTURE_TRUNCATED");
  copy(original,dir.resolve("extra.bin"),in->new SequenceInputStream(in,new ByteArrayInputStream(new byte[]{9})),ExperimentContract.SAMPLE_SHA,"FIXTURE_EXCESS_BYTES");
  copy(original,dir.resolve("hash.bin"),in->in,"0".repeat(64),"FIXTURE_HASH_MISMATCH");ok("raw_copy_truncation_excess_hash_failure_no_parser_claim");
  final int[] reads={0};InputStream denied=new InputStream(){public int read(){reads[0]++;return 0;}};ByteArrayOutputStream sink=new ByteArrayOutputStream();rejected(()->VerifiedFixtureCopy.copy(denied,sink,349102,ExperimentContract.SAMPLE_SHA,()->true),"EXPERIMENT_ADMISSION_STOPPED");rejected(()->VerifiedFixtureCopy.copy(denied,sink,8388609,ExperimentContract.SAMPLE_SHA,()->false),"FIXTURE_SCOPE_REJECTED");need(reads[0]==0&&sink.size()==0,"stopped/overbudget rejected before read/write");ok("copy_stopped_and_budget_before_original_IO");
 }
 static void identities()throws Exception{
  Source host=new Source(73L);HostInputFactory f=factory(host);HostDataSource d=f.createDataSource();long remaining=d.open(new DataSpec(f.uri(),5,-1));HostMp4Inspection.RangeObservation one=new HostMp4Inspection.RangeObservation(f,5,remaining);need(one.position==5&&one.remaining==68&&one.absoluteEnd==73&&one.uid==7&&one.pid==8&&one.epoch==f.sourceIdentity().epoch&&one.generation==f.sourceSnapshot().generation&&one.sourceVersion.equals("fixture_v1"),"same actual original identity and absolute endpoint");d.close();host.size=null;remaining=d.open(new DataSpec(f.uri(),2,-1));HostMp4Inspection.RangeObservation two=new HostMp4Inspection.RangeObservation(f,2,remaining);need(two.absoluteEnd==-1&&two.epoch>one.epoch&&two.uid==one.uid&&two.sourceVersion.equals(one.sourceVersion),"new actual epoch, unknown remains unknown; old observation immutable");close(d,f);ok("real_SourceFactory_range_identity_epoch_and_unknown_observation");
  MemSink h=new MemSink();rejected(()->new TemporaryOutput(h,false,WORKER,500,-1,1),"OUTPUT_GRANT_INVALID");rejected(()->new TemporaryOutput(h,false,WORKER,500,1,0),"OUTPUT_GRANT_INVALID");need(TemporaryOutput.retained()==0&&h.writes==0,"bad host-supplied read identity before owner allocation");ok("reopen_identity_invalid_before_new_owner");
 }
 public static void main(String[] argv)throws Exception{Path parent=Path.of(argv[0]),original=Path.of(argv[1]);Path dir=Files.createTempDirectory(parent,"android-ready-");try{policy();copier(original,dir);identities();need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0,"same original keepers0");System.out.println("DONE hostReadinessCases="+cases+" Android_instrumentation_FD_fsync_parser_mux=NOT_RUN no_new_platform_standins=true");}finally{try(java.util.stream.Stream<Path> files=Files.list(dir)){for(Path p:(Iterable<Path>)files::iterator)Files.delete(p);}Files.delete(dir);}}
}
