# D1 E4A-T2 远端执行定位工具独立复审报告 V1.0

日期：2026-10-17。依据 D1_E4A_T2_TESTER_REQUIREMENTS_V1.0.md。

**结论：SUPPORTED_FOR_SEPARATE_ONE_SHOT_256B_DIAGNOSTIC。未发现阻止另派一次固定 256 B 合成诊断的新问题。支持范围仅为指定平板的新诊断目录；不支持媒体补传或产品测试。当前设备诊断 NOT_RUN，须负责人另行正式派发。T1P 实际远端退出码、本机 SDK 的精确源码对应、旧 81,407 B 截断层次与前次远端所有权仍 UNKNOWN。D1 未通过，M0 未启动，P0/历史 FAIL 保持。**

## 1. 完整性与本轮范围

| 核验项 | 结果 |
|---|---|
| 外 seal SHA-256 | ce571e95cd294a46b2f852e2d07c7f91126d2b388eb6b27ddcc589e91010b09a |
| 源 ZIP SHA-256 | 9d4d2f6a65b93876fedf6df0257704beecb73cfc6d81928e349ed9a32237ac54 |
| 已检查的只读 verifier | PASS，295 源/297 不可变；精确归档成员/内容及最终语义证据一致；物理2,094,755 B/307文件、逻辑归档1,151,554 B |
| tester 独立哈希与记录审计 | PASS，见 D1_E4A_T2_EVIDENCE/audit.py、identity-and-recorded-model-audit.json |
| 原关闭证明 | exact_process.py 与 T1 字节相同，SHA f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d |
| 历史保持 | T1完整来源容器、T1P原报告/argv、E4A实际冻结身份保持；旧设备文件未访问或修改 |

本轮只读代码、归档及已有证据，另核对引用的公开上游固定源码。未执行 fake/模型重跑、ADB、设备、真实媒体 stat/hash/read、Gradle、补传或产品方法；无在途执行。网页核对不是本机 SDK 或设备观测。

## 2. 原 argv 与模型结论

