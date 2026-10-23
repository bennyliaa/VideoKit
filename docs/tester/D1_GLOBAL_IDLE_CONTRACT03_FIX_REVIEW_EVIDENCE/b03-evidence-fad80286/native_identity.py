"""Future original-HANDLE receipts. Functions are inert until explicitly called.
No OpenProcess/PID lookup, TerminateProcess, remote handle duplication or attach.
"""
import ctypes,os,sys
from ctypes import wintypes as W
def api():
 if os.name!='nt':raise RuntimeError('WINDOWS_ONLY')
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 k.GetCurrentProcess.restype=W.HANDLE;k.GetProcessId.argtypes=[W.HANDLE];k.GetProcessId.restype=W.DWORD
 k.GetProcessTimes.argtypes=[W.HANDLE]+[ctypes.POINTER(W.FILETIME)]*4;k.GetProcessTimes.restype=W.BOOL
 k.QueryFullProcessImageNameW.argtypes=[W.HANDLE,W.DWORD,W.LPWSTR,ctypes.POINTER(W.DWORD)];k.QueryFullProcessImageNameW.restype=W.BOOL
 k.GetCommandLineW.restype=W.LPWSTR
 return k
def from_original_handle(handle,argv):
 k=api();h=W.HANDLE(int(handle));times=[W.FILETIME() for _ in range(4)]
 if not k.GetProcessTimes(h,*[ctypes.byref(x) for x in times]):raise ctypes.WinError(ctypes.get_last_error())
 buf=ctypes.create_unicode_buffer(32768);n=W.DWORD(len(buf))
 if not k.QueryFullProcessImageNameW(h,0,buf,ctypes.byref(n)):raise ctypes.WinError(ctypes.get_last_error())
 pid=k.GetProcessId(h)
 if not pid:raise ctypes.WinError(ctypes.get_last_error())
 return {'pid':int(pid),'creationFileTime':(times[0].dwHighDateTime<<32)|times[0].dwLowDateTime,'image':buf.value,'argv':list(argv),'originalHandleValueForOwnerOnly':int(handle),'handleOrigin':'ORIGINAL_POPEN_OR_SELF_PSEUDOHANDLE','argvProvenance':'CREATOR_ARGV_PENDING_CHILD_SELF_CONFIRMATION'}
def own_identity():
 k=api();raw=k.GetCommandLineW();shell=ctypes.WinDLL('shell32',use_last_error=True)
 shell.CommandLineToArgvW.argtypes=[W.LPCWSTR,ctypes.POINTER(ctypes.c_int)];shell.CommandLineToArgvW.restype=ctypes.POINTER(W.LPWSTR)
 k.LocalFree.argtypes=[W.HLOCAL];k.LocalFree.restype=W.HLOCAL
 n=ctypes.c_int();ptr=shell.CommandLineToArgvW(raw,ctypes.byref(n))
 if not ptr:raise ctypes.WinError(ctypes.get_last_error())
 # New parser allocation only, never a process HANDLE.
 try:argv=[ptr[i] for i in range(n.value)]
 finally:
  if k.LocalFree(ctypes.cast(ptr,W.HLOCAL)):raise ctypes.WinError(ctypes.get_last_error())
 row=from_original_handle(k.GetCurrentProcess(),argv);row.update(rawCommandLine=raw,argvProvenance='ACTUAL_OWN_GETCOMMANDLINEW',selfPid=os.getpid(),pythonVersion=list(sys.version_info[:3]))
 if row['pid']!=os.getpid():raise RuntimeError('SELF_IDENTITY_MISMATCH')
 return row
