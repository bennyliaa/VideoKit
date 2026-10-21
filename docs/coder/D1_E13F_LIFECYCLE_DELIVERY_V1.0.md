# D1 E13F 生命周期集中修复交付 V1.0

2026-10-18。依据正式E13F coder/tester需求和E13E独立报告SHA3193a7728e84d860d03b14447214901f0641ccf135ffd655cfc69fc0938f9d6d。本候选完成三P1修复及指定有限离线自检，提交独立审查，未自批产品通过。

F01：公开case、新旧deploy在启动原child前把同一claim绑定同一supervisor；责任线程跨main超时isolation继续保管，join同一实际custodian后一次写准确marker。原超时继续失败，禁止自动下一方法。F02：request/fail锁内决定状态，锁外启动唯一worker与记录；平台日志通过48项有界异步队列，异常/未返不阻断请求及原归还。F03：writer体结束标志与线程真实结束分栏，原writer外检查并join同一线程后才退keeper；同样加强原PC starter/reader线程尾部屏障。

`evidence/host-007`实际两组日志测试、`public-008`六组完整公开入口链和`join-orders-009`三时序通过。全部生产class来自最终host-007编译，准确字节装入JAR，183个成员；所有成员保存原测试class字节并逐字节核对。未重跑长55秒/历史全套/媒体。

一次必要离线Gradle集中构建main-001 exit0；APK输入142项逐字节核对；app/test同签，fixture独立签。7 native与既审基线逐字节相同、35 Maven坐标及锁不变，fixture零第三方runtime，license NOT_GRANTED不变，无native重建/下载。DEX是静态接线核验，不能代替Android行为证据。

| 制品 | 字节 | SHA256 |
| --- | --- | --- |
| app | 10708622 | `938d70fbc70fd9bfdbef4ac37d2d83a66d7260e88e8c3c62bb2d022ea427908e` |
| test | 2774237 | `4227751bf659fca9efc8a8d2d32d5ce754bcbef9033e15a0c92ab7537dca9dd7` |
| fixture | 80041 | `a8c86650ae756f682fb2cbaaa896424974893282026525266e7b1912a8dd1867` |
| host JAR | 323116 | `97eadcd0cf7beaf1fd0bb7986e012ced69f6e09866f4af7e060338a2d0afabc4` |

app/test签名SHA5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；fixture签名SHA45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9。fixture私钥不分发，构建输入单列其pin。

包路径`D1-20261018-E13F-source.zip`；外seal `d1e13f/evidence/e13f-freeze.json`；最终只读回执`D1_E13F_FINAL_READONLY_VERIFICATION_V1.0.json`在ZIP外提供实际SHA，避免自引用。默认verify/带seal SHA verify/help/pack-help只读；仅显式pack生成一次新包。旧E11–E13E九组seal和准确成员保持原样，两份滚动协调文件只新增顶部安排，封包采用副本。

D1 NOT_PASSED / M0 NOT_STARTED；原实际卡点 NOT_UNIQUELY_DETERMINED。原v17主任务仅最后观测PENDING/UNKNOWN，本轮未查询；丢失诊断独立LOST_DIAGNOSTIC_OWNER_UNKNOWN。候选app19/fixture3未安装，真实Android/Binder/UID/Looper/monitor、kernel行为和T07均NOT_RUN。源码处置pin ABSENT，scope/release/once/sourceReview均未签发；旧资格/预算不继承。用户持续测试授权已具备，当前无设备操作源于原任务未决。

未来预算51成功/53含两次占用复查、2MiB文本仅全六法上限草案，非许可。须原任务及独立诊断处置审定、fresh完整M1、准确候选metadata、独立复审后重新派单一T07准确scope/budget；不得按此草案自动六法执行。P0、renderer/audio/Kit及历史FAIL/UNKNOWN保持。
