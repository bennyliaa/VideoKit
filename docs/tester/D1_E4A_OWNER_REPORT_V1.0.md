# D1 E4A-OWNER 旧接收归属核查及条件收尾报告 V1.0

日期：2026-10-17 09:41。依据 D1_E4A_OWNER_TESTER_REQUIREMENTS_V1.0.md，仅平板HA1Q6WXR、PID7722及准确父7718。

**结论：BLOCKED_PARENT_PROC_PERMISSION_DENIED_NO_SIGNAL。已取得7722的启动标识、UID/cmdline/cwd/exe及四项FD元数据；FD3指向合同中的归档残件。随后读取父7718的/proc/stat被系统拒绝，按权限拒绝即停止规则结束。未发送TERM，未提权或绕过限制；原远端所有权未清零，定向收尾没有完成。**

## 1. 范围和原命令

本批新证据目录 `docs/tester/D1_E4A_OWNER_EVIDENCE`，attempt.json在设备访问前CREATE_NEW持久保存。使用T3固定shell -T -e none及同目录exact_process/command_response，原T1 pump SHA f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d已核，不修改冻结工具。

实际仅1次metadata远端命令，先验证run-as实际UID10221及pwd /data/user/0/com.videokit.app，再依序读指定PID的/proc身份与FD链接/fdinfo。只读取元数据，不打开媒体或pipe内容；无父进程递归/全局扫描。脚本限制最多16个FD候选位置：7722的0–12及7718的0–2；本次父身份阶段失败，实际只取得7722的0/1/2/3共4项。

原命令约09:39:10执行，客户端记录耗时0.625秒，原exit1；完整stdout1210B、stderr41B，无截留。原stderr为：

```text
cat: /proc/7718/stat: Permission denied
```

T3完整成功响应门正确拒绝该非零/错误响应；原partial stdout和原错误仍完整保留。Python runner输出NOT_PROVEN_NO_SIGNAL后正常结束，不能以runner退出0误报归属/收尾通过。

## 2. 已观察的7722身份

以下均来自同一次原返回，报告阶段未追加设备命令：

| 元数据 | 原事实 |
|---|---|
| PID/comm | 7722 / tee |
| PPID | 7718 |
| /proc/stat启动ticks | 7571831，未转换为墙钟创建时间 |
| 状态 | S，status显示sleeping；未取得等待原因 |
| real/effective/saved/fs UID | 10221 / 10221 / 10221 / 10221 |
| cmdline原NUL分隔argv | `tee`、`files/e4_fixtures/basic.mp4`；保留原hex |
| cwd | /data/user/0/com.videokit.app |
| exe链接 | /system/bin/toybox |

cmdline、UID、cwd及输出FD线索与本项目旧测试receiver一致，不能由这些字段单独确定原批次、导致截断的具体层次或远端父资源生命周期。本批没有读CLK_TCK、额外进程或相关产品状态来扩展归因。

## 3. FD与归档残件

| FD | 原readlink目标 | fdinfo pos | flags（原八进制文本） | mnt_id |
|---|---|---:|---|---:|
| 0 | /dev/pts/0 | 0 | 0400002 | 17 |
| 1 | /dev/pts/0 | 0 | 0400002 | 17 |
| 2 | /dev/pts/0 | 0 | 0400002 | 17 |
| 3 | /data/user/0/com.videokit.app/files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep | 81407 | 0400002 | 74 |

FD3链接已观察到指定归档路径，说明当时该进程持有指向归档残件的FD。**pos81407是文件描述符位置，不是本轮文件长度或SHA证明。** 本次fdinfo未提供ino；父权限失败发生在后续目录/归档inode核验之前，所以当前归档inode及内容未取得，也没有hash确认旧内容继续不变。

FD0/1/2为/dev/pts/0是本次元数据事实；不能据此确定谁仍持有终端另一端、进程等待的是何事件，或直接判定历史81,407B截断根因。没有cat任何/proc/…/fd对象内容，没有读取终端或媒体字节。

## 4. 未证项目与未执行信号

父7718在stat阶段Permission denied：未取得它的启动ticks、UID、cmdline、cwd/exe或FD信息，未继续其他父路径；不推定父为shell/root/adbd，也不借其他UID、root或SELinux绕过来补齐。

完整父身份及后续归档/目录inode检查未完成，条件准入文件没有生成。同原控制命令的信号前PID/ticks/UID/cmdline/输出FD再核未执行，TERM尝试0、KILL0、父/组/server/app信号0。原脚本中包含的条件控制分支未被派发给设备；没有以静态代码存在冒充实际信号。

TERM后的2秒观察及结束UID快照均NOT_RUN，因为权限拒绝后已停止。没有轮询、反复信号、KILL升级或force-stop；不能写成“7722已结束”或“全部历史owner已清”。原远端状态继续UNKNOWN_NOT_CLEARED。

## 5. 预算与资源

metadata1/上限12，实际FD元数据4/上限16；未达到单命令15秒或共同本机收尾2秒。stdout1210B、stderr41B，各原字节完整长度/SHA绑定；证据低于1MiB，实际总量见review-summary.json。媒体内容、pipe内容、传输及文件hash全部0；本批没有修改/删除/重命名归档残件、媒体、cache或预算。

原客户端exit1且NOT_ADMITTED，但ownership=RETURNED：原stdin实际close、source关闭、writer、两drain、原process wait及原线程均已返回，retainedLocalOwners=0。没有本机未知Job或需保留会话handle；这不等于旧远端7722/7718及其他资源归还。

证据：01-identity-and-fds.json、attempt/result、原stdout/stderr文本、audit-summary和manifest。audit仅对保存字节复核摘要并规范CRLF进行报告解析，未重新设备取证；原raw字节不改。未发送新256B诊断、不预置、不安装/Gradle/Binder/产品、不查询手机模拟器。

## 6. 交接结论

定向收尾因平台权限边界受阻，本批不扩大权限或自行下一批。负责人需基于已证子身份/归档FD及父元数据拒绝，决定后续合法方案；本报告不是新的signal或恢复诊断/预置许可。设备原现场保持，不能假定关闭本地client已释放旧receiver的FD。

D1未通过、M0未启动，原P0/历史FAIL、T3P阻断、T1P/PREP-01未知及旧报告保持。完成后主动报告负责人。
