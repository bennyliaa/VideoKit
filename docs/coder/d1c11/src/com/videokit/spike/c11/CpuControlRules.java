package com.videokit.spike.c11;
/** Shared strict control authentication; moving a call to another thread does not authorize PID zero. */
public final class CpuControlRules {
    public static final int ERROR=0x564b4552;
    public static void synchronous(int flags){if((flags&1)!=0)throw new SecurityException("CPU_SYNC_CONTROL_REQUIRED");}
    public static void owner(int uid,int pid,int actualUid,int actualPid){if(uid<=0 || pid<=0 || actualPid<=0 || uid!=actualUid || pid!=actualPid)throw new SecurityException("CPU_OWNER");}
    public static void session(String task,long epoch,String requested,long requestedEpoch){if(task==null || !task.equals(requested) || epoch<=0 || epoch!=requestedEpoch)throw new SecurityException("CPU_TASK_EPOCH");}
    public static int errorNumber(String code){return "CPU_OWNER".equals(code) || "CPU_HELLO_IDENTITY".equals(code)?1:"CPU_TASK_EPOCH".equals(code)?2:"CPU_SYNC_CONTROL_REQUIRED".equals(code)?3:code!=null && code.contains("START")?4:"CPU_REQUEST_BUDGET".equals(code)?5:6;}
    public static String errorCode(int number){switch(number){case 1:return "CPU_CONTROL_AUTH_REJECTED";case 2:return "CPU_TASK_EPOCH_REJECTED";case 3:return "CPU_SYNC_CONTROL_REQUIRED";case 4:return "CPU_CONTROL_STATE_REJECTED";case 5:return "CPU_CONTROL_REQUEST_BUDGET";case 6:return "CPU_CONTROL_REJECTED";default:return "CPU_CONTROL_ERROR_PROTOCOL";}}
    private CpuControlRules(){}
}
