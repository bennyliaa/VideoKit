# D1 E4A-T 传输工具独立复审报告 V1.0

日期：2026-10-17 08:37。依据 D1_E4A_T_TESTER_REQUIREMENTS_V1.0.md，审查完整冻结 D1-20261017-E4A-T。

**结论：REQUEST_CHANGES_BEFORE_REAL_PRELOAD。发现 1 项 P1：stdin 关闭未证实时仍可释放原 Job 并放行下一调用。工具的独立落盘校验等改进获得静态及已有本机证据支持，但本轮不建议安排实际预置。真实 ADB 传输是否成功仍未验证，PREP-01 的截断层次仍 UNKNOWN。**

## 1. 冻结与证据

| 核验项 | 结果 |
|---|---|
| seal SHA-256 | 3b650fd8f14956216e9fa5c9f43ebe916e5b832980a6e450515275e09425902a |
| 源 ZIP SHA-256 | faeec9c657ae813e85ed23a042eeb900f9b26bb76cced52f4bfe1d9196fa6cdc |
| 已检查的只读 package_tools verify | PASS，151 源文件、153 不可变文件、精确归档成员与逐项哈希一致；读取物理 6,656,584 B/165 文件、归档逻辑 6,342,820 B |
| tester 独立归档/哈希检查 | PASS；见 D1_E4A_T_EVIDENCE/audit.py、identity-and-finding-audit.json |
| 产品及原报告 | E4A freeze a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d 保持；E4A-N 报告 SHA 37530ab70ade2b7bad5e5b144d3a9cab51b0a9986649c9172c996a237c7a250d 保持 |
| 已有本机结果 | repair-001 72 断言、52 调用记录，其中 51 个实际自有 fake 子进程 + 1 次源预检拒绝；未将 MAIN 66 条叠加 |

本轮只读源码、归档及已有证据；未导入生产 pump 执行故障，未运行 selfcheck/fake 重新评测，ADB、设备、媒体 stat/读取/hash/复制、Gradle、预置及 Binder 重跑均为零。已有本机数据读取 6,480,444 B 属开发自有测试数据，不能计为真实 AVI 或设备传输。没有新增依赖或产品 APK。

## 2. 阻断问题 E4AT-F01（P1）

位置：`docs/coder/d1e4at/tools/exact_process.py:62、76–78、110–115、136`。

触发路径是原 writer 的 `process.stdin.close()` 抛出异常：111 行未设置 stdin_closed，112 行记录 STDIN_CLOSE_UNKNOWN；随后原 source 关闭成功、writer 实际返回。若原子进程已退出、stdout/stderr 关闭和所有原线程也已返回，62 行的 returned 谓词仍为真，因为它没有要求 stdin_closed。

因此同一份结果会同时出现：

| 字段/动作 | 当前静态结果 |
|---|---|
| stdinCloseReturned | false |
| errors | 含 STDIN_CLOSE_UNKNOWN |
| status | NOT_ADMITTED |
| ownership | **RETURNED** |
| _release_if_returned | 从全局 _OWNERS 删除原 Job |
| 下一次 collect/transfer_file 的 _reserve | 可以接纳 |

这条路径不会误发布当前 fixture，因为 status 仍被拒绝；但它会把未证实关闭的原 stdin owner 从全局强保留集合移除，后续调用可以复用工具准入。结果字典没有保留实际 process/stdin 对象，函数返回后不能用错误文本代替原对象所有权。这与交付要求“原 pipe 关闭未证实必须 UNKNOWN_RETAINED、强留原 Job/参数/source/process 并阻止后续调用”不符。

这是静态谓词与真实生产调用链可直接确认的问题；**本轮没有注入关闭故障，也不声称设备复现**。当前自检检查了正常 close 返回、子进程失败及实际 wait/drain，但没有注入原 stdin close 抛出异常，所以 72 PASS 不能排除此分支。

建议修复：原子进程存在后的 ownership 归还判断应要求 stdin 的实际关闭已证实；关闭异常保留原 Job/process/stdin/参数，不二次 close、不因 exit0 或线程结束推断成功。补充有限、隔离的本机证据覆盖关闭抛错及原 close 尚未返回两种状态，确认 UNKNOWN 强留和下一准入拒绝；再以新完整工具冻结交审。不要改动本冻结或借修复许可执行设备。

## 3. 已获支持的部分及边界

