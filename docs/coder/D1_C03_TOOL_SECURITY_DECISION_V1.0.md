# D1 C03 工具依赖安全决定

日期：2026-10-05；决定：RESTRICTED_USE / PENDING_SUPPORTED_UPGRADE；不是已修补、豁免或全面不可达证明。

复用 C02 的 346 个精确坐标匹配与许可证底稿，没有重复扫描未变化组件。新增 companion 锁定 95 坐标，全部来自已审核集合；宿主仍 346 坐标，新 Maven 坐标 0。151 runtime 的旧记录无命中不能写成无漏洞。自己的 JNI flock 代码与已安装 NDK 30 的编译元数据另列，不纳入 Maven 无命中统计。

16 个工具坐标及每条 47 个唯一 advisory 的摘要、官方修复事件、上游链接、配置及原始 JSON hash 见 [逐条附录](d1c03/evidence/TOOL_VULNERABILITY_REVIEW.md)和 `tool-vulnerability-review.json` / `advisories/`。每个命中仍 `patched=false`；撤回状态按原始数据披露。不能把不同维护分支的 fixed event 混作推荐强制版本。

## 实际调用与限制

12 个 Netty 坐标来自 UTP core 的 4.1.93 和 emulator-control 的 4.1.110，涵盖 codec/http/http2/common/handler/proxy。触发条件分别是敌对 HTTP/HTTP2 frame/header/chunk/compression/reset/continuation、代理请求解析以及造成缓冲泄漏/资源耗尽的 channel 关闭。仅有 classpath 并不证明触发；本轮未启动 UTP core、emulator-control 或远程 listener。AGP 已缓存源码的任务证据保存于 `agp-task-source-excerpts.json`，配置阶段拒绝 connected/managed/deviceCheck 和执行类任务，相关任务类型还标记 disabled。`tool-guard-probe.log` 的 help 配置探针得到预期拒绝，**没有执行设备任务**。未来直接 instrumentation 不启动 Gradle UTP，但仍须单独设备授权。此限制覆盖当前构建流程，不保证任何 IDE/外部工具都受这个 Gradle 文件保护。

另 4 个坐标同时在 androidLintTool 与 UTP result-listener classpath：

| 坐标 | 触发入口与可达性判断 | 官方修复与处置 |
| --- | --- | --- |
| commons-lang3 3.16.0 | 极长类名经 ClassUtils.getClass 导致栈耗尽；lint 处理不可信工程/类名存在潜在调用面，没有逐调用点不可达证明 | GHSA-j288-q9x7-2f5v；3.18.0 修复。只允许当前本地固定工程，禁止拿此工具链审核外部敌对工程 |
| httpclient 4.5.6 | 非法 URI authority 导致错误主机解析；工具网络请求存在潜在入口 | GHSA-7r82-7xv7-xcpj；4.5.13 或独立 5.x 分支 5.0.3。构建严格 offline，不启动结果 listener；不强制换主版本 |
| bcpkix-jdk18on 1.79 | draft composite signature 验证接受空签名；敌对证书/签名输入可能触发 | GHSA-wg6q-6289-32hp；1.84 修复。当前只处理本地锁定构件与自生成 debug 签名，不导入敌对证书或开放 listener |
| bcprov-jdk18on 1.79 | G3413 GOST CTR 计数器复用、NameConstraints、LDAPStoreHelper 注入、lazy ASN.1 嵌套限制；密码/证书/ASN.1/LDAP 输入潜在可达 | 四条 ID 和各版本见逐条附录；1.84/1.85 及指定 backport 分别修复不同项。限制输入和网络，不把未使用某算法等同整个 provider 不可达 |

实际 `lintVitalRelease` 已运行在此本地工程，不能说所有受影响工具都未执行或完全不可达。本轮的 offline、受控本地输入和禁用服务是降低暴露的使用限制，未做敌对输入复现或运行时调用覆盖验证，不产生安全 PASS。

## 支持的升级门禁

[AGP 官方 9.3 发布说明](https://developer.android.com/build/releases/agp-9-3-0-release-notes)列出 9.3.3 的 D8/R8 修复，没有证明这一传递图的全部 47 advisory 已修补。保持现有锁定及严格 verification，不盲 override 内部 Netty/gRPC/BC，也不把“已最新 AGP”作为关闭理由。[Commons 官方变更](https://commons.apache.org/proper/commons-lang/changes.html)及每条上游 advisory 支持具体修复版本，不证明 AGP 兼容这些替换。

恢复 UTP/远程 emulator-control、接收外部工程/证书/URL 前，要求候选官方支持 AGP/UTP/lint 依赖图满足逐 advisory 的相应维护分支修复范围；对**变化坐标**再做精确许可/漏洞审核、verification、签名、编译和工具互操作回归，保留新的 candidate。若官方图仍含命中，则继续禁用相关入口并由负责人决定更换支持工具链，不能自行解除限制。当前存在工具风险残留，最终 SDK NOTICE/分发审核也未关闭。
