package android.content;
public class Context {
 public static final int BIND_AUTO_CREATE=1;
 public Context getApplicationContext(){return this;}
 public String getPackageName(){return "com.videokit.unit_fixture";}
 public boolean bindIsolatedService(Intent i,int f,String n,java.util.concurrent.Executor e,ServiceConnection c){throw new AssertionError("Android binding must not execute in JVM checks");}
 public void unbindService(ServiceConnection c){throw new AssertionError("Android binding must not execute in JVM checks");}
}
