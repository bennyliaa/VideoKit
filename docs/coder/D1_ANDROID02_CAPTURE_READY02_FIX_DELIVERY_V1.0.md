# D1_ANDROID02_CAPTURE_READY02_FIX 完整集中修复交付 V1.0

2026-10-21；开发交付状态：PREPARATION_ONLY，三P2已同批实现，最终有限整套离线自检通过，等待本候选完整独立 B。未签新执行许可、未实机；真实Android/FD/Media3/平台finish NOT_RUN，D1未过、M0未启。

## 依据与冻结边界

完整独立B报告606205d01c6db42c357ca72f403c6b676ed78b0f7a229f5a210e2c9be8efcfaa的CR-B01/02/03全部作为本批范围。新目录docs/coder/d1android02-capture-ready02-fix；没有重开已有限关闭的FIX02五项产品源码，无产品/APK/旧采集修改。静态整批核READY01原seal756、FIX02 seal874、旧RENDER capture seal818，所有原size/hash一致。产品/SDK只读文件pins亦一致，无SDK执行或查询。

reference含完整要求/B报告、READY01原入口、准确七角色计划及既有route/claim合同，最小diff在evidence/ready01-to-ready02.patch。tools/outer_owner.py由READY01已有Popen原owner模式准确适配为固定生产七角色owner，不接受任意命令调度；没有新native helper、通用诊断/dispatcher/release多层框架。

## CR-B01：原base + 真实外层delta

原console保留不可改base。已关闭的native outer-return写入长度和随后completion-proof写入长度，按明确delta加入control/总账；下一步骤不再要求总账等于早console。其余组仍与base严格相同。proof只求稳定自身长度，写后由同原owner取得真实SHA，不制造自身hash/close循环。

后继同时核delta各字段必须整数非负上界、实际文件长度、原controller PID/sourceOwner/sourceEntry/request/receipt/console/raw hashes、同一owner PID、eventId和准确nextId。eventId绑定scope|role|requestSHA|receiptSHA|nativeSHA；重置、重复相加、伪增无来源或amountUnknown均拒。原once/halt和角色先序继续防重放。另将本次request/admission原写成本在启动前计入control，读取admission/前驱proof/native另计读成本，不能把写成本偷换成后续read。

本owner不转发或打印scope输出，additionalForwardBytes固定0，源码和PS同时限制；console输出及外层保存console按原base的两份console成本计。今后若增加转发/报告/新记录，必须先改合同再整包冻结B，不能沿用0。末步骤END的外层delta也计入原control/总界，不因没有后继而漏账。APK和command与control独立。

正常同原七步实测首步console base14229B，后续真实outer/proof新增2806B，合法带增量前账成功接续，末总control138880B/总logicalInbound140377B；是有限本地模拟，不是假称真实SDK安装成本。三项原entry负例分别实际拒OUTER_DELTA_RESET_OR_DUPLICATE、ORIGINAL_OUTER_DELTA_SOURCE_BYTES、OUTER_DELTA_RESET_OR_DUPLICATE。额外纯预算门样本因control满界拒WHOLE_SEVEN_ROLE_BUDGET_BEFORE_CHILD，明确不是实际SDK超量。

## CR-B02：同原生产outer/proof owner实际落实

新tools/outer_owner.py与reference/original-outer-owner-contract.md一起交。生产仍默认拒；未来activation另绑定owner源码/Python文件SHA与旧有入口/计划/产品/B/toolseal/newscope/runId/root/freshRoute/初始proof。原fresh tool/server/exclusive claim检查器沿既有受审机制，本包不新建/运行其检查，也不拿历史文件当当前事实。

同一Owner只按准确七角色顺序调用。原starter、waiter、两reader、stream/Windows handle close worker和每个原writer都由强引用保管；主owner持续观察其原线程，start/wait/readers/close及proof真正待返期间也能记超时，不再只在调用返回后查字段。close与write各只一次，读原bytes不重编码；stdout/stderr、原PID/argv/原handle实际返回与proofwriter时序分列。

outerSeconds覆盖原Popen注册前到实际start/wait/readers/stream+handle close全部返回；localProofSeconds每角色共享启动前request/admission以及外层返回后保存console/native/proof和原writer返回的本地时间，排除outer等待，前后两个本地段不重新领取预算。whole仍是独立scope观察。实际outer/localproof/whole的范围600/30/600保持；全部生产实值仍未赋，分项SDK观察15/15/15/15/45/45/90与App60不扩。240只是分项和，不是批次已用时间或kill许可。

首个正确原Popen前，request/admission原writer必须已flush/close/join。下一Popen前，前驱proof原writer必须实际返回并及时，才由同原owner形成新的admission；PS核其原request/前驱proof/source/PID等精确绑定。proof显式candidateOnlyWriterCloseNotProven=true，不能自行证明自身关闭或及时。超时写入前形成的候选approved字段不能用于直接调下一角色，真实owner已sticky关闭准入，不生成新admission；迟返也不能改为成功。信任边界是受审源码原owner及其实际控制流，不宣称JSON/hash可以认证恶意本地主机。

两个独立有限用例：outer0.1秒时观察同原3线程尚pending；proof0.03秒时观察同原1writer线程尚pending，有限自身close gate0.12秒后自然返回。二者最终均保持sticky失败，下一run_one拒绝，没有kill/interrupt/taskcancel/二次close/替代进程或自动retry。未知start/wait/write/close错误路径保持同原context与引用、不退出解释器自动释放，永久未知仅静态审，不注入永久故障。完整合同定义了初始pre-SDK proof必须已归还且完整计费；未来取不到准确受审fresh proof时首SDK前BLOCKED。

