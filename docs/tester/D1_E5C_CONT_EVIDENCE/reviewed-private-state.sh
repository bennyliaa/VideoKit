set -eu
printf 'APP_UID|'; id -u
printf 'APP_PWD|'; pwd
for p in files/e4a_output_budget/identity.anchor files/e4a_output_budget/ledger.bin files/e4a_output_budget/operation.pending files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.owner files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.mp4; do
 test -f "$p"; test ! -L "$p"
 printf 'STAT|%s|' "$p"; stat -c '%d,%i,%s,%u,%f,%Y' "$p"
done
for p in files/e4a_output_budget/identity.anchor files/e4a_output_budget/ledger.bin files/e4a_output_budget/operation.pending files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.owner; do
 n=$(stat -c %s "$p"); test "$n" -le 2048
 printf 'SHA|'; sha256sum "$p"
done
printf 'ANCHOR|'; cat files/e4a_output_budget/identity.anchor; printf '
'
printf 'LEDGER_BEGIN
'; cat files/e4a_output_budget/ledger.bin; printf 'LEDGER_END
'
for p in files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease; do
 printf 'HEX_BEGIN|%s
' "$p"; od -An -v -tx1 "$p"; printf 'HEX_END
'
done
for p in files/e4a_output_budget/N2-e5-recovery files/e4a_output_budget/N2-e5-recovery.complete files/e4a_output_budget/operation.pending.N2-e5-aborted; do
 if [ -e "$p" ] || [ -L "$p" ]; then printf 'UNEXPECTED|%s
' "$p"; exit 44; fi
done
for p in files/e4_fixtures/basic.mp4 files/e4_fixtures/subtitle.avi; do
 test -f "$p"; test ! -L "$p"; printf 'FIXTURE_STAT|%s|' "$p"; stat -c '%d,%i,%s,%u,%f,%Y' "$p"
done
