# D1_MEDIA3_CONTAINER02_FIX 独立整包复审报告 V1.0

日期：2026-10-21。测试人：tester。接收人：负责人01a107c3-2bf9-7fa0-94a0-234258ca6774。

## 1. 结论及范围

**PASS_LIMITED_FIX_WITH_FUNCTIONAL_SCOPE_OPEN。MC-B01/P2在指定“实际结构检查开始前的准入/原任务归还”范围内修复通过，本次未发现新的离线阻断。** 原暂待状态不再记成首错或永久耗掉尚未开始的检查资格；同一原REOPEN及原Provider可以在原任务实际返回后继续，未发生第二次REOPEN。源码及生产JAR优先路径独立验证一致。

真实 MP4/fMP4 提取、合格六样本AVC fixture、实际mux/remux→Sink→结构重开继续 **OPEN/NOT_RUN**；真实结构成功缓存、解析中权限变化、恶意atom内部内存、SeekMap/NAL/时基/EOS duration亦未执行。有限修复通过不关闭原容器功能目标。D1未通过、M0未启动；原FAIL/UNKNOWN/P0记录保持，原01报告不回写。

依据 [正式测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_MEDIA3_CONTAINER02_FIX_TESTER_REQUIREMENTS_V1.0.md) 末尾交测，阅读 [主交付文档](D:/CodexProjects/VideoKit/docs/coder/D1_MEDIA3_CONTAINER02_FIX_DELIVERY_V1.0.md) 和 [准入顺序决定](D:/CodexProjects/VideoKit/docs/coder/D1_MEDIA3_CONTAINER02_FIX_ADMISSION_ORDER_V1.0.md) 后测试准确冻结候选。全程已有JDK/Python离线执行；零SDK/ADB/设备占用检查、零Gradle/网络/共享缓存修改，无新平台替身、fixture或编码器。

## 2. 冻结、产物及继承准入

|对象|独立核验|
|---|---|
|候选|docs/coder/d1media3-container02|
|主交付SHA-256|cfe817dd8d966f4cebdc8710a243d47b217f1ff16139f6099de91b29029efbc6|
|seal SHA-256|0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d|
|seal/ZIP|676项含ZIP；ZIP675唯一成员，路径集合及逐项大小/hash一致|
|生产JAR|108666 B；757e53a49d92a9b2148417e0b37ed9680162a7709b1493029759e58ce08dfd8f|
|编译探针APK|7094375 B；51d163ae79e4b3f92ca9417267806290b3924f66aba3f5871442a0c1d081c871|
|APK身份|com.videokit.d1input，versionCode7，D1-MEDIA3-CONTAINER02-FIX，min31/target36|
|签名|已有apksig独立v2验签通过；证书SHA-256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f|
|源码及旧封存|1043项输入核对；9批旧seal共5556项保全；生产Java仅TemporaryOutput变化|

独立解析APK清单、4927个DEX类及JAR64条目，核新增及既有检查类均排除；无权限、组件、native及主机平台测试端口混入APK。未安装、启动，不以编译/签名证明平台运行。

与01逐字节比较 app/settings锁、verification-metadata、deps、official-extractor保全来源/许可、offline-maven、平台端口及所有非TemporaryOutput生产输入，均一致；无新生产Java或新平台端口。继承原01独立报告对extractor/decoder **1.9.3** 的有限离线来源/许可准入：固定17个运行坐标，依赖/pin/版本/下载新增均0，LockMode.STRICT和metadata验证保持。

独立核本批实际消费300项的坐标、文件、hash与01闭包一致，并逐项关联本批829条事件中的验证记录：**123 binary、37 module、140 POM**。审阅的是冻结严格构建证据，本次未自行运行Gradle。未将既有POM pin误写成新增实际POM消费，也未重新联网获取来源材料。原01报告整体FAIL及容器OPEN不因继承准入改写。

证据：[身份/准入审计](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/admission-and-artifact-audit.json)、[独立验签](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/signature-1.stdout)。

## 3. 冻结入口与独立执行