## CR-B03：成功回执严格必需schema

新增StrictReceipt/IntField/BoolField/StringField，先于成功语义。所有接受成功所需字段须存在且类型准确；整数只接受int/long，不接受bool、字符串、分数、null，必须非负且不超各界。firstFailure属性必须存在并严格null。completed/expected=10、source/output keepers=0、finisher owner=1、准确runnerFinishReturn、原worker/return/timely bool等逐项核。

非fixture再核完整10项数组/逐项原return bool、runId/snapshot/共享budget标记、单调body时间<60秒、包/进程/versionCode/version/signer和meter三项范围/零活跃FD/资产/未知，末mux原return/EOS/6sample/重开1/READY0/sync/实际fMP4类；原固定case顺序/身份等语义仍保留。真实fixture仅额外增加必需firstFailure:null，旧候选producer不改。

同字节纯RoleSemantic政策样本13项：零值/精确上界两项有限PASS；负数、bool冒整数、string、分数、超界、null、缺字段、非空firstFailure、缺firstFailure、整数冒bool、history错误类型全部拒APP_REQUIRED_TYPES_BOUNDS_OR_FIRST_FAILURE。独立tester原组合反例作为来源保留并标LOCAL_POLICY_NOT_ANDROID；本批正反不是实际App输出、不是Android复现。

## 七角色、来源与不扩预算

计划仍identity→global_idle→app_absence→test_absence→install_app→install_test→scope_all，完整准确argv在reference/exact-seven-role-plan.json，SHA f0309a72789c67e0e0cd4afd54ca9e814384dc07d934241a6c07fe1c75ca7199。固定HA1Q6WXR/TB138FC/API31/future fresh fingerprint；global独立完整一次processes+activities，其他项目busy立即ENV_WAIT。任一包存在即停；无-r新安装，无覆盖/清理/卸载/换包/设备替代，唯一scopeAll+fixture19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c+新runId。

产品seal39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad；app7151481B/f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad；test478124B/b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9。准确FIX02版本/同cert5e841a04...de808f、runner com.videokit.d1media3.android02.test.Media3Instrumentation及两个原包保持。

七SDK最大/并发1/无retry；四preflight65536+851968+65536+65536=1048576，两install131072，单instrument所有pending/final两流1048576，controllerproof1048576，总inbound3276800；binary outbound7629605，command每步4096/全28672，总logical outbound7658277。原同源read-locked APK pin、读取/承诺/SDK内部再读/wire UNOBSERVED分层保持，不以6144B本地stdin模拟冒真实7629605B或wire精确量。

过量仍明确失败：原read192 B/saved64 B，未存部分不称完整raw，不截到cap补绿。最终instrument最高仍PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN；SDK壳exit、App自报原return和outer原返不能证明finisher Binder/平台尾段，无READY/COMMIT/播放/DTS/隔离结论。

## 自检与完整保全

最终整套19.125秒<30，7组全部完成通过；原capture controller12个串行（7正常+2busy+过量/outer/proof各1），另1个纯政策PS host，无并发SDK。模拟stdin4096+2048=6144 B，文本已观察/写入149868 B<4MiB；13个语义样本+3原delta负例+1纯预算门。包含完整正常七步、busy实际producer→capture停止且下一app_absence未进入、pending+final bytes、真实stdin返回、原writer/外层窗口迟返后保持失败。

较早19.062秒整套结果也原样保留，是中间源码结果、不是当前最终源码证明；当时未完整保存owner源快照，不能冒充可重放最终源。随后补全对starter/wait/close worker及未知强持有、共享proof预算和pending时点的源码落实，最终19.125秒整套使用准确新入口/owner并完整保存entry/owner/driver快照。没有失败整套被改记成功，没有任何原UNKNOWN调用被重试。selfchecks/work全部历史与准确SHA在static-audit中分层列出。

默认owner与PS均PREPARATION_ONLY拒绝。SDK/ADB/5037/占用查询/设备操作/Gradle/JVM/媒体执行/共享cache/旧35512/48945/17257操作/kill均0。静态hash读APK/原ZIP不冒物理I/O零读或当前host idle。FIX02五项产品有限关闭保持、前工具独立B三缺陷原报告不回写。

## 交接与本候选身份

入口 105118bf3d027ce0cb220e9a07ec50dbdedbf316edb15c72b7a93f660a6f3096

准确outer owner 3aab1fee40b2989e41e3ca4a2750a5a481b0caa5c8691bf287b26900ad192fa3

限定producer 4b0aea7b372f737ae6d0970374d18d491c2f537c741df3fa7166c5ef654e8d5a

最终自检文件 ada73ae25cacd6a9b1177adc6d6f41d40f6d65bb19ac3e05c36dcd9437492bd4

完整source/contract/最小diff/所有原bytes/native/proof/负例/计时在本包。tools/verify_frozen.py只读核清单，不启动进程；不要在冻结目录重跑写入型build/selfcheck/audit/freeze。独立B应整包审三项及合同，在自己的新目录用固定源做≤30秒串行有限自检，未覆盖的永久unknown/真实设备分支保留NOT_RUN。

freeze清单覆盖本报告及候选全部其他文件，排除自身/外部ZIP以免循环；ZIP为全清单+seal，逐member长度/hash/CRC核。外置D1_ANDROID02_CAPTURE_READY02_FIX_HANDOFF.json绑定报告/seal/ZIP长度、hash及member数，发送回执另存冻结外。完整独立B通过后才由负责人单独签准确activation；既有用户平板授权保持，不重复索一般许可，本批不设备执行。
