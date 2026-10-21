package com.videokit.spike.e4;
import java.io.IOException;
import java.util.*;

/** Finite test selection/order only. Receipt syntax never replaces this host's current proof. */
public final class E11Selection {
    public static final String BATCH="D1-E4A-E11-ACTIVATION-20261018",FINAL_REVIEW="a597bca5c392aaf142f1fa5e74ab4a1aa869fb3cdc367df5005af54e335feaff";
    public static final int VERSION=15;
    public static final String MP4="normalMp4SixRealFrames",AVI="normalAviSixRealFrames",CAPABILITY="capabilityDenialDoesNotOpenSource",CANCEL="cancelRejectsWrongEpochOversizeAndLateFrame";
    public static final Set<String> KEYS=Set.of("class","e4Case","e4Batch","e4BudgetIdentity","e5aObservation","e5aSettlementReceiptSha256","e4NormalReceiptSha256","e11ScopeSha256","e11ReleaseAppSha256","e11ReleaseTestSha256","e11Mp4Receipt","e11AviReceipt");
    private static String value(Map<String,String> args,String key)throws IOException{String s=args.get(key);if(s==null)throw new IOException("E11_SELECTION_MISSING_"+key);return s;}
    public static void require(Map<String,String> args)throws IOException{
        E9Catalog catalog=E9Phase.catalog().catalog();if(!KEYS.containsAll(args.keySet()))throw new IOException("E11_SELECTION_KEYS");
        String selected=value(args,"e4Case");if(!Set.of(MP4,AVI,CAPABILITY,CANCEL).contains(selected)||!value(args,"class").equals("com.videokit.spike.e4.E4DeviceTests#"+selected)||!value(args,"e4Batch").equals(BATCH)||!value(args,"e4BudgetIdentity").equals(E5N2Recovery.BUDGET)||!value(args,"e5aObservation").equals("REVIEWED_ORIGINAL_N2_SETTLEMENT")||!value(args,"e5aSettlementReceiptSha256").equals(FINAL_REVIEW))throw new IOException("E11_EXACT_ACTIVATION_SELECTION");
        for(String k:new String[]{"e11ScopeSha256","e11ReleaseAppSha256","e11ReleaseTestSha256"})E9Record.digest(value(args,k));
        if(selected.equals(MP4)){if(args.containsKey("e11Mp4Receipt")||args.containsKey("e11AviReceipt")||args.containsKey("e4NormalReceiptSha256"))throw new IOException("E11_FIRST_NORMAL_NO_PRIOR_RECEIPTS");return;}
        E9Record mp4=receipt(value(args,"e11Mp4Receipt"),MP4,args,catalog);
        if(selected.equals(AVI)){if(args.containsKey("e11AviReceipt")||args.containsKey("e4NormalReceiptSha256"))throw new IOException("E11_AVI_ONLY_AFTER_MP4");return;}
        E9Record avi=receipt(value(args,"e11AviReceipt"),AVI,args,catalog);
        if(mp4.get("report").equals(avi.get("report"))||mp4.get("task").equals(avi.get("task")))throw new IOException("E11_TWO_DISTINCT_NORMAL_REPORTS");
        byte[] left=mp4.bytes(),right=avi.bytes(),both=Arrays.copyOf(left,left.length+right.length);System.arraycopy(right,0,both,left.length,right.length);
        if(!value(args,"e4NormalReceiptSha256").equals(E9Record.sha(both)))throw new IOException("E11_CURRENT_NORMAL_RECEIPT_INDEX");
    }
    private static E9Record receipt(String packed,String method,Map<String,String> args,E9Catalog catalog)throws IOException{
        E9Record r=E9Record.parse(E9Record.unpack(packed,2048),2048);r.exact("kind","batch","scope","app","test","version","role","catalog","case","report","task","status","received","inputs","outputs","fullEof","ptsUs","ownersReturned");
        if(!r.get("kind").equals("e11NormalReceipt")||!r.get("batch").equals(BATCH)||!r.get("scope").equals(value(args,"e11ScopeSha256"))||!r.get("app").equals(value(args,"e11ReleaseAppSha256"))||!r.get("test").equals(value(args,"e11ReleaseTestSha256"))||!r.get("version").equals(Integer.toString(VERSION))||!r.get("role").equals("ACTIVATION")||!r.get("catalog").equals(catalog.record.hash())||!r.get("case").equals(method)||!r.get("status").equals("READY")||!r.get("received").equals("6")||!r.get("inputs").equals("6")||!r.get("outputs").equals("6")||!r.get("fullEof").equals("true")||!r.get("ptsUs").equals("1000")||!r.get("ownersReturned").equals("true"))throw new IOException("E11_NORMAL_RECEIPT_SCOPE_OR_RESULT");
        E9Record.digest(r.get("report"));E9Record.uuid(r.get("task"));return r;
    }
    private E11Selection(){}
}