实际运行文档入口，输出到此前不存在的新绝对子目录：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/tools/review_all.py --output D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/independent-001
```

源码编译及生产JAR优先路径共60条顶层回执退出0；原argv、起止时间、原进程返回及ORIGIN/JAR hash保全。覆盖继承05/01输入、原响应/observer/worker、取消、首错、终态、partial UNKNOWN、异常/宿主结果/顺序等回归，以及coder新增8项原输入重放和22项顺序检查。**60次退出0包含两条明确NOT_RUN的平台probe；重叠的子计数不求和，也不当作容器功能通过。**

另独立编写 [IndependentSharedAdmissionCheck.java](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/IndependentSharedAdmissionCheck.java)，保留实际产品和Media3，只控制宿主线程、门闩及真实CompletionStage。并由原01 tester用例输入生成 [IndependentContainer02BoundaryCheck.java](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/IndependentContainer02BoundaryCheck.java)，准确更新修复预期。仅在新独立目录编译辅助类，生产JAR路径始终优先。

最终源码及生产JAR每路径 **28项共享入口检查通过、8项读取/修复边界通过**。该计数分别属于两个有限套件，其中超时等内容存在重叠，不宣称36项不同容器功能。所有原caller、宿主worker、真实observer及输入/output keeper完成实际归还；未签发隔离格式结果或READY/COMMIT。

执行证据：[60条入口汇总](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/independent-001/summary.json)、[独立回执汇总](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/independent-summary-1.json)、[源码28项输出](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/independent-shared-source-1.stdout)、[生产28项输出](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/independent-shared-production-1.stdout)、[生产8项输出](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/independent-boundary-production-1.stdout)。

## 4. MC-B01及共享顺序独立结果

|独立输入|实际判据及结果|
|---|---|
|原问题重放|第一次结构检查得到OUTPUT_ORIGINAL_PENDING，firstFailure保持null；同原任务返回后继续到真实库构造失败边界；REOPEN=1，全程继续前无cancel/abort，MC-B01修复通过|
|ACK先、同原worker尾段后|两个入口反复观察均稳定暂待，首错null、provider open=0、无提前释放；放行并join同一worker后才继续|
|原worker先、ACK后|同原worker实际结束，但原ACK未到且原caller仍等待；同ACK在期限内返回后进入同一Provider准入，不误报真实超时|
|真实observer独立尾段|真实whenCompleteAsync observer被门闩保留，原worker已join且ACK isDone；两入口仍暂待；真实observer stage及原observer线程返回后才继续|
|两入口交叉继续|3种顺序×2个初次入口×2个继续入口=12项，无取消/abort干扰；结构检查和verifyAndValidate均复用原REOPEN|
|同Provider身份|仅一个未打开的HostInputFactory登记原Provider对象，全局第二槽仍空闲；两个入口均因重复该对象被SOURCE_RESOURCE_EXHAUSTED拒绝，首错null、检查资格未耗；该原能力归还后继续成功进入实际检查边界|
|继续的准确终点|结构入口进入真实Media3构造并以OUTPUT_HOST_STRUCTURE_FAILED拒绝，provider尚未open；既有验证入口使用同Provider短读1×4及已知长度EOF/hash后，由明确false的受控validator以OUTPUT_VALIDATION_FAILED拒绝|
|实际开始后失败|上述真实失败被记录为首错；两入口后续均OUTPUT_NOT_VALIDATABLE，REOPEN不增加，不循环检查、不开替代源；4B刻意非媒体，无内容资格或隔离验证PASS|
|真实超时|两个入口各一次真实70ms期限超时；迟到正常ACK及原worker返回后仍OUTPUT_TIMEOUT_PENDING，拒绝后续检查，REOPEN=1、provider open=0|
|取消/abort|原尾段未返时意图不能提前释放；原任务返回后意图仍有效，不恢复结构或验证入口|
|真实失败/UNKNOWN|两个初次入口各覆盖权限、调用结果UNKNOWN、null stage、null Provider、错误类型应答、取消的原stage，共12项；脱敏稳定首错不清、不重发、不解析|

其中共享套件28项 = 12正常顺序/交叉 + 2真实超时 + 2取消/abort + 12坏结果/权限/UNKNOWN；所有失败用例有同原对象清理。正常路径在继续前明确没有取消或abort。原Provider不是替代对象，也不是全局两槽耗尽产生的假同一性证据。

新生产逻辑审查与动态结果一致：[TemporaryOutput.java:130](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/src/com/videokit/d1input/TemporaryOutput.java:130) 共享inspectionReadProvider复用原响应，原任务/observer门保持；HostInputFactory成功取得资格后才设置hostInspectionAttempted，外层不再把所有准入等待笼统采纳为首错。实际检查内部仍记录真实失败，结构结果与validated/READY/COMMIT分离。真实结构成功缓存与容器种类约束仅完成静态审查，未以受控证据伪造成功对象，仍NOT_RUN。

## 5. 输入、预算、工具及历史证据

独立8项覆盖：真实DefaultExtractorInput peek/reset与3+3+1短读；同Reader跨close/reopen累计4+4MiB后下一读在provider及caller修改前拒绝；source73/open5/remaining68对应绝对end73及未知长度-1；取消时迟到原read/close仍保管、调用者缓冲区未被迟到数据修改；capability/container/seek参数预开拒绝；MC-B01无取消干扰修复；真实超时sticky；remux缺Evidence在写入及muxer构造前拒绝。真实输入类ORIGIN为冻结media3-extractor.jar，产品路径身份符合源码/JAR优先安排。

原输出16MiB/64KiB块、源总2/每源1/queue0、partial ACK/物理写入/UNKNOWN和原任务保管通过继承套件回归；实际容器整链的预算效果未执行。已批准原片在两路径各known/unknown只读全EOF/hash，前后均349102 B、SHA-256 `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9`，无改写或转码。

独立输出路径门：review_all/local_check各8项，共16项非0拒绝，覆盖旧01根、旧05根、候选内、伪前缀、越界、相对路径、根自身、已存在子目录，未新建非法目标。见 [output-gates.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/output-gates.json)。

测试过程纠正：独立辅助检查首轮错误地期望“已知4B长度、每次短读1B”产生第5次provider EOF读取；HostDataSource在remaining=0直接返回EOF，正确provider调用数为4。只修该测试预期，未改产品或放宽归还/首错/身份门；初始源码、失败退出1和日志保留，结论依据后缀`-1`的最终双路径回执。见 [纠正记录](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/independent-initial-test-correction.json)。coder先前local001的测试lambda编译错误及其修正记录亦保全，未计为当前产品FAIL。

最终再核676项候选未变；01复审1852项、阶段A75项及05复审1093项证据和原报告hash均未变。原01报告hash `4d8853e56b18de0605309a6ba627b674c222d8b846a670d4cb59754bc71a4e87` 的原FAIL不回写，仅本新报告有限关闭MC-B01。见 [收尾保全核对](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/post-review-preservation.json)。

## 6. OPEN/NOT_RUN及交接

32项原功能映射保存在 [independent-case-results.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/independent-case-results.json)：MC26/MC30指定准入/归还修复有限通过，MC01继承准入通过；其他组件/旧基线回归及真实功能缺口保留准确限制。MC05/06/12/17/18/22/27/28/32真实路径未执行，MC03/20/21仍OPEN，不能据子计数或有限修复关闭功能簇。

实际平台probe分别遇Mp4Extractor缺NameNotFoundException、FragmentedMp4Extractor缺Parcelable、FragmentedMp4Muxer缺SparseArray。没有实际轨道/样本提取、SeekMap、mux/remux或成功结构重开。原片权利记录及只读hash虽保持，但320×180/含AAC/8秒仍不符单AVC256×144/rotation0/恰六真实样本条件；无合格fixture/CSD/逐样本NAL表示、hash/keyframe/PTS/时基/EOS duration证据。

后续准确批次须由负责人统一安排实际运行环境及已准入合法fixture，并事先明确NAL转换、时基舍入和EOS总duration判据。真实解析中权限变化、畸形atom内部内存界、结构成功/同次缓存继续均需真实证据。Android FD/fsync/codec、隔离内容/死亡/时序、业务提交及播放效果继续NOT_RUN；4B false validator仅证明拒绝路径，不签发HOST_ISOLATED_FORMAT_V1或READY/COMMIT。

本报告与证据发送前冻结，发送回执另存。本批已完成，集中通知负责人后等待正式新冻结/新批次，不自动设备测试、继续解析或修改产品。负责人可在本报告限定范围关闭MC-B01；D1原容器目标及其余历史门仍保持。
