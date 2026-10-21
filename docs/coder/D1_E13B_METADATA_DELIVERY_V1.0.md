# D1 E13B metadata-only 交付 V1.0

日期：2026-10-18。范围：E13A-F01/P1活动instrumentation证据入口；产品仍为冻结E13A v17/ACTIVATION/ABI1，源仍接受v15。原绑定/只读入口CLOSED_STATIC_LOCAL保持；本批无APK/JAR/native构建、升版、产品用例、ADB、设备、remote脚本或媒体执行。

三份M1/M2/M3的INSTRUMENTATION记录改用受支持的无包过滤dumpsys activity processes。完整扫描同一返回流，核首行、All known processes、OOM阶段、最后非空mForceBackgroundCheck行以及原命令退出码；没有活动标题不单独判空闲，必须完整结构全部成立。保留整个活动列表所有记录、跨行target/arguments、未缩进权限字段及FINISHED但仍在列表的对象。活动是ENVIRONMENT_WAIT，不是测试失败或可抢占依据；缺段、格式/诊断/截断/过限/非零原返回均BLOCKED。

最终解析器只用shell内建，未引入或假定设备有awk；原三个小字段筛选按同一字段改为shell或sed，未加查询/字段预算。四份真实厂商历史raw空闲对照通过；活动与破坏输入是在这些raw上按Android12/AOSP格式明确构造的本机夹具，不冒新设备活动。最终20个shell语义分支、32个脚本/嵌套语法检查、4个精确collector本机替身分支通过。旧绑定九组/source/native/产品套件重跑0。

release/metadata三份sh与完整嵌入argv逐字节一致；原记录70/18/71、上界53512/27588/56360B不扩大。Windows完整命令行UTF16含NUL为23993/9899/24460，均在32767内。每份仍1个直接原ADB客户端、64KiB/55s，48操作和2MiB原分配保持，无额外PC wrapper/query。所有metadata命令仅生成，未执行。

本包是元数据覆盖层，基础三APK/JAR从原E13A精确复用，不复制重建；base-reuse、overlay-binding列实际SHA/签名/原seal/sourceZIP及scope草案。独立新metadata manifest必须由负责人正式设备scope采纳，当前actualScope/once均null。只读verify默认且实际执行，不写封装；pack为唯一显式写入口。

本机原输入/argv/stdout/stderr/exit、精确差分、AOSP依据/厂商raw pins、三脚本/全部期待记录/封印随包。开发期awk原型只作未部署参考，不是最终设备工具依赖；最终以shell结果为准。自检助手初始字符串换行及生成器查询计数断言已在本机构造阶段修正，未执行设备或改产品。

当前214483B/7R7S/0reserved及旧107218前缀/产物/fence/oldCloseACK=false只引用接受时点，未在线重读/写账，无新输出/READY/R/S。D1 NOT_PASSED/M0 NOT_STARTED，全部P0、历史FAIL/UNKNOWN、许可/renderer/audio/Kit剩余门保持。交tester集中审metadata语义及真实argv，负责人之后才可正式派六方法。
