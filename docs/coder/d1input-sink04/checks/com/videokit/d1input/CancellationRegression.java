package com.videokit.d1input;
import java.nio.*;import java.util.concurrent.*;import java.io.*;import com.videokit.spike.c14.*;import static com.videokit.d1input.InputSinkCheck.*;
/** Tester six inputs retained; assertions now require the corrected stable terminal consumption. */
public final class CancellationRegression {
 static <T>CompletionStage<T> cancelled(){return failed(new CancellationException("private-host-cancellation-detail"));}
 public static void main(String[] args)throws Exception{
  String phase=args[0];boolean[] resolved={false};MemSink h=new MemSink(){
   public CompletionStage<Integer> writeAt(long p,byte[] b,int o,int n){if(phase.equals("WRITE")){writes++;return cancelled();}return super.writeAt(p,b,o,n);}
   public CompletionStage<Void> flush(){if(phase.equals("FLUSH")){flushes++;return cancelled();}return super.flush();}
   public CompletionStage<Void> closeWriter(){if(phase.equals("CLOSE")){closes++;closed=true;return cancelled();}return super.closeWriter();}
   public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){return phase.equals("REOPEN")?cancelled():super.reopenReadOnly();}
  };TemporaryOutput s=output(h);ByteBuffer c=ByteBuffer.wrap(new byte[]{1,2,3,4});IOException caught=null;
  try{s.channel().write(c);s.channel().close();s.finishWriter();HostOutput.Validator v=phase.equals("VALIDATE")?new HostOutput.Validator(){public CompletionStage<HostOutput.Validation> validate(String id,long n,String sha){return cancelled();}public boolean originalOperationsReturned(){return true;}}:h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1");s.verifyAndValidate(v);s.markReady();
   if(phase.equals("COMMIT"))s.commitByExplicitHost(new HostOutput.Commit(){public CompletionStage<Void> commit(String id,String token){return cancelled();}public boolean originalOperationsReturned(){return true;}public HostOutput.CommitOutcome originalOutcome(String id,String token){return resolved[0]?HostOutput.CommitOutcome.CONFIRMED_NOT_APPLIED:HostOutput.CommitOutcome.UNKNOWN;}});
  }catch(IOException e){caught=e;}
  need(caught!=null&&caught.getCause()==null&&!caught.getMessage().contains("private"),"mapped first failure without private cause");String first=s.firstFailure();need(first!=null&&s.state().contains("pending=false"),"cancelled terminal original consumed once");
  for(int n=0;n<5;n++)s.observeOriginal();
  if(phase.equals("WRITE"))need(s.writeAmountUnknown()&&s.unknownWriteReservation()==4&&s.acknowledgedBytesLowerBound()==0&&c.position()==0&&h.writes==1,"one actual invocation, ACK lower0 UNKNOWN4 not actual0 inference");
  if(phase.equals("COMMIT")){need(!s.abort()&&!s.returned()&&!s.committed(),"no cancellation rollback/commit inference");resolved[0]=true;s.observeOriginal();s.finishOriginalCallbacks();need(!s.committed(),"same original authority explicitly proves no side effect, not ACK inference");}else need(s.abort(),"normal original cleanup can finish");
  need(s.returned()&&TemporaryOutput.retained()==0&&first.equals(s.firstFailure()),"sticky failure plus actual full original return");
  System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());System.out.println("PASS tester_cancel_"+phase+" consumedOnce=true privateCause=false originalOwnerReturned=true "+s.state());
 }
}
