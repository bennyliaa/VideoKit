# D1 E13B metadata语义与边界 V1.0

日期：2026-10-18。读取路线按Android12/API31固定源码与已有Lenovo TB138FC raw核对：

- [AMS命令分派、活动列表及进程尾标记](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java)：processes分派在8320附近，活动列表8635–8659，进程尾标记8874。
- [ProcessList输出顺序](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ProcessList.java)：3780–3860在进程/isolated信息后调用活动列表，再输出OOM及其余状态。
- [ActiveInstrumentation完整多行格式](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ActiveInstrumentation.java)：99–129输出class、finished、running、targets、targetInfo、权限与arguments。

没有下载SDK/依赖、没有查询设备。上游固定tag只证明API31路线/格式契约，已有四份原厂商完整raw验证本机支持的首尾与阶段顺序；不是本次设备现场观察。

## 采集、完整性与状态

每个直接客户端仅一次无包过滤processes查询，不过滤其他项目。原命令退出码由同一shell在流尾显式追加，不能因pipeline右侧退出0丢失左侧失败。纯shell解析完整流，必须唯一首行、All known/OOM/最后非空尾标记及唯一原exit0；尾后新诊断、重复头、未知阶段、缺段、超限均不接受。

输入有限检查为524288B/8192行/单行4096B，活动块3000B；这是Android端内部metadata扫描界限，不增加保留到PC的4KiB记录/64KiB客户端/总2MiB文本。触及界限保留BLOCKED，不截断后宣称完整。解析器在发现问题后继续排空同一流，避免提前关pipe充返回；55秒原操作未返仍按既有custodian保管，不强杀。

活动块从准确标题到下一OOM阶段完整保留，包括每个原index、全部续行、unindented字段和仍在全局列表中的FINISHED项；不按pkg过滤、不把finished当已空。每个项需要class/finished/running/target/targetInfo/arguments结构，缺字段不当合法空闲。无活动时仅在全结构闭合且没有活动标题/项/hint时输出IDLE。IDLE仅指该instrumentation快照，不证明总体设备空闲、epoch授权或SourceReleased，原controller独占证据及产品资源门仍必要。

ACTIVE完整记录先写入原stdout，再退出73/ENVIRONMENT_WAIT，后续metadata、部署、六方法均不得继续；BLOCKED记录退出21/过限22，未知不当空闲。只环境等待、不抢占。稍后有限复查由现有负责人/调度安排并计入实际原48总账，不高频或免费加查询；余量不足先交预算缺口，不重置账本掩盖已有消费。

PC消费可在既有tester controller内调用纯函数tools/process_record.py，仅读原返回字节，不是新的PC进程/ADB wrapper。还必须核完整M记录、所有34stat/18control、pair/data与原finish/PC归还；原exit0或解析IDLE都不替代这些门。

## 本机证据边界

四份完整E11厂商历史raw均逐字节pin并复制为本机输入。ACTIVE、多个对象、FINISHED和跨行是按上游契约插入历史raw的受控变异；unsupported/非零返回/缺头尾/未知OOM/空活动标题/缺字段/过大活动块/超长行/截断诊断等为明确标记的反例。20个最终shell分支均按期待通过；它们不是设备测试PASS。

另外使用与三argv内逐字节相同的collector定义，本机替换dumpsys为读上述文本，验证IDLE继续、ACTIVE完整保留后停止73、unsupported即使exit0也阻断、左侧非零不被pipeline吞掉。没有执行真实query/remote脚本。32个本机语法核对及完整argv解引号一致性不代表API31现场所有字段已取得。

本批不重新测试绑定/source/native/信号，不更改版本/安全模型或扩展诊断框架。原E13A P1/P2静态关闭、原六方法未来范围、全部历史结论及D1未过/M0未启保持。
