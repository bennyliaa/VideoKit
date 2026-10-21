package com.videokit.spike.e4;
import com.videokit.spike.c14.SourceAdmission;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
public final class E13ProductionCheck {
    static int assertions;
    static void ok(boolean value){assertions++;if(!value)throw new AssertionError("E13 assertion "+assertions);}
    interface Call {void run()throws Exception;}
    static void deny(Call c)throws Exception {boolean failed=false;try{c.run();}catch(IOException|IllegalArgumentException expected){failed=true;}ok(failed);}
    static E9Record change(E9Record r,String k,String v)throws Exception {Map<String,String> m=new TreeMap<>(r.fields());m.put(k,v);return new E9Record(m,8192);}
    static final class Port implements E9DeploymentGate.Port {
        byte[] app="SYNTHETIC_E13_APP_NOT_APPROVED".getBytes(StandardCharsets.US_ASCII),test="SYNTHETIC_E13_TEST_NOT_APPROVED".getBytes(StandardCharsets.US_ASCII);E9DeploymentGate.PackageInfo before=E9DeploymentGate.acceptedE11Source(),target;int sends;boolean fail;
        public byte[] artifact(Path p,int max){return p.toString().equals("app.apk")?app:test;}
        public E9DeploymentGate.PackageInfo inspectArtifacts(Path a,Path b){return target;}
        public E9DeploymentGate.PackageInfo installed(){return before;}
        public void dispatch(List<String> args)throws Exception {sends++;ok(args.size()==6 && args.get(3).equals("install") && args.get(4).equals("-r"));if(fail)throw new IOException("SYNTHETIC_PARTIAL_INSTALL_UNKNOWN");if(sends==2)before=target;}
    }
    public static void main(String[] a)throws Exception {
        String mode=a[0];
        if(mode.equals("DEPLOYMENT")){
            Path registry=Paths.get(a[1]);E9Record plan=E9Record.parse(Files.readAllBytes(registry.resolve("prepare-deployment.json")),8192),cat=E9Record.parse(Files.readAllBytes(registry.resolve("final.acceptance.json")),16384);
            E9Registry r=new E9Registry(new E9Registry.Store(registry,null),new E9Registry.Trust(plan.bytes(),plan.hash(),plan.get("authorization"),cat.get("review")));r.openKnownHead(cat.get("head"));
            Port p=new Port();String scope=E9Record.sha("SYNTHETIC_SCOPE_NOT_APPROVAL".getBytes(StandardCharsets.US_ASCII));
            E9Record release=new E9Record(E9Record.map("kind","activationRelease","head",cat.get("head"),"catalog",cat.hash(),"app",E9Record.sha(p.app),"test",E9Record.sha(p.test),"signer",p.before.signer,"role","ACTIVATION","abi","1","version","16","sourceReview",scope,"environment","DEVICE_HA1Q6WXR","sourceAcceptance",E9DeploymentGate.E13_SOURCE_ACCEPTANCE,"scope",scope),8192);
            p.target=new E9DeploymentGate.PackageInfo("com.videokit.app","com.videokit.app.test",release.get("app"),release.get("test"),p.before.signer,"ACTIVATION",10221,10222,16,1,false);
            E9DeploymentGate g=new E9DeploymentGate(p,"SYNTHETIC_NOT_EXECUTED/adb.exe","HA1Q6WXR");Path app=Paths.get("app.apk"),test=Paths.get("test.apk");
            for(String key:List.of("head","catalog","signer","role","abi","sourceReview","environment","sourceAcceptance","scope","version")){
                String value=key.equals("version")?"15":key.equals("role")?"PREPARE":key.equals("abi")?"2":key.equals("sourceReview")?"NOT_APPROVED":E9Record.sha(("wrong"+key).getBytes(StandardCharsets.US_ASCII));E9Record bad=change(release,key,value);deny(()->g.deployE13Detached(r,bad,bad.hash(),scope,app,test));ok(p.sends==0);
            }
            E9DeploymentGate.PackageInfo original=p.before;
            for(int i=0;i<7;i++){
                p.before=new E9DeploymentGate.PackageInfo(original.appId,original.testId,i==0?release.get("app"):original.appSha,original.testSha,i==1?scope:original.signer,i==2?"PREPARE":original.role,i==3?10220:original.appUid,original.testUid,i==4?14:i==5?16:15,1,i==6);
                deny(()->g.deployE13Detached(r,release,release.hash(),scope,app,test));ok(p.sends==0);
            }
            p.before=original;g.deployE13Detached(r,release,release.hash(),scope,app,test);ok(p.sends==2 && p.before.version==16);deny(()->g.deployE13Detached(r,release,release.hash(),scope,app,test));ok(p.sends==2);
            Port partial=new Port();partial.target=p.target;partial.fail=true;E9DeploymentGate pg=new E9DeploymentGate(partial,"SYNTHETIC_NOT_EXECUTED/adb.exe","HA1Q6WXR");deny(()->pg.deployE13Detached(r,release,release.hash(),scope,app,test));ok(partial.sends==1);deny(()->pg.deployE13Detached(r,release,release.hash(),scope,app,test));ok(partial.sends==1);ok(r.returned());
        }else if(mode.equals("BOUNDARIES")){
            String h=E9Record.sha("synthetic-only".getBytes(StandardCharsets.US_ASCII));
            for(String method:E13Selection.METHODS){Map<String,String> args=new TreeMap<>(Map.of("class","com.videokit.spike.e4.E13DeviceTests#"+method,"e13Case",method,"e13Batch",E13Selection.BATCH,"e13ScopeSha256",h));E13Selection.require(args);ok(true);args.put("class","com.videokit.spike.e4.E13DeviceTests");deny(()->E13Selection.require(args));}
            SourceAdmission.require(1,2,"current",3,1,2,"current",3,"REJECTED");ok(true);deny(()->SourceAdmission.require(1,2,"current",3,9,2,"current",3,"REJECTED"));deny(()->SourceAdmission.require(1,2,"current",3,1,9,"current",3,"REJECTED"));
            String method="authorizedHostSourceReadAndClose",raw="FRESH_E9_OBSERVATION_ADMITTED\nE13_RETURN_CHECK case="+method+" sourceRetained=0 canFinish=true\nE13_PLATFORM_FINISH_ADMITTED scope="+h+" case="+method+" ownersReturned=true\nOK (1 test)\nINSTRUMENTATION_CODE: -1\n";
            E13HostCase.requireResult(raw,h,method);ok(true);deny(()->E13HostCase.requireResult(raw.replace("ownersReturned=true","ownersReturned=false"),h,method));deny(()->E13HostCase.requireResult(raw+"FAILURES!!!",h,method));deny(()->E13HostCase.requireResult(raw.replace("canFinish=true","canFinish=false"),h,method));deny(()->E13HostCase.requireResult(raw,h,"twoConsumersHoldSourceUntilLastReturn"));
            E13HostCase.requireOwnerReturn(raw+"FAILURES!!!",h,method);ok(true);deny(()->E13HostCase.requireOwnerReturn(raw.replace("ownersReturned=true","ownersReturned=false"),h,method));
        }else throw new IOException("E13_LOCAL_CHECK_SCOPE");
        System.out.println("PASS_E13_"+mode+" assertions="+assertions+" synthetic_ports_not_device=true");
    }
}
