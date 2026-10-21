package android.os;public interface IBinder {int FLAG_ONEWAY=1;boolean transact(int c,Parcel i,Parcel o,int f)throws RemoteException;}
