import com.videokit.d1android.*;import com.videokit.spike.e4.E13ReturnEvents;
import java.io.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
/** Typed non-media ports only. No Android Os, actual muxer, parser, or reflection. */
public final class TypedFix02Check {
 interface Checked{void run()throws Exception;}static int cases;
 static void need(boolean value){if(!value)throw new AssertionError("FIX02_TYPED_ASSERTION");}
 static void pass(String name){cases++;System.out.println("PASS "+name);}
 static void denied(Checked call)throws Exception{try{call.run();throw new AssertionError("EXPECTED_REJECTION");}catch(IOException expected){}}
 static void joined(Thread t)throws Exception{t.join(2000);need(!t.isAlive());}
 static long num(Map<String,Object> map,String key){return ((Number)map.get(key)).longValue();}
 @SuppressWarnings("unchecked") static long row(ScopeMeter m,String phase,String key){return ((Map<String,Long>)((Map<String,Object>)m.snapshot().get("phases")).get(phase)).get(key);}
 static final class Token{final AtomicInteger closes=new AtomicInteger(),calls=new AtomicInteger();}
 static void journal()throws Exception {
  ScopeJournal j=new ScopeJournal(96,128,256);j.completed("{\"case\":\"one\"}");ScopeJournal.Snapshot before=j.snapshot();
  CountDownLatch published=new CountDownLatch(1),release=new CountDownLatch(1);AtomicReference<Throwable> failure=new AtomicReference<>();
  Thread original=new Thread(()->{try{j.current("{\"phase\":\"IO_PENDING\"}");published.countDown();need(release.await(2,TimeUnit.SECONDS));j.completed("{\"case\":\"two\"}");}catch(Throwable e){failure.set(e);}},"fix02-original-journal");original.start();
  try{need(published.await(2,TimeUnit.SECONDS));ScopeJournal.Snapshot pending=j.snapshot();need(pending.completed.size()==1&&pending.current.contains("IO_PENDING")&&before.current.equals("{}"));pass("B01_pending_keeps_completed_history_and_current_snapshot");}
  finally{release.countDown();joined(original);}need(failure.get()==null&&j.snapshot().completed.size()==2&&before.completed.size()==1);pass("B01_published_snapshot_does_not_change_after_worker_progress");
  try{before.completed.add("bad");throw new AssertionError();}catch(UnsupportedOperationException expected){pass("B01_history_list_immutable");}
  j.current("{\"case\":\"failed\",\"firstFailure\":\"ORIGINAL_PENDING\"}");ScopeJournal.Snapshot partial=j.snapshot();need(partial.completed.size()==2&&partial.current.contains("ORIGINAL_PENDING"));pass("B01_partial_failure_preserves_first_prior_cases");
  denied(()->j.current("x".repeat(97)));need(j.snapshot().overflow&&j.snapshot().completed.equals(partial.completed)&&j.snapshot().current.equals(partial.current));pass("B01_content_overflow_explicit_no_history_drop");
  j.reserveEmission(128);j.reserveEmission(128);denied(()->j.reserveEmission(1));need(j.snapshot().emittedAttempted==256);pass("B01_whole_pending_final_emission_budget_no_refund");
 }
 static void meter()throws Exception {
  ScopeMeter m=new ScopeMeter(16,16);m.input("caseA_HASH",ScopeMeter.Count.SDK_REQUEST,4);m.nativeAttempt("caseA_HASH",3);m.returned("caseA_HASH",ScopeMeter.Count.NATIVE_ACTUAL,ScopeMeter.Count.NATIVE_EOF,3,1);m.returned("caseA_HASH",ScopeMeter.Count.SDK_ACTUAL,ScopeMeter.Count.SDK_EOF,4,1);
  need(row(m,"caseA_HASH","SDK_REQUEST")==4&&row(m,"caseA_HASH","NATIVE_ATTEMPT")==3&&row(m,"caseA_HASH","NATIVE_ACTUAL")==1);pass("B02_sdk4_native_attempt3_actual1_layers_not_inferred");
  m.input("caseA_COPY",ScopeMeter.Count.COPY_REQUEST,4);m.returned("caseA_COPY",ScopeMeter.Count.COPY_ACTUAL,ScopeMeter.Count.COPY_EOF,4,4);m.input("caseB_SEEK",ScopeMeter.Count.SDK_REQUEST,7);m.input("caseB_REOPEN_HASH",ScopeMeter.Count.DIRECT_EOF,1);denied(()->m.input("caseC_PARSE",ScopeMeter.Count.SDK_REQUEST,1));need(num(m.snapshot(),"scopeInputReserved")==16);pass("B02_all_case_phase_budget_before_io_no_factory_refund");
  m.nativeAttempt("caseB_REOPEN_HASH",1);m.returned("caseB_REOPEN_HASH",ScopeMeter.Count.NATIVE_ACTUAL,ScopeMeter.Count.NATIVE_EOF,1,-1);need(row(m,"caseB_REOPEN_HASH","NATIVE_EOF")==1&&row(m,"caseB_REOPEN_HASH","NATIVE_ACTUAL")==0);pass("B02_direct_native_eof_not_positive_return_or_sdk_eof");
  m.inputUnknown("caseB_SEEK",ScopeMeter.Count.NATIVE_UNKNOWN,3);m.inputUnknown("caseB_SEEK",ScopeMeter.Count.SDK_FAILED_REQUEST,7);need(row(m,"caseB_SEEK","NATIVE_UNKNOWN")==3&&num(m.snapshot(),"scopeInputReserved")==16);pass("B02_unknown_reservations_not_actual_zero_or_refund");
  m.outputRequest("caseA_MUX",10);m.outputAttempt("caseA_MUX",10);m.outputReturned("caseA_MUX",10,4);m.outputAttempt("caseA_MUX",6);m.outputUnknown("caseA_MUX",6);denied(()->m.outputAttempt("caseB_MUX",1));need(num(m.snapshot(),"scopeOutputRequested")==10&&num(m.snapshot(),"scopeOutputAttempted")==16&&row(m,"caseA_MUX","OUTPUT_ACTUAL")==4&&row(m,"caseA_MUX","OUTPUT_UNKNOWN")==6);pass("B02_short_write_unknown_counts_all_attempts_no_refund");
  ScopeMeter bounds=new ScopeMeter(16,16);denied(()->bounds.input("c_HASH",ScopeMeter.Count.SDK_REQUEST,65537));need(num(bounds.snapshot(),"scopeInputReserved")==0);pass("B02_block_rejection_precedes_port");
  ScopeMeter concurrent=new ScopeMeter(16,16);CountDownLatch start=new CountDownLatch(1);AtomicInteger accepted=new AtomicInteger(),rejected=new AtomicInteger();List<Thread> threads=new ArrayList<>();
  for(int i=0;i<2;i++){final int index=i;Thread t=new Thread(()->{try{need(start.await(2,TimeUnit.SECONDS));concurrent.input("case"+index+"_PARSE",ScopeMeter.Count.SDK_REQUEST,10);accepted.incrementAndGet();}catch(IOException expected){rejected.incrementAndGet();}catch(InterruptedException e){throw new AssertionError(e);}},"fix02-budget-port-"+i);threads.add(t);t.start();}
  try{start.countDown();for(Thread t:threads)joined(t);}finally{start.countDown();for(Thread t:threads)joined(t);}need(accepted.get()==1&&rejected.get()==1&&num(concurrent.snapshot(),"scopeInputReserved")==10);pass("B02_atomic_shared_reservation_across_callers");
  ScopeMeter fds=new ScopeMeter();ScopeMeter.Descriptor asset=fds.descriptor("ASSET",false),raw=fds.descriptor("RAW",true),read=fds.descriptor("RAF",true);asset.adopted();raw.adopted();read.adopted();need(num(fds.snapshot(),"knownNativeFdPeak")==2&&num(fds.snapshot(),"assetStreamPeak")==1);raw.closed();read.unknown();asset.closed();need(num(fds.snapshot(),"knownNativeFdActive")==1&&num(fds.snapshot(),"unknownAllocationOrClose")==1);pass("B02_fd_native_peak_separate_from_asset_owner_and_source_lease");
 }
 static void completion(long callbackEnd,boolean timely)throws Exception{
  AtomicLong clock=new AtomicLong(59900000000L);CompletionPoint point=new CompletionPoint();CountDownLatch callback=new CountDownLatch(1),tail=new CountDownLatch(1);AtomicReference<Throwable> failure=new AtomicReference<>();
  E13ReturnEvents.Listener listener=()->{callback.countDown();try{need(tail.await(2,TimeUnit.SECONDS));}catch(InterruptedException e){throw new AssertionError(e);}};E13ReturnEvents.subscribe(listener);
  Thread original=new Thread(()->point.finishAfterSignal(E13ReturnEvents::returned,clock::get,failure::set),"fix02-original-return-signal");original.start();
  try{need(callback.await(2,TimeUnit.SECONDS));need(!point.bodyReturned()&&!point.timely(0,60000000000L));clock.set(callbackEnd);pass("B03_no_marker_while_sync_return_callback_tail_pending");}
  finally{tail.countDown();joined(original);E13ReturnEvents.unsubscribe(listener);}need(failure.get()==null&&point.completedNano()==callbackEnd&&point.timely(0,60000000000L)==timely);clock.set(90000000000L);need(point.timely(0,60000000000L)==timely);pass("B03_last_point_"+callbackEnd+"_late_observer_does_not_change_fact");
 }
 static void signalError(){CompletionPoint p=new CompletionPoint();AtomicLong c=new AtomicLong(2);AtomicBoolean recorded=new AtomicBoolean();p.finishAfterSignal(()->{throw new IOException("SIGNAL_ERROR");},c::get,t->{recorded.set(true);c.set(7);});need(recorded.get()&&p.completedNano()==7&&p.bodyReturned());pass("B03_signal_failure_recorded_before_marker_not_after");}
 static void ownerFailures(String kind)throws Exception {
  Token token=new Token();OriginalOwner<Token> owner=new OriginalOwner<>(kind,t->{need(t==token);t.closes.incrementAndGet();});need(owner.returned());owner.allocate(()->token);need(owner.original()==token&&!owner.returned());pass(kind+"_keeper_before_adoption_retains_same_original");
  denied(()->owner.call("INITIALIZE",t->{need(t==token);t.calls.incrementAndGet();throw new IOException("INIT_ERROR");}));need(owner.original()==token&&!owner.returned());denied(()->owner.call("SECOND_OPERATION",t->1));need(owner.closeOnce()&&owner.returned()&&token.closes.get()==1);need(owner.closeOnce()&&token.closes.get()==1);pass(kind+"_initialization_error_keeps_original_cleanup_single_close");
  OriginalOwner<Token> allocation=new OriginalOwner<>(kind,t->t.closes.incrementAndGet());denied(()->allocation.allocate(()->{throw new IOException("CONSTRUCTOR_UNCERTAIN");}));need(!allocation.returned()&&!allocation.closeOnce()&&Boolean.TRUE.equals(allocation.snapshot().get("allocationIntentRetained")));pass(kind+"_allocation_unknown_keeps_intent_never_false_return");
  Token failing=new Token();OriginalOwner<Token> closeUnknown=new OriginalOwner<>(kind,t->{t.closes.incrementAndGet();throw new IOException("CLOSE_UNKNOWN");});closeUnknown.allocate(()->failing);denied(closeUnknown::closeOnce);need(!closeUnknown.returned()&&!closeUnknown.closeOnce()&&failing.closes.get()==1&&closeUnknown.original()==failing);pass(kind+"_close_unknown_no_second_close_or_substitute");
 }
 static void pendingClose(String kind)throws Exception{
  Token token=new Token();CountDownLatch entered=new CountDownLatch(1),tail=new CountDownLatch(1);AtomicReference<Throwable> failure=new AtomicReference<>();OriginalOwner<Token> owner=new OriginalOwner<>(kind,t->{need(t==token);t.closes.incrementAndGet();entered.countDown();need(tail.await(2,TimeUnit.SECONDS));});owner.allocate(()->token);
  Thread original=new Thread(()->{try{need(owner.closeOnce());}catch(Throwable e){failure.set(e);}},"fix02-original-close-"+kind);original.start();
  try{need(entered.await(2,TimeUnit.SECONDS));need(!owner.returned()&&!owner.closeOnce()&&token.closes.get()==1&&owner.original()==token);pass(kind+"_inflight_close_blocks_finish_and_second_close");}
  finally{tail.countDown();joined(original);}need(failure.get()==null&&owner.returned()&&token.closes.get()==1);pass(kind+"_same_original_close_then_actual_thread_join");
 }
 static void muxStages()throws Exception{
  for(String stage:List.of("ADD_TRACK","SAMPLE","EMPTY_EOS")){Token mux=new Token(),fd=new Token();OriginalOwner<Token> sink=new OriginalOwner<>("FD",t->t.closes.incrementAndGet());sink.allocate(()->fd);OriginalOwner<Token> originalMuxer=new OriginalOwner<>("MATURE_MUXER_PORT",t->t.closes.incrementAndGet());originalMuxer.allocate(()->mux);
   denied(()->originalMuxer.call(stage,t->{need(t==mux);throw new IOException("ORIGINAL_MUX_STAGE_ERROR");}));need(!originalMuxer.returned()&&originalMuxer.original()==mux);need(sink.closeOnce()&&!originalMuxer.returned());need(originalMuxer.closeOnce()&&originalMuxer.returned()&&mux.closes.get()==1&&fd.closes.get()==1);pass("B05_"+stage+"_failure_sink_return_cannot_replace_muxer_gate");}
 }
 public static void main(String[] args)throws Exception {
  System.out.println("ORIGIN owner="+OriginalOwner.class.getProtectionDomain().getCodeSource().getLocation()+" typedPorts=true AndroidOs=NOT_RUN MatureMuxer=NOT_RUN payloadBytesUnder65536=true");
  journal();meter();completion(59900000000L,true);completion(60000000000L,false);completion(60100000000L,false);signalError();ownerFailures("B04_RAW_FD");pendingClose("B04_RAW_FD");ownerFailures("B05_MUXER");pendingClose("B05_MUXER");muxStages();
  System.out.println("DONE typedFix02Cases="+cases+" sameOriginalThreadsJoined=true permanentBlockersInjected=0 AndroidOsOrMediaRuntime=NOT_RUN");
 }
}
