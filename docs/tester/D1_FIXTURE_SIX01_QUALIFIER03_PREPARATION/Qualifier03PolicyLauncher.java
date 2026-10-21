package com.videokit.qualifier03launcher;
import java.net.*;import java.nio.file.*;import java.lang.reflect.*;import java.util.*;

/** Only JDK classes on launch classpath. One registered owned loader holds the
 * exact helper/test/support/fork universe and is closed by the original worker. */
public final class Qualifier03PolicyLauncher {
 static final String ROOT="D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_SIX01_QUALIFIER03_PREPARATION/";
 static volatile URLClassLoader original;static volatile boolean allocationEntered,allocationReturned,closeEntered,closeReturned,bodyReturned,unknown;static volatile long ended;static volatile Throwable failure;static volatile Map<?,?> result;
 static String quote(String s){return "\""+s.replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r")+"\"";}
 public static void main(String[]args)throws Exception {if(args.length!=0)throw new IllegalArgumentException("NO_ARGS");long start=System.nanoTime();Thread worker=new Thread(()->{try{
   URL[]urls={Paths.get(ROOT+"test-only-classes").toUri().toURL(),Paths.get(ROOT+"helper-classes").toUri().toURL(),Paths.get(ROOT+"support").toUri().toURL(),Paths.get("D:/CodexProjects/VideoKit/docs/coder/d1jcodec-observation01/artifacts/jcodec-0.2.5-videokit-observation01.jar").toUri().toURL()};
   allocationEntered=true;original=new URLClassLoader(urls,ClassLoader.getPlatformClassLoader());allocationReturned=true;Class<?> test=Class.forName("com.videokit.fixturetool.Qualifier03PolicyCheck",true,original);if(test.getClassLoader()!=original)throw new AssertionError("EXACT_ORIGINAL_TEST_LOADER");result=(Map<?,?>)test.getMethod("runCases").invoke(null);
  }catch(Throwable t){failure=t instanceof InvocationTargetException?((InvocationTargetException)t).getCause():t;}finally{if(original!=null&&!closeEntered){closeEntered=true;try{original.close();closeReturned=true;}catch(Throwable t){unknown=true;if(failure==null)failure=t;}}else if(original==null&&allocationEntered)unknown=true;bodyReturned=true;ended=System.nanoTime();}},"qualifier03-original-policy-worker");worker.setDaemon(false);worker.start();worker.join(5000);if(worker.isAlive()){unknown=true;System.out.println("{\"status\":\"UNKNOWN_ORIGINAL_POLICY_WORKER_RETAINED\"}");}worker.join();long elapsed=ended-start;if(elapsed<0||elapsed>=5000000000L)unknown=true;
  boolean success=bodyReturned&&!unknown&&failure==null&&closeReturned&&result!=null;String status=success?"QUALIFIER03_POLICY_ORIGINALS_RETURNED_NOT_MEDIA":"QUALIFIER03_POLICY_FAILED_OR_UNKNOWN_NO_RETRY";
  System.out.println("{\"status\":"+quote(status)+",\"holderRegisteredBeforeLoaderAllocation\":true,\"loaderAllocationEntered\":"+allocationEntered+",\"loaderAllocationReturned\":"+allocationReturned+",\"originalLoaderCloseEntered\":"+closeEntered+",\"sameOriginalLoaderCloseReturned\":"+closeReturned+",\"originalWorkerBodyReturned\":"+bodyReturned+",\"sameOriginalWorkerJoined\":true,\"unknownSticky\":"+unknown+",\"elapsedNanos\":"+elapsed+",\"policyCases\":"+(result==null?"null":result.get("cases"))+",\"explicitMetadataPayloadBytes\":"+(result==null?"null":result.get("explicitMetadataPayloadBytes"))+",\"matureScratchAllowance\":2048,\"failureClass\":"+(failure==null?"null":quote(failure.getClass().getName()))+",\"failureMessage\":"+(failure==null?"null":quote(String.valueOf(failure.getMessage())))+",\"mediaReads\":0,\"actualQualifierInvocations\":0}");
  if(!success)throw new AssertionError("Original finite policy test failure; no retry",failure);
 }
 private Qualifier03PolicyLauncher(){}
}
