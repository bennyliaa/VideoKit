# D1 E4A-T4P 二进制传输诊断提案 V1.0

2026-10-17。待负责人审查另派，executionAuthorized=false，设备执行NOT_RUN。仅平板HA1Q6WXR；批次D1-E4A-T4P-TABLET-20261017，nonce E4T4P_TABLET_20261017_ONCE。

## 准入与唯一范围

标准ADB push文件协议，不通过shell stdin传payload；shell仅-n -T -e none。原app com.videokit.app，UID10221、pwd /data/user/0/com.videokit.app，shell UID2000。固定ADB路径D:/Android/SDK/platform-tools/adb.exe。

| 项目 | 准确路径 |
| --- | --- |
| 必须已存在的应用专属外部base | /storage/emulated/0/Android/data/com.videokit.app/files |
| 唯一新stage目录 | /storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once |
| 唯一push目标 | 上述目录/payload256.bin |
| 唯一新internal目录 | files/e4_diag_T4P_TABLET_20261017_once |
| 唯一内部copy目标 | files/e4_diag_T4P_TABLET_20261017_once/payload256.bin |
| 唯一新包外证据目录 | D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T4P_EVIDENCE |

外部base、Android12/FUSE/SELinux及shell/run-as访问均UNKNOWN，须本批准入。不能默认产品曾创建external files。base不存在、不可访问、模式/工具不兼容或目录冲突就报告并停；不mkdir上层、不改权限、不root、不改manifest、不向媒体库发布、不改用全局暂存或其他路线。stage目录只能在准确base下创建一次，新目录创建后再核双UID访问，未通过时push0。

输入仅冻结payload256.bin，全字节0..255，256B，SHA256 40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880。无--source/媒体参数。旧26B准确残件及旧媒体/临时文件均不访问、不stat、不hash、不改名、覆盖或删除；本批无需补查历史文件。

## 固定顺序

1. features完整成功响应，原exit/实际归还/长度SHA门齐全，精确shell_v2；无fallback。
2. shell对准确既有base作只读角色/rwx/stat及工具探针。
3. run-as对同一base作只读访问检查，原UID/pwd/files角色、新internal目录不存在；head-c0读取/dev/null确认工具支持，不读payload。
4. 一次原UID进程快照。疑似旧cat/tee/sh/mksh/head/cp/dd或旧接收线索即停止，不信号。未见仍UNKNOWN_NOT_CLEARED；格式不符停止，不跳过异常行。
5. 主机仅预哈希固定256B合成源并实际close；shell以umask077独占mkdir准确stage子目录，拒全局可写位。
6. app UID只读核新stage访问/目标不存在；shell再核同一新stage及叶目标不存在。
7. 唯一`adb -s HA1Q6WXR push -q -Z <冻结payload> <准确stage目标>`。原客户端exit0不等成功落盘，原stdin始终0B。
8. 另条run-as命令独立stage前后stat、普通非symlink、长度256及最多256B SHA。完全一致才继续，失败保留stage、copy0。
9. 唯一run-as本地copy：stage身份须仍同第8步，新internal目录/目标无冲突；umask077/mkdir准确子目录/set-C，head-c256从stage文件写internal。BEGIN/END原UID/pwd/同PID/准确source-target/256计数齐全；不读取host stdin。
10. 再独立命令核internal普通非symlink、原app UID、前后stat/256长度/最多256B SHA；全部相符才记合成二进制路线通过，不准入媒体/产品测试。

标准push无原子no-replace能力；本提案以新专属目录及紧邻push的冲突门防止使用既有目标，**不保证抵抗同UID并发抢建**。负责人审查须保留此边界，不能将exit0或独立SHA解释为原子拒覆盖。若该边界不获接受，提案不执行，不现场更换方案。

## 预算与停止

metadata计划9/硬上限20，push1、copy1。metadata/push/copy各15s；本机归还观察2s，不是远端生命周期上限。日志1MiB；stdout/stderr各16KiB、各保留4KiB，完整响应超前缀即拒。一个CREATE_NEW attempt在首个远端变更前消费，任何失败保留全部新目录、部分文件及原记录，无补跑/换路/清理。

主机工具预哈希正常256B/硬读257B，ADB名义文件输入256B；其实际内部读取计数UNKNOWN，不伪造submitted256。设备stage哈希≤256B、内部copy读取≤256B、internal哈希≤256B；新增文件stage/internal各≤256B，不全片复制或读媒体。payload没有经过shell stdin。

保留T1实际close强owner；若源close/原进程/管道/线程未证明归还，原解释器持有对象，不下一I/O、不二次close、不用GC或退出洗清；仅观察实际原返回。旧远端UNKNOWN全程保持。失败或疑似并发变化报告原事实，禁止自动修复后重试。无手机、安装、Gradle、Binder、预算/pending标记或产品方法。

## 准确入口

默认只打印计划（无adb、无payload读取）：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at4/tools/diagnose_binary_once.py'
```

仅负责人正式派发后，由tester一次执行；formal-batch是误用防护，不是授权凭据。证据目录须全新且在冻结包外。

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at4/tools/diagnose_binary_once.py' --execute --formal-batch D1-E4A-T4P-TABLET-20261017 --evidence-dir 'D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T4P_EVIDENCE'
```

执行前以集中消息外seal SHA核验：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at4/tools/package_tools.py' verify --expected-freeze <外部seal-SHA256>
```

保存attempt.json、各原命令argv/exit/完整有界输出/长度SHA及实际归还记录、result.json中的两个独立proof/copy proof与失败首因。独立媒体恢复计划可在路线实际通过后由负责人另定，本批不执行；D1未通过/M0未启动/P0和历史FAIL保持。
