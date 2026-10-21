# D1 E4A-T 一次平板新预置与使用计划 V1.0

2026-10-17。提案D1-E4A-TP-TABLET-20261017，**executionAuthorized=false，实际预置NOT_RUN**。须先由负责人整包交独立审查，再另派准确批次。本文不是自动执行许可；本窗口不ADB、不读真实媒体、不Gradle。只处理正式准入平板HA1Q6WXR；手机不查询/启用/安装，模拟器不操作。

E4A产品freeze仍a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d。原平板Binder PASS不重跑，正常/取消方法不在本预置计划中；已有APP/test不重装，不动e4a_output_budget/operation.pending、历史cache/输出或其他fixture。

## 执行前只读准入

正式tester从外freeze验证本工具后，保留该新批次与原E4A-N证据；记录准确设备、user0、包/签名及原enabled状态、当前可用空间。仅对指定平板必要状态做一次只读确认，不能从旧连接猜可用，也不能因准备失败重复安装或轮询。

用正确整体引用的run-as com.videokit.app sh -c读取原id/pwd及files/e4_fixtures父目录角色，确认实际app UID/目录、父目录不是symlink，现有预算/marker不被本工具修改。任何权限/引号/工具不支持/状态未知即停止；不换run-as范围、shell模式、传输路线或手机补跑。检查toybox stat/sha256sum/mv -n等命令支持若失败，记录原错误，不启动producer。此Android兼容性本机未实证。

只读计划预览可用现有Python执行 tools/fixture_transfer.py --plan tools/tablet-preload-plan.json；--plan只读JSON/构造字符串，绝不打开source路径或调用ADB。真正执行只在正式派发后显式调用库；不要把预览的receive/verify/publish三个示意命令当完整手工runner，残件保存和attempt护栏必须通过provision_once。

## MP4：先保原残件，再传一次

| 身份 | 固定值 |
|---|---|
| 已有不合格原路径 | files/e4_fixtures/basic.mp4 |
| 必须保持原字节 | 81407B，SHA a790f44fc3c6ff4579c83f57b42a4b31cd95278cca28fd4aa6b97fd295fd9695 |
| 原路径改名归档 | files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep |
| 全新临时名 | files/e4_fixtures/.basic.E4ATP_TABLET_20261017_once.part |
| 成功发布路径 | files/e4_fixtures/basic.mp4 |
| 本次唯一attempt | E4ATP_TABLET_20261017_basic_once |
| 授权源的历史声明 | D:/CodexProjects/VideoKit/test_media/imgs_and_videos/videos/sample.mp4，349102B，SHA720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 |

1. 在新tester证据目录先CREATE_NEW attempt记录、flush/fsync。已有同attempt记录拒绝，不续传或重跑；记录保留源/预期/临时/最终/归档身份。
2. 原路径必须是预期普通残件，先stat、只在不超过81407B后完整SHA，长度/hash全匹配才继续；归档目标必须不存在，只读metadata判断。不同/缺失/超大/权限未知立即停，不猜旧件已成功归档。
3. 同目录无覆盖改名，随后独立核归档长度/hash与改名前完全相同，原固定路径必须已不存在。不得删除残件；archive已存在也不能覆盖。
4. 新临时名必须不存在。源同一只读FD先完整长度/SHA、再归零进行唯一二进制传输；不经PowerShell文本管道/base64/编码转换，不把source路径拼入远端shell。接收脚本为受限目录noclobber cat，仅输出metadata，不tee回显媒体。
5. host检查每次实际写入、总字节/SHA、flush/close返回、原进程退出与stdout/stderr/writer归还；exit0仅PROCESS_IO_COMPLETE_ONLY，不能宣布预置成功。普通过程60s计划，原OS调用不返回只能UNKNOWN，不能猜已写完。
6. 用独立进程stat新临时件，先长度上界，再完整sha256sum；准确长度/SHA都匹配才能发布。固定路径再次只读确认空，再同目录mv -n无覆盖发布；独立核固定文件长度/hash及临时名消失后才FIXTURE_ADMITTED。

