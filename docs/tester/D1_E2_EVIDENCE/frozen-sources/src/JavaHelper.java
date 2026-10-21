package videokit.e1;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
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
    static final class Handle {
        final RandomAccessFile file;final String object=UUID.randomUUID().toString(),ticket=UUID.randomUUID().toString();
        String state="OWNED_OPEN_RETRYABLE",first="",heldFault="";int attempts,calls,reads,seeks;long revision;boolean held;
        Handle(Path path)throws IOException{file=new RandomAccessFile(path.toFile(),"r");}
        String view(){return object+"|"+ticket+"|"+state+"|"+attempts+"|"+calls+"|"+revision+"|"+first;}
        void begin(long expected,String fault,boolean hold)throws Exception{
            require(expected==revision,"STALE_REVISION");require(state.equals("OWNED_OPEN_RETRYABLE"),"CLOSE_NOT_RETRYABLE");require(attempts<3,"EXHAUSTED");attempts++;revision++;state="IN_FLIGHT";heldFault=fault;held=hold;if(!hold)perform();
        }
        void perform(){
            require(state.equals("IN_FLIGHT"),"NO_CLOSE_ADMISSION");held=false;
            if(heldFault.equals("before")){state="OWNED_OPEN_RETRYABLE";if(first.isEmpty())first="INJECTED_BEFORE_DELEGATE";}
            else{calls++;try{file.close();state=heldFault.equals("unknown")?"UNKNOWN":"CLOSED_PROVEN";if(!heldFault.equals("none")&&first.isEmpty())first=heldFault.equals("unknown")?"INJECTED_RESULT_UNKNOWN":"INJECTED_ACK_LOST";}
                catch(IOException e){state="UNKNOWN";if(first.isEmpty())first="NATIVE_CLOSE_UNKNOWN";}}
            revision++;
        }
    }
    public static void main(String[] args)throws Exception{
        require(args.length==2&&args[0].equals("--admitted-helper"),"EXPLICIT_HELPER_REQUIRED");
        key=Base64.getDecoder().decode(System.getenv().getOrDefault("E2_KEY",""));require(key.length==32,"NO_ADMISSION_KEY");
        Path root=Path.of(args[1]).toAbsolutePath().normalize();Path base=Path.of(JavaHelper.class.getProtectionDomain().getCodeSource().getLocation().toURI()).getParent().getParent();
        require(root.startsWith(base.resolve("selfcheck"))&&root.equals(root.toRealPath()),"SYNTHETIC_ROOT_ONLY");
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
                        Path path=safe(root,p[8]);Handle h=new Handle(path);handles.put(p[7],h);var attrs=Files.readAttributes(path,java.nio.file.attribute.BasicFileAttributes.class);
                        result=h.file.length()+"|"+attrs.lastModifiedTime().toMillis()+"|"+String.valueOf(attrs.fileKey())+"|"+h.view();break;}
                    case "READ":case "READ_ZERO":{
                        Handle h=handles.get(p[7]);require(h.state.equals("OWNED_OPEN_RETRYABLE"),"OBJECT_NOT_OPEN");int n=Integer.parseInt(p[9]),cap=Integer.parseInt(p[10]);long offset=Long.parseLong(p[8]);
                        require(p[6].equals("I")&&offset>=0&&n>=0&&n<=65536&&cap>0&&input+n<=1573522&&inputCalls<59,"INPUT_LIMIT");input+=n;inputCalls++;
                        int got=0;byte[] b=new byte[Math.min(n,cap)];if(!verb.equals("READ_ZERO")&&n>0){h.file.seek(offset);h.seeks++;got=h.file.read(b);h.reads++;}
                        MessageDigest digest=MessageDigest.getInstance("SHA-256");if(got>0)digest.update(b,0,got);
                        result=got+"|"+HexFormat.of().formatHex(digest.digest())+"|"+(got>0&&got<=32?Base64.getEncoder().encodeToString(Arrays.copyOf(b,got)):"")+"|"+h.reads+"|"+h.seeks;break;}
                    case "CLOSE":case "HOLD_CLOSE":{
                        require(p[6].equals("N"),"CLOSE_KIND");Handle h=handles.get(p[7]);h.begin(Long.parseLong(p[8]),p[9],verb.equals("HOLD_CLOSE"));result=h.view();break;}
                    case "GATE_CLOSE":{Handle h=handles.get(p[7]);require(p[6].equals("N")&&h.held,"NO_HELD_CLOSE");h.perform();result=h.view();break;}
                    case "RECOVER":{
                        Path directory=safe(root,p[7]);require(directory.toRealPath().startsWith(root),"RECOVERY_ROOT");long seq=0;byte[] payload=null;
                        for(int slot=0;slot<2;slot++){Path f=safe(directory,"state"+slot+".slot");if(!Files.exists(f))continue;require(Files.size(f)==8192,"JOURNAL_CORRUPT");byte[] b=Files.readAllBytes(f);ByteBuffer header=ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN);long s=header.getLong();int n=header.getInt();require(n>=0&&n<=8144&&s>0,"JOURNAL_CORRUPT");byte[] record=Arrays.copyOfRange(b,48,48+n);MessageDigest digest=MessageDigest.getInstance("SHA-256");digest.update(b,0,16);digest.update(record);require(MessageDigest.isEqual(digest.digest(),Arrays.copyOfRange(b,16,48)),"JOURNAL_CORRUPT");if(s>seq){seq=s;payload=record;}}
                        require(payload!=null&&payload.length<=4400,"RECOVERY_FRAME");String encoded=Base64.getEncoder().encodeToString(payload);
                        for(String type:new String[]{"RECOVERY_QNEW","RECOVERY_QREPLAY"}){
                            out.println(pack("CALLBACK",id,type,Long.toString(seq),encoded));String[] answer=admitted(bounded(reader));require(answer[1].equals("QUERY_RESULT")&&answer[2].equals(row),"RECOVERY_CALLBACK");
                        }
                        result=seq+"|"+encoded;break;}
                    case "EXIT":out.println(pack(id,"OK",owner));return;
                    default:throw new IllegalStateException("UNKNOWN_VERB");
                }
                response=pack(id,"OK",result);
            }catch(Exception e){response=pack(id,"ERROR",e instanceof IllegalStateException?e.getMessage():"NATIVE_BACKEND_ERROR");}
            require(response.length()<8192,"RESPONSE_LIMIT");cache.put(id,new String[]{raw,response});cacheBytes+=raw.length()+response.length();out.println(response);
        }
    }
}
