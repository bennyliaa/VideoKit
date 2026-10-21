ps -A -o PID,PPID,UID,NAME | {
 IFS= read -r e_row || exit 1
 printf '%s\n' "$e_row"
 while IFS= read -r e_row; do
  case "$e_row" in *com.videokit.app*|*com.videokit.e13.sender*)printf '%s\n' "$e_row";;esac
 done
}