# D1 E2F 离线命令、最小差异与封存复核 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2f`。本附录中的执行仅指离线读取/判定，不是G/J/R或actual运行。

## 源码差异与只读合同

原E2E硬编码rows!=61缺陷位于冻结driver；旧文件不可改。新纯完成模块核PF＋61精确批准记录并单独核GC实际返回，纯资源模块核身份、原资源与独立输出，`e2f_wrapper.evaluate_bound_bundle`以AND聚合并强制保留旧FAIL/exit2/调用工具exit1/160/消费事实。新增 `reevaluate.py`仅有Inspect/离线重评；不提供--run，也没有新预约、claim或fixture生成器。`evidence/minimal-diff.json`记录旧位置/摘要及新函数/摘要，不将未定义的示意补丁当可执行修复。

32src＋5配置、10编译产物、原r-helper均保持原E2C/E2E字节。新manifest固定三原输入hash与E2F正式需求文档hash，明确actual/realMedia/compile=false。旧完整E2E源码ZIP及更早C/D/B/A/E2/E1E依赖入新源码集合；原执行输出直接只读，未作为新fixture复制。

## 离线命令

默认只Inspect，不读执行证据、创建目录或写原文件：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e2f\tools\reevaluate.py'
```

仅只读重新计算重评，不写新结果或原证据：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e2f\tools\reevaluate.py' --reevaluate --read-only --expected-original-seal 'aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a'
```

coder在新包未封存时，以同命令去掉--read-only独占创建一次 `reevaluation/evidence-reevaluation.json`；已有目录、输出或封存即拒绝，不覆盖原结果。tester复核只用只读形式或verify。

整包只读verify（负责人交接报告提供本E2F seal具体SHA，显式加--expected-freeze）：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e2f\tools\verify.py' --expected-freeze '<负责人报告中的E2F封存SHA256>'
```

封存文件不嵌自身hash，具体SHA在负责人完整交接报告中提供。verify核原证据与新结果一致、源/ZIP精确集合和每字节hash、原生产不变及新日志总账；不会修复输出、写原PASS、自动重跑或开启actual。

## 有界读取与检查

原结果读取按固定root与显式tester回执白名单，拒绝路径越界/reparse，≤16MiB/1024文件；原146输出包含自身清单及145成员，tester独立回执也计入结果读取。源码完整性另≤256MiB/8192，含verify中的原源码核验、新包及ZIP压缩流/解压成员读取合并，块65536B，剩余额度先于读取限制。源码与原输出hash预算不混入生产452。

本次452条离线断言全部通过。负例仅操作已读bytes/JSON内存副本，覆盖完整、缺失/重复/乱序/额外/PF缺、控制/query/时间/断言未完成、GC仅意图/缺实际返回、未知资源、输出篡改及旧FAIL不可改写，并核具体资源语义原因以免只靠hash拒绝获得假覆盖。不会导入生产Engine/Native/Channel/Hub/Popen，未进行OS/fresh/实际PF/full/mock/媒体/设备/构建。具体每项结果由evidence/offline-checks.json与seal记载，不混入原160或旧153；原452控制动作预算是另一统计口径。

新fixture占用0；新日志/证据（含离线检查、重评、source-manifest、最小差异、seal）合计≤4MiB，编译产物/源码ZIP另列开发产物；旧失败证据不删除。封存状态为E2F_FROZEN_PENDING_INDEPENDENT_REVIEW，完整冻结后一次报告负责人，等待独立tester复核，不自派新actual许可。D1 NOT_PASSED、M0 NOT_STARTED；JNI/P0/C14、历史G/R FAIL及五产品变体限制保持。
