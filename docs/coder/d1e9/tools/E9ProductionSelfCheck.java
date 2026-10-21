package com.videokit.spike.e4;



import java.io.*;

import java.lang.reflect.*;

import java.net.*;

import java.nio.channels.*;

import java.nio.charset.StandardCharsets;

import java.nio.file.*;

import java.util.*;

import java.util.concurrent.*;



/** Finite direct production checks; only platform identity/IO faults/clock/system-log origin are substituted. */

public final class E9ProductionSelfCheck {

    interface Attempt {void run()throws Exception;}

    static int assertions;static Path output,reference;static String selected;static final List<E9TestFiles> IO=new ArrayList<>();

    static void ok(boolean value){assertions++;if(!value)throw new AssertionError(selected+" assertion="+assertions);}

    static void rejected(Attempt op)throws Exception{boolean rejected=false;try{op.run();}catch(Exception e){rejected=true;}ok(rejected);}

    static E9Record changed(E9Record r,String key,String value,int max)throws Exception{Map<String,String> m=new TreeMap<>(r.fields());m.put(key,value);return new E9Record(m,max);}

    static final String SIGNER="5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f";

    static final byte[] PREP_APP="SYNTHETIC_PREPARE_APP_NOT_APK".getBytes(StandardCharsets.US_ASCII),PREP_TEST="SYNTHETIC_PREPARE_TEST_NOT_APK".getBytes(StandardCharsets.US_ASCII);

    static final class Fixture {

        final Path base,device;final E9Registry.Store store;final E9Registry.Trust trust;final E9Registry registry;final E9Record plan;final List<ActorRun> actors=new ArrayList<>();

        Fixture(String name)throws Exception{this(name,null,true);}

        Fixture(String name,E9Registry.Cut cut,boolean initialize)throws Exception{

            base=output.resolve(name);device=base.resolve("synthetic-device-files");E9TestFiles.fixture(device,reference);

            plan=new E9Record(E9Record.map("kind","preparePlan","registry",E9TestFiles.uuid(name+"registry"),"migration",E9TestFiles.uuid(name+"migration"),"descriptor",E9LegacyProfile.proposal().hash(),"authorization",E9TestFiles.digest("authorization"),"app",E9Record.sha(PREP_APP),"test",E9Record.sha(PREP_TEST),"signer",SIGNER,"appId","com.videokit.app","testId","com.videokit.app.test","uid","10221","testUid","10222","version","11","role","PREPARE","abi","1","sourceReview",E9TestFiles.digest("source-review"),"environment","SYNTHETIC_LOCAL"),8192);

            trust=new E9Registry.Trust(plan.bytes(),plan.hash(),plan.get("authorization"),E9TestFiles.digest("independent-final-review"));store=new E9Registry.Store(base.resolve("synthetic-external-registry"),cut);registry=new E9Registry(store,trust);if(initialize)registry.initialize();

        }

        ActorRun actor(int ordinal,String recovery)throws Exception{

            E9Actor a=new E9Actor(new E9Record(E9Record.map("kind","actor","registry",trust.registry,"migration",trust.migration,"ordinal",Integer.toString(ordinal),"attempt",E9TestFiles.uuid(base+"attempt"+ordinal),"handle",E9TestFiles.uuid(base+"handle"+ordinal),"task",E5N2Recovery.TASK,"budget",E5N2Recovery.BUDGET,"policy",E9LegacyProfile.POLICY,"descriptor",E9LegacyProfile.proposal().hash(),"app",plan.get("app"),"test",plan.get("test"),"uid","10221","pid",Integer.toString(13000+ordinal),"process","com.videokit.app","bootKind","SYSTEM_BOOT_COUNT","boot","7","start",Integer.toString(100+ordinal),"participants","SELF_NO_FD_TRANSFER","environment","SYNTHETIC_LOCAL"),2048));

            registry.allocate(ordinal,a.attempt,a.handle);Path identityFile=base.resolve("synthetic-identity-"+ordinal+".json");E9TestFiles.put(identityFile,a.record.bytes());E9TestFiles.Identity identity=new E9TestFiles.Identity(a,identityFile);identity.recovery=recovery;

            ActorRun run=new ActorRun(this,a,identity);actors.add(run);return run;

        }

        E9Catalog complete()throws Exception{ActorRun a=actor(1,"NONE");a.identifyAndBind("NONE");a.run.execute();a.archiveAndFinish();return registry.sealFinal();}

        void oldUnchanged()throws Exception{E9LegacyState.Accounting a=E9LegacyState.ledger(inspectOriginal(device.resolve("e4a_output_budget/ledger.bin")));ok(a.consumed==107218&&a.reserved==0&&a.tasks==3);for(String path:E9LegacyProfile.IMMUTABLE.keySet())ok(E9Record.sha(inspectOriginal(device.resolve(path))).equals(E9LegacyProfile.IMMUTABLE.get(path)));ok(Files.size(device.resolve("e4a_outputs/"+E5N2Recovery.TASK+".mp4"))==0);for(ActorRun r:actors)ok(r.io.guardCreates==0&&r.files.registered()+r.identity.owned()<=48);}

    }

    static byte[] inspectOriginal(Path p)throws Exception{

        for(E9TestFiles io:IO){for(E9TestFiles.G g:io.nativeGuards)if(p.equals(g.path)&&g.file!=null&&g.file.isOpen())return inspectChannel(g.file);for(E9TestFiles.H h:io.nativeHandles)if(p.equals(h.path)&&h.file!=null&&h.file.isOpen())return inspectChannel(h.file);}

        return Files.readAllBytes(p);

    }

    static byte[] inspectChannel(FileChannel f)throws Exception{long before=f.position();try{java.nio.ByteBuffer b=java.nio.ByteBuffer.allocate((int)f.size());f.position(0);while(b.hasRemaining())if(f.read(b)<=0)throw new IOException("INSPECT_NO_PROGRESS");return b.array();}finally{f.position(before);}}

