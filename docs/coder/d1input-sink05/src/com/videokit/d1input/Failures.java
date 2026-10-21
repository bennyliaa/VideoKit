package com.videokit.d1input;
import java.io.*;
import java.nio.file.*;
import java.util.*;
public final class Failures {
 private static final Set<String> SAFE=Set.of("OUTPUT_INVALID_HOST_RESULT","CANCELLED","SOURCE_TIMEOUT","SESSION_RELEASED","SOURCE_DISCONNECTED","SOURCE_NOT_FOUND","SOURCE_PERMISSION_DENIED","INVALID_RANGE","READ_IN_FLIGHT","SOURCE_RESOURCE_EXHAUSTED","SOURCE_ORIGINAL_PENDING","SOURCE_ALREADY_OPEN","SOURCE_NOT_OPEN","SOURCE_CONSUMER_BUDGET","SOURCE_IO_FAILED","INVALID_READ_RESULT","OUTPUT_TIMEOUT_PENDING","OUTPUT_PERMISSION_DENIED","OUTPUT_NO_SPACE","OUTPUT_DISCONNECTED","OUTPUT_IO_FAILED","OUTPUT_INVALID_WRITE_RESULT","OUTPUT_CAPABILITY_UNSUPPORTED","OUTPUT_REOPEN_FAILED","OUTPUT_VALIDATION_FAILED","OUTPUT_STATE_UNKNOWN","OUTPUT_READY_UNKNOWN","OUTPUT_ABORT_UNKNOWN","OUTPUT_COMMIT_UNKNOWN","WORKER_REQUIRED");
 public static IOException io(Throwable t,String fallback){while((t instanceof java.util.concurrent.ExecutionException||t instanceof java.util.concurrent.CompletionException)&&t.getCause()!=null)t=t.getCause();if(t instanceof AccessDeniedException||t instanceof SecurityException)return new IOException("OUTPUT_PERMISSION_DENIED");if(t instanceof IOException&&t.getMessage()!=null&&SAFE.contains(t.getMessage()))return new IOException(t.getMessage());return new IOException(fallback);}
 private Failures(){}
}
