package com.videokit.d1hosttx;

import com.videokit.spike.e4.E13SourceGroup;
import java.io.*;
import java.util.*;

/** This finite host's grant tuple. Original source authority remains E13SourceGroup. */
public final class Binding {
 public final String transactionId,grant,sourceTask,sourceInstance;public final long epoch,generation;public final int outputVersion,uid,pid;
 private final E13SourceGroup sourceAuthority;private final E13SourceGroup.Identity sourceIdentity;private final String encodedKey;
 public Binding(String id,String grant,E13SourceGroup source,int outputVersion)throws IOException {
  if(id==null||!id.matches("[A-Za-z0-9_-]{1,64}")||grant==null||!grant.matches("[A-Za-z0-9_-]{1,64}")||outputVersion<1)throw new IOException("OUTPUT_GRANT_INVALID");
  if(source==null||source.identity==null)throw new IOException("SOURCE_IDENTITY_REJECTED");
  this.transactionId=id;this.grant=grant;this.outputVersion=outputVersion;sourceAuthority=source;sourceIdentity=source.identity;
  E13SourceGroup.Identity s=sourceIdentity;sourceTask=s.task;sourceInstance=s.instance;epoch=s.epoch;uid=s.uid;pid=s.pid;generation=source.snapshot().generation;
  if(sourceTask==null||sourceInstance==null)throw new IOException("SOURCE_IDENTITY_REJECTED");
  encodedKey=encodeKey();if(encodedKey.length()>2048)throw new IOException("OUTPUT_GRANT_INVALID");
 }
 private static void text(DataOutputStream out,String value)throws IOException {
  // Length and exact Java UTF-16 code units: delimiters, NUL and surrogate
  // values cannot alias through separator concatenation or lossy UTF-8.
  out.writeInt(value.length());for(int i=0;i<value.length();i++)out.writeChar(value.charAt(i));
 }
 private String encodeKey()throws IOException {
  ByteArrayOutputStream b=new ByteArrayOutputStream();try(DataOutputStream out=new DataOutputStream(b)){
   out.writeInt(0x48544232);text(out,transactionId);text(out,grant);out.writeInt(uid);out.writeInt(pid);text(out,sourceTask);text(out,sourceInstance);out.writeLong(epoch);out.writeLong(generation);out.writeInt(outputVersion);
  }return "HTB2:"+Base64.getEncoder().encodeToString(b.toByteArray());
 }
 public String key(){return encodedKey;}
 public void require(Binding actual)throws IOException {
  if(actual==null||!transactionId.equals(actual.transactionId)||!grant.equals(actual.grant)||uid!=actual.uid||pid!=actual.pid||!sourceTask.equals(actual.sourceTask)||!sourceInstance.equals(actual.sourceInstance)||epoch!=actual.epoch||generation!=actual.generation||outputVersion!=actual.outputVersion)throw new IOException("OUTPUT_GRANT_INVALID");
  if(sourceAuthority!=actual.sourceAuthority||sourceIdentity!=actual.sourceIdentity)throw new IOException("OUTPUT_GRANT_INVALID");
 }
 public void requireSource(E13SourceGroup source)throws IOException {
  if(source==null)throw new IOException("SOURCE_IDENTITY_REJECTED");E13SourceGroup.Identity s=source.identity;
  if(s==null||s.uid!=uid||s.pid!=pid||!Objects.equals(s.task,sourceTask)||s.epoch!=epoch||!Objects.equals(s.instance,sourceInstance)||source.snapshot().generation!=generation)throw new IOException("SOURCE_IDENTITY_REJECTED");
  if(source!=sourceAuthority||s!=sourceIdentity)throw new IOException("SOURCE_IDENTITY_REJECTED");
 }
}
