# ENV03 独立机械核验 V1.0

2026-10-20。结论：PASS_INDEPENDENT_ENV03_MECHANICAL。新scopeId `f0be73d2-01d2-4775-be6d-b6e55b8b77b3`；机械核验尚未启动设备查询。负责人已有条件授权允许本门及fresh本地/tool/default路由/claim门通过后，仅执行一次identity→global，两项后无论空闲与否停止报告。

独立逐字节核验24项冻结行、ZIP23成员及完整成员集合、旧activation33项。delivery SHA256 `47f9e9a504c00f4f172357d78c16ede428d3eae72ed1e1e1231c3a4d871f5994`；seal `37fbd2b0f4842099f6ffb27a642eb58d8e22d89b394925abd9ca6b44d70ad302`；ZIP `f20e61cfdcabb9154ec12af09251af295b734afeeabbc6bb48274ed868ac0bd0`。实际授权原件与包内副本字节相同，SHA `dcc163aa7f4764a7cef146b33dadf1e5c86793be987efc95aefc1c315fcec44c`。

environment-plan SHA `ff23db7cdba88db95af9e9e39af8738fea4be9ec90b3cd9fb73402996051b27d`，准确绑定新UUID、独立root、2操作/1048576B文本/1048576B归档；policy SHA `a32081b68c811497b122cac63d042816423c1776852bfda7ecfc301f3fb17ee8`，PRODUCTION、三类来源pin唯一，全部原始摘要、两请求与dispatch准确命令/前项证明关系匹配。未生成或继承产品permit，原两项/388818B及历史UNKNOWN不冲销。

未依赖coder的10项自检断言。直接读原采集器源码及准确字节SHA `fef62cb2a2ddbca49e22b1f041e59387185323539945d86e06dd8823449e25fe`：27行先用区分大小写的完整id逐槽匹配，28行拒绝index<0或不符合 `^[A-Za-z0-9_]{1,80}$` 的请求。后三槽含冒号，精确匹配时必被正则拒绝；去掉冒号或其他合法id则无精确槽。五槽与合法id域交集准确仅为ENV03_M1_identity、ENV03_M1_global。拒绝先于记录写入/上下文创建，且先于141行原子进程Start；全程未运行PRODUCTION入口试探第三项。五槽argv/phase/cap/15秒逐项与原参考相同，实际请求与命令仅前两项。

运行条件仍须fresh现场验证。仅主App版本17、fixture1有版本要求，测试APK按准确SHA及签名/UID/data判断，观察版本如实记录。identity必须同原工具真实自然返回、EOF/文件/元数据/锁归还并独立语义通过，另次调用形成外部proof后才能global；global之后不生成第三项准入proof，不部署/ps/M2/case/自动重试。

证据：`D:/CodexProjects/VideoKit/docs/tester/D1_ENV03_REVIEW_EVIDENCE/independent-mechanical-audit.json`。本报告仅机械PASS，不能代替设备空闲或D1产品PASS；D1未过/M0未启。
