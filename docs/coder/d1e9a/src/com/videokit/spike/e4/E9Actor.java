package com.videokit.spike.e4;

import java.io.IOException;

/** Identity sampled before the first application-private write; actor identity is immutable. */
public final class E9Actor {
    public final E9Record record;public final String migration,handle,attempt,descriptor,app,test,boot,start,process;public final int ordinal,pid,uid;
    public E9Actor(E9Record r)throws IOException{
        r.exact("kind","registry","migration","ordinal","attempt","handle","task","budget","policy","descriptor","app","test","uid","pid","process","bootKind","boot","start","participants","environment");
        if(!r.get("kind").equals("actor")||!r.get("task").equals(E5N2Recovery.TASK)||!r.get("budget").equals(E5N2Recovery.BUDGET)||!r.get("policy").equals(E9LegacyProfile.POLICY)||!r.get("participants").equals("SELF_NO_FD_TRANSFER"))throw new IOException("E9_ACTOR_SCOPE");
        for(String key:new String[]{"registry","migration","attempt","handle"})E9Record.uuid(r.get(key));
        for(String key:new String[]{"descriptor","app","test"})E9Record.digest(r.get(key));
        ordinal=(int)r.number("ordinal",2);pid=(int)r.number("pid",Integer.MAX_VALUE);uid=(int)r.number("uid",Integer.MAX_VALUE);
        if(ordinal<1||pid<1||uid!=10221||!r.get("process").equals("com.videokit.app")||!r.get("start").matches("[1-9][0-9]{0,18}"))throw new IOException("E9_ACTOR_PROCESS");
        if(!r.get("bootKind").equals("KERNEL_BOOT_ID")&&!r.get("bootKind").equals("SYSTEM_BOOT_COUNT"))throw new IOException("E9_BOOT_SOURCE");
        if(r.get("bootKind").equals("KERNEL_BOOT_ID"))E9Record.uuid(r.get("boot"));else r.number("boot",Integer.MAX_VALUE);
        if(!r.get("environment").equals("DEVICE_HA1Q6WXR")&&!r.get("environment").equals("SYNTHETIC_LOCAL"))throw new IOException("E9_ENVIRONMENT");
        if(!r.get("descriptor").equals(E9LegacyProfile.proposal().hash())||r.number("start",Long.MAX_VALUE)==0)throw new IOException("E9_DESCRIPTOR_OR_START");
        record=r;migration=r.get("migration");handle=r.get("handle");attempt=r.get("attempt");descriptor=r.get("descriptor");app=r.get("app");test=r.get("test");boot=r.get("boot");start=r.get("start");process=r.get("process");
    }
    public String hash(){return record.hash();}
    public byte[] intent(String reserve)throws IOException{E9Record.digest(reserve);java.util.Map<String,String> m=new java.util.TreeMap<>(record.fields());m.put("kind","intent");m.put("actor",hash());m.put("reserve",reserve);return new E9Record(m,2048).bytes();}
    public static E9Actor fromIntent(byte[] raw,String expectedReserve)throws IOException{E9Record r=E9Record.parse(raw,2048);if(!r.get("kind").equals("intent")||!r.get("reserve").equals(expectedReserve))throw new IOException("E9_INTENT_BINDING");java.util.Map<String,String> m=new java.util.TreeMap<>(r.fields());String hash=m.remove("actor");m.remove("reserve");m.put("kind","actor");E9Actor a=new E9Actor(new E9Record(m,2048));if(!a.hash().equals(hash))throw new IOException("E9_INTENT_BINDING");return a;}
}
