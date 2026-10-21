package com.videokit.spike.c14;
import java.util.*;
import java.util.concurrent.atomic.*;
import java.io.*;
public final class C14EncoderSelfCheck {
    static int checks;static void yes(boolean value){if(!value)throw new AssertionError("check "+checks);checks++;}
    interface Action{void run()throws Exception;}static void rejects(String code,Action action)throws Exception{try{action.run();throw new AssertionError("accepted "+code);}catch(IOException e){yes(code.equals(e.getMessage()));}}
    static EncoderNegotiation.Descriptor d(String name,boolean sw,int[] colors)throws Exception{return new EncoderNegotiation.Descriptor(name,name,!sw,sw,false,true,colors,new int[]{1,256});}
    static final class Driver implements EncoderNegotiation.Driver {
        int creates,configs,starts,closes,failures;boolean live,support=true,failConfigure,failAll,failClose,createUnknown,cancelAfterConfigure;AtomicBoolean cancel=new AtomicBoolean();AtomicLong clock=new AtomicLong();boolean expireConfigure;final List<String> events=new ArrayList<>();
        public boolean supported(EncoderNegotiation.Candidate c){return support;}
        public void create(EncoderNegotiation.Candidate c)throws Exception{yes(!live);live=true;creates++;if(createUnknown)throw new IOException("create error");}
        public void configure(EncoderNegotiation.Candidate c)throws Exception{configs++;if(cancelAfterConfigure)cancel.set(true);if(expireConfigure)clock.set(EncoderNegotiation.BUDGET_NS);if(failAll || (failConfigure && configs==1))throw new IOException("configure error");}
        public void start(EncoderNegotiation.Candidate c){starts++;}
        public void release()throws Exception{closes++;if(failClose || createUnknown)throw new IOException("close uncertain");live=false;}
        public boolean released(){return !live;}public void event(String phase,EncoderNegotiation.Candidate c,Throwable e,String outcome,boolean first){events.add(phase+":"+outcome);if(e!=null)failures++;}
        EncoderNegotiation engine(){return new EncoderNegotiation(this,cancel::get,clock::get);}
    }
    public static void main(String[] args)throws Exception{
        var hw=d("OMX.test.avc",false,new int[]{19,21,EncoderNegotiation.FLEX});var sw=d("c2.android.avc.encoder",true,new int[]{19,EncoderNegotiation.FLEX});var plan=EncoderNegotiation.plan(List.of(sw,hw));yes(plan.size()==4);yes(plan.get(0).codec==hw);yes(plan.get(1).codec==sw);yes(plan.get(2).color==19);yes(plan.get(3).color==EncoderNegotiation.FLEX);yes(!plan.get(0).baseline && plan.get(2).baseline);
        yes(EncoderNegotiation.plan(List.of(hw,hw,sw)).size()==4);yes(EncoderNegotiation.plan(List.of(d("no.color",false,new int[]{7}))).isEmpty());yes(EncoderNegotiation.plan(List.of(new EncoderNegotiation.Descriptor("wrong.size","wrong.size",true,false,false,false,new int[]{19},new int[0]))).isEmpty());
        Driver deny=new Driver();deny.support=false;var n=deny.engine();rejects("PIPE_CAPABILITY_UNSUPPORTED",()->n.run(plan));yes(n.attempts()==0 && n.proposals()==4 && deny.creates==0);
        Driver once=new Driver();once.failConfigure=true;var engine=once.engine();yes(engine.run(plan)==plan.get(1));yes(once.creates==2 && once.closes==1 && once.starts==1);yes(engine.attempts()==2);yes(engine.firstError().equals("PIPE_ENCODER_CONFIGURE_FAILED"));yes(once.events.indexOf("CLOSE:RELEASED")<once.events.lastIndexOf("CREATE:BEGIN"));once.release();yes(once.released());
        Driver all=new Driver();all.failAll=true;var exhausted=all.engine();rejects("PIPE_ENCODER_CONFIGURE_FAILED",()->exhausted.run(plan));yes(all.creates==4 && all.closes==4 && all.released());yes(exhausted.firstError().equals("PIPE_ENCODER_CONFIGURE_FAILED"));
        Driver stuck=new Driver();stuck.failConfigure=true;stuck.failClose=true;var hold=stuck.engine();rejects("PIPE_ENCODER_CONFIGURE_FAILED",()->hold.run(plan));yes(hold.attempts()==1 && stuck.live && stuck.closes==1);
        Driver unknown=new Driver();unknown.createUnknown=true;rejects("PIPE_ENCODER_CREATE_FAILED",()->unknown.engine().run(plan));yes(unknown.creates==1 && unknown.live);
        Driver cancel=new Driver();cancel.cancel.set(true);rejects("PIPE_CANCELLED",()->cancel.engine().run(plan));yes(cancel.creates==0);
        Driver midway=new Driver();midway.cancelAfterConfigure=true;rejects("PIPE_CANCELLED",()->midway.engine().run(plan));yes(midway.creates==1 && midway.closes==1 && midway.released() && midway.starts==0);
        Driver timeout=new Driver();timeout.expireConfigure=true;rejects("PIPE_ENCODER_NEGOTIATION_DEADLINE",()->timeout.engine().run(plan));yes(timeout.creates==1 && timeout.closes==1 && timeout.released());
        Driver budget=new Driver();rejects("PIPE_ENCODER_ATTEMPT_BUDGET",()->budget.engine().run(Arrays.asList(plan.get(0),plan.get(1),plan.get(2),plan.get(3),plan.get(0))));yes(budget.creates==0);
        rejects("PIPE_ENCODER_METADATA_BUDGET",()->d("bad/path",false,new int[]{19}));rejects("PIPE_ENCODER_METADATA_BUDGET",()->d("x".repeat(129),false,new int[]{19}));rejects("PIPE_ENCODER_METADATA_BUDGET",()->d("huge",false,new int[65]));rejects("PIPE_ENCODER_METADATA_BUDGET",()->new EncoderNegotiation.Descriptor("odd","odd",true,false,false,true,new int[]{19},new int[]{1}));rejects("PIPE_ENCODER_METADATA_BUDGET",()->EncoderNegotiation.plan(Collections.nCopies(17,hw)));
        int[] mutable={19};var copied=d("copied",false,mutable);mutable[0]=7;yes(EncoderNegotiation.plan(List.of(copied)).get(0).color==19);
        yes(EncoderNegotiation.diagnostic("android.media.MediaCodec.error_neg_38").endsWith("neg_38"));yes(EncoderNegotiation.diagnostic("/private/source.mp4?token=x").equals("UNAVAILABLE_PATTERN"));yes(EncoderNegotiation.diagnostic("x".repeat(200)).equals("UNAVAILABLE_PATTERN"));
        System.out.println("PASS "+checks+" finite capability/configure/release/cancel/deadline/metadata/diagnostic counterexamples; fake Driver is NOT actual Android codec support");
    }
}
