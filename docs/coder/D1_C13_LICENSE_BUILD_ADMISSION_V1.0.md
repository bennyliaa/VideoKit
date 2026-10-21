# C13 许可与构建准入 V1.0

2026-10-16：仅本地Debug技术实验。C13继承C09签名核验收据及C12已准入五个FFmpeg/配额二进制；本批没有重跑GPG、重建FFmpeg或新全量漏洞扫描。完整源ffmpeg-8.0.3.tar.xz SHA256 `6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818`、官方签名/公钥、生成配置、266对象/608依赖映射与安全差异证据实际随源归档保留。

FFmpeg聚合LGPL-2.1-or-later；IJG、ISC、MIT、Zlib编译文件声明保留在notice-assets。GPL/nonfree/version3/network均禁用，无FFmpeg encoder/muxer/protocol/hardware codec扩展；H263为MPEG4传递编译要求，运行输入仍只MP4/H264、AVI/MPEG4。quota.c及五库与C12逐字节核验，原vk_c09前缀故意保留。API31 ARM64、16KiB ELF/ZIP对齐为静态证据，不是16KiB页设备通过。

本批NDK改动为项目cpu.c JNI glue：mode10旋转安全门、mode11六帧完整EOF/实际尺寸/PTS验证；普通mode0–9同实现复用，不宣称源只改JNI包名。原配额/白名单不变。lease.c除包身份保持。实际源码差异、编译命令、符号、JNI callback descriptor和产物SHA留在evidence；无模型/媒体入APK。

Media3 1.9.3为既有Apache-2.0依赖，现使用其fMP4 WritableByteChannel与sample-copy能力；公共系统AVC属于设备能力，非新引第三方codec。其实现、安全与专利/发行条件不是一次本地构建自动许可。C13自有胶水映射见FRAMEWORK_MAPPING，c13-sbom.cdx.json与NOTICE随产物保留。Release必须与历史release同SHA且无c13 class/service/native/notice。

外发完整对应源、修改标识、替换/再链接材料、接收方使用条款、EULA/商店/专利/模型和素材权利仍需独立准入；动态链接及Debug编译通过不关闭发行门禁。新增胶水没有限制LGPL允许的修改/调试。YuNet/ViTTrack只有文字与LFS指针调查，不加入SBOM为已集成模型；ML Kit未准入。
