# D1 E2D 修后 G 六点 OS 对照独立复审报告 V1.0

日期：2026-10-17。角色：VideoKit tester。依据：E2D 正式测试需求及开发冻结整包。结论：**本轮证据复审通过，未发现新增阻断项；修复后的引用释放获得小范围实际证据支持。建议负责人另行派发一次新的 actual 自有文件完整 61 分支回归，按原门槛判断。当前没有完整运行授权，也没有完整 Engine 通过结论。**

本轮仅做静态、字节校验和既有证据复审，执行已审读的只读 verify 与 tester 自有静态审计；未重新运行小实验、定向测试、构建、PF、媒体或设备测试。所有实际运行数字均来自开发保留的原始记录。

## 1. 整包与原实现绑定

- 冻结摘要 SHA256：`f0a3e8fc9ae7e6e8c3def52d0002d23af77212ad35cb016a612e34e45f42de1b`。
- E2D-source.zip SHA256：`6c6eef8c0d9541aefe1eb807a312d1fce7ba968038c127e565af9becd7ccf9d8`。
- 63 个源码条目、32 个冻结条目、自检文件 0：逐项长度/hash、ZIP 精确成员集合及成员 hash 一致。三份开发文档、原始六点/entered/预约/退出与绑定记录齐备。
- 生产 32 源文件及 manifest/profiles 共 37 文件与 E2C 原包逐字节一致；原 E2C.dll 和 9 个 Java class 共 10 产物绑定一致。保留原 E2C 路径、命名及协议，没有用重命名制造新授权。
- 61 分支入口符号可由 AST 定位，N/query/time 分配与 R4 一致；`experimentEnabled=false`、真实执行授权层保持关闭。

只读 verify 返回 PASS；tester 独立校验结果及归档见 [independent-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_E2D_EVIDENCE/independent-audit.json)。这两类校验均不等于功能执行。

## 2. 唯一修后六点结果

原实例 PID35964、creationTime100ns=134366485352518462、owner=E2D-G-1792174935530529100。唯一 G，两个原 Hub worker，无第二实例或第七点。原始 [六点记录](D:/CodexProjects/VideoKit/docs/tester/D1_E2D_EVIDENCE/g-comparison-1792174935530529100.json) SHA256 为 `9180cf6fe2b8358d2c3ccdc5a23ce85fbf7b5cda6148ea1da8b98bf7a279667a`。

| 固定观察点 | 线程/句柄 | 句柄增量 | active/archived/total | weak cell/Future/closure | 额外审计副本 |
|---|---|---:|---|---|---:|
| ZERO_CELLS | 6/160 | 0 | 0/0/0 | 0/0/0 | 0 |
| ONE_LIVE | 6/164 | +4 | 1/0/1 | 1/1/2 | 0 |
| ONE_DRAINED_COMPACTED | 6/161 | +1 | 0/1/1 | 0/1/0 | 1 |
| EIGHT_LIVE | 6/193 | +33 | 8/1/9 | 8/9/16 | 1 |
| EIGHT_DRAINED_COMPACTED | 6/161 | +1 | 0/9/9 | 0/1/0 | 9 |
| PROBE_AUDIT_COPY_RELEASED | 6/161 | +1 | 0/9/9 | 0/1/0 | 0 |

六点线程、句柄、working set/private 的绝对值及相对本实例 ZERO 的差值均在批准界内。working set 从 27,082,752 至 27,185,152 字节，private 固定 18,104,320 字节。ZERO 在本实例两 Hub worker 启动后固定；不能代替下一次完整 Engine 原 G 在 PF/n01 前的基线。

两次实际排空和生产 compact 后，重 cell/闭包弱引用都为 0，首个外部 Future 持续有效，原值身份在消费及 Hub 关闭后仍成立。最终只删除 probe 审计副本，生产累计 9、history 9、峰 8 保持，未退款或删生产历史。修前 E2C 六点的已完成对象保留现象，与本次原实现归档后弱引用消失形成对照；两次是不同进程，只支持限定范围的改善判断。

末点句柄为 ZERO+1 不构成失败；不要求强制回到 ZERO。离散采样可能遗漏短峰，不能声称连续全过程峰值。每 cell 固定句柄数、残余 +1 的类型因果、CPython 精确编译同步 C 后端仍为 UNKNOWN。

## 3. 调用者、引用与退出边界

静态核 [compare-g.py](D:/CodexProjects/VideoKit/docs/coder/d1e2d/tools/compare-g.py:50)：直接绑定生产 Engine.private_cell/compact_cells/cell_facts，原运行亦核函数对象身份。该 Probe 未构造完整 Engine/Native/Channel，未创建 J/R，未执行文件 native 读写。

