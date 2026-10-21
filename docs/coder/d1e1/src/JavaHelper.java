package videokit.e1;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.*;

/** Independent real RandomAccessFile backend. No C14 edits, memory provider or dependency downloads. */
public final class JavaHelper {
    static final int FRAME=8192;
    static final class Owned {
        final RandomAccessFile file; final String object=UUID.randomUUID().toString(), ticket=UUID.randomUUID().toString();
        String disposition="OWNED_OPEN_RETRYABLE", first=""; int attempts, calls; long revision;
        final Map<String,String> cache=new HashMap<>();
        Owned(Path p)throws IOException{file=new RandomAccessFile(p.toFile(),"r");}
        String view(){return object+"|"+ticket+"|"+disposition+"|"+attempts+"|"+calls+"|"+revision+"|"+first;}
        synchronized String close(String command,long expected,String fault)throws IOException{
            if(cache.containsKey(command))return cache.get(command);
            require(cache.size()<16,"CLOSE_COMMAND_LIMIT");
            require(expected==revision,"STALE_REVISION");require(disposition.equals("OWNED_OPEN_RETRYABLE"),"CLOSE_NOT_RETRYABLE");require(attempts<3,"EXHAUSTED");
            attempts++;revision++;disposition="IN_FLIGHT";
            if(fault.equals("BeforeDelegate")){disposition="OWNED_OPEN_RETRYABLE";if(first.isEmpty())first="INJECTED_BEFORE_DELEGATE";}
            else if(fault.equals("UnknownBeforeDelegate")){disposition="UNKNOWN";if(first.isEmpty())first="INJECTED_UNKNOWN_NO_CLOSE";}
            else {calls++;try{file.close();disposition="CLOSED_PROVEN";if(fault.equals("LoseReplyAfterClose")&&first.isEmpty())first="INJECTED_ACK_LOST";}
                catch(IOException ex){disposition="UNKNOWN";if(first.isEmpty())first="NATIVE_CLOSE_UNKNOWN";}}
            revision++;String result=view();cache.put(command,result);return result;
        }
    }
    static void require(boolean b,String reason){if(!b)throw new IllegalStateException(reason);}
    static String bounded(Reader r)throws IOException{
        StringBuilder b=new StringBuilder();for(int i=0;i<=FRAME;i++){int c=r.read();if(c<0)return b.length()==0?null:b.toString();if(c=='\n')return b.toString().replace("\r","");b.append((char)c);}throw new IOException("FRAME_LIMIT");
    }
    static String pack(String... s){return String.join("\t",Arrays.stream(s).map(x->Base64.getEncoder().encodeToString(x.getBytes(StandardCharsets.UTF_8))).toList());}
    static String[] unpack(String s){String[] p=s.split("\t",-1);require(p.length<=16,"FIELD_LIMIT");return Arrays.stream(p).map(x->new String(Base64.getDecoder().decode(x),StandardCharsets.UTF_8)).toArray(String[]::new);}
    static Path file(Path root,String name)throws IOException{
        require(name.matches("[A-Za-z0-9_.-]{1,64}")&&!name.contains(".."),"FIXTURE_NAME");Path p=root.resolve(name);
        require(!Files.isSymbolicLink(p),"SYMLINK_DENIED");return p;
    }
    public static void main(String[] args)throws Exception{
        if(args.length!=2||!args[0].equals("--synthetic-helper")){System.err.println("E1_EXECUTION_NOT_AUTHORIZED");System.exit(2);}
        Path root=Path.of(args[1]).toAbsolutePath().normalize();require(root.toString().replace('\\','/').contains("/docs/coder/d1e1/selfcheck/"),"SYNTHETIC_ROOT_ONLY");
        require(root.equals(root.toRealPath()),"REPARSE_ROOT_DENIED");
        String instance=UUID.randomUUID().toString();Map<String,Owned> handles=new HashMap<>();
        Map<String,String[]> cache=new HashMap<>();int cacheBytes=0;
        long requested=0;Reader reader=new InputStreamReader(System.in,StandardCharsets.UTF_8);PrintWriter out=new PrintWriter(System.out,true,StandardCharsets.UTF_8);
        for(;;){String raw=bounded(reader);if(raw==null)return;String[] p=unpack(raw);String id=p[0];
            if(cache.containsKey(id)){String[] old=cache.get(id);out.println(old[0].equals(raw)?old[1]:pack(id,"ERROR","COMMAND_CONFLICT"));continue;}
            if(cache.size()>=512||cacheBytes+raw.length()+2048>131072){out.println(pack(id,"ERROR","COMMAND_CACHE_LIMIT"));continue;}
            String response;
            try{String result="";
                switch(p[1]){
                    case "HELLO":result=instance+"|"+ProcessHandle.current().pid()+"|"+System.getProperty("java.runtime.version");break;
                    case "OPEN":require(handles.size()<64&&!handles.containsKey(p[2])&&handles.values().stream().filter(x->!x.disposition.equals("CLOSED_PROVEN")).count()<2,"HANDLE_LIMIT");Owned h=new Owned(file(root,p[3]));handles.put(p[2],h);result=h.file.length()+"|"+h.object;break;
                    case "READ":{
                        Owned v=handles.get(p[2]);require(v.disposition.equals("OWNED_OPEN_RETRYABLE"),"OBJECT_NOT_OPEN");int n=Integer.parseInt(p[4]);long offset=Long.parseLong(p[3]);
                        require(n>=0&&n<=65536&&offset>=0&&requested+n<=1048576,"READ_BUDGET");requested+=n;
                        byte[] b=new byte[n];int got=0;if(n>0){v.file.seek(offset);got=v.file.read(b);}
                        byte[] actual=got>0?Arrays.copyOf(b,got):new byte[0];result=got+"|"+HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual))+"|"+(actual.length<=32?Base64.getEncoder().encodeToString(actual):"");break;}
                    case "CLOSE":result=handles.get(p[2]).close(id,Long.parseLong(p[3]),p[4]);break;
                    case "QUERY":result=handles.get(p[2]).view();break;
                    case "RECOVER":{
                        Path directory=file(root,p[2]);require(directory.toRealPath().startsWith(root),"JOURNAL_ROOT");long best=0;byte[] payload=null;
                        for(int slot=0;slot<2;slot++){
                            Path path=file(directory,"state"+slot+".slot");if(!Files.exists(path))continue;
                            require(Files.size(path)==8192,"JOURNAL_UNKNOWN_OR_CORRUPT");byte[] all=Files.readAllBytes(path);require(all.length==8192,"JOURNAL_UNKNOWN_OR_CORRUPT");
                            ByteBuffer header=ByteBuffer.wrap(all).order(ByteOrder.LITTLE_ENDIAN);long seq=header.getLong();int n=header.getInt();
                            require(seq>0&&n>=0&&n<=8192-48,"JOURNAL_UNKNOWN_OR_CORRUPT");byte[] body=Arrays.copyOfRange(all,48,48+n);
                            MessageDigest digest=MessageDigest.getInstance("SHA-256");digest.update(all,0,16);digest.update(body);
                            require(MessageDigest.isEqual(digest.digest(),Arrays.copyOfRange(all,16,48)),"JOURNAL_UNKNOWN_OR_CORRUPT");
                            if(seq>best){best=seq;payload=body;}
                        }
                        require(payload!=null&&payload.length<=2048,"RECOVERY_UNKNOWN_OR_FRAME_LIMIT");result=best+"|"+Base64.getEncoder().encodeToString(payload);break;}
                    case "EXIT":out.println(pack(id,"OK",instance));return;
                    default:throw new IllegalStateException("UNSUPPORTED_OPERATION");
                }
                response=pack(id,"OK",result);
            }catch(Exception e){response=pack(id,"ERROR",e instanceof IllegalStateException?e.getMessage():"BACKEND_ERROR");}
            cache.put(id,new String[]{raw,response});cacheBytes+=raw.length()+response.length();out.println(response);
        }
    }
}
