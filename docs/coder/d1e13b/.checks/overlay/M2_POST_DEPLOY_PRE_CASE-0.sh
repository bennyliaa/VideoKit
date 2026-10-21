set -eu
export LC_ALL=C
emit() {
 label="$1"; max="$2"; shift 2
 if value=$("$@" 2>&1); then :; else printf 'RECORD_ERROR\t%s\n' "$label" >&2; exit 21; fi
 size=$(printf '%s' "$value" | wc -c)
 if [ "$size" -gt "$max" ]; then printf 'RECORD_OVERSIZE\t%s\n' "$label" >&2; exit 22; fi
 printf 'BEGIN\t%s\n%s\nEND\t%s\n' "$label" "$value" "$label"
}

printf 'E13A_METADATA\tM2_POST_DEPLOY_PRE_CASE\tD1-20261018-E13A\n'
emit SERIAL 64 getprop ro.serialno
emit MODEL 128 getprop ro.product.model
emit API 16 getprop ro.build.version.sdk
emit ABI 128 getprop ro.product.cpu.abilist
emit CURRENT_USER 16 am get-current-user
emit USER0_STATE 512 sh -c 'dumpsys user | {
 e_want=0
 while IFS= read -r e_row; do
  case "$e_row" in *UserInfo*)case "$e_row" in *'"'"'UserInfo{0:'"'"'*)e_want=1;;*)e_want=0;;esac;;esac
  if [ "$e_want" -eq 1 ]; then case "$e_row" in *UserInfo*|*State:*)printf '"'"'%s\n'"'"' "$e_row";;esac;fi
 done
}'
emit RELATED_PS 4096 sh -c 'ps -A -o PID,PPID,UID,NAME | {
 IFS= read -r e_row || exit 1
 printf '"'"'%s\n'"'"' "$e_row"
 while IFS= read -r e_row; do
  case "$e_row" in *com.videokit.app*|*com.videokit.e13.sender*)printf '"'"'%s\n'"'"' "$e_row";;esac
 done
}'
# This parser uses shell builtins only. Input is one whole processes dump + original exit status.
e13b_fail() { if [ -z "$e_bad" ]; then e_bad=$1; fi; }
e13b_fields_done() {
 if [ "$e_entries" -gt 0 ] && { [ "$e_class" -eq 0 ] || [ "$e_finished" -eq 0 ] || [ "$e_running" -eq 0 ] || [ "$e_targets" -eq 0 ] || [ "$e_info" -eq 0 ] || [ "$e_args" -eq 0 ]; }; then e13b_fail INCOMPLETE_ACTIVE_ENTRY; fi
}
e13b_parse_processes() {
 LC_ALL=C; export LC_ALL
 e_bytes=0; e_lines=0; e_h=0; e_known=0; e_oom=0; e_tail=0; e_status=0; e_active=0; e_capture=0; e_entries=0; e_hint=0
 e_bad=; e_block=; e_class=0; e_finished=0; e_running=0; e_targets=0; e_info=0; e_args=0
 e_nl='
'
 while IFS= read -r e_line || [ -n "$e_line" ]; do
  e_lines=$((e_lines+1)); e_bytes=$((e_bytes+${#e_line}+1))
  if [ "$e_bytes" -gt 524288 ] || [ "$e_lines" -gt 8192 ] || [ "${#e_line}" -gt 4096 ]; then e13b_fail RAW_LIMIT; fi
  case "$e_line" in
   E13B_DUMPSYS_EXIT=*)
    e_status=$((e_status+1)); e_code=${e_line#E13B_DUMPSYS_EXIT=}
    if [ "$e_tail" -ne 1 ] || [ "$e_code" != 0 ]; then e13b_fail COMMAND_EXIT_OR_MISSING_TAIL; fi
    continue;;
  esac
  if [ "$e_status" -gt 0 ] && [ -n "$e_line" ]; then e13b_fail AFTER_COMMAND_STATUS; fi
  case "$e_line" in
   Error:*|Unknown\ command*|Bad\ activity\ command*|*Permission\ Denial*|Permission\ denied*|"Can't find service"*|Exception*|java.*|*DUMP\ TIMEOUT*|*DUMP\ FAILED*|*truncated*|*Truncated*) e13b_fail DIAGNOSTIC;;
  esac
  if [ "$e_lines" -eq 1 ] && [ "$e_line" != 'ACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)' ]; then e13b_fail HEADER; fi
  if [ "$e_line" = 'ACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)' ]; then e_h=$((e_h+1)); if [ "$e_lines" -ne 1 ]; then e13b_fail DUPLICATE_HEADER; fi; fi
  if [ "$e_tail" -gt 0 ] && [ -n "$e_line" ]; then e13b_fail AFTER_FINAL_TAIL; fi
  if [ "$e_line" = '  All known processes:' ]; then
   e_known=$((e_known+1)); if [ "$e_oom" -gt 0 ] || [ "$e_active" -gt 0 ]; then e13b_fail PHASE_ORDER; fi
  fi
  if [ "$e_line" = '  Active instrumentation:' ]; then
   e_active=$((e_active+1)); e_capture=1
   if [ "$e_known" -ne 1 ] || [ "$e_oom" -gt 0 ] || [ "$e_active" -ne 1 ]; then e13b_fail ACTIVE_HEADER_OR_ORDER; fi
  fi
  if [ "$e_line" = '  OOM levels:' ]; then
   if [ "$e_capture" -eq 1 ]; then e13b_fields_done; e_capture=0; fi
   e_oom=$((e_oom+1)); if [ "$e_known" -ne 1 ] || [ "$e_oom" -ne 1 ]; then e13b_fail OOM_ORDER; fi
  fi
  case "$e_line" in
   '  mForceBackgroundCheck=true'|'  mForceBackgroundCheck=false')
    e_tail=$((e_tail+1)); e_tailtext=$e_line
    if [ "$e_oom" -ne 1 ] || [ "$e_capture" -ne 0 ] || [ "$e_tail" -ne 1 ]; then e13b_fail TAIL_ORDER; fi;;
  esac
  case "$e_line" in *'ActiveInstrumentation{'*)e_hint=1;; esac
  if [ "$e_capture" -eq 1 ]; then
   if [ $((${#e_block}+${#e_line}+1)) -gt 3000 ]; then e13b_fail ACTIVE_BLOCK_LIMIT; fi
   if [ -z "$e_bad" ]; then e_block=$e_block$e_line$e_nl; fi
   case "$e_line" in
    '    Instrumentation #'*': ActiveInstrumentation{'*'}')
     e13b_fields_done; e_index=${e_line#'    Instrumentation #'}; e_index=${e_index%%:*}
     case "$e_index" in ''|*[!0-9]*)e13b_fail ENTRY_FORMAT;; *)if [ "$e_index" -ne "$e_entries" ]; then e13b_fail ENTRY_INDEX; fi;; esac
     e_entries=$((e_entries+1)); e_class=0; e_finished=0; e_running=0; e_targets=0; e_info=0; e_args=0;;
    '    Instrumentation #'*)e13b_fail ENTRY_FORMAT;;
   esac
   case "$e_line" in '      mClass=ComponentInfo{'*)e_class=1;; esac
   case "$e_line" in *mFinished=true*|*mFinished=false*)e_finished=1;; esac
   case "$e_line" in '      mRunningProcesses:')e_running=1;; esac
   case "$e_line" in '      mTargetProcesses='*)e_targets=1;; esac
   case "$e_line" in '      mTargetInfo='*)e_info=1;; esac
   case "$e_line" in '      mArguments='*)e_args=1;; esac
  else
   case "$e_line" in '    Instrumentation #'*)e13b_fail ACTIVE_OUTSIDE_BLOCK;; esac
   case "$e_line" in '  Active instrumentation'*)e13b_fail ACTIVE_OUTSIDE_BLOCK;; esac
  fi
 done
 if [ "$e_h" -ne 1 ] || [ "$e_known" -ne 1 ] || [ "$e_oom" -ne 1 ] || [ "$e_tail" -ne 1 ] || [ "$e_status" -ne 1 ] || [ "$e_capture" -ne 0 ]; then e13b_fail INCOMPLETE_DUMP; fi
 if [ "$e_active" -gt 0 ] && [ "$e_entries" -eq 0 ]; then e13b_fail EMPTY_ACTIVE_HEADER; fi
 if [ "$e_active" -eq 0 ] && { [ "$e_entries" -gt 0 ] || [ "$e_hint" -gt 0 ]; }; then e13b_fail ACTIVE_INCONSISTENCY; fi
 if [ -n "$e_bad" ]; then printf 'E13B_PROCESS_BLOCKED reason=%s\n' "$e_bad"; return 42; fi
 e_state=IDLE; if [ "$e_entries" -gt 0 ]; then e_state=ACTIVE; fi
 printf 'E13B_PROCESS_SNAPSHOT_V1 state=%s\n' "$e_state"
 printf '%s\n' 'SOURCE_HEADER ACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)' 'SOURCE_ANCHORS all_known=1 oom_levels=1 final_tail=1 command_exit=0'
 printf 'SOURCE_SCAN bytes=%s lines=%s active_entries=%s\n' "$e_bytes" "$e_lines" "$e_entries"
 printf 'SOURCE_TAIL%s\n' "$e_tailtext"
 printf 'ACTIVE_BLOCK_BEGIN\n%sACTIVE_BLOCK_END\nE13B_PROCESS_SNAPSHOT_END\n' "$e_block"
}

