# D1 R4 控制操作清单交付回执 V1.0

2026-10-16。依据[R4正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_R4_CODER_REQUIREMENTS_V1.0.md)，补充[R3独立复审R3-R01](D:/CodexProjects/VideoKit/docs/tester/D1_R3_REVIEW_REPORT_V1.0.md)。**仅文档，未实现/执行；交完整包待独立复审，不宣布D1通过或有限harness已获实现准入。**

## 1. 交付身份与覆盖关系

| 文件 | 原始字节SHA-256 | 范围 |
|---|---|---|
| [D1_R4_CONTROL_OPERATION_MANIFEST_V1.0.md](D:/CodexProjects/VideoKit/docs/coder/D1_R4_CONTROL_OPERATION_MANIFEST_V1.0.md) | `6492f598b8b9f605239648277d08a56beae565c65de0f1dac5cee6db2ffa40bd` | 61行＋PF16＋清理/停止32槽的具体逻辑请求、权威、子IO、资源与异常出口 |
| 本回执 | 不嵌自引用hash；主动通知中另给实际hash | 求和、自查、范围与未验证限制 |

只新增上述两份R4文档。R2/R3原件、R1、C14、产品与素材不编辑。R4主体§1/§6替代R3 manifest§2/§6及回执§3“普通行非query6、D8/C4、总515”的计数分配，以每行具名操作实际数重新分配；不改close disposition、grant/delivery/claim及未知abort-only等已获材料认可语义，不改101次query或任何既定媒体IO/资源/记录/时间硬限额。全部32条任务记录仍为17S＋14T＋PF，未拆出新case或新目标。

## 2. R3-R01的补充映射

| 缺证位置 | 现在的可复核内容 |
|---|---|
| 操作粒度/请求ID与权威 | 主体§1–2：每token独立`row/nNN`，重放沿用原commandId而请求仍收费；拒绝也收费，query新观察与同ID重放分开。G/S/O/J/R的进程与拥有权固定；每次create/dup/send/take/claim/flush/close/验证有实际调用子账本。数据面D独立operationId/请求字节/调用数，不含免费的open/close/claim。 |
| T05/Q07-TAKEFIRST原行6不足 | 主体§4：本行14次N，完整grant→allocA→dupB→sendB→takeB→claim→flushB→cb→ca→v+→cv→takeover→旧ready拒绝→新abort。写32B和本task验证读取另列D；独立T05 receipt，不借T01/T02授权、writer或receipt，无组合finalize。 |
| P11两个consumer与future open | 主体§3：FUTURE13次N，两个res/两个真实open/先关闭并end(A)再open(B)，最后逐份关闭/end(B)；SEALED12次N，seal先赢，第二open请求计费但factory0。两次query分别看中间reservation和终态。 |
| P10-B旧对象关闭丢ACK/新对象 | 主体§3：13次N，旧对象close1，q1匹配证明，再分配新对象/真实32B＋ref32B；旧命令重放及旧revision重试两请求均native0，新对象独立close；未真实复用裸数值则不假造已发生复用。 |
| S17预登记/三次安全失败/第四拒绝/未知 | 主体§3/§5：D行11次N，在首次失败前两对象及两个异步close均独立登记，两个ticket分开；首次＋两retry原子获权、第三失败响应给revision，第四拒绝；C行4次N，放行原C请求、拒不同op、模型退休owner、再拒新owner重试。无UNKNOWN后新开对象。 |
| PF及GC32的可执行映射 | 主体§5：PF/n01–16逐项，两个既有helper分别hello、reserve/guard/J/ref、双16B读取、独立close/end/能力预检。GC/n01–32逐槽，fence/cancel/放闸/安全close/两helper正常退出/三个独立权威death通知/consumer结束/6父pipe/2父process handle/journal/log；无正常32另加故障32。 |
| 共享任务前置收费及存量资源 | 每行声明空初态或已有状态，T01/T02后行明确沿用前行已收费对象；新T05从空开始。P12-OLDOPEN行19次N含v2读后真正关闭三引用/end(B)，NOTICE/CHANGED行H=0有实际前提；v2在NOTICE时仍ACTIVE但无seal/移动许可，CHANGED才显式seal，原文件不改。 |
| 控制之外实际副作用/证据 | 主体§2/§4.1：每个native计数、至多两次接纳/完成元数据事务及其open/write/sync/close/namespace ACK均列界限；不是把多个独立API藏成一次finalize。每N/D有界接纳/完成事件、query响应和快照双槽计文件峰值；实际不支持则NOT_RUN/PENDING。 |

GC一个原owner的death证据通知只更新固定ledger内匹配该owner的逐ticket知识，不执行批量close；S收J、S收R、O收R分别收费。未实际退出不清账；父guard、pipe、process handle、log与journal也不能靠helper死亡清除。S17.D nativeclose0，C原close UNKNOWN不改为调用成功。最后log close结果经原调用返回通道交外层，不在关闭后再建新log；返回未知同样保留未证。