    static final class ActorRun {

        final Fixture fixture;final E9Actor actor;final E9TestFiles io;final E9OwnedFiles files;final E9TestFiles.Identity identity;final E9MigrationTransaction transaction;final E9TestFiles.Clock clock=new E9TestFiles.Clock();final E9MigrationRun run;

        E9Record binding;int finishes;String systemLog="";

        ActorRun(Fixture f,E9Actor a,E9TestFiles.Identity id)throws Exception{

            fixture=f;actor=a;identity=id;io=new E9TestFiles(f.device);IO.add(io);files=new E9OwnedFiles(f.device,io);transaction=new E9MigrationTransaction(files,id);

            run=new E9MigrationRun(a.handle,clock,transaction,proof->{ok(files.returned());ok(identity.returned());ok(runSafe());finishes++;systemLog="E9_FINAL_FINISH handle="+a.handle+" actor="+a.hash()+" returned="+proof.hash()+"\nForce stopping com.videokit.app appid=10221 user=0: finished inst\nKilling "+a.pid+":com.videokit.app/u0a221: finished inst\n";});

        }

        boolean runSafe()throws Exception{return run.snapshot().get("safe").equals("true");}

        void identifyAndBind(String predecessorIntent)throws Exception{run.identify();ok(run.snapshot().get("verdict").equals("IDENTITY_QUALIFIED"));binding=fixture.registry.reserve(actor,run.returnProof().bytes(),predecessorIntent);bind(binding);}

        void bind(E9Record binding)throws Exception{E9Record s=run.snapshot();run.bindAndReserve(binding.bytes(),actor.handle,(int)s.number("commandSeq",8)+1,(int)s.number("stateSeq",Integer.MAX_VALUE));}

        void ack()throws Exception{E9Record s=run.snapshot();ok(run.acknowledgeFinish(actor.handle,(int)s.number("commandSeq",8)+1,(int)s.number("stateSeq",Integer.MAX_VALUE),run.returnProof().hash()));}

        void archiveAndFinish()throws Exception{fixture.registry.captureReturned(actor.ordinal,run.returnProof().bytes());ack();ok(finishes==1);fixture.registry.captureNormalFinish(actor.ordinal,systemLog.getBytes(StandardCharsets.UTF_8),true);}

    }

    static void a01()throws Exception{Fixture f=new Fixture("A01");ActorRun a=f.actor(1,"NONE");a.identity.fail=new IOException("IDENTITY_FAILURE");a.run.identify();ok(a.identity.returned());ok(a.io.opens==0&&a.io.writes==0);rejected(()->f.registry.reserve(a.actor,a.run.returnProof().bytes(),"NONE"));a.run.execute();ok(a.io.writes==0);rejected(E9Phase::requireProduct);f.oldUnchanged();}

    static void a02()throws Exception{

        Fixture f=new Fixture("A02");ActorRun a=f.actor(1,"NONE");a.run.identify();for(String[] field:new String[][]{{"uid","12"},{"pid","0"},{"start","0"},{"descriptor",E9TestFiles.digest("wrong")},{"bootKind","WALL_CLOCK"},{"task",E9TestFiles.uuid("wrongtask")}})rejected(()->new E9Actor(changed(a.actor.record,field[0],field[1],2048)));

        E9Record b=f.registry.reserve(a.actor,a.run.returnProof().bytes(),"NONE");rejected(()->a.bind(changed(b,"actor",E9TestFiles.digest("wrongactor"),4096)));ok(a.io.writes==0);

        String stat="123 (name with ) and space) S 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 777 0\n";ok(E9ProcessIdentity.start(stat.getBytes(StandardCharsets.US_ASCII),123).equals("777"));rejected(()->E9ProcessIdentity.start(stat.getBytes(StandardCharsets.US_ASCII),124));rejected(()->E9ProcessIdentity.termination(a.actor,"SYSTEM_BOOT_COUNT","7","7",null,false));f.oldUnchanged();

    }

    static void a03()throws Exception{Fixture f=new Fixture("A03",(op,path)->{if(op.equals("FORCE")&&path.equals("authorization-reference.json"))throw new IOException("HOST_FORCE_FAILURE");},false);rejected(f.registry::initialize);rejected(()->f.registry.allocate(1,E9TestFiles.uuid("attempt"),E9TestFiles.uuid("handle")));ok(f.store.highWater()<=1);f.oldUnchanged();

        for(String op:new String[]{"WRITE","FORCE","CLOSE_AFTER","READ"}){boolean[] enabled={false};Fixture bad=new Fixture("A03-reserve-"+op,(o,path)->{if(enabled[0]&&o.equals(op)&&path.endsWith("/reserve.json"))throw new IOException("RESERVE_STORE_CUT");},true);ActorRun actor=bad.actor(1,"NONE");actor.run.identify();enabled[0]=true;rejected(()->bad.registry.reserve(actor.actor,actor.run.returnProof().bytes(),"NONE"));ok(actor.io.opens==0&&actor.io.writes==0);rejected(()->bad.registry.commandIntent(1,new E9Record(E9Record.map("kind","control","seq","1","command","EXECUTE_COMMIT","handle",actor.actor.handle,"intent",E9TestFiles.digest("cut")),1024)));bad.oldUnchanged();}

    }

