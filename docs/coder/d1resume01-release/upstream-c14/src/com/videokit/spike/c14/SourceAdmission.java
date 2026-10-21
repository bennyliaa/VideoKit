package com.videokit.spike.c14;
import java.io.IOException;
/** Shared actual source broker identity predicate. Endpoint/instance ownership remains with caller. */
public final class SourceAdmission {
    public static void require(int expectedUid,int expectedPid,String expectedTask,long expectedEpoch,
            int actualUid,int actualPid,String actualTask,long actualEpoch,String error)throws IOException {
        if(expectedUid!=actualUid || expectedPid!=actualPid || !expectedTask.equals(actualTask) || expectedEpoch!=actualEpoch)
            throw new IOException(error);
    }
    private SourceAdmission(){}
}
