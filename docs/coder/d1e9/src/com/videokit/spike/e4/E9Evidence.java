package com.videokit.spike.e4;

import java.io.IOException;

/** Typed interpretation of ORIGINAL managed outputs. Files are not their own return evidence. */
public final class E9Evidence {
    public static E9Record identity(E9Actor actor,byte[] bytes)throws IOException{
        E9Record r=E9Record.parse(bytes,8192);r.exact("kind","actor","stateSeq","identityNanos","executeNanos","verdict","reason","phase","owned","unreturned","executeDone","device","deviceRecord","environment");
        if(!r.get("kind").equals("returned")||!r.get("actor").equals(actor.hash())||!r.get("environment").equals(actor.record.get("environment"))||!r.get("phase").equals("IDENTITY")||!r.get("verdict").equals("IDENTITY_QUALIFIED")||!r.get("executeDone").equals("false")||r.number("identityNanos",Long.MAX_VALUE)>=E9MigrationRun.QUALIFY_NS||r.number("executeNanos",Long.MAX_VALUE)!=0||r.number("owned",48)<1||r.number("unreturned",48)!=0||!r.get("device").equals("ABSENT")||!r.get("deviceRecord").equals("ABSENT"))throw new IOException("E9_IDENTITY_NOT_RETURNED");return r;
    }
    /** Archival/finish permission includes a known failed/no-write commit, never final authority. */
    public static E9Record returnedForArchive(E9Actor actor,byte[] bytes)throws IOException{
        E9Record r=E9Record.parse(bytes,8192);r.exact("kind","actor","stateSeq","identityNanos","executeNanos","verdict","reason","phase","owned","unreturned","executeDone","device","deviceRecord","environment");
        if(!r.get("kind").equals("returned")||!r.get("actor").equals(actor.hash())||!r.get("environment").equals(actor.record.get("environment"))||!r.get("phase").equals("COMMIT")||!r.get("executeDone").equals("true")||r.number("unreturned",48)!=0||r.number("owned",48)<1||r.number("stateSeq",Integer.MAX_VALUE)<1||!java.util.Set.of("QUALIFIED_MIGRATION","FAILED","PENDING").contains(r.get("verdict")))throw new IOException("E9_RETURN_NOT_ORIGINAL_OR_COMPLETE");
        r.number("identityNanos",Long.MAX_VALUE);r.number("executeNanos",Long.MAX_VALUE);
        if(r.get("device").equals("ABSENT")){if(!r.get("deviceRecord").equals("ABSENT")||r.get("verdict").equals("QUALIFIED_MIGRATION"))throw new IOException("E9_RETURN_DEVICE_MISSING");}
        else{E9Record.digest(r.get("device"));E9Record d=E9Record.parse(E9Record.unpack(r.get("deviceRecord"),2048),2048);if(!d.hash().equals(r.get("device")))throw new IOException("E9_RETURN_DEVICE_BINDING");}
        return r;
    }
    public static E9Record returned(E9Actor actor,byte[] bytes,boolean qualified)throws IOException{
        E9Record r=E9Record.parse(bytes,8192);r.exact("kind","actor","stateSeq","identityNanos","executeNanos","verdict","reason","phase","owned","unreturned","executeDone","device","deviceRecord","environment");
        if(!r.get("kind").equals("returned")||!r.get("actor").equals(actor.hash())||!r.get("environment").equals(actor.record.get("environment"))||!r.get("phase").equals("COMMIT")||!r.get("executeDone").equals("true")||r.number("unreturned",48)!=0||r.number("owned",48)<1||r.number("stateSeq",Integer.MAX_VALUE)<1)throw new IOException("E9_RETURN_NOT_ORIGINAL_OR_COMPLETE");
        long id=r.number("identityNanos",Long.MAX_VALUE),ex=r.number("executeNanos",Long.MAX_VALUE);
        if(qualified&&(!r.get("verdict").equals("QUALIFIED_MIGRATION")||id>=E9MigrationRun.QUALIFY_NS||ex>=E9MigrationRun.QUALIFY_NS))throw new IOException("E9_RETURN_NOT_QUALIFIED");
        if(!qualified&&(!r.get("verdict").equals("PENDING")||(id<E9MigrationRun.QUALIFY_NS&&ex<E9MigrationRun.QUALIFY_NS)))throw new IOException("E9_NOT_A_LATE_PENDING_RETURN");
        E9Record.digest(r.get("device"));E9Record device=E9Record.parse(E9Record.unpack(r.get("deviceRecord"),2048),2048);if(!device.hash().equals(r.get("device")))throw new IOException("E9_RETURN_DEVICE_BINDING");return r;
    }
    public static E9Record finish(E9Actor actor,E9Record returned,byte[] bytes)throws IOException{
        E9Record r=E9Record.parse(bytes,4096);r.exact("kind","actor","returned","evidence","disposition","environment");
        if(!r.get("kind").equals("finish")||!r.get("actor").equals(actor.hash())||!r.get("returned").equals(returned.hash())||!r.get("disposition").equals("NORMAL_FINISH_CONFIRMED")||!r.get("environment").equals(actor.record.get("environment")))throw new IOException("E9_FINISH_BINDING");E9Record.digest(r.get("evidence"));return r;
    }
    public static E9Record termination(E9Actor actor,byte[] bytes)throws IOException{
        E9Record r=E9Record.parse(bytes,4096);r.exact("kind","actor","bootKind","currentBoot","currentStart","outcome","source","evidence","participants","environment");
        if(!r.get("kind").equals("termination")||!r.get("actor").equals(actor.hash())||!r.get("bootKind").equals(actor.record.get("bootKind"))||!r.get("participants").equals("SELF_NO_FD_TRANSFER")||!r.get("environment").equals(actor.record.get("environment")))throw new IOException("E9_TERMINATION_BINDING");
        if(r.get("bootKind").equals("KERNEL_BOOT_ID"))E9Record.uuid(r.get("currentBoot"));else r.number("currentBoot",Integer.MAX_VALUE);
        String outcome=r.get("outcome");boolean valid=false;
        if(outcome.equals("BOOT_CHANGED"))valid=!r.get("currentBoot").equals(actor.boot)&&r.get("source").equals("DOUBLE_SAMPLED_OS_BOOT");
        if(outcome.equals("PID_ABSENT"))valid=r.get("currentBoot").equals(actor.boot)&&r.get("currentStart").equals("ENOENT")&&r.get("source").equals("DOUBLE_SAMPLED_PROC");
        if(outcome.equals("PID_REUSED"))valid=r.get("currentBoot").equals(actor.boot)&&r.get("currentStart").matches("[1-9][0-9]{0,18}")&&!r.get("currentStart").equals(actor.start)&&r.get("source").equals("DOUBLE_SAMPLED_PROC");
        if(!valid)throw new IOException("E9_TERMINATION_UNPROVEN");E9Record.digest(r.get("evidence"));return r;
    }
    private E9Evidence(){}
}