## 3. 逐行与累计预算静态自查

读取Markdown表格逐行解析控制token数，花括号并发双请求分别计2；与N列一致，61 ID无重复且与R3集合完全相同，各行Qr/Qn及秒数逐一等于原R3。PF与GC的ID分别连续01–16/01–32。此为文档检查，不执行其中任何动作。

| 项 | R4分配/重算 | 原硬上限与边界 |
|---|---:|---|
| P非query | 176 | 31行，含拒绝/重放/闸门/consumer结束 |
| Q非query | 127 | 30行，含每个新任务完整前置 |
| PF/GC非query | 16＋32＝48 | GC清理与停止共用；不用的槽跳过不挪用 |
| 非query总数 | 176＋127＋48＝**351** | ≤443，余92不授权额外操作 |
| query | P7重放/42新＋Q11重放/41新＝**101** | 保持18重放/83新，各行不增 |
| 全控制 | 351＋101＝**452** | ≤544，未用92不增加分支/补读/重试 |
| 时间 | P57＋Q55＋PF20＋清理20＋记账10＋停止18＝**180秒** | P尾5已含在57；不额外加计控制或预检时间 |
| 输入请求/调用 | **1,573,522B / 59** | ≤4MiB/256，保持R3全表数据面分配，失败/未知不退预留 |
| 目标/顶层记录 | **10 / 32** | ≤12/32；日志、版本、ticket嵌既有记录 |
| 输出写/验证读取 | **655,360B / 262,144B** | ≤2MiB/4MiB，四个独立validation lease各有open/read/close |
| 日志/元数据文件峰值 | **3,178,496B** | ≤4MiB，1,015,808B仍仅停止证据；活动snapshot/暂存各≤8KiB合计≤16KiB/记录 |
| 并发资源 | 媒体≤6，全部新增实验OS句柄≤24，缓冲≤8×64KiB | owner归属及父/子端不漏账，未证禁止新独立任务 |

逐行时间余量核算采用主体声明的规划快速处理10ms/N、至多100ms/query，余量留给native/D/实际同步与回报；61行均为正，最小为P12-OLDOPEN的710ms（1秒−19×10ms−1×100ms）。T05为2660ms（3秒−14×10ms−2×100ms）；S17-D1590ms，C2560ms。10ms不是平台保证，只说明列全步骤之后无必然的控制数/纯调度预留冲突；真正IO/启动/同步/退出能否满足时限，仍须后续实现和测量。无法满足应给NOT_RUN/失败/PENDING及具体预算，不删步骤凑PASS，也不加限额。

正常到达全部计划检查点时，输出真实副作用上界另核：create10、dup9、send8、take7、claim提交6，flush/sync各4；write请求9、delegate最多8（T04注入写错误delegate0）；写descriptor A10/B9各独立close，共19。validator open/read/close各4。W3安装位置未证之前用区间，不能从这些计划计数提前报实际归还或精确0。

对新增主体的本地链接存在性、主体hash与本回执值完成核对。R3三原件SHA仍为：契约 `c91743c74bab78ea854c4e5f6dbe7bd2c09da6e3428641f3b31db158323ebb44`、manifest `6b5cb83a9e67fc7de69cac0817f53e29e6ee82b69e9defc781504e0a148e569b`、回执 `ee8086792298abd31a99bd4ed627ce2adcabddf3b0dec94372b38a9101a6a605`；R2五份hash与R3回执列值相同。

现成C14完整性脚本只读working-tree核对PASS：342源、139证据、5产物；freeze-summary `880b38f3896df2f6bed2657d54c7fb8a954d3d05d8c730faf1b11278726e7155`，source ZIP `69ca847d7c1947ae65eb3ed6e79d8ab50e21ac9463a1a686cdeda6cfef2d683d`。这是文件完整性结果，不是重跑871断言、启动JDK/.NET预检或新增功能/设备PASS。

## 4. 限制与交接

本批只有两份文档，无产品/harness实现、媒体IO、故障实验、构建、Gradle、ADB、模型下载或设备任务在途。没有自主派tester/下一阶段。61分支与元数据事务只是待审工具设计；公共API承载、真实backend/JDK/.NET/共享模式/版本/dup/mailbox/认领/关闭/持久性/进程退出均未验证。已有材料认可不等功能通过。

Kit独立、Android先行、Flutter控制层、AAR/C ABI/框架与许可、全部P0/历史FAIL及C14冻结计划保持；有限字节IO不能代正式媒体或故障隔离。F03四次仅encoder协商，不泛化API/close。宿主JNI仍BLOCKED，D1未通过，M0未启动，C14继续环境等待。

整包自查后一次主动向负责人 `01a107c3-2bf9-7fa0-94a0-234258ca6774` 报告两文档和实际hash；通知结果以当前窗口最终回复为准。若通知失败保留回执，不反复绕过。由负责人安排完整独立复审，再决定有限harness实现准入；本回执不代替该决定。
