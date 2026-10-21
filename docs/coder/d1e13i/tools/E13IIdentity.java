package com.videokit.spike.e4;

import java.io.*;import java.net.*;import java.nio.*;import java.nio.charset.*;import java.nio.file.*;import java.util.*;import java.util.concurrent.*;import java.util.regex.*;
/** Existing reviewed G identity gates and fixed scripts; no executable or network dispatch. */
final class E13IIdentity {
 static final String SCOPE="116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef",BATCH="D1-E13A-SOURCE-20261018",METHOD="ordinarySenderCannotBindCodec";
 static final String COMPONENT="com.videokit.app.test/com.videokit.spike.e4.E13Instrumentation",TEST="com.videokit.spike.e4.E13DeviceTests#"+METHOD;
 static final int CAP=65536,TOTAL=262144;static final long QUALIFICATION=10_000_000_000L;
 static final String INVENTORY="printf 'E13G_AM_BEGIN\\n'; dumpsys activity processes; r=$?; printf '\\nE13G_AM_END rc=%d\\n' \"$r\"; [ \"$r\" -eq 0 ] || exit \"$r\"; printf 'E13G_PS_BEGIN\\n'; ps -A -w -o UID,PID,PPID,NAME,ARGS; r=$?; printf '\\nE13G_PS_END rc=%d\\n' \"$r\"; exit \"$r\"";
 static String utf8(byte[] raw)throws Exception{if(raw.length>CAP)throw new IOException("G_RAW_BOUND");String s=StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(raw)).toString().replace("\r\n","\n");if(s.indexOf('\0')>=0)throw new IOException("G_NUL_REJECTED");return s;}
 static String section(String raw,String begin,String end)throws IOException{int a=raw.indexOf(begin),b=raw.indexOf(end);if(a<0||b<a||a!=raw.lastIndexOf(begin)||b!=raw.lastIndexOf(end))throw new IOException("G_INCOMPLETE_OR_DUPLICATE_SECTION");return raw.substring(a+begin.length(),b);}
 static final class Identity {final int uid,pid,ppid;final String name,args;Identity(int u,int p,int pp,String n,String a){uid=u;pid=p;ppid=pp;name=n;args=a;}String summary(){return uid+":"+pid+":"+ppid+":"+name;}}
 static List<Identity> derive(byte[] raw)throws Exception{
  String s=utf8(raw);if(!s.startsWith("E13G_AM_BEGIN\n")||!s.endsWith("E13G_PS_END rc=0\n"))throw new IOException("G_GLOBAL_BOUNDARIES");
  String am=section(s,"E13G_AM_BEGIN\n","\nE13G_AM_END rc=0\n"),ps=section(s,"E13G_PS_BEGIN\n","\nE13G_PS_END rc=0\n");
  if(!am.startsWith("ACTIVITY MANAGER RUNNING PROCESSES")||am.contains("Permission Denial")||am.contains("DUMP TIMEOUT")||am.contains("Can't find service")||am.contains("Error"))throw new IOException("G_GLOBAL_AM_UNKNOWN");
  Matcher count=Pattern.compile("(?m)^\\s*Instrumentation #\\d+:.*$").matcher(am);int n=0,start=-1;while(count.find()){n++;start=count.start();}if(n!=1||!am.contains("Active instrumentation:"))throw new IOException("G_OTHER_OR_MISSING_ACTIVE_INSTRUMENTATION");
  int end=am.indexOf("mArguments=",start),line=end<0?-1:am.indexOf('\n',end);if(end<0)throw new IOException("G_ARGUMENTS_UNKNOWN");if(line<0)line=am.length();String block=am.substring(start,line);
  if(!block.contains(COMPONENT)||!block.contains("mFinished=false"))throw new IOException("G_ORIGINAL_INSTRUMENTATION_IDENTITY");
  String arguments=block.substring(block.indexOf("mArguments=")+11);
  for(String[] kv:new String[][]{{"e13ScopeSha256",SCOPE},{"e13Batch",BATCH},{"e13Case",METHOD},{"class",TEST}}){Matcher m=Pattern.compile("(?:^|[\\[,{\\s])"+Pattern.quote(kv[0])+"="+Pattern.quote(kv[1])+"(?=[,\\] }]|$)").matcher(arguments);if(!m.find()||m.find())throw new IOException("G_SCOPE_ARGUMENT_IDENTITY");}
  Matcher running=Pattern.compile("ProcessRecord\\{[0-9a-fA-F]+ (\\d{1,7}):com\\.videokit\\.app/u0a221\\}").matcher(block);if(!running.find())throw new IOException("G_RUNNING_TARGET_UNKNOWN");int appPid=number(running.group(1));if(running.find())throw new IOException("G_MULTIPLE_RUNNING_TARGETS");
  String[] lines=ps.strip().split("\n");if(lines.length<2||!lines[0].strip().matches("UID\\s+PID\\s+PPID\\s+NAME\\s+ARGS"))throw new IOException("G_FULL_PS_HEADER");Map<Integer,Identity> rows=new HashMap<>();
  Pattern row=Pattern.compile("\\s*(\\d{1,7})\\s+(\\d{1,7})\\s+(\\d{1,7})\\s+(\\S+)\\s+(.+)");
  for(int i=1;i<lines.length;i++){Matcher m=row.matcher(lines[i]);if(!m.matches())throw new IOException("G_FULL_PS_ROW");Identity v=new Identity(Integer.parseInt(m.group(1)),number(m.group(2)),Integer.parseInt(m.group(3)),m.group(4),m.group(5));if(rows.put(v.pid,v)!=null)throw new IOException("G_DUPLICATE_PID");}
  Identity app=rows.get(appPid);if(app==null||app.uid!=10221||!app.name.equals("com.videokit.app")||!app.args.equals("com.videokit.app")||app.ppid<1||!rows.containsKey(app.ppid))throw new IOException("G_APP_UID_NAME_PARENT");
  Identity instrument=null;String tail="/system/bin com.android.commands.am.Am instrument -w -r -e class "+TEST+" -e e13Case "+METHOD+" -e e13Batch "+BATCH+" -e e13ScopeSha256 "+SCOPE+" "+COMPONENT;
  for(Identity v:rows.values())if(v.uid==2000&&(v.name.equals("app_process")||v.name.equals("app_process64")||v.name.equals("app_process32"))&&(v.args.equals("app_process "+tail)||v.args.equals("/system/bin/app_process "+tail)||v.args.equals("app_process64 "+tail)||v.args.equals("app_process32 "+tail))){if(instrument!=null)throw new IOException("G_DUPLICATE_SCOPE_CLIENT");instrument=v;}
  if(instrument==null||instrument.ppid<1||!rows.containsKey(instrument.ppid)||rows.get(instrument.ppid).uid!=2000)throw new IOException("G_SCOPE_CLIENT_PARENT_UNKNOWN");
  return List.of(app,instrument);
 }
 static int number(String s)throws IOException{if(!s.matches("[1-9][0-9]{0,6}"))throw new IOException("G_PID_ONLY_FROM_VALIDATED_EVIDENCE");return Integer.parseInt(s);}
 static String identityScript(List<Identity> identities)throws Exception{
  if(identities.size()!=2||identities.get(0).uid!=10221||identities.get(1).uid!=2000||identities.get(0).pid==identities.get(1).pid)throw new IOException("G_DERIVED_IDENTITIES_REQUIRED");
  StringBuilder sh=new StringBuilder("printf 'E13G_BOOT_BEGIN\\n'; cat /proc/sys/kernel/random/boot_id || exit 70; printf '\\nE13G_BOOT_END\\n'; ");
  for(Identity v:identities){number(Integer.toString(v.pid));sh.append("printf 'E13G_PID_").append(v.pid).append("_BEGIN\\n'; cat /proc/").append(v.pid).append("/stat || exit 71; printf '\\nE13G_STATUS\\n'; cat /proc/").append(v.pid).append("/status || exit 72; printf '\\nE13G_CMDLINE\\n'; tr '\\000' ' ' < /proc/").append(v.pid).append("/cmdline || exit 73; printf '\\nE13G_PID_").append(v.pid).append("_END\\n'; ");}
  sh.append("printf 'E13G_IDENTITY_COMPLETE\\n'");return sh.toString();
 }
 static void validateIdentity(byte[] raw,List<Identity> expected)throws Exception{
  String s=utf8(raw);String boot=section(s,"E13G_BOOT_BEGIN\n","\nE13G_BOOT_END\n").strip();E9Record.uuid(boot);if(!s.endsWith("E13G_IDENTITY_COMPLETE\n"))throw new IOException("G_IDENTITY_INCOMPLETE");
  for(Identity v:expected){String b=section(s,"E13G_PID_"+v.pid+"_BEGIN\n","\nE13G_PID_"+v.pid+"_END\n");int st=b.indexOf("\nE13G_STATUS\n"),cmd=b.indexOf("\nE13G_CMDLINE\n");if(st<0||cmd<st)throw new IOException("G_IDENTITY_SECTIONS");String stat=b.substring(0,st).strip();int comm=stat.lastIndexOf(") ");if(comm<0||!stat.startsWith(v.pid+" ("))throw new IOException("G_STAT_PID");String[] fields=stat.substring(comm+2).split("\\s+");if(fields.length<20||!fields[1].equals(Integer.toString(v.ppid))||!fields[19].matches("[1-9][0-9]*"))throw new IOException("G_START_TICKS_PARENT_UNKNOWN");String status=b.substring(st+"\nE13G_STATUS\n".length(),cmd);if(!Pattern.compile("(?m)^Uid:\\s+"+v.uid+"\\s+"+v.uid+"\\s+"+v.uid+"\\s+"+v.uid+"\\s*$").matcher(status).find()||!Pattern.compile("(?m)^PPid:\\s+"+v.ppid+"\\s*$").matcher(status).find())throw new IOException("G_FRESH_UID_PARENT_MISMATCH");if(!b.substring(cmd+"\nE13G_CMDLINE\n".length()).strip().equals(v.args))throw new IOException("G_FRESH_ARGV_MISMATCH");}
 }
 private E13IIdentity(){}
}