| 项目 | 独立审查结果 |
|---|---|
| 二进制与短写 | shell=False 参数数组、无缓冲二进制管道；同一只读 source FD 先完整长度/SHA、再归零转发。write_all 仅累计实际正返回，短正写继续原余量，0/None/越界/异常拒绝。流式字节与摘要再核；不是以 copyfileobj 的通常行为猜根因。 |
| 并发 stdout/stderr | 两个原 drain 持续消费，各计总量和摘要、只保留 64 KiB 前缀；默认各 1 MiB，超额最多再读一个 16 KiB 块后拒绝。原 writer、drain、source 与原进程 wait 大部分状态均记录。超时只停止自有客户端，不杀 server/设备进程；未知不等于远端已终止。stdin close 漏洞另列 F01。 |
| exit0 短件拒绝 | producer 结束只标 PROCESS_IO_COMPLETE_ONLY；生产 workflow 再通过独立进程 stat/SHA 核临时件，长度/摘要不符不发布。已有 81,407 B 截断、同长度错 SHA、自有超大件先长度拒绝等证据直接走生产 workflow；它们不能证明真实 ADB 根因或实际修复成功。 |
| 引号与路径 | run_as_argv 对整个脚本作 POSIX literal quoting，使分号留在同一个 run-as sh -c 作用域；host 仍参数数组。远端仅允许 files/e4_fixtures 的受限 basename，拒绝点目录、引号和分号注入；leaf 普通文件/非 symlink 检查存在。父目录实际 UID/pwd/非 symlink 是后续正式预检的必要条件，不能省略；不提供同 UID 并发恶意替换防护。 |
| hash 范围 | 内容 probe 先 stat，再按审定 cap 判断，超大不进入 sha256sum；碰撞存在性仅 metadata。真实 sha256sum 不提供打开后硬字节限制，故字节预算依赖合作式稳定普通文件及预检；发生增长或变化只能拒绝，不能声称恶意并发情况下也有强读取界。 |
| 保留与发布 | attempt CREATE_NEW 并 flush/fsync 在远端修改之前；原残件长度/hash 匹配才同目录 mv -n 归档，再独立核同字节与原名消失。新临时名 noclobber cat 接收，独立核验后 mv -n，最后核最终件与临时名消失。碰撞、未知或半完成不删除、回滚或换名补跑。该合作式发布不等于远端掉电持久性证明或强权限沙箱；Android toybox 支持及 rename 行为仍需另批首次实证。 |
| 安装提示解析 | 只解析已结束响应的 exit0、空 stderr、末独立行 Success 及白名单 banner；实际旧记录可接受，不把全文等于 Success。函数不安装，也不触发重装。 |

主机普通 source open/read 和预 hash 没有独立可强制中断的硬期限；原进程期限从 Job 创建计起，不能当作不返回 OS 调用的绝对上界。超时杀掉本地 adb 客户端也不能推断远端接收进程及文件已经归还；后续实际执行仍须保留原现场，不将本机 owner 状态写成设备 owner 状态。

## 4. 后续预置计划审查

计划仍 executionAuthorized=false。只面向平板 HA1Q6WXR，产品双 APK 不重装，手机不查询，已 PASS Binder 不重跑，也不执行正常/取消/故障方法。原 81,407 B 残件必须按固定摘要先后核验并无覆盖归档；MP4 唯一 attempt 全部准入后才读 AVI，不能把示意的三个命令当作完整 runner。

| 两文件全成功的计划项 | 数量 |
|---|---:|
| 唯一 producer payload | 736,803,758 B |
| host prehash + 同 FD 传输读取 | 1,473,607,516 B |
| 新临时及最终件各一次完整 hash | 1,473,607,516 B |
| 原残件归档前后 hash | 162,814 B |
| 设备内容 hash 合计 | 1,473,770,330 B |
| 新增 payload + 保留残件 | 736,885,165 B |

算术与计划一致。AVI 是首次一次预置 736,454,656 B，不能忽略为仅补 MP4；空间须重新核准确现场，另保留旧 cache/APK/fixture 和安全余量，不能删除凑空间。MP4 producer 60 秒、AVI 300 秒、metadata/hash 每命令最多 120 秒、cleanup 共 2 秒是有限计划，不是已测吞吐保证；超时按未知处理、停止而非放宽重跑。每进程输出量和协议调用次数有限，但正式 tester 仍须在包外落盘、累计核 8 MiB 证据预算并保存原 backend.logs，不能省略这个外部总量门。

计划结构可供后续审查使用；**因 F01 当前不能进入实际预置**。修复后重新完整冻结，先独立审查再另派精确一次平板批次；不得用本报告补传、切换通道或自动下一批。

本轮无在途执行，全部设备残件/备份/既有报告保持。E4A-N PASS1/BLOCKED9 和 PREP-01 UNKNOWN 不变；D1 未通过、M0 未启动，全部 P0/历史 FAIL/C14 待测保持。
