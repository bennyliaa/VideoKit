package com.videokit.spike.e4;
import java.io.IOException;
import java.util.*;
public final class E13Selection {
    public static final Set<String> METHODS=Set.of("ordinarySenderCannotBindCodec","authorizedHostSourceReadAndClose","oldGenerationNeverOpensSource","twoConsumersHoldSourceUntilLastReturn","cancelLateOpenRetainsOriginalOwner","lateReadAndCloseFailureDoNotReleaseEarly");
    public static final String BATCH="D1-E13-SOURCE-20261018";
    public static void require(Map<String,String> args)throws IOException {
        if(!args.keySet().equals(Set.of("class","e13Case","e13Batch","e13ScopeSha256")))throw new IOException("E13_EXACT_ARGUMENTS");
        String method=args.get("e13Case");if(!METHODS.contains(method) || !args.get("class").equals("com.videokit.spike.e4.E13DeviceTests#"+method) || !BATCH.equals(args.get("e13Batch")))throw new IOException("E13_EXACT_METHOD");
        E9Record.digest(args.get("e13ScopeSha256"));E9Phase.requireObservationRole();
    }
    private E13Selection(){}
}
