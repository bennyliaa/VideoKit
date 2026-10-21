# D1 E13K 机械自检 V1.0

2026-10-18；一次策略javac exit0，R1业务源未重编。实际193成员逐个核，192完全相同，仅E13JReadOnly.class变化；包括新编出的nested3类也逐字节相同。真实javap -p -c -constants只消去准确SHA/CP数字索引/水平对齐空格后完全一致，保留所有指令偏移和分支目标，不把字节比较不等隐写成等。

最初文本断言未归一javap CP数字宽度引起的两处对齐空格，曾报NON_POLICY_DISASSEMBLY_DIFFERENCE；原javap输出/原build工具保留。后续仅完善文本归一证明，没有再编译或改业务。真实E9Record精确解析/重序列化及实际最终JAR反射批准常量通过；describe安全执行，不运行有效dispatch。

脚本完整AST、真正生产policy前缀（owner分配标记之前）精确RequestPath/hash/JAR pin/批准字段通过；仅摘要代码对明确合成JSON验证≤128B，没执行launch或Process owner。原observer owner主体同R1实际字节相同。outer-budget真实PS序列化保守上界8157、余35，原始stdout/stderr/exit、机械绑定receipt保存。

没有Socket peer测试、APK/Gradle/native、SDK或长套件；不拿已过功能再循环。这里只是coder机械自检，等待tester独立机械PASS；无新执行结果或UNKNOWN。本轮仅发布绑定准备和机械自检，未运行launch、有效--g-readonly或observer原owner，不真实5037/设备/SDK/旧handle/PID/处置。三历史UNKNOWN独立不补ACK，D1未过/M0未启、T07未派、P0/许可与原v17边界保持。功能review沿已通过R1，本次机械验核另存，不自循环。
