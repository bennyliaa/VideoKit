# D1 E4A-T5P 私有 ASCII 流唯一诊断报告 V1.0

日期：2026-10-17，约10:55；设备HA1Q6WXR；批次D1-E4A-T5P-TABLET-20261017；nonce E4T5P_TABLET_20261017_ONCE。依据 `docs/milestones/D1_E4A_T5P_TESTER_REQUIREMENTS_V1.0.md` 执行已审固定CLI一次。

**结论：NOT_ADMITTED，1B无文件解码探针的原端点标记交织，严格解析以MARKER_IDENTITY拒绝；256B接收和独立raw校验NOT_RUN。** 新增工具问题 **E4AT5P-F01 / P1：并行端点共用FD3，标记缺少可靠的互不交织边界**。这是测试诊断工具问题，未形成产品缺陷结论。本轮已停止，无目录/文件创建，无重试或改令。D1 NOT_PASSED、M0 NOT_STARTED、P0及历史FAIL保持。

## 1. 冻结身份及唯一执行

执行前包外证据目录 `docs/tester/D1_E4A_T5P_EVIDENCE` 不存在。只读verify PASS：88源/90不可变；seal `425c53957f6733eda7c23d3cbb81251c31ddd20c3ab4da5a87187ff799291363`；ZIP126167B，SHA256 `32f5bb3d90c41491b7251f66e75b88798f6489c127f3e9cea92cb784f3de6eb8`，准确导入/继承模块绑定通过。冻结源码与JSON未改。

唯一执行 `docs/coder/d1e4at5/tools/diagnose_ascii_once.py --execute --formal-batch D1-E4A-T5P-TABLET-20261017 --evidence-dir D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T5P_EVIDENCE`，原CLI退出1。使用主机权限连接既有ADB，未使用设备root或更改权限。

## 2. 全部原调用和实际返回

| 次序/原记录 | 原命令 | exit | stdout/stderr | elapsed | 原本机owner |
| --- | --- | --- | --- | --- | --- |
| 00-features.json | adb -s HA1Q6WXR features | 0 | 220B/0B | 0.062s | RETURNED |
| 01-original-context.json | 固定shell -n -T -e none run-as原app，原context脚本 | 0 | 83B/0B | 0.156s | RETURNED |
| 02-one-byte-no-file-decoder-probe.json | 同一路由，冻结1B无文件probe脚本 | 0 | 286B/0B | 0.188s | RETURNED |

features完整含精确shell_v2，SHA `05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce`。context完整原标记确认UID10221、pwd `/data/user/0/com.videokit.app`，files为目录/非链接，新 `files/e4_diag_T5P_TABLET_20261017_once` 在原检查时不存在且非链接。context响应SHA `c6ef099f04a9f52daba540251b53ceb981d53ab276c125559d0f0e6f06fa1788`。

probe原客户端exit0且stdout完整未截断，SHA `f15424ea4759dc3e299308d50f8da8ebf3a48d0e79169ee65525122a2ad7a8d3`。以下保留原splitlines内容，不重排、补全或修复标记；原字节换行是CRLF：

```text
TT5_PROBE_RC|E4T5P_TABLET_20261017_ONCE|stage=printf|rc=05_PROBE_RC|E4T5P_TABLET_20261017_ONCE|stage=
decoder|rc=0
T5_PROBE_RC|E4T5P_TABLET_20261017_ONCE|stage=od|rc=0
T5_PROBE|E4T5P_TABLET_20261017_ONCE|uid=10221|pwd=/data/user/0/com.videokit.app|pipelineRc=0|fd3CloseRc=0|hex= 00
```

第三、四行可独立观察od rc0、最后pipelineRc0/fd3CloseRc0/hex00及原身份。第一、二行不具备两个完整准确的printf/decoder端点标记，不能靠片段`decoder|rc=0`或重新拼接就记各端都通过。parse_probe第一行准确身份检查失败，首因MARKER_IDENTITY。**既不能将此称base64不支持，也不能把整套1B兼容门记PASS。** 最后00只证明本次管道末端的原输出，不代替三端独立返回和后续256B证明。

## 3. E4AT5P-F01：端点标记并发交织

严重度P1，范围为测试工具，阻断当前T5P探针协议准入。位置：`docs/coder/d1e4at5/tools/private_commands.py` 的decoder_probe_script/parse_probe。

