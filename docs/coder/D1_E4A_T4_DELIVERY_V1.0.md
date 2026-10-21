# D1 E4A-T4 开发交付 V1.0

2026-10-17。候选 D1-20261017-E4A-T4。已实现标准 push→应用专属 staging→设备本地有限复制路线，并完成本机有限检查；设备执行 NOT_RUN，待负责人审查另派。路径相对 D:\CodexProjects\VideoKit。

## 已证与未知

T3R 原客户端提交256B、仅BEGIN、exit1；T3L后续准确文件为26B，SHA b858da80d8a57dc546905fd147612ebddd3c9188620405d058f9ee5ab1e6bc52，等于0..25前缀，首缺0x1A。T3L不是T3R原END，旧NOT_ADMITTED不变；新工具不访问该26B残件或媒体路径。

本轮在本机实际调用 Windows CRT _open/_read/_close：同一自有256B文件，_O_TEXT返回26B及同一前缀SHA，_O_BINARY返回256B及完整SHA，两个原描述符均实际close返回0。这证明该本机CRT机制可以复现边界，**没有运行或证明现场ADB实际用了该模式**。Microsoft明确记录文本读取的Ctrl-Z结束语义及二进制模式区别。[CRT _read](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/read?view=msvc-170)、[_setmode](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/setmode?view=msvc-170)。父Python使用二进制管道不证明子进程自身CRT描述符处于二进制模式。

