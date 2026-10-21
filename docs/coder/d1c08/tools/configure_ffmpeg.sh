#!/usr/bin/env bash
set -eu
cd /d/CodexProjects/VideoKit/docs/coder/d1c08/outputs
mkdir -p ffmpeg-build
cd ffmpeg-build
export PATH="/d/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin:/usr/bin:$PATH"
../../upstream/source/ffmpeg-8.0/configure \
 --target-os=android --arch=aarch64 --enable-cross-compile \
 --cc=clang --cxx=clang++ --ar=llvm-ar --ranlib=llvm-ranlib --nm=llvm-nm --strip=llvm-strip \
 --extra-cflags='--target=aarch64-linux-android31 -fPIC -O2' \
 --extra-ldflags='--target=aarch64-linux-android31 -Wl,-z,max-page-size=16384' \
 --enable-shared --disable-static --disable-programs --disable-doc --disable-debug \
 --enable-hardcoded-tables --host-cc='clang --target=aarch64-linux-android31' \
 --disable-autodetect --disable-network --disable-protocols \
 --disable-gpl --disable-nonfree --disable-version3 --disable-hwaccels \
 --disable-avdevice --disable-avfilter --disable-everything \
 --enable-avformat --enable-avcodec --enable-avutil --enable-swscale --disable-swresample \
 --enable-pthreads --disable-asm --disable-x86asm \
 --enable-demuxer=avi,mov --enable-decoder=mpeg4,h264 --enable-parser=mpeg4video,h264 \
 --prefix=/d/CodexProjects/VideoKit/docs/coder/d1c08/outputs/ffmpeg-install
echo C08_CONFIGURE_COMPLETE
