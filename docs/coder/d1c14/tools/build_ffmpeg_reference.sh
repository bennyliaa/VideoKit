#!/usr/bin/env bash
set -eu
if [ "${VIDEOKIT_EXPLICIT_REFERENCE_REBUILD:-}" != "1" ]; then
 echo REFERENCE_ONLY_NOT_EXECUTED
 exit 0
fi
export PATH="/d/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin:/usr/bin:$PATH"
cd /d/CodexProjects/VideoKit/docs/coder/d1c14/outputs
mkdir -p ffmpeg-build
cd ffmpeg-build
../../upstream/source/ffmpeg-8.0.3/configure \
 --target-os=android --arch=aarch64 --enable-cross-compile \
 --cc=clang --cxx=clang++ --ar=llvm-ar --ranlib=llvm-ranlib --nm=llvm-nm --strip=llvm-strip \
 --extra-cflags='--target=aarch64-linux-android31 -fPIC -O2' \
 --extra-ldflags='--target=aarch64-linux-android31 -Wl,-z,max-page-size=16384 -L../allocator' \
 --extra-libs=-lvideokit_alloc --malloc-prefix=vk_c09_ \
 --enable-shared --disable-static --disable-programs --disable-doc --disable-debug \
 --enable-hardcoded-tables --host-cc='clang --target=aarch64-linux-android31' \
 --disable-autodetect --disable-network --disable-protocols --disable-gpl --disable-nonfree --disable-version3 \
 --disable-hwaccels --disable-avdevice --disable-avfilter --disable-everything \
 --enable-avformat --enable-avcodec --enable-avutil --enable-swscale --disable-swresample \
 --enable-pthreads --disable-asm --disable-x86asm \
 --enable-demuxer=avi,mov --enable-decoder=mpeg4,h264 --enable-parser=mpeg4video,h264
echo C09_CONFIGURE_COMPLETE
/d/Android/SDK/ndk/30.0.16248370/prebuilt/windows-x86_64/bin/make.exe \
 -f ../../upstream/source/ffmpeg-8.0.3/Makefile -j4 'SHELL=C:/Program Files/Git/bin/bash.exe' \
 SRC_PATH=../../upstream/source/ffmpeg-8.0.3 SRC_LINK=../../upstream/source/ffmpeg-8.0.3
echo C09_MAKE_COMPLETE