e13b_collect_state() {
 if value=$({
  if dumpsys activity processes 2>&1; then e_dump_code=0; else e_dump_code=$?; fi
  printf '\nE13B_DUMPSYS_EXIT=%s\n' "$e_dump_code"
 } | e13b_parse_processes); then e_collect_code=0; else e_collect_code=$?; fi
 size=$(printf '%s' "$value" | wc -c)
 if [ "$size" -gt 4096 ]; then printf 'RECORD_OVERSIZE\tINSTRUMENTATION\n' >&2; exit 22; fi
 printf 'BEGIN\tINSTRUMENTATION\n%s\nEND\tINSTRUMENTATION\n' "$value"
 if [ "$e_collect_code" -ne 0 ]; then printf 'E13B_METADATA_BLOCKED\n' >&2; exit 21; fi
 case "$value" in
  'E13B_PROCESS_SNAPSHOT_V1 state=IDLE'*) :;;
  'E13B_PROCESS_SNAPSHOT_V1 state=ACTIVE'*) printf 'E13B_ENVIRONMENT_WAIT_NO_DEPLOY_NO_TEST\n' >&2; exit 73;;
  *) printf 'E13B_METADATA_BLOCKED_UNKNOWN_FRAME\n' >&2; exit 21;;
 esac
}

