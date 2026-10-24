# HOST_TRANSACTION02_SOURCE_BINDING_FIX

本包仅集中修复01静态F01：原source task遗漏和不同原authority可能混用。当前开发一次严格JDK编译及一个串行worker通过，仍待独立整包B，不代Android/D1通过。旧01两开发FAIL、独立8+3有限PASS/整包静态FAIL均保持。

## 准确接口与私有编码

Binding保存原E13SourceGroup/Identity引用、sourceTask及uid/pid/instance/epoch/generation快照。requireSource与require逐字段核验后核同原对象，不能让新registry generation1充当原权威；同一个原authority的合法新Binding wrapper仍可用。原SDK API没有新增字段或第二身份/资源服务。

HTB2是版本化私有数据key：长度前缀+精确UTF16 code units及固定宽度整数，再Base64；task被包含，不trim/lowercase/分隔符拼接。私有key最大2048字符以守4096B record边界，超界在Binding构造期拒绝；不是修改SDK公共SourceIdentity的容量合同。授权永远用typed字段和原引用，不靠key相等。相同字段的不同authority可能编码相同，但不能通过构造/移动/RecoveryRef的live binding门，key不是可携带授权token。

新本地帧为VKH2，record为HTX2。旧VKH1/HTX1拒绝，不读/迁移旧原事务、不补COMMIT。record旧header只做共享production version函数的纯输入负例；正确当前record和同grant readonly QUERY真实运行。HOST_ISOLATED_FORMAT_V1仍为原受控validator端口tag，不是MP4/Android隔离格式或RCE安全证明。

## 本批实际验证

case-plan.json预声明8原real-file场景+4新增矩阵组+3原authority回归。同task其他字段完全相同的SRC_A/SRC_B错构造在目录/host登记前拒绝；原source完整排空后错Binding移动仍在产品IO接纳前拒绝，source/target不变；错task RecoveryRef在业务record读取接纳前拒绝。全字段相同但不同group引用也分别拒绝。IO接纳计数是当前代码分支诊断，不冒全部OS读写API拦截。

原opaqueTask构造快照正例实际通过：委托host访问器改label，但原已捕获task/grant不重定向，原SourceTask/绑定仍不变，原内容校验→READY→COMMIT→QUERY完成。全owner归还、首错/UNKNOWN保留、原ACK/worker尾段、双consumer和旧epoch晚读原门继续成立。

本轮固定Python/JBR、新独立根的准确命令按正式单通过工具require_escalated自动审核；仅本批生成临时源/输出/硬链接/发布文件，无管理员、ACL/防护修改。实际Popen前order.json冻结src/lib/argv/cwd/显式env快照hash/预算，env原值不入档。首读前同调用monotonic计时在first-read-clock.json，不从prepare重新计时。无修复重跑、Gradle、SDK/ADB、设备、网络或Git。

R03同bytes对象替换、TOCTOU/原FD竞态、隔离攻击、真正应用崩溃/跨进程恢复、完整数据库及压缩音轨/AV同步未运行或不在范围；不因task修复关闭它们。

## 完整材料与独立入口

读REPORT.md、API_MAPPING.md、manifest/seal及evidence/attempt01原回执。候选自己的源码/结果冻结后，只能在准确新外部root执行独立入口，不覆盖开发attempt或旧01：

`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -I -X utf8 -B D:\CodexProjects\VideoKit\docs\coder\d1-host-transaction02-source-binding-fix\run_batch.py --output D:\CodexProjects\VideoKit\docs\tester\D1_HOST_TRANSACTION02_SOURCE_BINDING_FIX_REVIEW_EVIDENCE\<new-scope>`

review模式要求候选manifest、canonical/nonreparse及准确root下一层新leaf，source/libs只读，classes/原文件测试只写该新scope；一个严格--release11编译+一个串行worker，未超观察时不强杀原对象。需负责人另正式派B并将该准确命令交工具审核，不能把本开发命令批准当未来泛授权或修改ACL。当前不自动启动独立B/设备。
