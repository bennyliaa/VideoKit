# D1 CONTRACT03 COVERAGE_CHECKPOINT01 覆盖报告 V1.0

2026-10-23；tester。依据同名正式测试要求，仅审冻结 CONTRACT03；本报告是 Git 检查点前冻结的测试结论，Git 实际结果另见同级 `D1_CONTRACT03_COVERAGE_CHECKPOINT01_DELIVERY_V1.0.md`。

## 结论

**FAIL_TEST_DRIVER_PRE_PERMIT_TARGET_NOT_COVERED**。本次唯一动态尝试在测试辅助脚本生成许可前发生 `NameError: name 'BACKEND' is not defined`。没有进入产品构造、Gate.prepare 或物化 proof 读取；物化内过期目标仍未覆盖。该错误属于 tester 脚本，不是新确认的产品源码缺陷。未修补原驱动、未追加第二次尝试。

source 门采用负责人已接受的原 B 单字节追加补充层，准确命中 `OWNER_SOURCE_PIN_ENTRY` 且原资源返回。原 `WRONG_OUTPUT_SOURCE` 大输入实际命中 cap、原 9s 过期在前置阶段停止的两项失败继续保留，均不改写为 PASS。原完整 B 的 `FAIL_TARGET_COVERAGE_GAPS` 不变。

本批原 worker 的 wait、两 reader、流与原 HANDLE 唯一关闭回执均已返回。结合准确异常位置和冻结调用路径，产品 claim/lease、checker 和阶段观察线程尚未创建；没有新增资源 UNKNOWN。真实 SDK/ADB/Native route/TCP/help/设备/Gradle/媒体均 0，D1 未通过、M0 未启动。后续测试不自动开始。

## 来源与已接受层

| 项目 | 准确来源或结果 |
| --- | --- |
| 产品源17 | `4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93` |
| gate9 | `9cff279ddb9e60632b1422dca16af0dac4ab1922fb6b0b27c5a232055e439d72` |
| plan | `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8` |
| 开发 SELFCHECK02 | 报告 `9acdf4089a4134997e53adf6a765b11ca4f6ca48a35a256eeaa21b7497f30246`；13 PASS / 1 已知时限 FAIL，原状态不变 |
| 独立 A | 报告 `a6f2f4fe2cf1e7d8553d27f428f79753251ab8653e7d579a4fab621f506d7ea2`；400/400 限定语义与纯静态检查已接受，未重跑 |
| 完整 B | 报告 `f67cdf23cf0132fe6ae1d9ef50976ef91de06035e5e729cf2a77278c1f96925b`；10组 PASS，11个有限故障9个精确命中、2个原未覆盖；本轮引用，未重跑 |

源和原完整文件始终保持。返回后的只读核验：产品98项 / 1,245,040B，开发484项 / 5,286,017B，A408项 / 3,877,819B，B744项 / 2,668,183B，全部 bad0；两原 ZIP 的 SHA 与唯一成员数99/485均匹配。未读取任何旧对象运行态或重开原失败 scope。

## 先固定的时序方案

从原 B 冻结的真实完成记录抽取11个 proof 起点样本和4个已完成首控制器准入样本，保留每个文件 hash 与原 tick。proof 起点相对 scope 为3.344–10.375s；proof 到首控制器外层开始的最大上界1.687s。用后者保守包住物化 proof 读取完成阶段。原9s失败只有前置阶段截断事实，未被当作读取完成的上界。

加入输入准备0.5s、两端各0.25s余量，静态区间为 `(12.812s, 13.094s)`，固定 TTL `12.952s`。上限来自原 proof10s/gate30s；原 materialize 等到 expiry+20ms 后按 whole→gate→proof→permit 原排序检查。该区间只是冻结样本支持的经验规划，不能保证未来调度；实际阶段、时刻及原返回必须全部满足才接受。此次产品未进入，未获得任何新的实际时序验证。

订单 SHA `7dbd9da8b264892f298336cb22582401397e8f38e0be4aae3fb47a0b7bf9bace`；batch `af2619b2-fd06-4c35-8860-504294d65255`。新输出根为 `D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/fixtures/cc01-7d59668f`，没有续跑 f-7。预先固定一次范围、输入函数及源 hash、TTL 和预算。通用启动 profile 纯检查已完成；精确 checker profile 检查代码因前置异常尚未运行，实际 permit/approval 双 hash 也未生成，不声称它们已完成。

