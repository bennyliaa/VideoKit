#!/usr/bin/env bash
# S4 run on the emulator only (never the two phones). Copies the export input and the playback sample from
# test_media (read-only) to the app's external files dir, runs the fault cases, pulls the results, deletes the copies.
# Usage: spikes/S4/run_s4.sh <out-dir> <export-input> <playback-sample> [FAULTS=NONE,CANCEL,SIGSEGV,OOM,LOOP,KILL]
set -euo pipefail
SERIAL=emulator-5556
PKG=com.videokit.spike.s4
OUT=$1; INPUT=$2; PLAY=$3
ADB="adb -s $SERIAL"
HERE="$(cd "$(dirname "$0")" && pwd)"; command -v cygpath >/dev/null && HERE="$(cygpath -m "$HERE")"   # Windows adb needs D:/ paths
APK="$HERE/app/build/outputs/apk/debug/app-debug.apk"
mkdir -p "$OUT"
$ADB install -r "$APK"
$ADB shell am start -W -n $PKG/.S4Activity >/dev/null
$ADB shell am force-stop $PKG
DIR=/sdcard/Android/data/$PKG/files
$ADB push "$INPUT" "$DIR/" >/dev/null
[ "$PLAY" != "$INPUT" ] && $ADB push "$PLAY" "$DIR/" >/dev/null
EXTRA=(); [ -n "${FAULTS:-}" ] && EXTRA=(--es faults "$FAULTS")
$ADB shell rm -f "$DIR/s4_results.jsonl"   # the directory-creating launch above leaves a finished results file
$ADB logcat -c
$ADB shell am start -n $PKG/.S4Activity --es input "$(basename "$INPUT")" --es play "$(basename "$PLAY")" "${EXTRA[@]}"
until $ADB shell cat "$DIR/s4_results.jsonl" 2>/dev/null | grep -q '"event":"done"'; do sleep 10; done
$ADB pull "$DIR/s4_results.jsonl" "$OUT/s4_results.jsonl"
$ADB logcat -d -v threadtime > "$OUT/logcat.txt"
# Worker processes that may survive (LOOP): record what the system shows, then stop the app.
$ADB shell ps -A -o PID,USER,RSS,NAME | grep -i "s4" > "$OUT/processes_after.txt" || true
$ADB shell am force-stop $PKG
$ADB shell rm -f "$DIR/$(basename "$INPUT")" "$DIR/$(basename "$PLAY")"
echo "results in $OUT"
