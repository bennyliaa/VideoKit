# D1 E10A 终局本机只读补审报告 V1.0

日期：2026-10-18。批次：E10A_FINAL_READONLY_REVIEW。

**结论：PASS_FINAL_READONLY_EXISTING_EVIDENCE。** 对既有冻结证据的独立补审通过：单次 actor1 生产迁移的原 identity/COMMIT、正常系统结束、PC 原资源自然归还、旧账档守恒，以及 catalog/checkpoint/seal 完整无环绑定均得到原始证据支持。原执行报告中的“最终审证未完成”由本新批次完成，不覆盖其当时状态或原失败脚本。此结论只接受本次既有 actor1 终局证据，不代表 D1 总体验收、产品激活或后续测试许可。

## 派发、输入与方法

负责人 VideoKit项目助理（01a107c3-2bf9-7fa0-94a0-234258ca6774）正式派发本机只读补审；需求已先保存于 docs/milestones/D1_E10A_FINAL_READONLY_REVIEW_TESTER_REQUIREMENTS_V1.0.md。

- 原报告 docs/tester/D1_E10A_ACTOR1_EXECUTION_REPORT_V1.0.md，原 SHA256：27bfa28db47d9956e1b151a81398e69fe483d39523dabbe353eac2659d0cd3b2。
- 原 manifest SHA256：e045e98bae54159c863f5ac01823cc5fc70c91591247681dc46f3cf917846726，所列217项全部匹配。
- 接受的候选 freeze SHA256：0a2d1c3a6c02f6194427ca93688a804f7df8d7966ffedb1ee0324cbccaf7d090，所列463项及源归档原pin全部匹配。
- 本批独立脚本与证据位于 docs/tester/D1_E10A_FINAL_READONLY_REVIEW_EVIDENCE。脚本仅使用本机文件/JSON/hash/Base64处理，无设备、网络或子进程调用；未导入或运行原执行控制器、生产JAR或原失败函数。

先静态核生产 E9Registry、E9Evidence、E9Catalog、E9Actor、E9Record、原受管主机与PC实现，形成新只读脚本，再执行一次独立审证，原进程exit0、两pipe返回，未修正重跑。共688个实际读入本机文件列入独立输入pin；不以原汇总的true代替raw stdout、原字节和原exit/归还回执。

## 七组独立审证

| 检查 | 结果及原始依据 |
| --- | --- |
| 冻结输入与源码 | PASS。原manifest217项、候选463项、原报告、原执行脚本、真实authority及候选包原pin均匹配。 |
| 授权与单向输入 | PASS。真实用户消息01a14cd3-0192-7072-afc2-c6052e9c15e7的具体批准、同次scope/新身份、接受报告SHA、scope→plan→config→index及registry授权引用一致。来源13、目标14/PREPARE/ABI1均绑定固定包。 |
| 原身份、COMMIT与控制 | PASS。新actor PID22086/UID10221/boot2/start17030020与原transport及独立ps/boot/proc回执匹配。identity34705365ns、COMMIT109746615ns；原COMMIT QUALIFIED_MIGRATION、owned34/unreturned0。四次原控制为STATUS1、EXEC2、STATUS3、ACK4，原bridge各响应小于5秒，无重放。 |
| 正常系统结束 | PASS。原returned与归档、ACK字节完全相同；754909B原日志hash、唯一原E9_FINAL_FINISH锚及其后正常finished inst/Killing PID22086匹配，既有独立ps回执确认原PID及相关app进程缺席。 |
| 完整终局DAG | PASS。四事件canonical、seq、parent、actor、evidence原SHA全部重算；catalog嵌入descriptor/actor/reserve/returned/finish/device均逐字节匹配；intent与durable reserve和actor重算一致；head、catalog、checkpoint、seal全链匹配且无自指/逆向环。 |
| 旧账档与三记录 | PASS。从原私有metadata采集stdout重新解码及解析stat，核13metadata原hash、旧guard dev/inode/UID/size/fence、完整1011B ledger全链及三R三S、107218消费/0预留；原三个产物stat身份与大小不变。新三文件与目录集合精确，无pending或其他M。 |
| 原PC归还与资源 | PASS。19份独立metadata原exit/pipe/hash回执和3份PC查询原返回匹配。生产原operations28、nonqualified/unresolved/unreturned/live均0，Store返回；原manager PID29504自然exit0、两reader返回，同handle两个边界显示同一pcClosed，唯一物理E9_PC_CLOSED actualOriginalReturns=true。 |

