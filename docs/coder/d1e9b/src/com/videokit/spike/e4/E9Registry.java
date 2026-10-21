package com.videokit.spike.e4;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.file.*;
import java.util.*;

/** Actual external authority store/sealer, using the SAME records as Android. No remote root or device flags. */
public final class E9Registry {
    public interface Cut {void at(String operation,String path)throws Exception;}
    private static final Cut NONE=(a,b)->{};
    public static final class Trust {
        public final E9Record plan;public final String authorization,review,environment,registry,migration;
        public Trust(byte[] approvedPlan,String pinnedPlanSha,String authorization,String review)throws Exception{
            E9Record.digest(pinnedPlanSha);E9Record.digest(authorization);E9Record.digest(review);if(!E9Record.sha(approvedPlan).equals(pinnedPlanSha))throw new IOException("E9_TRUSTED_PLAN_PIN");
            E9Record p=E9Record.parse(approvedPlan,8192);p.exact("kind","registry","migration","descriptor","authorization","app","test","signer","appId","testId","uid","testUid","version","role","abi","sourceReview","environment");
            if(!p.get("kind").equals("preparePlan")||!p.get("descriptor").equals(E9LegacyProfile.proposal().hash())||!p.get("authorization").equals(authorization)||!p.get("role").equals("PREPARE")||!p.get("abi").equals("1")||!p.get("appId").equals("com.videokit.app")||!p.get("testId").equals("com.videokit.app.test")||!p.get("uid").equals("10221")||!p.get("testUid").equals("10222")||p.number("version",Integer.MAX_VALUE)<=10)throw new IOException("E9_PREPARE_PLAN_SCOPE");
            for(String k:new String[]{"app","test","signer","sourceReview"})E9Record.digest(p.get(k));if(!p.get("signer").equals("5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f"))throw new IOException("E9_ORIGINAL_SIGNER_REQUIRED");
            E9Record.uuid(p.get("registry"));E9Record.uuid(p.get("migration"));if(!Set.of("DEVICE_HA1Q6WXR","SYNTHETIC_LOCAL").contains(p.get("environment")))throw new IOException("E9_ENVIRONMENT");
            plan=p;this.authorization=authorization;this.review=review;environment=p.get("environment");registry=p.get("registry");migration=p.get("migration");
        }
    }
    public static final class Store {
        public final Path root;private final Cut cut;private final Map<String,Integer> bounds=new TreeMap<>();private final List<E4Owned<?>> outstanding=new ArrayList<>();private int highWater,walkRegistrations;private volatile boolean healthy=true;
        private static final class IO {FileChannel channel;FileLock lock;}
        public Store(Path root,Cut cut)throws Exception{
            this.root=root.toAbsolutePath().normalize();this.cut=cut==null?NONE:cut;
            String[] names={"descriptor.json","authorization-reference.json","prepare-deployment.json","activation-release.json","registry.events.jsonl","registry.checkpoint.json","final.acceptance.json","final.seal.json"};int[] sizes={8192,4096,8192,8192,32768,4096,16384,8192};for(int i=0;i<names.length;i++)bounds.put(names[i],sizes[i]);
            for(int i=1;i<=2;i++){String p="actors/000"+i+"/";bounds.put(p+"reserve.json",4096);bounds.put(p+"identify.json",4096);bounds.put(p+"returned.json",8192);bounds.put(p+"finish.json",4096);bounds.put(p+"termination.json",4096);bounds.put(p+"commands.jsonl",8192);}
            if(bounds.size()!=20)throw new IOException("E9_EXTERNAL_INVENTORY");
        }
        public synchronized int highWater(){return highWater;}public synchronized int registered(){return outstanding.size();}public synchronized int walkRegistrations(){return walkRegistrations;}public synchronized boolean returned(){for(E4Owned<?> h:outstanding)if(!h.returned())return false;return true;}public boolean usable(){return healthy&&returned();}
        private synchronized <T>E4Owned<T> register(Object parameters,E4Owned.Action<T> closer)throws Exception{
            if(!healthy||!returned())throw new IOException("E9_REGISTRY_ORIGINAL_OWNER_UNKNOWN");outstanding.removeIf(E4Owned::returned);E4Owned<T> original=new E4Owned<>(parameters,closer);outstanding.add(original);highWater=Math.max(highWater,outstanding.size());return original;
        }
        private synchronized void retireReturned(E4Owned<?> original){if(original.returned())outstanding.remove(original);}
        public synchronized String originalStates(){StringBuilder states=new StringBuilder();for(E4Owned<?> h:outstanding){if(states.length()>0)states.append(',');states.append(h.state().name());}return states.length()==0?"NONE":states.toString();}
        private Path path(String name)throws Exception{if(!bounds.containsKey(name))throw new IOException("E9_REGISTRY_PATH");Path p=root.resolve(name);for(Path q=p.getParent();q!=null&&q.startsWith(root);q=q.getParent())if(Files.isSymbolicLink(q))throw new IOException("E9_REGISTRY_SYMLINK");if(Files.isSymbolicLink(p))throw new IOException("E9_REGISTRY_SYMLINK");return p;}
        private E4Owned<IO> open(String name,boolean create,boolean append)throws Exception{
            if(!usable())throw new IOException("E9_REGISTRY_ORIGINAL_OWNER_UNKNOWN");Path p=path(name);if(create){Files.createDirectories(p.getParent());path(name);}E4Owned<IO> h=register(p,value->{Exception first=null;try{if(value.lock!=null)value.lock.release();}catch(Exception e){first=e;}try{cut.at("CLOSE_BEFORE",name);if(value.channel!=null)value.channel.close();cut.at("CLOSE_AFTER",name);}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}if(first!=null)throw first;});h.allocate(IO::new);
            try{h.initialize(value->{cut.at("OPEN_BEFORE",name);value.channel=create?FileChannel.open(p,StandardOpenOption.CREATE_NEW,StandardOpenOption.READ,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS):FileChannel.open(p,StandardOpenOption.READ,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS);cut.at("OPEN_AFTER",name);if(append){value.lock=value.channel.tryLock();if(value.lock==null)throw new IOException("E9_REGISTRY_BUSY");}if(value.channel.size()>bounds.get(name))throw new IOException("E9_REGISTRY_FILE_BOUND");});}catch(Exception|Error e){healthy=false;throw e;}return h;
        }
        private <T>void close(E4Owned<T> h,Throwable primary)throws Exception{try{h.close();}catch(Exception|Error t){healthy=false;if(primary!=null)primary.addSuppressed(t);else throw t;}finally{retireReturned(h);}}
        public boolean exists(String name)throws Exception{return Files.exists(path(name),LinkOption.NOFOLLOW_LINKS);}
        public byte[] read(String name)throws Exception{
            E4Owned<IO> h=open(name,false,false);Throwable first=null;try{cut.at("READ",name);int n=(int)h.original().channel.size();byte[] raw=new byte[n];ByteBuffer b=ByteBuffer.wrap(raw);h.original().channel.position(0);while(b.hasRemaining())if(h.original().channel.read(b)<=0)throw new EOFException("E9_REGISTRY_SHORT");return raw;}catch(Exception|Error t){healthy=false;first=t;throw t;}finally{close(h,first);}
        }
        public void create(String name,byte[] bytes)throws Exception{
            if(bytes.length>bounds.getOrDefault(name,-1))throw new IOException("E9_REGISTRY_WRITE_BOUND");E4Owned<IO> h=open(name,true,false);Throwable first=null;
            try{cut.at("WRITE",name);ByteBuffer b=ByteBuffer.wrap(bytes);while(b.hasRemaining())if(h.original().channel.write(b)<=0)throw new IOException("E9_REGISTRY_WRITE");cut.at("FORCE",name);h.original().channel.force(true);}catch(Exception|Error t){healthy=false;first=t;throw t;}finally{close(h,first);}if(!Arrays.equals(read(name),bytes))throw new IOException("E9_REGISTRY_WRITE_READBACK");checkTotal();
        }
        public void append(String name,byte[] bytes,byte[] expectedBefore)throws Exception{
            if(!name.endsWith(".jsonl"))throw new IOException("E9_APPEND_ONLY_LOG");E4Owned<IO> h=open(name,false,true);Throwable first=null;
            try{FileChannel c=h.original().channel;if(c.size()!=expectedBefore.length||c.size()+bytes.length>bounds.get(name))throw new IOException("E9_REGISTRY_LOG_RACE_OR_BOUND");byte[] previous=new byte[expectedBefore.length];c.position(0);ByteBuffer old=ByteBuffer.wrap(previous);while(old.hasRemaining())if(c.read(old)<=0)throw new EOFException();if(!Arrays.equals(previous,expectedBefore))throw new IOException("E9_REGISTRY_LOG_RACE");cut.at("APPEND",name);c.position(c.size());ByteBuffer b=ByteBuffer.wrap(bytes);while(b.hasRemaining())if(c.write(b)<=0)throw new IOException("E9_APPEND_PROGRESS");cut.at("FORCE",name);c.force(true);}catch(Exception|Error t){healthy=false;first=t;throw t;}finally{close(h,first);}checkTotal();
        }
        public void checkTotal()throws Exception{
            if(!usable())throw new IOException("E9_REGISTRY_OWNER_UNKNOWN");long n=0,logs=0;int files=0,visited=0;
            // Register in the same long-lived Store owner BEFORE Files.walk or any platform cut.
            E4Owned<java.util.stream.Stream<Path>> walk=register(root,stream->{cut.at("WALK_CLOSE_BEFORE","checkTotal");stream.close();cut.at("WALK_CLOSE_AFTER","checkTotal");});
            synchronized(this){walkRegistrations++;}Throwable primary=null;
            try{
                walk.allocate(()->{cut.at("WALK_ALLOCATE_ENTER","checkTotal");return Files.walk(root);});cut.at("WALK_ALLOCATE_RETURNED","checkTotal");
                cut.at("WALK_ITERATOR","checkTotal");Iterator<Path> entries=walk.original().iterator();
                for(;;){cut.at("WALK_ITERATE","checkTotal");if(!entries.hasNext())break;
                    if(++visited>40)throw new IOException("E9_EXTERNAL_ENTRY_BOUND");Path p=entries.next();String name=root.relativize(p).toString().replace('\\','/');cut.at("WALK_READ",name.isEmpty()?"ROOT":name);
                    if(Files.isSymbolicLink(p))throw new IOException("E9_EXTERNAL_LINK");
                    if(Files.isDirectory(p,LinkOption.NOFOLLOW_LINKS)){if(!Set.of("","actors","actors/0001","actors/0002","logs").contains(name))throw new IOException("E9_EXTERNAL_DIRECTORY");continue;}
                    if(!Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS))throw new IOException("E9_EXTERNAL_FILE_ROLE");long size=Files.size(p);
                    if(bounds.containsKey(name)){if(size>bounds.get(name))throw new IOException("E9_EXTERNAL_FILE_BOUND");n+=size;files++;}
                    else if(name.matches("logs/actor-000[12][.](instrument|finish)[.]log"))logs+=size;else throw new IOException("E9_EXTERNAL_UNEXPECTED_FILE");
                    if(files>20||n>155648||n>196608||logs>1048576)throw new IOException("E9_REGISTRY_TOTAL_BOUND");
                }
            }catch(Exception|Error t){healthy=false;primary=t;throw t;}
            finally{
                // UNKNOWN/ALLOCATING/CLOSING has no safe second close. The original stays in Store.
                if(walk.state()==E4Owned.State.OPEN||walk.state()==E4Owned.State.READY)close(walk,primary);
                else retireReturned(walk);
            }
        }

    }
    private final Store store;public final Trust trust;private byte[] events=new byte[0];private String head;private boolean sealed,initialized;
    public E9Registry(Store store,Trust trust){this.store=store;this.trust=trust;try{head=E9LegacyProfile.proposal().hash();}catch(IOException e){throw new IllegalStateException(e);}}
    public String head(){return head;}public boolean returned(){return store.returned();}
    private void ready()throws IOException{if(!initialized||!store.usable())throw new IOException("E9_REGISTRY_NOT_READY_OR_UNCERTAIN");}
    public void initialize()throws Exception{
        if(Files.exists(store.root,LinkOption.NOFOLLOW_LINKS))throw new IOException("E9_REGISTRY_EXISTS_NO_RESET");Files.createDirectories(store.root);
        store.create("descriptor.json",E9LegacyProfile.proposal().bytes());store.create("authorization-reference.json",new E9Record(E9Record.map("kind","authorization","descriptor",E9LegacyProfile.proposal().hash(),"reference",trust.authorization,"registry",trust.registry,"migration",trust.migration,"environment",trust.environment),4096).bytes());store.create("prepare-deployment.json",trust.plan.bytes());store.create("registry.events.jsonl",events);initialized=true;
    }
    public void openKnownHead(String expected)throws Exception{
        initialized=false;sealed=false;store.checkTotal();
        E9Record auth=E9Record.parse(store.read("authorization-reference.json"),4096);auth.exact("kind","descriptor","reference","registry","migration","environment");
        if(!auth.get("kind").equals("authorization")||!auth.get("descriptor").equals(E9LegacyProfile.proposal().hash())||!auth.get("reference").equals(trust.authorization)||!auth.get("registry").equals(trust.registry)||!auth.get("migration").equals(trust.migration)||!auth.get("environment").equals(trust.environment))throw new IOException("E9_AUTHORIZATION_REFERENCE_CHANGED");
        if(!Arrays.equals(store.read("descriptor.json"),E9LegacyProfile.proposal().bytes())||!Arrays.equals(store.read("prepare-deployment.json"),trust.plan.bytes()))throw new IOException("E9_REGISTRY_IDENTITY");
        events=store.read("registry.events.jsonl");head=E9LegacyProfile.proposal().hash();int seq=0;Set<String> covered=new HashSet<>();
        for(byte[] raw:lines(events)){E9Record e=E9Record.parse(raw,1024);e.exact("kind","seq","parent","actor","state","path","evidence");if(!e.get("kind").equals("event")||e.number("seq",32)!=++seq||!e.get("parent").equals(head))throw new IOException("E9_REGISTRY_EVENT_CHAIN");byte[] evidence=store.read(e.get("path"));if(!E9Record.sha(evidence).equals(e.get("evidence")))throw new IOException("E9_REGISTRY_EVENT_EVIDENCE");String kind=E9Record.parse(evidence,16384).get("kind");if(Set.of("catalog","checkpoint","seal","activationRelease").contains(kind))throw new IOException("E9_HASH_DAG_CYCLE");covered.add(e.get("path"));head=e.hash();}
        for(int n=1;n<=2;n++)for(String file:new String[]{"reserve.json","returned.json","finish.json","termination.json"})if(store.exists(actorPath(n,file))&&!covered.contains(actorPath(n,file)))throw new IOException("E9_UNANCHORED_REGISTRY_RECORD");
        if(!head.equals(expected))throw new IOException("E9_REGISTRY_UNCERTAIN_HEAD_NO_AUTO_RECOVERY");sealed=store.exists("final.seal.json");
        for(int n=1;n<=2;n++)if(store.exists(actorPath(n,"commands.jsonl"))){E9Actor a=actor(n);if(!store.exists(actorPath(n,"reserve.json")))throw new IOException("E9_REGISTRY_UNCERTAIN_ACTOR");if(store.exists(actorPath(n,"termination.json")))E9Evidence.termination(a,store.read(actorPath(n,"termination.json")));else {E9Record r=E9Record.parse(store.read(actorPath(n,"returned.json")),8192);E9Evidence.returned(a,r.bytes(),r.get("verdict").equals("QUALIFIED_MIGRATION"));E9Evidence.finish(a,r,store.read(actorPath(n,"finish.json")));}}
        initialized=true;if(sealed){try{finalCatalog();}catch(Exception e){initialized=false;throw e;}}
    }
    private static List<byte[]> lines(byte[] bytes)throws Exception{List<byte[]> lines=new ArrayList<>();int from=0;for(int i=0;i<bytes.length;i++)if(bytes[i]=='\n'){lines.add(Arrays.copyOfRange(bytes,from,i+1));from=i+1;}if(from!=bytes.length||lines.size()>32)throw new IOException("E9_LOG_TORN_OR_BOUND");return lines;}
    private String actorPath(int n,String file)throws IOException{if(n<1||n>2)throw new IOException("E9_ACTOR_LIMIT");return "actors/000"+n+"/"+file;}
    private void event(String actor,String state,String evidencePath)throws Exception{
        if(sealed)throw new IOException("E9_FINAL_HEAD_IMMUTABLE");byte[] evidence=store.read(evidencePath);String kind=E9Record.parse(evidence,16384).get("kind");if(Set.of("catalog","checkpoint","seal","activationRelease").contains(kind))throw new IOException("E9_HASH_DAG_CYCLE");
        E9Record e=new E9Record(E9Record.map("kind","event","seq",Integer.toString(lines(events).size()+1),"parent",head,"actor",actor,"state",state,"path",evidencePath,"evidence",E9Record.sha(evidence)),1024);if(lines(events).size()>=32)throw new IOException("E9_EVENT_BOUND");store.append("registry.events.jsonl",e.bytes(),events);byte[] joined=new byte[events.length+e.bytes().length];System.arraycopy(events,0,joined,0,events.length);System.arraycopy(e.bytes(),0,joined,events.length,e.bytes().length);events=joined;head=e.hash();
    }
    public void allocate(int ordinal,String attempt,String handle)throws Exception{ready();
        E9Record.uuid(attempt);E9Record.uuid(handle);if(ordinal==2)requireRecovery();String path=actorPath(ordinal,"commands.jsonl");
        E9Record launch=new E9Record(E9Record.map("kind","launch","registry",trust.registry,"migration",trust.migration,"ordinal",Integer.toString(ordinal),"attempt",attempt,"handle",handle,"plan",trust.plan.hash()),1024);store.create(path,launch.bytes());
    }
    public void commandIntent(int ordinal,E9Record command)throws Exception{ready();
        if(sealed)throw new IOException("E9_REGISTRY_SEALED");String path=actorPath(ordinal,"commands.jsonl");byte[] prior=store.read(path);List<byte[]> rows=lines(prior);if(rows.size()>8)throw new IOException("E9_CONTROL_BUDGET");command.exact("kind","seq","command","handle","intent");if(!command.get("kind").equals("control")||command.number("seq",8)!=rows.size()||!Set.of("STATUS","EXECUTE_COMMIT","ACK_FINISH","STOP_DEPENDENCIES").contains(command.get("command")))throw new IOException("E9_CONTROL_SEQUENCE");E9Record launch=E9Record.parse(rows.get(0),1024);if(!command.get("handle").equals(launch.get("handle")))throw new IOException("E9_CONTROL_HANDLE");int statuses=command.get("command").equals("STATUS")?1:0;for(int i=1;i<rows.size();i++)if(E9Record.parse(rows.get(i),1024).get("command").equals("STATUS"))statuses++;if(statuses>3)throw new IOException("E9_STATUS_BUDGET");if(Set.of("EXECUTE_COMMIT","ACK_FINISH").contains(command.get("command")))for(int i=1;i<rows.size();i++)if(E9Record.parse(rows.get(i),1024).get("command").equals(command.get("command")))throw new IOException("E9_ONCE_CONTROL_NO_REPLAY");store.append(path,command.bytes(),prior);
    }
    public E9Record reserve(E9Actor a,byte[] identityProof,String predecessorIntent)throws Exception{ready();
        if(sealed||!a.record.get("registry").equals(trust.registry)||!a.migration.equals(trust.migration)||!a.descriptor.equals(E9LegacyProfile.proposal().hash())||!a.app.equals(trust.plan.get("app"))||!a.test.equals(trust.plan.get("test"))||!a.record.get("environment").equals(trust.environment))throw new IOException("E9_BOUND_ACTOR_SCOPE");
        E9Record launch=E9Record.parse(lines(store.read(actorPath(a.ordinal,"commands.jsonl"))).get(0),1024);if(!launch.get("attempt").equals(a.attempt)||!launch.get("handle").equals(a.handle))throw new IOException("E9_BOUND_LAUNCH_IDENTITY");
        E9Record proof=E9Evidence.identity(a,identityProof);
        String predecessor="NONE",recovery="NONE",disposition="NONE";
        if(a.ordinal==2){disposition=requireRecovery();E9Actor previous=actor(1);predecessor=previous.hash();recovery=E9Record.sha(store.read(actorPath(1,disposition.equals("TERMINATED_WITHOUT_RETURN")?"termination.json":"returned.json")));if(!predecessorIntent.equals("ABSENT"))E9Record.digest(predecessorIntent);}else if(!predecessorIntent.equals("NONE"))throw new IOException("E9_FIRST_INTENT");
        E9Record r=new E9Record(E9Record.map("kind","reserve","actor",a.hash(),"descriptor",a.descriptor,"authorization",trust.authorization,"preparePlan",trust.plan.hash(),"state","BOUND","ordinal",Integer.toString(a.ordinal),"predecessor",predecessor,"recoveryEvidence",recovery,"recoveryDisposition",disposition,"registry",trust.registry,"predecessorIntent",predecessorIntent),4096);
        store.create(actorPath(a.ordinal,"identify.json"),new E9Record(E9Record.map("kind","identity","actor",E9Record.pack(a.record.bytes()),"returned",E9Record.pack(proof.bytes())),4096).bytes());store.create(actorPath(a.ordinal,"reserve.json"),r.bytes());event(a.hash(),"BOUND",actorPath(a.ordinal,"reserve.json"));return r;
    }
    public void captureIdentityForFinish(E9Actor a,byte[] originalFrame)throws Exception{ready();
        E9Record proof=E9Evidence.archiveComplete(a,originalFrame);if(!proof.get("phase").equals("IDENTITY")||store.exists(actorPath(a.ordinal,"reserve.json"))||!a.record.get("registry").equals(trust.registry)||!a.migration.equals(trust.migration)||!a.app.equals(trust.plan.get("app"))||!a.test.equals(trust.plan.get("test"))||!a.record.get("environment").equals(trust.environment))throw new IOException("E9_IDENTITY_ONLY_CLEANUP_SCOPE");
        E9Record launch=E9Record.parse(lines(store.read(actorPath(a.ordinal,"commands.jsonl"))).get(0),1024);if(!launch.get("handle").equals(a.handle)||!launch.get("attempt").equals(a.attempt))throw new IOException("E9_IDENTITY_ONLY_LAUNCH");
        store.create(actorPath(a.ordinal,"identify.json"),new E9Record(E9Record.map("kind","identity","actor",E9Record.pack(a.record.bytes()),"returned",E9Record.pack(proof.bytes())),4096).bytes());store.create(actorPath(a.ordinal,"returned.json"),proof.bytes());event(a.hash(),"IDENTITY_ONLY_RETURN_NO_COMMIT",actorPath(a.ordinal,"returned.json"));
    }
    public E9Actor actor(int ordinal)throws Exception{if(!store.exists(actorPath(ordinal,"identify.json")))throw new IOException("E9_ACTOR_IDENTITY_NOT_AVAILABLE");E9Record id=E9Record.parse(store.read(actorPath(ordinal,"identify.json")),4096);id.exact("kind","actor","returned");if(!id.get("kind").equals("identity"))throw new IOException("E9_IDENTITY_SCHEMA");return new E9Actor(E9Record.parse(E9Record.unpack(id.get("actor"),2048),2048));}
    public void captureReturned(int ordinal,byte[] originalFrame)throws Exception{ready();
        E9Actor a=actor(ordinal);E9Record r=E9Evidence.returnedForArchive(a,originalFrame);String state="NONQUALIFIED_RETURN_OBSERVED";
        if(r.get("verdict").equals("QUALIFIED_MIGRATION")){E9Evidence.returned(a,originalFrame,true);state="RETURN_OBSERVED";}
        else if(r.get("verdict").equals("PENDING")&&!r.get("device").equals("ABSENT")&&(r.number("identityNanos",Long.MAX_VALUE)>=E9MigrationRun.QUALIFY_NS||r.number("executeNanos",Long.MAX_VALUE)>=E9MigrationRun.QUALIFY_NS)){E9Evidence.returned(a,originalFrame,false);state="RETURNED_LATE_NONQUALIFIED";}
        store.create(actorPath(ordinal,"returned.json"),r.bytes());event(a.hash(),state,actorPath(ordinal,"returned.json"));
    }
    public void captureNormalFinish(int ordinal,byte[] boundedSystemLog,boolean actualOriginalPidAbsent)throws Exception{ready();
        E9Actor a=actor(ordinal);E9Record r=E9Record.parse(store.read(actorPath(ordinal,"returned.json")),8192);
        if(!actualOriginalPidAbsent||boundedSystemLog.length>1048576)throw new IOException("E9_PLATFORM_FINISH_NOT_PROVEN");String log=new String(boundedSystemLog,java.nio.charset.StandardCharsets.UTF_8);
        String anchor="E9_FINAL_FINISH handle="+a.handle+" actor="+a.hash()+" returned="+r.hash();int at=log.indexOf(anchor);if(at<0||log.indexOf(anchor,at+1)>=0)throw new IOException("E9_FINISH_ANCHOR");String after=log.substring(at+anchor.length());
        if(!after.matches("(?s).*Force stopping com[.]videokit[.]app[^\\n]*finished inst.*")||!after.matches("(?s).*Killing "+a.pid+"[^\\n]*finished inst.*"))throw new IOException("E9_NORMAL_FINISH_SYSTEM_EVIDENCE");
        E9Record finish=new E9Record(E9Record.map("kind","finish","actor",a.hash(),"returned",r.hash(),"evidence",E9Record.sha(boundedSystemLog),"disposition","NORMAL_FINISH_CONFIRMED","environment",trust.environment),4096);store.create(actorPath(ordinal,"finish.json"),finish.bytes());event(a.hash(),"NORMAL_FINISH_CONFIRMED",actorPath(ordinal,"finish.json"));
    }
    public void captureTermination(int ordinal,byte[] actualProbe)throws Exception{ready();if(ordinal!=1||store.exists(actorPath(1,"returned.json"))||store.exists(actorPath(2,"commands.jsonl")))throw new IOException("E9_TERMINATION_DISPOSITION_ORDER");E9Actor a=actor(1);E9Record t=E9Evidence.termination(a,actualProbe);store.create(actorPath(1,"termination.json"),t.bytes());event(a.hash(),"TERMINATED_WITHOUT_RETURN",actorPath(1,"termination.json"));}
    private String requireRecovery()throws Exception{
        E9Actor a=actor(1);if(store.exists(actorPath(1,"termination.json"))){E9Evidence.termination(a,store.read(actorPath(1,"termination.json")));return "TERMINATED_WITHOUT_RETURN";}
        if(store.exists(actorPath(1,"returned.json"))&&store.exists(actorPath(1,"finish.json"))){E9Record r=E9Evidence.returned(a,store.read(actorPath(1,"returned.json")),false);E9Evidence.finish(a,r,store.read(actorPath(1,"finish.json")));return "RETURNED_LATE_NONQUALIFIED";}
        throw new IOException("E9_PREDECESSOR_ACTIVE_OR_UNKNOWN");
    }
    public E9Catalog sealFinal()throws Exception{ready();
        if(sealed||!store.returned())throw new IOException("E9_FINAL_NOT_AVAILABLE");int count=store.exists(actorPath(2,"reserve.json"))?2:1;if(!store.exists(actorPath(count,"returned.json"))||!store.exists(actorPath(count,"finish.json")))throw new IOException("E9_ACTOR_NOT_RETURNED_AND_FINISHED");E9Actor last=actor(count);E9Record returned=E9Evidence.returned(last,store.read(actorPath(count,"returned.json")),true);E9Evidence.finish(last,returned,store.read(actorPath(count,"finish.json")));
        if(count==1&&store.exists(actorPath(2,"commands.jsonl")))throw new IOException("E9_UNRESOLVED_EXTRA_ACTOR");if(count==2)requireRecovery();
        event(last.hash(),"FINAL_ACCEPTED",actorPath(count,"finish.json"));Map<String,String> fields=E9Record.map("kind","catalog","version","1","policy",E9LegacyProfile.POLICY,"descriptor",E9Record.pack(E9LegacyProfile.proposal().bytes()),"authorization",trust.authorization,"review",trust.review,"registry",trust.registry,"migration",trust.migration,"head",head,"environment",trust.environment,"actorCount",Integer.toString(count),"device",returned.get("deviceRecord"));
        for(int i=1;i<=2;i++){
            String suffix=Integer.toString(i);if(i>count){for(String p:new String[]{"actor","reserve","returned","finish","termination","disposition"})fields.put(p+suffix,"ABSENT");continue;}
            E9Actor a=actor(i);fields.put("actor"+suffix,E9Record.pack(a.record.bytes()));fields.put("reserve"+suffix,E9Record.pack(store.read(actorPath(i,"reserve.json"))));
            boolean dead=store.exists(actorPath(i,"termination.json"));fields.put("termination"+suffix,dead?E9Record.pack(store.read(actorPath(i,"termination.json"))):"ABSENT");fields.put("returned"+suffix,dead?"ABSENT":E9Record.pack(store.read(actorPath(i,"returned.json"))));fields.put("finish"+suffix,dead?"ABSENT":E9Record.pack(store.read(actorPath(i,"finish.json"))));fields.put("disposition"+suffix,dead?"TERMINATED_WITHOUT_RETURN":i<count?"RETURNED_LATE_NONQUALIFIED":"RETURN_VERIFIED_IN_TIME");
        }
        E9Record catalog=new E9Record(fields,16384);E9Catalog result=E9Catalog.parse(catalog.bytes());store.create("final.acceptance.json",catalog.bytes());
        E9Record checkpoint=new E9Record(E9Record.map("kind","checkpoint","head",head,"catalog",catalog.hash(),"registry",trust.registry),4096);store.create("registry.checkpoint.json",checkpoint.bytes());
        store.create("final.seal.json",new E9Record(E9Record.map("kind","seal","head",head,"catalog",catalog.hash(),"checkpoint",checkpoint.hash(),"descriptor",E9LegacyProfile.proposal().hash(),"preparePlan",trust.plan.hash(),"review",trust.review),8192).bytes());sealed=true;return result;
    }
    public E9Catalog finalCatalog()throws Exception{ready();if(!sealed)throw new IOException("E9_NO_FINAL_CATALOG");E9Catalog c=E9Catalog.parse(store.read("final.acceptance.json"));if(!c.record.get("head").equals(head)||!c.record.get("authorization").equals(trust.authorization)||!c.record.get("review").equals(trust.review)||!c.record.get("registry").equals(trust.registry)||!c.record.get("migration").equals(trust.migration)||!c.record.get("environment").equals(trust.environment))throw new IOException("E9_FINAL_HEAD_OR_AUTHORITY_CHANGED");
        E9Record checkpoint=E9Record.parse(store.read("registry.checkpoint.json"),4096);checkpoint.exact("kind","head","catalog","registry");if(!checkpoint.get("kind").equals("checkpoint")||!checkpoint.get("head").equals(head)||!checkpoint.get("catalog").equals(c.record.hash())||!checkpoint.get("registry").equals(trust.registry))throw new IOException("E9_FINAL_CHECKPOINT");
        E9Record seal=E9Record.parse(store.read("final.seal.json"),8192);seal.exact("kind","head","catalog","checkpoint","descriptor","preparePlan","review");if(!seal.get("kind").equals("seal")||!seal.get("head").equals(head)||!seal.get("catalog").equals(c.record.hash())||!seal.get("checkpoint").equals(checkpoint.hash())||!seal.get("descriptor").equals(E9LegacyProfile.proposal().hash())||!seal.get("preparePlan").equals(trust.plan.hash())||!seal.get("review").equals(trust.review))throw new IOException("E9_FINAL_SEAL_DAG");return c;
    }
    public void requireDeploymentQuiet()throws Exception{ready();boolean any=false;for(int i=1;i<=2;i++)if(store.exists(actorPath(i,"commands.jsonl")))any=true;if(any){if(!sealed)throw new IOException("E9_DEPLOY_ACTOR_NOT_FINAL");finalCatalog();}}
    public E9Record readActivationRelease()throws Exception{ready();E9Catalog c=finalCatalog();E9Record r=E9Record.parse(store.read("activation-release.json"),8192);if(!r.get("signer").equals(trust.plan.get("signer"))||!r.get("role").equals("ACTIVATION")||!r.get("head").equals(head)||!r.get("catalog").equals(c.record.hash())||r.number("version",Integer.MAX_VALUE)<=trust.plan.number("version",Integer.MAX_VALUE))throw new IOException("E9_RELEASE_NOT_SOURCE_APPROVED");return r;}
    public void recordActivationRelease(E9Record release)throws Exception{E9Catalog c=finalCatalog();release.exact("kind","head","catalog","app","test","signer","role","abi","version","sourceReview","environment");if(!release.get("kind").equals("activationRelease")||!release.get("head").equals(head)||!release.get("catalog").equals(c.record.hash())||!release.get("role").equals("ACTIVATION")||!release.get("abi").equals("1")||!release.get("signer").equals(trust.plan.get("signer"))||release.number("version",Integer.MAX_VALUE)<=trust.plan.number("version",Integer.MAX_VALUE)||!release.get("environment").equals(trust.environment))throw new IOException("E9_ACTIVATION_RELEASE_BINDING");for(String k:new String[]{"app","test","sourceReview"})E9Record.digest(release.get(k));store.create("activation-release.json",release.bytes());}
}
