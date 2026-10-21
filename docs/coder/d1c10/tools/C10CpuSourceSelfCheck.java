package com.videokit.spike.c10;
import java.io.IOException;
import java.util.concurrent.*;
public final class C10CpuSourceSelfCheck {
    static int checks;
    static void yes(boolean value){if(!value)throw new AssertionError("case "+checks);checks++;}
    public static void main(String[] args)throws Exception {
        try(AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime()){
            LeaseRegistry leases=new LeaseRegistry();long gen=leases.create();
            AsyncReadBridge.Provider large=c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
                public Long length(){return 1L<<34;}
                public CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){b[o]=(byte)(p&255);return CompletableFuture.completedFuture(1);}
                public CompletionStage<Void> closeAsync(){return CompletableFuture.completedFuture(null);}
            });
            AsyncReadBridge source=new AsyncReadBridge(runtime,large,leases,gen,1000);yes(source.open(0,-1)==1L<<34);
            source.seekAbsolute((1L<<33)+17);byte[] bytes=new byte[8];yes(source.read(bytes,0,8)==1);yes(bytes[0]==17);
            source.seekAbsolute(1L<<34);yes(source.read(bytes,0,8)==-1);
            source.close();leases.retire(gen);yes(leases.awaitReleased(gen,1000));yes(leases.query(gen).operations==0);
            long zeroGen=leases.create();AsyncReadBridge zero=new AsyncReadBridge(runtime,c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
                public Long length(){return 100L;}public CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){return CompletableFuture.completedFuture(0);}public CompletionStage<Void> closeAsync(){return CompletableFuture.completedFuture(null);}
            }),leases,zeroGen,1000);zero.open(0,-1);
            try{zero.read(bytes,0,8);throw new AssertionError("zero read accepted");}catch(IOException expected){yes("INVALID_READ_RESULT".equals(expected.getMessage()));}
            zero.close();leases.retire(zeroGen);yes(leases.awaitReleased(zeroGen,1000));
            long blockedGen=leases.create();CompletableFuture<Integer> pending=new CompletableFuture<>();CountDownLatch entered=new CountDownLatch(1);
            AsyncReadBridge blocked=new AsyncReadBridge(runtime,c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
                public Long length(){return 100L;}public CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){entered.countDown();return pending;}public CompletionStage<Void> closeAsync(){return CompletableFuture.completedFuture(null);}
            }),leases,blockedGen,100);blocked.open(0,-1);
            try{blocked.read(bytes,0,8);throw new AssertionError("deadline not reached");}catch(IOException expected){yes("SOURCE_TIMEOUT".equals(expected.getMessage()));}
            yes(entered.getCount()==0);leases.retire(blockedGen);yes(!leases.awaitReleased(blockedGen,50));yes(leases.query(blockedGen).operations==1);
            pending.complete(1);yes(leases.awaitReleased(blockedGen,1000));
            try{blocked.seekAbsolute(1);throw new AssertionError("retired seek accepted");}catch(IOException expected){checks++;}
        }
        System.out.println("PASS "+checks+" provider/short-read/EOF/>2GiB/quarantine source assertions");
    }
}
