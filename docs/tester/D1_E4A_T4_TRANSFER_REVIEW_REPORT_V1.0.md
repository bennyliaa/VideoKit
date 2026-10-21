# D1 E4A-T4 二进制路线独立复审报告 V1.0

日期：2026-10-17。依据D1_E4A_T4_TESTER_REQUIREMENTS_V1.0.md及负责人限定接受的合作式256B诊断范围。

**结论：SUPPORTED_FOR_SEPARATE_COOPERATIVE_256B_T4P_DIAGNOSTIC。未发现新的静态阻断，可另派准确T4P一次合成push与一次本地copy。设备执行仍NOT_RUN；Android12 staging基址/双视图权限必须现场准入，缺失或未知即停，不补建/改权限。push无原子no-replace已被负责人限定接受，不作为本范围阻断，也不推广为产品或对抗同UID承诺。D1未通过、M0未启动，P0/历史FAIL保持。**

## 1. 冻结与审查范围

| 项目 | 核验结果 |
|---|---|
| 外seal SHA-256 | 8eb3b4d82adaaba225eb22ee0afe90d551f9735a7518d1b34a7355927e4b2e67 |
| 源ZIP SHA-256 | a5a3b34daad71a86d7d5a993deb9c56e83895c662b9c9362b25268573676d0af |
| 已检查的只读verifier | PASS，72源/74不可变，精确归档与内容一致；物理623,172B/85文件、逻辑归档378,964B |
| tester独立审计 | PASS，见D1_E4A_T4_EVIDENCE/audit.py、identity-and-recorded-binary-audit.json |
| 原强门 | exact_process与T1/T3、command_response与T3字节相同；原T3L报告与E4A实际冻结保持 |

本轮仅静态代码/归档及已有记录审查，另核公开一手文档/源码；未执行CRT、fake或任何设备重评。ADB、设备、真实媒体stat/read/hash、Gradle和payload推送均0，无在途执行。

## 2. 0x1A机制与现场归因分栏

| 已证或有来源支持 | 尚未知 |
|---|---|
| T3L当前合成文件26B，与0..25前缀摘要一致；首缺字节0x1A | 原T3R具体失败子句与当时原n未记录 |
| 已有本机真实CRT _open/_read/_close：TEXT读26B、BINARY读256B，两原FD closeReturn0 | 没有运行现场ADB来观察其进程全局/描述符CRT模式 |
| Microsoft文档说明文本_read遇Ctrl-Z结束；机制可复现该边界 | SDK37.0.1与所查源码精确对应、现场具体截断函数、旧81,407B同因均UNKNOWN |

父Python二进制管道不证明子进程CRT模式。上述CRT结果只支持本机机制，不足以宣布设备根因已关闭。[Microsoft _read说明](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/read?view=msvc-170)

所查ADB sync实现通过源文件名读取并发送带长度的DATA数据，符合新路线不经shell stdin传payload的设计；该源码仍不能当成本机SDK精确映射。[ADB文件sync源码](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main-16k/client/file_sync_client.cpp)

## 3. staging双视图与权限门

固定base为 `/storage/emulated/0/Android/data/com.videokit.app/files`，必须已存在。shell UID2000与run-as UID10221分别确认实际角色、目录/非symlink、r/w/x及stat格式；app另外验证原pwd与files角色。两端均在变更前检查准确stage冲突，app检查准确internal冲突；base的已查询mode拒全局可写位。

准入后仅shell以umask077独占mkdir `e4_stage_T4P_TABLET_20261017_once`，不mkdir-p、不创建base或Android/data上层、不chmod、不root或改manifest权限。新stage创建后再次从app与shell验证可访问性及叶目标不存在，紧邻push的最后shell冲突门仍在。base、stage或模式不准入即停止，不能换全局可写临时区或改变路线。

