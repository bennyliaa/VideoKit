# D1 E13A coder正式需求 V1.0

日期：2026-10-18。来源：负责人正式派发；修复依据docs/tester/D1_E13_ARCHITECTURE_REVIEW_REPORT_V1.0.md的E13-F01/P1与E13-F02/P2。旧E13冻结367项不改。

1. 依据本机SDK Context.java 4206–4215及ContextImpl注册/forget顺序，修SenderService和E13PermissionProbe：bind false、SecurityException同样对同一原ServiceConnection执行一次必要unbind/forget，不能凭kernel拒绝或accepted布尔值声称资源归还。调用前keeper；bind调用在途、正常false/true、异常实际返回、回调在途、unbind实际返回/异常分栏。未知保原connection/host/fixture/runner，不重bind/换对象/重复unbind填归还。
2. 补直接生产路径的false/SE/true正常、回调时序、原解绑异常/在途等有限证据；平台替身明确不是Android实测。普通权限结论只到bind门拒绝，没有endpoint不冒内部onTransact。其他source keeper/聚合/当前代同门真读与六方法范围保留，不跑未变native/旧套件。
3. 打包写操作必须显式独立子命令；新增默认严格只读verify入口。help/verify不得先复制/写证据/打包或构建，仅读metadata/hash/ZIP/JAR。复核负责人原误传verify在既有JAR处x失败后旧冻结字节不变，不计功能FAIL，不新建工具框架。
4. docs/coder/d1e13a新完整四文档、diff、自检原输入日志、三APK签名及hostJAR来源、SBOM、ZIP外seal及真实只读verify。目标新候选v17/ACTIVATION/ABI1，实际升级源仍已接受v15（E13 v16未安装）。受影响app/test/fixture集中一次主构建，必要repair留痕，不改旧冻结。
5. 六方法及48操作/2MiB原分配不扩；采用tester已给M1/M2/M3、34stat/18control pins，更新到新pair并附精确argv/只读脚本文本，不加预算外Java wrapper/查询；不能满足则预先集中说明。旧214483B/7R7S/0reserved、107218前缀/产物保持。

当前不设备/媒体/真实scope/once。完整冻结后主动一次交tester复审；长期真机授权及他项目占用稍后试仍有效，全部P0/历史FAIL、D1未过/M0未启保持。
