# D1 E12 剩余门裁定 V1.0

日期：2026-10-18。提交负责人/独立tester审定；本文只做证据与范围裁定，不是未来实现/设备派单。

## 有限关闭

E6B-OBS-F01/P1仅在E11 final R1本平板、四个独立instrumentation host的真实当前观察范围记CLOSED_LIMITED_E11_CROSS_HOST。E11独立报告已接受准确14→15保数据部署、两个6帧READY、能力源零打开、条件取消、全部原资源和五PC自然归还。保持严格6帧/双EOF/drain/PTS1000µs；不重复MP4/AVI/迁移实现。未触发的UNKNOWN、重启、长期、其他设备仍OPEN。E11较旧交付中“尚未部署/回执不存在”是当时事实，由新报告补充，原冻结文件不改。

## 剩余门、优先级及责任

| 门 | 本批判定 | D1必须处置的有限内容与后续阶段 |
|---|---|---|
| 普通发送者权限 | OPEN，源码有exported=false及内核UID/实例校验，E11无实际普通发送者负例 | 下一完整批次先补最小真实负例和同授权host正对照；不同UID/旧代拒绝不等同UID RCE沙箱 |
| 隔离资源UNKNOWN | OPEN，SESSION/CPU/LIFE已有保留门，旧close-unproven是quarantine用例，E11 runner不选它 | 下一批先沿既有owner证明可返回的源/调用异常；真实永久UNKNOWN必须有原持有者持续保管及可观察停止方案后另派，不能为了JUnit结束释放/杀进程 |
| 源/取消/SourceReleased | PARTIAL，正常和条件取消通过 | 补双消费者/迟到返回/源聚合可行性；一个CPU结束不能宣布全源释放；NAS真实产品M1/M7 |
| renderer/audio/source边界 | BLOCKED，六帧输出没有Surface和声音；PCM合法路线未准入 | D1要明确压缩输入、raw渲染owner、音频源/焦点唯一权威、销毁代次和归还机制；先做具体接口差距决定，不扩音频codec/FFmpeg。实际显示/听音另完整批次，不以设计标PASS |
| 独立Kit | OPEN，SET只有app/BUILD application，并非AAR | D1先定无Browser类型/无硬编码宿主、服务命名和独立依赖的可行性；M0模块/API/Fake，M7独立构建、双宿主/可移除/升级实证，不要求本批提前完成M7 |
| J01–J11全危险链 | PARTIAL/OPEN，各行见矩阵 | J03–J05迁到独立codec进程是实际改进，同UID不提供权限隔离；host lease/file JNI、图片字幕GL/显示声音仍有边界缺口 |
| 跟踪与模型/样本权利 | BLOCKED | D1由负责人组织合法候选/标签/质量最小路线，不能以FaceDetector数量或模板完成度替代自动跟踪P0；完整M5/M6质量后验 |
| 许可/发行/供应链 | OPEN，当前受限Debug记录不能外推外发准入 | 冻结原7库/35Maven，FFmpeg8.0.3/Media3 1.9.3不扩；权利决定由负责人处理，M6/M7发行材料继续硬门 |
| 手机及设备差异 | OPEN/历史环境阻断 | 平板四方法不覆盖手机AVI/MKV音频旧差异；按可用资源后续整批验证，其他项目占设备时等待 |
| C13/C14 signal历史 | FAIL/UNKNOWN/NOT_RUN原样保留 | 2026-10-16 C13 self系统0严格FAIL，外部raw11及另方法OS11不互相覆盖；C14两项未跑。新的有限功能证据不修改历史测试结果 |
| 长期准入/重启 | OPEN | 新host短时通过不是长期可靠性；不再为本门扩展迁移/许可管理工具平台 |

## 下一批建议

建议只派“普通发送者与源资源生命周期完整簇”（暂称E13提案），详见两份NEXT_BATCH提案：补真实权限负例、授权source正对照、迟到源/多消费者释放以及既有UNKNOWN门的有限可核验检查，同一新候选一次集中构建。其核心是补现有输入/资源边界缺证，不重复编码normal实现，不再新增authority、安全或诊断模型。

真实永久UNKNOWN的Android quarantine执行不并入可正常收尾的四方法，也不得直接把旧closeUnproven方法加进E11 runner。先复用原owner/监督器做静态及受控可返回的有限检查；如果缺少既有机制可持有并观察未知，交BLOCKED及具体证据，由负责人再定专门批次，禁止拿模拟检查关闭Android UNKNOWN门。renderer/audio、Kit封装可行性以具体接口差距与决定同时提交；不提前实现M0或扩依赖。

这是优先次序建议，不是把其余D1项删除或延期到最终发布才发现：源聚合/渲染声音/封装关键接口仍不满足D1退出条件，完整D1不能在本提案完成后自动通过。全部13项P0、原文§27发布阻断及§29设计决定逐项保留。负责人审查后正式派发才开始下一批；当前D1 NOT_PASSED / M0 NOT_STARTED。
