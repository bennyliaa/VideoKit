package com.videokit.spike.e4;

import android.content.Context;
import android.os.Bundle;
import android.os.Looper;
import android.os.Process;
import android.system.Os;
import android.system.OsConstants;
import android.system.StructStat;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import java.io.FileDescriptor;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;

/** Compiled future read-only metadata diagnosis. Does not observe, settle, admit, or open media. */
@RunWith(AndroidJUnit4.class)
public final class E7WriterDeathDiagnosticTests {
    private static Job original; // Retain the original owner on any in-flight/unknown open or close.
    private static final String OWNER="E5A_N2_RECOVERY_OWNER_V1 8c6673b7-38a5-4a24-838d-ca8466d8b75f 4869 10221 com.videokit.app 1792224193301\n";
    private static final class Job implements Runnable {
        final CountDownLatch done=new CountDownLatch(1);
        final Context context;final E4Owned<FileDescriptor> fd=new E4Owned<>("originalRecoveryOwnerReadOnly",Os::close);
        volatile String result="PENDING_ORIGINAL_OWNER";volatile Throwable failure;
        Job(Context c){context=c;}
        public void run(){
            try{
                Path base=context.getFilesDir().toPath();Path path=base.resolve("e4a_output_budget/N2-e5-recovery/recovery.owner");
                for(Path p:new Path[]{base,base.resolve("e4a_output_budget"),path.getParent()}){
                    StructStat st=Os.lstat(p.toString());if(!OsConstants.S_ISDIR(st.st_mode)||st.st_uid!=10221)throw new IOException("E7_OWNER_DIRECTORY_ROLE");
                }
                StructStat before=Os.lstat(path.toString());role(before);
                fd.allocate(()->Os.open(path.toString(),OsConstants.O_RDONLY|OsConstants.O_NOFOLLOW|OsConstants.O_NONBLOCK,0));
                try{
                    StructStat opened=Os.fstat(fd.original());role(opened);same(before,opened);
                    byte[] bytes=new byte[257];int total=0;
                    while(total<bytes.length){int n=Os.read(fd.original(),bytes,total,bytes.length-total);if(n==0)break;total+=n;}
                    if(total>256||!OWNER.equals(new String(bytes,0,total,StandardCharsets.US_ASCII)))throw new IOException("E7_FIXED_OWNER_BYTES_MISMATCH");
                    same(opened,Os.fstat(fd.original()));
                }finally{fd.close();}
                same(before,Os.lstat(path.toString()));
                E5N2RecoveryAndroid platform=new E5N2RecoveryAndroid(context);
                String gate="RETURNED_CURRENT_GATE";
                try{platform.requireRecoveryWriterDead(E5AOwner.parse(OWNER.getBytes(StandardCharsets.US_ASCII)));}
                catch(IOException expected){gate="BLOCKED_CURRENT_GATE";}
                result=gate+" "+platform.evidence()+" ownerFdReturned="+fd.returned()+" observation=NOT_CALLED admission=NONE mediaReads=0 persistentWrites=0";
            }catch(Throwable t){failure=t;result="DIAGNOSTIC_FAILED type="+t.getClass().getSimpleName()+" ownerState="+fd.state()+" admission=NONE";}
            finally{done.countDown();}
        }
        private void role(StructStat s)throws IOException{if(!OsConstants.S_ISREG(s.st_mode)||s.st_uid!=10221||s.st_size<1||s.st_size>256)throw new IOException("E7_OWNER_FILE_ROLE");}
        private void same(StructStat a,StructStat b)throws IOException{role(b);if(a.st_dev!=b.st_dev||a.st_ino!=b.st_ino||a.st_size!=b.st_size||a.st_mtime!=b.st_mtime||a.st_ctime!=b.st_ctime)throw new IOException("E7_OWNER_FILE_CHANGED");}
    }
    @Test public void originalRecoveryWriterReadOnly()throws Exception {
        Bundle args=InstrumentationRegistry.getArguments();
        assertEquals("originalRecoveryWriterReadOnly",args.getString("e7Case"));
        assertEquals("D1-E7-WRITER-DIAG-TABLET-20261017",args.getString("e7Batch"));
        assertEquals("READ_ONLY_NO_ADMISSION",args.getString("e7Scope"));
        assertNotEquals(Looper.getMainLooper(),Looper.myLooper());assertEquals(10221,Process.myUid());
        assertEquals(0,E4Session.retainedSessions());assertEquals(0,E4Session.reservedEncoderSlots());
        synchronized(E7WriterDeathDiagnosticTests.class){assertNull("Single original diagnostic only; no retry",original);original=new Job(InstrumentationRegistry.getInstrumentation().getTargetContext());}
        new Thread(original,"E7-original-read-only-owner").start();
        boolean completed=original.done.await(10,TimeUnit.SECONDS);
        String value=completed?original.result:"PENDING_ORIGINAL_OWNER noCancel=true noRetry=true admission=NONE";
        assertTrue(value.length()<=4096);Bundle status=new Bundle();status.putString("stream","E7_READ_ONLY "+value+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(0,status);
        assertTrue("Original owner still in flight; retain and stop batch",completed);
        if(original.failure!=null)throw new AssertionError("Read-only diagnostic failed",original.failure);
        assertTrue(original.fd.returned());assertEquals(0,E4Session.retainedSessions());assertEquals(0,E4Session.reservedEncoderSlots());
    }
}
