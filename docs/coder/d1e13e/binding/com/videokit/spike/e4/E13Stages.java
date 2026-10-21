package com.videokit.spike.e4;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
/** Fixed metadata ring; no platform IO, callback or blocking call while an owner lock is held. */
public final class E13Stages {
 public static final int MAX_EVENTS=48,MAX_LINE=500,MAX_TOTAL=24576;
 private static volatile int uid=-1,pid=-1;
 public static void identity(int u,int p){uid=u;pid=p;}
 private static volatile java.util.function.Consumer<String> sink=s->{};
 private static final ArrayDeque<String> events=new ArrayDeque<>();private static final AtomicLong ids=new AtomicLong();
 private static String scope="UNSET",method="UNSET";private static int bytes,dropped;private static long seq;
 public static String owner(String role){return role+"-"+ids.incrementAndGet();}
 public static synchronized void begin(String s,String m){if(!scope.equals("UNSET")&&!scope.equals(s))throw new IllegalStateException("E13_STAGE_SCOPE_ONCE");scope=s;method=m;}
 public static void sink(java.util.function.Consumer<String> s){sink=Objects.requireNonNull(s);}
 public static void at(String owner,String stage,String detail){String line;synchronized(E13Stages.class){line=(++seq)+" scope="+scope+" method="+method+" owner="+owner+" uid="+uid+" pid="+pid+" stage="+stage+" thread="+Thread.currentThread().getName()+" at="+System.nanoTime()+" "+detail;line=line.replaceAll("[^\\x20-\\x7e]","?");if(line.length()>MAX_LINE)line=line.substring(0,MAX_LINE);if(events.size()>=MAX_EVENTS||bytes+line.length()+33>MAX_TOTAL){dropped++;return;}events.add(line);bytes+=line.length()+1;}try{sink.accept(line);}catch(Throwable ignored){/* diagnostic failure is never return evidence */}}
 public static synchronized String snapshot(){return String.join("\n",events)+"\ndropped="+dropped;}
 private E13Stages(){}
}
