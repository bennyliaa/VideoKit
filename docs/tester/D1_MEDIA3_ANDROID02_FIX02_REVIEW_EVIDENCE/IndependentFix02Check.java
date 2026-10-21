import com.videokit.d1android.*;
import com.videokit.spike.e4.E13ReturnEvents;
import com.android.apksig.ApkVerifier;
import java.io.*;import java.nio.charset.StandardCharsets;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;import java.security.*;

/** Tester-owned bounded typed ports. Does not load ExperimentJob, Android Os, or a media parser/muxer. */
public final class IndependentFix02Check {
 interface Checked{void run()throws Exception;}
 static int checks;static long payloadBytes;
 static void need(boolean b){if(!b)throw new AssertionError("INDEPENDENT_FIX02_ASSERT");}
 static void pass(String s){checks++;System.out.println("PASS "+s);}
 static void denied(Checked c)throws Exception{boolean denied=false;try{c.run();}catch(IOException e){denied=true;}need(denied);}
 static void joined(Thread t)throws Exception{t.join(2000);need(!t.isAlive());}
 static String payload(String s){payloadBytes+=s.getBytes(StandardCharsets.UTF_8).length;need(payloadBytes<=65536);return s;}
 static long value(Map<String,Object> m,String k){return ((Number)m.get(k)).longValue();}
 @SuppressWarnings("unchecked") static long count(ScopeMeter m,String p,String k){return ((Number)((Map<String,Object>)((Map<String,Object>)m.snapshot().get("phases")).get(p)).get(k)).longValue();}
 static void journal()throws Exception{
  ScopeJournal j=new ScopeJournal(512,1024,2048);List<String> expected=new ArrayList<>();
  for(int n=0;n<10;n++){String s=payload("{\"completedCase\":"+n+"}");expected.add(s);j.completed(s);}
  ScopeJournal.Snapshot full=j.snapshot();denied(()->j.completed(payload("{}")));need(j.snapshot().completed.equals(expected)&&j.snapshot().overflow);pass("journal_ten_case_limit_preserves_all_prior_values");
  try{full.completed.clear();throw new AssertionError();}catch(UnsupportedOperationException okay){}pass("published_history_list_is_immutable");
  ScopeJournal pending=new ScopeJournal(128,256,512);pending.completed(payload("{\"case\":\"done\"}"));ScopeJournal.Snapshot before=pending.snapshot();CountDownLatch entered=new CountDownLatch(1),tail=new CountDownLatch(1);AtomicReference<Throwable> error=new AtomicReference<>();
  Thread worker=new Thread(()->{try{pending.current(payload("{\"case\":\"second\",\"status\":\"PENDING\"}"));entered.countDown();need(tail.await(2,TimeUnit.SECONDS));pending.current(payload("{\"case\":\"second\",\"firstFailure\":\"IO_UNKNOWN\"}"));}catch(Throwable t){error.set(t);}},"tester-fix02-journal-original");worker.start();
  try{need(entered.await(2,TimeUnit.SECONDS));ScopeJournal.Snapshot s=pending.snapshot();need(s.completed.size()==1&&s.current.contains("PENDING")&&before.current.equals("{}"));pass("pending_receipt_reads_immutable_prior_history");}finally{tail.countDown();joined(worker);}
  need(error.get()==null&&pending.snapshot().completed.size()==1&&pending.snapshot().current.contains("IO_UNKNOWN")&&before.current.equals("{}"));pass("partial_failure_does_not_reexecute_or_drop_completed_case");
  ScopeJournal utf=new ScopeJournal(6,16,32);utf.current(payload("中文"));String saved=utf.snapshot().current;denied(()->utf.current(payload("中文x")));need(utf.snapshot().current.equals(saved)&&utf.snapshot().overflow);pass("content_boundary_uses_utf8_bytes_not_characters");
  pending.reserveEmission(256);pending.reserveEmission(256);denied(()->pending.reserveEmission(1));need(pending.snapshot().emittedAttempted==512);pass("all_pending_final_emissions_share_exact_cap");
 }
 static void meter()throws Exception{
  ScopeMeter m=new ScopeMeter(32,16);m.input("caseA_HASH",ScopeMeter.Count.SDK_REQUEST,4);m.nativeAttempt("caseA_HASH",3);m.returned("caseA_HASH",ScopeMeter.Count.NATIVE_ACTUAL,ScopeMeter.Count.NATIVE_EOF,3,1);m.returned("caseA_HASH",ScopeMeter.Count.SDK_ACTUAL,ScopeMeter.Count.SDK_EOF,4,1);need(count(m,"caseA_HASH","SDK_REQUEST")==4&&count(m,"caseA_HASH","NATIVE_ATTEMPT")==3&&count(m,"caseA_HASH","NATIVE_ACTUAL")==1);pass("sdk4_native3_actual1_are_distinct");
  m.input("caseA_COPY",ScopeMeter.Count.COPY_REQUEST,8);m.input("caseB_CONTROLLED",ScopeMeter.Count.CONTROLLED_INPUT,2);m.input("caseB_REOPEN",ScopeMeter.Count.DIRECT_EOF,1);m.input("caseB_SEEK",ScopeMeter.Count.SDK_REQUEST,17);denied(()->m.input("caseC_PARSE",ScopeMeter.Count.SDK_REQUEST,1));need(value(m.snapshot(),"scopeInputReserved")==32&&value(m.caseSnapshot("caseA"),"scopeInputReserved")==32);pass("all_case_copy_hash_seek_reopen_shared_cap_no_reset");
  m.inputUnknown("caseB_SEEK",ScopeMeter.Count.SDK_FAILED_REQUEST,17);m.nativeAttempt("caseB_REOPEN",1);m.returned("caseB_REOPEN",ScopeMeter.Count.NATIVE_ACTUAL,ScopeMeter.Count.NATIVE_EOF,1,-1);need(count(m,"caseB_REOPEN","NATIVE_EOF")==1&&count(m,"caseB_REOPEN","NATIVE_ACTUAL")==0&&value(m.snapshot(),"scopeInputReserved")==32);pass("eof_and_failed_request_never_refund_or_fake_actual");
  m.outputRequest("caseA_COPY",8);m.outputAttempt("caseA_COPY",8);m.outputReturned("caseA_COPY",8,3);m.outputAttempt("caseA_COPY",5);m.outputUnknown("caseA_COPY",5);m.outputRequest("caseB_MUX",8);m.outputAttempt("caseB_MUX",3);denied(()->m.outputAttempt("caseB_MUX",1));denied(()->m.outputRequest("caseC_MUX",1));need(value(m.snapshot(),"scopeOutputAttempted")==16&&value(m.snapshot(),"scopeOutputRequested")==16&&count(m,"caseA_COPY","OUTPUT_ACTUAL")==3&&count(m,"caseA_COPY","OUTPUT_UNKNOWN")==5);pass("output_copy_mux_short_unknown_all_attempts_not_extent");
  ScopeMeter limits=new ScopeMeter(7,9);denied(()->limits.input("case_HASH",ScopeMeter.Count.SDK_REQUEST,65537));need(value(limits.snapshot(),"scopeInputReserved")==0&&value(limits.snapshot(),"inputLimit")==7&&value(limits.snapshot(),"outputLimit")==9);pass("final_display_limits_match_enforced_values");
  ScopeMeter f=new ScopeMeter();ScopeMeter.Descriptor fd=f.descriptor("RAW",true),asset=f.descriptor("ASSET",false);need(value(f.snapshot(),"knownNativeFdActive")==0);fd.adopted();asset.adopted();fd.unknown();asset.closed();need(value(f.snapshot(),"knownNativeFdActive")==1&&value(f.snapshot(),"knownNativeFdPeak")==1&&value(f.snapshot(),"assetStreamPeak")==1&&value(f.snapshot(),"unknownAllocationOrClose")==1);pass("registered_native_fd_peak_is_not_asset_or_source_count");
  ScopeMeter atomic=new ScopeMeter(5,8);CountDownLatch release=new CountDownLatch(1);AtomicInteger yes=new AtomicInteger(),no=new AtomicInteger();AtomicReference<Throwable> err=new AtomicReference<>();List<Thread> threads=new ArrayList<>();for(int n=0;n<2;n++){final int id=n;Thread t=new Thread(()->{try{need(release.await(2,TimeUnit.SECONDS));atomic.input("case"+id+"_PARSE",ScopeMeter.Count.SDK_REQUEST,4);yes.incrementAndGet();}catch(IOException expected){no.incrementAndGet();}catch(Throwable failure){err.set(failure);}},"tester-fix02-atomic-"+n);threads.add(t);t.start();}try{release.countDown();for(Thread t:threads)joined(t);}finally{release.countDown();for(Thread t:threads)joined(t);}need(err.get()==null&&yes.get()==1&&no.get()==1&&value(atomic.snapshot(),"scopeInputReserved")==4);pass("concurrent_reservations_cannot_split_shared_remaining_cap");
 }
 static final class Token{int closes;}
 static void owners(String role)throws Exception{
  List<OriginalOwner<Token>> keepers=new ArrayList<>();Token token=new Token();OriginalOwner<Token> o=new OriginalOwner<>(role,t->{need(t==token);t.closes++;});keepers.add(o);o.allocate(()->{need(keepers.contains(o)&&!o.returned());return token;});need(o.original()==token&&o.adopted()&&!o.returned());pass(role+"_keeper_precedes_allocator_and_retains_same_object");
  denied(()->o.call("INITIALIZE",t->{need(t==token);throw new IOException("INITIALIZATION_ERROR");}));denied(()->o.call("SECOND_CALL",t->1));need(o.original()==token&&o.closeOnce()&&o.returned()&&o.closeOnce()&&token.closes==1);pass(role+"_call_failure_cleanup_once_preserves_first_error");
  OriginalOwner<Token> unknown=new OriginalOwner<>(role,t->{throw new AssertionError("MUST_NOT_CLOSE_UNKNOWN_ALLOCATION");});denied(()->unknown.allocate(()->{throw new IOException("CONSTRUCTOR_UNKNOWN");}));need(!unknown.returned()&&!unknown.closeOnce()&&Boolean.TRUE.equals(unknown.snapshot().get("allocationIntentRetained")));pass(role+"_allocation_unknown_strong_intent_no_fake_return");
  Token failed=new Token();OriginalOwner<Token> close=new OriginalOwner<>(role,t->{t.closes++;throw new IOException("CLOSE_UNKNOWN");});close.allocate(()->failed);denied(close::closeOnce);need(!close.closeOnce()&&!close.returned()&&close.original()==failed&&failed.closes==1);pass(role+"_throwing_close_retained_never_second_close");
  for(String stage:List.of("ALLOCATE","CALL","CLOSE")){
   CountDownLatch entered=new CountDownLatch(1),tail=new CountDownLatch(1);AtomicReference<Throwable> error=new AtomicReference<>();Token tok=new Token();OriginalOwner<Token> p=new OriginalOwner<>(role,t->{need(t==tok);tok.closes++;if(stage.equals("CLOSE")){entered.countDown();need(tail.await(2,TimeUnit.SECONDS));}});
   if(!stage.equals("ALLOCATE"))p.allocate(()->tok);
   Thread original=new Thread(()->{try{if(stage.equals("ALLOCATE"))p.allocate(()->{entered.countDown();need(tail.await(2,TimeUnit.SECONDS));return tok;});else if(stage.equals("CALL"))p.call("CONTROLLED_IO",t->{need(t==tok);entered.countDown();need(tail.await(2,TimeUnit.SECONDS));return 1;});else need(p.closeOnce());}catch(Throwable t){error.set(t);}},"tester-fix02-"+role+"-"+stage);original.start();
   try{need(entered.await(2,TimeUnit.SECONDS));need(!p.returned()&&!p.closeOnce());if(!stage.equals("ALLOCATE"))need(p.original()==tok);pass(role+"_pending_"+stage+"_blocks_finish_and_second_close");}finally{tail.countDown();joined(original);}
   need(error.get()==null);if(!stage.equals("CLOSE"))need(p.closeOnce());need(p.returned()&&tok.closes==1);pass(role+"_original_"+stage+"_return_and_same_thread_join");
  }
 }
 static void muxFailures()throws Exception{
  for(String stage:List.of("ADD_TRACK","SAMPLE","EMPTY_EOS")){Token m=new Token(),f=new Token();OriginalOwner<Token> mux=new OriginalOwner<>("MATURE_MUX_PORT",t->t.closes++),fd=new OriginalOwner<>("RAW_PORT",t->t.closes++);mux.allocate(()->m);fd.allocate(()->f);denied(()->mux.call(stage,t->{need(t==m);throw new IOException("MATURE_STAGE_FAILURE");}));need(fd.closeOnce()&&!mux.returned()&&mux.original()==m);need(mux.closeOnce()&&mux.returned()&&m.closes==1&&f.closes==1);pass("mux_"+stage+"_sink_return_does_not_prove_mux_return");}
 }
 static void time(long end,boolean timely)throws Exception{
  CompletionPoint point=new CompletionPoint();AtomicLong clock=new AtomicLong(59900000000L);CountDownLatch entered=new CountDownLatch(1),tail=new CountDownLatch(1);AtomicReference<Throwable> error=new AtomicReference<>();
  E13ReturnEvents.Listener listener=()->{entered.countDown();try{need(tail.await(2,TimeUnit.SECONDS));}catch(InterruptedException e){throw new AssertionError(e);}};E13ReturnEvents.subscribe(listener);
  Thread original=new Thread(()->point.finishAfterSignal(E13ReturnEvents::returned,clock::get,error::set),"tester-fix02-last-callback");original.start();
  try{need(entered.await(2,TimeUnit.SECONDS));need(!point.bodyReturned()&&!point.timely(0,60000000000L));clock.set(end);pass("no_body_marker_inside_original_callback_tail_"+end);}finally{tail.countDown();joined(original);E13ReturnEvents.unsubscribe(listener);}
  need(error.get()==null&&point.bodyReturned()&&point.completedNano()==end&&point.timely(0,60000000000L)==timely);clock.set(120000000000L);need(point.timely(0,60000000000L)==timely);pass("last_callback_marker_then_join_and_late_observer_"+end);
 }
 static void signalFailure(){CompletionPoint p=new CompletionPoint();AtomicLong clock=new AtomicLong(1);AtomicBoolean error=new AtomicBoolean();p.finishAfterSignal(()->{throw new IOException("SYNC_SIGNAL_ERROR");},clock::get,t->{error.set(true);clock.set(5);});need(error.get()&&p.completedNano()==5&&p.bodyReturned());pass("signal_failure_recording_precedes_last_controlled_marker");}
 static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte x:b)s.append(String.format(Locale.ROOT,"%02x",x&255));return s.toString();}
 public static void main(String[] args)throws Exception{
  for(Class<?> c:List.of(OriginalOwner.class,ScopeMeter.class,ScopeJournal.class,CompletionPoint.class,E13ReturnEvents.class)){String origin=c.getProtectionDomain().getCodeSource().getLocation().toString();need(origin.endsWith("media3-android02-fix02-classes.jar"));System.out.println("ORIGIN "+c.getName()+"="+origin);}pass("all_five_real_production_classes_from_final_jar");
  need(ExperimentContract.admit(Map.of("case","scopeAll","fixtureSha256",ExperimentContract.qualifiedFixture().sha256,"runId","D1MA02-TESTER"))==ExperimentContract.Method.scopeAll);for(ExperimentContract.Method m:ExperimentContract.Method.values())if(m!=ExperimentContract.Method.scopeAll)denied(()->ExperimentContract.admit(Map.of("case",m.name(),"fixtureSha256",ExperimentContract.qualifiedFixture().sha256,"runId","D1MA02-TESTER")));pass("only_one_scope_all_admitted_no_case_budget_reset");
  journal();meter();owners("RAW_DESCRIPTOR_PORT");owners("MATURE_MUXER_PORT");muxFailures();time(59999999999L,true);time(60000000000L,false);time(60000000001L,false);signalFailure();
  need(args.length==4);for(String name:args){ApkVerifier.Result v=new ApkVerifier.Builder(new File(name)).build().verify();need(v.isVerified()&&v.isVerifiedUsingV2Scheme()&&v.getSignerCertificates().size()==1);String cert=hex(MessageDigest.getInstance("SHA-256").digest(v.getSignerCertificates().get(0).getEncoded()));need(cert.equals("5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f"));System.out.println("VERIFIED "+new File(name).getName()+" v2=true certificateSha256="+cert);}pass("four_real_apksig_verifications");
  System.out.println("DONE independentGroups="+checks+" typedPayloadUtf8Bytes="+payloadBytes+" sameOriginalThreadsJoined=true AndroidOs_ExperimentJob_Media3Parsing_ActualMuxer=NOT_RUN");
 }
}
