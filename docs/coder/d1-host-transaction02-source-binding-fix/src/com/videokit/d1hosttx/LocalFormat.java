package com.videokit.d1hosttx;

import java.io.*;import java.nio.file.*;import java.security.*;import java.util.*;

/** Generated finite host-test document format, deliberately NOT an MP4 validator. */
public final class LocalFormat {
 public static final int MAX=8*1024*1024;
 static final int MAGIC=0x564b4832;
 public static String hash(byte[] raw){try{return hex(MessageDigest.getInstance("SHA-256").digest(raw));}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
 public static String hex(byte[] raw){StringBuilder s=new StringBuilder();for(byte b:raw)s.append(String.format(Locale.ROOT,"%02x",b&255));return s.toString();}
 public static byte[] generated(Binding b)throws IOException {
  byte[] body=new byte[4096];for(int i=0;i<body.length;i++)body[i]=(byte)((i*73+19)&255);
  ByteArrayOutputStream bytes=new ByteArrayOutputStream();try(DataOutputStream out=new DataOutputStream(bytes)){out.writeInt(MAGIC);out.writeUTF(b.key());out.writeInt(body.length);out.writeUTF(hash(body));out.write(body);}return bytes.toByteArray();
 }
 public static byte[] readBounded(Path p)throws IOException {
  long n=Files.size(p);if(n<1||n>MAX)throw new IOException("OUTPUT_VALIDATION_FAILED");ByteArrayOutputStream out=new ByteArrayOutputStream();
  try(InputStream in=Files.newInputStream(p)){byte[] block=new byte[65536];int got;while((got=in.read(block))!=-1){if(out.size()+got>MAX)throw new IOException("OUTPUT_VALIDATION_FAILED");out.write(block,0,got);}}
  if(out.size()!=n)throw new IOException("OUTPUT_VALIDATION_FAILED");return out.toByteArray();
 }
 public static void validate(byte[] raw,Binding expected,long expectedBytes,String expectedSha)throws IOException {
  if(raw.length!=expectedBytes||!hash(raw).equals(expectedSha))throw new IOException("OUTPUT_VALIDATION_FAILED");
  try(DataInputStream in=new DataInputStream(new ByteArrayInputStream(raw))){
   if(in.readInt()!=MAGIC||!in.readUTF().equals(expected.key()))throw new IOException("OUTPUT_VALIDATION_FAILED");
   int count=in.readInt();String sha=in.readUTF();if(count<1||count>MAX||count>in.available())throw new IOException("OUTPUT_VALIDATION_FAILED");
   byte[] body=new byte[count];in.readFully(body);if(in.read()!=-1||!hash(body).equals(sha))throw new IOException("OUTPUT_VALIDATION_FAILED");
  }
 }
 private LocalFormat(){}
}
