package com.videokit.spike.c14;
public final class C14ExitRecordSelfCheck {
    static int count;
    static void check(boolean value) { if (!value) throw new AssertionError("case " + count); count++; }
    public static void main(String[] args) {
        check(ExitRecordRules.matches(12, 99001, 1000, 2000, 12, 99001, 1500));
        check(!ExitRecordRules.matches(12, 99001, 1000, 2000, 13, 99001, 1500));
        check(!ExitRecordRules.matches(12, 99001, 1000, 2000, 12, 99002, 1500));
        check(!ExitRecordRules.matches(12, 99001, 1000, 2000, 12, 99001, 999));
        check(!ExitRecordRules.matches(12, 99001, 1000, 2000, 12, 99001, 2001));
        check(!ExitRecordRules.matches(0, 99001, 1000, 2000, 0, 99001, 1500));
        check(!ExitRecordRules.matches(12, 0, 1000, 2000, 12, 0, 1500));
        check(!ExitRecordRules.matches(12, 99001, 1000, 999, 12, 99001, 1000));
        check(ExitRecordRules.awaitSignal(5, 0));
        check(ExitRecordRules.awaitSignal(2, 0));
        check(!ExitRecordRules.awaitSignal(5, 11));
        check(!ExitRecordRules.awaitSignal(5, 9));
        check(!ExitRecordRules.awaitSignal(1, 0));
        check(!ExitRecordRules.awaitSignal(-1, 0));
        System.out.println("PASS " + count + " local pure-rule counterexamples; Android NOT_RUN");
    }
}
