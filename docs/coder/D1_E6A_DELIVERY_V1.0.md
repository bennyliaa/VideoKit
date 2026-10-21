# D1 E6A 完整交付 V1.0

2026-10-17。D1-20261017-E6A / versionCode7 / D1-E6A。集中修复E6-F01/F02/F03三个P2，实际共享生产边界20用例/112断言PASS、离线双APK构建与身份核验PASS。Android/JNI/Binder系统及正常回归NOT_RUN，不把本机结果当实机关闭问题。D1 NOT_PASSED、M0 NOT_STARTED、全P0及旧FAIL/框架许可保持。

## 三项修复

F01：E4CpuAdapter实际validate工作流在native await、stop、close、digest及实际PipelineValidationReceipt.prove/内容/thumbnail异常处，仍读取实际接收器首份snapshot并随E6AFailure携出。原Throwable作为primary/cause完整保留，cleanup按原顺序单列，不用native OK覆盖原Java错误。停止或close未实际返回时保留原verifier；不构造成功Verification，不做资源或预算信用重置。source同一所有权工作流也保原始异常和快照。

F02：source/validator分开task、role mode10/11、phase和专用报告字段。source.next失败只填sourceNativeDiagnostic，不再使用E6_VALIDATOR_REJECTED标签；validator尚未进入时严格NOT_STARTED。source成功也保实际source task/snapshot，validator成功保自身task/snapshot。已知CREATE/TIMELINE/BEFORE_READ失败明确start=NOT_STARTED，在途validation记录start=UNKNOWN；ENTERED只是开始调用相关入口，不是实际进程start ACK。源提取mode10的native accepted计数与mode11完整输出验收不混用。

F03：原Binder回调实际委托E6ADiagnosticInbox.receive完整接收边界，保原PID/UID/task/epoch/revoked/1024B鉴权、原数值schema、parse/end、stage与实际frame-count一致检查，全部完成后CAS原子发布首份合格snapshot。非法数据不占槽，重复/并发不能覆盖第一份；对象不可变、无reset接口，后续DONE/ERROR读同一首份。

## 有限本机证据

tools/E6ABoundarySelfCheck.java直接执行生产E4CpuAdapter.validate(ValidationOwner,...)和next(int,SourceOwner)共享工作流、真实PipelineValidationReceipt.prove/View及原PipelineRules内容/缩略图条件、完整生产receive及实际session scope路由组件。公开生产入口只封装真实CpuTaskClient平台操作并进入同一工作流；没有复制模型算法、test分支或成功豁免。测试只模拟start/stop/close/lifecycle事实与Context/Looper/Log基础API，不调用实际Android Binder/JNI或媒体。

20用例包括digest异常、实际receipt摘要不一致/未完成、真实内容及缩略图失败、stop false/throw、close throw、native首错+两cleanup、validator成功、实际source工作流失败→validator NOT_STARTED、已拥有资源的坏timeline/创建后取消窗口，以及完整receiver鉴权/size/revoked/字段/尾数据/stage/frame/重复/并发。16个并发receive仅1发布/15拒绝，首对象保留；非法首份后合法首份能占尚空的诊断槽。原协议对非法请求仍失败关闭，不表示容忍非法请求继续正常业务。最终20/112，记录evidence/local-check-results.json和boundary-run-005.log。

早期JVM001编译因自有Context shim缺少API签名停止；002通过18例，003补所有权窗口20/111，004补source成功归属20/112，005精确未启动状态20/112。全日志保留，未重跑旧E6的34或270/82历史套件，未重新读取E6媒体/回放件。不能把这些模拟平台事实当真实进程death/FD归还。

## 最终双APK与来源

| 角色 | 字节 | SHA-256 |
|---|---:|---|
| app-debug | 10726269 | `3d1ab7b287a089217d22be43184cc5d3f94b1a136d6c80ef192a92026ee1a134` |
| androidTest | 2718669 | `ea3c95bc774204651bc8defc5084890694a192e8273e543ea37e040f6a9a9d69` |

仅用docs/coder/d1e6a/artifacts/D1-20261017-E6A/final。证书均 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，原AppID、两私有服务及权限不变。sourceNativeDiagnostic/validatorNativeDiagnostic均确认进入最终app/test DEX，非源码空声明；本机test类不进APK。最终输入SHA `1d4f86663e8e016b3c175ea7df1cbb9f1a1f64b6b0e77a810000ab7fd073ace0`，repair-001绑定；main-001成功后最后核查补启动状态精确语义，必要一次修复也成功。首轮APK/签名/输入/理由/日志及build-results-before-repair-001保留冻结，最终只认final。

七native、native源码/header/config、JNI sender/schema、E6Muxer/E4CodecSink、原严格PipelineRules均逐字节同E6，本批native重建0、Maven35坐标锁不变/FFmpeg8.0.3/Media3 1.9.3不变、下载0。SBOM nativeDelta空、NOTICE-E6A及原E6/C14来源/完整对应源容器保留。最终ZIP16KiB对齐静态核验，不是Android16KiB实测或合规/漏洞放行。

## 冻结及下一步

开发原派发完整存docs/milestones/D1_E6A_CODER_REQUIREMENTS_V1.0.md，独立验收另存D1_E6A_TESTER_REQUIREMENTS_V1.0.md。四文档、精确diff/证据、SBOM/源码ZIP/freeze/只读verify整包交负责人复审；E6全部254不可变项只读复核PASS，无修改旧冻结。

本批设备/ADB/媒体源/导出件/新故障/下载均0。Guard/恢复/当前host实际观察/绝对deadline/原53651消费及失败输出保持。下一准确待审计划tools/device_plan.json：同签名保数据部署E6A→MP4→AVI→能力→仅本批两正常独立审证后条件cancel，稳定budget不变，不先部署E6，不新QUERY/ABORT。真实动作仍待正式派发。
