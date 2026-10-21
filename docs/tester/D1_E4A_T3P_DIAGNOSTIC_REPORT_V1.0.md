# D1 E4A-T3P 唯一合成诊断报告 V1.0

日期：2026-10-17 09:34。批次 D1-E4A-T3P-TABLET-20261017。依据 D1_E4A_T3P_TESTER_REQUIREMENTS_V1.0.md。

**结论：NOT_ADMITTED / POSSIBLE_PRIOR_RECEIVER_STOP_NO_KILL。features修复已在本次真实响应上通过，原UID/pwd确认通过；一次UID进程快照观察到旧路径接收线索，触发合同停止门。未启动256B producer、未创建诊断目录，不重跑、不kill或修改设备文件。这不是codec产品失败，也不是本次新增解析缺陷。**

## 1. 冻结与唯一入口

执行前只读核验T3外seal `4fbeef4948c8615e406b0e3a778d1c499c7a8c6fc133dc75822972a5a38e6628`、ZIP `eb7a66f8e693efb9c1256a52e32a2d978154cfb122cf0dd7aabb416c9c1c084c`，57源/59不可变及精确归档身份PASS。固定新Python脚本入口从T3 tools目录导入冻结模块，未修改JSON/source：

`diagnose_once.py --execute --formal-batch D1-E4A-T3P-TABLET-20261017 --evidence-dir D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T3P_EVIDENCE`

09:33:00在新包外目录建立CREATE_NEW attempt并完成原结果收据。未复用旧T2P入口、nonce、目录或次数。全部三条客户端命令仅指向HA1Q6WXR，固定shell -T -e none；没有全设备清单、手机或模拟器访问。

## 2. 实际执行及停止证据

| 原阶段 | 结果与范围 |
|---|---|
| features | PASS：原220B CRLF输出，SHA05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce，完整未截留，含shell_v2，生产解析进入下一阶段 |
| context | PASS：原输出UID10221、pwd /data/user/0/com.videokit.app；同命令对UID/pwd及files目录非symlink验证成功，exit0 |
| prior-uid-processes | 原命令exit0、完整474B stdout；发现符合停止条件的同UID tee项，整体诊断停止 |
| 三历史no-L stat | NOT_RUN，不追加历史路径访问或内容确认 |
| 新诊断目录与256B producer | NOT_RUN，未创建/写入 |
| BEGIN/END及独立SHA | NOT_RUN，无接收或落盘准入证明 |

原快照关键行如下，来自保存的原stdout字节，不是重复查询：

```text
E4T2_PS|E4T3P_TABLET_20261017_ONCE|self=13663
PID   PPID   UID   ARGS
7722  7718   10221 tee files/e4_fixtures/basic.mp4
```

快照还含本次shell PID13663及其toybox ps PID13667；原解析正确排除自身，再由PID7722/PPID7718/UID10221和`tee files/e4_fixtures/basic.mp4`命中旧接收线索。原快照SHA为 `1c2ebe2c936704b565c98763fe7034ffa572e9fa0c9650755ae2bcb31fd5b840`。

该命令行与旧N接收命令形式一致，但本批没有采集PID创建时间、状态列、FD或父进程详情，**不能确定其原始批次、当前等待原因、文件是否仍打开、是否正在写入，或把它直接认定为截断根因**。原快照只能证明当时存在该进程项并满足合同阻断条件。没有kill、等待其退出的轮询或再次快照。

T3P新身份由nonce E4T3P_TABLET_20261017_ONCE区分；E4T2_PS/CONTEXT是沿用协议前缀，不是复用T2P。原context完整85B stdout见01-context.json，三份原stdout已按原总量/SHA复核并还原为文本。

## 3. 原资源及实际预算

metadata实际3/上限20，producer0/上限1；host合成source prehash/stream读取0B、payload提交0B、独立设备hash0B、真实媒体内容0B。三历史lstat次数0，新目录创建0；未将计划512B/256B计作实际流量。旧残件归档及其他媒体本批未访问或修改，不能据此确认它们当前内容仍与历史hash相同。

三客户端原退出均0，记录耗时分别0.063、0.156、0.203秒；均未触及15秒或共同2秒收尾，无terminate/kill。stdout分别220/85/474B，合计779B，stderr全部0；未截留，低于各16KiB门及4KiB前缀。包外证据低于1MiB，实际总量见review-summary.json。

三份原客户端的stdin实际close、source close、writer返回、两drain关闭、原process wait及线程归还均通过T1/T3门，ownership=RETURNED、retainedLocalOwners=0。入口因诊断拒绝退出1；没有本机保留Job或在途会话handle需要继续持有。

**旧远端状态仍UNKNOWN_NOT_CLEARED，并新增这一次可见接收线索；不以本机三客户端归还清零远端未知。** 未声明旧receiver已经结束，也未以重启工具、补传或kill消除阻断。

## 4. 后续交接

本批正确执行了前置停止门，完整合成诊断尚未完成。负责人需先审阅PID7722/PPID7718/UID10221的原线索，另行决定如何确认归属及合法处理原资源；本报告不授权继续检查、关闭进程、恢复媒体或重复诊断。即使producer0，T3P唯一入口已消耗，不能自行改期望、换名/换路或补跑。

证据目录 `docs/tester/D1_E4A_T3P_EVIDENCE`：原attempt、00-features、01-context、02-prior-uid-processes、result；audit.py只解析原收据，生成原stdout文本、audit-summary和manifest，没有追加设备访问。报告完成后主动交负责人。

手机/模拟器/安装/Gradle/Binder/预算标记/MP4AVI/产品正常取消故障均0，未自动下一批。旧T2P结果、T1P/PREP-01未知及E4A-N PASS1/BLOCKED9保持。D1未通过、M0未启动，P0/历史FAIL/C14待测不变。
