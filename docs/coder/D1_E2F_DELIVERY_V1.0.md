# D1 E2F 包装判定修复与只读重评交付 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2f`，依据 `docs/milestones/D1_E2F_CODER_REQUIREMENTS_V1.0.md`。本批只修复完成判定、检查其离线负例并重评原E2E封存执行证据，没有新actual许可或运行。原E2E最终 **FAIL、G exit2、原调用工具exit1、160条断言及已消费预约**保持不变。

## F01修复

原包装在原生产Cleanup已返回后，要求 `rows==61`。原Flow.finish同时记录PF与61场景，故完整原checkpoint为62；这导致E2E实际正常完成后被包装改写为FAIL。原153条准备检查没有覆盖PF与真实结果计数的组合。本批不以单纯改成62代替完成证明。

新 `tools/e2f_wrapper.py` 是离线包装判定入口，采用三个必须同时成立的门槛：

- 原封存、原源码与三项原输入hash身份完整，旧FAIL/退出码/断言/许可未改。
- `completion_evaluation.py`核PF首条、批准61精确ID集合/唯一性/批准顺序、逐行control/data/query/time、原断言及原global每槽完成证据，并单独核GC/n01..n31与n32实际关闭返回。
- `resource_evaluation.py`核原父子/助手身份、实际OS观察及资源界、Hub/cell/IO/native/日志/原退出、完整输出清单与独立预期字节/hash。

计数相同但缺行、重复、乱序、额外、未完成、非批准错误/WAITING、GC仅有意图、资源FAIL/未知或输出篡改均不能支持重评。原E2E `e2e_driver.py`、原最终FAIL与所有原证据不修改；最小差异另以新包装函数及 `evidence/minimal-diff.json`记录。新入口不含actual启动模式。

## 重评输入与结论语义

固定原batch `D1-E2E-201dffc63b60405da3046f21fa7ff26d`，原自有root `e2e-201dffc63b60405da3046f21fa7ff26d`。输入直接只读原d1e2e，不重建fixtures，不从tester摘要替代底层原输出。

| 原输入 | SHA256 |
|---|---|
| evidence/e2e-freeze.json | aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a |
| execution/result-manifest.json | baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea |
| 原result-before-close.json | 702d8505e16bf504564179c14477e7cfe50af35c922531034c66645d6bc79032 |

独立输出 `d1e2f/reevaluation/evidence-reevaluation.json` 命名空间 **EVIDENCE_REEVALUATION**。`SUPPORTED_ORIGINAL_TOOL_FACTS`仅指这一次原场景、资源、输出及收尾证据获得新判定支持，不能命名原批PASS、追写原文件、改exit、退款、计新actual通过或放行真实媒体。原E2E整批通过数仍0；本批newActualAttempts/newActualPasses均0。

本次452条离线断言全部通过，与原160条执行断言、旧153条准备检查及原452控制动作预算分列，明细见 `evidence/offline-checks.json`。源码集合79文件；源码/原产物/旧封存、离线输出和三文档由本批freeze及只读verify收取，ZIP与SHA由封存摘要及负责人完整交接报告给出。只读audit已通过，完成与资源两个判定均accepted。

## 生产、资源与范围

32生产源码＋5原配置、E2C.dll及9 class共10产物、555B原r-helper从E2E按原E2C身份逐hash保持，无生产更改、编译或修复编译。C/D及更早依赖、E2E完整源码ZIP只读承接。新manifest只描述离线范围，不授权新root、G/J/R或actual。

原G PF前baseline不重置，原J/R HELLO实例不替换。所有原资源、query/IO、452/544/101、180/200、2GiB fresh、24/6/8、cell64/8、日志与observer界沿用；本批没有再测OS。离散采样峰及源码锁存guard的可采信范围、逐query/逐采样duration未单存的边界详见重评报告，不编造缺失数值。

原结果读取与hash严格≤16MiB/1024文件，源码完整性另≤256MiB/8192，64KiB块。新包不复制原L/C/Z或.out为新fixtures；fixture新占用0。新日志/证据含重评与seal合计≤4MiB，源码/依赖ZIP另作为开发产物计账。不删除旧失败证据换额度。

所有检查仅JSON/bytes/内存副本，不导入Engine/Native/Channel/Hub/Popen或OS采样器；没有实际PF/full/mock、设备/Gradle/ADB/下载/test_media行为。JNI/P0/C14、历史G369/+209与R519 FAIL及五产品namespace/READY限制保持。D1 NOT_PASSED、M0 NOT_STARTED；完整冻结后一次报告负责人，等待tester独立复核及负责人裁定。
