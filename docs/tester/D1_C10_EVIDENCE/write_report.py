import collections,datetime,json,pathlib,re
B=pathlib.Path(__file__).resolve().parent;R=B.parent
data={d:json.loads((B/d/'results.json').read_text()) for d in ['phone','tablet']}
assert all(len(v)==40 and len({r['method'] for r in v})==40 for v in data.values())
counts={d:dict(collections.Counter(r['result'] for r in rows)) for d,rows in data.items()}
assert counts=={'phone':{'ENVIRONMENT_BLOCKED':40},'tablet':{'PASS':38,'FAIL':2}}
audit=[]
for r in data['tablet']:
 o=B/'tablet'/r['attempt'];e=json.loads((o/'post/evidence.json').read_text());logs='\n'.join(f.read_text(errors='replace') for f in o.glob('*-command.log'))
 assert e['instrumentationCompletion'] and not e['activeWorkerLines']
 assert ('OK (1 test)' in logs) if r['result']=='PASS' else ('FAILURES!!!' in logs)
 audit.append(dict(method=r['method'],result=r['result'],instrumentationFinished=True,noActiveWorkersInPostSnapshot=True,rawProof=e['rawProof']))
legacy={}
for method in ['workerSigsegvDuringActualEncoding','secondCodecTaskSurvivesFirstNativeCrash']:
 text=(B/'tablet/attempts'/method/'post/legacy-worker.log').read_text(errors='replace')
 m=re.search(r'pid:\s*(\d+),.*?>>> com\.videokit\.worker\.spike[^\n]*<<<.*?uid:\s*(\d+).*?signal 11',text,re.S);assert m
 legacy[method]=dict(pid=int(m[1]),uid=int(m[2]),signal=11,source='post/legacy-worker.log',appExitClassification='NOT_ASSERTED_BY_THIS_METHOD')
