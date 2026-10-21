package com.videokit.d1android;
import java.io.*;import java.security.*;
/** Streaming verification of the single approved asset before parser admission.
 * Caller owns, flushes and closes the SAME streams; no hidden closer/retry/cache. */
public final class VerifiedFixtureCopy {
 public interface Stop {boolean stopped();}
 public static final class Receipt {public final long bytes;public final String sha256;public final boolean fullEof;private Receipt(long n,String h){bytes=n;sha256=h;fullEof=true;}}
 public static Receipt copy(InputStream input,OutputStream output,long expectedBytes,String expectedSha,Stop stop)throws IOException {
  if(expectedBytes<1||expectedBytes>8388608||expectedSha==null||!expectedSha.matches("[0-9a-f]{64}"))throw new IOException("FIXTURE_SCOPE_REJECTED");
  MessageDigest digest=digest();byte[] block=new byte[65536];long count=0;
  while(count<expectedBytes){if(stop.stopped())throw new IOException("EXPERIMENT_ADMISSION_STOPPED");int n=input.read(block,0,(int)Math.min(block.length,expectedBytes-count));if(n<0)throw new IOException("FIXTURE_TRUNCATED");if(n==0)throw new IOException("FIXTURE_ZERO_READ");if(n>expectedBytes-count||n>block.length)throw new IOException("FIXTURE_INVALID_READ");output.write(block,0,n);digest.update(block,0,n);count+=n;}
  if(stop.stopped())throw new IOException("EXPERIMENT_ADMISSION_STOPPED");if(input.read()!=-1)throw new IOException("FIXTURE_EXCESS_BYTES");String hash=hex(digest.digest());if(!hash.equals(expectedSha))throw new IOException("FIXTURE_HASH_MISMATCH");return new Receipt(count,hash);
 }
 public static String hash(byte[] data){return hex(digest().digest(data));}
 private static MessageDigest digest(){try{return MessageDigest.getInstance("SHA-256");}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
 private static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte v:b)s.append(String.format(java.util.Locale.ROOT,"%02x",v&255));return s.toString();}
 private VerifiedFixtureCopy(){}
}
