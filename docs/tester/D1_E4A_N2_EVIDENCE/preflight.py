from common import *
new('preflight-attempt.json',{'batch':BATCH,'budget':BUDGET,'scope':'READONLY_NO_FIXTURE_HASH_NO_INSTALL'})
script='set -eu; getprop ro.product.model; getprop ro.build.version.sdk; getprop ro.product.cpu.abilist; am get-current-user; pm list packages -U com.videokit; pm path com.videokit.app; pm path com.videokit.app.test; date +%s; ps -A -o PID,UID,NAME'
r,text=shell(script,'00-environment',False);assert r['originalExitCode']==0
r,helptext=call(['logcat','--help'],'01-logcat-help');assert r['originalExitCode']==0
script='''set -u
u=$(id -u); p=$(pwd); printf 'IDENTITY|uid=%s|pwd=%s\n' "$u" "$p"; test "$u" = 10221 || exit 1; test "$p" = /data/user/0/com.videokit.app || exit 1
for f in files/e4_fixtures/basic.mp4 files/e4_fixtures/subtitle.avi; do test -f "$f" && test ! -L "$f" || exit 1; /system/bin/toybox stat -c '%n|%d,%i,%s,%u,%f,%Y' -- "$f" || exit 1; done
/system/bin/toybox df -k files
if test -e files/e4a_output_budget; then test -d files/e4a_output_budget && test ! -L files/e4a_output_budget || exit 1; printf 'BUDGET_DIR_PRESENT\n'; else printf 'BUDGET_DIR_ABSENT\n'; fi
for f in files/e4a_output_budget/identity.anchor files/e4a_output_budget/ledger.bin; do printf 'METADATA_BEGIN|%s\n' "$f"; if test -e "$f"; then test -f "$f" && test ! -L "$f" || exit 1; n=$(/system/bin/toybox stat -c %s -- "$f") || exit 1; test "$n" -le 131072 || exit 1; /system/bin/toybox head -c 131073 -- "$f"; printf '\n'; else printf 'ABSENT\n'; fi; printf 'METADATA_END|%s\n' "$f"; done
if test -e files/e4a_output_budget/operation.pending || test -L files/e4a_output_budget/operation.pending; then printf 'ORIGINAL_PENDING_PRESENT\n'; else printf 'ORIGINAL_PENDING_ABSENT\n'; fi
if test -e files/e4a_outputs; then test -d files/e4a_outputs && test ! -L files/e4a_outputs || exit 1; ls -lan -- files/e4a_outputs; else printf 'OUTPUT_DIRECTORY_ABSENT\n'; fi
'''
new('preflight-script.json',{'script':script,'sha256':hashlib.sha256(script.encode()).hexdigest(),'writes':0,'fixtureContentReadBytes':0,'scope':'Exact fixture stat, space, stable anchor/ledger/pending and nonrecursive output metadata only'})
r,text=shell(script,'02-private-admission');assert r['originalExitCode']==0 and 'ORIGINAL_PENDING_ABSENT' in text
new('preflight-result.json',{'status':'READONLY_OBSERVATIONS_COMPLETE_PENDING_ABSENT','fixtureShaReads':0,'retained':ep.retained_owners()});print(text,flush=True)
hold()
