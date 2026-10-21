# D1 E4A-N 有限真机测试报告 V1.0

日期：2026-10-17 08:18。依据：D1_E4A_N_TESTER_REQUIREMENTS_V1.0.md。执行者：tester。

**结论：批次受阻，未达到正常链路验收。共 10 项：PASS 1、BLOCKED 9、FAIL 0；另有一次测试准备失败。平板独立 Binder 拒绝测试原返回 PASS。手机仍被系统禁用；平板媒体预置后的长度不符，按各复制一次及不重试要求停止媒体相关测试。D1 未通过，M0 未启动，历史 FAIL/P0/C14 待测状态均不改变。**

## 1. 冻结及现场准入

冻结候选 D1-20261017-E4A，freeze SHA-256 `a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d`。仅使用 final 目录双 APK；平板安装后对实际安装路径执行完整 SHA-256，分别匹配 app `e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f`、test `1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be`。

| 设备 | 身份/环境 | 准入与处理 |
|---|---|---|
| 手机 U4999DLBNRR89DOR | PDYM20，API 31，ARM64，user 0；/data 可用 98,507,676 KiB | enabled=2，lastDisabledCaller=com.oplus.athena；五项全部环境 BLOCKED。未启用、安装、清数据、复制媒体或运行测试。既有预算及缓存未完成可信读取，不推定为空。 |
| 平板 HA1Q6WXR | TB138FC，API 31，ARM64，user 0；app UID 10221，test UID 10222；/data 可用 86,093,056 KiB | enabled=0，旧双 APK 签名与最终证书一致。旧 app/test APK 45,420,951/2,432,101 B 已备份，旧 cache tar 26,750,976 B 已备份。正确 run-as 目录记录中无 e4a_outputs/e4a_output_budget/e4_fixtures；随后保留数据更新双 APK，各安装一次。 |

唯一有效设备清单包含上述两台及 emulator-5580；模拟器未操作。首次受限进程无法访问/启动 ADB 服务，未取得清单；提升连接权限后取得一次有效清单，不因设备缺失轮询。受限环境的只读状态命令失败记录仍保留。

平板稳定预算身份 `730a73e1-50e1-4198-a515-047104f00e31`，batch `D1-E4A-N-TABLET-20261017`。手机预定身份 `530758aa-9254-45ee-9142-771f4d176341` 与 batch `D1-E4A-N-PHONE-20261017` 未用于执行。不建立替代预算，不覆盖既有 anchor/marker。

## 2. 五项矩阵

| 精确方法 | 手机 | 平板 | 依据 |
|---|---|---|---|
| normalMp4SixRealFrames | BLOCKED | BLOCKED | 手机系统禁用；平板 basic.mp4 预置长度核验失败，未发起方法 |
| normalAviSixRealFrames | BLOCKED | BLOCKED | 手机系统禁用；平板准备流程 fail-stop，AVI 未预置，未发起方法 |
| capabilityDenialDoesNotOpenSource | BLOCKED | BLOCKED | 此方法也先构造并验证 basic.mp4 Fixture；残件不合格，不能把它当成能力拒绝用例执行 |
| binderRefusesBeforeBeginAndOversizeParcel | BLOCKED | PASS | 平板一次独立 metadata 方法，无 Fixture、BEGIN、Source/Sink 或 encoder；不存在前序 E4Session 未知资源，故可独立继续 |
| cancelRejectsWrongEpochOversizeAndLateFrame | BLOCKED | BLOCKED | 两项正常实证及 receipt 均未成立，未产生正常 receipt SHA，不启动取消方法 |

三个 quarantine 方法均 NOT_RUN，未注入故障。无重跑、整 class、压力测试或自动下一批。

平板 Binder 方法执行时间 08:16:34.913–08:16:38.226，runner 内计时 0.138 秒；原记录 `actual_remote_refusals=4 codec_started=false no_BEGIN=true`、`OK (1 test)`、`INSTRUMENTATION_CODE: -1`，命令退出 0。四个拒绝涵盖 BEGIN 前 FRAME、错误 epoch、旧 service instance，以及超过 Parcel 上限。原证据见 `D1_E4A_N_EVIDENCE/tablet/binder-instrumentation.txt` 和 `binder-result.json`。

