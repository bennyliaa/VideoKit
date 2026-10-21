# Fixed read-only T4L checklist; subfailures preserved, no set-e.
step() { label=$1; shift; printf 'STEP_BEGIN|%s\n' "$label"; "$@"; rc=$?; printf 'STEP_END|%s|rc=%s\n' "$label" "$rc"; }
u=$(id -u); urc=$?; p=$(pwd); prc=$?; printf 'IDENTITY|uid=%s|idrc=%s|pwd=%s|pwdrc=%s\n' "$u" "$urc" "$p" "$prc"
step uid test "$u" = 10221
if [ "$urc" != 0 ] || [ "$u" != 10221 ]; then printf "CONTEXT_REJECT\n"; exit 0; fi
step pwd test "$p" = /data/user/0/com.videokit.app
if [ "$prc" != 0 ] || [ "$p" != /data/user/0/com.videokit.app ]; then printf "CONTEXT_REJECT\n"; exit 0; fi
step base.e test -e /storage/emulated/0/Android/data/com.videokit.app/files
step base.d test -d /storage/emulated/0/Android/data/com.videokit.app/files
step base.L test -L /storage/emulated/0/Android/data/com.videokit.app/files
step base.r test -r /storage/emulated/0/Android/data/com.videokit.app/files
step base.w test -w /storage/emulated/0/Android/data/com.videokit.app/files
step base.x test -x /storage/emulated/0/Android/data/com.videokit.app/files
step base.stat /system/bin/toybox stat -c %d,%i,%s,%u,%f,%Y -- /storage/emulated/0/Android/data/com.videokit.app/files
step stage.e test -e /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once
step stage.d test -d /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once
step stage.L test -L /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once
step stage.r test -r /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once
step stage.w test -w /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once
step stage.x test -x /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once
step stage.absent_e test ! -e /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once
step stage.absent_L test ! -L /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once
step stage.stat /system/bin/toybox stat -c %d,%i,%s,%u,%f,%Y -- /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once
step download.e test -e /storage/emulated/0/Download
step download.d test -d /storage/emulated/0/Download
step download.L test -L /storage/emulated/0/Download
step download.r test -r /storage/emulated/0/Download
step download.w test -w /storage/emulated/0/Download
step download.x test -x /storage/emulated/0/Download
step download.stat /system/bin/toybox stat -c %d,%i,%s,%u,%f,%Y -- /storage/emulated/0/Download
step files.e test -e files
step files.d test -d files
step files.L test -L files
step files.r test -r files
step files.w test -w files
step files.x test -x files
step files.stat /system/bin/toybox stat -c %d,%i,%s,%u,%f,%Y -- files
step internal.e test -e files/e4_diag_T4P_TABLET_20261017_once
step internal.d test -d files/e4_diag_T4P_TABLET_20261017_once
step internal.L test -L files/e4_diag_T4P_TABLET_20261017_once
step internal.r test -r files/e4_diag_T4P_TABLET_20261017_once
step internal.w test -w files/e4_diag_T4P_TABLET_20261017_once
step internal.x test -x files/e4_diag_T4P_TABLET_20261017_once
step internal.absent_e test ! -e files/e4_diag_T4P_TABLET_20261017_once
step internal.absent_L test ! -L files/e4_diag_T4P_TABLET_20261017_once
step internal.stat /system/bin/toybox stat -c %d,%i,%s,%u,%f,%Y -- files/e4_diag_T4P_TABLET_20261017_once
step tool.head0 /system/bin/toybox head -c 0 -- /dev/null
printf "STEP_BEGIN|tool.sha_empty\n"; h=$(printf "" | /system/bin/toybox sha256sum); rc=$?; printf "%s\n" "$h"; printf "STEP_END|tool.sha_empty|rc=%s\n" "$rc"; h=${h%% *}
step tool.sha_expected test "$h" = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
printf "STEP_BEGIN|tool.setC\n"; (set -C); rc=$?; printf "STEP_END|tool.setC|rc=%s\n" "$rc"
step download.df /system/bin/toybox df -k /storage/emulated/0/Download
printf "CHECKLIST_END\n"