所查固定[AOSP commandline.cpp](https://android.googlesource.com/platform/packages/modules/adb/+/7c2fd99d6ec7e0d2d977ba03cecc82375af1baad/client/commandline.cpp)中，shell输入线程调用unix_read_interruptible；copy_to_file另有显式Windows二进制prologue，不能将后一条路径的设置套用于前者。另一固定版本[sysdeps_win32.cpp](https://android.googlesource.com/platform/packages/modules/adb/+/f4ba8d73079b99532069dbe888a58167b8723d6c/sysdeps_win32.cpp)的非控制台输入委托CRT读取，文件描述符实现则使用ReadFile。所查函数不能排除其他全局初始化的作用。

本地SDK source.properties为37.0.1；精确源码/二进制映射、SDK进程全局CRT模式、T3R现场截断函数以及旧81407B问题根因仍UNKNOWN。未通过运行adb或下载依赖补证。必要报告、两份原收据及源码出处分析保存在reference与evidence/source-analysis.json，不嵌套复制历史源码包。

## 新路线与限制

diag工具只有固定合成文件，没有媒体源参数。所有命令复用T1 exact_process.collect，原stdin为空；shell使用-n -T -e none。标准`adb push -q -Z <固定payload256.bin> <准确staging文件>`通过文件名读取合成源，不通过shell stdin发送payload。所查[ADB文件sync实现](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main-16k/client/file_sync_client.cpp)从文件读取并发送带长度的数据；本工具没有另造sync协议。

候选外部base为/storage/emulated/0/Android/data/com.videokit.app/files，必须已存在。shell UID2000与run-as原UID10221/pwd分别检查它的目录角色、非符号链接、r/w/x及stat格式，并以空输入探测head/stat/SHA工具与set-C语法。随后一次原UID进程快照；若见疑似旧接收即停止，不信号，未见仍UNKNOWN_NOT_CLEARED。

准入后仅mkdir准确新子目录e4_stage_T4P_TABLET_20261017_once，不mkdir -p、不创建框架base或其父目录、不chmod。新stage分别从app与shell复核可访问性/目标不存在，才一次push。目录及文件元数据门拒绝全局可写位；内部最终文件须原app UID。Android12 scoped storage/FUSE、SELinux与shell/run-as双视图权限仍须现场准入；不默认可用，拒绝即停。[Android应用专属存储说明](https://developer.android.com/training/data-storage/app-specific)也不能代替这些现场事实；其Android11+框架目录限制是要求base预存在的原因。

push exit0只证明原客户端命令完成。另起run-as命令对准确stage文件独立前后stat、长度256与最多256B内容SHA，完全一致才准入copy。一次内部copy先核stage原stat身份不变、新internal目录不存在；mkdir准确子目录、set-C后从stage文件head -c256输出至新internal文件。原BEGIN/END须同UID/pwd/PID/准确source/target及256计数。再起独立命令对internal作前后stat、长度及最多256B SHA。只有两个独立证明与原copy结束齐全才记BINARY_PUSH_AND_LOCAL_COPY_VERIFIED_NOT_A_MEDIA_FIXTURE。

**标准adb push不提供原子no-replace选项。** 本方案使用独占创建的新应用专属子目录和push前准确冲突门，已有目录/文件即拒绝；它不保证抵抗同UID并发者在检查后抢建目标。这个已知边界在计划JSON与封存facts中明确保留，不能宣称ADB有原子拒覆盖能力。内部输出采用noclobber，旧路径从不作为目标。若负责人要求对抗并发抢建也必须原子拒覆盖，本提案不能据此直接获准；不得临时放宽目录或换路线。

## 预算与原owner

新批次D1-E4A-T4P-TABLET-20261017，nonce E4T4P_TABLET_20261017_ONCE；stage/internal各最多新增一个256B文件。metadata计划9、上限20，push1/copy1各15s，所有metadata15s、本机共同归还观察2s、日志1MiB。每份原记录64KiB，stdout/stderr各16KiB/保留各4KiB。失败保留所有产物，不重传/换路/删除/重命名/发布媒体。

主机只读固定冻结合成源：工具预哈希正常256B、硬读上限257B（检测增长）；实际close返回后才继续。ADB按文件名读取的名义输入256B，其内部实际read次数/字节量不可从命令回执观察，明确记UNKNOWN，不伪造submitted256。固定源不是对并发修改的文件快照；stage预期SHA和后续身份/独立SHA继续约束接纳。设备stage哈希最多256B、内部copy读取最多256B、internal哈希最多256B；预检head0对/dev/null无payload读取。

exact_process.py仍13077B/SHA f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d，command_response.py与T3字节相同。原进程/管道/stdin/source/wait强owner归还门不退回。额外主机合成源close异常也强持有原file，禁止下一I/O，CLI保留解释器等待，不二次close或用GC清零。超时不是远端归还证明，旧远端未知不清零。

## 有限本机证据

唯一main-001：**41项断言PASS，25条实际本机调用记录（24个自有Python假客户端＋1次Git sh -n语法检查）**。外层60s限时未触发，原检查解释器exit0。无历史全套重跑。evidence/local-check-results.json与check-attempt/result、checks.log绑定最终源码和原记录。

除了真实CRT读取，假客户端从固定argv文件以rb读取并以xb写入本机自有stage/internal文件；成功场景两个实际文件均完整0..255。原stdin始终0B，原25进程及管道均已返回，retainedLocalOwners0。覆盖stage26B但push exit0拒绝且copy0、base权限拒绝/已有stage冲突均在读取合成源和push前停止、失败保留、本机旧26B占位文件不变、独立SHA/UID/路径/长度错误、全局可写/内部错误UID、缺END与疑似旧tee拒绝、同attempt不能复用。所有9个生成脚本集中实际sh -n通过，未执行脚本中的设备命令。

假客户端仅为固定脚本响应模型，Android UID/mode/权限均为合成字段，没有模拟SELinux或执行真正run-as；本机实际二进制文件、CRT及本机进程归还证据不能升级为Android证明。实际ADB=0/device=0/真实媒体stat-read-hash=0/Gradle=0/下载=0。Git语法检查所需Windows同步对象访问已获自动审核允许，范围仅本机自有数据。

## 交付与后续

直接执行入口、前置准入和精确预算见D1_E4A_T4_BINARY_TRANSFER_PLAN_V1.0.md，当前executionAuthorized=false。下一批只有一次256B合成诊断，不补MP4/AVI、不运行产品方法、Binder、预算标记、手机、安装或播放。若实际通过，负责人可据该证据另定媒体恢复批次；本工具没有媒体入口。

seal：d1e4at4/evidence/binary-freeze.json；精确清单evidence/source-manifest.json；完整小包artifacts/D1-20261017-E4A-T4-source.zip。外部seal SHA、ZIP身份、数量与实际只读verify结果集中发送负责人，不向seal自引用。旧T3/T1/产品冻结保持只读，D1 NOT_PASSED/M0 NOT_STARTED/P0与历史FAIL保持。
