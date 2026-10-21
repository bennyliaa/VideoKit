package com.videokit.spike.e4;

import java.io.IOException;
import java.util.*;

/** Final catalog reader shared by host sealing and activation. PREPARE never loads this as authority. */
public final class E9Catalog {
    public final E9Record record,device;public final E9Actor[] actors;public final E9Record[] reserves,returns,finishes,terminations;public final String[] dispositions;
    private E9Catalog(E9Record r)throws IOException{
        r.exact("kind","version","policy","descriptor","authorization","review","registry","migration","head","environment","actorCount","actor1","reserve1","returned1","finish1","termination1","disposition1","actor2","reserve2","returned2","finish2","termination2","disposition2","device");
        if(!r.get("kind").equals("catalog")||!r.get("version").equals("1")||!r.get("policy").equals(E9LegacyProfile.POLICY))throw new IOException("E9_CATALOG_SCHEMA");
        if(!Arrays.equals(E9Record.unpack(r.get("descriptor"),4096),E9LegacyProfile.proposal().bytes()))throw new IOException("E9_CATALOG_DESCRIPTOR");
        for(String k:new String[]{"authorization","review","head"})E9Record.digest(r.get(k));E9Record.uuid(r.get("registry"));E9Record.uuid(r.get("migration"));
        int count=(int)r.number("actorCount",2);if(count<1)throw new IOException("E9_ACTOR_CATALOG_COUNT");actors=new E9Actor[count];reserves=new E9Record[count];returns=new E9Record[count];finishes=new E9Record[count];terminations=new E9Record[count];dispositions=new String[count];
        for(int i=0;i<2;i++){
            int n=i+1;String suffix=Integer.toString(n);if(i>=count){for(String p:new String[]{"actor","reserve","returned","finish","termination","disposition"})if(!r.get(p+suffix).equals("ABSENT"))throw new IOException("E9_UNDECLARED_ACTOR");continue;}
            E9Actor a=new E9Actor(E9Record.parse(E9Record.unpack(r.get("actor"+suffix),2048),2048));actors[i]=a;
            if(a.ordinal!=n||!a.migration.equals(r.get("migration"))||!a.record.get("registry").equals(r.get("registry"))||!a.record.get("environment").equals(r.get("environment")))throw new IOException("E9_CATALOG_ACTOR_IDENTITY");
            E9Record reserve=E9Record.parse(E9Record.unpack(r.get("reserve"+suffix),4096),4096);reserves[i]=reserve;
            reserve.exact("kind","actor","descriptor","authorization","preparePlan","state","ordinal","predecessor","recoveryEvidence","recoveryDisposition","registry","predecessorIntent");
            if(!reserve.get("kind").equals("reserve")||!reserve.get("actor").equals(a.hash())||!reserve.get("descriptor").equals(a.descriptor)||!reserve.get("authorization").equals(r.get("authorization"))||!reserve.get("registry").equals(r.get("registry"))||!reserve.get("state").equals("BOUND")||reserve.number("ordinal",2)!=n)throw new IOException("E9_CATALOG_RESERVE");E9Record.digest(reserve.get("preparePlan"));
            dispositions[i]=r.get("disposition"+suffix);
            if(dispositions[i].equals("RETURN_VERIFIED_IN_TIME")){
                returns[i]=E9Evidence.returned(a,E9Record.unpack(r.get("returned"+suffix),8192),true);finishes[i]=E9Evidence.finish(a,returns[i],E9Record.unpack(r.get("finish"+suffix),4096));if(!r.get("termination"+suffix).equals("ABSENT"))throw new IOException("E9_RETURN_WITH_DEATH_OVERRIDE");
            }else if(i==0&&count==2&&dispositions[i].equals("RETURNED_LATE_NONQUALIFIED")){
                returns[i]=E9Evidence.returned(a,E9Record.unpack(r.get("returned"+suffix),8192),false);finishes[i]=E9Evidence.finish(a,returns[i],E9Record.unpack(r.get("finish"+suffix),4096));if(!r.get("termination"+suffix).equals("ABSENT"))throw new IOException("E9_RETURN_WITH_DEATH_OVERRIDE");
            }else if(i==0&&count==2&&dispositions[i].equals("TERMINATED_WITHOUT_RETURN")){
                if(!r.get("returned"+suffix).equals("ABSENT")||!r.get("finish"+suffix).equals("ABSENT"))throw new IOException("E9_FAKE_OLD_JAVA_RETURN");terminations[i]=E9Evidence.termination(a,E9Record.unpack(r.get("termination"+suffix),4096));
            }else throw new IOException("E9_UNRESOLVED_ACTOR");
            if(i==0){if(!reserve.get("predecessor").equals("NONE")||!reserve.get("recoveryEvidence").equals("NONE")||!reserve.get("recoveryDisposition").equals("NONE")||!reserve.get("predecessorIntent").equals("NONE"))throw new IOException("E9_FIRST_RESERVE");}
            else{
                E9Record evidence=terminations[0]!=null?terminations[0]:returns[0];if(!reserve.get("predecessor").equals(actors[0].hash())||!reserve.get("recoveryEvidence").equals(evidence.hash())||!reserve.get("recoveryDisposition").equals(dispositions[0])||!a.app.equals(actors[0].app)||!a.test.equals(actors[0].test)||a.handle.equals(actors[0].handle)||a.attempt.equals(actors[0].attempt))throw new IOException("E9_RECOVERY_CHAIN");
            }
        }
        if(!dispositions[count-1].equals("RETURN_VERIFIED_IN_TIME"))throw new IOException("E9_NO_QUALIFIED_FINAL_OWNER");
        device=E9Record.parse(E9Record.unpack(r.get("device"),2048),2048);device.exact("kind","migration","descriptor","intent1","intent2","payload","commit");
        if(!device.get("kind").equals("device")||!device.get("migration").equals(r.get("migration"))||!device.get("descriptor").equals(E9LegacyProfile.proposal().hash())||!device.get("payload").equals(E9LegacyProfile.proposal().hash())||!device.get("commit").equals(E9MigrationTransaction.commitRecord().hash())||!device.hash().equals(returns[count-1].get("device")))throw new IOException("E9_CATALOG_DEVICE");
        String expected1=E9Record.sha(actors[0].intent(reserves[0].hash()));
        if(!device.get("intent1").equals(expected1)&&!(count==2&&dispositions[0].equals("TERMINATED_WITHOUT_RETURN")&&device.get("intent1").equals("ABSENT")&&reserves[1].get("predecessorIntent").equals("ABSENT")))throw new IOException("E9_INTENT1_BINDING");
        if(count==1){if(!device.get("intent2").equals("ABSENT"))throw new IOException("E9_UNDECLARED_INTENT2");}
        else {if(!device.get("intent2").equals(E9Record.sha(actors[1].intent(reserves[1].hash())))||!reserves[1].get("predecessorIntent").equals(device.get("intent1")))throw new IOException("E9_INTENT2_BINDING");}
        record=r;
    }
    public static E9Catalog parse(byte[] raw)throws IOException{return new E9Catalog(E9Record.parse(raw,16384));}
    public static final class Trusted {private final E9Catalog catalog;private Trusted(E9Catalog c){catalog=c;}public E9Catalog catalog(){return catalog;}}
    /** expectedDigest/environment MUST come from the reviewed release input, never a device file. */
    public static Trusted fromTrustedRelease(byte[] raw,String expectedDigest,String environment)throws IOException{E9Record.digest(expectedDigest);if(!E9Record.sha(raw).equals(expectedDigest))throw new IOException("E9_TRUSTED_RELEASE_DIGEST");E9Catalog c=parse(raw);if(!c.record.get("environment").equals(environment))throw new IOException("E9_TRUSTED_RELEASE_ENVIRONMENT");return new Trusted(c);}
}
