# D1 C12 注册握手与未知绑定撤销整批修复

> C11最终报告已落盘审阅：docs/tester/D1_C11_TEST_REPORT_V1.0.md。C11-T01为注册握手失败，C11-T02为未知绑定取消/撤销收敛缺口，C11-ENV01为手机禁用。tester明确22个实际方法全部结束、无残留服务/在途，原23项BLOCKED保持。交付矩阵用上述编号，C10原代次/取证阻断亦保留，不能因C11前置未过而称已解决。

> 正式派发：C11平板45项已完成20 PASS/2 FAIL/23 BLOCKED，手机45项环境阻断；结束进程记录为空，tester正在最终报告收敛。负责人批准仅本机开始整批修复，不等待报告排版；最终编号落盘后一次对齐。仍不设备、不改C11。此段覆盖下文准备状态。

日期：2026-10-16；状态：准备，等待C11设备批次确认结束后负责人正式派发。当前仅只读定位，不修改冻结C11。

## 输入事实

C11平板正常MP4/AVI前置FAIL，CPU5 PASS/2 FAIL/23 BLOCKED，host7/legacy8当前记录PASS；最终编号以C11集中报告为准。onBind实际报CPU_REGISTRATION_REJECTED，两个方法各三worker退出并被系统重建，无注册代次和帧；最终unknown worker/slot保留。第118行合并了transact返回false、ACK错误及尾随数据，缺运行分支，不能断言唯一根因。registrar用flags!=0拒绝所有非零flags是已确认兼容性缺陷；同步Binder可能携带系统附加标志，具体设备flags尚未记录。未知绑定cancel无法STOP且allDead=false导致不走unbind是另一已确认缺陷。

## 整批实现

1. 修正registrar同步事务标志处理。按Android Binder实际语义拒绝oneway，兼容同步框架附加标志；不得以“客户端传0”要求接收端恰为0。保留descriptor、code、内核caller UID/PID、task/epoch、输入形状和长度、隔离身份校验；不接受PID0、不弱化权限。明确控制和框架元数据标志区别，实际flags与认证失败原因脱敏记录。核查其他Binder入口是否同类错误，必要适配限本批。
2. 注册握手返回固定有界ACK/错误枚举，不跨不可信边界反序列化异常。分别记录transact=false、ACK magic/长度错误、尾随数据、会话/身份拒绝、endpoint/重复/溢出与回调异常；保留首次启动原因和独立cleanup。拒绝必须可定位，不能只靠generic CONNECT timeout猜权限或死锁。
3. 将未知绑定撤销与死亡/释放证明解耦。bind已接受但未注册/未连接、HELLO失败/超时、cancel与bind返回交错均可有界安排撤销绑定，关闭自动重建；不等待allDead后才unbind。晚到bind返回/注册/连接仍受代次与终态门禁控制。解绑不等于死亡，不以解绑或回调超时伪造未创建；未知worker/在途/解绑失败继续quarantine。需要明确query/recover事实与结束条件，避免既无限重建又只保留槽位。
4. 沿用C11固定首次Binder/身份、逐代次death、额外控制端点与全局预算，确保没有额外START/source/解码许可。未知/溢出不能释放新槽，另一任务必须独立继续真实解码。控制取消不阻塞主线程，注册/STOP/解绑不因锁等待互相卡住。不得用新crash handler、高权限组件、companion或自制媒体实现绕过问题。
5. 有意义反例至少：同步flags0/框架metadata位、oneway及组合拒绝、未知code、错误descriptor/session/kernel identity、异常ACK/尾随；bind已接受无注册后cancel、迟到bind/HELLO与cancel、重复取消/解绑失败、旧death与新连接交错、未知资源不能借解绑清零。纯规则不能替代实际registrar事务；新增真实Android入口须验证正常注册与拒绝诊断、取消收敛、另一槽存活。分开记录每阶段原始证据与最终释放。
6. 不更改Media3/FFmpeg8.0.3/配额、白名单及Debug-only准入。正式Flutter＋独立Kit/AAR、全P0和许可证边界保持。C11取证设计原始system status0 UNKNOWN/FAIL门禁保持；前置恢复后才单次验证未执行的代次/trace变化，不同条件失败不冒充C10/C11已闭合。

## 交付

对齐C11最终报告全部缺陷编号，集中完成实现、竞态反例、自检和构建冻结D1-20261016-C12后统一交tester。仅本机，无ADB/设备；C01–C11/素材只读。交docs/coder/D1_DELIVERY_D1-20261016-C12.md、缺陷/设计/框架映射、实际测试方法/依赖计划、源码/证据/产物hash及归档核验。保留失败尝试证据，不逐项编译/小交接、不无理由clean。D1未通过，不进入M0。
