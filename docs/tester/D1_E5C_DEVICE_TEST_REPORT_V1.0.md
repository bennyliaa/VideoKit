# D1 E5C 部署、隔离补验及只读 QUERY 整批测试报告 V1.0

2026-10-17；tester。依据 `docs/milestones/D1_E5C_EXECUTION_TESTER_REQUIREMENTS_V1.0.md` 正式执行原平板单批任务。

**结论：BLOCKED_PREFLIGHT_TESTER_QUOTING_ERROR。安装前的原 N2 元数据核验因 tester 命令引号错误失败；按本批失败即停、不得重试要求，停止全部依赖动作。** 部署未尝试，隔离补验及原 QUERY 均 NOT_RUN。本次不新增产品缺陷，不改变 E5C 静态审查支持结论，也不将 G01 登记通过。

## 1. 三阶段实际结果

| 阶段 | 实际结果 | 证据与限制 |
| --- | --- | --- |
| 设备/既有包前置 | 部分通过 | 原平板在线、型号/API/架构/user、原 app/test UID、既有 APK 准确 SHA 和空间核验通过；原 N2 metadata 前置失败 |
| 部署最终双 APK | BLOCKED / 未尝试 | install 调用 0；未升级或卸载 app/test |
| 隔离三例补验 | NOT_RUN | instrumentation 调用 0；未创建夹具 root、未调用 Guard/观察锁边界；root 是否已存在未采证 |
| 原 N2 只读 QUERY | NOT_RUN | 未调用恢复入口，不推断 QUERY_ELIGIBLE 或真实死亡证据 |

E5B-G01=AWAITING_ANDROID_EVIDENCE_AND_REVIEW；Windows 文件符号链接历史 NOT_RUN 保持。没有 Android 真 symlink/ELOOP/flock/FD 关闭用例成功记录。

## 2. 已确认身份

设备仅绑定 `HA1Q6WXR`，get-state=device；TB138FC / API31 / arm64-v8a,armeabi-v7a,armeabi / 当前 user0。com.videokit.app UID10221，test UID10222；User0 均 installed=true、hidden=false、suspended=false、enabled=0。手机未查询或操作。

既有 app versionCode1 / D1-E4A，设备 base.apk SHA `e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f`；test SHA `1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be`。两者与已冻结 E4A APK 准确字节身份一致，其既有签名审计证书为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；设备 package dump 两包签名标识相同。此为设备 APK SHA 与已有签名身份绑定，没有将 package dump 的短签名 hash 当证书 SHA，也未下载设备 APK 或重跑签名器。

/data available 85360328KiB，高于 runner 的 65536KiB 前置值。空间与包信息在本批原始回执中保存。

待部署 E5C seal `75ad67f90cb7689cd4b7d765afc6b9101dcf75cc1f9e5f1343b9d7db9a1be47c`、ZIP `ac7d5bc2901ab66bb16299cf8c2052e6e7bd3344276b1c3d2a0b50b38a291743` 已在整包复审核验；执行 runner 再核 seal 及计划绑定最终双 APK：app `5b7992f1ec01f8782b59dd1508c6a47e3af4f2602ba428e1b65892724f73f464`，test `5101c8efa43fd4ab5944479c8bafa8934ab9c4a1a1318fd9c6eae4c5d3f0e36c`。这些本机身份不代表实际部署完成。

## 3. E5CEXEC-T01：tester 只读 shell 命令嵌套引号错误

分类：测试执行脚本错误，非产品 P1；影响为本批前置证据不成立、全部后续动作阻塞。

原 runner 把多行只读脚本简单包在单引号内，脚本自身又含 printf/stat 的单引号。远端 shell 的嵌套引号被提前结束，管道等文本被当作外层命令，返回 127。原始输出出现 `printf APP_PWD: inaccessible or not found` 等解析错误，没有合格的 APP_UID/APP_PWD、STAT/SHA、ledger/identity/journal/lease 证据块。

该命令计划只读准确原 metadata、stat 原输出/fixture，不包含安装、删除、写账、锁、fence 或媒体内容 hash。但解析失败意味着不能声称原 N2 现场已由本轮完整复核无变化；**原 metadata 有效新证据 NOT_COLLECTED**。没有把错误输出当作缺文件、应用权限失败或产品恢复失败。

实际顺序仅为：get-state、设备/包/空间查询、app APK SHA、test APK SHA、失败的 private-state 调用，共 5 次 ADB；最后一次 exit127，前四次 exit0。root 新鲜性检查尚未开始。自动检查在该失败后退出，没有执行 install/fixture/QUERY，没有改期望或自动重试。

保留 [原失败 runner](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_DEVICE_EVIDENCE/execute-original-failed.py)、逐命令 attempt/receipt/stdout 及 preflight-failure.json。备用 [修正 runner](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_DEVICE_EVIDENCE/execute.py) 改为用 shlex.quote 编码整段远端脚本；仅完成本机 AST 解析与 shlex round-trip，确认 `run-as / app / sh / -c / 完整原脚本` 五段一致。**该修正未在设备运行，不算前置或补验通过。** 既有 stage-attempt 以独占创建限制误重用本批。

## 4. 预算、实际返回及原结果

本批 ADB stdout 保存 18021B，低于 8MiB；各次 metadata 输出均低于 256KiB。5 个客户端均实际 wait 返回，输出管道已关闭，本机无该批在途 client/handle；不存在新开的产品/夹具 instrumentation owner，因此不能把本次客户端返回登记成原 N2 产品资源释放。

install=0、instrumentation=0、真实媒体内容读取/hash=0、Gradle/Java/开发模型=0、native fault/信号/force-stop/cancel=0、本机符号链接一次 ID 脚本=0。fixture 64 节点/256KiB/单64KiB/128holder/4MiB日志/60s 预算均未消费。没有创建或清理 fixture root，也没有读取已有 root。

原 N2 仍沿用历史 FAIL/PENDING、R2MiB 无 S/operation.pending 与原协议 owner UNKNOWN 的既有记录；本次没有 QUERY、结算、清 marker、换 UUID 或恢复动作，也没有获得有效新 metadata 回执，不能额外宣称本轮现场保全复核 PASS。D1 NOT_PASSED、M0 NOT_STARTED、全部 P0/JNI/历史 signal FAIL/C14 待测保持。

## 5. 后续处理

本批失败关闭依赖，不自动启动下一批。已修正的命令及原失败证据可供负责人审查；如另行正式派发，可仅安排未成功的 metadata/root 前置，再按准确计划决定后续部署、隔离补验和条件 QUERY。是否复用已成功前置结果、时间有效性及新的 attempt 名称由新任务明确，不能在本批内改名伪装重试。

写入式 ABORT、OBSERVE_SETTLED_N2、正常 MP4/AVI/能力/取消仍未授权。本报告将主动发送负责人，说明阻塞来自 tester 引号错误而非候选产品。

汇总：[blocked-result.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_DEVICE_EVIDENCE/blocked-result.json)。
