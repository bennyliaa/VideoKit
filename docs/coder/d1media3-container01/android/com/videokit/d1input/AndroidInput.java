package com.videokit.d1input;
import android.os.Looper;import com.videokit.spike.c14.AsyncReadBridge;import java.io.IOException;
/** Actual platform thread binding; no fake Media3 API and no path/URL/network source constructor. */
public final class AndroidInput {
 public static final WorkerRule WORKER=()->{if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("WORKER_REQUIRED");};
 public static HostInputFactory factory(String opaqueVersion,AsyncReadBridge.Provider capability)throws IOException{return new HostInputFactory(android.os.Process.myUid(),android.os.Process.myPid(),opaqueVersion,capability,WORKER);}
 private AndroidInput(){}
}
