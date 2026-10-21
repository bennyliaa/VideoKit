package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** Shared app/host canonical JSON wire record. No caller-chosen JSON defaults or duplicate fields. */
public final class E9Record {
    private final SortedMap<String,String> values;private final byte[] bytes;
    public E9Record(Map<String,String> input,int max)throws IOException {
        TreeMap<String,String> map=new TreeMap<>(input);StringBuilder out=new StringBuilder("{\"e9\":1,\"fields\":{");boolean first=true;
        if(map.isEmpty()||map.size()>48)throw new IOException("E9_RECORD_FIELDS");
        for(Map.Entry<String,String> e:map.entrySet()){
            String k=e.getKey(),v=e.getValue();if(k==null||v==null||!k.matches("[a-z][A-Za-z0-9]{0,31}")||!v.matches("[A-Za-z0-9._:/,@+~-]{1,8192}"))throw new IOException("E9_RECORD_ENCODING");
            if(!first)out.append(',');first=false;out.append('"').append(k).append("\":\"").append(v).append('"');
        }
        out.append("}}\n");bytes=out.toString().getBytes(StandardCharsets.US_ASCII);if(bytes.length>max)throw new IOException("E9_RECORD_BOUND");values=Collections.unmodifiableSortedMap(map);
    }
    public static E9Record parse(byte[] raw,int max)throws IOException{
        if(raw==null||raw.length<6||raw.length>max)throw new IOException("E9_RECORD_BOUND");
        String s=new String(raw,StandardCharsets.US_ASCII),prefix="{\"e9\":1,\"fields\":{";
        if(!s.startsWith(prefix)||!s.endsWith("}}\n"))throw new IOException("E9_RECORD_HEADER");
        String inner=s.substring(prefix.length(),s.length()-3);TreeMap<String,String> m=new TreeMap<>();
        java.util.regex.Pattern field=java.util.regex.Pattern.compile("\"([a-z][A-Za-z0-9]{0,31})\":\"([A-Za-z0-9._:/,@+~-]{1,8192})\"(?:,|$)");
        int cursor=0;java.util.regex.Matcher matcher=field.matcher(inner);
        while(cursor<inner.length()){matcher.region(cursor,inner.length());if(!matcher.lookingAt()||m.put(matcher.group(1),matcher.group(2))!=null)throw new IOException("E9_RECORD_DUPLICATE_OR_FIELD");cursor=matcher.end();}
        E9Record r=new E9Record(m,max);if(!Arrays.equals(raw,r.bytes))throw new IOException("E9_RECORD_NONCANONICAL");return r;
    }
    public String get(String key)throws IOException{String value=values.get(key);if(value==null)throw new IOException("E9_RECORD_MISSING_"+key);return value;}
    public long number(String key,long max)throws IOException{String v=get(key);if(!v.matches("0|[1-9][0-9]{0,18}"))throw new IOException("E9_RECORD_NUMBER");try{long n=Long.parseLong(v);if(n>max)throw new IOException("E9_RECORD_NUMBER_BOUND");return n;}catch(NumberFormatException e){throw new IOException("E9_RECORD_NUMBER_BOUND");}}
    public void exact(String... keys)throws IOException{if(!values.keySet().equals(new TreeSet<>(Arrays.asList(keys))))throw new IOException("E9_RECORD_SCHEMA");}
    public Map<String,String> fields(){return values;}
    public byte[] bytes(){return bytes.clone();}
    public String hash(){return sha(bytes);}
    public static String sha(byte[] data){try{StringBuilder b=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(data))b.append(String.format(Locale.ROOT,"%02x",x&255));return b.toString();}catch(Exception impossible){throw new IllegalStateException(impossible);}}
    public static String pack(byte[] bytes){return java.util.Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);}
    public static byte[] unpack(String value,int max)throws IOException{try{if(value.length()>max*2)throw new IOException("E9_PACK_BOUND");byte[] b=java.util.Base64.getUrlDecoder().decode(value);if(b.length>max||!pack(b).equals(value))throw new IOException("E9_PACK_ENCODING");return b;}catch(IllegalArgumentException e){throw new IOException("E9_PACK_ENCODING");}}
    public static void digest(String s)throws IOException{if(s==null||!s.matches("[a-f0-9]{64}"))throw new IOException("E9_DIGEST");}
    public static void uuid(String s)throws IOException{try{if(s==null||!UUID.fromString(s).toString().equals(s))throw new Exception();}catch(Exception e){throw new IOException("E9_UUID");}}
    public static Map<String,String> map(String... pairs){if(pairs.length%2!=0)throw new IllegalArgumentException();Map<String,String> m=new TreeMap<>();for(int i=0;i<pairs.length;i+=2)if(m.put(pairs[i],pairs[i+1])!=null)throw new IllegalArgumentException("DUPLICATE");return m;}
}