    static void a04()throws Exception{Fixture f=new Fixture("A04");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");ok(!a.runSafe()&&a.files.registered()==0);E9Record s=a.run.snapshot();rejected(()->a.run.acknowledgeFinish(a.actor.handle,2,(int)s.number("stateSeq",Integer.MAX_VALUE),E9TestFiles.digest("no-return")));ok(a.finishes==0);a.run.execute();ok(a.io.writes==0);ok(a.run.snapshot().get("verdict").equals("PENDING"));a.archiveAndFinish();rejected(f.registry::sealFinal);rejected(()->f.registry.allocate(2,E9TestFiles.uuid("not-late"),E9TestFiles.uuid("not-late-handle")));f.oldUnchanged();}

    static void cutTransactions(String group,String suffix)throws Exception{

        int n=0;for(boolean error:new boolean[]{false,true})for(String op:new String[]{"OPEN_BEFORE","OPEN_AFTER","WRITE","FORCE","READ","CLOSE_BEFORE","CLOSE_AFTER"}){

            Fixture f=new Fixture(group+"-"+n++);ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");boolean[] once={false};a.io.cut=(operation,path)->{if(!once[0]&&operation.equals(op)&&path.endsWith(suffix)){once[0]=true;if(error)throw new AssertionError("CUT_ERROR_"+op);throw new IOException("CUT_"+op);}};

            a.run.execute();if(!once[0]&&a.run.firstFailure()!=null)a.run.firstFailure().printStackTrace();ok(once[0]);ok(!a.run.snapshot().get("verdict").equals("QUALIFIED_MIGRATION"));ok(a.finishes==0);rejected(()->f.registry.sealFinal());f.oldUnchanged();

        }

    }

    static void a05()throws Exception{cutTransactions("A05","0001.intent");for(String op:new String[]{"MKDIR","DIR_SYNC"}){Fixture f=new Fixture("A05-"+op);ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");boolean[] once={false};a.io.cut=(o,p)->{if(!once[0]&&o.equals(op)&&p.contains("legacy-acceptance")){once[0]=true;throw new IOException("DIRECTORY_CUT");}};a.run.execute();ok(once[0]);ok(!a.run.snapshot().get("verdict").equals("QUALIFIED_MIGRATION"));f.oldUnchanged();}}

    static void a06()throws Exception{cutTransactions("A06-payload","n2-v2.acceptance");cutTransactions("A06-commit","n2-v2.commit");}

    static void a07()throws Exception{

        Fixture f=new Fixture("A07");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);boolean[] once={false};

        a.io.cut=(op,path)->{if(!once[0]&&op.equals("GUARD_CLOSE_BEFORE")&&path.endsWith(".lease")){once[0]=true;entered.countDown();if(!release.await(2,TimeUnit.SECONDS))throw new IOException("FINITE_CUT_TIMEOUT");}};

        Thread t=new Thread(a.run::execute);t.start();ok(entered.await(1,TimeUnit.SECONDS));ok(!a.runSafe());ok(a.io.unlocks>0);

        try(FileChannel other=FileChannel.open(f.device.resolve("e4a_outputs/"+E5N2Recovery.TASK+".lease"),StandardOpenOption.READ,StandardOpenOption.WRITE);FileLock acquired=other.tryLock()){ok(acquired!=null);}

        rejected(f.registry::requireDeploymentQuiet);rejected(f.registry::sealFinal);ok(a.finishes==0);a.clock.now=E9MigrationRun.QUALIFY_NS;a.run.deadline();release.countDown();t.join(1000);ok(!t.isAlive());ok(a.runSafe());ok(a.run.snapshot().get("verdict").equals("PENDING"));a.archiveAndFinish();rejected(f.registry::sealFinal);f.oldUnchanged();

    }

    static void a08()throws Exception{Fixture f=new Fixture("A08");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");boolean[] once={false};a.io.cut=(op,path)->{if(!once[0]&&op.equals("GUARD_CLOSE_AFTER")&&path.endsWith(".owner")){once[0]=true;throw new IOException("CLOSE_UNKNOWN_AFTER_NATIVE_RETURN");}};a.run.execute();ok(once[0]);ok(!a.runSafe());ok(a.run.snapshot().get("verdict").equals("PENDING"));rejected(()->a.run.returnProof());rejected(f.registry::sealFinal);ok(a.finishes==0);f.oldUnchanged();}

    static void a09()throws Exception{

        Fixture f=new Fixture("A09");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");a.clock.now=E9MigrationRun.QUALIFY_NS;a.run.deadline();a.run.execute();ok(a.io.writes==0);ok(a.run.snapshot().get("verdict").equals("PENDING"));ok(a.runSafe());rejected(f.registry::sealFinal);f.oldUnchanged();

        Fixture id=new Fixture("A09-identity");ActorRun b=id.actor(1,"NONE");b.clock.now=E9MigrationRun.QUALIFY_NS;b.run.deadline();b.run.identify();ok(b.io.writes==0&&b.identity.owned.state()==E4Owned.State.EMPTY);ok(b.runSafe());ok(b.run.snapshot().get("verdict").equals("PENDING"));

    }

    static void a10()throws Exception{Fixture f=new Fixture("A10");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");rejected(()->f.registry.captureReturned(1,new E9Record(E9Record.map("kind","returned","returned","true"),8192).bytes()));a.run.execute();E9Record r=a.run.returnProof();rejected(()->f.registry.captureReturned(1,changed(r,"actor",E9TestFiles.digest("wrongactor"),8192).bytes()));rejected(()->f.registry.captureReturned(1,changed(r,"unreturned","1",8192).bytes()));ok(a.finishes==0);f.oldUnchanged();}

    static void a11()throws Exception{Fixture f=new Fixture("A11");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");a.run.execute();f.registry.captureReturned(1,a.run.returnProof().bytes());rejected(()->f.registry.captureNormalFinish(1,"finishClaimed=true".getBytes(),true));rejected(f.registry::sealFinal);a.ack();f.registry.captureNormalFinish(1,a.systemLog.getBytes(StandardCharsets.UTF_8),true);ok(f.registry.sealFinal().actors.length==1);f.oldUnchanged();}

    static void a12()throws Exception{

        for(String file:new String[]{"actors/0001/returned.json","registry.checkpoint.json","final.seal.json"})for(String op:new String[]{"WRITE","FORCE","CLOSE_AFTER","READ"}){

            boolean[] enabled={false};Fixture f=new Fixture("A12-"+file.replace('/','_')+"-"+op,(o,path)->{if(enabled[0]&&o.equals(op)&&path.equals(file))throw new IOException("FINAL_STORE_CUT");},true);ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");a.run.execute();

            if(file.endsWith("returned.json")){enabled[0]=true;rejected(()->f.registry.captureReturned(1,a.run.returnProof().bytes()));ok(a.finishes==0);}

            else{a.archiveAndFinish();enabled[0]=true;rejected(f.registry::sealFinal);}

            rejected(f.registry::finalCatalog);f.oldUnchanged();

        }

    }

    static void a13()throws Exception{Fixture f=new Fixture("A13");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");E9Registry reopened=new E9Registry(new E9Registry.Store(f.store.root,null),f.trust);rejected(()->reopened.openKnownHead(E9TestFiles.digest("unknownhead")));rejected(()->reopened.openKnownHead(f.registry.head()));rejected(reopened::requireDeploymentQuiet);E9Record intent=new E9Record(E9Record.map("kind","control","seq","1","command","EXECUTE_COMMIT","handle",a.actor.handle,"intent",E9TestFiles.digest("intent")),1024);f.registry.commandIntent(1,intent);rejected(()->f.registry.commandIntent(1,intent));ok(a.io.writes==0);f.oldUnchanged();}

    static void a14()throws Exception{Fixture f=new Fixture("A14");E9Catalog c=f.complete();ok(Files.exists(f.device.resolve("e4a_output_budget/legacy-acceptance/"+f.trust.migration+"/n2-v2.commit")));ok(c.device.get("commit").equals(E9MigrationTransaction.commitRecord().hash()));rejected(E9Phase::requireProduct);rejected(E9Phase::requireObservationRole);ok(E9BuildPolicy.CATALOG_SHA.equals("ABSENT"));f.oldUnchanged();}

    static void a15()throws Exception{Fixture f=new Fixture("A15");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");rejected(()->f.registry.allocate(2,E9TestFiles.uuid("secondattempt"),E9TestFiles.uuid("secondhandle")));rejected(()->E9ProcessIdentity.termination(a.actor,"SYSTEM_BOOT_COUNT","7","7",proc(a.actor.pid,a.actor.start),false));ok(a.io.writes==0);f.oldUnchanged();}

    static byte[] proc(int pid,String start){String[] f=new String[21];Arrays.fill(f,"0");f[0]="S";f[19]=start;return (pid+" (synthetic ) name) "+String.join(" ",f)+"\n").getBytes(StandardCharsets.US_ASCII);}

    static void a16()throws Exception{

        Fixture f=new Fixture("A16");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");a.io.cut=(op,path)->{if(op.equals("CLOSE_AFTER")&&path.endsWith("n2-v2.commit"))throw new IOException("ORIGINAL_CLOSE_UNKNOWN");};a.run.execute();ok(!a.runSafe());

        // Platform substitute says the exact original process generation has terminated, NOT Java close.

        E9Record term=E9ProcessIdentity.termination(a.actor,"SYSTEM_BOOT_COUNT","7","7",null,true);f.registry.captureTermination(1,term.bytes());a.io.closeNativeFacsimilesAfterAssertions();

        ActorRun b=f.actor(2,term.hash());String oldIntent=E9Record.sha(a.actor.intent(a.binding.hash()));b.identifyAndBind(oldIntent);b.run.execute();b.archiveAndFinish();E9Catalog c=f.registry.sealFinal();ok(c.dispositions[0].equals("TERMINATED_WITHOUT_RETURN"));ok(c.returns[0]==null);ok(c.dispositions[1].equals("RETURN_VERIFIED_IN_TIME"));ok(!a.runSafe());f.oldUnchanged();

    }

    static void a17()throws Exception{Fixture f=new Fixture("A17");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");a.io.cut=(op,path)->{if(op.equals("GUARD_CLOSE_AFTER"))a.clock.now=E9MigrationRun.QUALIFY_NS;};a.run.execute();ok(a.run.snapshot().get("verdict").equals("PENDING"));a.archiveAndFinish();ActorRun b=f.actor(2,a.run.returnProof().hash());b.identifyAndBind(E9Record.sha(a.actor.intent(a.binding.hash())));b.run.execute();b.archiveAndFinish();E9Catalog c=f.registry.sealFinal();ok(c.dispositions[0].equals("RETURNED_LATE_NONQUALIFIED"));ok(c.returns[0].get("verdict").equals("PENDING"));ok(c.dispositions[1].equals("RETURN_VERIFIED_IN_TIME"));f.oldUnchanged();}

    static void a18()throws Exception{

        Fixture f=new Fixture("A18");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");a.io.cut=(op,path)->{if(op.equals("OPEN_BEFORE")&&path.endsWith("n2-v2.commit"))throw new IOException("NO_COMMIT_CREATED");};a.run.execute();E9Record term=E9ProcessIdentity.termination(a.actor,"SYSTEM_BOOT_COUNT","7","7",null,true);f.registry.captureTermination(1,term.bytes());a.io.closeNativeFacsimilesAfterAssertions();ActorRun b=f.actor(2,term.hash());b.identifyAndBind(E9Record.sha(a.actor.intent(a.binding.hash())));b.run.execute();b.archiveAndFinish();ok(f.registry.sealFinal().actors.length==2);f.oldUnchanged();

        Fixture bad=new Fixture("A18-torn");ActorRun x=bad.actor(1,"NONE");x.identifyAndBind("NONE");x.io.cut=(op,path)->{if(op.equals("WRITE")&&path.endsWith("n2-v2.commit"))throw new IOException("EMPTY_TORN_COMMIT");};x.run.execute();E9Record death=E9ProcessIdentity.termination(x.actor,"SYSTEM_BOOT_COUNT","8","8",null,false);bad.registry.captureTermination(1,death.bytes());x.io.closeNativeFacsimilesAfterAssertions();ActorRun y=bad.actor(2,death.hash());y.identifyAndBind(E9Record.sha(x.actor.intent(x.binding.hash())));y.run.execute();ok(!y.run.snapshot().get("verdict").equals("QUALIFIED_MIGRATION"));ok(Files.size(bad.device.resolve("e4a_output_budget/legacy-acceptance/"+bad.trust.migration+"/n2-v2.commit"))==0);rejected(bad.registry::sealFinal);bad.oldUnchanged();

    }

    static void a19()throws Exception{Fixture f=new Fixture("A19");ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");a.io.cut=(op,path)->{if(op.equals("GUARD_CLOSE_AFTER"))a.clock.now=E9MigrationRun.QUALIFY_NS;};a.run.execute();a.archiveAndFinish();ActorRun b=f.actor(2,a.run.returnProof().hash());b.identifyAndBind(E9Record.sha(a.actor.intent(a.binding.hash())));b.io.cut=(op,path)->{if(op.equals("CLOSE_AFTER")&&path.endsWith("0002.intent"))throw new IOException("ACTOR2_CLOSE_UNKNOWN");};b.run.execute();rejected(()->f.registry.allocate(3,E9TestFiles.uuid("third"),E9TestFiles.uuid("thirdhandle")));rejected(f.registry::sealFinal);ok(!b.runSafe());f.oldUnchanged();}

    static void a20()throws Exception{Fixture f=new Fixture("A20");E9Catalog c=f.complete();byte[] events=Files.readAllBytes(f.store.root.resolve("registry.events.jsonl"));String head=f.registry.head();E9Record release=activationRelease(f,c);f.registry.recordActivationRelease(release);ok(Arrays.equals(events,Files.readAllBytes(f.store.root.resolve("registry.events.jsonl"))));ok(head.equals(f.registry.head()));ok(!new String(events,StandardCharsets.US_ASCII).contains(c.record.hash()));E9Registry reloaded=new E9Registry(new E9Registry.Store(f.store.root,null),f.trust);reloaded.openKnownHead(head);ok(reloaded.finalCatalog().record.hash().equals(c.record.hash()));

        rejected(()->E9ActivationPolicyExport.export(f.registry,f.base.resolve("forbidden-synthetic-release")));ok(!Files.exists(f.base.resolve("forbidden-synthetic-release")));

        Path auth=f.store.root.resolve("authorization-reference.json");byte[] saved=Files.readAllBytes(auth);E9Record ar=E9Record.parse(saved,4096);Files.write(auth,changed(ar,"reference",E9TestFiles.digest("revoked"),4096).bytes(),StandardOpenOption.TRUNCATE_EXISTING);rejected(()->new E9Registry(new E9Registry.Store(f.store.root,null),f.trust).openKnownHead(head));Files.write(auth,saved,StandardOpenOption.TRUNCATE_EXISTING);

        E9TestFiles.put(f.store.root.resolve("unexpected.json"),new byte[0]);rejected(()->new E9Registry(new E9Registry.Store(f.store.root,null),f.trust).openKnownHead(head));f.oldUnchanged();}

    static E9Record activationRelease(Fixture f,E9Catalog c)throws Exception{return new E9Record(E9Record.map("kind","activationRelease","head",c.record.get("head"),"catalog",c.record.hash(),"app",E9Record.sha("SYNTHETIC_ACTIVATION_APP".getBytes()),"test",E9Record.sha("SYNTHETIC_ACTIVATION_TEST".getBytes()),"signer",SIGNER,"role","ACTIVATION","abi","1","version","12","sourceReview",E9TestFiles.digest("activation-source-review"),"environment","SYNTHETIC_LOCAL"),8192);}

    static void a21()throws Exception{

        Fixture f=new Fixture(selected);E9Catalog c=f.complete();rejected(()->E9Catalog.fromTrustedRelease(changed(c.record,"head",E9TestFiles.digest("wronghead"),16384).bytes(),c.record.hash(),"SYNTHETIC_LOCAL"));rejected(()->E9Catalog.fromTrustedRelease(c.record.bytes(),c.record.hash(),"DEVICE_HA1Q6WXR"));

        for(String[] bad:new String[][]{{"registry",E9TestFiles.uuid("otherregistry")},{"actorCount","2"},{"policy","UNKNOWN_SCHEMA"},{"device",E9Record.pack(changed(c.device,"commit",E9TestFiles.digest("wrongcommit"),2048).bytes())}})rejected(()->E9Catalog.parse(changed(c.record,bad[0],bad[1],16384).bytes()));

        E9Catalog.Trusted t=E9Catalog.fromTrustedRelease(c.record.bytes(),c.record.hash(),"SYNTHETIC_LOCAL");E9TestFiles io=new E9TestFiles(f.device);IO.add(io);

        if(selected.endsWith("pending"))E9TestFiles.put(f.device.resolve("e4a_output_budget/operation.pending"),new byte[0]);

        else if(selected.endsWith("guard"))io.inodeChanged="e4a_outputs/"+E5N2Recovery.TASK+".owner";

        else if(selected.endsWith("ledger"))Files.writeString(f.device.resolve("e4a_output_budget/ledger.bin"),"ILLEGAL_SUFFIX\n",StandardCharsets.US_ASCII,StandardOpenOption.APPEND);

        else if(selected.endsWith("close"))io.cut=(op,path)->{if(op.equals("GUARD_CLOSE_AFTER")&&path.endsWith(".owner"))throw new IOException("CURRENT_ORIGINAL_CLOSE_UNKNOWN");};

        else Files.write(f.device.resolve("e4a_output_budget/legacy-acceptance/"+f.trust.migration+"/n2-v2.acceptance"),new byte[]{1},StandardOpenOption.TRUNCATE_EXISTING);

        E9CurrentObservation o=new E9CurrentObservation(f.device,t,io);ok(o.observe().startsWith("BLOCKED"));ok(!o.actualReturnProven());rejected(E5AAdmission::requireCurrent);if(!selected.endsWith("ledger"))f.oldUnchanged();

    }

    static void appendSettled(Path ledger)throws Exception{String text=Files.readString(ledger,StandardCharsets.US_ASCII);String last=text.stripTrailing();String chain=last.substring(last.lastIndexOf(' ')+1);String id=E9TestFiles.uuid("legal-new-task"),r="R "+id+" D1-E4A-E9-SYNTHETIC",rh=E9Record.sha((chain+" "+r).getBytes(StandardCharsets.US_ASCII)),s="S "+id+" ABORTED 7 "+E9TestFiles.digest("sevenbytes"),sh=E9Record.sha((rh+" "+s).getBytes(StandardCharsets.US_ASCII));Files.writeString(ledger,r+" "+rh+"\n"+s+" "+sh+"\n",StandardCharsets.US_ASCII,StandardOpenOption.APPEND);}

    static void a22()throws Exception{Fixture f=new Fixture("A22");E9Catalog c=f.complete();appendSettled(f.device.resolve("e4a_output_budget/ledger.bin"));E9TestFiles io=new E9TestFiles(f.device);IO.add(io);E9CurrentObservation o=new E9CurrentObservation(f.device,E9Catalog.fromTrustedRelease(c.record.bytes(),c.record.hash(),"SYNTHETIC_LOCAL"),io);String result=o.observe();ok(result.startsWith("FRESH_E9_OBSERVATION_ADMITTED"));ok(o.actualReturnProven());E5AAdmission.requireCurrent();ok(o.registered()<=48);ok(E9LegacyState.ledger(Files.readAllBytes(f.device.resolve("e4a_output_budget/ledger.bin"))).consumed==107225);rejected(E9Phase::requireProduct);ok(o.observe().startsWith("BLOCKED"));}

    static void a23()throws Exception{Fixture f=new Fixture("A23");ActorRun a=f.actor(1,"NONE");a.run.identify();a.run.closeUnstartedWriteIngress();E9Record b=f.registry.reserve(a.actor,a.run.returnProof().bytes(),"NONE");rejected(()->a.bind(b));ok(a.io.writes==0&&a.runSafe());a.ack();ok(a.finishes==1);f.oldUnchanged();}



    static final class DeployPort implements E9DeploymentGate.Port {

        E9DeploymentGate.PackageInfo current,candidate;int inspectCalls,installs;boolean postMismatch;final List<List<String>> commands=new ArrayList<>();

        public byte[] artifact(Path p,int max)throws Exception{byte[] b=Files.readAllBytes(p);if(b.length>max)throw new IOException("TEST_ARTIFACT_BOUND");return b;}

        public E9DeploymentGate.PackageInfo inspectArtifacts(Path a,Path t){inspectCalls++;return candidate;}

        public E9DeploymentGate.PackageInfo installed(){if(installs>=2){if(postMismatch)return new E9DeploymentGate.PackageInfo(candidate.appId,candidate.testId,E9TestFiles.digest("post-mismatch"),candidate.testSha,candidate.signer,candidate.role,10221,10222,candidate.version,candidate.abi,false);return candidate;}return current;}

        public void dispatch(List<String> argv){ok(argv.size()==6&&argv.get(3).equals("install")&&argv.get(4).equals("-r"));commands.add(argv);installs++;}

    }

    static E9DeploymentGate.PackageInfo pkg(String app,String test,String role,int version,int abi,boolean live){return new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",app,test,SIGNER,role,10221,10222,version,abi,live);}

    static DeployPort deployPort(Fixture f)throws Exception{DeployPort p=new DeployPort();p.current=pkg(E9TestFiles.digest("legacy-app"),E9TestFiles.digest("legacy-test"),"LEGACY_NO_GATE",10,0,false);p.candidate=pkg(f.plan.get("app"),f.plan.get("test"),"PREPARE",11,1,false);return p;}

    static Path[] prepareArtifacts(Fixture f)throws Exception{Path a=f.base.resolve("synthetic-prepare-app.apk"),t=f.base.resolve("synthetic-prepare-test.apk");E9TestFiles.put(a,PREP_APP);E9TestFiles.put(t,PREP_TEST);return new Path[]{a,t};}

    static E9DeploymentGate gate(DeployPort p)throws Exception{return new E9DeploymentGate(p,"D:/Android/SDK/platform-tools/adb.exe","HA1Q6WXR");}

    static void d01(Path oldClasses,Path oldSupport)throws Exception{

        Fixture f=new Fixture("D01");Path unknown=f.device.resolve("e4a_output_budget/legacy-acceptance/unsupported/policy.revoked");E9TestFiles.put(unknown,"UNKNOWN_SCHEMA_REVOKED".getBytes(StandardCharsets.US_ASCII));

        try(URLClassLoader old=new URLClassLoader(new URL[]{oldClasses.toUri().toURL(),oldSupport.toUri().toURL()},null)){

            Class<?> platform=Class.forName("com.videokit.spike.e4.E5AFinalObservation$Platform",true,old);Class<?> lease=Class.forName("com.videokit.spike.e4.E4FencedTask$LeaseGuard",true,old);Class<?> allocate=Class.forName("com.videokit.spike.e4.E4Owned$Allocate",true,old);

            Object port=java.lang.reflect.Proxy.newProxyInstance(old,new Class<?>[]{platform},(proxy,method,args)->{

                switch(method.getName()){

                    case "requireRecoveryWriterDead":return null; // Positive old Android history/proc platform substitute.

                    case "existingGuard":Object expected=args[3];Object g=java.lang.reflect.Proxy.newProxyInstance(old,new Class<?>[]{lease},(p,m,a)->m.getName().equals("fileId")?expected:null);Object allocator=java.lang.reflect.Proxy.newProxyInstance(old,new Class<?>[]{allocate},(p,m,a)->g);args[4].getClass().getMethod("allocate",allocate).invoke(args[4],allocator);return null;

                    case "forceMetadata":((FileChannel)args[1]).force(true);return null;

                    case "closeMetadata":((FileChannel)args[1]).close();return null;

                    case "sync":return null; // Directory fsync is a platform shim, not a Windows claim.

                    case "returned":return true;

                    default:throw new UnsupportedOperationException(method.getName());

                }

            });

            Class<?> observer=Class.forName("com.videokit.spike.e4.E5AFinalObservation",true,old);Object instance=observer.getConstructor(Path.class,platform).newInstance(f.device,port);String result=(String)observer.getMethod("observe").invoke(instance);System.out.println("REAL_FROZEN_OLD_READER_RESULT="+result);ok(result.startsWith("FRESH_OBSERVATION_ADMITTED"));ok(Files.exists(unknown));

        }

        DeployPort p=deployPort(f);Path[] files=prepareArtifacts(f);Files.write(files[0],"OLD_REAL_READER_CODE_UNKNOWN_NEW_SCHEMA".getBytes(),StandardOpenOption.TRUNCATE_EXISTING);rejected(()->gate(p).deployPrepare(f.registry,files[0],files[1],p.current));ok(p.installs==0);f.oldUnchanged();

    }

    static void d02()throws Exception{Fixture f=new Fixture("D02");Path[] paths=prepareArtifacts(f);Files.write(paths[0],"SAME_SIGNER_HIGH_VERSION_OLD_CODE_FAKE_ABI_1".getBytes(),StandardOpenOption.TRUNCATE_EXISTING);DeployPort p=deployPort(f);p.candidate=pkg(E9Record.sha(Files.readAllBytes(paths[0])),f.plan.get("test"),"PREPARE",100000,1,false);rejected(()->gate(p).deployPrepare(f.registry,paths[0],paths[1],p.current));ok(p.installs==0&&p.inspectCalls==0);}

    static void d03()throws Exception{Fixture f=new Fixture("D03");Path[] paths=prepareArtifacts(f);DeployPort p=deployPort(f);p.candidate=pkg(f.plan.get("app"),f.plan.get("test"),"ACTIVATION",11,1,false);rejected(()->gate(p).deployPrepare(f.registry,paths[0],paths[1],p.current));ok(p.installs==0);DeployPort mismatch=deployPort(f);rejected(()->gate(mismatch).deployPrepare(f.registry,paths[1],paths[0],mismatch.current));ok(mismatch.installs==0);}

    static void d04()throws Exception{Fixture f=new Fixture("D04");Path[] paths=prepareArtifacts(f);DeployPort p=deployPort(f);E9DeploymentGate.PackageInfo expected=p.current;p.current=pkg(expected.appSha,expected.testSha,expected.role,10,0,true);rejected(()->gate(p).deployPrepare(f.registry,paths[0],paths[1],expected));ok(p.installs==0);ActorRun a=f.actor(1,"NONE");a.identifyAndBind("NONE");DeployPort q=deployPort(f);rejected(()->gate(q).deployPrepare(f.registry,paths[0],paths[1],q.current));ok(q.installs==0);}

    static void d05()throws Exception{Fixture f=new Fixture("D05");Path[] paths=prepareArtifacts(f);DeployPort p=deployPort(f);E9DeploymentGate g=gate(p);g.deployPrepare(f.registry,paths[0],paths[1],p.current);ok(p.installs==2);for(List<String> command:p.commands)for(String forbidden:new String[]{"-d","uninstall","clear","force-stop"})ok(!command.contains(forbidden));rejected(()->g.deployPrepare(f.registry,paths[0],paths[1],p.current));ok(p.installs==2);hostDispatch(f,paths);}

    static void hostDispatch(Fixture f,Path[] paths)throws Exception{

        int[] installs={0},calls={0};boolean[] replaceAtDispatch={false};E9HostDeployment.Commands os=(argv,max)->{calls[0]++;String result;String all=String.join(" ",argv);

            if(all.contains(" install -r ")){ok(argv.size()==6);installs[0]++;result="Success\n";}

            else if(all.contains("dump badging")){boolean test=argv.get(argv.size()-1).equals(paths[1].toString());result="package: name='"+(test?"com.videokit.app.test":"com.videokit.app")+"' versionCode='11' versionName='D1-E9-PREPARE'\n";}

            else if(all.contains("apksigner.jar"))result="Signer #1 certificate SHA-256 digest: "+SIGNER+"\n";

            else if(all.contains("xmltree"))result="videokit.e9.role \"PREPARE\" videokit.e9.gateAbi\n";

            else if(all.contains(" pm path "))result="package:/data/app/"+(argv.get(argv.size()-1).endsWith(".test")?"test":"app")+"/base.apk\n";

            else if(all.contains(" sha256sum ")){boolean test=argv.get(argv.size()-1).contains("/test/");result=(installs[0]>=2?f.plan.get(test?"test":"app"):E9TestFiles.digest(test?"legacy-test":"legacy-app"))+"  "+argv.get(argv.size()-1)+"\n";}

            else if(all.contains(" dumpsys package "))result="userId="+(argv.get(argv.size()-1).endsWith(".test")?"10222":"10221")+"\nversionCode="+(installs[0]>=2?"11":"10")+" minSdk=31\n";

            else if(all.contains(" ps -A ")){if(replaceAtDispatch[0])Files.write(paths[0],"SYNTHETIC_NOT_AN_APPROVAL_legacy-app".getBytes(StandardCharsets.US_ASCII),StandardOpenOption.TRUNCATE_EXISTING);result="PID UID NAME\n1 0 init\n";}

            else throw new IOException("UNEXPECTED_PLATFORM_COMMAND:"+all);return result.getBytes(StandardCharsets.UTF_8);};

        DeployPort expected=deployPort(f);E9HostDeployment port=new E9HostDeployment(os,Paths.get("D:/Android/SDK"),Paths.get("D:/Android/Android Studio/jbr"),expected.current,expected.candidate);

        rejected(()->port.dispatch(List.of(port.adb(),"-s","HA1Q6WXR","uninstall","com.videokit.app")));ok(calls[0]==0);

        new E9DeploymentGate(port,port.adb(),"HA1Q6WXR").deployPrepare(f.registry,paths[0],paths[1],expected.current);ok(installs[0]==2&&calls[0]>10);
        installs[0]=0;replaceAtDispatch[0]=true;
        E9HostDeployment changed=new E9HostDeployment(os,Paths.get("D:/Android/SDK"),Paths.get("D:/Android/Android Studio/jbr"),expected.current,expected.candidate);
        rejected(()->new E9DeploymentGate(changed,changed.adb(),"HA1Q6WXR").deployPrepare(f.registry,paths[0],paths[1],expected.current));ok(installs[0]==0);Files.write(paths[0],PREP_APP,StandardOpenOption.TRUNCATE_EXISTING);


    }

    static void d06()throws Exception{Fixture f=new Fixture("D06");Path[] paths=prepareArtifacts(f);DeployPort p=deployPort(f);p.postMismatch=true;rejected(()->gate(p).deployPrepare(f.registry,paths[0],paths[1],p.current));ok(p.installs==2);}

    static void d07()throws Exception{rejected(E9Phase::requireProduct);rejected(E9Phase::requireObservationRole);rejected(E9Phase::rejectLegacyRecovery);ok(E9BuildPolicy.role().equals("PREPARE")&&E9BuildPolicy.CATALOG_SHA.equals("ABSENT"));Fixture f=new Fixture("D07");Path fresh=f.base.resolve("must-not-create");E4FencedTask t=new E4FencedTask(fresh,E9TestFiles.uuid("task"),p->{throw new AssertionError("NO_SYNC_ALLOWED");},new E4FencedTask.LeasePolicy(){public void createNew(Path p,E5BGuard.Role r,E4Owned<E4FencedTask.LeaseGuard> h){throw new AssertionError("NO_GUARD_ALLOWED");}public void openExisting(Path p,E5BGuard.Role r,String e,E5BFileId id,E4Owned<E4FencedTask.LeaseGuard> h){throw new AssertionError("NO_GUARD_ALLOWED");}});rejected(t::initialize);ok(!Files.exists(fresh));E4OutputBudget b=new E4OutputBudget(f.device.resolve("e4a_output_budget"),E5N2Recovery.BUDGET,E9TestFiles.uuid("newtask"),"D1-E4A-E9-SYNTHETIC",p->{});rejected(b::reserve);ok(!Files.exists(f.device.resolve("e4a_output_budget/operation.pending")));

        E5AFinalObservation.Platform disabled=(E5AFinalObservation.Platform)java.lang.reflect.Proxy.newProxyInstance(E9ProductionSelfCheck.class.getClassLoader(),new Class<?>[]{E5AFinalObservation.Platform.class},(proxy,method,args)->{throw new AssertionError("OLD_PLATFORM_IO_REACHED");});

        ok(new E5AFinalObservation(f.device,disabled).observe().startsWith("BLOCKED"));ok(new E5N2Recovery(f.device,disabled).execute(true).status.equals("BLOCKED"));f.oldUnchanged();}

    static void d08()throws Exception{Fixture f=new Fixture("D08");E9Catalog c=f.complete();E9Record release=activationRelease(f,c);rejected(()->f.registry.recordActivationRelease(changed(release,"role","REVOKED_EXTERNAL_JSON_IS_NOT_DEPLOYED_CODE",8192)));Path[] paths=prepareArtifacts(f);DeployPort p=deployPort(f);rejected(()->gate(p).deployActivation(f.registry,release,paths[0],paths[1]));ok(p.installs==0);f.oldUnchanged();}

    static void d09()throws Exception{Fixture f=new Fixture("D09");E9Catalog c=f.complete();E9Record release=activationRelease(f,c);f.registry.recordActivationRelease(release);Path a=f.base.resolve("synthetic-activation-app.apk"),t=f.base.resolve("synthetic-activation-test.apk");E9TestFiles.put(a,"SYNTHETIC_ACTIVATION_APP".getBytes());E9TestFiles.put(t,"SYNTHETIC_ACTIVATION_TEST".getBytes());DeployPort p=deployPort(f);p.current=p.candidate;p.candidate=pkg(release.get("app"),release.get("test"),"ACTIVATION",12,1,false);String before=f.registry.head();gate(p).deployActivation(f.registry,release,a,t);ok(p.installs==2&&f.registry.head().equals(before));rejected(E9Phase::requireProduct);f.oldUnchanged();}

    public static void main(String[] args)throws Exception{

        selected=args[0];output=Paths.get(args[1]);reference=Paths.get(args[2]);Files.createDirectories(output);

        try{

            switch(selected){case "A01":a01();break;case "A02":a02();break;case "A03":a03();break;case "A04":a04();break;case "A05":a05();break;case "A06":a06();break;case "A07":a07();break;case "A08":a08();break;case "A09":a09();break;case "A10":a10();break;case "A11":a11();break;case "A12":a12();break;case "A13":a13();break;case "A14":a14();break;case "A15":a15();break;case "A16":a16();break;case "A17":a17();break;case "A18":a18();break;case "A19":a19();break;case "A20":a20();break;case "A21":case "A21-pending":case "A21-guard":case "A21-ledger":case "A21-close":a21();break;case "A22":a22();break;case "A23":a23();break;case "D01":d01(Paths.get(args[3]),Paths.get(args[4]));break;case "D02":d02();break;case "D03":d03();break;case "D04":d04();break;case "D05":d05();break;case "D06":d06();break;case "D07":d07();break;case "D08":d08();break;case "D09":d09();break;default:throw new IllegalArgumentException("CASE");}

            System.out.println("PASS actual_production_group="+selected+" assertions="+assertions+" androidDeviceCalls=0 realMediaReads=0 nativeExecution=0 syntheticOnly=true");

        }finally{int i=0;for(E9TestFiles io:IO){Path trace=output.resolve(selected+"-platform-trace-"+i+++".txt");Files.write(trace,io.trace,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);io.closeNativeFacsimilesAfterAssertions();}}

    }

}

