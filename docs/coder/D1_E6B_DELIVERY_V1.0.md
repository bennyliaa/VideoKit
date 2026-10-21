# D1 E6B 完整交付 V1.0

2026-10-17。D1-20261017-E6B / versionCode8 / D1-E6B。仅修E6A-F01/P2公开入口创建前timeline异常归属，6个直接公开入口有限检查/59断言PASS，集中一次offline双APK构建PASS，无repair/native重建。Android/JNI/Binder系统及正常回归NOT_RUN，D1 NOT_PASSED/M0 NOT_STARTED、原P0/旧FAIL/许可保持。

唯一运行代码差异：公开E4CpuAdapter.validate(Context,...)的原PipelineRules.timeline调用外包catch(Exception|Error)，直接将捕获的原Throwable传给既有E6AFailure，标VALIDATOR/mode11/TIMELINE/NOT_CREATED/start NOT_STARTED，snapshot null。预检仍在TrackedProvider/CpuTaskClient创建之前，不为取得task而创建资源；offMain、合法输入后续及全部已拥有owner/后置验证/cleanup/原首份并发逻辑保持。未知实际在途仍原UNKNOWN。

tools/E6BPublicPreflightSelfCheck.java直接调用该公开Context重载，未用内部owner重载替代。5个坏timeline（null、长度、首值、非单调、超窗）均取得原生产PipelineRules.timeline抛出的IOException；primary与cause同一对象、原code/throw-site/type保持，无重建异常、cleanup为空、无task/snapshot，session实际路由由UNKNOWN改准确NOT_STARTED。五例均CPU创建tripwire/context/source open/digest为0。合法timeline另经同公开入口到达真实CpuTaskClient创建点，由测试Binder构造tripwire恰好一次终止，原sentinel身份保留；这是合法预检通过的校准，不是完整验证成功，也不作合法路径资源0或Android证明。

源码精确差异核实整个adapter仅上述catch不同，内部owned工作流后缀逐字节一致；其余所有运行源码、原JNI schema/sender/receiver、Source/validator作用域与原子首份、E6Muxer/E4CodecSink/PipelineRules、guard/recovery/每host观察/deadline/budget、app测试源码全部逐字节同E6A。原E6A20/112及E6原34只引用不重跑；本批仅6/59，日志evidence/public-run-001.log、输入/命令evidence/local-check-results.json。平台Context/Looper/Log/Binder为测试shim，实际Binder方法均禁止执行；无设备/媒体/导出件。

## 最终产物

| 角色 | 字节 | SHA-256 |
|---|---:|---|
| app-debug | 10544590 | `1930ff1cde30ab48adb184128c1313ac6a0ab6957ce425dfe4974c970a91a987` |
| androidTest | 2718669 | `ea3c95bc774204651bc8defc5084890694a192e8273e543ea37e040f6a9a9d69` |

仅用docs/coder/d1e6b/artifacts/D1-20261017-E6B/final，双证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f` 与原相同，原AppID/两私有服务/权限保持。最终main-001绑定输入SHA `35de0ac79c792f5a6c4f37937a4ee5166557fbcaa001e635110756d0c483fbce`，一次offline成功。七native、native源码/header/config原字节不变，native重建0；35Maven/Media3 1.9.3/FFmpeg8.0.3/原白名单不变、下载0。原NOTICE及完整C14对应源容器保留；16KiB ZIP静态核验，不作Android16KiB或安全/许可放行。

开发与独立测试需求分别保存docs/milestones/D1_E6B_CODER_REQUIREMENTS_V1.0.md、D1_E6B_TESTER_REQUIREMENTS_V1.0.md，并随原审查报告纳入reference。完整四文档、精确diff、输入日志/SBOM/源码ZIP/外seal/包外只读verify整包交负责人复审。原E6A228不可变项只读核验PASS，未改旧冻结或原53651消费/失败产物。下一准确计划tools/device_plan.json：同签名保数据部署E6B→MP4→AVI→能力→仅本批两正常独立报告receipt条件cancel，每新host原实际观察，不新QUERY/ABORT。实际动作尚未启动。