## 唯一尝试的实际阶段

| 判据 | 实际证据与裁定 |
| --- | --- |
| worker 准入 | PID18652，creation FILETIME `134372333676108344`；自身命令行/nonce 与原 H 身份绑定 |
| 许可/approval | 未生成；模板求值在引用缺失的 BACKEND 时中断 |
| 产品构造 / Gate.prepare | NOT_RUN；仅调用无资源的 fixture 模板方法，不调用产品构造函数体 |
| materializer-proof-read 原读取返回且许可有效 | NOT_RUN |
| expiry 后准确 PERMIT_EXPIRED_OR_FUTURE 且早于原时限 | NOT_RUN |
| activation / 控制器 | 均0，未创建 actual-home |
| 产品 claim / 原唯一释放 | 未创建，释放 N/A；不伪造产品 abort-release 回执 |
| 原辅助归还 | 原 wait、reader join、流和 H 关闭均返回；外层 exit1，worker exit1 |
| 重试 / 新范围 | 0 / 0；原 once 保留，不修补后复跑 |

异常回溯准确落在 worker.py 第20行的 `permit(...)` 调用、抽取的 input_definitions.py 第6行。`BACKEND` 本应来自已导入的原 win32_route 常量，但传给抽取函数的独立全局字典漏掉该键。发生异常前只建立 W/one 空目录，未写 review/permit，未创建 checker、Popen 包装、audit 或观察线程。本轮 `worker-final.json` 没有生成；资源结论由外层原回执、异常前缀和实际产物共同支持，不用工具退出码或空 custody 单独代替证明。

返回后增加18个文件型阶段/时序判定模型，仅说明同码提前拒绝不接受、经验区间和原失败保留规则，不调用产品函数体，不计为产品动态用例通过。

## 预算与保全

预存180s / 150s停新增、并发1 / retry0、最多4个自有辅助、读取256MiB / 2048次、产物16MiB / 512项、单流1MiB；原生产600/30/20/10/120及各字节/source门未改。

实际启动一个 worker，checker0；worker0.328s、外层0.359s，stdout0B / stderr763B。后验盘点早期材料25项 / 98,924B（含纯模型，不含后验裁定文件本身、报告及Git材料）。外层记录读取84,896B / 16次；worker因异常无最终账本，按已执行的确定性 self_io 前缀重建96,980B / 19次。这是有明确来源的逻辑读取核算，不冒称 worker 自报或完整 Python/runtime 物理IO总量。返回后冻结校验读15,011,782B / 1759次，全部文件作用域正常关闭。

原98/484/408/744及两ZIP、所有旧 FAIL/UNKNOWN/once/N2/预算原账目均未改写，不退款、不补ACK、不查询/kill/二close旧资源。test_media未写入。没有启动新PREAUTH浮动候选或任何设备测试。

## Git 审阅检查点与交付

本测试报告及准确 manifest/冻结回执完成后，才按正式工作单创建当前 HEAD 派生的唯一 WIP 分支、提交准确白名单、push指定私人仓库并创建草稿PR。逐文件 hash、排除理由、许可/秘密/大小检查和 stage/diff 结果单独保存在本批 `EVIDENCE/git`，不改原完整 manifest。Git 中排除原始二进制、ZIP、媒体、第三方分发材料、运行时、凭据及新PREAUTH浮动源；本地完整 manifest 仍可引用这些排除材料，不声称远端能独立重现全部历史二进制。

最终分支/commit/PR或实际阻塞另写交付报告，避免让已冻结测试报告自引用后续 commit SHA。仅集中回交负责人，不逐问题交接或擅自进入后续测试。

证据：[后验裁定](D:/CodexProjects/VideoKit/docs/tester/D1_CONTRACT03_COVERAGE_CHECKPOINT01_EVIDENCE/post-audit.json)、[时序依据](D:/CodexProjects/VideoKit/docs/tester/D1_CONTRACT03_COVERAGE_CHECKPOINT01_EVIDENCE/timing-envelope.json)、[原外层返回](D:/CodexProjects/VideoKit/docs/tester/D1_CONTRACT03_COVERAGE_CHECKPOINT01_EVIDENCE/outer-final.json)。

