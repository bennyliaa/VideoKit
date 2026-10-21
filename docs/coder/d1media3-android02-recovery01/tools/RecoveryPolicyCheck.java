import com.videokit.d1android.*;import androidx.media3.common.C;import java.util.*;import java.io.*;
/** Public pure policy only and real APK signature verification; no Android/media runtime. */
public final class RecoveryPolicyCheck {
 static int cases;static void need(boolean ok){if(!ok)throw new AssertionError("RECOVERY_POLICY_FAILURE");}
 static void pass(String s){cases++;System.out.println("PASS "+s);}
 public static void main(String[] args)throws Exception {
  System.out.println("ORIGIN contract="+ExperimentContract.class.getProtectionDomain().getCodeSource().getLocation()+" qualified="+QualifiedObservation.class.getProtectionDomain().getCodeSource().getLocation());
  String sha=ExperimentContract.qualifiedFixture().sha256;
  need(ExperimentContract.admit(Map.of("case","scopeAll","fixtureSha256",sha,"runId","D1MA02-POLICY"))==ExperimentContract.Method.scopeAll);pass("single_scope_batch_entry");
  for(ExperimentContract.Method m:ExperimentContract.Method.values())if(m!=ExperimentContract.Method.scopeAll){try{ExperimentContract.admit(Map.of("case",m.name(),"fixtureSha256",sha,"runId","D1MA02-POLICY"));throw new AssertionError();}catch(IOException expected){pass("no_case_budget_reset_"+m.name());}}
  need(QualifiedObservation.supportedFlags(C.BUFFER_FLAG_KEY_FRAME,0));pass("actual_raw_key_supported");
  need(QualifiedObservation.supportedFlags(C.BUFFER_FLAG_KEY_FRAME|C.BUFFER_FLAG_LAST_SAMPLE,5));pass("declared_last_marker_only_last");
  need(!QualifiedObservation.supportedFlags(C.BUFFER_FLAG_KEY_FRAME|C.BUFFER_FLAG_LAST_SAMPLE,0));pass("reject_early_last_marker");
  need(!QualifiedObservation.supportedFlags(C.BUFFER_FLAG_KEY_FRAME|C.BUFFER_FLAG_END_OF_STREAM,5));pass("eos_not_payload");
  need(!QualifiedObservation.supportedFlags(0,0)&&!QualifiedObservation.supportedFlags(C.BUFFER_FLAG_KEY_FRAME|C.BUFFER_FLAG_ENCRYPTED,0));pass("no_unproven_key_or_encryption");
  VerifyApk.main(args);pass("real_apksig_four_actual_apks");
  System.out.println("DONE recoveryPolicyCases="+cases+" AndroidRuntime=NOT_RUN actualMedia=NOT_RUN scopeBudgetRuntime=NOT_RUN");
 }
}
