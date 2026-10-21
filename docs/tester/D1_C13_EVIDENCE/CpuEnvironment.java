package com.videokit.spike.c13;
import android.content.*;
import android.content.pm.*;
/** Read-only actual installed state, never an attempt to enable/clear/reinstall an App. */
public final class CpuEnvironment {
    public static final class Snapshot {
        public final int appSetting,componentSetting;public final boolean appEnabled,serviceEnabled,visible,isolated,exported;public final long versionCode;
        Snapshot(int app,int component,boolean enabled,boolean service,boolean visible,boolean isolated,boolean exported,long version){appSetting=app;componentSetting=component;appEnabled=enabled;serviceEnabled=service;this.visible=visible;this.isolated=isolated;this.exported=exported;versionCode=version;}
        public boolean ready(){return CpuLifecycle.environmentReady(appSetting,appEnabled,componentSetting,serviceEnabled,visible,isolated,exported);}
        public String details(){return "app_setting="+appSetting+" app_enabled="+appEnabled+" component_setting="+componentSetting+" service_enabled="+serviceEnabled+" service_visible="+visible+" isolated="+isolated+" exported="+exported+" version_code="+versionCode;}
    }
    public static Snapshot inspect(Context context){
        try{
            PackageManager pm=context.getPackageManager();String pkg=context.getPackageName();ComponentName component=new ComponentName(context,CpuIsolatedService.class);
            ApplicationInfo app=pm.getApplicationInfo(pkg,PackageManager.MATCH_DISABLED_COMPONENTS);ServiceInfo service=pm.getServiceInfo(component,PackageManager.MATCH_DISABLED_COMPONENTS);
            ResolveInfo resolved=pm.resolveService(new Intent().setComponent(component),0);
            Snapshot snapshot=new Snapshot(pm.getApplicationEnabledSetting(pkg),pm.getComponentEnabledSetting(component),app.enabled,service.enabled,resolved!=null && resolved.serviceInfo!=null,(service.flags&ServiceInfo.FLAG_ISOLATED_PROCESS)!=0,service.exported,pm.getPackageInfo(pkg,0).getLongVersionCode());
            StageLog.event(snapshot.ready()?"CPU_ENVIRONMENT_READY":"CPU_ENVIRONMENT_BLOCKED",snapshot.details());return snapshot;
        }catch(Exception error){StageLog.failure("CPU_ENVIRONMENT_QUERY_FAILED",error);return new Snapshot(-1,-1,false,false,false,false,true,-1);}
    }
    public static void requireReady(Context context)throws CpuDiagnostics.Failure {if(!inspect(context).ready())throw CpuDiagnostics.failure("CPU_ENVIRONMENT_BLOCKED","ENVIRONMENT",null);}
    private CpuEnvironment(){}
}
