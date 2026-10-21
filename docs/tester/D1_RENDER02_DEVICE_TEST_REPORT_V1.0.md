# RENDER02_DEVICE 整包实机测试报告 V1.0

2026-10-20；候选D1-20261020-RENDER02；目标平板HA1Q6WXR。

**结论：BLOCKED_PRE_SDK_CAPTURE_CAPABILITY。** 已完成准确授权/输入核对、有限逐操作计费清单及既有采集入口能力审查；必需的新包安装、私有fixture输入和新runner没有能直接复用的已审入口，按本批明确条件在第一个SDK子进程前停止。实际SDK操作0、安装0、fixture写入0、用例0、截图0，无新增设备原owner/pending。

这是本批执行准备BLOCKED，不是RENDER02产品回归FAIL，也不撤销此前三项有限离线PASS。**没有新鲜设备占用读数，不能把ENV03旧占用结论登记为本轮ENV_WAIT。** D1未通过，M0未启动，当前不自动后续测试。

## 1. 授权与输入

scopeId：`78df082b-ed71-4c34-b032-448c061a299b`。实际授权文件 `D:/CodexProjects/VideoKit/docs/milestones/D1_RENDER02_DEVICE_EXECUTION_AUTHORIZATION_V1.0.json`，SHA256 `641b93e27365df9b3a3bcb9373d0e2dd34d99956f96a4ea771fdd3fb020db01f`；计划的renderScopeSha256准确使用此值，无另造语法hash或release许可链。

授权5项pins逐一核长度/hash相符：独立离线报告2b4b4379…198d9、候选seal a226b5fe…83581、App `2f6e1cf02d85d8b0bd32ca0c475aea9e182a8b3b55e17a6da066a6ddfc5e2d94`、test `88241afd1cfe50fee41be95d788d76948bdee24cec14a26329040f69970e63cb`、准确设备计划45066074…97c。

新实验包com.videokit.d1present、version2、原Debug证书及四方法不变。本地准确fixture源已核，仅读取授权的 `D:/CodexProjects/VideoKit/test_media/imgs_and_videos/videos/sample.mp4`，349102 B，SHA `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9`；未遍历/读取其他媒体payload，未拷到设备或修改原件。新目标私有路径为files/d1_render_fixtures/basic.mp4，不复用旧App私有数据。

## 2. 原入口能力门阻断证据

本批授权conditions要求使用“existing approved same-original client owner capture mechanisms”，并要求“Record exact finite command plan/operation costs … before first SDK; any unsupported lifecycle or budget preflight BLOCKED”。TESTER要求也明确：“若现有工具不支持原进程保管、实际计量或有限命令则SDK前BLOCKED集中说明，不造新框架。”本次按这一规定停止，不缺一般真机授权，也不是自动批准审查拒绝。

| 已有入口 | 实际源码限制 | 对本批的影响 |
|---|---|---|
| d1resume02-activation/tools/capture_metadata.ps1，SHA fef62cb2a2ddbca49e22b1f041e59387185323539945d86e06dd8823449e25fe | PRODUCTION固定五槽，逐项核原argv/phase/cap/15秒；源码FIVE_FIXED_SDK_REQUESTS_ONLY和精确slot/前项proof拒绝其他请求 | 无法直接承载新短identity、新包identity、install、fixture或RenderDeviceTests。改request名字/policy不能绕过固定argv。不能改为OFFLINE_FIXTURE执行SDK |
| d1resume02-release/tools/observe_original.ps1，SHA0667bc7fe93cf2010cd337eeafaeabd94b7a795efa74059365af3fb83c8485b8 | 8行仅接受Java E13HostCase / E13HostActivationSession；10行只接受32768/81920文本界 | 不接直接ADB、新Render runner、二进制截图或新fixture stdin；不能冒充旧E13角色套用旧部署/用例链 |
| 历史E11 tester controller | communicate完整缓冲后才检查输出量，timeout后只等poll，不继续收齐同原stdout/stderr | 不能为本批原实际读取/未知分栏和持续保管门直接提供合格证明；不因过去使用过就扩大批准范围 |
| 历史C14 prepare_device.py | subprocess.run(capture_output=True, timeout=...) | 超时处理可能终止子进程，不符合本批禁kill与原保管条件；不重新试跑 |
| 历史C14 transfer_fixtures.py | 自定义socket路径固定旧com.videokit.app及files/d1_c14_fixtures | 不是当前新包私有目标；不能为本批换包名/目录或绕开SDK子操作计费，未调用该协议 |

349102 B私有fixture复制需要同原stdin写入/实际计数/关闭归还能力；现有入口未覆盖，不能仅用普通输出采集包装一个新输入泵。截图还需要同一已批准Activity安全可见期间的时序与二进制原读/保存/未知计量；现有固定入口也未覆盖。截图不足本可单列NOT_RUN，但必需的安装/fixture/runner已不满足准入，故整批在SDK前停止。

本次没有放宽冻结entry/argv/cap/regex，没有创建新custodian/传输协议/发布框架，没有启动SDK试探拒绝，也没有先消费identity/global再回头处理后继工具缺口。工具源码准确hash及限制证据在capture-capability-audit.json。

## 3. 精确有限操作与预算清单