失败时停止，保留归档/临时/固定路径的实际现场，不清理、不自动rollback、不换临时名补传。rename可能已发生但回执未知时也不能把旧步骤再执行一次；归档结果供负责人另行判读。

## AVI：MP4全部准入后一次首次预置

源仅取历史指定D:/CodexProjects/VideoKit/test_media/02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi，736454656B、SHA3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f。本窗口未stat/读取它。目标files/e4_fixtures/subtitle.avi必须不存在；新临时名files/e4_fixtures/.subtitle.E4ATP_TABLET_20261017_once.part，attempt E4ATP_TABLET_20261017_avi_once。没有原AVI可覆盖或复用。

沿相同生产pump/独立长度SHA/同目录发布协议，仅一次producer，过程300s计划、metadata/hash命令至多120s、共同cleanup2s。MP4失败即不读AVI；AVI失败不重试、续传、删临时件或更换传输工具。新临时名和时间预算不能自动滚动产生下一次许可。

## 正式tester的库接入

下面是另行正式派发后的接入形态，本次不执行。plan从冻结JSON读取，证据目录必须放在新的tester批次下，**不要在冻结的docs/coder/d1e4at内写新结果**。execution_authorized护栏只有误操作防护，不替代负责人对准确设备、源与次数的授权。

```python
# Only after a separate formal tester dispatch, with the frozen tools directory on sys.path.
from fixture_transfer import AdbBackend, FileProof, provision_once
for item in reviewed_plan["files"]:
    backend = AdbBackend(reviewed_plan["adb"], reviewed_plan["serial"],
                         execution_authorized=True, timeout=item["timeoutSeconds"])
    old = item["residual"]
    result = provision_once(
        backend, item["source"], FileProof(item["bytes"], item["sha256"]),
        item["final"], item["temp"], new_tester_evidence_directory,
        attempt_id=item["attemptId"],
        residual=FileProof(old["bytes"], old["sha256"]) if old else None,
        archive_path=item["archive"],
    )
    # Persist the bounded original backend.logs outside the frozen tool package as well.
    if result["status"] != "FIXTURE_ADMITTED":
        break
```

保存process原argv/exit/writer/flush/close/drain/实际字节、source两遍SHA、独立设备stat/hash、改名前后残件、临时与发布证明，以及attempt/result/events。stdout/stderr前缀可能截留，但总量/摘要单列；命令解析需要完整短metadata stdout，截留/异常stderr拒绝。不要在收据中将submittedBytes当landedBytes。

## 次数、空间、流量与停止

| 项 | 两个文件全部成功的计划量；非实际用量 |
|---|---:|
| 唯一producer payload | 736803758B |
| host完整prehash+同FD传输读取 | 1473607516B |
| 设备新临时/发布后两次完整hash | 1473607516B |
| 残件改名前后hash | 162814B |
| 设备计划总内容hash读取 | 1473770330B |
| 新增数据峰值 | 736803758B |
| 新件+仍保留原残件 | 736885165B |

同目录rename不增加第二份payload；历史APK/cache/未知fixture及安全余量另核，不能删来凑空间。metadata存在性不读旧件内容；超大目标在hash前拒绝，短件hash不超过该文件声明上限。数据增长/并发恶意替换不在合作式协议的强权限保证内，发现不符即停。

每process stdout/stderr各≤1MiB，超过最多额外一个16KiB块即失败，各只留64KiB前缀；源块64KiB。整体本预置证据≤8MiB，超额停止而非丢弃首因。两文件协议控制调用次数固定有限，不能轮询重试。原进程/pipe未知强保留，不能强制全局归零或杀ADB server证明结束。

本批不预先验证可用空间/现场目录，不保证Android cat/ADB传输必然成功；独立hash准入保障不合格不发布，具体截断根因仍UNKNOWN。完整真实结果由下一tester批次主动交负责人，不接着自行执行codec/取消/故障；D1未通过/M0未启动。
