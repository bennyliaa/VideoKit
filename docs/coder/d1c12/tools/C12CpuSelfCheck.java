package com.videokit.spike.c12;
import java.io.IOException;
/** Independent counterexamples include large offsets and adversarial primitive headers. */
public final class C12CpuSelfCheck {
    static int checks;
    interface Work {void run()throws Exception;}
    static void yes(boolean condition){if(!condition)throw new AssertionError("case "+checks);checks++;}
    static void rejected(Work call)throws Exception {try{call.run();throw new AssertionError("accepted case "+checks);}catch(IOException expected){checks++;}}
    static void frame(int magic,int version,String task,long epoch,int pid,int uid,int w,int h,int stride,int off,int len,long pts,int seq)throws IOException {
        CpuFrameRules.frame(magic,version,task,"task",epoch,7,12,99001,pid,uid,w,h,stride,off,len,pts,1000000,seq);
    }
    public static void main(String[] args)throws Exception {
        yes(CpuFrameRules.seek(0,1L<<33,0,1L<<34)==1L<<33);
        yes(CpuFrameRules.seek(1L<<33,-5,1,1L<<34)==(1L<<33)-5);
        yes(CpuFrameRules.seek(0,-1,2,1L<<34)==(1L<<34)-1);
        yes(CpuFrameRules.seek(0,0,0x10000,1L<<34)==1L<<34);
        rejected(()->CpuFrameRules.seek(0,-1,0,10));rejected(()->CpuFrameRules.seek(0,11,0,10));
        rejected(()->CpuFrameRules.seek(0,Long.MAX_VALUE,2,10));rejected(()->CpuFrameRules.seek(0,Long.MIN_VALUE,2,10));
        rejected(()->CpuFrameRules.seek(0,0,4,10));rejected(()->CpuFrameRules.seek(0,0,0,0));
        rejected(()->CpuFrameRules.seek(11,0,1,10));
        frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,144,1024,0,147456,1000000,1);checks++;
        rejected(()->frame(0,1,"task",7,12,99001,256,144,1024,0,147456,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,2,"task",7,12,99001,256,144,1024,0,147456,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"other",7,12,99001,256,144,1024,0,147456,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",8,12,99001,256,144,1024,0,147456,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,13,99001,256,144,1024,0,147456,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99002,256,144,1024,0,147456,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,Integer.MAX_VALUE,144,1024,0,147456,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,Integer.MAX_VALUE,Integer.MAX_VALUE,0,147456,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,144,-1024,0,147456,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,144,1024,Integer.MAX_VALUE,Integer.MAX_VALUE,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,144,1024,0,-1,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,144,1024,0,147455,1000000,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,144,1024,0,147456,Long.MIN_VALUE,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,144,1024,0,147456,999999,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,144,1024,0,147456,3000001,1));
        rejected(()->frame(CpuFrameRules.MAGIC,1,"task",7,12,99001,256,144,1024,0,147456,1000000,2));
        CpuFrameRules.timestamp(90000,1,90000,1000000,0,65536);checks++;
        CpuFrameRules.timestamp(90000,1,90000,1000000,1,65536);checks++;
        rejected(()->CpuFrameRules.timestamp(Long.MIN_VALUE,1,90000,1000000,0,65536));
        rejected(()->CpuFrameRules.timestamp(90000,0,90000,1000000,0,65536));
        rejected(()->CpuFrameRules.timestamp(90000,1,0,1000000,0,65536));
        rejected(()->CpuFrameRules.timestamp(90000,1,90000,999999,0,65536));
        rejected(()->CpuFrameRules.timestamp(90000,1,90000,1000000,2,65536));
        rejected(()->CpuFrameRules.timestamp(90000,1,90000,1000000,0,262145));
        rejected(()->CpuFrameRules.timestamp(90000,1,90000,1000000,0,-1));
        CpuFrameRules.sourceLength(1L<<33);checks++;
        rejected(()->CpuFrameRules.sourceLength(-1));rejected(()->CpuFrameRules.sourceLength(0));rejected(()->CpuFrameRules.sourceLength(CpuFrameRules.MAX_SOURCE+1));
        CpuFrameRules.allocationQuota(67108864,147456);checks++;
        rejected(()->CpuFrameRules.allocationQuota(67108865,147456));rejected(()->CpuFrameRules.allocationQuota(147456,147457));
        rejected(()->CpuFrameRules.allocationQuota(147456,0));rejected(()->CpuFrameRules.allocationQuota(-1,-1));
        CpuFrameRules.acknowledgement(CpuFrameRules.ACK,4);checks++;CpuFrameRules.acknowledgement(CpuFrameRules.ACK,12);checks++;
        rejected(()->CpuFrameRules.acknowledgement(0,4));rejected(()->CpuFrameRules.acknowledgement(-9,12));
        rejected(()->CpuFrameRules.acknowledgement(CpuFrameRules.ACK,0));rejected(()->CpuFrameRules.acknowledgement(CpuFrameRules.ACK,4096));
        System.out.println("PASS "+checks+" CPU protocol/64-bit seek counterexamples; no Android/native execution");
    }
}