(B/'execution-audit.json').write_text(json.dumps(dict(counts=counts,tabletMethods=audit,legacyRawWitnesses=legacy,noAdditionalDeviceExecution=True),indent=2),encoding='utf-8')
budget={d:json.loads((B/d/'output-budget-final.json').read_text()) for d in data}
logbudget={d:json.loads((B/d/'log-budget-final.json').read_text()) for d in data}
now=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
lines=[f'''# D1 C10 集中测试报告 V1.0

报告生成：{now}。候选：D1-20261016-C10；无 Git commit。执行输入：D1_PHONE_TEST_EXECUTION_V1.0 最新 C10 交接、D1_C10_TESTER_REQUIREMENTS_V1.0、D1_DELIVERY_D1-20261016-C10、设备附录与许可准入文档。

## 结论

**D1 未通过，不进入 M0。** 平板 40 项实际运行，38 PASS / 2 FAIL；手机 40 项 ENVIRONMENT_BLOCKED，未安装或执行 C10。手机系统禁用问题未解除，平板两个 CPU 崩溃入口的严格信号断言失败。新增同 task/epoch 重连覆盖进程身份、死亡账本缺少代次的问题。CPU 正常帧、同步 STOP 和若干生命周期反例已有本轮通过证据，但不能代替完整产品隔离或发行准入。

| 设备 | CPU 25 | host 7 | legacy 8 | 合计 |
| --- | --- | --- | --- | --- |
| OPPO PDYM20 / U4999DLBNRR89DOR | 25 ENVIRONMENT_BLOCKED | 7 ENVIRONMENT_BLOCKED | 8 ENVIRONMENT_BLOCKED | 40 环境阻断，0 次 C10 instrumentation |
| Lenovo TB138FC / HA1Q6WXR | 23 PASS / 2 FAIL | 7 PASS | 8 PASS | 38 PASS / 2 FAIL |

两设备 API 31、ARM64、实际页大小 4096。静态 16KiB 对齐不等于 16KiB 页设备实测。手机首次预检及结束状态均 enabled=2、lastDisabledCaller=com.oplus.athena；本轮没有 enable、卸载、清数据或失败后继续启动手机测试。用户“已连接”仅作为设备连接反馈。

## 候选身份与执行过程

独立核验冻结 163 源文件、108 证据文件及 5 产物，完整性 PASS；核验对象为冻结候选，不要求浮动工作树等于旧候选。冻结时间 2026-10-16 09:31:33。详见 [freeze-check](D1_C10_EVIDENCE/freeze-check.json)、[admission-check](D1_C10_EVIDENCE/admission-check.json)。

| 对象 | SHA256 |
| --- | --- |
| freeze-summary | 4b728a9b5694e096e0374cd8d2e5bb77ce53afb173e512d0308d8f9ca4e0deec |
| source ZIP | 7ab367f61f0e185d9ae4f70dbcbb6c2502e4cb03fdf46441e145c93fb5ea7a70 |
| app-debug.apk | 87d178d03f5075507cde6ca8974a3129f9c7a2d69f5401d30d48c04610112b76 |
| app-debug-androidTest.apk | 34c96b9e86386ebcc98b70dcf7c438b14edc6de3f44fe5d43f978c43bec41b72 |
| worker-debug.apk | 027d2e369916d1c0aef50ea157dd855cd5033ac56fbfad7ad2126ebb0c53a29a |
| release-unsigned，仅对照、未安装 | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e |

三个 Debug APK 证书 SHA256：5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。平板实际安装 main/test 及最终 worker APK 回读 hash 与候选相符。更新前旧 APK、包状态及缓存已备份；CPU 阶段只更新 main/test，legacy 阶段才更新 companion。未运行 Gradle、未修改产品源码或旧冻结。321 项本机断言为交付自检证据，不计入设备 40 项。

顺序为手机预检阻断→平板 CPU→host→legacy，逐方法独占目录、明确 serial；每方法只有一次尝试。两次 FAIL 均先停止外层调度，核对 instrumentation 完成、无残留 worker、Source/在途状态，再通过各自 review.json 继续独立项。没有重跑获取理想信号，没有强停进程或以终止 ADB 客户端当作远端结束。40 项均有完整单用例终态；FAIL 保留原始断言，未改为环境阻断。详见 [execution-audit](D1_C10_EVIDENCE/execution-audit.json)。

## 逐项结果

手机列 EB = ENVIRONMENT_BLOCKED；证据统一在 phone/environment.json、preflight.json、package-at-end.txt。平板每行证据在 `D1_C10_EVIDENCE/tablet/attempts/方法名/`，含原命令、result.json 和 post；总表为各设备 results.json。

| 序号 | 组 | 方法 | 手机 | 平板 |
| --- | --- | --- | --- | --- |''']
for i,r in enumerate(data['tablet'],1):lines.append(f"| {i:02} | {r['group']} | {r['method']} | EB | {r['result']} |")
lines.append('''
## 核心运行证据与已有限定闭合

- MP4：真实 RGBA 帧 147456 bytes；raw=24576、time_base=1/12288、pts_us=2000000、best_effort=0。正常入口成功，最终同步 STOP caller_uid=10221/caller_pid=25149、ACK、actual_death=true、source CLOSED、slot released、pending_calls=0 均有记录。
- AVI MPEG4：raw=300、time_base=83417/2500000、pts_us=10010040、best_effort=1；峰值 RSS 173908 KiB、FFmpeg allocation_peak=15179327。只证明本片段的真实帧和时间戳路径，best-effort 不能写为原始 PTS。
- C09-T01：正常 MP4/AVI、取消、挂起等本轮入口通过；oneway 负例实际 caller_pid=0、caller_uid=10221、flags=17，被 CPU_SYNC_CONTROL_REQUIRED 拒绝，之后严格同步 STOP 仍通过。没有接受 PID0 作为同步 owner。错误 epoch、STOP 卡住不挤占第二 RPC、主线程取消与 ACK 丢失入口均通过。ACK 丢失最终 stop_ack=false、stop_result=CPU_WORKER_ACK_PROTOCOL，但 actual_death=true、no_worker_proven=false、source/slot released，未将 ACK 当死亡证明。
- 无绑定清理：binding=NOT_REQUESTED、pid/uid=-1、actual_death=false、no_worker_proven=true，源关闭后释放预留槽。这不是已创建 worker 的死亡证据。活动读取取消入口的严格 pending/source 断言通过，结束账本为 operations/consumers/pending_calls=0、source CLOSED。
- C09-T02：首个失败保留与 cleanup failure 反例入口 PASS；本轮两个真实失败均保留原始 AssertionError（178/190 行），未被 finally 覆盖。仅声明已覆盖路径通过，不扩大为全部故障诊断闭合。
- host 7 项与 legacy 8 项均通过，包括真实编码输出、响应丢失/写/flush/验证故障、journal 恢复、重复 FD 锁、取消、worker 退出、native crash、另一任务及 host death 恢复。legacy 的真实 SIGSEGV 另由 worker UID 日志保留：单任务 PID29022/UID10220、双任务首 worker PID29193/UID10220，均为 signal11；这些方法不额外断言 App ExitEvidence 分类，不能用 legacy PASS 覆盖 CPU 的 UNKNOWN。

## 集中缺陷

### C10-T01：CPU 崩溃的 App 信号证据不闭合（阻断）

`cpuSelfSigsegvSignalMustBeProven` 和 `cpuSecondSlotAndHostSurviveFirstSelfCrash` 各运行一次，均 FAIL。

| 入口 | 原始崩溃身份/信号 | App 退出记录 | 最终判定 |
| --- | --- | --- | --- |
| self SIGSEGV | PID27146 / UID99055 / signal11 | matched=true、reason5、signal0、cause UNKNOWN、PARTIAL_SIGNAL_UNKNOWN、trace_sha 空 | FAIL；原始 AssertionError: signal0 stays UNKNOWN/FAIL |
| 双槽首任务 SIGSEGV | PID27457 / UID99057 / signal11 | matched=true、reason5、signal0、cause UNKNOWN、PARTIAL_SIGNAL_UNKNOWN、trace_sha 空 | FAIL；原始 AssertionError: target signal must remain independently proven |

同次原始 tombstone 与任务 PID/UID 匹配，证明故障命中；App status0 仍未知，不将原始 signal 回填为 App PASS。双槽方法在最后信号断言前，已通过第二 Binder 存活、resume 后取得结果及 host PID 未变断言，但整个方法仍 FAIL。

只读检查冻结 ExitEvidence.java：awaitSignal(reason,status) 命中后创建 PARTIAL_SIGNAL_UNKNOWN 并 continue，位于 getTraceInputStream() 之前。因此本轮日志不能证明 trace 不存在、不可读或解析失败；status0 分支跳过 trace 采集是待修证据缺口。不得据本轮推断 Android 没有 trace，亦不通过追加重跑碰信号值。

证据：[self](D1_C10_EVIDENCE/tablet/attempts/cpuSelfSigsegvSignalMustBeProven/post/evidence.json)、[双槽](D1_C10_EVIDENCE/tablet/attempts/cpuSecondSlotAndHostSurviveFirstSelfCrash/post/evidence.json)，相邻 host.log、tombstone-pid*.log、原 command log 和 review.json。

### C10-T02：同 task/epoch 重连覆盖身份，死亡状态与新进程混用（阻断）

self 任务 dfba2d81847544f0b66bc693a28757bb / epoch3676676221173001482：首次 HELLO 27146/99055，崩溃后同 task/epoch 再次 HELLO 27175/99056。最终 CPU_LEDGER 写新 PID/UID，却保留 actual_death=true、stop_attempts=0、stop_result=NOT_SENT、slot_released=true。

双槽首任务 e3663aef6ae642e19be5f8ec175d5cdb / epoch1207628141031480155：首次 HELLO 27457/99057，崩溃后再次 HELLO 27502/99059，最后账本同样记录新身份与旧死亡状态。两个独立方法都观察到该现象。

冻结 CpuTaskClient 的 hello() 可重新写 pid/uid，onServiceConnected() 再次接受连接；死亡状态按 task 保存，缺少进程代次关联。日志已直接证明身份混用；旧进程 death 不能证明新进程 death，不能仅凭该账本声明安全释放。建议修复时绑定不可混淆的 Binder/进程代次、拒绝或独立管理死亡后的重连，并按代次证明 death、在途调用与 slot 回收。具体实现由研发整批处理。

本轮最终 Source CLOSED、在途计数零，失败后和批次结束的进程快照均未见残留工作进程；这是独立读到的结束事实，不能追溯修正混用账本的语义。未通过 kill/force-stop 制造该结果。

### C10-ENV01：手机应用被系统禁用（环境阻断）

PDYM20 的实际包状态 enabled=2，lastDisabledCaller=com.oplus.athena。本轮未安装 C10、未调 instrumentation、未启用或绕过限制。40 项全部环境阻断，无法据平板结果外推手机。需要系统侧实际恢复后再由后续正式候选安排手机覆盖，不自动续跑旧候选。

## 数据保留、预算及结束状态

''')
lines.append('| 设备 | 新 C10 数据字节 | task/journal 记录 | 日志/文本字节 | 旧 capture |\n| --- | ---: | ---: | ---: | --- |')
for d,label in [('phone','手机'),('tablet','平板')]:
 b=budget[d];lines.append(f"| {label} | {b['newBytes']} / 8388608 | {b['terminalTaskRecords']} / 32 | {logbudget[d]['bytes']} / 33554432 | {b['oldCaptureEntries']} 个文件哈希未变 |")
