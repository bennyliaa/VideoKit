package com.videokit.spike.e4;
import java.io.*;
public final class E5BFileId {
    public static final int REGULAR=1,LINK=2,DIRECTORY=3,OTHER=4;
    public final long device,inode,size;public final int uid,kind;
    public E5BFileId(long dev,long ino,long bytes,int user,int type){device=dev;inode=ino;size=bytes;uid=user;kind=type;}
    public boolean same(E5BFileId other){return other!=null && device==other.device && inode==other.inode && uid==other.uid;}
    public void role(long length,int expectedUid)throws IOException{if(kind!=REGULAR || size!=length || uid!=expectedUid)throw new IOException("E5B_EXISTING_GUARD_ROLE_LENGTH_UID");}
    public String toString(){return Long.toUnsignedString(device)+":"+Long.toUnsignedString(inode)+":"+uid;}
    public static byte[] pair(String task,E5BFileId owner,E5BFileId lease)throws IOException{ByteArrayOutputStream b=new ByteArrayOutputStream();DataOutputStream d=new DataOutputStream(b);d.writeInt(0x45354231);d.writeUTF(task);for(E5BFileId id:new E5BFileId[]{owner,lease}){d.writeLong(id.device);d.writeLong(id.inode);d.writeInt(id.uid);}d.flush();return b.toByteArray();}
    public static E5BFileId[] pair(String task,byte[] bytes)throws IOException{DataInputStream d=new DataInputStream(new ByteArrayInputStream(bytes));if(d.readInt()!=0x45354231 || !d.readUTF().equals(task))throw new IOException("E5B_GUARD_IDENTITY_RECORD");E5BFileId[] ids=new E5BFileId[2];for(int n=0;n<2;n++)ids[n]=new E5BFileId(d.readLong(),d.readLong(),n==0?0:36,d.readInt(),REGULAR);if(d.read()!=-1)throw new IOException("E5B_GUARD_IDENTITY_RECORD");return ids;}
}
