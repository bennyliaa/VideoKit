# C12 缺陷与证据矩阵

以 docs/tester/D1_C11_TEST_REPORT_V1.0.md 为正式输入：平板20 PASS/2 FAIL/23 BLOCKED，手机45环境阻断，结束无在途/服务；历史结果只读。

| 编号 | 本批实现 | 本机证据 | 设备/验收剩余 |
|---|---|---|---|
| C11-T01 注册握手 | 同步metadata兼容、oneway拒绝；16字节固定reply与10～28错误；内核caller/flags/分支日志；合法致命失败回报及首错保留 | RegistrationSelfCheck、Android编译、包/静态检查 | 具体C11 flags仍未知，需C12实际REGISTER/HELLO/帧/负例新证据；不宣称唯一根因已证 |
| C11-T02 未知绑定撤销 | 独立绑定撤销状态与UNBINDS执行器；cancel/迟到返回/HELLO失败主动撤销；无锁跨Context IPC；原子一次性start；unknown不借unbind清零 | BindingSelfCheck、Generation反例、真实方法只编译 | 真实解绑、迟到注册、未知计数/槽保留、显式失败恢复与第二任务，均NOT_RUN |
| C11-ENV01 手机禁用 | 保留只读状态/组件/Service硬预检；不找不存在的启用按钮 | 既有16环境守卫＋12执行器脚本检查 | 环境未恢复则整组ENVIRONMENT_BLOCKED，不绕过 |
| C10-T01/T02 延续 | C11 trace原逻辑不变；首次代次/死亡/两槽保持，失败端点仅用于撤销 | 源码等价/继承反例 | C11前置失败未到达的路径不冒充通过；signal0仍FAIL |
| host7/legacy8 | Media3、输出双轨/READY/abort/reconcile、共享退出取证不变；companion仅legacy回归 | 原纯检查、源码等价、包/依赖锁核验 | C11已有PASS只作为基线；C12仍完整回归，旧ordinary UNKNOWN不自动重跑 |
| 来源/框架/资源 | FFmpeg8.0.3及五原库/quota不变，无新权限/组件/模型/codec | 原库hash、完整源档/许可、266对象/608依赖、实际APK核验 | 有限Debug准入，正式Flutter/Kit/AAR/16KiB设备/全P0/发行未闭合 |

实际断言/方法/文件计数以本批local-check-results、device_plan、candidate-self-review、freeze-summary动态结果为准。只一次完整冻结交tester。
