package com.videokit.spike.e4;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

/** Original PC process/pipe owner and persistent, identified local custodian. No process cancellation. */
public final class E9PcSupervisor {
    public interface Decoder {Object decode(byte[] original)throws Exception;}
    public interface Hooks {void at(String point,String operation)throws Exception;}
    public interface Cleanup {E9Record run(E9Record command)throws Exception;}
    public interface OriginalAuthority {boolean originalResourcesReturned();}
    private static final Map<String,E9PcSupervisor> LIVE=new ConcurrentHashMap<>();
    public static final int MAX_ACCEPTS=128;
    public static final long CONTROL_NS=5_000_000_000L,GENERAL_NS=55_000_000_000L;
    private final Hooks hooks;private final List<Operation> originals=new ArrayList<>();private final List<Remote> remote=new ArrayList<>();
    private final Path archiveRoot;
    private final E4Owned<ServerSocket> listener;private final List<E4Owned<Accepted>> clients=new ArrayList<>();private final Thread custodian;
    public final String handle=UUID.randomUUID().toString(),scope;public final long pcPid=ProcessHandle.current().pid();public volatile int port;
    private volatile String cleanupPin;private volatile Object authority;private volatile Cleanup cleanup;private volatile OriginalAuthority authorityResources;private volatile boolean ingressClosed,dependenciesStopped,custodianReturned,listenerCloseAttempted,statusTransportUncertain;private volatile String reason="NONE";
    private E9Record transferAck,closedAck;private int accepted,acceptReservations;private volatile boolean admissionExhausted;private volatile E9Registry.Store registryStore;private volatile E9Registry registryAuthority;
    public E9PcSupervisor(String scope)throws Exception{this(scope,(p,h)->{});}
    public E9PcSupervisor(String scope,Hooks hooks)throws Exception{
        this(scope,hooks,Paths.get("D:/CodexProjects/VideoKit/docs/tester/VideoKit-pc-archives"));
    }
    E9PcSupervisor(String scope,Hooks hooks,Path archiveRoot)throws Exception{
        this.scope=scope;this.hooks=hooks;this.archiveRoot=archiveRoot.resolve(handle);listener=new E4Owned<>(handle,socket->{hooks.at("LISTENER_CLOSE_BEFORE",handle);socket.close();hooks.at("LISTENER_CLOSE_AFTER",handle);});
        custodian=new Thread(this::supervise,"E9-PC-custodian-"+handle);custodian.setDaemon(false);LIVE.put(handle,this);
        Throwable initialization=null;
        try{listener.allocate(ServerSocket::new);listener.initialize(socket->{socket.bind(new InetSocketAddress(InetAddress.getByName("127.0.0.1"),0),8);port=socket.getLocalPort();socket.setSoTimeout(100);});}
        catch(Throwable t){initialization=t;ingressClosed=true;stopDependencies("PC_LISTENER_INITIALIZATION_FAILED");}
        custodian.start();System.err.println("E9_PC_SUPERVISOR_READY handle="+handle+" pcPid="+pcPid+" address=127.0.0.1:"+port+" scope="+scope);
        if(initialization!=null)throw new IOException("E9_PC_SUPERVISOR_INITIALIZATION handle="+handle,initialization);
    }
    public void retainAuthority(Object authority,Cleanup cleanup){this.authority=Objects.requireNonNull(authority);this.cleanup=cleanup;}
    public void retainAuthority(Object authority,Cleanup cleanup,OriginalAuthority resources){retainAuthority(authority,cleanup);authorityResources=Objects.requireNonNull(resources);}
    public void authorizeCleanup(String existingApprovedConfigurationPin)throws Exception{E9Record.digest(existingApprovedConfigurationPin);cleanupPin=existingApprovedConfigurationPin;}
    /** Register the real Store before its first filesystem operation, even if registry construction fails. */
    public synchronized void retainRegistry(E9Registry.Store store){if(registryStore!=null&&registryStore!=store)throw new IllegalStateException("E9_PC_SINGLE_REGISTRY_SCOPE");registryStore=Objects.requireNonNull(store);}
    public synchronized void retainRegistryAuthority(E9Registry registry){if(registryStore==null||registryAuthority!=null&&registryAuthority!=registry)throw new IllegalStateException("E9_PC_REGISTRY_AUTHORITY_SCOPE");registryAuthority=Objects.requireNonNull(registry);}
    private synchronized void changed(){notifyAll();}
    public synchronized void stopDependencies(String why){dependenciesStopped=true;if(reason.equals("NONE"))reason=why;notifyAll();}
    public final class Remote {
        public final String actorHandle;private E9Actor actor;private boolean finished;private String disposition="OPEN_OR_UNKNOWN";
        private Remote(String handle){actorHandle=handle;}
        public void bind(E9Actor value)throws Exception{synchronized(E9PcSupervisor.this){if(!value.handle.equals(actorHandle)||actor!=null&&!actor.hash().equals(value.hash()))throw new IOException("E9_PC_REMOTE_IDENTITY");actor=value;}}
        public void normalFinish(E9Record returned,byte[] finish)throws Exception{synchronized(E9PcSupervisor.this){if(actor==null)throw new IOException("E9_PC_REMOTE_UNBOUND");E9Evidence.archiveComplete(actor,returned.bytes());E9Evidence.finish(actor,returned,finish);finished=true;disposition="NORMAL_FINISH_CONFIRMED";changed();}}
        public void termination(byte[] evidence)throws Exception{synchronized(E9PcSupervisor.this){if(actor==null)throw new IOException("E9_PC_REMOTE_UNBOUND");E9Evidence.termination(actor,evidence);finished=true;disposition="TERMINATED_WITHOUT_JAVA_RETURN";changed();}}
        public boolean returned(){synchronized(E9PcSupervisor.this){return finished;}}
    }
    public synchronized Remote reserveRemote(String actorHandle)throws Exception{if(ingressClosed||dependenciesStopped||remote.size()>=2)throw new IOException("E9_PC_REMOTE_RESERVATION_DENIED");E9Record.uuid(actorHandle);for(Remote r:remote)if(r.actorHandle.equals(actorHandle))throw new IOException("E9_PC_REMOTE_ONCE");Remote value=new Remote(actorHandle);remote.add(value);return value;}
    public final class Operation {
        public final String id=UUID.randomUUID().toString(),label;public final List<String> argv;public final long started,deadline,budget;
        private final int max;private final Decoder decoder;private volatile Object decoded;private volatile boolean decodeEntered,decodeReturned;private final ByteArrayOutputStream bytes=new ByteArrayOutputStream();
        private final E13OperationArchive archive;
        private final E4Owned<InputStream> stdout,stderr;private final E4Owned<OutputStream> stdin;
        private volatile Process process;private volatile Thread starter,reader;private volatile boolean startEntered,startReturned,starterReturned,readerEntered,readerReturned,exitObserved;
        private volatile int exit=-999;private volatile Throwable failure;private volatile String verdict="RUNNING";private volatile long completedAt;
        private Operation(String label,List<String> argv,int max,long budget,Decoder decoder){
            this.label=label;this.argv=List.copyOf(argv);this.max=max;this.budget=budget;this.decoder=decoder;started=System.nanoTime();deadline=started+budget;
            archive=new E13OperationArchive(archiveRoot,id,max);
            stdout=new E4Owned<>(id+":stdout",s->{hooks.at("STDOUT_CLOSE_BEFORE",id);s.close();hooks.at("STDOUT_CLOSE_AFTER",id);});
            stderr=new E4Owned<>(id+":stderr",OutputStreamOrInput::closeInput);
            stdin=new E4Owned<>(id+":stdin",OutputStreamOrInput::closeOutput);
        }
        private synchronized void failed(Throwable t){if(failure==null)failure=t;else failure.addSuppressed(t);if(!verdict.equals("PENDING"))verdict="FAILED";stopDependencies("ORIGINAL_PC_OPERATION_FAILED");}
        private void start(){
            try{
                archive.start(label,argv);startEntered=true;process=new ProcessBuilder(argv).redirectErrorStream(true).start();startReturned=true;archive.started(process.pid());hooks.at("START_RETURNED",id);
            }catch(Throwable t){failed(t);if(!startReturned){starterReturned=true;changed();return;}}
            try{stdin.allocate(()->process.getOutputStream());}catch(Throwable t){failed(t);}
            try{stderr.allocate(()->process.getErrorStream());}catch(Throwable t){failed(t);}
            try{stdout.allocate(()->process.getInputStream());}catch(Throwable t){failed(t);}
            try{if(stdin.original()!=null)stdin.close();}catch(Throwable t){failed(t);}
            try{if(stderr.original()!=null)stderr.close();}catch(Throwable t){failed(t);}
            try{if(stdout.original()!=null){reader=new Thread(this::read,"E9-PC-original-reader-"+id);reader.setDaemon(false);readerEntered=true;reader.start();}else readerReturned=true;}catch(Throwable t){failed(t);}
            try{
                exit=process.waitFor();exitObserved=true;archive.processExit(exit);hooks.at("WAIT_RETURNED",id);
                if(decoder!=null){synchronized(E9PcSupervisor.this){while(!readerReturned)E9PcSupervisor.this.wait(100);}
                    if(failure==null&&exit==0&&stdout.returned()){decodeEntered=true;try{hooks.at("DECODE_BEFORE",id);byte[] raw;synchronized(bytes){raw=bytes.toByteArray();}decoded=decoder.decode(raw);hooks.at("DECODE_AFTER",id);}finally{decodeReturned=true;}}
                }
            }catch(Throwable t){failed(t);}
            finally{starterReturned=true;changed();}
        }
        private void read(){
            try{byte[] buffer=new byte[4096];for(;;){hooks.at("READ_BEFORE",id);int n=stdout.original().read(buffer);hooks.at("READ_AFTER",id);if(n<0){archive.eof();break;}archive.append(buffer,n);synchronized(bytes){if(bytes.size()+n>max)throw new IOException("E9_PC_OUTPUT_BOUND");bytes.write(buffer,0,n);}}}
            catch(Throwable t){failed(t);}
            finally{archive.readerDone();try{stdout.close();}catch(Throwable t){failed(t);}readerReturned=true;changed();}
        }
        private void observeExit(){Process p=process;if(p!=null&&!exitObserved)try{if(p.waitFor(0,TimeUnit.NANOSECONDS)){exit=p.exitValue();exitObserved=true;}}catch(Throwable t){failed(t);}}
        private boolean observedOriginalThreadEnd(Thread original){if(original==null)return true;if(Thread.currentThread()==original||original.isAlive())return false;try{original.join();return true;}catch(InterruptedException e){Thread.currentThread().interrupt();return false;}}
        public boolean resourcesReturned(){return startReturned&&starterReturned&&(!readerEntered||readerReturned)&&exitObserved&&stdin.returned()&&stderr.returned()&&stdout.returned()&&observedOriginalThreadEnd(starter)&&observedOriginalThreadEnd(reader)&&archive.resourcesReturned();}
        public boolean processAlive(){Process p=process;return p!=null&&p.isAlive();}
        public String archiveState(){return archive.state();}
        private Object await()throws Exception{
            synchronized(E9PcSupervisor.this){for(;;){long now=System.nanoTime();if(now-deadline>=0){verdict="PENDING";stopDependencies("PC_ABSOLUTE_RESPONSE_DEADLINE");throw new IOException("E9_PC_RESPONSE_PENDING handle="+handle+" operation="+id+" budgetNanos="+budget);}
                if(resourcesReturned()){
                    completedAt=now;if(verdict.equals("PENDING")||failure!=null||exit!=0||archive.failed()){stopDependencies("PC_ORIGINAL_FAILED_RETURNED");throw new IOException("E9_PC_FAILED_RETURNED operation="+id+" exit="+exit,failure);}verdict="SUCCEEDED";if(decoder!=null)return decoded;synchronized(bytes){return bytes.toByteArray();}
                }
                long left=deadline-now;TimeUnit.NANOSECONDS.timedWait(E9PcSupervisor.this,Math.min(left,100_000_000L));
            }}
        }
        public E9Record status()throws Exception{return new E9Record(E9Record.map("kind","pcOperation","session",handle,"operation",id,"label",label,"verdict",verdict,"startEntered",Boolean.toString(startEntered),"startReturned",Boolean.toString(startReturned),"processAlive",Boolean.toString(processAlive()),"childPid",process==null?"NOT_RETURNED":Long.toString(process.pid()),"exitObserved",Boolean.toString(exitObserved),"starterReturned",Boolean.toString(starterReturned),"readerReturned",Boolean.toString(readerReturned),"decodeEntered",Boolean.toString(decodeEntered),"decodeReturned",Boolean.toString(decodeReturned),"stdin",stdin.state().name(),"stdout",stdout.state().name(),"stderr",stderr.state().name(),"allReturned",Boolean.toString(resourcesReturned()),"budgetNanos",Long.toString(budget),"completedAt",Long.toString(Math.max(0,completedAt))),4096);}
    }
    private static final class OutputStreamOrInput {static void closeInput(InputStream s)throws Exception{s.close();}static void closeOutput(OutputStream s)throws Exception{s.close();}}
    public byte[] run(String label,List<String> argv,int max,long budget,boolean cleanupOnly)throws Exception{return (byte[])runDecoded(label,argv,max,budget,cleanupOnly,null);}
    public Object runDecoded(String label,List<String> argv,int max,long budget,boolean cleanupOnly,Decoder decoder)throws Exception{
        Operation op;synchronized(this){if((dependenciesStopped||ingressClosed)&&!cleanupOnly)throw new IOException("E9_PC_DEPENDENCIES_STOPPED handle="+handle);if(originals.size()>=96||max<1||max>1048576||budget<=0||budget>GENERAL_NS)throw new IOException("E9_PC_PROCESS_BOUND");op=new Operation(label,argv,max,budget,decoder);originals.add(op);op.starter=new Thread(op::start,"E9-PC-original-process-"+op.id);op.starter.setDaemon(false);op.starter.start();}
        try{return op.await();}catch(Exception|Error t){stopDependencies("PC_ORIGINAL_COMMAND_NOT_QUALIFIED");if(t instanceof InterruptedException)Thread.currentThread().interrupt();throw t;}
    }
    private synchronized boolean originalsReturned(){for(Operation o:originals)if(!o.resourcesReturned())return false;for(Remote r:remote)if(!r.returned())return false;for(E4Owned<Accepted> c:clients)if(!c.returned())return false;E9Registry.Store store=registryStore;if(store!=null&&!store.returned())return false;OriginalAuthority resources=authorityResources;return resources==null||resources.originalResourcesReturned();}
    public synchronized E9Record status()throws Exception{int running=0,alive=0,unknown=0;for(Operation o:originals){if(!o.resourcesReturned())running++;if(o.processAlive())alive++;if(o.verdict.equals("PENDING")||o.failure!=null)unknown++;}int remotes=0;String handles="NONE";for(Remote r:remote)if(!r.returned()){remotes++;handles=handles.equals("NONE")?r.actorHandle:handles+","+r.actorHandle;}
        return new E9Record(E9Record.map("kind","pcSupervisor","handle",handle,"scope",scope,"pcPid",Long.toString(pcPid),"port",Integer.toString(port),"ingressClosed",Boolean.toString(ingressClosed),"dependenciesStopped",Boolean.toString(dependenciesStopped),"reason",reason,"operations",Integer.toString(originals.size()),"unreturnedOperations",Integer.toString(running),"liveProcesses",Integer.toString(alive),"nonqualifiedOperations",Integer.toString(unknown),"unresolvedActors",Integer.toString(remotes),"actorHandles",handles,"allOriginalsReturned",Boolean.toString(originalsReturned()),"listenerReturned",Boolean.toString(listener.returned()),"listenerState",listener.state().name(),"accepted",Integer.toString(accepted),"acceptReservations",Integer.toString(acceptReservations),"acceptLimit",Integer.toString(MAX_ACCEPTS),"admissionExhausted",Boolean.toString(admissionExhausted),"registryReturned",registryStore==null?"NOT_STARTED":Boolean.toString(registryStore.returned()),"registryOwned",registryStore==null?"0":Integer.toString(registryStore.registered()),"registryStates",registryStore==null?"NONE":registryStore.originalStates(),"custodianReturned",Boolean.toString(custodianReturned)),4096);
    }
    /** Actual in-process custody ACK. Main may return; this non-daemon original custodian keeps the JVM alive. */
    public E9Record closeIngressAndSupervise()throws Exception{
        boolean interrupted=false;try{synchronized(this){ingressClosed=true;notifyAll();for(;;){if(closedAck!=null)return closedAck;if(transferAck!=null)return transferAck;try{wait(100);}catch(InterruptedException e){interrupted=true;stopDependencies("PC_INGRESS_INTERRUPTED");}}}}finally{if(interrupted)Thread.currentThread().interrupt();}
    }
    public boolean terminated(){return custodianReturned&&!custodian.isAlive()&&listener.returned()&&!LIVE.containsKey(handle);}
    public void awaitOriginalTermination()throws Exception{if(Thread.currentThread()==custodian)throw new IOException("E13_NO_CUSTODIAN_SELF_JOIN");custodian.join();if(!terminated())throw new IOException("E13_ORIGINAL_SUPERVISOR_NOT_RETURNED");}
    public synchronized List<Operation> operations(){return List.copyOf(originals);}
    private E9Record response(String line)throws Exception{
        String[] q=line.split(" ",3);if(q.length<2||!q[1].equals(handle))throw new IOException("E9_PC_STATUS_HANDLE");
        if(q[0].equals("STATUS")&&q.length==2)return status();
        if(q[0].equals("OP")&&q.length==3){for(Operation o:operations())if(o.id.equals(q[2]))return o.status();throw new IOException("E9_PC_OPERATION_HANDLE");}
        if(q[0].equals("CLEANUP")&&q.length==3&&ingressClosed&&authority!=null&&cleanup!=null&&cleanupPin!=null){String[] request=q[2].split(":",2);if(request.length!=2||!java.security.MessageDigest.isEqual(request[0].getBytes(StandardCharsets.US_ASCII),cleanupPin.getBytes(StandardCharsets.US_ASCII)))throw new IOException("E9_PC_CLEANUP_ORIGINAL_CONFIG_PIN");return cleanup.run(E9Record.parse(E9Record.unpack(request[1],16384),16384));}
        throw new IOException("E9_PC_READONLY_OR_CUSTODIAL_CLEANUP_ONLY");
    }
    private static final class Accepted {Socket socket;boolean acceptReturned,noAccept;}
    private synchronized boolean reserveAccept(){
        if(admissionExhausted||listenerCloseAttempted||statusTransportUncertain)return false;
        if(accepted+acceptReservations>=MAX_ACCEPTS){admissionExhausted=true;return false;}acceptReservations++;return true;
    }
    private synchronized void resolveAccept(boolean connectionOrUnknown){
        if(acceptReservations!=1)throw new IllegalStateException("E9_PC_ACCEPT_RESERVATION");acceptReservations--;
        if(connectionOrUnknown)accepted++;if(accepted>=MAX_ACCEPTS){admissionExhausted=true;if(reason.equals("NONE"))reason="PC_ACCEPT_BUDGET_EXHAUSTED";}
        notifyAll();
    }
    private void closeListenerOnce(){
        synchronized(this){if(listenerCloseAttempted)return;listenerCloseAttempted=true;}
        try{if(listener.state()==E4Owned.State.OPEN||listener.state()==E4Owned.State.READY||listener.returned())listener.close();else throw new IOException("E9_PC_LISTENER_OUTCOME_UNKNOWN");}
        catch(Throwable t){stopDependencies("PC_LISTENER_CLOSE_UNKNOWN");}
    }
    private void acceptAndServe()throws Exception{
        if(!reserveAccept())return;
        E4Owned<Accepted> original=new E4Owned<>(handle+":status-client",value->{if(value.socket!=null)value.socket.close();if(!value.acceptReturned&&!value.noAccept)throw new IOException("E9_PC_ACCEPT_OUTCOME_UNKNOWN");});
        synchronized(this){clients.removeIf(E4Owned::returned);clients.add(original);}boolean resolved=false;
        try{
            original.allocate(Accepted::new);
            original.initialize(value->{try{hooks.at("ACCEPT_BEFORE",handle);value.socket=listener.original().accept();value.acceptReturned=true;}catch(SocketTimeoutException expected){value.noAccept=true;throw expected;}});
            // Charge every actual accepted Socket BEFORE parsing/processing or additional platform calls.
            resolveAccept(true);resolved=true;
        }catch(SocketTimeoutException knownNoAccept){resolveAccept(false);resolved=true;return;}
        catch(Exception|Error failure){if(!resolved){resolveAccept(true);resolved=true;}if(original.state()==E4Owned.State.OPEN||original.state()==E4Owned.State.READY||original.state()==E4Owned.State.INITIALIZING)try{original.close();}catch(Throwable close){failure.addSuppressed(close);}throw failure;}
        finally{if(!resolved)resolveAccept(true);}
        if(admissionExhausted){System.err.println("E9_PC_ADMISSION_EXHAUSTED handle="+handle+" pcPid="+pcPid+" accepted="+accepted+" cap="+MAX_ACCEPTS);closeListenerOnce();}
        Socket socket=original.original().socket;Throwable first=null;
        try{
            hooks.at("ACCEPT_UNPROCESSED",handle);socket.setSoTimeout(5000);
            InputStream in=socket.getInputStream();ByteArrayOutputStream line=new ByteArrayOutputStream();for(;;){int b=in.read();if(b<0)throw new EOFException("E9_PC_STATUS_TRUNCATED");if(b=='\n')break;if(line.size()>=16384)throw new IOException("E9_PC_STATUS_LINE_BOUND");line.write(b);}byte[] reply;
            try{reply=response(line.toString(StandardCharsets.US_ASCII)).bytes();}catch(Exception e){reply=new E9Record(E9Record.map("kind","pcRejected","handle",handle,"reason","QUERY_OR_CLEANUP_REJECTED"),1024).bytes();}
            socket.getOutputStream().write(reply);socket.getOutputStream().flush();
        }catch(Exception|Error t){first=t;throw t;}finally{try{original.close();}catch(Exception|Error t){stopDependencies("PC_STATUS_CLIENT_CLOSE_UNKNOWN");if(first!=null)first.addSuppressed(t);else throw t;}}
    }
    private void supervise(){
        try{for(;;){for(Operation o:operations())o.observeExit();boolean closeNow;
            synchronized(this){closeNow=admissionExhausted||ingressClosed&&originalsReturned();}
            if(closeNow)closeListenerOnce();
            boolean terminate=false;synchronized(this){if(ingressClosed){
                if(originalsReturned()&&listener.returned()){
                    closedAck=new E9Record(E9Record.map("kind","pcClosed","handle",handle,"pcPid",Long.toString(pcPid),"allOriginalsReturned","true"),1024);LIVE.remove(handle,this);custodianReturned=true;notifyAll();terminate=true;
                }else if(transferAck==null&&LIVE.get(handle)==this&&(admissionExhausted||!statusTransportUncertain&&(listener.state()==E4Owned.State.OPEN||listener.state()==E4Owned.State.READY))){
                    transferAck=new E9Record(E9Record.map("kind","pcIsolationAck","handle",handle,"pcPid",Long.toString(pcPid),"port",Integer.toString(port),"custodian","NON_DAEMON_ORIGINAL_SUPERVISOR","authority","ORIGINAL_IN_MEMORY_OBJECTS","statusChannel",admissionExhausted?"ACCEPT_BUDGET_EXHAUSTED":"ORIGINAL_LISTENER","listenerState",listener.state().name(),"disposition","PENDING_NO_DEPENDENT_WORK"),2048);stopDependencies("PC_INGRESS_CLOSED_PENDING");notifyAll();System.err.println("E9_PC_ISOLATION_ACCEPTED "+new String(transferAck.bytes(),StandardCharsets.US_ASCII));
                }
            }}
            if(terminate){System.err.println("E9_PC_CLOSED handle="+handle+" actualOriginalReturns=true");return;}
            if(!listenerCloseAttempted&&!statusTransportUncertain&&!admissionExhausted)try{acceptAndServe();}catch(SocketTimeoutException expected){}catch(Throwable t){
                synchronized(this){for(E4Owned<Accepted> c:clients)if(!c.returned()){statusTransportUncertain=true;stopDependencies("PC_STATUS_TRANSPORT_UNKNOWN");}}
                System.err.println("E9_PC_STATUS_FAILURE handle="+handle+" pcPid="+pcPid+" reason="+t.getClass().getSimpleName()+" transportUnknown="+statusTransportUncertain);
            }else synchronized(this){wait(100);}
        }}catch(Throwable t){stopDependencies("PC_CUSTODIAN_EXCEPTION");System.err.println("E9_PC_CUSTODIAN_PENDING handle="+handle+" pcPid="+pcPid+" reason="+t.getClass().getSimpleName());
            for(;;)try{Thread.sleep(1000);}catch(InterruptedException ignored){}
        }
    }
    public static String consoleLine(InputStream input,int max)throws Exception{ByteArrayOutputStream b=new ByteArrayOutputStream();for(;;){int n=input.read();if(n<0)return b.size()==0?null:b.toString(StandardCharsets.US_ASCII);if(n=='\n')return b.toString(StandardCharsets.US_ASCII);if(n=='\r')continue;if(b.size()>=max)throw new IOException("E9_PC_CONSOLE_BOUND");b.write(n);}}
}
