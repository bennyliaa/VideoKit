package com.videokit.spike.e4;
/** Called by the actual activation runner before platform finish; no synthetic close or retry. */
public final class E11ActivationLifetime {
    public static boolean canFinish(){return E9CurrentObservation.retained()==0&&E4Session.retainedSessions()==0&&E4Session.reservedEncoderSlots()==0&&E5N2Recovery.retainedOperations()==0&&E5AFinalObservation.retained()==0;}
    private E11ActivationLifetime(){}
}
