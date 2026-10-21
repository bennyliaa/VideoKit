# C12 框架与自有胶水映射

2026-10-16；正式Flutter宿主＋独立Kit/AAR方向不变。本批是有限Debug实验，没有替换产品架构或自制媒体实现。

| 层 | 现有来源/版本 | C12适配与边界 |
|---|---|---|
| 正式宿主/Kit接口 | 既有SYSTEM_ARCHITECTURE及框架估算文档 | 不新增Flutter/AAR产品功能，Debug harness不冒充Kit完成 |
| 播放/编码/导出 | AndroidX Media3 1.9.3，锁定依赖 | 引擎、双轨输出/验证/READY及恢复算法不改，host7/legacy8回归 |
| CPU受限解码 | 官方签名FFmpeg8.0.3，原LGPL及特别许可映射 | 五原库与quota.c不变，仅JNI包身份重编译；不重写codec、不扩白名单/配额 |
| 隔离与传输 | Android Binder/Context.bindIsolatedService/ServiceConnection，API31+ | RegistrationProtocol、BindingRevocation及客户端/Service自编胶水；无新权限/组件/高权限服务 |
| 生命周期 | C11 WorkerGenerations、CpuLifecycle、AsyncReadBridge | 增加失败端点非primary记录；首次Binder/UID/PID、实际death、Source及两槽语义保持 |
| 退出取证 | ApplicationExitInfo、公开AOSP tombstone字段，C11有界reader | C12只包身份变化；原OS signal0、trace数据、外部raw边界不改；无protobuf runtime或自制crash handler |

Binder同步语义参照安装SDK36.1的IBinder/BinderProxy及固定 [AOSP Android12 BinderProxy](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/core/java/android/os/BinderProxy.java) 与 [JNI桥](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/core/jni/android_util_Binder.cpp)：同步RPC可附加框架标志，JNI继续传递flags。同步业务只按ONEWAY位判定，metadata不是业务授权；descriptor/code/kernel身份/session/端点/长度另行验证。不是声称设备恰为某个flags值。

本批新增Java规则/状态机/固定primitive协议为项目自编，没有引入第三方运行时依赖或算法/模型源码。API/schema来源用于兼容性参考；完整FFmpeg源档/许可/来源/配置/266对象/608依赖及NDK NOTICE随归档保留。正式外发/专利/商店义务仍未准入。
