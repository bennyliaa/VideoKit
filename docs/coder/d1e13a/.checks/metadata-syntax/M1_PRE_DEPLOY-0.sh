set -eu
export LC_ALL=C
emit() {
 label="$1"; max="$2"; shift 2
 if value=$("$@" 2>&1); then :; else printf 'RECORD_ERROR\t%s\n' "$label" >&2; exit 21; fi
 size=$(printf '%s' "$value" | wc -c)
 if [ "$size" -gt "$max" ]; then printf 'RECORD_OVERSIZE\t%s\n' "$label" >&2; exit 22; fi
 printf 'BEGIN\t%s\n%s\nEND\t%s\n' "$label" "$value" "$label"
}

printf 'E13A_METADATA\tM1_PRE_DEPLOY\tD1-20261018-E13A\n'
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
emit DATA_APP 128 run-as com.videokit.app stat -c '%u|%i' .
emit DATA_TEST 128 run-as com.videokit.app.test stat -c '%u|%i' .
emit FIXTURE_ABSENT 256 pm list packages com.videokit.e13.sender
run-as com.videokit.app sh -c 'set -eu
export LC_ALL=C
emit() {
 label="$1"; max="$2"; shift 2
 if value=$("$@" 2>&1); then :; else printf '"'"'RECORD_ERROR\t%s\n'"'"' "$label" >&2; exit 21; fi
 size=$(printf '"'"'%s'"'"' "$value" | wc -c)
 if [ "$size" -gt "$max" ]; then printf '"'"'RECORD_OVERSIZE\t%s\n'"'"' "$label" >&2; exit 22; fi
 printf '"'"'BEGIN\t%s\n%s\nEND\t%s\n'"'"' "$label" "$value" "$label"
}

