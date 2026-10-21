# D1 E4A-T1 原 stdin 关闭证明修复交付 V1.0

2026-10-17。候选D1-20261017-E4A-T1，按[开发要求](D:/CodexProjects/VideoKit/docs/milestones/D1_E4A_T1_CODER_REQUIREMENTS_V1.0.md)集中修复[独立审查](D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T_TRANSFER_REVIEW_REPORT_V1.0.md)的E4AT-F01/P1，待独立复审。新目录[docs/coder/d1e4at1](D:/CodexProjects/VideoKit/docs/coder/d1e4at1)，旧T工具及E4A/E4/C14冻结不改，原81407B设备残件不动。**无ADB、设备、真实媒体stat/读取/hash/复制、Gradle、网络或下载；D1未通过/M0未启动，所有原P0/历史FAIL保持。**

## 修复与实际归还条件

原T returned谓词缺stdin_closed，会出现stdin.close抛错、writer/source/其他pipe/原process都结束却删除原Job的路径。T1在[exact_process.py](D:/CodexProjects/VideoKit/docs/coder/d1e4at1/tools/exact_process.py)集中修正：

1. Popen实际返回后，保存原stdin对象及stdin_allocated；writer的write/flush/close都使用这个原对象。实际closer调用前记stdin_close_attempted，只有正常返回才置stdin_closed。原关闭异常保在stdin_close_error，不能把错误文本、raw.closed、exit0或线程结束当证明。
2. ownership_returned对实际分配stdin要求stdin_closed，同时继续要求原wait、writer/source、stdout/stderr关闭以及所有原线程真正结束。close抛错/未返回均UNKNOWN_RETAINED，原全局集合继续持Job→process/stdin/raw pipe/source/argv/异常。下一collect和transfer_file均在任何新进程/源预检前拒绝。清理路径不再或另行close stdin，不重复close求成功。
3. 屏障内未返回时保原owner。最后实际close/source/drain/wait/thread都返回后，retained_owners或下一明确请求只观察原事实并移除已证归还项；不执行IO/close，不重设计时、不清UNKNOWN、不改原字段。原超时结果仍NOT_ADMITTED，即使资源后来归还，也不续跑原传输/发布。
4. 启动前要求绝对路径、普通非symlink可执行文件，不隐式PATH查找。此预检拒绝发生在Popen前，确认process/stdin根本未分配；仍须实际source.close返回才能归还。字段stdinOwnerAllocated/CloseAttempted/CloseReturned都保false，不伪造close。已创建process但实际stdin=None时也不close不存在对象；其他原资源照实收尾，缺少请求输入管道使本次NOT_ADMITTED。
5. 若已进入不透明构造器而未取得返回对象，不从异常或None推断“肯定零分配”；creation_unknown及原startup异常保留，保守UNKNOWN。它与明确启动前拒绝不同。不能借这个分支弱化实际存在source/drain/wait的归还要求。

独立落盘长度/SHA、metadata-only碰撞、hash前长度界、一次attempt、残件归档/同目录发布、安装提示和整体run-as引用沿用T1随包完整源码；fixture_transfer.py与fake_child.py逐字节不变。没有扩展传输通道、设备路线或产品功能。

## 生产路径的有限本机证据

[local-check-results.json](D:/CodexProjects/VideoKit/docs/coder/d1e4at1/evidence/local-check-results.json)：一个MAIN、零修复，08:43:52—08:43:55，**63项新断言PASS**。六个独立case解释器、其中7个实际fake子进程；未重跑/叠加旧72项。五个生产/检查输入的原hash、每case原argv/退出/日志/JSON随包绑定。

每个case通过真实生产collect或transfer_file→_run→原writer/finally→ownership_returned→原全局准入，只有实际stdin.close受控代理做假抛错/屏障；没有复制归还谓词或直接修改Job证明字段。用实际Popen/原raw FileIO、256B自有二进制或0B metadata输入，不是设备fault。

| 独立case | 断言数 | 实际结果 |
|---|---:|---|
| success_transfer | 4 | 256B实际二进制传输及文件同字节；原分配stdin的close返回，全部原资源归还，进程1个 |
| no_process | 4 | 不存在的自有exe在启动前拒绝，allocator未调用/process及stdin未分配，原source已关闭后不永久占用；随后一个独立正常调用通过 |
| no_stdin | 5 | 测试启动适配明确用DEVNULL，不分配parent stdin；不调用/伪造close，其他原资源实际关闭后RETURNED，但本次缺请求输入故NOT_ADMITTED |
| throw_before | 15 | 原进程exit0、source及所有线程/其他pipe都返回，但原stdin.close抛错；UNKNOWN、原对象/异常可达、collect/transfer双拒绝、close恰一次；退出case前registry仍1 |
| throw_after | 16 | 原raw实际closed再抛错，仍不得借closed属性/exit0推断API返回；UNKNOWN、原owner仍1，close恰一次 |
| blocked_return | 19 | 原process已exit0且drains返回，stdin.close仍在屏障内；UNKNOWN、下一调用拒绝。放行同一次closer并join原线程后才观察RETURNED，原超时仍NOT_ADMITTED；无手动清集合/二次close/续期，后续一个独立metadata调用才可接纳 |

throw_before/throw_after故意保UNKNOWN到各自case解释器退出；实际Job/process/stdin/raw/source/参数/异常由原registry强留。进程退出的OS清理**不计协议归还**，不把两个1写成统一0。六个case解释器均已结束，7个fake子进程实际结束，没有在途执行；从未清全局集合假恢复或强制GC。

blocked_return的旧UNKNOWN不可变结果和同原Job的后续RETURNED观察均保留。第二次独立metadata调用只在实际证明后发生，不能当原失败预置自动恢复；现实批次仍须按失败停止并交负责人。

## 保留、边界和下一计划

旧T完整SOURCE ZIP、原manifest/seal与来源在reference中原样保留；原日志在原冻结及完整容器内，未重测。旧T seal 3b650fd8f14956216e9fa5c9f43ebe916e5b832980a6e450515275e09425902a，ZIP faeec9c657ae813e85ed23a042eeb900f9b26bb76cced52f4bfe1d9196fa6cdc；E4A seal a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d不变。衍生map将四个继承文件绑定到旧完整容器及新身份。

调整后的[精确预置计划](D:/CodexProjects/VideoKit/docs/coder/D1_E4A_T1_PRELOAD_PLAN_V1.0.md)与tools/tablet-preload-plan.json继续executionAuthorized=false。只提议未来平板一次新临时名，原81407B残件仍须前后hash保留；MP4失败阻断AVI，不重装产品、不问手机、不重跑Binder，不碰marker/cache/旧fixture。产生UNKNOWN则保持原解释器/原owner，禁止通过重启工具/新进程洗准入；本机隔离case退出只为证据隔离，不能复制到真实流程当恢复。

source open/prehash或系统调用不返回没有绝对硬中断保证；原客户端结束/本机pipe关闭也不证明ADB远端owner已归还。先stat后sha的读取界依赖合作式稳定普通文件，非恶意并发增长的硬字节沙箱；父目录UID/pwd/非symlink及Android toybox行为仍须另批实际预检。具体349102→81407的截断层次仍UNKNOWN，不由本机close修复倒推。

完整源码ZIP/外seal与只读核验工具package_tools.py一并封存；外部报告给最终hash，verify要求--expected-freeze，不启动进程/媒体/ADB。完成封存无在途后仅向负责人一次完整交审；不自行交tester/实际预置，D1未通过/M0未启动。
