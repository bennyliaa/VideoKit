"""Pure in-process framing validation for the existing tester controller. No adb/process/IO wrapper."""
import re
def parse(raw):
    if isinstance(raw,bytes):raw=raw.decode('utf-8',errors='strict')
    if len(raw.encode())>4096:raise ValueError('RECORD_LIMIT')
    lines=raw.splitlines()
    if len(lines)<8 or lines[-1]!='E13B_PROCESS_SNAPSHOT_END':raise ValueError('INCOMPLETE_FRAME')
    match=re.fullmatch(r'E13B_PROCESS_SNAPSHOT_V1 state=(IDLE|ACTIVE)',lines[0])
    if not match:raise ValueError('BLOCKED_OR_UNKNOWN')
    if lines[1]!='SOURCE_HEADER ACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)' or lines[2]!='SOURCE_ANCHORS all_known=1 oom_levels=1 final_tail=1 command_exit=0':raise ValueError('SOURCE_ANCHORS')
    scan=re.fullmatch(r'SOURCE_SCAN bytes=([0-9]+) lines=([0-9]+) active_entries=([0-9]+)',lines[3])
    if not scan or not 0<int(scan[1])<=524288 or not 0<int(scan[2])<=8192:raise ValueError('SOURCE_BOUNDS')
    if not re.fullmatch(r'SOURCE_TAIL  mForceBackgroundCheck=(true|false)',lines[4]):raise ValueError('SOURCE_TAIL')
    if lines[5]!='ACTIVE_BLOCK_BEGIN' or lines[-2]!='ACTIVE_BLOCK_END' or lines.count('ACTIVE_BLOCK_BEGIN')!=1 or lines.count('ACTIVE_BLOCK_END')!=1:raise ValueError('ACTIVE_FRAME')
    body='\n'.join(lines[6:-2]);entries=int(scan[3]);state=match[1]
    roots=re.findall(r'^    Instrumentation #[0-9]+: ActiveInstrumentation\{[^}]+\}$',body,re.M)
    if state=='IDLE' and (entries or body):raise ValueError('FALSE_IDLE')
    if state=='ACTIVE' and (entries<1 or len(roots)!=entries or not body.startswith('  Active instrumentation:\n')):raise ValueError('INCOMPLETE_ACTIVE')
    return {'state':state,'decision':'ENVIRONMENT_WAIT' if state=='ACTIVE' else 'INSTRUMENTATION_IDLE_ONLY','activeEntries':entries,'completeActiveBlock':body+'\n' if state=='ACTIVE' else '', 'rawDumpBytesConsumed':int(scan[1]),'deviceIdleOrResourcesReleasedProven':False}
