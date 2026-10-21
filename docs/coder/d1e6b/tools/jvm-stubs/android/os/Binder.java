package android.os;
/** Test-only creation tripwire; never emulates Binder execution or ships in the APK. */
public class Binder implements IBinder {
    public static int creations;
    public static final IllegalStateException CREATION_SENTINEL=new IllegalStateException("E6B_CREATION_PROBE");
    public Binder(){creations++;throw CREATION_SENTINEL;}
    public static int getCallingPid(){throw new AssertionError("no Binder calls");}
    public static int getCallingUid(){throw new AssertionError("no Binder calls");}
    protected boolean onTransact(int code,Parcel data,Parcel reply,int flags)throws RemoteException{throw new AssertionError();}
    public void dump(java.io.FileDescriptor fd,String[] args){throw new AssertionError();}
    public void dumpAsync(java.io.FileDescriptor fd,String[] args){throw new AssertionError();}
    public String getInterfaceDescriptor(){throw new AssertionError();}
    public boolean isBinderAlive(){throw new AssertionError();}
    public void linkToDeath(DeathRecipient r,int flags){throw new AssertionError();}
    public boolean pingBinder(){throw new AssertionError();}
    public IInterface queryLocalInterface(String d){throw new AssertionError();}
    public boolean transact(int code,Parcel data,Parcel reply,int flags){throw new AssertionError();}
    public boolean unlinkToDeath(DeathRecipient r,int flags){throw new AssertionError();}
}
