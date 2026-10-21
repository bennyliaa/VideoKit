package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.file.*;

/** A file is never its own close/fsync receipt. Grants are live, process-local original-operation proofs. */
final class E5AAdmission {
    interface Proof {Path budget();boolean actualReturnProven();}
    private static volatile Proof grant;
    static void fromRecovery(E5N2Recovery operation){if(operation.actualReturnProven())grant=operation;}
    static void fromObservation(E5AFinalObservation operation){if(operation.actualReturnProven())grant=operation;}
    static void fromCurrentObservation(E9CurrentObservation operation){if(operation.actualReturnProven())grant=operation;}
    static void invalidateCurrent(){grant=null;}
    static void requireCurrent()throws IOException{if(E9CurrentObservation.retained()!=0)throw new IOException("E9_CURRENT_OBSERVATION_PENDING");Proof p=grant;if(p==null||!p.actualReturnProven())throw new IOException("E9_CURRENT_HOST_PROOF_REQUIRED");}
    static void require(Path budget,String identity)throws IOException {
        E9Phase.requireObservationRole();
        if(E9CurrentObservation.retained()!=0)throw new IOException("E9_CURRENT_OBSERVATION_PENDING");
        if(!identity.equals(E5N2Recovery.BUDGET) && !Files.exists(budget.resolve("N2-e5-recovery"),LinkOption.NOFOLLOW_LINKS) && !Files.exists(budget.resolve("operation.pending.N2-e5-aborted"),LinkOption.NOFOLLOW_LINKS) && !Files.exists(budget.resolve("N2-e5-recovery.complete"),LinkOption.NOFOLLOW_LINKS))return;
        Proof p=grant;
        if(p==null || !p.budget().equals(budget.toAbsolutePath().normalize()) || !p.actualReturnProven())throw new IOException("E5A_INDEPENDENT_FINAL_OBSERVATION_REQUIRED");
    }
    private E5AAdmission(){}
}
