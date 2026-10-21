# D1 C11 进程代次与退出取证集中测试需求

日期：2026-10-16；状态：准备，等待完整C11冻结正式交接；当前先完成C10报告，不测试浮动源码。

## 验收重点

复验C10两项CPU故障，独立核对原始signal11、App原始reason/status/trace及任务worker身份，不以外部日志替代App能力。status0缺少已批准的独立证明时仍UNKNOWN/FAIL，不因主动注入或预期信号改判；如新设计改变取证依据，须先有负责人明确评审。对trace缺失/解析失败/冲突如实记录。

核对每代Binder/PID/UID/task/epoch固定，实际death只关闭所属代次。重点验证旧death→重连→旧回调迟到、取消与HELLO交错、重复/终态连接、真实未知worker占额与受控停止。新进程身份不能继承旧frame_count/death或借旧death释放槽位；unbind、STOP ACK及等待超时均不等于实际死亡。第二CPU槽及宿主须有真实存活与解码证据。

完整正常MP4/AVI、seek/PTS、配额/输入白名单、取消/HANG、新停止认证与恢复反例作为一组回归；host7与legacy8依据共享代码影响执行，不能替代CPU。冻结后以明确的方法清单和依赖矩阵派发，不任意缩为容易通过项。主异常与cleanup分栏，原始退出status与trace信号分栏；不回写C10历史FAIL。

## 执行和报告

两设备已有授权，实际身份/API/ABI/页大小/包hash/签名/用途、enabled和Service现场核验；手机禁用则单列环境阻断，无需重复授权或绕过。每次仅一个设备、一个明确方法，无Gradle、不更换浮动候选。保留既有包/可读数据/证据/capture，明确用途同签名更新；素材只读并核hash。每设备日志32MiB、新legacy输出32项/8MiB，采集中限制，不删除旧证据。

失败先停调度，核对远端实际执行及资源，再继续可独立项；本机ADB退出不证明设备已停。分别报告PASS/FAIL/环境BLOCKED/执行UNKNOWN/NOT_RUN，零方法和缺少完整证据不能PASS。交docs/tester/D1_C11_TEST_REPORT_V1.0.md逐项结果、集中缺陷、预算及无在途状态。整批结束不等于D1或正式产品通过。
