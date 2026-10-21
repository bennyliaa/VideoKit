# D1 E2E 新actual自有回归批次准备开发需求 V1.0

2026-10-17。负责人全文读E2D复审，新增阻断0，正式批准准备一次新actual自有文件全61回归批次，执行交tester整包核验后进行。新docs/coder/d1e2e保留旧C/D及历史FAIL只读。

绑定E2C修后生产32源码/manifest/profiles与10原产物，E2C freeze bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179及D确认。不编译/修改生产代码；只新增有限运行wrapper、批次机器授权/原父PID/unique root/CREATE_NEW预约与claim门禁，原E2B诊断许可不得复用。wrapper只允许自有SYNTHETIC+ACTUAL_OS_OBSERVER，mock/REAL_IO拒绝；完整性不符、fresh内存不足或其他前置拒绝也不得自动重启求低值。新批准最多一次G/full尝试，预约在G前持久一次，启动后即消费，不退款。

生产src/配置若因绝对旧路径/入口冻结不能安全原样运行，只给必要wrapper差异及身份映射，不能擅自解除生产范围门禁或改成真实素材。所有新代码/脚本独立审查，默认Inspect、不创建root或消费许可；tester正式启动才创建唯一新自有根/fixtures。保留原R LoadFrom与修后compact完整链。

全部门槛沿E2D报告§4：fresh≥2GiB；G PF前固定基线16/+12线程、256/+64句柄、WS/private256MiB/+128；JR HELLO64/+32线程、512/+128句柄，J768MiB/R512MiB及+256；24/6/8、累计cell64/活8、452/544/101query、IO/事务/32记录/180秒及外200仅停止等待、1s/201/gap2.5/0.1、global事件104320/metrics26752保持。不强GC/重启择低/提限，首FAIL/PENDING保留并有界原owner收尾。

交D1_E2E_DELIVERY/EXECUTION_PLAN/EXECUTION_APPENDIX_V1.0.md、完整源码/依赖ZIP与产物hash、批次manifest/只读verify/静态检查证据，明确一次启动命令/拒绝/停止和不在途。只做静态/合成无OS守卫检查，不运行新G/JR/full/诊断或媒体。自有准备fixture≤2MiB/证据≤4MiB，执行额度也独立有界并计总账；执行输出不纳入不可变代码hash集合，另结果manifest收取。

一次整包主动报告负责人，等待tester核验及执行，不自行消耗新full许可。无真实test_media/stat/hash/PF媒体/runs/设备/Gradle/ADB/下载；JNI/P0/C14/历史FAIL及五产品变体限制保持，D1未通过/M0未启动。
