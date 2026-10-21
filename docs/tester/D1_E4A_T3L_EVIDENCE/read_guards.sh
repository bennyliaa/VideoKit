set -uf
step() { _step_name=$1; shift; "$@"; RC=$?; printf 'T3L_STEP|%s|rc=%s\n' "$_step_name" "$RC"; }
u=$(id -u 2>&1); urc=$?; p=$(pwd 2>&1); prc=$?
printf 'T3L_CONTEXT|id_rc=%s|uid=%s|pwd_rc=%s|pwd=%s\n' "$urc" "$u" "$prc" "$p"
if [ "$urc" -ne 0 ] || [ "$prc" -ne 0 ] || [ "$u" != 10221 ] || [ "$p" != /data/user/0/com.videokit.app ]; then printf 'T3L_CONTEXT_REJECT\n'; exit 0; fi
step uid_guard test "$u" = 10221
step pwd_guard test "$p" = /data/user/0/com.videokit.app
d=files/e4_diag_T3P_TABLET_20261017_once
t=files/e4_diag_T3P_TABLET_20261017_once/payload256.bin
step files_d test -d files; files_d=$RC
step files_L test -L files; files_L=$RC
step directory_d test -d "$d"; directory_d=$RC
step directory_L test -L "$d"; directory_L=$RC
step target_e test -e "$t"; target_e=$RC
step target_L test -L "$t"; target_L=$RC
step target_f test -f "$t"; target_f=$RC
step current_original_noclobber_absence_guard test ! -e "$t"
opts=$(
 (
  set -C
  r=$?; printf 'T3L_SET_C|rc=%s|flags=%s\n' "$r" "$-"
  set -o
  r=$?; printf 'T3L_QUERY_OPTIONS|rc=%s\n' "$r"
 ) 2>&1
); orc=$?
printf 'T3L_OPTION_SCOPE_BEGIN|rc=%s\n%s\nT3L_OPTION_SCOPE_END\n' "$orc" "$opts"
before=$(/system/bin/toybox stat -c '%d|%i|%u|%f|%s|%Y' -- "$t" 2>&1); brc=$?
printf 'T3L_PRE_STAT|rc=%s|%s\n' "$brc" "$before"
size=UNPROVEN; owner=UNPROVEN
if [ "$brc" -eq 0 ]; then
 saved_ifs=$IFS; IFS='|'; set -- $before; IFS=$saved_ifs
 if [ "$#" -eq 6 ]; then size=$5; owner=$3; fi
fi
case "$size" in ''|*[!0-9]*) printf 'T3L_HASH_SKIPPED|UNPROVEN_SIZE\n'; exit 0;; esac
step current_count_256_guard test "$size" = 256
if [ "$files_d" -ne 0 ] || [ "$files_L" -ne 1 ] || [ "$directory_d" -ne 0 ] || [ "$directory_L" -ne 1 ] || [ "$target_e" -ne 0 ] || [ "$target_L" -ne 1 ] || [ "$target_f" -ne 0 ] || [ "$owner" != 10221 ]; then printf 'T3L_HASH_SKIPPED|ROLE_OR_OWNER\n'; exit 0; fi
if [ "$size" -gt 256 ]; then printf 'T3L_HASH_SKIPPED|OVER_256|size=%s\n' "$size"; exit 0; fi
printf 'T3L_HASH_STARTED|size=%s\n' "$size"
digest=$(/system/bin/toybox sha256sum -- "$t" 2>&1); hrc=$?
printf 'T3L_HASH_RESULT|rc=%s|%s\n' "$hrc" "$digest"
after=$(/system/bin/toybox stat -c '%d|%i|%u|%f|%s|%Y' -- "$t" 2>&1); arc=$?
printf 'T3L_POST_STAT|rc=%s|%s\n' "$arc" "$after"
if [ "$arc" -eq 0 ] && [ "$before" = "$after" ]; then printf 'T3L_WINDOW_METADATA_UNCHANGED\n'; else printf 'T3L_WINDOW_CHANGED_NO_HASH_INFERENCE\n'; fi
printf 'T3L_READONLY_COMPLETE\n'
