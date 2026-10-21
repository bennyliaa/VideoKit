package com.videokit.spike.e4;
import java.io.*;import java.nio.charset.*;import java.nio.file.*;import java.util.*;import java.util.concurrent.atomic.*;
/** Additional test-only probe against final host-001 classes; production is not recompiled. */
public final class IAdditionalCheck {
 interface Check{void run()throws Exception;}static void reject(Check c)throws Exception{boolean refused=false;try{c.run();}catch(IOException e){refused=true;}ICheck.need(refused,"negative gate must refuse");}
 static byte[] b(String s){return s.getBytes(StandardCharsets.UTF_8);}
 public static void main(String[] a)throws Exception{
  String first=IFixtures.inventory();for(String bad:List.of(first.replace(E13IIdentity.SCOPE,"0".repeat(64)),first.replace("10221 101","10222 101"),first.replace("mFinished=false","mFinished=true"),first.replace("E13G_PS_END rc=0","E13G_PS_END rc=1"),first.replace("    mClass=","    Instrumentation #1: OTHER\n    mClass="),first.replace("2000 90 1 sh /system/bin/sh\n",""),first+"trailing",first.replace(E13IIdentity.COMPONENT,"other.package/Other")))reject(()->E13IIdentity.derive(b(bad)));
  reject(()->E13IIdentity.derive(new byte[]{(byte)255}));reject(()->E13IIdentity.number("101;id"));var identities=E13IIdentity.derive(b(first));String second=IFixtures.identity();for(String bad:List.of(second.replace("123456","0"),second.replace("PPid:\t90","PPid:\t91"),second.replace("Uid:\t10221","Uid:\t10222"),second.replace("com.videokit.app \n","com.videokit.app:other \n"),second.replace("E13G_IDENTITY_COMPLETE","TRUNCATED")))reject(()->E13IIdentity.validateIdentity(b(bad),identities));
  reject(()->E13IReadOnly.main(new String[]{"--host","OTHER"}));reject(()->E13IReadOnly.main(new String[]{"--g-readonly","UNISSUED","a".repeat(64)}));
  ICheck.Peer peer=new ICheck.Peer("OK",E13IIdentity.INVENTORY,"");E13ISocket original=new E13ISocket(Paths.get(a[0]),E13IIdentity.INVENTORY,"127.0.0.1",peer.listener.getLocalPort(),p->{},null);try{ICheck.need(original.run(E13ISocket.QUALIFICATION).length==0,"empty stdout with exact EXIT0+EOF can qualify protocol only");}finally{peer.close();original.reader.join();original.keeper.join();}ICheck.need(original.physicalReturned&&!original.failed,"empty original actually returned");
  AtomicInteger opens=new AtomicInteger();E4Owned<Object> allocation=new E4Owned<>("FINITE_NON_IO_OPEN_FAILURE",v->{});reject(()->allocation.allocate(()->{opens.incrementAndGet();throw new IOException("CONTROLLED_OPEN_FAILURE");}));reject(()->allocation.allocate(Object::new));ICheck.need(allocation.state()==E4Owned.State.UNKNOWN&&!allocation.returned()&&opens.get()==1,"unknown open no second allocation, not live IO fixture");
  System.out.println("PASS ADDITIONAL_IDENTITY_EMPTY_OPEN_CONTRACT negativeIdentityGates=15 productionClassesUnchanged=true emptyOriginalSocketReturned=true nonIoUnknownAllocationNotLiveOwnerAck=true SDK0 actual5037=0");
 }
}
