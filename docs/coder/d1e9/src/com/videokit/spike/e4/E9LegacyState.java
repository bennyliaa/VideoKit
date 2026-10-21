package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Shared real legacy validation used by migration and the new host observer; never modifies R/S. */
public final class E9LegacyState {
    public static final class Accounting {public final long consumed,reserved;public final int tasks;Accounting(long c,long r,int t){consumed=c;reserved=r;tasks=t;}}
    public static Accounting ledger(byte[] raw)throws Exception{
        if(raw==null||raw.length<E9LegacyProfile.PREFIX_BYTES||raw.length>131072||!E9Record.sha(Arrays.copyOf(raw,E9LegacyProfile.PREFIX_BYTES)).equals(E9LegacyProfile.PREFIX_SHA))throw new IOException("E9_ACCEPTED_LEDGER_PREFIX");
        String s=new String(raw,StandardCharsets.US_ASCII);if(!Arrays.equals(s.getBytes(StandardCharsets.US_ASCII),raw)||!s.startsWith(E5N2Recovery.HEADER)||!s.endsWith("\n"))throw new IOException("E9_LEDGER_ENCODING");
        String chain=E9Record.sha(E5N2Recovery.HEADER.getBytes(StandardCharsets.US_ASCII));Map<String,Long> values=new LinkedHashMap<>();int events=0;
        for(String line:s.substring(E5N2Recovery.HEADER.length()).split("\n")){
            if(++events>256)throw new IOException("E9_LEDGER_EVENTS");int at=line.lastIndexOf(' ');if(at<0)throw new IOException("E9_LEDGER_RECORD");String payload=line.substring(0,at),digest=line.substring(at+1);if(!E9Record.sha((chain+" "+payload).getBytes(StandardCharsets.US_ASCII)).equals(digest))throw new IOException("E9_LEDGER_CHAIN");chain=digest;
            String[] p=payload.split(" ");if(p.length==3&&p[0].equals("R")){E9Record.uuid(p[1]);if(!p[2].matches("D1-E4A-[A-Za-z0-9-]{8,80}")||values.containsKey(p[1])||values.size()>=128)throw new IOException("E9_LEDGER_R");values.put(p[1],null);}
            else if(p.length==5&&p[0].equals("S")){if(!values.containsKey(p[1])||values.get(p[1])!=null||!Set.of("READY","ABORTED").contains(p[2])||!p[3].matches("0|[1-9][0-9]{0,7}"))throw new IOException("E9_LEDGER_S");long n=Long.parseLong(p[3]);if(n>2097152)throw new IOException("E9_LEDGER_OUTPUT_BOUND");E9Record.digest(p[4]);values.put(p[1],n);}
            else throw new IOException("E9_LEDGER_RECORD");
        }
        long consumed=0,reserved=0;for(Long n:values.values())if(n==null)reserved+=2097152;else consumed+=n;
        if(consumed<E9LegacyProfile.MIN_CONSUMED||consumed+reserved>4194304||reserved!=0)throw new IOException("E9_LEDGER_PENDING_OR_CONSUMPTION");return new Accounting(consumed,reserved,values.size());
    }
    public static E4Owned<E9OwnedFiles.Handle> openAndValidate(E9OwnedFiles files,boolean force)throws Exception{
        files.directory(".");files.directory("e4a_output_budget");files.directory("e4a_outputs");files.directory("e4a_output_budget/N2-e5-recovery");
        if(files.exists("e4a_output_budget/operation.pending"))throw new IOException("E9_ACTIVE_PENDING");
        for(Map.Entry<String,String> e:E9LegacyProfile.IMMUTABLE.entrySet())if(!E9Record.sha(files.read(e.getKey(),2048,force)).equals(e.getValue()))throw new IOException("E9_IMMUTABLE_LEGACY_CHANGED");
        byte[] output=files.read("e4a_outputs/"+E5N2Recovery.TASK+".mp4",0,force);if(output.length!=0)throw new IOException("E9_LEGACY_OUTPUT_NOT_ZERO");
        E4Owned<E9OwnedFiles.Handle> ledger=files.open("e4a_output_budget/ledger.bin",E9OwnedFiles.Mode.LEDGER,131072);ledger(files.read(ledger,131072));return ledger;
    }
    public static void lockOriginalGuards(E9OwnedFiles files)throws Exception{
        files.guard("e4a_outputs/"+E5N2Recovery.TASK+".owner",E5BGuard.Role.OWNER,null,new E5BFileId(64522,20304,0,10221,E5BFileId.REGULAR));
        files.guard("e4a_outputs/"+E5N2Recovery.TASK+".lease",E5BGuard.Role.LEASE,E9LegacyProfile.FENCE,new E5BFileId(64522,20385,36,10221,E5BFileId.REGULAR));
    }
    private E9LegacyState(){}
}
