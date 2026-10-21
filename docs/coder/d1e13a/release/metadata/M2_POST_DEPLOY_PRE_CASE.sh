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
emit USER0_STATE 512 sh -c 'dumpsys user | awk '"'"'/UserInfo/ {want=($0 ~ /UserInfo\{0:/)} want && /UserInfo|State:/ {print}'"'"''
emit RELATED_PS 4096 sh -c 'ps -A -o PID,PPID,UID,NAME | awk '"'"'NR==1 || $4 ~ /^com[.]videokit[.](app|e13[.]sender)([:.]|$)/ {print}'"'"''
emit INSTRUMENTATION 4096 dumpsys activity instrumentation
emit APP_SERVICES 4096 dumpsys activity services com.videokit.app
emit FIXTURE_SERVICES 4096 dumpsys activity services com.videokit.e13.sender
emit APK_APP 1024 sh -c 'p=$(pm path com.videokit.app); case "$p" in package:/data/app/*/base.apk) ;; *) exit 23;; esac; p=${p#package:}; case "$p" in *'"'"'
'"'"'*) exit 24;; esac; printf '"'"'%s\n'"'"' "$p"; sha256sum "$p"'
emit PKG_APP 2048 sh -c 'dumpsys package com.videokit.app | awk '"'"'/^[ ]*(userId=|versionCode=|User 0:)/ {print}'"'"''
emit APK_TEST 1024 sh -c 'p=$(pm path com.videokit.app.test); case "$p" in package:/data/app/*/base.apk) ;; *) exit 23;; esac; p=${p#package:}; case "$p" in *'"'"'
'"'"'*) exit 24;; esac; printf '"'"'%s\n'"'"' "$p"; sha256sum "$p"'
emit PKG_TEST 2048 sh -c 'dumpsys package com.videokit.app.test | awk '"'"'/^[ ]*(userId=|versionCode=|User 0:)/ {print}'"'"''
emit APK_FIXTURE 1024 sh -c 'p=$(pm path com.videokit.e13.sender); case "$p" in package:/data/app/*/base.apk) ;; *) exit 23;; esac; p=${p#package:}; case "$p" in *'"'"'
'"'"'*) exit 24;; esac; printf '"'"'%s\n'"'"' "$p"; sha256sum "$p"'
emit PKG_FIXTURE 2048 sh -c 'dumpsys package com.videokit.e13.sender | awk '"'"'/^[ ]*(userId=|versionCode=|User 0:)/ {print}'"'"''
emit DATA_APP 128 run-as com.videokit.app stat -c '%u|%i' .
emit DATA_TEST 128 run-as com.videokit.app.test stat -c '%u|%i' .
printf 'E13A_METADATA_END\tM2_POST_DEPLOY_PRE_CASE\n'
