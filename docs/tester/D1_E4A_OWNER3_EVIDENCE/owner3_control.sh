set -efu
owner_stat_fields() {
 case "$1" in '7722 ('*) ;; *) return 1;; esac
 _owner_rest=${1##*) }
 [ "$_owner_rest" != "$1" ] || return 1
 set -- $_owner_rest
 [ "$#" -ge 20 ] || return 1
 OWNER_STATE=$1; OWNER_PPID=$2; shift 19; OWNER_TICKS=$1
 case "$OWNER_PPID" in ''|*[!0-9]*) return 1;; esac
 case "$OWNER_TICKS" in ''|*[!0-9]*) return 1;; esac
 case "$OWNER_STATE" in R|S|D|T|t|Z|X|I|W|P) ;; *) return 1;; esac
}
owner_stat_verify() {
 case "$1" in '7722 (tee) '*) ;; *) return 1;; esac
 owner_stat_fields "$1" || return 1
 [ "$OWNER_PPID" = 7718 ] && [ "$OWNER_TICKS" = 7571831 ]
}
owner_uid_verify() {
 OWNER_UIDS=UNOBSERVED; _owner_uid_count=0
 while IFS= read -r _owner_line || [ -n "$_owner_line" ]; do
  case "$_owner_line" in
   Uid:*)
    set -- $_owner_line
    [ "$#" -eq 5 ] || return 1
    OWNER_UIDS="$2 $3 $4 $5"
    [ "$2" = 10221 ] && [ "$3" = 10221 ] && [ "$4" = 10221 ] && [ "$5" = 10221 ] || return 1
    _owner_uid_count=$((_owner_uid_count+1))
   ;;
  esac
 done < "$1"
 [ "$_owner_uid_count" -eq 1 ]
}
owner_pair_verify() {
 [ "$1" = "$2" ] || return 1
 _owner_value=$1; _owner_saved_ifs=$IFS; IFS='|'; set -- $_owner_value; IFS=$_owner_saved_ifs
 [ "$#" -eq 3 ] || return 1
 case "$1" in ''|*[!0-9]*) return 1;; esac
 case "$2" in ''|*[!0-9]*) return 1;; esac
 [ "$3" = 10221 ]
}
owner_observe_fields() {
 if ! owner_stat_fields "$1"; then OWNER_OBSERVATION=UNKNOWN
 elif [ "$OWNER_TICKS" != 7571831 ]; then OWNER_OBSERVATION=REUSED
 elif [ "$OWNER_STATE" = Z ]; then OWNER_OBSERVATION=ZOMBIE
 else OWNER_OBSERVATION=STILL_VISIBLE
 fi
}

test "$(id -u)" = 10221; test "$(pwd)" = /data/user/0/com.videokit.app
if [ ! -d /proc/7722 ]; then printf 'OWNER3_ORIGINAL_PID_NOT_VISIBLE_NO_SIGNAL\n'; exit 0; fi
s=$(cat /proc/7722/stat); printf 'OWNER3_ORIGINAL_STAT|%s\n' "$s"; owner_stat_verify "$s"
if owner_uid_verify /proc/7722/status; then printf 'OWNER3_UIDS|%s\n' "$OWNER_UIDS"; else printf 'OWNER3_UID_REJECT|%s\n' "$OWNER_UIDS"; exit 54; fi
h=$(/system/bin/toybox od -An -v -tx1 /proc/7722/cmdline | /system/bin/toybox tr -d ' \n'); printf 'OWNER3_CMDHEX|%s\n' "$h"; test "$h" = 7465650066696c65732f65345f66697874757265732f62617369632e6d703400
c=$(/system/bin/toybox readlink /proc/7722/cwd); printf 'OWNER3_CWD|%s\n' "$c"; test "$c" = /data/user/0/com.videokit.app
x=$(/system/bin/toybox readlink /proc/7722/exe); printf 'OWNER3_EXE|%s\n' "$x"; test "$x" = /system/bin/toybox
l=$(/system/bin/toybox readlink /proc/7722/fd/3); printf 'OWNER3_FD3_LINK|%s\n' "$l"; test "$l" = /data/user/0/com.videokit.app/files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep
a=files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep; test -f "$a"; test ! -L "$a"
f=$(/system/bin/toybox stat -L -c '%d|%i|%u' -- /proc/7722/fd/3); printf 'OWNER3_FD3_TARGET_STAT|%s\n' "$f"
v=$(/system/bin/toybox stat -c '%d|%i|%u' -- "$a"); printf 'OWNER3_ARCHIVE_STAT|%s\n' "$v"; owner_pair_verify "$f" "$v"
start=$(/system/bin/toybox date +%s%N); case "$start" in ''|*[!0-9]*) exit 52;; esac; end=$((start+2000000000))
s=$(cat /proc/7722/stat); owner_stat_verify "$s"
printf 'OWNER3_RECHECK_COMPLETE|pid=7722|ticks=7571831|uid=10221|ppid=7718|fd=3\n'
printf 'OWNER3_TERM_ATTEMPT|pid=7722\n'
if /system/bin/toybox kill -TERM 7722; then printf 'OWNER3_TERM_RETURN|rc=0\n'; else r=$?; printf 'OWNER3_TERM_RETURN|rc=%s\n' "$r"; exit "$r"; fi
count=0; OWNER_OBSERVATION=UNKNOWN
while [ "$count" -lt 20 ]; do
 now=$(/system/bin/toybox date +%s%N); if [ "$now" -ge "$end" ]; then break; fi
 if [ ! -d /proc/7722 ]; then printf 'OWNER3_OBSERVATION|GONE|pid=7722|ticks=7571831\n'; exit 0; fi
 if ! s=$(cat /proc/7722/stat); then printf 'OWNER3_OBSERVATION|UNKNOWN|pid=7722\n'; exit 0; fi
 owner_observe_fields "$s"
 case "$OWNER_OBSERVATION" in
  REUSED) printf 'OWNER3_OBSERVATION|REUSED|original_ticks=7571831\n'; exit 0;;
  ZOMBIE) printf 'OWNER3_OBSERVATION|ZOMBIE|pid=7722|ticks=7571831|parent_reap=UNPROVEN\n'; exit 0;;
  UNKNOWN) printf 'OWNER3_OBSERVATION|UNKNOWN|pid=7722\n'; exit 0;;
 esac
 now=$(/system/bin/toybox date +%s%N); left=$((end-now)); if [ "$left" -lt 100000000 ]; then break; fi
 /system/bin/toybox sleep 0.1; count=$((count+1))
done
printf 'OWNER3_OBSERVATION|STILL_VISIBLE_OR_UNPROVEN|pid=7722|last=%s\n' "$OWNER_OBSERVATION"