原actor准确SHA256（806B原actor字节计算）：**aa35cc47f8408f5a78bc2f322372d79a7c3f5fa5010453729f5759148223ad22**。原 COMMIT returned SHA256：dee972492b705bc3ac6801caaa786567d30ce711f9be01d77268675f7b51e668。

## 补齐的终局绑定

准确migration：4f21f71a-bf66-4a44-a287-320f0ae25fde；registry：bbf71f7f-ab67-4bf8-af8f-731a38963e49。

生产源码明确：captureReturned 在原QUALIFIED_MIGRATION验证通过后写归档事件 RETURN_OBSERVED；sealFinal 把最后一个合格归还actor在catalog中的disposition写为 RETURN_VERIFIED_IN_TIME。前者表示原归档事件，后者表示终局处置。本次分别验证两者及其实际原输入，不将它们互相替换。

四个原事件恰为：BOUND→RETURN_OBSERVED→NORMAL_FINISH_CONFIRMED→FINAL_ACCEPTED；对应证据依次为原reserve、returned、finish、finish。四事件均不引用catalog/checkpoint/seal等后继记录，最终head由原descriptor及四个事件原字节逐级形成。

| 实际终局对象 | 原SHA256 |
| --- | --- |
| final head | 6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5 |
| catalog，5853B | 27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7 |
| checkpoint，241B | f57af4f4ea47199dc28dfc1c6c7921aef3e66fafcf56337a09375b9c944ede7f |
| seal，502B | c99cf4565aba45c62232d5214f779f7b514df51392bc3736e934a04fde07a6ff |

checkpoint引用实际head/catalog/registry；seal引用实际head/catalog/checkpoint/descriptor/preparePlan/review，均为原字节重算。catalog准确actorCount1、disposition1 RETURN_VERIFIED_IN_TIME、termination1 ABSENT，全部actor2字段ABSENT。无actor2目录及activation-release。

## 守恒、开销与原报告勘误

原budget730a73e1-50e1-4198-a515-047104f00e31及fence662e9ecd-bede-42e6-bb58-ce81d668ff44保持。原owner64522:20304:10221/0B与lease64522:20385:10221/36B保持；原ledger1011B SHA f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba，三R三S/107218消费/0预留，前后原字节完全相同。0B、53651B、53567B产物只用原stat证据核身份/大小；未读取非零媒体payload。

新三份控制记录为959B intent、725B acceptance、244B commit，总内容1928B；文件系统stat块占用共12288B另列，不能把内容上限理解成实际磁盘块占用。原采集文件完整集合、旧文件stat及metadata前后守恒，新目录恰3个。

原报告有两项测试侧记录须区分：

1. 原最终审证函数将 RETURN_OBSERVED 误写为 RETURN_VERIFIED_IN_TIME，导致断言失败；当时未进行第三次兼容修正或重跑，原失败及原报告“未完成”状态保留。本次通过新的独立批次完整核验补齐，无重迁移或重SEAL。
2. 原报告表格actor SHA文本误写为 aa35cc47f8408f5a78bc2f322372d79a7c36c5fa5010453729f5759148223ad22。正确值见本报告及新audit.errata，为原actor字节、transport、catalog和device intent共同支持的 aa35cc47f8408f5a78bc2f322372d79a7c3f5fa5010453729f5759148223ad22。原报告未改写；原证据绑定未受此文字错误影响。

## 范围、NOT_RUN与交付

本次新增ADB/设备metadata/生产命令/安装/EXEC/ACK/SEAL/迁移/媒体读取均为0；没有访问设备或主机运行中服务，也没有生成新catalog。结论基于原批次记录的设备状态与归还证据，并非当前时刻重新探测设备状态。

NOT_RUN：新设备回归、actor2/3、产品准入/激活/播放、长期回归、原历史缺失出生证据或oldCloseACK补证。D1 NOT_PASSED、M0 NOT_STARTED、P0及历史FAIL和UNKNOWN保持，oldCloseACK仍false。既有单次迁移终局审证通过不解除产品门禁。

本批文件：

- independent-final-review-audit.json，SHA72f065c6286884b4774675c7896d705d4586a4f95a27e2493cd133b113229905。
- input-pins.json，SHA159314b189dde2aa687c229fc178caacb4e9e0fd9fdd462c0ac88e58d58a1e5b。
- evidence-manifest.json，SHA94b5079cd4567a61079481ad21ff6270180ff61d7f34265d85d98290874e680c。
- review.py，SHAbe65f9872320a7e9274441b8ee4ca00dcb9bfde745b27b88eb6ded6f5aa58b74；另含静态语义检查、原argv/exit/stdout/stderr与两pipe返回回执。

报告完成后主动通知负责人，保存通知回执，停止等待，不自动激活产品或继续测试。
