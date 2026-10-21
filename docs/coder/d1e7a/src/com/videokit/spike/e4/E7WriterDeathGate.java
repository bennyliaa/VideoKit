package com.videokit.spike.e4;

import java.util.List;

/** The production history/proc predicate. Reports are diagnostics, never admission grants. */
public final class E7WriterDeathGate {
    public static final int LIMIT=8;
    public enum Proc { ABSENT, EXISTS, UNAVAILABLE }
    public static final class Exit {
        public final int pid,uid,reason,status; public final String process; public final long timestamp;
        public Exit(int p,int u,String n,long t,int r,int s){pid=p;uid=u;process=n;timestamp=t;reason=r;status=s;}
    }
    public interface Port {
        List<Exit> history(int pid,int max) throws Exception;
        Proc proc(int pid) throws Exception;
    }
    public static final class Report {
        public final String code,history,proc,errorClass;
        public final int returned,matches,pidReject,uidReject,processReject,beforeReject,futureReject,reasonNonPositive;
        public final Exit matching;
        private Report(String c,String h,String p,String e,int returned,int matches,int[] rejects,Exit m){
            code=c;history=h;proc=p;errorClass=e;this.returned=returned;this.matches=matches;
            pidReject=rejects[0];uidReject=rejects[1];processReject=rejects[2];beforeReject=rejects[3];futureReject=rejects[4];reasonNonPositive=rejects[5];matching=m;
        }
        public boolean passed(){return code.equals("PASS_CURRENT_HISTORY_AND_PROC");}
        private String count(int n){return n<0?"NOT_COLLECTED":Integer.toString(n);}
        public String record(){
            return "E7_WRITER_DEATH schema=1 code="+code+" history="+history+" limit=8 callsMax=1 returned="+count(returned)+
                " matches="+count(matches)+" rejectPid="+count(pidReject)+" rejectUid="+count(uidReject)+" rejectProcess="+count(processReject)+
                " rejectBeforeOwner="+count(beforeReject)+" rejectFuture="+count(futureReject)+" reasonNonPositive="+count(reasonNonPositive)+
                " matchedTimestamp="+(matching==null?"NOT_COLLECTED":matching.timestamp)+" matchedReason="+(matching==null?"NOT_COLLECTED":matching.reason)+
                " matchedStatus="+(matching==null?"NOT_COLLECTED":matching.status)+" proc="+proc+" errorClass="+errorClass+
                " persistentFact=DISABLED birthGeneration=NOT_RECORDED reboot=NOT_PROVEN pidReuse=NOT_PROVEN grant=NONE";
        }
    }
    private static final int[] UNKNOWN={-1,-1,-1,-1,-1,-1};
    public static Report notRequested(){return new Report("OBSERVER_PRECONDITION","NOT_REQUESTED","NOT_REQUESTED","NONE",-1,-1,UNKNOWN,null);}
    public static Report inspect(E5AOwner owner,long now,Port port){
        if(owner==null || now<owner.began)return new Report("CLOCK_OR_OWNER_INVALID","NOT_REQUESTED","NOT_REQUESTED","NONE",-1,-1,UNKNOWN,null);
        List<Exit> rows;
        try{rows=port.history(owner.pid,LIMIT);}catch(Exception e){return new Report("HISTORY_UNAVAILABLE","UNAVAILABLE","NOT_REQUESTED","Exception",-1,-1,UNKNOWN,null);}
        if(rows==null)return new Report("HISTORY_NULL","UNAVAILABLE","NOT_REQUESTED","NONE",-1,-1,UNKNOWN,null);
        int size=rows.size();
        if(size>LIMIT)return new Report("HISTORY_OVER_BUDGET","OVER_BUDGET","NOT_REQUESTED","NONE",size,-1,UNKNOWN,null);
        int[] rejects=new int[6];int n=0;Exit match=null;
        for(Exit r:rows){
            if(r==null)return new Report("HISTORY_MALFORMED","MALFORMED","NOT_REQUESTED","NONE",size,-1,UNKNOWN,null);
            boolean pid=r.pid==owner.pid,uid=r.uid==owner.uid,name=owner.process.equals(r.process),before=r.timestamp<owner.began,future=r.timestamp>now;
            if(!pid)rejects[0]++;if(!uid)rejects[1]++;if(!name)rejects[2]++;if(before)rejects[3]++;if(future)rejects[4]++;
            if(pid&&uid&&name&&!before&&!future){n++;match=r;if(r.reason<=0)rejects[5]++;}
        }
        // Count identity/time matches BEFORE applying reason, preserving the legacy duplicate rejection.
        Exit unique=n==1?match:null;
        if(n!=1)return new Report(n==0?"NO_UNIQUE_MATCH_MISSING":"NO_UNIQUE_MATCH_DUPLICATE","AVAILABLE","NOT_REQUESTED","NONE",size,n,rejects,null);
        if(match.reason<=0)return new Report("MATCH_REASON_NON_POSITIVE","AVAILABLE","NOT_REQUESTED","NONE",size,n,rejects,unique);
        Proc proc;
        try{proc=port.proc(owner.pid);}catch(Exception e){return new Report("PROC_UNAVAILABLE","AVAILABLE","UNAVAILABLE","Exception",size,n,rejects,unique);}
        if(proc==null || proc==Proc.UNAVAILABLE)return new Report("PROC_UNAVAILABLE","AVAILABLE","UNAVAILABLE","NONE",size,n,rejects,unique);
        return new Report(proc==Proc.ABSENT?"PASS_CURRENT_HISTORY_AND_PROC":"WRITER_VISIBLE_OR_REUSED","AVAILABLE",proc.name(),"NONE",size,n,rejects,unique);
    }
    private E7WriterDeathGate(){}
}