emit STAT:files 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files
emit STAT:files/e4a_output_budget 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget
emit STAT:files/e4a_outputs 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs
emit STAT:files/e4a_output_budget/N2-e5-recovery 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/N2-e5-recovery
emit STAT:files/e4a_output_budget/legacy-acceptance 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/legacy-acceptance
emit STAT:files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde
emit STAT:files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/actors 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/actors
emit STAT:files/e4a_output_budget/N2-e5-recovery/identity.before 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/N2-e5-recovery/identity.before
emit STAT:files/e4a_output_budget/N2-e5-recovery/journal.before 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/N2-e5-recovery/journal.before
emit STAT:files/e4a_output_budget/N2-e5-recovery/lease.before 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/N2-e5-recovery/lease.before
emit STAT:files/e4a_output_budget/N2-e5-recovery/ledger.before 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/N2-e5-recovery/ledger.before
emit STAT:files/e4a_output_budget/N2-e5-recovery/recovery.owner 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/N2-e5-recovery/recovery.owner
emit STAT:files/e4a_output_budget/N2-e5-recovery/proof.txt 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/N2-e5-recovery/proof.txt
emit STAT:files/e4a_output_budget/N2-e5-recovery/guard.identity 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/N2-e5-recovery/guard.identity
emit STAT:files/e4a_output_budget/identity.anchor 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/identity.anchor
emit STAT:files/e4a_output_budget/N2-e5-recovery.complete 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/N2-e5-recovery.complete
emit STAT:files/e4a_output_budget/operation.pending.N2-e5-aborted 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/operation.pending.N2-e5-aborted
emit STAT:files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity
emit STAT:files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal
emit STAT:files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease
emit STAT:files/e4a_output_budget/ledger.bin 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/ledger.bin
emit STAT:files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.owner 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.owner
emit STAT:files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/actors/0001.intent 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/actors/0001.intent
emit STAT:files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.acceptance 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.acceptance
emit STAT:files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.commit 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.commit
emit STAT:files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.mp4 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.mp4
emit STAT:files/e4a_outputs/0ee15550-8952-4639-91ac-83ab9d14d36c.mp4 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/0ee15550-8952-4639-91ac-83ab9d14d36c.mp4
emit STAT:files/e4a_outputs/fbe4330b-111b-4b05-a93c-467413eb8d34.mp4 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/fbe4330b-111b-4b05-a93c-467413eb8d34.mp4
emit STAT:files/e4_fixtures/basic.mp4 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4_fixtures/basic.mp4
emit STAT:files/e4_fixtures/subtitle.avi 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4_fixtures/subtitle.avi
emit STAT:files/e4a_outputs/0e3dcbcc-d7db-451e-ad17-00b95c3c04a1.mp4 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/0e3dcbcc-d7db-451e-ad17-00b95c3c04a1.mp4
emit STAT:files/e4a_outputs/acb10ab9-b26c-42b3-b04a-d27417c868fd.mp4 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/acb10ab9-b26c-42b3-b04a-d27417c868fd.mp4
emit STAT:files/e4a_outputs/5b78515c-1699-4374-be66-8b8a367a6dec.mp4 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/5b78515c-1699-4374-be66-8b8a367a6dec.mp4
emit STAT:files/e4a_outputs/64507c9c-a650-462f-9af7-bc2bf32b1f5a.mp4 160 stat -c '"'"'%d|%i|%u|%f|%s|%b'"'"' files/e4a_outputs/64507c9c-a650-462f-9af7-bc2bf32b1f5a.mp4
emit INVENTORY 8192 sh -c '"'"'find files/e4a_output_budget files/e4a_outputs -maxdepth 4 -print | sort'"'"'
[ -f files/e4a_output_budget/N2-e5-recovery/identity.before ] && [ ! -L files/e4a_output_budget/N2-e5-recovery/identity.before ] || exit 25
[ "$(wc -c < files/e4a_output_budget/N2-e5-recovery/identity.before)" -eq 225 ] || exit 26
emit CONTROL:files/e4a_output_budget/N2-e5-recovery/identity.before 305 base64 files/e4a_output_budget/N2-e5-recovery/identity.before
[ -f files/e4a_output_budget/N2-e5-recovery/journal.before ] && [ ! -L files/e4a_output_budget/N2-e5-recovery/journal.before ] || exit 25
[ "$(wc -c < files/e4a_output_budget/N2-e5-recovery/journal.before)" -eq 85 ] || exit 26
emit CONTROL:files/e4a_output_budget/N2-e5-recovery/journal.before 119 base64 files/e4a_output_budget/N2-e5-recovery/journal.before
[ -f files/e4a_output_budget/N2-e5-recovery/lease.before ] && [ ! -L files/e4a_output_budget/N2-e5-recovery/lease.before ] || exit 25
[ "$(wc -c < files/e4a_output_budget/N2-e5-recovery/lease.before)" -eq 36 ] || exit 26
emit CONTROL:files/e4a_output_budget/N2-e5-recovery/lease.before 50 base64 files/e4a_output_budget/N2-e5-recovery/lease.before
[ -f files/e4a_output_budget/N2-e5-recovery/ledger.before ] && [ ! -L files/e4a_output_budget/N2-e5-recovery/ledger.before ] || exit 25
[ "$(wc -c < files/e4a_output_budget/N2-e5-recovery/ledger.before)" -eq 192 ] || exit 26
emit CONTROL:files/e4a_output_budget/N2-e5-recovery/ledger.before 261 base64 files/e4a_output_budget/N2-e5-recovery/ledger.before
[ -f files/e4a_output_budget/N2-e5-recovery/recovery.owner ] && [ ! -L files/e4a_output_budget/N2-e5-recovery/recovery.owner ] || exit 25
[ "$(wc -c < files/e4a_output_budget/N2-e5-recovery/recovery.owner)" -eq 104 ] || exit 26
emit CONTROL:files/e4a_output_budget/N2-e5-recovery/recovery.owner 143 base64 files/e4a_output_budget/N2-e5-recovery/recovery.owner
[ -f files/e4a_output_budget/N2-e5-recovery/proof.txt ] && [ ! -L files/e4a_output_budget/N2-e5-recovery/proof.txt ] || exit 25
[ "$(wc -c < files/e4a_output_budget/N2-e5-recovery/proof.txt)" -eq 401 ] || exit 26
emit CONTROL:files/e4a_output_budget/N2-e5-recovery/proof.txt 545 base64 files/e4a_output_budget/N2-e5-recovery/proof.txt
[ -f files/e4a_output_budget/N2-e5-recovery/guard.identity ] && [ ! -L files/e4a_output_budget/N2-e5-recovery/guard.identity ] || exit 25
[ "$(wc -c < files/e4a_output_budget/N2-e5-recovery/guard.identity)" -eq 82 ] || exit 26
emit CONTROL:files/e4a_output_budget/N2-e5-recovery/guard.identity 115 base64 files/e4a_output_budget/N2-e5-recovery/guard.identity
[ -f files/e4a_output_budget/identity.anchor ] && [ ! -L files/e4a_output_budget/identity.anchor ] || exit 25
[ "$(wc -c < files/e4a_output_budget/identity.anchor)" -eq 36 ] || exit 26
emit CONTROL:files/e4a_output_budget/identity.anchor 50 base64 files/e4a_output_budget/identity.anchor
[ -f files/e4a_output_budget/N2-e5-recovery.complete ] && [ ! -L files/e4a_output_budget/N2-e5-recovery.complete ] || exit 25
[ "$(wc -c < files/e4a_output_budget/N2-e5-recovery.complete)" -eq 96 ] || exit 26
emit CONTROL:files/e4a_output_budget/N2-e5-recovery.complete 131 base64 files/e4a_output_budget/N2-e5-recovery.complete
[ -f files/e4a_output_budget/operation.pending.N2-e5-aborted ] && [ ! -L files/e4a_output_budget/operation.pending.N2-e5-aborted ] || exit 25
[ "$(wc -c < files/e4a_output_budget/operation.pending.N2-e5-aborted)" -eq 0 ] || exit 26
emit CONTROL:files/e4a_output_budget/operation.pending.N2-e5-aborted 1 base64 files/e4a_output_budget/operation.pending.N2-e5-aborted
[ -f files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity ] && [ ! -L files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity ] || exit 25
[ "$(wc -c < files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity)" -eq 225 ] || exit 26
emit CONTROL:files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity 305 base64 files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity
[ -f files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal ] && [ ! -L files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal ] || exit 25
[ "$(wc -c < files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal)" -eq 85 ] || exit 26
emit CONTROL:files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal 119 base64 files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal
[ -f files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease ] && [ ! -L files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease ] || exit 25
[ "$(wc -c < files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease)" -eq 36 ] || exit 26
emit CONTROL:files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease 50 base64 files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease
[ -f files/e4a_output_budget/ledger.bin ] && [ ! -L files/e4a_output_budget/ledger.bin ] || exit 25
[ "$(wc -c < files/e4a_output_budget/ledger.bin)" -eq 2271 ] || exit 26
emit CONTROL:files/e4a_output_budget/ledger.bin 3069 base64 files/e4a_output_budget/ledger.bin
[ -f files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.owner ] && [ ! -L files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.owner ] || exit 25
[ "$(wc -c < files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.owner)" -eq 0 ] || exit 26
emit CONTROL:files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.owner 1 base64 files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.owner
[ -f files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/actors/0001.intent ] && [ ! -L files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/actors/0001.intent ] || exit 25
[ "$(wc -c < files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/actors/0001.intent)" -eq 959 ] || exit 26
emit CONTROL:files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/actors/0001.intent 1298 base64 files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/actors/0001.intent
[ -f files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.acceptance ] && [ ! -L files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.acceptance ] || exit 25
[ "$(wc -c < files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.acceptance)" -eq 725 ] || exit 26
emit CONTROL:files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.acceptance 982 base64 files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.acceptance
[ -f files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.commit ] && [ ! -L files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.commit ] || exit 25
[ "$(wc -c < files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.commit)" -eq 244 ] || exit 26
emit CONTROL:files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.commit 334 base64 files/e4a_output_budget/legacy-acceptance/4f21f71a-bf66-4a44-a287-320f0ae25fde/n2-v2.commit'
printf 'E13A_METADATA_END\tM1_PRE_DEPLOY\n'
