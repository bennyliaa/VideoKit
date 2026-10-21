# D1 E4A-T3R 收尾后有限合成诊断报告 V1.0

日期：2026-10-17 09:58。依据D1_E4A_T3R_TESTER_REQUIREMENTS_V1.0.md。

**结论：NOT_ADMITTED_RECEIVER_EXIT1_BEGIN_ONLY。一次合成producer已执行：主机prehash/stream及实际提交均为256B、摘要正确；原远端输出准确BEGIN，随后原通道exit1、stderr0，缺少END。未取得接收计数或独立stat/SHA，落盘是否完整仍UNKNOWN。已停止，不重跑/换路/加时/清理；不是媒体或codec产品失败。**

## 1. 新授权与内部字段

OWNER3准确原PID收尾后现场实质变化，负责人明确允许新的独立执行批次复用未改T3入口及此前未创建目标。身份区别如下，不能以内部字段声称全历史仅执行一次：

| 项目 | 精确值 |
|---|---|
| 本次外部执行批次 | D1-E4A-T3R-TABLET-20261017 |
| 冻结工具内部formal-batch/result.batch | D1-E4A-T3P-TABLET-20261017 |
| 复用内部nonce | E4T3P_TABLET_20261017_ONCE |
| 复用此前未创建目录/目标 | files/e4_diag_T3P_TABLET_20261017_once/payload256.bin |
| 本次唯一新包外证据 | docs/tester/D1_E4A_T3R_EVIDENCE |

旧T3P为metadata3/producer0，未创建目录；旧attempt/result和报告不覆盖。复用依据是本次书面外部授权，不是绕过旧失败次数。执行前只读核T3 seal `4fbeef4948c8615e406b0e3a778d1c499c7a8c6fc133dc75822972a5a38e6628`、ZIP `eb7a66f8e693efb9c1256a52e32a2d978154cfb122cf0dd7aabb416c9c1c084c`，57源/59不可变及归档PASS，准确直接运行冻结CLI，未改源码/JSON。

## 2. 实际阶段

本次仅HA1Q6WXR，约09:55完成。固定shell_v2与shell -T -e none，无fallback；5个metadata加1个producer：

| 阶段 | 原结果 |
|---|---|
| features | exit0，220B完整CRLF；shell_v2精确准入 |
| context | exit0，实际UID10221、pwd /data/user/0/com.videokit.app，files角色门通过 |
| 一次UID快照 | exit0，421B原输出；未命中其他旧receiver停止条件，仅一次观察，不清全部旧UNKNOWN |
| 三历史准确no-L stat | exit0，保留三个原rc/输出，未读内容/hash |
| 新诊断目录 | exit0，87B DIRECTORY原标记路径匹配，确认本次独占创建 |
| 唯一接收 | exit1，PROCESS_NONZERO_EXIT；完整152B stdout仅BEGIN，stderr0；NOT_ADMITTED |
| 独立stat/SHA | NOT_RUN，因producer失败未继续 |

唯一接收的原BEGIN为：

```text
E4T2_BEGIN|E4T3P_TABLET_20261017_ONCE|uid=10221|pid=16643|pwd=/data/user/0/com.videokit.app|path=files/e4_diag_T3P_TABLET_20261017_once/payload256.bin
```

这提供实际接收脚本开始、原UID/pwd/PID/目标声明的部分证明；BEGIN在角色检查与写入之前输出，**不能单凭它确认cat已执行、文件存在、接收256B或全部资源已归还**。原完整输出无END，不能升级为完整接收执行证明。工具正确保存原非零首因并停在ORIGINAL_COMMAND_NOT_COMPLETE_single-receiver，未将主机提交量当落盘量。

## 3. 数据、原文件及失败边界

冻结合成source为0..255全字节，256B；本次同FD prehash与stream读取各256B，实际submitted256B，源/提交SHA均为 `40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880`。flush、原stdin/source close、writer/drain/wait均返回；只记录原非零退出错误，未记录输入未完成、源摘要不符或关闭错误。总量不用于推断每次write的返回长度。

原通道exit1且无stderr不足以确定BEGIN之后具体哪条检查/写入/stat/计数子步骤失败。本批没有追加probe或/proc查询，也没有读取可能的新诊断文件；实际落盘长度、内容SHA、END计数均未知。不能猜为26B、81,407B、0B或256B，不能直接归因为旧截断问题或某个Windows/ADB层次。

三条允许的历史lstat原事实：

| 合同准确路径 | 原rc/元数据 |
|---|---|
| files/e4_fixtures/basic.mp4 | rc1，原stat输出No such file or directory；保留原错，不替换为自造ABSENT标记 |
| files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep | rc0：UID10221、size81407、inode21416、mode81b6、mtime1792196186 |
| files/e4_fixtures/.basic.E4AT1P_TABLET_20261017_once.part | rc1，原stat输出No such file or directory；保留原错 |

归档元数据与此前准确inode线索相容，不代表当前内容摘要仍为历史值；本次媒体内容/hash0。没有恢复或改名旧残件，也未删改旧临时或归档。本次新诊断目录已经创建，目标是否存在未独立证明；目录及任何可能产物原样保留，不能再按“未创建目标”假设自行复用此入口传输。

## 4. 实际预算与所有权

| 项目 | 实际 |
|---|---:|
| metadata / 上限 | 5 / 20 |
| producer / 上限 | 1 / 1 |
| 主机合成source读取 | 512B |
| 主机提交payload | 256B，非落盘证明 |
| 独立设备新内容hash | 0B |
| 真实媒体内容读写/hash | 0B |
| 历史准确lstat命令 | 1，含三固定叶路径 |

六原客户端耗时0.078/0.156/0.157/0.218/0.157/0.156秒，未达15秒/共同本机收尾2秒，未terminate/kill或延长时限。stdout220/85/421/387/87/152B，stderr全部0，完整未截留；证据低于1MiB，实际总量见review-summary.json。

所有六份原记录本机ownership=RETURNED，实际stdin/source/writer、两drain、原wait与线程归还；retainedLocalOwners=0，runner以诊断拒绝exit1结束，无本机在途Job或需保留handle。原shell_v2通道非零和本机归还不等于完整接收/落盘及全部历史远端owner清零；PID16643只有BEGIN部分证明，未追加OS生命周期取证。旧远端priorRemoteOwnership仍UNKNOWN_NOT_CLEARED。

## 5. 交接

原attempt/result、六调用、完整stdout/stderr、audit-summary及manifest均保留。审计只解析已保存字节，未追加设备或payload读取；旧T3P与OWNER3报告完整SHA保持。OWNER3限定原receiver结束结论不因本批失败回退，也不扩大成全局资源清零。

本批结束，主动交负责人。后续如需定位BEGIN后的具体失败步骤或独立核新诊断文件，须另行准确授权；本批不自行补查、修改脚本重跑、换目标或继续MP4/AVI。无手机/模拟器/安装/Gradle/Binder/预算标记/产品方法或自动下一批。D1未通过、M0未启动，P0/历史FAIL及原未知保持。