Android11+应用专属外部根目录有框架管理约束，官方文档不能替代现场FUSE/SELinux/shell与run-as视图事实。现有base若未被应用创建，本合同应在只读阶段阻断，不授权现场补建。[Android应用专属存储](https://developer.android.com/training/data-storage/app-specific)

标准push不存在原子no-replace。本次新独占应用专属子目录和紧邻冲突门只按已获接受的合作式自有256B范围使用；没有对抗同UID检查后抢建保证。local fake用xb写文件也不能验证真实push原子拒覆盖。这个已知边界不需要再次询问或改变本轮结论，后续产品/媒体范围不得自动继承。

## 4. 独立stage、copy及internal证明

| 链路 | 生产代码门 |
|---|---|
| 主机固定源 | 无任意source参数；只读冻结payload256.bin，长度/SHA正确，单次read最多257B检测增长；实际close正常返回才继续 |
| 唯一push | 参数数组`push -q -Z 固定源 准确stage`，用标准ADB文件协议；所有shell带-n -T -e none，原collect stdin为空，不传payload |
| 独立stage证明 | 另条run-as命令核普通非symlink、stat长度256；head-c256硬限内容读取后SHA；前后完整stat相同，字段精确UID/pwd/path及预期SHA才准入 |
| 一次内部copy | stage原stamp须等于独立证明；新internal目录/目标不存在；同一原PID输出准确BEGIN/END、UID/pwd/source/target和256计数。umask077/mkdir准确子目录、set-C及head-c256文件到文件；源stamp复制前后仍相同 |
| 独立internal证明 | 再一条命令核普通非symlink、原app UID、前后stamp、256长度及最多256B SHA；全齐才合成通过 |

stamp包含dev/inode/size/uid/mode/mtime，文件角色和全局可写位均检查；internal UID必须10221。stage外部owner不盲定为app或shell，实际app可读门和独立内容/身份再核约束后续copy。双视图分别准入，不将两端路径字符串相同或fake字段当FUSE身份实证。

push exit0只表示原客户端命令完成。26B或超大stage在生产长度门先拒绝，不进入copy；即使某些本机fake直接生成了短件SHA，也不冒充已实跑Android的提前拒绝分支。缺END、SHA/身份/路径不符、模式不合法或源变化均不准入，失败文件/目录保留，不删除、回滚或续传。

设备hash和copy均使用head-c256，有硬读取量界；前后stamp和完整SHA用于合作式变化检测，不宣称对抗并发替换或掉电持久性。精确shell命令本机集中语法检查仅证明语法；设备head/stat/SHA/set-C通过base空输入探针和后续真实返回准入，不以本机模型猜兼容成功。

## 5. 原owner及本机证据

原T1 pump继续要求实际stdin/source/writer/drains/wait与线程归还；T3完整原响应门检查exit、无错误、完整总量/SHA及空stderr。新增SOURCE_OWNERS在实际源close异常时仍持原file对象，后续call在任何新IO前拒绝，CLI保留解释器；不二次close、用GC或退出假归还。此新增异常路径获得静态支持，本轮41条不是实际源close故障注入全覆盖。普通open/read/close不返回仍无绝对可强制中断承诺。

已有唯一main-001共41断言、25条真实本机调用：24个自有Python假客户端及1个Git shell-n，9个生成脚本只作语法检查。另有真实本机CRT模式对照。所有25个原进程/管道归还、stdin提交0；没有历史全套重跑或断言叠加。

成功模型走生产编排并在本机生成完整stage/internal 0..255文件；短stage26B但push0退出仍拒绝且copy0，base拒绝/冲突在源预哈希和push前停，旧自有26B dummy保持。独立SHA/UID/path/length、全局可写、内部错误owner、缺END和旧tee线索的拒绝有已有有限证据。

fake只是固定脚本响应模型，权限/UID/mode为合成字段；不执行真实run-as/SELinux/FUSE，不证明标准ADB实际收发、Android文件身份或权限成功。tester未重跑这些检查，旧设备26B文件未访问或修改。

## 6. 可另派T4P的精确条件

批次D1-E4A-T4P-TABLET-20261017、nonce E4T4P_TABLET_20261017_ONCE；仅HA1Q6WXR。stage准确leaf为上述专属base下 `e4_stage_T4P_TABLET_20261017_once/payload256.bin`；internal为 `files/e4_diag_T4P_TABLET_20261017_once/payload256.bin`。新包外证据D1_E4A_T4P_EVIDENCE；外seal/准确导入绑定后只按另行正式派发执行，当前executionAuthorized=false。

| 全成功计划量/上限，非实际用量 | 数量 |
|---|---:|
| metadata计划/上限 | 9 / 20 |
| push / copy次数 | 各1 |
| 每命令 / 本机收尾 | 15s / 2s |
| 日志 / 单原记录 | 1MiB / 64KiB |
| stdout/stderr计数门 / 前缀 | 各16KiB / 各4KiB |
| 主机工具预hash | 正常256B，硬读257B |
| ADB按文件名的名义输入 | 256B，实际内部read字节/次数UNKNOWN |
| stage SHA / 本地copy读取 / internal SHA | 各最多256B |
| stage/internal新增文件 | 各一个256B合成文件 |
| payload经stdin | 0B |

完整响应超过保留前缀即拒，不以未截留证明以外的摘要通过；沿T1 drain，超计数门最多额外一个16KiB块后拒绝。没有把命令回执伪造成ADB actualRead或submitted256；固定源不是对并发修改的快照，后续独立SHA继续约束准入。

base或权限/语法未知、旧receiver线索、冲突、任一非零/不完整/身份或SHA错误即保首因停止；UNKNOWN保原解释器和owner，不放宽目录、不加时/换路/补跑。不得访问旧26B路径/历史媒体、手机模拟器、安装、产品/Binder或预算标记。合成成功也仅说明新路线有限实证，由负责人另定媒体恢复，不能自动下一批。

本轮无新静态阻断、无在途；设备Android12准入及传输仍未知，当前仅支持上述已接受合作式范围另派一次。D1未通过、M0未启动，P0/历史FAIL及旧根因未知保持。
