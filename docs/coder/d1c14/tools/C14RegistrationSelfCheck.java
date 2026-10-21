package com.videokit.spike.c14;
public final class C14RegistrationSelfCheck {
    static int checks;static void yes(boolean value){if(!value)throw new AssertionError("case "+checks);checks++;}
    interface Work{void run();}static void reject(int code,Work work){try{work.run();throw new AssertionError("accepted");}catch(RegistrationProtocol.Rejected expected){yes(expected.code==code);yes(expected.getMessage().equals(RegistrationProtocol.name(code)));}}
    public static void main(String[] args){
        for(int flags:new int[]{0,2,16,32,50,Integer.MIN_VALUE})yes(RegistrationProtocol.synchronous(flags));
        for(int flags:new int[]{1,3,17,51,-1})yes(!RegistrationProtocol.synchronous(flags));
        for(int i=1;i<31;i++){yes(RegistrationProtocol.synchronous(1<<i));yes(!RegistrationProtocol.synchronous((1<<i)|1));}
        RegistrationProtocol.identity(200,99060,100,10221);checks++;
        for(int[] pair:new int[][]{{0,99060},{100,99060},{200,0},{200,10221},{200,80000},{-1,99060}})reject(RegistrationProtocol.IDENTITY,()->RegistrationProtocol.identity(pair[0],pair[1],100,10221));
        for(int result:new int[]{RegistrationProtocol.OK,RegistrationProtocol.DUPLICATE,RegistrationProtocol.RETIRED})yes(RegistrationProtocol.validateReply(16,RegistrationProtocol.MAGIC,1,result,1)==result);
        reject(RegistrationProtocol.REPLY_LENGTH,()->RegistrationProtocol.validateReply(12,RegistrationProtocol.MAGIC,1,0,1));
        reject(RegistrationProtocol.REPLY_TRAILING,()->RegistrationProtocol.validateReply(20,RegistrationProtocol.MAGIC,1,0,1));
        reject(RegistrationProtocol.REPLY_MAGIC,()->RegistrationProtocol.validateReply(16,0,1,0,1));
        reject(RegistrationProtocol.REPLY_VERSION,()->RegistrationProtocol.validateReply(16,RegistrationProtocol.MAGIC,2,0,1));
        reject(RegistrationProtocol.REPLY_ENUM,()->RegistrationProtocol.validateReply(16,RegistrationProtocol.MAGIC,1,999,0));
        reject(RegistrationProtocol.REPLY_GENERATION,()->RegistrationProtocol.validateReply(16,RegistrationProtocol.MAGIC,1,0,0));
        reject(RegistrationProtocol.REPLY_GENERATION,()->RegistrationProtocol.validateReply(16,RegistrationProtocol.MAGIC,1,0,WorkerGenerations.MAX_WORKERS+1));
        reject(RegistrationProtocol.REPLY_GENERATION,()->RegistrationProtocol.validateReply(16,RegistrationProtocol.MAGIC,1,RegistrationProtocol.IDENTITY,2));
        for(int code=RegistrationProtocol.ONEWAY;code<=RegistrationProtocol.MISSING;code++){final int expected=code;reject(expected,()->RegistrationProtocol.validateReply(16,RegistrationProtocol.MAGIC,1,expected,0));yes(!RegistrationProtocol.name(code).equals("CPU_REG_UNKNOWN"));}
        WorkerGenerations workers=new WorkerGenerations();WorkerGenerations.Worker failed=workers.register(new Object(),200,99060,false);yes(!failed.primary);yes(workers.primary()==null);yes(!workers.accept(failed));workers.bindingClosed();yes(!workers.canRelease());workers.died(failed);yes(workers.canRelease());
        System.out.println("PASS "+checks+" registration flags/kernel-identity/fixed-reply/fatal-worker counterexamples; remote Binder NOT_RUN");
    }
}