create 帧仅让首 Future 作为外部对象逃逸，观察集合保存 weakref。consume 先执行逻辑 native completion、gate、原 Future.result，确认源 operation done/nativeReturned、callback 实际返回及该 cell 的 Hub 静默；整个消费函数与其等待谓词返回后，原 creator 再调用生产 compact，实际归档 1 与 8。九份消费证明各项为 true。引用统计帧在 OS 查询前返回，只留下标量和纯审计视图，未由最后循环变量、等待闭包或批量 cell 列表污染观察。生产 UNKNOWN、通知容量及外部 Future 语义沿用 E2C。

实际 CPython3.12.14/MSC1944/64 位及 python312.dll hash 与 E2C 记录一致；GC 原启用、阈值 700/10/10，无强制 GC 或禁用 GC。probe SHA256 为 `6975917a764cde4db387c35ddd93a902ba37433e072eb092d7ace598ebcaca46`，原运行后未变。

原预约先于 Hub/cell 创建。observer 六周期、identity 查询 1、13 开 13 关、同时最多自有句柄 1，最终信用归零，无 close UNKNOWN。独立账本资源峰 3、buffer 信用峰 8，最终均归零。正常 compact 2 次，失败收尾 completion/gate/consume/compact 均 0；fixture/RPC/驱动控制均 0。总时长约 1.125 秒，小于 60 秒；样本均在 0.1 秒内，记录中的 0.0 属于时钟粒度。

第六点后原 Hub.close，两个原 worker join，状态 CLOSED、无 in-flight/ownership pending，外部 Future 仍保留原值。 [原 caller 退出回执](D:/CodexProjects/VideoKit/docs/tester/D1_E2D_EVIDENCE/g-comparison-outer-exit.json) 绑定原证据及身份，记录原命令 exit0；未另起 G 查询退出。没有关闭后第七次 OS 采样。

原报告的 100,630 字节是生成时 g-comparison 前缀文件快照；最终加 outer 635 与 production-binding 7,964 后为 109,229 字节，未超过诊断 512KiB。整批日志/证据含 seal 为 268,089 字节，低于 4MiB；没有媒体 fixture。

## 4. 给负责人的集中处理建议

**可另派一次新的 actual 自有文件完整 61 分支回归。** 这是一项后续派发建议；本报告不消费新许可，也不复用 E2B 已消费许可。执行前须同时满足：

1. 新派发明确一次性批次、原父进程/运行身份、全新自有输出根及 CREATE_NEW 预约；绑定本轮确认的 E2C 修复源码、配置、原依赖产物及 hash。保留 E2D/旧 FAIL 只读，不变更真实媒体授权层。
2. fresh 可用物理内存至少 2GiB；原 G 的 PF/n01 前基线固定，J/R 各自原 HELLO 实例基线固定。禁止后移基线、重启择低、提高阈值、强 GC 或失败自动重跑。
3. G 线程≤16/增量≤12、句柄≤256/增量≤64，WS/private≤256MiB/增量≤128MiB；J/R 线程≤64/增量≤32、句柄≤512/增量≤128。J WS/private≤768MiB、R≤512MiB，两者增量≤256MiB。绝对值与增量同时执行。
4. 保留 active≤8/累计≤64、全局资源24/单行媒体句柄6/buffer 8×64KiB，以及原61预算、日志精确写入和剩余配额。原计划180秒、外层200秒只作停止等待边界；不能把超时或 Future.done 当 native 返回/进程退出证明。
5. 沿用 1秒周期、最多201周期、间隙≤2.5秒、样本≤0.1秒、单 observer 信用及最多一自有 OS 句柄；global.log≤131072字节，events≤104320、metrics≤26752。原生观察或 close UNKNOWN 保留信用并 STOP_PENDING，不扩容补偿。
6. 原始首次 FAIL/PENDING、实际完成分支数、部分断言、进程/线程/句柄实际清理事实完整保留。停止后只做已授权的有界原 owner 收尾；缺 native return/close/join/原 caller exit 证据仍 PENDING。全部通过后再整包交 tester 复审。

本次累计 9/峰 8 的 Probe 不覆盖完整 Engine 构造、IO/transport 池、PF、J/R、61分支、真实文件的实际读写和全程资源轨迹。新批次须自行证明这些门槛，不能用当前六点替代。

## 5. 保留事项与最终状态

本轮新增阻断项 0；本轮构建、定向断言、完整运行断言均 0，六点是观察记录而非测试断言。旧 E2C1125、E2B955、部分运行77/完整通过0及更早断言均仅作历史，不累加成本或成功数。

E2B 原 G369/基线160/增量209 超过256/+64的 FAIL，以及 E2A 原 R519>512 FAIL 保留。host JNI BLOCKED、Kit/Flutter/AAR/Android/licensing P0、五项产品 namespace/READY 限制及 C14 原限制不变；本轮未恢复设备/媒体测试，C14 平板功能仍为0。**D1 NOT_PASSED，M0 NOT_STARTED；完整 actual/真实媒体尚未获本轮执行授权。**

复审报告及证据交项目负责人，供统一派发开发后续回归。通知回执单独记录在本报告证据目录，报告签发后保持原字节。
