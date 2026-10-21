dumpsys user | {
 e_want=0
 while IFS= read -r e_row; do
  case "$e_row" in *UserInfo*)case "$e_row" in *'UserInfo{0:'*)e_want=1;;*)e_want=0;;esac;;esac
  if [ "$e_want" -eq 1 ]; then case "$e_row" in *UserInfo*|*State:*)printf '%s\n' "$e_row";;esac;fi
 done
}