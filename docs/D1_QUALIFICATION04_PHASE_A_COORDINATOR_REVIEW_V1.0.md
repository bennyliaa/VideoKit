# QUALIFICATION04 阶段A完整审阅与集中吸收裁定

2026-10-24；负责人已核tester静态A完整交付：报告a7d0b7d14cc0dcf581baac347f25fb286440a898eac971d00b66b5b4427cbf2a；manifest31ce729f7b7b772b34a70313a621d42b96423cfb2caa8abd7ad727aa30b363d8，14项/144121B，逐项bad0。只审冻结03、未审04浮动源、未运行产品；63项oracle均PLANNED_NOT_RUN，不能作为功能通过。

依原04开发单第6条，一次性转交此完整A供当前整批吸收。仅在04尚未完整冻结且不需重放已消耗产品scope时集中处理；若已经冻结或唯一动态批次已经开始，保持其原源/profile/结果，不临时补丁后称同一实测，完整回交时列吸收/未吸收，负责人再统一裁定。不得逐问题交接、扩大当前预算、改旧03/02/01或冒真实UNKNOWN回收。

## 集中裁定

- A04-01：已确认固定helper字节错误，按原04恢复02原bytes47f9…c982，原失败/USED保持；保留33处常量分组，不能统改hash。完整固定契约预检仍是产品调用前条件。
- A04-02：确认为条件预算义务，未证固定正常图可达超读，不能报现网必现。选择给出全固定合法图/大小的精确上界（包括reserve后3次Runner物理复读）或补原read_file的读前准入；原上限不提高、不漏计合法额外读。与B02累计账本同批处理，不新建预算服务。
- A04-03：正常原调用顺序的静态保证不代非法delta类型处理。集中补足或明确证成merge时原holder/thread、双向owner/Gate-budget/Runner同一性与最终界；不强令Runner等于base+reference而丢后续合法读。event必须先核dict、path与opened等准确类型，非法结构受控拒绝；保留永久charge/pending，opened=false不虚构原close发生。可信同进程任意私有内存修改不作为外部攻击保证。
- A04-04：prefix必须在进入产品once之前要求精确int2，float2.0/True等受控拒绝，LIVE prefix仍拒绝，不改默认七角色。
- A04-05：任何实际控制器启动前，纯序列化完整Snapshot+delta、admission及原转发记录的可达最长合法路径/计数上界，实际UTF8必须满足原console8192B、admission声明4096B及读取8192B等原门。不能只量delta、提高cap或用真实超限控制器制造永久等待。若不满足，先最小有界去重并保持原证据语义，固定新源/profile后再按原授权进行唯一批次。

原重复引用计数identity1组/global2组/app_absence1组、prefix总3组6次/full七角色4组8次与预算归属作为独立oracle核对；facts和目标scope分开，原unused永久预留不退。63项全追踪，但按影响/必要性记录实际、静态、引用或NOT_RUN，不为数量堆故障/永久UNKNOWN。

tester阶段A到此冻结停止，不新增动态或审04浮动源。coder完整自测冻结后主动回负责人；负责人核完整包才正式派独立B。原动态360/320秒、1GiB/16MiB/96/并发1/产品retry0及SDK/设备/Git0保持。D1未过/M0未启，主阶段及框架许可/Flutter/独立Kit/P0不变。