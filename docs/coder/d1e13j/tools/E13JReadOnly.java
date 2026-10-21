package com.videokit.spike.e4;
import java.io.*;import java.nio.*;import java.nio.channels.*;import java.nio.charset.*;import java.nio.file.*;import java.util.*;import java.util.concurrent.*;
/** Fixed role only. No actual execution release has been issued for this source candidate. */
public final class E13JReadOnly {
 static final String APPROVED_REQUEST_SHA="ABSENT";
 static final Path ROOT=Paths.get("D:/CodexProjects/VideoKit/docs/tester/D1_E13J_G_SUPPLEMENT_EVIDENCE");
 static final int TOTAL=262144,HOST=8192,ORIGINAL_SESSION=65536,JAVA_CONSOLE=32768,OBSERVER_CONSOLE=8192,BATCH_META=2048,OP_META=2048;
 static final Set<Batch> OWNERS=ConcurrentHashMap.newKeySet();
 interface Factory{E13JSocket create(Path directory,String script)throws Exception;long qualification();}
 static final class Batch {
  final Path root;final Factory factory;final E4Owned<FileChannel> intent;final List<E13JSocket> originals=new CopyOnWriteArrayList<>();final Thread keeper;volatile boolean callerDone;volatile int reservations=HOST+ORIGINAL_SESSION+JAVA_CONSOLE+OBSERVER_CONSOLE+BATCH_META;volatile boolean failed;volatile String failure="NONE";
  Batch(Path p,Factory f){root=p;factory=f;intent=new E4Owned<>(root.resolve("e13j-g-readonly.once"),FileChannel::close);OWNERS.add(this);keeper=new Thread(()->{for(;;){if(callerDone&&intent.returned()&&originals.stream().allMatch(o->o.physicalReturned&&!o.reader.isAlive()&&!o.keeper.isAlive())){OWNERS.remove(this);return;}try{Thread.sleep(2);}catch(InterruptedException ignored){}}},"I-original-batch-custodian");keeper.setDaemon(false);keeper.start();}
  void intent()throws Exception{Files.createDirectories(root);byte[] raw=("kind=E13J_FIXED_G_READONLY_PENDING\nscope="+E13JIdentity.SCOPE+"\nserial=HA1Q6WXR\nrequestsMax=2\ntotalReservation=262144\nversionQueries=0\n").getBytes(StandardCharsets.US_ASCII);if(raw.length>BATCH_META)throw new IOException("I_BATCH_INTENT_BOUND");intent.allocate(()->FileChannel.open(root.resolve("e13j-g-readonly.once"),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE));try{ByteBuffer b=ByteBuffer.wrap(raw);while(b.hasRemaining())if(intent.original().write(b)<=0)throw new IOException("I_BATCH_INTENT_WRITE");intent.original().force(true);}finally{intent.close();}if(!intent.returned())throw new IOException("I_BATCH_INTENT_CLOSE_UNPROVEN");}
  byte[] query(String script)throws Exception{if(failed||originals.size()>=2||reservations+E13JSocket.WIRE_CAP+OP_META>TOTAL)throw new IOException("I_DEPENDENCIES_OR_BUDGET_SEALED");reservations+=E13JSocket.WIRE_CAP+OP_META;E13JSocket o=factory.create(root.resolve("query-"+(originals.size()+1)),script);originals.add(o);return o.run(factory.qualification());}
  void run()throws Exception{try{intent();byte[] first=query(E13JIdentity.INVENTORY);List<E13JIdentity.Identity> identities=E13JIdentity.derive(first);byte[] second=query(E13JIdentity.identityScript(identities));E13JIdentity.validateIdentity(second,identities);}catch(Exception|Error e){failed=true;failure=e.getClass().getSimpleName();throw e;}finally{callerDone=true;for(E13JSocket o:originals)System.out.println("J_PRODUCTION_RETURN_SNAPSHOT "+o.facts()+" callerQualified="+!failed);}}
 }
 public static void main(String[] a)throws Exception{
  if(a.length==0||Arrays.equals(a,new String[]{"--describe"})){System.out.println("PREPARE_E13J_FIXED_SOCKET_ONLY endpoint=127.0.0.1:5037 serial=HA1Q6WXR services=host:transport:HA1Q6WXR_then_shell,v2,raw:fixedScript versionQueries=0 maxQuerySockets=2 totalBytes=262144 perQueryWire70656_includesTxRx perQueryRaw65536_combined perQueryMetadata2048 batchMetadata2048 maxFrames256 maxService2048 maxFail256 qualificationNs10000000000 actualRelease=ABSENT");return;}
  if(a.length!=3||!a[0].equals("--g-readonly"))throw new IOException("I_FIXED_ROLE_NO_EXTERNAL_HOST_SERVICE_SERIAL_SCRIPT_PID");
  if(APPROVED_REQUEST_SHA.equals("ABSENT")||!APPROVED_REQUEST_SHA.equals(a[2]))throw new IOException("I_EXECUTION_NOT_DISPATCHED_NO_OWNER_OR_NETWORK");
  byte[] raw=E13HostActivationSession.pinned(Paths.get(a[1]),a[2],2048);E9Record r=E9Record.parse(raw,2048);r.exact("kind","scope","serial","review","budget","requests");if(!r.get("kind").equals("e13jFixedReadOnlyRelease")||!r.get("scope").equals(E13JIdentity.SCOPE)||!r.get("serial").equals("HA1Q6WXR")||!r.get("budget").equals("262144")||!r.get("requests").equals("2"))throw new IOException("I_EXACT_REVIEWED_RELEASE_REQUIRED");E9Record.digest(r.get("review"));
  Batch b=new Batch(ROOT,new Factory(){public E13JSocket create(Path p,String s){return new E13JSocket(p,s);}public long qualification(){return E13JSocket.QUALIFICATION;}});b.run();b.keeper.join();System.out.println("I_READONLY_CAPTURE_RETURNED NOT_OLD_OWNER_ACK reservations="+b.reservations);
 }
 private E13JReadOnly(){}
}
