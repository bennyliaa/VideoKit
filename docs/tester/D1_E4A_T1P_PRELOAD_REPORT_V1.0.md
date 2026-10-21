# D1 E4A-T1P 平板唯一预置报告 V1.0

日期：2026-10-17 08:54。批次 D1-E4A-T1P-TABLET-20261017；依据 D1_E4A_T1P_TESTER_REQUIREMENTS_V1.0.md 及已审 T1 计划。

**结论：预置未通过。MP4 唯一 attempt 为 NOT_ADMITTED，AVI 为 BLOCKED，未读取/传输。主机完整提交及客户端 exit0 后，独立临时件 probe 返回 E4AT_ABSENT；不能宣称落盘成功。旧 81,407 B 残件已无覆盖归档且前后字节身份一致。已停止，不补传、不换路、不加时、不执行产品测试。具体失败层次仍 UNKNOWN；不是 codec 产品失败。**

## 1. 精确工具与现场

T1 外 seal `954288092916e5281c7a50183adc9041e82c05d16cfe6fd6cd5013fb75139c0f`，ZIP `0ed267e6665b481c0858492413b56a6b0ac79c257765e063ba37ee2521cf08bb`；运行前逐项验证 43 不可变文件身份。实际导入的 exact_process.py、fixture_transfer.py 均为 `docs/coder/d1e4at1/tools` 对应文件；冻结 JSON 未修改，execution_authorized=True 仅由本次外部正式需求授权。

全部命令仅指向 HA1Q6WXR，无全设备清单、手机或模拟器操作。一次必要准入确认：TB138FC、API31、ARM64、user0、app UID10221、启用，run-as id/pwd 正确，files 与 files/e4_fixtures 非 symlink、目录可读写；toybox mv/stat/sha256sum 帮助及 shell noclobber/cat 空输入检查通过。未用预检替代实际传输验证。

实际安装路径 SHA-256 仍匹配 final E4A：

| 包 | SHA-256 |
|---|---|
| com.videokit.app | e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f |
| com.videokit.app.test | 1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be |

准入时可用空间 88,146,935,808 B，核门为新 payload 736,803,758 B 加 268,435,456 B 余量；旧 APK/cache/其他 fixture 没有删除或覆盖。正确范围的目录记录及 NO_PRIOR_PENDING 已保存，不创建或修改产品预算。

## 2. 唯一 MP4 attempt 与实际结果

08:52:40.817 开始 `E4AT1P_TABLET_20261017_basic_once`，08:52:41.882 批次收据结束。所有收据都在新包外 `docs/tester/D1_E4A_T1P_EVIDENCE`，CREATE_NEW attempt 在修改远端之前持久保存。

| 环节 | 原证据 |
|---|---|
| 原残件 | files/e4_fixtures/basic.mp4，81,407 B；SHA a790f44fc3c6ff4579c83f57b42a4b31cd95278cca28fd4aa6b97fd295fd9695 |
| 保留归档 | files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep；无覆盖 mv -n 后独立 stat/SHA 与改名前相同，原固定名已证不存在 |
| 唯一临时路径 | files/e4_fixtures/.basic.E4AT1P_TABLET_20261017_once.part，producer 前独立 metadata 证明不存在 |
| 授权源 | test_media/imgs_and_videos/videos/sample.mp4，349,102 B；同原只读 FD prehash 与流式提交 SHA 均为 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 |
| producer 主机证明 | 实际 streamRead/submitted 各 349,102 B；flush、原 stdin close、source close、writer、两 drain close、原 process wait/exit 均返回；exit0，stdout/stderr 均0 B，无 stop/kill，无异常；客户端记录耗时0.093秒 |
| 独立临时件 probe | 单独原命令退出0，完整 stdout 仅 E4AT_ABSENT；没有取得临时件长度/SHA |
| 最终准入 | NOT_ADMITTED / INDEPENDENT_LANDED_LENGTH_OR_SHA_MISMATCH；没有执行发布 rename、最终文件 hash 或 FIXTURE_ADMITTED |

本次不是“又测到 81,407 B 新短件”：**新临时件在独立检查时未见**。81,407 B 仅指已验证归档的旧残件。不能把主机 submittedBytes、客户端 exit0 或无 stderr 改写为 landedBytes，也不能把未见临时件推断成“从未发生任何远端 IO”。原固定名最后实际缺失证明在 producer 前；失败后没有追加设备巡检或猜测新的最终状态。

## 3. AVI 与实际读取预算

AVI `E4AT1P_TABLET_20261017_avi_once` 未消耗、未建 attempt；源未 stat/open/hash，producer未启动。既定最终路径与 T1 临时名均未由本批操作，不能计为已经准备完成。

| 项目 | 实际量 |
|---|---:|
| 主机 MP4 prehash | 349,102 B |
| 主机 MP4 同 FD stream 读取 | 349,102 B |
| 主机真实媒体读取合计 | 698,204 B |
| producer 提交 payload | 349,102 B；不是设备落盘证明 |
| 原残件归档前后设备完整 hash | 162,814 B |
| 新临时件/最终件内容 hash | 0 B；临时件不存在，未进入内容 hash |
| AVI 读取/传输/hash | 全部0 B |
| 现场安装 APK 完整 hash | 13,309,805 B，独立于 fixture 内容预算单列 |

以上均低于原 payload/host读取/设备 hash 上限。未延长 MP4 60秒、metadata/hash 120秒或共同 cleanup2秒；AVI300秒未使用。源码/收据/metadata 不计入媒体流量；整个包外证据当前远低于8MiB，最终总量见 review-summary.json。归档同目录改名不增加第二份 payload，旧残件保留81,407 B；没有以“未见新临时件”声称完整远端写入峰值已知。

## 4. 原资源与停止状态

一次准入15个客户端命令、MP4协议8个客户端命令，共23份原调用记录。所有记录的原 process/writer/source/stdin/stdout/stderr 关闭及线程归还均符合 T1 条件；retainedOriginalProcessOwners=0，原 runner 正常退出，无本机在途 Job/保留会话 handle。没有关闭异常或二次 close/重试。

**本机客户端与 pipe 的归还只证明本机资源，不证明远端接收进程完整生命周期或文件写入完成。** 远端未准入，失败层次未定，现场保持供负责人审阅；没有通过杀 server/设备进程、退出 UNKNOWN 解释器或重新启动脚本洗许可。没有本机未知 owner 需要保留原解释器，也没有宣称远端未知已清零。

手机/模拟器、安装/重建、Gradle、Binder、产品正常/取消/故障执行均为零。MP4失败后立即 break，没有读 AVI、删除残件/临时件、回滚归档、换路补传或自动下一批。

## 5. 证据与交接

原 attempt/result/events、basic.mp4-backend-logs.json、15项现场原结果、batch-result.json 均保存；`audit-summary.json` 与 `evidence-manifest.json` 为仅解析现有收据的复核，不发起额外设备/媒体访问。下一步须负责人审阅本次真实“完整主机提交/exit0、临时件未见”证据后另行安排排查，不能复用本批次数自行补传。

旧 PREP-01 UNKNOWN 与 E4A-N PASS1/BLOCKED9 不改，旧残件以合同指定归档方式保留。D1 未通过、M0 未启动，原 P0/历史 FAIL/C14 待测保持。报告完成主动交负责人，预置成功条件尚未成立，任何产品测试继续未授权。
