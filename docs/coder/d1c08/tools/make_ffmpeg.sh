#!/usr/bin/env bash
set -eu
export PATH="/d/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin:/usr/bin:$PATH"
cd /d/CodexProjects/VideoKit/docs/coder/d1c08/outputs/ffmpeg-build
/d/Android/SDK/ndk/30.0.16248370/prebuilt/windows-x86_64/bin/make.exe -f ../../upstream/source/ffmpeg-8.0/Makefile -j4 'SHELL=C:/Program Files/Git/bin/bash.exe' SRC_PATH=../../upstream/source/ffmpeg-8.0 SRC_LINK=../../upstream/source/ffmpeg-8.0
