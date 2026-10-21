# D1 E4A-OWNER2 精确旧接收收尾报告 V1.0

日期：2026-10-17 09:46。依据D1_E4A_OWNER2_TESTER_REQUIREMENTS_V1.0.md，仅HA1Q6WXR、原PID7722/startTicks7571831。

**结论：BLOCKED_TESTER_SCRIPT_UNSUPPORTED_TOYBOX_AWK_NO_SIGNAL。一次控制命令核到原PID/comm/PPID/启动ticks仍相符，随后调用本机设备不提供的toybox awk失败，未完成全部前置证明。TERM尝试0，收尾未完成。该兼容性错误来自tester编写的执行脚本，不是产品失败、身份不符或新的权限拒绝。已停止，未替换命令重跑。**

## 1. 实际入口与范围

新包外目录 `docs/tester/D1_E4A_OWNER2_EVIDENCE`，attempt在设备访问前CREATE_NEW持久记录。使用T3固定shell -T -e none、原T1强关闭pump与原成功响应门，执行前核对应模块实际SHA。仅一次指定平板/run-as控制命令；无父/proc读取或其他设备查询。

合同固定值直接写入同一控制脚本：PID7722、comm tee、PPID7718、ticks7571831、四UID10221、完整NUL argv、原cwd、toybox exe、FD3准确归档链接以及FD目标/归档dev-inode。所有条件齐全才有一次TERM分支；没有用旧OWNER部分证据代替本批再核，也没有修改固定期望。

## 2. 已证与失败点

原控制命令stdout仅315B，输出原/proc/7722/stat；其中：

| 字段 | 本次实际值 |
|---|---|
| PID / comm | 7722 / tee |
| 状态 | S |
| PPID | 7718，仅读取子stat中的数值 |
| 启动ticks | 7571831，与原固定身份一致 |

控制脚本前置run-as UID/pwd比较已成功，之后进入子status UID提取。stderr完整51B，原错误：

```text
toybox: Unknown command awk (see "toybox --help")
```

原客户端exit127、首错PROCESS_NONZERO_EXIT，耗时1.875秒。脚本的`set -e`在UID提取失败处停止，未输出OWNER2_UIDS、完整再核或TERM标记。父权限前置已经按新合同去除，本次没有访问父/proc；失败与OWNER的父Permission denied不同。

这是我的执行脚本在命令选择上的可避免兼容性错误。没有依据该错误推定设备UID不符，也没有在本批把awk替换为其他命令重新取得身份继续。后续若另派，应先按设备已知工具集合核对执行脚本，优先采用已证可用字段读取或shell内建方案，并保持全部固定身份与信号门；本报告不构成补跑许可。

## 3. 未执行项目与信号

本次未完成子四UID、完整cmdline/cwd/exe/FD3、归档普通非symlink及dev-inode比较；旧OWNER的这些部分实证仍按原范围保存，不能被当作OWNER2全部前提已经成立。

原完整stdout无OWNER2_RECHECK_COMPLETE或OWNER2_TERM_ATTEMPT，且成功响应门因exit127拒绝。TERM0、KILL0、父/组/server/app/global信号0；没有信号后2秒观察、UID结束快照、加时或重复调用。不能报告该原owner已退出、僵尸或地址空间释放。其他旧远端资源继续UNKNOWN_NOT_CLEARED。

## 4. 预算与归还

metadata1/上限4；原stdout315B、stderr51B，均完整总量/SHA绑定、没有截留，低于单流16KiB和证据1MiB；实际目录总量见review-summary.json。未达单命令15秒或共同本机收尾2秒，没有terminate/kill升级。

原命令NOT_ADMITTED，但本机ownership=RETURNED：实际stdin关闭、source关闭、writer、两drain、原process wait及原线程均已返回，retainedLocalOwners=0。runner正常生成失败收据并退出，无本机在途Job或需保留handle；这不等于旧远端receiver或父资源已归还。

媒体内容/hash/传输、归档修改/删除/改名、cache/预算操作均0；FD目标stat因前序错误尚未执行。无手机/模拟器/安装/Gradle/Binder/产品/256B诊断/预置。没有自动下一批。

## 5. 证据交接

原01-conditional-term-and-original-observation.json、attempt/result、原stdout/stderr、audit-summary及manifest保持；audit只解析保存字节，不执行设备命令。完整结果主动交负责人，由负责人决定是否另派修正后的精确收尾方案，不自行补跑。

D1未通过、M0未启动，原P0/历史FAIL、OWNER权限边界及T3P/T1P/PREP-01未知保持；旧报告不修改。
