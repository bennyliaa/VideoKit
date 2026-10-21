package com.videokit.spike.e4;

import android.content.Context;
import android.content.pm.*;
import android.os.Process;
import android.provider.Settings;
import android.system.*;
import java.io.*;
import java.util.*;

/** Pre-write real self identity; all exposed metadata FDs belong to this original phase. */
public final class E9AndroidIdentity implements E9MigrationTransaction.IdentitySource {
    private final Context context;private final E9Record request;private final List<E4Owned<FileDescriptor>> holders=new ArrayList<>();private volatile boolean finished;private String recovery="NONE";
    public E9AndroidIdentity(Context context,E9Record request)throws IOException{
        request.exact("kind","registry","migration","ordinal","attempt","handle","descriptor","app","test","bootKind","priorActor","priorEvidence","recoveryDisposition","environment");
        if(!request.get("kind").equals("identityRequest")||!request.get("environment").equals(E9BuildPolicy.SOURCE_ENVIRONMENT)||!request.get("descriptor").equals(E9LegacyProfile.proposal().hash()))throw new IOException("E9_IDENTITY_REQUEST_SCOPE");
        E9Phase.requireMigrationPair(request.get("app"),request.get("test"));this.context=context.getApplicationContext();this.request=request;
    }
    private byte[] read(String fixed,int max)throws Exception{
        E4Owned<FileDescriptor> h=new E4Owned<>(fixed,Os::close);synchronized(holders){if(holders.size()>=8)throw new IOException("E9_IDENTITY_FD_BOUND");holders.add(h);}h.allocate(()->Os.open(fixed,OsConstants.O_RDONLY|OsConstants.O_NOFOLLOW|OsConstants.O_CLOEXEC,0));Throwable first=null;
        try{byte[] b=new byte[max+1];int at=0,calls=0;while(at<b.length){if(++calls>64)throw new IOException("E9_IDENTITY_READ_CALL_BOUND");int n=Os.read(h.original(),b,at,b.length-at);if(n<=0)break;at+=n;}if(at>max)throw new IOException("E9_IDENTITY_READ_BOUND");return Arrays.copyOf(b,at);}catch(Exception|Error e){first=e;throw e;}finally{try{h.close();}catch(Exception|Error e){if(first!=null)first.addSuppressed(e);else throw e;}}
    }
    private String boot(String kind)throws Exception{if(kind.equals("KERNEL_BOOT_ID")){String value=new String(read("/proc/sys/kernel/random/boot_id",64),java.nio.charset.StandardCharsets.US_ASCII).trim();E9Record.uuid(value);return value;}if(kind.equals("SYSTEM_BOOT_COUNT")){int value=Settings.Global.getInt(context.getContentResolver(),Settings.Global.BOOT_COUNT);if(value<0)throw new IOException("E9_BOOT_COUNT");return Integer.toString(value);}throw new IOException("E9_BOOT_SOURCE_REQUIRED");}
    private void packages()throws Exception{
        if(Process.myUid()!=10221||!"com.videokit.app".equals(android.app.Application.getProcessName())||!context.getPackageName().equals("com.videokit.app")||E4Session.retainedSessions()!=0||E4Session.reservedEncoderSlots()!=0)throw new IOException("E9_IDENTITY_ORIGINAL_IDLE_APP");
        PackageManager pm=context.getPackageManager();PackageInfo app=pm.getPackageInfo("com.videokit.app",PackageManager.GET_SIGNING_CERTIFICATES),test=pm.getPackageInfo("com.videokit.app.test",PackageManager.GET_SIGNING_CERTIFICATES);
        if(app.applicationInfo.uid!=10221||test.applicationInfo.uid!=10222||app.getLongVersionCode()!=13)throw new IOException("E9_PREPARE_INSTALLED_VERSION_UID");
        String expected="5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f";
        for(PackageInfo info:new PackageInfo[]{app,test}){Signature[] signatures=info.signingInfo.getApkContentsSigners();if(signatures.length!=1||!E9Record.sha(signatures[0].toByteArray()).equals(expected))throw new IOException("E9_INSTALLED_SIGNER");}
        // Exact APK SHA pair is bound by the trusted manager's before/after-install verification.
        // Runtime role is queried through the app method, not an inlined test-APK constant.
        E9Phase.requireMigrationPair(request.get("app"),request.get("test"));
    }
    public E9Actor sample()throws Exception{
        if(finished)throw new IOException("E9_IDENTITY_ONCE");
        try{
            packages();int pid=Process.myPid();String kind=request.get("bootKind"),before=boot(kind),start=E9ProcessIdentity.start(read("/proc/self/stat",4096),pid);
            int ordinal=(int)request.number("ordinal",2);
            if(ordinal==2){
                E9Actor prior=new E9Actor(E9Record.parse(E9Record.unpack(request.get("priorActor"),2048),2048));if(prior.ordinal!=1||!prior.migration.equals(request.get("migration"))||!prior.record.get("registry").equals(request.get("registry"))||!prior.app.equals(request.get("app"))||!prior.test.equals(request.get("test")))throw new IOException("E9_PRIOR_ACTOR_BINDING");
                E9Record proof;
                if(request.get("recoveryDisposition").equals("TERMINATED_WITHOUT_RETURN"))proof=E9Evidence.termination(prior,E9Record.unpack(request.get("priorEvidence"),4096));
                else if(request.get("recoveryDisposition").equals("RETURNED_LATE_NONQUALIFIED"))proof=E9Evidence.returned(prior,E9Record.unpack(request.get("priorEvidence"),8192),false);
                else throw new IOException("E9_RECOVERY_REQUEST_DISPOSITION");
                boolean absent=false;byte[] oldStat=null;
                if(before.equals(prior.boot)){try{Os.lstat("/proc/"+prior.pid);}catch(ErrnoException e){if(e.errno!=OsConstants.ENOENT)throw e;absent=true;}if(!absent)oldStat=read("/proc/"+prior.pid+"/stat",4096);}
                E9ProcessIdentity.termination(prior,kind,before,boot(kind),oldStat,absent);recovery=proof.hash();
            }else if(!request.get("priorActor").equals("ABSENT")||!request.get("priorEvidence").equals("ABSENT")||!request.get("recoveryDisposition").equals("NONE"))throw new IOException("E9_FIRST_ACTOR_RECOVERY_DATA");
            String lastStart=E9ProcessIdentity.start(read("/proc/self/stat",4096),pid),after=boot(kind);if(!before.equals(after)||!start.equals(lastStart))throw new IOException("E9_TORN_SELF_IDENTITY");
            return new E9Actor(new E9Record(E9Record.map("kind","actor","registry",request.get("registry"),"migration",request.get("migration"),"ordinal",Integer.toString(ordinal),"attempt",request.get("attempt"),"handle",request.get("handle"),"task",E5N2Recovery.TASK,"budget",E5N2Recovery.BUDGET,"policy",E9LegacyProfile.POLICY,"descriptor",request.get("descriptor"),"app",request.get("app"),"test",request.get("test"),"uid","10221","pid",Integer.toString(pid),"process","com.videokit.app","bootKind",kind,"boot",before,"start",start,"participants","SELF_NO_FD_TRANSFER","environment",request.get("environment")),2048));
        }finally{finished=true;}
    }
    public boolean returned(){if(!finished)return false;synchronized(holders){for(E4Owned<?> h:holders)if(!h.returned())return false;}return true;}public int owned(){synchronized(holders){return holders.size();}}public String recoveryDigest(){return recovery;}
}