冻结脚本让printf、decoder和od三个并行管道段各自向继承的同一FD3执行shell printf。当前协议要求每段恰好一条完整原标记，但没有机制保证多个写者的整条标记互不交织；本次真实原stdout已出现起始`TT5_`及被嵌入的`5_PROBE_RC`，printf/decoder的标记边界损坏。不能把“一个shell printf调用”直接当作一次原子记录写入保证。

已证事实是共享输出协议收到交织形态、严格解析拒绝。没有新增设备追踪来确认shell内部具体write切分或每个交错时点，不将更细层原因写成已证。修复应在生产probe设计中保证各端返回值独立可验证并以可靠边界输出，保留各原rc、pipeline及FD关闭门；不能仅容错拼接/丢弃异常字符、退化只看最后exit/hex或现场反复重跑。修复后提交完整新冻结包、兼容及交织/中间失败证据静态复审；本报告不授权改设备脚本或另一次实机尝试。

T5已有本机Git探针通过只说明当时本机调度和工具行为，不覆盖本次Android并发标记输出。原静态复审结论及记录保持，不回填为已预先验证设备协议。

## 4. 未执行阶段和实际预算

UID进程快照、新私有目录创建、固定源预哈希、raw→encoded流读提交、producer BEGIN/DECODE/END、独立raw proof均NOT_RUN。result中的rawSource、encoding、receiverObservation、receiverProof、independentProof均null；没有设备目标stat/摘要证据。唯一计划目标为 `files/e4_diag_T5P_TABLET_20261017_once/payload256.bin`，本轮未创建，未额外补查。attempt已消费，不能自动复用。

| 项目 | 本轮实际 | 上限/边界 |
| --- | --- | --- |
| metadata | 3 | 计划6，硬20 |
| producer | 0 | 1 |
| host raw预哈希/流读 | 0B/0B | 各256B |
| encoded生成/提交 | 0B/0B | 各344B；本轮未读取源 |
| host命令stdin | 0B | 三条均metadata -n |
| 额外probe | 固定脚本AA==4B→管道，末hex00 | 不落文件；三端完整返回门未通过 |
| 设备独立raw hash | 0B | ≤256B |
| 设备新增目录/文件 | 0/0 | 未到mkdir/producer |
| 原单记录 | 1828B/1968B/2776B | 各≤64KiB |
| 原attempt+3记录+result | 7739B | <1MiB，后续tester审计/报告另计 |
| 最大单流 | 286B | 16KiB硬界/4KiB保留，均完整未截断 |
| 调用时间 | 0.062/0.156/0.188s | 各15s，共同本机归还观察2s |
| 在途/本机保留owner | 无/0 | 全部原实际返回 |

三条原记录均PROCESS_IO_COMPLETE_ONLY、RETURNED、原exit0已观察、creationUnknown=false、errors空；flush/stdin实际close/source close/writer/两个drain close均返回，无stdinCloseError、无强制终止owned child。停止来自回执内容协议门，不是原本机资源未归还。历史远端仍UNKNOWN_NOT_CLEARED，因本轮尚未到UID快照，不能断言旧远端已清理。

外部路径/push/权限变更0，旧26B或81407B/真实媒体stat-read-hash0，手机/安装/Gradle/Binder/预算/产品调用0，signal0，无补传、换路、加时、修码后重试或清理。

## 5. 原证据与交付

证据 `docs/tester/D1_E4A_T5P_EVIDENCE`：attempt.json、result.json、三原调用JSON、probe-original-stdout.txt/stderr.txt及receipt-audit.json。audit.py只读原本机回执，核验完整字节长度/SHA/实际归还/计数PASS，不重放probe、不调用设备。审计PASS不等于诊断准入PASS。

原记录文件SHA256：features `72a8eaef8ed474a381f354835aaca689a50860db4cd9ee3f737ba3aa8f744c3b`；context `cf68864dc3a0c77dd089d44667f9faa359b45c5db94bde3921b7b2f2ae056d4c`；probe `138006ae256a6d8a48de3913d849f683c8a635d524132a22e5fd5736e89ead85`。

报告及工具阻断项主动发送负责人，后续集中修复和复审另派；没有自动执行下一批或媒体预置。D1未通过、M0未启动、历史问题不关闭。
