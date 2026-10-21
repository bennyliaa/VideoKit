package com.videokit.spike.c11;

/** Conservative identity and time bounds; signal zero remains unknown. */
public final class ExitRecordRules {
    private ExitRecordRules() {}
    public static boolean matches(int expectedPid, int expectedUid, long startedAt,
                                  long observedAt, int pid, int uid, long timestamp) {
        return expectedPid > 0 && expectedUid > 0 && startedAt > 0
            && observedAt >= startedAt && pid == expectedPid && uid == expectedUid
            && timestamp >= startedAt && timestamp <= observedAt;
    }
    public static boolean awaitSignal(int reason, int status) {
        // Android ApplicationExitInfo: native crash=5, signaled=2.
        return status == 0 && (reason == 5 || reason == 2);
    }
}
