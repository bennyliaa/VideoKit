package com.videokit.fixturetool;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** Only a bounded evidence representation. No container/codec implementation. */
final class ReceiptJson {
    static final int MAX_UTF8 = 1048576;
    static Map<String,Object> map(Object... pairs) {
        Map<String,Object> result = new LinkedHashMap<>();
        if (pairs.length % 2 != 0) throw new IllegalArgumentException("PAIRS_REQUIRED");
        for (int i=0;i<pairs.length;i+=2) result.put((String)pairs[i], pairs[i+1]);
        return result;
    }
    static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length*2);
        for (byte value: bytes) result.append(Character.forDigit((value>>>4)&15,16)).append(Character.forDigit(value&15,16));
        return result.toString();
    }
    static byte[] bytes(ByteBuffer data) {
        ByteBuffer copy = data.duplicate(); byte[] result = new byte[copy.remaining()]; copy.get(result); return result;
    }
    static String hash(ByteBuffer data) { return hash(bytes(data)); }
    static String hash(byte[] data) {
        try { return hex(MessageDigest.getInstance("SHA-256").digest(data)); }
        catch (Exception impossible) { throw new IllegalStateException("SHA256_UNAVAILABLE", impossible); }
    }
    static String json(Object value) {
        StringBuilder out = new StringBuilder(); append(out,value);
        String text = out.toString();
        if (text.getBytes(StandardCharsets.UTF_8).length > MAX_UTF8) throw new IllegalStateException("RECEIPT_LIMIT");
        return text;
    }
    private static void append(StringBuilder out,Object value) {
        if (out.length()>MAX_UTF8) throw new IllegalStateException("RECEIPT_LIMIT");
        if (value==null) out.append("null");
        else if (value instanceof Boolean || value instanceof Number) out.append(value);
        else if (value instanceof Map) {
            out.append('{'); boolean first=true;
            for (Object item:((Map<?,?>)value).entrySet()) {
                Map.Entry<?,?> e=(Map.Entry<?,?>)item;
                if(!first)out.append(','); first=false; quote(out,String.valueOf(e.getKey()));out.append(':');append(out,e.getValue());
            }
            out.append('}');
        } else if (value instanceof Iterable) {
            out.append('[');boolean first=true;
            for(Object item:(Iterable<?>)value){if(!first)out.append(',');first=false;append(out,item);}out.append(']');
        } else quote(out,String.valueOf(value));
    }
    private static void quote(StringBuilder out,String value) {
        out.append('"');
        for(int i=0;i<value.length();i++) {
            char c=value.charAt(i);
            if(c=='"'||c=='\\')out.append('\\').append(c);
            else if(c<' ') {out.append("\\u");String h=Integer.toHexString(c);for(int j=h.length();j<4;j++)out.append('0');out.append(h);}
            else out.append(c);
        }
        out.append('"');
    }
    private ReceiptJson() { }
}