独立阅读固定提交的 ADB commandline.cpp，shell 分支直接拼接参数；legacy exec 将后续参数再次交给 escape_arg，exec-in 只向远端复制输入，该分支不传播远端退出码。此差异支持不能把两种模式统一按预引用脚本处理，也支持不以 legacy 客户端0作为远端成功证据。[上游固定源码](https://android.googlesource.com/platform/packages/modules/adb/+/7c2fd99d6ec7e0d2d977ba03cecc82375af1baad/client/commandline.cpp)

生产 remote_command.run_as_argv 对 shell 的整个脚本预引用一次，legacy 则传原脚本。模型按上述拼接方式构造命令；fake_aosp_client 使用真实 Git sh 解析，run-as 仅替换为命令包装、并未切换 UID，toybox 前缀也仅映射本机工具。故它是有来源支持的本机执行模型，不是原 ADB 二进制或设备 daemon 实现。

已有原 argv 回放 trace 的 remoteShellExit=127、客户端0及目标未创建，修正 legacy 参数的模型 exit0且256B文件同字节，exec-out 模型不转发上传输入。这些结果分别留有原 trace 与本机进程记录。它们支持模式混用缺陷及诊断方向，**不能写成 T1P 设备实际返回127、SDK37.0.1已精确映射该提交，或 E4A-N 的81,407B已被解释**。SDK仅 source.properties 版本声明；精确对应仍未知。旧 T1P 实际事实继续是提交349,102B、客户端0、独立临时路径 ABSENT。

## 3. 一次诊断的生产准入

| 门槛 | 静态复核 |
|---|---|
| 固定通道 | features必须含shell_v2；实际流程所有远端命令和producer固定shell -T -e none。无 -x/-n、无PTY、无legacy fallback；仅模型辅助函数支持legacy，未被诊断生产流程调用 |
| 固定输入 | 随包payload256.bin确为bytes(range(256))，SHA40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880。无任意--source；实际source限定该文件，同FD预hash/stream沿T1 |
| 原上下文 | 原命令先输出实际UID/pwd，再验证10221及/data/user/0/com.videokit.app和files非symlink；角色不符保留原输出并停止，不改期望值补跑 |
| 旧资源观察 | 一次指定UID的PID/PPID/UID/ARGS快照，排除本shell自身后有cat/tee/sh/mksh或T1P线索就停止、不kill。未见匹配只作一次观察，priorRemoteOwnership全程UNKNOWN_NOT_CLEARED |
| 历史媒体 | 仅三个合同准确路径的无-L stat，并保留原rc/输出；没有内容打开、hash、跟随存在性探针、递归或通配扫描。失败不能写成ABSENT。此是上游默认lstat模型，OEM行为尚未验证 |
| 新对象 | 固定files/e4_diag_T2P_TABLET_20261017_once，mkdir独占；目标payload256.bin，nonce固定。已有目录/对象或symlink拒绝，不删除、不换名 |
| 原接收执行 | 完整stdout恰两行BEGIN/END；验证同nonce、准确字段集合、实际UID/pwd/path、同一个正PID，END计数256；原命令须成功结束、stderr空且T1本机资源已证返回 |
| 独立落盘 | 另一条命令再次验证上下文、普通非symlink文件、stat=256及完整SHA；PROOF各字段精确一致才准入 |
| 结果边界 | 通过只记SYNTHETIC_DIAGNOSTIC_VERIFIED_NOT_A_MEDIA_FIXTURE。submittedBytes快照、256预算、原接收计数及独立SHA分列；无完整BEGIN/END不能升级receiverExecution，更不能准入媒体 |

原 T1 close/源/wait/drain/线程强证明保持；实际stdin未归还仍强持原Job/对象和参数，下一IO拒绝。main的保留循环仅观察实际原事实，不执行设备IO或再次close；迟后归还不会恢复失败诊断。退出本机客户端或未见旧cat都不证明前次远端资源已归还。

## 4. 43项已有证据与限制

最终repair-004为43条断言、32条直接调用记录，全部原退出及本机owner归还已记录。MAIN及repair-001的FAIL、repair-002的39 PASS、repair-003的41 PASS及替代源码均保留；不累加断言，不把旧72/63重复计算。

已有证据包括原参数回放、修正legacy及exec-out方向，五种生产run_diagnostic场景：成功、缺END、缺shell_v2、疑似旧cat、独立SHA错。成功在真实本机UID/pwd与自有256B文件上成立，UID快照为合成数据；不冒充Android UID或设备证明。缺END/错SHA不准入且保产物，缺协议/旧cat在producer前拒绝，同证据目录拒绝第二次调用。

解析器对准确path、同PID及字段形状的拒绝获静态支持；现有显式变异断言主要覆盖UID、255计数及缺END，不能把这些写成每种path/PID错误均已单独执行。这个覆盖边界不改变精确比较生产代码的审查结果。tester本轮未重跑任何模型。

## 5. 可另派范围与条件

仅提议 **D1-E4A-T2P-TABLET-20261017，HA1Q6WXR，user0/app UID10221，一次新目录、一份256B合成输入**。固定命令入口、冻结源和唯一新包外证据目录在执行前再次校验；默认计划及JSON仍executionAuthorized=false，不能据本报告启动设备。

计划6个metadata命令加1个producer；代码metadata上限20、producer上限1，单命令15秒、共同收尾2秒；总日志1MiB，单原记录最多64KiB并在新调用前留收尾余量。stdout/stderr各16KiB计数门、各保留4KiB前缀，超过门最多额外读一个16KiB块即拒绝；不是无限输出或磁盘硬实时保证。

全成功预期主机合成数据读取512B（prehash+stream各256），payload256B，设备独立hash256B。历史媒体内容读写均0；三个准确lstat为metadata，不能另加旧媒体hash/目录扫描。不得查手机/模拟器、安装/重建、操作预算标记、补MP4/AVI、重跑Binder、执行产品正常/取消/故障。

无shell_v2、旧receiver线索、角色/权限不符、任一步错误/超时/缺标记/独立SHA不符即停止，保留新目录/文件及原返回，不换路、不补跑、不清理。UNKNOWN时保留原解释器和原owner并报告；即使诊断成功也不自动媒体预置或产品下一批。新诊断不能用来清零旧远端UNKNOWN，具体OEM兼容与实际双向全字节传输仍待另批原始证据。

本轮未发现新的静态阻断项。旧PREP-01/T1P未知结论及残件归档、E4A-N PASS1/BLOCKED9、所有旧报告保持；D1未通过、M0未启动、P0/历史FAIL不变。
