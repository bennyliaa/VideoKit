# C11 缺陷与验证矩阵

输入：D1_C10_TEST_REPORT_V1.0（平板38 PASS/2 FAIL；手机40环境阻断）。C01–C10历史结果不改写。

| 编号 | C11实现 | 本机验证 | 待设备验证/状态 |
|---|---|---|---|
| C10-T01 | status0也读取App trace；原系统字段与trace分栏；有界读取、身份/进程/时间验证、冲突拒绝、主线程拒绝、真实pending隔离 | TraceCapture真实输入流反例和ExitRecordRules；Android编译 | 两个原始SIGSEGV入口仍须严格系统signal11；status0仍FAIL；OEM trace可见性未证 |
| C10-T02 | WorkerGenerations固定首次端点与身份；逐代次死亡；onBind登记；额外端点仅撤销；绑定撤销、全部worker死亡及在途返回后释放 | 代次、重复/迟到、取消/HELLO模型、上限/溢出、第二槽独立反例 | 新增真实Binder/隔离进程竞态测试只编译；未宣称设备修复闭合 |
| C10-ENV01 | 沿用只读installed/enabled/component/service预检、脚本硬停止 | 16环境守卫、12执行器检查 | 手机系统禁用继续ENVIRONMENT_BLOCKED；不enable/卸载/清数据 |
| host回归 | Media3、输出验证、双轨ready/reconcile/abort逻辑除包名不改 | 原纯检查及源码等价/包审计 | 7项整批回归；不能借CPU修复绕过输出安全门禁 |
| legacy回归 | companion仅历史回归；共享ExitEvidence与TombstoneWitness变化明确 | 原纯检查、包审计、严格native-abort白名单不扩大 | 8项整批回归，新增trace冲突可能使原入口更保守失败，不能改判通过 |
| 资源/许可 | 两CPU槽、FFmpeg8.0.3和配额不改；额外登记记录上限不是解码许可 | 继承库hash、266对象/608依赖、源档与包审计 | 真实峰值/设备页大小/全产品隔离不由本机证明 |

整批验收及门槛见 EXIT_EVIDENCE_DESIGN 和 DEVICE_APPENDIX。本机计数以 local-check-results/candidate-self-review/freeze-summary 动态生成结果为准，不沿用C10硬编码。
