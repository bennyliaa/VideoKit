package com.videokit.spike.e4;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

/** Identity of the actual recovery writer, persisted before fencing. It conveys no completion authority. */
public final class E5AOwner {
    public final String attempt,process;public final int pid,uid;public final long began;
    public E5AOwner(String a,int p,int u,String n,long b)throws IOException {
        if(!a.matches("[a-f0-9-]{36}") || !UUID.fromString(a).toString().equals(a) || p<=0 || p==E5N2Recovery.HOST || p==E5N2Recovery.CODEC || u!=E5N2Recovery.UID || !"com.videokit.app".equals(n) || b<1792208970000L)throw new IOException("E5A_RECOVERY_WRITER_IDENTITY");
        attempt=a;pid=p;uid=u;process=n;began=b;
    }
    public byte[] bytes(){return ("E5A_N2_RECOVERY_OWNER_V1 "+attempt+" "+pid+" "+uid+" "+process+" "+began+"\n").getBytes(StandardCharsets.US_ASCII);}
    public static E5AOwner parse(byte[] raw)throws Exception {
        String s=new String(raw,StandardCharsets.US_ASCII);String[] p=s.trim().split(" ");if(p.length!=6 || !p[0].equals("E5A_N2_RECOVERY_OWNER_V1"))throw new IOException("E5A_RECOVERY_WRITER_RECORD");
        E5AOwner result=new E5AOwner(p[1],Integer.parseInt(p[2]),Integer.parseInt(p[3]),p[4],Long.parseLong(p[5]));if(!java.util.Arrays.equals(raw,result.bytes()))throw new IOException("E5A_RECOVERY_WRITER_ENCODING");return result;
    }
}
