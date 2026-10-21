package com.videokit.spike.e4;
import com.videokit.spike.c14.E6AFailure;
/** Exact source/validator attribution at the real session catch boundary. */
public final class E6ADiagnosticState {
    private volatile String source="NOT_STARTED",validator="NOT_STARTED";
    public void sourceEnter(){source="NOT_COLLECTED scope=SOURCE mode=10";}
    public void sourceSuccess(String task,String snapshot){source="scope=SOURCE task="+task+" mode=10 phase=FRAME_ACCEPTED "+snapshot;}
    public void validatorEnter(){validator="NOT_COLLECTED scope=VALIDATOR mode=11 phase=VALIDATION_ENTERED start=UNKNOWN";}
    public void validatorSuccess(String task,String snapshot){validator="scope=VALIDATOR task="+task+" mode=11 phase=VERIFIED "+snapshot;}
    public void failure(Throwable error){
        for(int depth=0;depth<8 && error!=null;depth++,error=error.getCause())if(error instanceof E6AFailure){
            E6AFailure f=(E6AFailure)error;if(f.scope.equals("SOURCE"))source=f.safe();else validator=f.safe();return;
        }
    }
    public String source(){return source;}public String validator(){return validator;}
}