## 3. 准备失败与保留现场

问题编号 E4A-N-PREP-01（测试基础设施，尚未归因产品）：主机授权源 `test_media/imgs_and_videos/videos/sample.mp4` 为 349,102 B，SHA `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9`；AVI 授权源大小 736,454,656 B，SHA `3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f`，二者主机核验均匹配冻结计划。

首次 `exec-in run-as ... tee files/e4_fixtures/basic.mp4` 返回 0、stderr 为空，但随后的实际 stat 只有 **81,407 B**。残件摘要 `a790f44fc3c6ff4579c83f57b42a4b31cd95278cca28fd4aa6b97fd295fd9695`，保留在原路径，不覆盖、不删除。当前证据不能确定截断发生的具体层次；传输返回 0 不等于完整写入。AVI 没有复制。依据本批每文件各一次预置约束，本轮未换传输方式补传，也未借用旧 fixture 路径或猜替代样本。

另一项执行脚本错误已限定处理：主 APK 安装原返回为 `Performing Streamed Install` 加 `Success`，准备脚本把完整文本严格等于 Success 作为条件，导致错误中断。核对原始成功返回及更新后版本后，只继续安装尚未安装的 test APK，没有重复安装 app、没有卸载或清数据。两个脚本及中断原记录保留。首次组合只读目录命令存在远端 shell 引号作用域问题，不能用其 Permission denied/目录不存在输出推断真实私有目录；平板已用直接 run-as ls 正确读取，手机因 disabled 已停止准入。

## 4. 实际预算与证据限制

| 项目 | 实际量/状态 |
|---|---|
| 主机授权媒体完整 hash | 736,803,758 B，两源各一次 |
| 主机预置输入读取/尝试提交 | basic.mp4 349,102 B；AVI 0；未以提交量冒充设备落盘量 |
| 设备新媒体落盘与只读残件 hash | 81,407 B；残件完整 hash 一次 81,407 B |
| 测试 Fixture 前后完整 hash | 0 B；唯一执行 Binder 方法不使用 Fixture |
| CPU Source 请求/真实样本/输出/输出 hash | 均 0；未启动 E4Session/encoder |
| 新预算 R/S、anchor、operation.pending | 无创建；结束 files 目录记录未出现 e4a_output_budget/e4a_outputs |
| 单方法原测试日志 | 小于 4 MiB；本批测试日志小于 32 MiB；旧 APK/cache 备份单列，不作日志或新输出预算 |
| 实际 codec/硬软/Image/帧 EOF/PTS/画面 | NOT_RUN，无编码实证 |
| PID/实例与资源峰值 | 唯一测试未输出 service PID/实例，不能编造；结束 ps 未见 VideoKit 进程，未取得执行期间峰值 |

唯一方法的完整终止返回和结束 ps 支持没有该 instrumentation 在途；未产生原 source/sink/callback/CONTROL/encoder owner。`dumpsys activity instrumentation` 在该系统不支持，原错误保留，不用它证明无在途。没有未知编码资源或需要强制回收的任务；81,407 B 不合格 fixture 与历史文件原样保留。

## 5. 交接结论

本批结束，不补跑、不自动下一批。负责人需先审阅 E4A-N-PREP-01 的传输证据；任何修正传输工具及重新预置都须另行正式派发并明确如何保留本轮残件与次数。本报告未将测试准备失败记作 codec 产品失败，也未将 Binder 单项通过扩展为正常媒体链路、资源回收或信号门通过。正常 receipt 准入为 NOT_ADMITTED，取消继续 BLOCKED。

证据目录：`docs/tester/D1_E4A_N_EVIDENCE`。报告完成后主动交负责人；原 E4A 静态审查结论、旧 E4/C14 冻结及历史信号 FAIL 全部保持。
