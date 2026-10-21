set -uf
u=$(id -u 2>&1); urc=$?; p=$(pwd 2>&1); prc=$?
printf 'T3L_PROC_CONTEXT|id_rc=%s|uid=%s|pwd_rc=%s|pwd=%s\n' "$urc" "$u" "$prc" "$p"
if [ "$urc" -ne 0 ] || [ "$prc" -ne 0 ] || [ "$u" != 10221 ] || [ "$p" != /data/user/0/com.videokit.app ]; then printf 'T3L_PROC_CONTEXT_REJECT\n'; exit 0; fi
s=$(cat /proc/16643/stat 2>&1); r=$?; printf 'T3L_PROC_STAT|pid=16643|rc=%s|%s\n' "$r" "$s"
if [ "$r" -ne 0 ]; then printf 'T3L_PROC_REST_SKIPPED_STAT_UNAVAILABLE\n'; exit 0; fi
status=$(cat /proc/16643/status 2>&1); r=$?; printf 'T3L_PROC_STATUS_BEGIN|rc=%s\n%s\nT3L_PROC_STATUS_END\n' "$r" "$status"
if [ "$r" -ne 0 ]; then printf 'T3L_PROC_REST_SKIPPED_STATUS_UNAVAILABLE\n'; exit 0; fi
good_uid=0
while IFS= read -r line || [ -n "$line" ]; do
 case "$line" in
  Uid:*) set -- $line; if [ "$#" -eq 5 ] && [ "$2" = 10221 ] && [ "$3" = 10221 ] && [ "$4" = 10221 ] && [ "$5" = 10221 ]; then good_uid=1; fi;;
 esac
done <<T3L_STATUS_METADATA
$status
T3L_STATUS_METADATA
if [ "$good_uid" -ne 1 ]; then printf 'T3L_PROC_REST_SKIPPED_UID_UNPROVEN\n'; exit 0; fi
h=$(/system/bin/toybox od -An -v -tx1 /proc/16643/cmdline 2>&1); r=$?; printf 'T3L_PROC_CMDHEX|rc=%s|%s\n' "$r" "$h"
v=$(/system/bin/toybox readlink /proc/16643/cwd 2>&1); r=$?; printf 'T3L_PROC_CWD|rc=%s|%s\n' "$r" "$v"
v=$(/system/bin/toybox readlink /proc/16643/exe 2>&1); r=$?; printf 'T3L_PROC_EXE|rc=%s|%s\n' "$r" "$v"
for fd in 0 1 2 3; do
 v=$(/system/bin/toybox readlink /proc/16643/fd/$fd 2>&1); r=$?; printf 'T3L_PROC_FD_LINK|fd=%s|rc=%s|%s\n' "$fd" "$r" "$v"
done
printf 'T3L_PROC_READONLY_COMPLETE\n'
