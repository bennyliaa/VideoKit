package com.videokit.d1input;
import android.system.ErrnoException;import android.system.OsConstants;import java.io.IOException;
/** Real Android errno classification, never parses or forwards private platform error text. */
public final class PlatformOutputErrors {
 public static IOException map(Throwable original){Throwable t=original;for(int i=0;i<8&&t!=null;i++,t=t.getCause()){if(t instanceof ErrnoException){int e=((ErrnoException)t).errno;if(e==OsConstants.ENOSPC||e==OsConstants.EDQUOT)return new IOException("OUTPUT_NO_SPACE");if(e==OsConstants.EACCES||e==OsConstants.EPERM)return new IOException("OUTPUT_PERMISSION_DENIED");if(e==OsConstants.EPIPE||e==OsConstants.EBADF||e==OsConstants.ENODEV)return new IOException("OUTPUT_DISCONNECTED");}}return Failures.io(original,"OUTPUT_IO_FAILED");}
 private PlatformOutputErrors(){}
}
