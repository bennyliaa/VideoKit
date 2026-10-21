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
