package videokit.e1;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.lang.foreign.*;
import java.lang.invoke.MethodHandle;
import java.lang.management.ManagementFactory;
import java.lang.ref.Reference;
import java.lang.reflect.Field;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.util.*;

public final class JavaHelper {
    static final int FRAME=8192;static byte[] key;
    static void require(boolean b,String error){if(!b)throw new IllegalStateException(error);}
    static String pack(String... p){return String.join("\t",Arrays.stream(p).map(x->Base64.getEncoder().encodeToString(x.getBytes(StandardCharsets.UTF_8))).toList());}
    static String[] unpack(String s){return Arrays.stream(s.split("\t",-1)).map(x->new String(Base64.getDecoder().decode(x),StandardCharsets.UTF_8)).toArray(String[]::new);}
    static String bounded(Reader r)throws IOException{StringBuilder b=new StringBuilder();for(int i=0;i<=FRAME;i++){int c=r.read();if(c<0)return b.length()==0?null:b.toString();if(c=='\n')return b.toString().replace("\r","");b.append((char)c);}throw new IOException("FRAME_LIMIT");}
    static String[] admitted(String raw)throws Exception{
        int at=raw.lastIndexOf('\t');require(at>0,"NO_CAPABILITY");String body=raw.substring(0,at);Mac m=Mac.getInstance("HmacSHA256");m.init(new SecretKeySpec(key,"HmacSHA256"));
        require(MessageDigest.isEqual(m.doFinal(body.getBytes(StandardCharsets.UTF_8)),HexFormat.of().parseHex(raw.substring(at+1))),"BAD_CAPABILITY");return unpack(body);
    }
    static Path safe(Path root,String name)throws IOException{require(name.matches("[A-Za-z0-9_.-]{1,64}")&&!name.contains(".."),"FIXTURE_NAME");Path p=root.resolve(name);require(!Files.isSymbolicLink(p),"SYMLINK_DENIED");return p;}
    record OpenedInfo(String identity,String lengthBytes,String lastWriteTime100ns){}
    interface IdentityQuery { OpenedInfo inspect(FileDescriptor descriptor)throws Exception; }
    static final class BridgeBlocked extends Exception {
        final String reason;
        BridgeBlocked(String reason){super(reason);this.reason=reason;}
    }
    static IdentityQuery bridge(){return bridge("handle","GetFileInformationByHandle");}
    // Package-private injection seam is only used by the independent owned-file
    // probe. Neither the wire protocol nor an environment field chooses it.
    static IdentityQuery bridge(String field,String symbol){
        try{return new OpenedFdBridge(field,symbol);}
        catch(BridgeBlocked e){return descriptor->{throw e;};}
        catch(Throwable e){return descriptor->{throw new BridgeBlocked("BRIDGE_INITIALIZATION_UNAVAILABLE");};}
    }
    static final class OpenedFdBridge implements IdentityQuery {
        final Field handleField;final MethodHandle query,attributes;long pathMetadataQueries;
        OpenedFdBridge(String fieldName,String symbol)throws Exception {
            if(!System.getProperty("os.name","").startsWith("Windows")||
               !Set.of("amd64","x86_64").contains(System.getProperty("os.arch",""))||
               !System.getProperty("java.version","").equals("21.0.10")||
               !System.getProperty("java.vendor","").contains("JetBrains"))throw new BridgeBlocked("FIXED_JBR_WINDOWS_X64_REQUIRED");
            var flags=ManagementFactory.getRuntimeMXBean().getInputArguments();
            if(!flags.contains("--enable-preview")||!flags.contains("--enable-native-access=ALL-UNNAMED"))throw new BridgeBlocked("PREVIEW_AND_NATIVE_ACCESS_FLAGS_REQUIRED");
            handleField=FileDescriptor.class.getDeclaredField(fieldName);
            if(handleField.getType()!=long.class||!handleField.trySetAccessible())throw new BridgeBlocked("JAVA_IO_HANDLE_FIELD_UNAVAILABLE");
            if(ValueLayout.ADDRESS.byteSize()!=8||ByteOrder.nativeOrder()!=ByteOrder.LITTLE_ENDIAN)throw new BridgeBlocked("WINDOWS_X64_ABI_REQUIRED");
            // One process-lifetime kernel32 lookup. This arena owns no media
            // HANDLE; borrowed descriptor addresses are never assigned a cleanup.
            SymbolLookup library=SymbolLookup.libraryLookup("kernel32.dll",Arena.global());
            var address=library.find(symbol).orElseThrow(()->new BridgeBlocked("GET_FILE_INFORMATION_SYMBOL_UNAVAILABLE"));
            query=Linker.nativeLinker().downcallHandle(address,FunctionDescriptor.of(ValueLayout.JAVA_INT,ValueLayout.ADDRESS,ValueLayout.ADDRESS));
            var attrs=library.find("GetFileAttributesW").orElseThrow(()->new BridgeBlocked("GET_FILE_ATTRIBUTES_SYMBOL_UNAVAILABLE"));
            attributes=Linker.nativeLinker().downcallHandle(attrs,FunctionDescriptor.of(ValueLayout.JAVA_INT,ValueLayout.ADDRESS));
        }
        int pathAttributes(Path path)throws Exception {
            String value=path.toString();if(value.length()>1024)throw new BridgeBlocked("PATH_LIMIT");
            try(Arena memory=Arena.ofConfined()) {
                MemorySegment text=memory.allocate((value.length()+1L)*2,2);
                for(int i=0;i<value.length();i++)text.set(ValueLayout.JAVA_CHAR,i*2L,value.charAt(i));
                text.set(ValueLayout.JAVA_CHAR,value.length()*2L,'\0');pathMetadataQueries++;
                try{return (int)attributes.invokeExact(text);}
                catch(Throwable e){throw new BridgeBlocked("PATH_ATTRIBUTES_UNAVAILABLE");}
            }
        }
        public OpenedInfo inspect(FileDescriptor descriptor)throws Exception {
            // The enclosing Handle monitor protects this original descriptor
            // against our own close. Neither path attributes nor a reopened FD
            // are accepted as evidence for this query.
            try {
                if(descriptor==null||!descriptor.valid())throw new BridgeBlocked("ORIGINAL_DESCRIPTOR_NOT_VALID");
                long borrowed=handleField.getLong(descriptor);
                if(borrowed==0||borrowed==-1)throw new BridgeBlocked("ORIGINAL_HANDLE_NOT_VALID");
                try(Arena memory=Arena.ofConfined()) {
                    MemorySegment information=memory.allocate(52,4);
                    int ok;
                    try{ok=(int)query.invokeExact(MemorySegment.ofAddress(borrowed),information);}
                    catch(Throwable e){throw new BridgeBlocked("GET_FILE_INFORMATION_CALL_UNAVAILABLE");}
                    if(ok==0)throw new BridgeBlocked("GET_FILE_INFORMATION_FAILED");
                    int volume=information.get(ValueLayout.JAVA_INT,28),high=information.get(ValueLayout.JAVA_INT,44),low=information.get(ValueLayout.JAVA_INT,48);
                    long size=(Integer.toUnsignedLong(information.get(ValueLayout.JAVA_INT,32))<<32)|Integer.toUnsignedLong(information.get(ValueLayout.JAVA_INT,36));
                    long write=(Integer.toUnsignedLong(information.get(ValueLayout.JAVA_INT,24))<<32)|Integer.toUnsignedLong(information.get(ValueLayout.JAVA_INT,20));
                    return new OpenedInfo(Integer.toUnsignedString(volume)+":"+Integer.toUnsignedString(high)+":"+Integer.toUnsignedString(low),Long.toUnsignedString(size),Long.toUnsignedString(write));
                }
            } finally {Reference.reachabilityFence(descriptor);}
        }
    }
    static final class JsonStrings {
        final String text;int at;
        JsonStrings(String text){require(text.length()<=8192,"INPUT_BINDINGS_LIMIT");this.text=text;}
        void space(){while(at<text.length()&&Character.isWhitespace(text.charAt(at)))at++;}
        void token(char expected){space();require(at<text.length()&&text.charAt(at++)==expected,"INPUT_BINDINGS_JSON");}
        String string(){
            token('"');StringBuilder out=new StringBuilder();boolean ended=false;
            while(at<text.length()) {
                char c=text.charAt(at++);if(c=='"'){ended=true;break;}
                require(c>=32,"INPUT_BINDINGS_JSON");
                if(c=='\\') {
                    require(at<text.length(),"INPUT_BINDINGS_JSON");char escape=text.charAt(at++);
                    if(escape=='u'){require(at+4<=text.length(),"INPUT_BINDINGS_JSON");c=(char)Integer.parseInt(text.substring(at,at+4),16);at+=4;}
                    else if(escape=='"'||escape=='\\'||escape=='/')c=escape;
                    else throw new IllegalStateException("INPUT_BINDINGS_ESCAPE");
                }
                require(c!=0&&c!='\r'&&c!='\n',"INPUT_BINDINGS_PATH_CHARACTER");out.append(c);
            }
            require(ended,"INPUT_BINDINGS_JSON");return out.toString();
        }
        Map<String,String> object(){
            Map<String,String> result=new LinkedHashMap<>();token('{');
            for(int i=0;i<3;i++){if(i>0)token(',');String key=string();token(':');String value=string();require(!result.containsKey(key),"INPUT_BINDINGS_DUPLICATE");result.put(key,value);}
            token('}');space();require(at==text.length()&&result.keySet().equals(Set.of("L.bin","C.bin","Z.bin")),"EXACT_INPUT_ALIASES_REQUIRED");return result;
        }
    }
    static final class Namespace {
        final Path root;final OpenedFdBridge paths;final Map<String,Path> inputs=new HashMap<>();
        Namespace(Path root,Path base,IdentityQuery query,String mode,String encoded)throws Exception {
            require(query instanceof OpenedFdBridge,"BLOCKED_VERSION_NOT_PROVEN");paths=(OpenedFdBridge)query;
            require(mode.equals("SYNTHETIC")||mode.equals("CANDIDATE_IO"),"NAMESPACE_MODE");this.root=normalized(root);
            Path allowed=base.resolve(mode.equals("SYNTHETIC")?"selfcheck":"runs").toAbsolutePath().normalize();
            require(this.root.startsWith(allowed)&&!this.root.equals(allowed),"ROOT_NAMESPACE_DENIED");checked(this.root,true);
            if(encoded.isEmpty()) {
                require(mode.equals("SYNTHETIC"),"EXACT_INPUT_BINDINGS_REQUIRED");
                for(String alias:List.of("L.bin","C.bin","Z.bin"))inputs.put(alias,this.root.resolve(alias));
            } else {
                require(encoded.length()<=12288,"INPUT_BINDINGS_LIMIT");
                String json=StandardCharsets.UTF_8.newDecoder().decode(ByteBuffer.wrap(Base64.getDecoder().decode(encoded))).toString();
                for(var entry:new JsonStrings(json).object().entrySet()) {
                    Path input=normalized(Path.of(entry.getValue()));
                    if(mode.equals("SYNTHETIC"))require(input.startsWith(base.resolve("selfcheck").toAbsolutePath().normalize()),"SYNTHETIC_INPUT_SCOPE_DENIED");
                    else require(!input.startsWith(this.root),"INPUT_OUTPUT_NAMESPACE_OVERLAP");
                    inputs.put(entry.getKey(),input);
                }
            }
        }
        static Path normalized(Path path){
            require(path.isAbsolute()&&path.equals(path.normalize()),"ABSOLUTE_NORMAL_INPUT_PATH_REQUIRED");
            String value=path.toString();require(value.matches("[A-Za-z]:\\\\.*")&&!value.substring(2).contains(":"),"LOCAL_DRIVE_PATH_ONLY");
            require(path.getNameCount()<=64,"PATH_DEPTH_LIMIT");return path;
        }
        void checked(Path path,boolean directory)throws Exception {
            normalized(path);int count=0;int finalAttributes=0;
            for(Path current=path;current!=null;current=current.getParent()) {
                require(++count<=66,"PATH_DEPTH_LIMIT");int attrs=paths.pathAttributes(current);
                if(attrs==-1)throw new BridgeBlocked("PATH_METADATA_UNPROVEN");
                require((attrs&0x400)==0,"REPARSE_PATH_DENIED");if(count==1)finalAttributes=attrs;
            }
            require(((finalAttributes&0x10)!=0)==directory,"PATH_ROLE_MISMATCH");
        }
        Path input(String alias)throws Exception {
            require(inputs.containsKey(alias),"INPUT_ALIAS_NOT_ADMITTED");Path result=inputs.get(alias);checked(result,false);return result;
        }
        Path metadataDirectory(String name)throws Exception {Path result=safe(root,name);checked(result,true);return result;}
        Path metadataFile(Path directory,String name)throws Exception {Path result=safe(directory,name);checked(result,false);return result;}
    }
    static final class Handle {
        final RandomAccessFile file;FileDescriptor descriptor;final IdentityQuery identityQuery;final String object=UUID.randomUUID().toString(),ticket=UUID.randomUUID().toString();
        String state="OWNED_OPEN_RETRYABLE",first="",heldFault="";int attempts,calls,reads,seeks;long revision;boolean held;
        String identityStatus="NOT_QUERIED",identityFailure="";int identityQueries;OpenedInfo opened;
        Handle(Path path,IdentityQuery query)throws IOException{file=new RandomAccessFile(path.toFile(),"r");identityQuery=query;}
        synchronized String view(){return object+"|"+ticket+"|"+state+"|"+attempts+"|"+calls+"|"+revision+"|"+first;}
        synchronized String openReceipt(){
            require(state.equals("OWNED_OPEN_RETRYABLE"),"OBJECT_NOT_OPEN");
            if(identityStatus.equals("NOT_QUERIED")) {
                identityQueries++;
                try{descriptor=file.getFD();opened=identityQuery.inspect(descriptor);identityStatus="PROVEN";}
                catch(Exception e){identityStatus="BLOCKED_VERSION_NOT_PROVEN";identityFailure=e instanceof BridgeBlocked?((BridgeBlocked)e).reason:"OPENED_IDENTITY_QUERY_UNAVAILABLE";}
                finally{Reference.reachabilityFence(descriptor);Reference.reachabilityFence(file);}
            }
            return (opened==null?"-1|-1|":opened.lengthBytes()+"|"+opened.lastWriteTime100ns()+"|"+opened.identity())+"|"+view()+"|"+identityStatus;
        }
        synchronized void begin(long expected,String fault,boolean hold)throws Exception{
            require(expected==revision,"STALE_REVISION");require(state.equals("OWNED_OPEN_RETRYABLE"),"CLOSE_NOT_RETRYABLE");require(attempts<3,"EXHAUSTED");attempts++;revision++;state="IN_FLIGHT";heldFault=fault;held=hold;if(!hold)perform();
        }
        synchronized void perform(){
            require(state.equals("IN_FLIGHT"),"NO_CLOSE_ADMISSION");held=false;
            if(heldFault.equals("before")){state="OWNED_OPEN_RETRYABLE";if(first.isEmpty())first="INJECTED_BEFORE_DELEGATE";}
            else{calls++;try{file.close();state=heldFault.equals("unknown")?"UNKNOWN":"CLOSED_PROVEN";if(!heldFault.equals("none")&&first.isEmpty())first=heldFault.equals("unknown")?"INJECTED_RESULT_UNKNOWN":"INJECTED_ACK_LOST";}
                catch(IOException e){state="UNKNOWN";if(first.isEmpty())first="NATIVE_CLOSE_UNKNOWN";}}
            revision++;
        }
    }
    public static void main(String[] args)throws Exception{
        require(args.length==2&&args[0].equals("--admitted-helper"),"EXPLICIT_HELPER_REQUIRED");
        key=Base64.getDecoder().decode(System.getenv().getOrDefault("E2C_KEY",""));require(key.length==32,"NO_ADMISSION_KEY");
        Path root=Path.of(args[1]);Path base=Path.of(JavaHelper.class.getProtectionDomain().getCodeSource().getLocation().toURI()).getParent().getParent();
        IdentityQuery identityQuery=bridge();Namespace namespace=new Namespace(root,base,identityQuery,System.getenv().getOrDefault("E2C_NAMESPACE_MODE","SYNTHETIC"),System.getenv().getOrDefault("E2C_INPUT_BINDINGS",""));
        String owner=UUID.randomUUID().toString();Map<String,Handle> handles=new HashMap<>();Map<String,String[]> cache=new HashMap<>();int cacheBytes=0;long input=0;int inputCalls=0;
        Reader reader=new InputStreamReader(System.in,StandardCharsets.UTF_8);PrintWriter out=new PrintWriter(System.out,true,StandardCharsets.UTF_8);
        for(;;){String raw=bounded(reader);if(raw==null)return;String[] p=admitted(raw);String id=p[0],verb=p[1],row=p[2];require(id.startsWith(row+"/"),"BAD_SLOT");
            if(cache.containsKey(id)){String[] old=cache.get(id);require(old[0].equals(raw),"CAPABILITY_REPLAY_CONFLICT");out.println(old[1]);continue;}
            require(cache.size()<512&&cacheBytes+raw.length()+2048<196608,"CACHE_LIMIT");String response;
            try{String result="";
                switch(verb){
                    case "HELLO":result=owner+"|"+ProcessHandle.current().pid()+"|"+System.getProperty("java.runtime.version");break;
                    case "OPEN":{
                        require(p[6].equals("N")&&handles.size()<64&&!handles.containsKey(p[7])&&handles.values().stream().filter(x->!x.state.equals("CLOSED_PROVEN")).count()<2,"HANDLE_LIMIT");
                        Path path=namespace.input(p[8]);Handle h=new Handle(path,identityQuery);handles.put(p[7],h);
                        result=h.openReceipt();break;}
                    case "READ":case "READ_ZERO":{
                        Handle h=handles.get(p[7]);int n=Integer.parseInt(p[9]),cap=Integer.parseInt(p[10]);long offset=Long.parseLong(p[8]);
                        require(p[6].equals("I")&&offset>=0&&n>=0&&n<=65536&&cap>0&&input+n<=1573522&&inputCalls<59,"INPUT_LIMIT");input+=n;inputCalls++;
                        int got=0;byte[] b=new byte[Math.min(n,cap)];synchronized(h){require(h.state.equals("OWNED_OPEN_RETRYABLE"),"OBJECT_NOT_OPEN");if(!verb.equals("READ_ZERO")&&n>0){h.file.seek(offset);h.seeks++;got=h.file.read(b);h.reads++;}}
                        MessageDigest digest=MessageDigest.getInstance("SHA-256");if(got>0)digest.update(b,0,got);
                        result=got+"|"+HexFormat.of().formatHex(digest.digest())+"|"+(got>0&&got<=32?Base64.getEncoder().encodeToString(Arrays.copyOf(b,got)):"")+"|"+h.reads+"|"+h.seeks;break;}
                    case "CLOSE":case "HOLD_CLOSE":{
                        require(p[6].equals("N"),"CLOSE_KIND");Handle h=handles.get(p[7]);h.begin(Long.parseLong(p[8]),p[9],verb.equals("HOLD_CLOSE"));result=h.view();break;}
                    case "GATE_CLOSE":{Handle h=handles.get(p[7]);require(p[6].equals("N")&&h.held,"NO_HELD_CLOSE");h.perform();result=h.view();break;}
                    case "RECOVER":{
                        Path directory=namespace.metadataDirectory(p[7]);long seq=0;byte[] payload=null;
                        for(int slot=0;slot<2;slot++){Path f=safe(directory,"state"+slot+".slot");if(!Files.exists(f))continue;f=namespace.metadataFile(directory,"state"+slot+".slot");require(Files.size(f)==8192,"JOURNAL_CORRUPT");byte[] b=Files.readAllBytes(f);ByteBuffer header=ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN);long s=header.getLong();int n=header.getInt();require(n>=0&&n<=8144&&s>0,"JOURNAL_CORRUPT");byte[] record=Arrays.copyOfRange(b,48,48+n);MessageDigest digest=MessageDigest.getInstance("SHA-256");digest.update(b,0,16);digest.update(record);require(MessageDigest.isEqual(digest.digest(),Arrays.copyOfRange(b,16,48)),"JOURNAL_CORRUPT");if(s>seq){seq=s;payload=record;}}
                        require(payload!=null&&payload.length<=4400,"RECOVERY_FRAME");String encoded=Base64.getEncoder().encodeToString(payload);
                        for(String type:new String[]{"RECOVERY_QNEW","RECOVERY_QREPLAY"}){
                            out.println(pack("CALLBACK",id,type,Long.toString(seq),encoded));String[] answer=admitted(bounded(reader));require(answer[1].equals("QUERY_RESULT")&&answer[2].equals(row),"RECOVERY_CALLBACK");
                        }
                        result=seq+"|"+encoded;break;}
                    case "EXIT":out.println(pack(id,"OK",owner));return;
                    default:throw new IllegalStateException("UNKNOWN_VERB");
                }
                response=pack(id,"OK",result);
            }catch(Exception e){response=pack(id,"ERROR",e instanceof BridgeBlocked?"BLOCKED_VERSION_NOT_PROVEN":e instanceof IllegalStateException?e.getMessage():"NATIVE_BACKEND_ERROR");}
            require(response.length()<8192,"RESPONSE_LIMIT");cache.put(id,new String[]{raw,response});cacheBytes+=raw.length()+response.length();out.println(response);
        }
    }
}
