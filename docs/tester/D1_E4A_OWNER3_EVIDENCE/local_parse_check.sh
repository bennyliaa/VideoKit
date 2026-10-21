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

if owner_stat_verify '7722 (tee) S 7718 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7571831 0 0 0'; then actual=yes; else actual=no; fi; test "$actual" = yes; printf "LOCAL_ASSERT|good-stat|PASS\n"
if owner_stat_verify '9999 (tee) S 7718 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7571831 0 0 0'; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|wrong-pid|PASS\n"
if owner_stat_verify '7722 (other) S 7718 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7571831 0 0 0'; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|wrong-comm|PASS\n"
if owner_stat_verify '7722 (tee) S 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7571831 0 0 0'; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|wrong-parent|PASS\n"
if owner_stat_verify '7722 (tee) S 7718 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7571832 0 0 0'; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|wrong-ticks|PASS\n"
if owner_stat_verify '7722 (tee) S 7718'; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|short-stat|PASS\n"
if owner_uid_verify D:/CodexProjects/VideoKit/docs/tester/D1_E4A_OWNER3_EVIDENCE/uid-good.txt; then actual=yes; else actual=no; fi; test "$actual" = yes; printf "LOCAL_ASSERT|uid-good|PASS\n"
if owner_uid_verify D:/CodexProjects/VideoKit/docs/tester/D1_E4A_OWNER3_EVIDENCE/uid-bad.txt; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|uid-bad|PASS\n"
if owner_uid_verify D:/CodexProjects/VideoKit/docs/tester/D1_E4A_OWNER3_EVIDENCE/uid-missing.txt; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|uid-missing|PASS\n"
if owner_uid_verify D:/CodexProjects/VideoKit/docs/tester/D1_E4A_OWNER3_EVIDENCE/uid-duplicate.txt; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|uid-duplicate|PASS\n"
if owner_pair_verify '74|123|10221' '74|123|10221'; then actual=yes; else actual=no; fi; test "$actual" = yes; printf "LOCAL_ASSERT|same-dev-inode|PASS\n"
if owner_pair_verify '75|123|10221' '74|123|10221'; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|wrong-dev|PASS\n"
if owner_pair_verify '74|124|10221' '74|123|10221'; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|wrong-inode|PASS\n"
if owner_pair_verify '74|123|2000' '74|123|2000'; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|wrong-owner|PASS\n"
if owner_pair_verify '74|123' '74|123'; then actual=yes; else actual=no; fi; test "$actual" = no; printf "LOCAL_ASSERT|malformed-stat-pair|PASS\n"
owner_observe_fields '7722 (tee) S 7718 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7571831 0 0 0'; test "$OWNER_OBSERVATION" = STILL_VISIBLE; printf "LOCAL_ASSERT|observe-same|PASS\n"
owner_observe_fields '7722 (tee) Z 7718 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7571831 0 0 0'; test "$OWNER_OBSERVATION" = ZOMBIE; printf "LOCAL_ASSERT|observe-zombie|PASS\n"
owner_observe_fields '7722 (tee) S 7718 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7571832 0 0 0'; test "$OWNER_OBSERVATION" = REUSED; printf "LOCAL_ASSERT|observe-reused|PASS\n"
owner_observe_fields '7722 (tee) S'; test "$OWNER_OBSERVATION" = UNKNOWN; printf "LOCAL_ASSERT|observe-malformed|PASS\n"
