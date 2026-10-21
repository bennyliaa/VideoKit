package com.videokit.spike.e4;
import android.content.*;import android.os.*;import androidx.test.runner.AndroidJUnitRunner;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
public final class E13EProtocolCheck {
 static void need(boolean b,String s){if(!b)throw new AssertionError(s);}static void until(java.util.function.BooleanSupplier s)throws Exception{long e=System.nanoTime()+5000000000L;while(!s.getAsBoolean()&&System.nanoTime()<e)Thread.sleep(2);need(s.getAsBoolean(),"bounded same-original wait");}
 static final class Late extends E13EAndroidCheck.Router {
  final CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1),ackEntered=new CountDownLatch(1);Thread originalCallback;int snapshots;
  public boolean bind(Intent i,ServiceConnection c){
   if(android.os.Process.myUid()==10228){binds++;E13Stages.sink(s->{if(s.contains("CALLBACK_ENTER")){entered.countDown();try{release.await();}catch(InterruptedException e){throw new RuntimeException(e);}}if(s.contains("ORIGINAL_ACK_WAIT_ENTER"))ackEntered.countDown();});originalCallback=new Thread(()->c.onServiceConnected(i.component,new Binder()),"platform-main-original-target");originalCallback.start();try{need(entered.await(2,TimeUnit.SECONDS),"target original callback entered");}catch(Exception e){throw new RuntimeException(e);}throw new SecurityException("CONTROLLED_DENIAL_WITH_CALLBACK_IN_FLIGHT");}
   if(i.component.pkg.equals("com.videokit.e13.sender")){binds++;IBinder proxy=(code,in,out,flags)->{if(code==2||code==3){snapshots++;if(code==3){new Thread(()->{try{need(ackEntered.await(2,TimeUnit.SECONDS),"actual original ACK entered");release.countDown();originalCallback.join(2000);}catch(InterruptedException e){throw new RuntimeException(e);}},"platform-original-late-return").start();}}return sender.transact(code,in,out,flags);};new Thread(()->c.onServiceConnected(i.component,proxy),"platform-main-fixture-client").start();return true;}
   return super.bind(i,c);
  }
 }
 static final class Pending extends E13EAndroidCheck.Router {
  final String mode;final CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);boolean unbound;
  Pending(String m){mode=m;}
  void hold(){entered.countDown();try{release.await();}catch(InterruptedException e){throw new RuntimeException(e);}}
  public boolean bind(Intent i,ServiceConnection c){
   if(android.os.Process.myUid()==10228)return super.bind(i,c);
   if(mode.equals("BIND_PENDING")&&!i.component.pkg.equals("com.videokit.e13.sender"))hold();
   if(mode.equals("HELLO_PENDING")&&!i.component.pkg.equals("com.videokit.e13.sender")){binds++;IBinder hello=new Binder(){protected boolean onTransact(int code,Parcel in,Parcel out,int f){hold();Bundle b=new Bundle();b.putInt("uid",10221);out.writeNoException();out.writeBundle(b);return true;}};new Thread(()->c.onServiceConnected(i.component,hello),"platform-main-codec").start();return true;}
   if(mode.equals("FIXTURE_PENDING")&&i.component.pkg.equals("com.videokit.e13.sender")){binds++;IBinder proxy=(code,in,out,flags)->{hold();return sender.transact(code,in,out,flags);};new Thread(()->c.onServiceConnected(i.component,proxy),"platform-main-fixture").start();return true;}
   return super.bind(i,c);
  }
  public void unbind(ServiceConnection c){if(mode.equals("UNBIND_PENDING")&&!unbound&&android.os.Process.myUid()==10221){unbound=true;hold();}super.unbind(c);}
 }
 public static void main(String[] a)throws Exception{
  String mode=a[0];if(mode.equals("LATE_SNAPSHOT")){Late p=new Late();Context.router=p;Bundle b=E13PermissionProbe.run(new Context(),"a".repeat(64));need(b.getBoolean("resourcesReturned")&&p.snapshots==2&&p.binds==3&&p.unbinds==3,"two original snapshots, no second bind/unbind");need(E13PermissionProbe.canFinish(),"original resources now returned");System.out.println("PASS LATE_SNAPSHOT first=false second=true sameOwner=true query2 bind3 unbind3 platformOnly=true");return;}
  if(mode.equals("STAGE_BOUND")){E13Stages.identity(10221,123);E13Stages.begin("a".repeat(64),"ordinarySenderCannotBindCodec");for(int i=0;i<200;i++)E13Stages.at("original","EVENT","x".repeat(1000));String value=E13Stages.snapshot();need(value.length()<=24576&&value.contains("dropped=152")&&value.contains("uid=10221 pid=123"),"exact bounded metadata");System.out.println("PASS STAGE_BOUND events48 line500 total24576 dropped152");return;}
  Pending p=new Pending(mode);Context.router=p;E13Instrumentation r=E13EAndroidCheck.runner();AtomicReference<Throwable> failure=new AtomicReference<>();Thread original=new Thread(()->{try{E13PermissionProbe.run(new Context(),"a".repeat(64));}catch(Throwable t){failure.set(t);}},"original-test-thread");original.start();need(p.entered.await(2,TimeUnit.SECONDS),"actual original call entered");Thread.sleep(mode.equals("HELLO_PENDING")?31000:5200);need(original.isAlive()&&!E13PermissionProbe.canFinish()&&AndroidJUnitRunner.finishes==0,"no timeout-as-close");p.release.countDown();original.join(5000);need(!original.isAlive()&&failure.get()==null,"same call naturally returned "+failure.get());Bundle value=new Bundle();value.putString("stream","ORIGINAL_RESULT");r.finish(-1,value);until(()->AndroidJUnitRunner.finishes==1);need(AndroidJUnitRunner.saved.getString("stream").contains("FAILURES!!!")==mode.equals("HELLO_PENDING"),"over30s cannot turn pass");System.out.println("PASS "+mode+" actualAdapter=true originalReturn=true timeoutNeverClose=true over30s="+mode.equals("HELLO_PENDING"));
 }
}