e13b_collect_state
emit APP_SERVICES 4096 dumpsys activity services com.videokit.app
emit FIXTURE_SERVICES 4096 dumpsys activity services com.videokit.e13.sender
emit APK_APP 1024 sh -c 'p=$(pm path com.videokit.app); case "$p" in package:/data/app/*/base.apk) ;; *) exit 23;; esac; p=${p#package:}; case "$p" in *'"'"'
'"'"'*) exit 24;; esac; printf '"'"'%s\n'"'"' "$p"; sha256sum "$p"'
emit PKG_APP 2048 sh -c 'dumpsys package com.videokit.app | sed -n '"'"'/^[ ]*userId=/p; /^[ ]*versionCode=/p; /^[ ]*User 0:/p'"'"' '
emit APK_TEST 1024 sh -c 'p=$(pm path com.videokit.app.test); case "$p" in package:/data/app/*/base.apk) ;; *) exit 23;; esac; p=${p#package:}; case "$p" in *'"'"'
'"'"'*) exit 24;; esac; printf '"'"'%s\n'"'"' "$p"; sha256sum "$p"'
emit PKG_TEST 2048 sh -c 'dumpsys package com.videokit.app.test | sed -n '"'"'/^[ ]*userId=/p; /^[ ]*versionCode=/p; /^[ ]*User 0:/p'"'"' '
emit APK_FIXTURE 1024 sh -c 'p=$(pm path com.videokit.e13.sender); case "$p" in package:/data/app/*/base.apk) ;; *) exit 23;; esac; p=${p#package:}; case "$p" in *'"'"'
'"'"'*) exit 24;; esac; printf '"'"'%s\n'"'"' "$p"; sha256sum "$p"'
emit PKG_FIXTURE 2048 sh -c 'dumpsys package com.videokit.e13.sender | sed -n '"'"'/^[ ]*userId=/p; /^[ ]*versionCode=/p; /^[ ]*User 0:/p'"'"' '
emit DATA_APP 128 run-as com.videokit.app stat -c '%u|%i' .
emit DATA_TEST 128 run-as com.videokit.app.test stat -c '%u|%i' .
printf 'E13A_METADATA_END\tM2_POST_DEPLOY_PRE_CASE\n'
