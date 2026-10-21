package com.videokit.spike.e4;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

/** Local client of the ORIGINAL custodian; never replaces it or grants Android authority. */
public final class E9PcClient {
    public static E9Record query(int port,String handle,String command)throws Exception{
        E9Record.uuid(handle);if(port<1||port>65535||command.contains("\n")||command.length()>16300)throw new IOException("E9_PC_LOCAL_QUERY_BOUND");
        long deadline=System.nanoTime()+E9PcSupervisor.CONTROL_NS;Socket socket=new Socket();Throwable first=null;
        try{
            socket.connect(new InetSocketAddress(InetAddress.getByName("127.0.0.1"),port),2000);socket.getOutputStream().write((command+" "+handle+"\n").getBytes(StandardCharsets.US_ASCII));socket.getOutputStream().flush();ByteArrayOutputStream raw=new ByteArrayOutputStream();byte[] b=new byte[2048];
            for(;;){long left=deadline-System.nanoTime();if(left<=0)throw new IOException("E9_PC_LOCAL_QUERY_DEADLINE");socket.setSoTimeout((int)Math.max(1,(left+999999)/1000000));int n=socket.getInputStream().read(b);if(n<0)break;if(raw.size()+n>16384)throw new IOException("E9_PC_LOCAL_QUERY_RESPONSE_BOUND");raw.write(b,0,n);}
            E9Record reply=E9Record.parse(raw.toByteArray(),16384);if(System.nanoTime()-deadline>=0)throw new IOException("E9_PC_LOCAL_QUERY_LATE");return reply;
        }catch(Exception|Error t){first=t;throw t;}finally{try{socket.close();}catch(Exception|Error t){if(first!=null)first.addSuppressed(t);else throw t;}}
    }
    private static String wire(String operation,String handle,String extra){return extra==null?operation+" "+handle:operation+" "+handle+" "+extra;}
    public static E9Record command(int port,String handle,String operation,String extra)throws Exception{
        // query's fixed append form is for STATUS; explicit OP/CLEANUP use the same bounded one-shot transport.
        if(operation.equals("STATUS")&&extra==null)return query(port,handle,"STATUS");
        E9Record.uuid(handle);if(port<1||port>65535||!operation.matches("OP|CLEANUP")||extra==null||extra.length()>16000||extra.contains("\n"))throw new IOException("E9_PC_LOCAL_COMMAND_BOUND");
        long deadline=System.nanoTime()+E9PcSupervisor.CONTROL_NS;
        try(Socket socket=new Socket()){socket.connect(new InetSocketAddress("127.0.0.1",port),2000);socket.getOutputStream().write((wire(operation,handle,extra)+"\n").getBytes(StandardCharsets.US_ASCII));socket.getOutputStream().flush();ByteArrayOutputStream raw=new ByteArrayOutputStream();byte[] b=new byte[2048];
            for(;;){long left=deadline-System.nanoTime();if(left<=0)throw new IOException("E9_PC_LOCAL_COMMAND_DEADLINE");socket.setSoTimeout((int)Math.max(1,(left+999999)/1000000));int n=socket.getInputStream().read(b);if(n<0)break;if(raw.size()+n>16384)throw new IOException("E9_PC_LOCAL_RESPONSE_BOUND");raw.write(b,0,n);}
            E9Record response=E9Record.parse(raw.toByteArray(),16384);if(System.nanoTime()-deadline>=0)throw new IOException("E9_PC_LOCAL_COMMAND_LATE");return response;
        }
    }
    public static void main(String[] args)throws Exception{
        if(args.length==0){System.out.println("INSPECT_ONLY: original PC custodian client; no device call. Future --status/--operation use its exact port+handle; --cleanup additionally requires the original approved configuration pin and pinned canonical command.");return;}
        if(args.length==3&&args[0].equals("--status")){System.out.write(command(Integer.parseInt(args[1]),args[2],"STATUS",null).bytes());return;}
        if(args.length==4&&args[0].equals("--operation")){E9Record.uuid(args[3]);System.out.write(command(Integer.parseInt(args[1]),args[2],"OP",args[3]).bytes());return;}
        if(args.length==6&&args[0].equals("--cleanup")){E9Record.digest(args[3]);E9Record.digest(args[5]);Path path=Paths.get(args[4]);if(Files.isSymbolicLink(path)||!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS)||Files.size(path)>8192)throw new IOException("E9_PC_CLEANUP_INPUT_BOUND");byte[] raw=Files.readAllBytes(path);if(!E9Record.sha(raw).equals(args[5]))throw new IOException("E9_PC_CLEANUP_COMMAND_PIN");E9Record c=E9Record.parse(raw,8192);System.out.write(command(Integer.parseInt(args[1]),args[2],"CLEANUP",args[3]+":"+E9Record.pack(c.bytes())).bytes());return;}
        throw new IOException("E9_PC_CLIENT_EXPLICIT_MODE_REQUIRED");
    }
    private E9PcClient(){}
}
