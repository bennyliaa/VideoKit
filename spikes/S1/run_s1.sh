#!/usr/bin/env bash
# S1 run on the emulator only (never the two phones). Copies samples from test_media (read-only) to the app's
# external files dir, runs the bench, pulls the results, deletes the copies.
# Usage: [CONDITIONS=local,lat100] [PREFETCH=256] [REPS=20] spikes/S1/run_s1.sh <out-dir> <sample>...
# Threshold pass (15 §4 item 7): CONDITIONS=local,lat100 PREFETCH=256 REPS=20 with the 1080p H.264 sample.
# Comparison pass: all conditions, the three read-ahead sizes, REPS=1.
set -euo pipefail
SERIAL=emulator-5556
PKG=com.videokit.spike.s1
OUT=$1; shift
ADB="adb -s $SERIAL"
HERE="$(cd "$(dirname "$0")" && pwd)"; command -v cygpath >/dev/null && HERE="$(cygpath -m "$HERE")"   # Windows adb needs D:/ paths
APK="$HERE/app/build/outputs/apk/debug/app-debug.apk"
mkdir -p "$OUT"
$ADB install -r "$APK"
$ADB shell am start -W -n $PKG/.S1Activity >/dev/null   # creates the external files dir
$ADB shell am force-stop $PKG
DIR=/sdcard/Android/data/$PKG/files
NAMES=()
for f in "$@"; do $ADB push "$f" "$DIR/" >/dev/null; NAMES+=("$(basename "$f")"); done
FILES=$(IFS=,; echo "${NAMES[*]}")
EXTRA=()
[ -n "${CONDITIONS:-}" ] && EXTRA+=(--es conditions "$CONDITIONS")
[ -n "${PREFETCH:-}" ] && EXTRA+=(--es prefetch "$PREFETCH")   # KiB, e.g. 256
[ -n "${REPS:-}" ] && EXTRA+=(--ei reps "$REPS")
$ADB shell rm -f "$DIR/s1_results.jsonl"   # the directory-creating launch above leaves a finished results file
$ADB logcat -c
$ADB shell am start -n $PKG/.S1Activity --es files "$FILES" "${EXTRA[@]}"
until $ADB shell cat "$DIR/s1_results.jsonl" 2>/dev/null | grep -q '"event":"done"'; do sleep 15; done
$ADB pull "$DIR/s1_results.jsonl" "$OUT/s1_results.jsonl"
$ADB logcat -d -v threadtime > "$OUT/logcat.txt"
$ADB shell am force-stop $PKG
for n in "${NAMES[@]}"; do $ADB shell rm -f "$DIR/$n"; done
echo "results in $OUT"
