package com.videokit.spike.e4;
public final class FixtureBoundsSelfCheck {
    static int count;
    interface Op {void run();}
    static void check(boolean b){if(!b)throw new AssertionError();count++;}
    static void rejects(Op op){try{op.run();throw new AssertionError("accepted");}catch(IllegalStateException expected){count++;}}
    public static void main(String[] args){
        E5CFixtureBounds b=new E5CFixtureBounds();for(int i=0;i<64;i++)b.add(0);check(b.nodes()==64);rejects(()->b.add(0));
        E5CFixtureBounds c=new E5CFixtureBounds();for(int i=0;i<4;i++)c.add(65536);check(c.bytes()==262144);rejects(()->c.add(1));
        rejects(()->new E5CFixtureBounds().add(-1));rejects(()->new E5CFixtureBounds().add(65537));
        E5CFixtureBounds.deadline(100,100+E5CFixtureBounds.DEADLINE_NS-1);check(true);
        rejects(()->E5CFixtureBounds.deadline(100,100+E5CFixtureBounds.DEADLINE_NS));
        long start=Long.MAX_VALUE-10;E5CFixtureBounds.deadline(start,start+20);check(true);
        rejects(()->E5CFixtureBounds.deadline(start,start+E5CFixtureBounds.DEADLINE_NS));
        System.out.println("PASS finite policy cases="+count+" Android symlink/FD/flock=NOT_RUN");
    }
}
