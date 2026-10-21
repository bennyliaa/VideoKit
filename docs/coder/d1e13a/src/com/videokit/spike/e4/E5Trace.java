package com.videokit.spike.e4;

import java.util.ArrayList;
import java.util.List;

/** Task-local metadata only. No lock is held while codec, Binder or filesystem code executes. */
public final class E5Trace {
    private final long began=System.nanoTime();private final List<String> rows=new ArrayList<>();
    private String phase="NEW",first="";private long phaseAt;private int dropped;
    public static String safe(String text){if(text==null)return "";String clean=text.replaceAll("[^A-Za-z0-9_.:=,; -]","_");return clean.substring(0,Math.min(160,clean.length()));}
    public synchronized void event(String stage,String detail){
        phase=safe(stage);phaseAt=(System.nanoTime()-began)/1000000;
        String row=safe(phaseAt+":"+phase+":"+safe(detail));if(rows.size()==64){rows.remove(16);dropped++;}rows.add(row);
    }
    public synchronized void failure(String code){if(first.isEmpty())first=safe(code);event("FIRST_ERROR",code);}
    public synchronized String phase(){return phase;}
    public synchronized String first(){return first;}
    public synchronized long phaseAtMs(){return phaseAt;}
    public synchronized int dropped(){return dropped;}
    public synchronized List<String> rows(){return List.copyOf(rows);}
    public synchronized String tail(){int start=Math.max(0,rows.size()-8);return String.join(";",rows.subList(start,rows.size()));}
}
