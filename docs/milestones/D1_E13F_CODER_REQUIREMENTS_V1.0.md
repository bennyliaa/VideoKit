# D1 E13F 集中修复开发需求 V1.0

2026-10-18。依据 E13E 独立复审报告 SHA256 3193a7728e84d860d03b14447214901f0641ccf135ffd655cfc69fc0938f9d6d。原 E13E 全部冻结，不覆盖；本批集中关闭三项 P1，再完整自检冻结整包交审。仅离线实现及必要构建，无设备、ADB、原句柄查询、处置、部署或方法重测。

1. F01：所有公开 case/deploy 入口在启动前将同一原 claim custody 接到同一 supervisor 实际完整归还事件。超时 isolation 后继续强持有续办；真实全部资源归还后一次结算原 claim，不能人工 true、重入 main 或依赖已退出 finally。订阅/检查并发不得漏通知。marker 写失败保持封锁和责任对象，原超时/失败资格不改，不自动续后续方法。
2. F02：E13FinishOwner request/fail 的状态决定和有限记录数据在锁内，所有 stage/platform sink 在相关 owner monitor 外。请求发布/唯一 worker 启动不能因日志异常或日志未返丢失完成请求；日志不得阻塞原归还续办。验证实际两个入口，不仅 E9 类锁。
3. F03：archive writer 在线程内标志和通知不等于线程归还。由原 writer 外的原保管方观察同一线程实际终止/join 后，才退 keeper、认定资源完整归还、pcClosed 和 claim marker。禁止自 join，通知未返继续持有原对象；保留文件 close 与事实快照区别。

直接有限回归：公开入口同原 claim→短受控超时 isolation→原自然归还→准确唯一 marker→另一 scope 准入，覆盖 case 及各 deploy 接线；marker 持久化失败仍封锁；request/fail sink 不持 owner 锁且有限扣住/抛错不丢请求；原 writer 尾部通知扣住时 resourcesReturned/pcClosed/claim 均不得提前通过，释放并 join 原线程后才可结算。实际生产 classes/最终 JAR 字节绑定；替身边界明确。不机械重复 55 秒全套、历史套件或媒体测试。

保持原 source pin ABSENT、scope/release/once 未签发和旧任务 PENDING/UNKNOWN；LOST 诊断独立，不以此修复反控旧字节码。处置方案只更新受三缺陷影响的部分，未选择或执行行政终止。D1未过、M0未启、P0/许可/历史证据不变。

交付：新 E13F 源码差异、实际边界原证据、构建理由与失败历史、最终 APK/JAR/签名/来源/SBOM、四类交付文档与只读 verify/外 seal/完整 ZIP。先集中实现再必要构建，不频繁小交接。同步两份协调文档顶部最新安排，完整结果主动通知负责人。
