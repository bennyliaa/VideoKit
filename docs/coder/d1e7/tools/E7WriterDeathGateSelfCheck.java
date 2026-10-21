package com.videokit.spike.e4;

import java.util.*;

/** Calls the exact production predicate, substituting only the Android history/proc ports. */
public final class E7WriterDeathGateSelfCheck {
    static int assertions,cases;
    static final long BEGIN=1792224193301L,NOW=BEGIN+1000;
    static E5AOwner owner;
    static class Port implements E7WriterDeathGate.Port {
        List<E7WriterDeathGate.Exit> rows;int history,proc;boolean apiThrows,procThrows;
        E7WriterDeathGate.Proc state=E7WriterDeathGate.Proc.ABSENT;
        Port(List<E7WriterDeathGate.Exit> r){rows=r;}
        public List<E7WriterDeathGate.Exit> history(int pid,int max)throws Exception{history++;ok(pid==4869);ok(max==8);if(apiThrows)throw new Exception("private-other-process-must-not-leak");return rows;}
        public E7WriterDeathGate.Proc proc(int pid)throws Exception{proc++;ok(pid==4869);if(procThrows)throw new Exception("private-other-process-must-not-leak");return state;}
    }
    static void ok(boolean v){assertions++;if(!v)throw new AssertionError("assertion="+assertions+" case="+cases);}
    static E7WriterDeathGate.Exit row(int pid,int uid,String name,long time,int reason){return new E7WriterDeathGate.Exit(pid,uid,name,time,reason,7);}
    static E7WriterDeathGate.Exit good(){return row(4869,10221,"com.videokit.app",BEGIN+36,10);}
    static Port p(E7WriterDeathGate.Exit... rows){return new Port(Arrays.asList(rows));}
    static E7WriterDeathGate.Report run(Port p,String code,int proc){cases++;E7WriterDeathGate.Report r=E7WriterDeathGate.inspect(owner,NOW,p);ok(r.code.equals(code));ok(p.history==1);ok(p.proc==proc);ok(r.passed()==code.equals("PASS_CURRENT_HISTORY_AND_PROC"));ok(r.record().length()<=1400);ok(!r.record().contains("private-other-process"));ok(!r.record().contains("unrelated.secret"));ok(r.record().contains("grant=NONE"));ok(r.record().contains("persistentFact=DISABLED"));return r;}
    public static void main(String[] args)throws Exception{
        owner=new E5AOwner("8c6673b7-38a5-4a24-838d-ca8466d8b75f",4869,10221,"com.videokit.app",BEGIN);
        E7WriterDeathGate.Report r=run(p(good()),"PASS_CURRENT_HISTORY_AND_PROC",1);ok(r.matches==1);ok(r.matching.status==7);ok(r.record().contains("pidReuse=NOT_PROVEN"));ok(r.record().contains("reboot=NOT_PROVEN"));
        r=run(p(),"NO_UNIQUE_MATCH_MISSING",0);ok(r.returned==0);ok(r.matches==0);
        r=run(p(good(),good()),"NO_UNIQUE_MATCH_DUPLICATE",0);ok(r.matches==2);ok(r.matching==null);
        run(p(good(),row(4869,10221,"com.videokit.app",BEGIN,0)),"NO_UNIQUE_MATCH_DUPLICATE",0);
        r=run(p(row(4869,10221,"com.videokit.app",BEGIN,0)),"MATCH_REASON_NON_POSITIVE",0);ok(r.reasonNonPositive==1);ok(r.matching.reason==0);
        run(p(row(4869,10221,"com.videokit.app",BEGIN,-1)),"MATCH_REASON_NON_POSITIVE",0);
        r=run(p(row(42,10221,"com.videokit.app",BEGIN,10)),"NO_UNIQUE_MATCH_MISSING",0);ok(r.pidReject==1);
        r=run(p(row(4869,11,"com.videokit.app",BEGIN,10)),"NO_UNIQUE_MATCH_MISSING",0);ok(r.uidReject==1);
        r=run(p(row(4869,10221,"unrelated.secret",BEGIN,10)),"NO_UNIQUE_MATCH_MISSING",0);ok(r.processReject==1);ok(r.matching==null);
        r=run(p(row(4869,10221,"com.videokit.app",BEGIN-1,10)),"NO_UNIQUE_MATCH_MISSING",0);ok(r.beforeReject==1);
        r=run(p(row(4869,10221,"com.videokit.app",NOW+1,10)),"NO_UNIQUE_MATCH_MISSING",0);ok(r.futureReject==1);
        r=run(p(row(9,9,"unrelated.secret",BEGIN-1,10),good()),"PASS_CURRENT_HISTORY_AND_PROC",1);ok(r.returned==2);ok(r.matches==1);ok(r.pidReject==1&&r.uidReject==1&&r.processReject==1&&r.beforeReject==1);
        Port q=p();q.apiThrows=true;r=run(q,"HISTORY_UNAVAILABLE",0);ok(r.returned==-1);ok(r.matches==-1);ok(r.record().contains("returned=NOT_COLLECTED"));
        run(new Port(null),"HISTORY_NULL",0);
        run(p((E7WriterDeathGate.Exit)null),"HISTORY_MALFORMED",0);
        r=run(new Port(Collections.nCopies(9,good())),"HISTORY_OVER_BUDGET",0);ok(r.returned==9&&r.matches==-1);
        q=p(good());q.state=E7WriterDeathGate.Proc.EXISTS;run(q,"WRITER_VISIBLE_OR_REUSED",1);
        q=p(good());q.state=E7WriterDeathGate.Proc.UNAVAILABLE;run(q,"PROC_UNAVAILABLE",1);
        q=p(good());q.procThrows=true;run(q,"PROC_UNAVAILABLE",1);
        q=p(good());q.state=null;run(q,"PROC_UNAVAILABLE",1);
        // Existing positive report cannot replace the next host's actual current query.
        E7WriterDeathGate.Report old=run(p(good()),"PASS_CURRENT_HISTORY_AND_PROC",1);
        r=run(p(),"NO_UNIQUE_MATCH_MISSING",0);ok(old.passed()&&!r.passed());
        // Inclusive time boundaries, matching the previous production predicate.
        run(p(row(4869,10221,"com.videokit.app",BEGIN,1)),"PASS_CURRENT_HISTORY_AND_PROC",1);
        run(p(row(4869,10221,"com.videokit.app",NOW,1)),"PASS_CURRENT_HISTORY_AND_PROC",1);
        cases++;q=p(good());r=E7WriterDeathGate.inspect(owner,BEGIN-1,q);ok(r.code.equals("CLOCK_OR_OWNER_INVALID"));ok(q.history==0&&q.proc==0);ok(r.record().contains("NOT_COLLECTED"));
        cases++;r=E7WriterDeathGate.notRequested();ok(!r.passed());ok(r.history.equals("NOT_REQUESTED"));ok(r.matches==-1);
        // Full bound: eight real rows still accepted only with exactly one identity/time match.
        E7WriterDeathGate.Exit[] eight=new E7WriterDeathGate.Exit[8];Arrays.fill(eight,row(99,7,"unrelated.secret",BEGIN,10));eight[7]=good();r=run(p(eight),"PASS_CURRENT_HISTORY_AND_PROC",1);ok(r.returned==8&&r.matches==1);
        System.out.println("production_gate_cases="+cases+" assertions="+assertions+" historyCallsPerCaseMax=1 historyLimit=8 admissionGrants=0 mediaReads=0");
    }
}