完整逐项argv、前置、SDK成本、文本/二进制资格界和有限复合shell子命令已保存：`D:/CodexProjects/VideoKit/docs/tester/D1_RENDER02_DEVICE_EVIDENCE/exact-operation-and-accounting-plan.json`。这是PLAN_ONLY，不是新可运行dispatcher、许可或已执行记录。每条准确ADB子进程计1；有限remote程序另明列，无隐藏循环/无限复合shell。

| 序号 | 有限计划 |
|---|---|
| 1–4 | model/API/user/ABI准确identity、完整global、ps、新实验包是否存在；任何他项目占用或未接受的已有身份即停 |
| 5–6 | 两个准确APK各安装一次；只在确认新空沙箱及空闲后，不卸载/清数据/重装绕门 |
| 7–12 | app/test完整包信息、已装APK准确SHA、两者UID:inode |
| 13–14 | 准确349102 B同原stdin私有复制（无覆盖）、大小/hash验证；这是当前不支持的必需能力，未执行 |
| 15、18、21、23 | 四个准确静音方法各一次；class#method/renderCase/真实授权SHA，逐原内部资源及外部客户端归还 |
| 16、19、24 | 最多3张截图，各≤4MiB；只在同次原目标安全可见时，无法证明即NOT_RUN，不对其他App截屏或增加UI查询 |
| 17、20、22 | 后续每方法前准确global，无他项目/旧本候选原进程复用 |
| 25–28 | 最终global、fixture hash和两份数据身份；只有前项实际归还及未失败才可执行 |

四方法准确为generatedMutedDualConsumers、existingMp4RawMutedDualConsumers、cancelRejectsLateGeneration、pausedSeekAndSurfaceRecreation；runner为com.videokit.d1present.test/com.videokit.d1present.RenderInstrumentation。第五人工方法不在当前28项自动计划内，无就绪操作者，不创建或启动其invocation；余4操作不自动转为手工/重试许可。

| 预算项目 | 计划承诺 / 授权上限 |
|---|---:|
| SDK子操作（含3张条件截图） | 28 / 32 |
| 原文本资格界合计 | 3559424 B |
| 控制/转发/记录/报告预留 | 393216 B |
| 文本总承诺 | 3952640 / 4194304 B |
| 3张截图二进制归档预留 | 12582912 B |
| 如需保留一次fixture副本预留 | 349102 B |
| 二进制归档总承诺 | 12932014 / 16777216 B |

准确APK输入仅引用冻结原件，未重复归档；APK上传输入13176001 B及fixture输入349102 B另列为出站payload，不能冒充stdout原始读取或新增归档产物。授权字段为binaryArchiveBytes，未把16MiB解释为所有出站/入站协议流量总和，也不虚构SDK内部协议实际字节数。

资格界不是物理读取硬界。若未来发生超额、faulted read/partial write或原对象不明，实际成功原始读取、保存、控制/转发分别照记；未知保留整类，不以cap/文件长度填造精确数，停止依赖并保管同原owner。本次尚未进入SDK，不能将计划上限当实际消耗。

## 4. 本轮实际结果与账本

| 项目 | 状态 |
|---|---|
| 授权/冻结输入/fixture本地身份、有限清单 | PASS_LOCAL_PREPARATION |
| 必需采集入口能力 | BLOCKED_PRE_SDK_CAPTURE_CAPABILITY |
| 新鲜host listener/tool/default route、claim/live ledger | NOT_RUN，能力门在前；本轮没有此类现场查询 |
| 平板identity/global/占用 | NOT_RUN；不从旧ENV03读数推当前占用 |
| 安装、安装后身份、私有fixture复制 | NOT_RUN |
| 四自动用例、真实截图/方向/PTS/代次/双consumer平台效果 | NOT_RUN |
| 人工听音/第五方法/真实焦点 | NOT_RUN_NO_OBSERVER_READY；不播音、不改音量、不录音 |
| 实际SDK子操作 / SDK文本 / SDK二进制读取/保存 | 0 / 0 B / 0 B |
| 新增SDK/设备原owner pending | 无；未启动 |

实际账本：actual-execution-ledger.json。0 B仅指没有启动的SDK原输出和二进制产物，不称本地准备/报告没有字节开销；这些新文档控制量在授权控制预留内保留，不退款任何历史UNKNOWN。新scope未初始化设备采集root/guard/claim/once，旧com.videokit.app及其数据、旧账本、UNKNOWN均未操作。未退款旧2/388818 B、ENV03的2/371309 B或旧8192/409600。

## 5. 集中移交与后续边界

请负责人接收本执行准备阻断及完整清单。若存在能直接承载这些准确角色的其他已审入口，可明确其路径、hash和批准范围以供核对；否则需由负责人先协调最小既有入口适配的明确范围，再整包交测。本轮不自行修改采集器或造新框架，也不在能力未满足时只跑前两条查询求部分结果。

既有一般真机授权继续有效，不需要用户重复授权。完成工具准入后仍须新鲜平板/空闲/准确新包身份与原owner门，禁止操作其他项目、kill、server重启、强finish、二close、清数据或重试。第五项仍待事先真实操作者就绪，不能自动点Listen冒听音结果。

报告主动交负责人；RENDER02离线修复PASS保持，设备项全部如实NOT_RUN，D1未过/M0未启，不自动进入其他测试。
