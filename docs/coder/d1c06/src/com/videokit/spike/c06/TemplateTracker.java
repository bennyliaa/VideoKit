package com.videokit.spike.c06;

/** Independent normalized-correlation baseline: translation only, no downloaded weights. */
public final class TemplateTracker {
    public enum State { TRACKED, LOST, AMBIGUOUS, STALE }
    public static final class Result {public final State state;public final int x,y;public final double score;public final long revision;Result(State s,int x,int y,double score,long revision){state=s;this.x=x;this.y=y;this.score=score;this.revision=revision;}}
    private byte[] template;private int x,y,w,h;private long revision;private double mean,variance;
    public synchronized long correct(byte[] frame,int width,int height,int x,int y,int w,int h){
        dimensions(frame,width,height);if(w<4 || h<4 || w>32 || h>32 || x<0 || y<0 || x+w>width || y+h>height)throw new IllegalArgumentException("ROI_BOUNDS");
        this.x=x;this.y=y;this.w=w;this.h=h;template=new byte[w*h];double sum=0,squared=0;
        for(int row=0;row<h;row++)for(int col=0;col<w;col++){int v=frame[(y+row)*width+x+col]&255;template[row*w+col]=(byte)v;sum+=v;squared+=v*v;}
        mean=sum/(w*h);variance=squared-sum*sum/(w*h);return ++revision;
    }
    private static void dimensions(byte[] frame,int width,int height){if(width<=0 || height<=0 || width>256 || height>256 || frame.length!=width*height)throw new IllegalArgumentException("FRAME_BOUNDS");}
    public synchronized Result update(byte[] frame,int width,int height,long expectedRevision){
        dimensions(frame,width,height);if(expectedRevision!=revision)return new Result(State.STALE,x,y,0,revision);
        if(template==null || variance<1)return new Result(State.LOST,x,y,0,revision);
        int minX=Math.max(0,x-24),maxX=Math.min(width-w,x+24),minY=Math.max(0,y-24),maxY=Math.min(height-h,y+24);double best=-2;int bx=x,by=y;
        for(int row=minY;row<=maxY;row++)for(int col=minX;col<=maxX;col++){double score=score(frame,width,col,row);if(score>best){best=score;bx=col;by=row;}}
        if(best<.80)return new Result(State.LOST,x,y,best,revision);
        double competitor=-2;for(int row=minY;row<=maxY;row++)for(int col=minX;col<=maxX;col++){if(Math.abs(col-bx)<w/2 && Math.abs(row-by)<h/2)continue;competitor=Math.max(competitor,score(frame,width,col,row));}
        if(best-competitor<.05)return new Result(State.AMBIGUOUS,x,y,best,revision);
        x=bx;y=by;return new Result(State.TRACKED,x,y,best,revision);
    }
    private double score(byte[] frame,int width,int px,int py){
        double sum=0,squared=0,cross=0;for(int row=0;row<h;row++)for(int col=0;col<w;col++){int v=frame[(py+row)*width+px+col]&255;sum+=v;squared+=v*v;cross+=v*((template[row*w+col]&255)-mean);}
        double var=squared-sum*sum/(w*h);return var<=0?-1:cross/Math.sqrt(variance*var);
    }
    public static void main(String[] args){
        int width=96,height=64;byte[] texture=new byte[64];new java.util.Random(42).nextBytes(texture);TemplateTracker tracker=new TemplateTracker();
        byte[] first=new byte[width*height];paint(first,width,10,10,texture);long rev=tracker.correct(first,width,height,10,10,8,8);
        byte[] moved=new byte[width*height];paint(moved,width,15,13,texture);Result r=tracker.update(moved,width,height,rev);require(r.state==State.TRACKED && r.x==15 && r.y==13,"synthetic translation");
        require(tracker.update(new byte[width*height],width,height,rev).state==State.LOST,"occluded target LOST");
        paint(moved,width,29,13,texture);require(tracker.update(moved,width,height,rev).state==State.AMBIGUOUS,"identical alternatives AMBIGUOUS");
        long corrected=tracker.correct(moved,width,height,29,13,8,8);require(tracker.update(moved,width,height,rev).state==State.STALE,"old revision rejected after correction");
        byte[] next=new byte[width*height];paint(next,width,32,14,texture);require(tracker.update(next,width,height,corrected).state==State.TRACKED,"tracking resumes from correction");
        System.out.println("NOT_RUN real-video target coverage, scale/rotation, multi-target identity/reentry, face detection quality; .80/.05 are experimental only");
    }
    private static void paint(byte[] frame,int width,int x,int y,byte[] texture){for(int row=0;row<8;row++)System.arraycopy(texture,row*8,frame,(y+row)*width+x,8);}
    private static void require(boolean result,String name){if(!result)throw new AssertionError(name);System.out.println("PASS "+name);}
}
