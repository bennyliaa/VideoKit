package com.videokit.d1input;
import java.io.*;import java.nio.*;import java.util.concurrent.*;import com.videokit.spike.c14.*;
import static com.videokit.d1input.InputSinkCheck.*;
public class IndependentCancellationCheck {
 static <T>CompletionStage<T> cancelled(){CancellationException e=new CancellationException("private://credential/token");e.initCause(new IOException("private-cause-secret"));return failed(e);}
 static void one(String phase)throws Exception{
  class Host extends MemSink {
   int targetCalls;boolean commitFact;String commitTask,commitToken;
   public CompletionStage<Integer> writeAt(long p,byte[] b,int o,int n){if(phase.equals("WRITE")){targetCalls++;super.writeAt(p,b,o,n);return cancelled();}return super.writeAt(p,b,o,n);}
   public CompletionStage<Void> flush(){if(phase.equals("FLUSH")){targetCalls++;return cancelled();}return super.flush();}
   public CompletionStage<Void> closeWriter(){if(phase.equals("CLOSE")){targetCalls++;super.closeWriter();return cancelled();}return super.closeWriter();}
   public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){if(phase.equals("REOPEN")){targetCalls++;return cancelled();}return super.reopenReadOnly();}
  }
  Host h=new Host();TemporaryOutput s=output(h);ByteBuffer caller=ByteBuffer.wrap(new byte[]{1,2,3,4});IOException caught=null;
  HostOutput.Validator validator=new HostOutput.Validator(){public CompletionStage<HostOutput.Validation> validate(String id,long n,String sha){h.targetCalls++;return cancelled();}public boolean originalOperationsReturned(){return true;}};
  HostOutput.Commit commit=new HostOutput.Commit(){public CompletionStage<Void> commit(String id,String token){h.targetCalls++;h.commitTask=id;h.commitToken=token;return cancelled();}public boolean originalOperationsReturned(){return true;}public HostOutput.CommitOutcome originalOutcome(String id,String token){need(id.equals(h.commitTask)&&token.equals(h.commitToken),"exact original commit");return h.commitFact?HostOutput.CommitOutcome.CONFIRMED_NOT_APPLIED:HostOutput.CommitOutcome.UNKNOWN;}};
  try{
   try{s.channel().write(caller);s.channel().close();s.finishWriter();s.verifyAndValidate(phase.equals("VALIDATE")?validator:h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1"));s.markReady();if(phase.equals("COMMIT"))s.commitByExplicitHost(commit);}catch(IOException e){caught=e;}
   String expected=phase.equals("REOPEN")?"OUTPUT_REOPEN_FAILED":phase.equals("VALIDATE")?"OUTPUT_VALIDATION_FAILED":phase.equals("COMMIT")?"OUTPUT_COMMIT_UNKNOWN":"OUTPUT_IO_FAILED";
   need(caught!=null&&expected.equals(caught.getMessage())&&caught.getCause()==null&&h.targetCalls==1&&s.state().contains("pending=false"),"stable terminal result consumed once");String first=s.firstFailure();
   for(int i=0;i<5;i++)s.observeOriginal();need(first.equals(s.firstFailure())&&h.targetCalls==1,"no repeated consumption/RPC");
   if(phase.equals("WRITE"))need(h.physical==4&&s.acknowledgedBytesLowerBound()==0&&caller.position()==0&&s.unknownWriteReservation()==4,"actual4 not ACK0; UNKNOWN once");
   if(phase.equals("COMMIT")){need(!s.abort()&&!s.returned()&&!s.committed(),"default UNKNOWN remains held");h.commitFact=true;s.observeOriginal();s.finishOriginalCallbacks();need(!s.committed()&&!s.state().contains("abortedAck=true"),"confirmed NOT_APPLIED no fabricated rollback");}else need(s.abort(),"same original cleanup");
   need(s.returned()&&TemporaryOutput.retained()==0&&first.equals(s.firstFailure()),"stable error plus truthful return");System.out.println("PASS independent_cancel "+phase+" actualCall1 consumedOnce=true privateMessageCauseRemoved=true "+s.state());
  }finally{if(!s.returned()){h.commitFact=true;s.observeOriginal();if(s.readyAcknowledged())s.finishOriginalCallbacks();else s.abort();}}
 }
 public static void main(String[] args)throws Exception{System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());for(String p:new String[]{"WRITE","FLUSH","CLOSE","REOPEN","VALIDATE","COMMIT"})one(p);System.out.println("DONE independent_cancel_cases=6 outputKeepers0=true");}
}