lines.append('''
日志在读写时实施限制，最终预算不是事后删日志所得。各设备 cache-before/after-c10.tar、output-budget-final.json、log-budget-final.json 已留存。平板旧 C06/C07 capture 共8文件未改，新 C10 无 capture；手机没有旧 capture 供比较。原缓存及旧候选保留。平板新私有测试源两文件总736803758 bytes，与测试前及已验证旧源 hash 一致：basic.mp4 720957c9…a1f9、subtitle.avi 3f0bf3e9…52f。源文件不计新输出预算，未覆盖原素材。实际完整 hash 见 source-after-hashes.txt。

平板40个 instrumentation 均有终态、每次 post 无活动 CPU worker；结束 processes-at-end.txt 无 VideoKit 进程。手机结束仍禁用，没有 C10 在途方法；结束进程快照亦无 VideoKit 进程。保留缓存、APK和证据；没有清理、降级或修改启用状态。

## 设计/开源对应与剩余门禁

Flutter 正式 App、独立 Kit/AAR 与 Media3 薄适配仍是正式设计；本轮同 APK Debug harness 不是正式产品完成。FFmpeg 官方8.0.3 CPU 有限实验仅 Debug 准入，自有实现限于 AVIO/JNI、协议、配额与生命周期，不重写解码器、不引入模型。独立核验16个 native 包条目实际 hash、zip布局与 ELF 对齐；五个 FFmpeg/allocator 库逐字节继承 C09，release 对照未变且未安装。许可对应源、NOTICE/SBOM和构建准入继承核验，266对象/608依赖元数据纠错不等于新增依赖或发行批准。

C10-T01/T02、手机覆盖、16KiB页设备、可信像素/PTS质量及B帧/EOS全变体、完整Kit/多宿主/Flutter产品、系统编码显示及宿主JNI风险、全P0和发行条件仍未闭合。旧 ordinary-isolated 未解释结局的历史 FAIL/UNKNOWN 未在本次40项中重跑或关闭。人工播放声音/字幕反馈仅保留在此前对应版本记录，本轮没有新增人工效果结论。历史 C02–C09 报告不回写。本批已结束，不新增设备方法，等待后续整批修复交接。
''')
dest=R/'D1_C10_TEST_REPORT_V1.0.md';assert not dest.exists(),'NO_OVERWRITE';dest.write_text('\n'.join(lines),encoding='utf-8')
assert sum(1 for line in dest.read_text(encoding='utf-8').splitlines() if re.match(r'\| \d{2} \|',line))==40
print(str(dest));print(json.dumps(counts));print('40 rows, 40 complete tablet attempts, budgets and legacy raw witnesses verified')
