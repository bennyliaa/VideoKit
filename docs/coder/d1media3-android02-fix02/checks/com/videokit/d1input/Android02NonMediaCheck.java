package com.videokit.d1input;
import com.videokit.d1android.*;import java.io.*;import java.util.*;
/** Non-media only: arguments/copy/hash/budgets and actual controlled original-return ports. */
public final class Android02NonMediaCheck {
 static int count;static void need(boolean x){if(!x)throw new AssertionError("ANDROID02_NONMEDIA_CHECK_FAILED");}
 static void pass(String s){count++;System.out.println("PASS "+s);}
 public static void main(String[] args)throws Exception {
  ExperimentContract.QualifiedFixture q=ExperimentContract.qualifiedFixture();need(q!=null&&q.bytes==8849&&q.sampleHashes.size()==6&&q.csdHashes.size()==1);pass("fixed_qualified_registry");
  for(ExperimentContract.Method m:ExperimentContract.Method.values()){need(ExperimentContract.admit(Map.of("case",m.name(),"fixtureSha256",q.sha256,"runId","D1MA02-NONMEDIA"))==m);pass("admit_"+m.name());}
  for(Map<String,String> v:List.of(Map.of("case","muxQualified","fixtureSha256",ExperimentContract.SAMPLE_SHA,"runId","D1MA02-X"),Map.of("case","muxQualified","fixtureSha256",q.sha256,"runId","../escape"),Map.of("case","bad","fixtureSha256",q.sha256,"runId","D1MA02-X"),Map.of("case","muxQualified","fixtureSha256",q.sha256,"runId","D1MA02-X","path","bad"))){try{ExperimentContract.admit(v);throw new AssertionError();}catch(IOException expected){pass("reject_before_io");}}
  byte[] data={7,4,2,9};ByteArrayOutputStream out=new ByteArrayOutputStream();VerifiedFixtureCopy.Receipt copied=VerifiedFixtureCopy.copy(new ByteArrayInputStream(data),out,4,VerifiedFixtureCopy.hash(data),()->false);need(copied.fullEof&&copied.bytes==4&&Arrays.equals(out.toByteArray(),data));pass("nonmedia_copy_eof_hash");
  try{VerifiedFixtureCopy.copy(new ByteArrayInputStream(data),new ByteArrayOutputStream(),4,"0".repeat(64),()->false);throw new AssertionError();}catch(IOException e){need(e.getMessage().equals("FIXTURE_HASH_MISMATCH"));pass("nonmedia_copy_mismatch");}
  BoundaryScenarios.run("cancelLateRead",()->{});pass("late_read_cancel_originals_and_caller_buffer");
  BoundaryScenarios.run("writerPending",()->{});pass("writer_ack_not_physical_return_no_reopen_or_early_release");
  ContainerB01Regression.main(new String[0]);pass("inherited_MC_B01_8_nonmedia_boundaries");
  need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0);
  System.out.println("DONE nonMediaChecks="+count+" originalsReturned=true sourceKeepers0 outputKeepers0 AndroidMediaRuntime=NOT_RUN APK=NOT_BUILT");
 }
}
