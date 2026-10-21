# D1 E13J IO与审账契约 V1.0

2026-10-18 J-R1最终增补：本文件仅属最终R1，旧J首次包/源码/四文档/外seal保持不变且尚未另交审。收尾自核发现raw写异常可能令审账writer先退出，故真实源码修正为raw失败仅停raw写，审账writer继续等待同reader done，再写准确终止快照。新增AUDIT_AFTER_RAW_FAILURE真实生产回归验证原raw故障后仍准入的有限后续RX进入最终cw/in，未用harness额外facts。最终为10个有限组（原9＋新增1）及3父故障组；本revision一次host编译，整个J阶段两次，因实际源码变化而非同源机械重建。旧J算第十三组既有seal，均逐字节保持。

2026-10-18；最小修已有固定Socket/archive/父run，不增加通用框架。

F01 allowance在实际InputStream.read与OutputStream.write前执行。唯一reader下chargedWire=incomingWire+intendedTx；read传入min(wanted,remaining)，returned n才加实际RX；完整TX意图在写前扣费并入归档，writesEntered/Returned分栏。额度不足不执行该次read/write、不退款、不借第二条/其他预留。parse错误后的drain也同门控，余额0停止全部新IO、未知Socket不关闭，archive有限终止并审账，同原non-daemon keeper继续持有budgetUnknown；不会将未消费EOF当返回。最多两query串行，各wire70656+metadata2048，加base116736正好262144。原脚本/serial/白名单/同连接及第一真实归还后第二派生不变。

F02原writer在连接前建立intent和原facts文件。facts只有可选P（caller请求后首次可写切片）与T（reader结束/原writer尾通知返回后的切片），每条≤512，合≤1024；写入意图先计auditBytes，不按部分失败退款或重试。记录cw/in/tx/we/wr/rt/off/disk/rawQuota/frames/eof/exitSeen/exit/failed/late/qualification/budgetUnknown/readerBody/readerAlive/socketReturned/writerAlive/physical/why及auditOwnClose=UNPROVEN。cw是实际应用RX＋保守TX，rawQuota是帧长度预扣，不冒实际完整payload；off/disk是原queue/成功write事实，不冒power-loss耐久保证。

P/T是执行时点快照，P不保证恰在超时瞬间（writer可能先有原IO），T仍在原writer内，不能写自身join/close已证。无失败时qualification=SNAPSHOT_NOT_FINAL，失败/已超资格时FAILED；最终caller资格/各原线程真实join由生产Batch的有界J_PRODUCTION_RETURN_SNAPSHOT补充，落入既有外层Java32768B预留，不另分配query元数据。若迟到只发生在审账文件关闭后的caller调度阶段，不能回写旧切片冒当时已迟到，以该后续生产摘要登记。审账open/write/close失败保同原Op/keeper和计费内存，不以缺facts充成功；永不二close。

F03父holder在Popen/记录文件前登记；pending写入与print的任何BaseException只降资格并留有界诊断码，不越过finally内同原wait。wait本身未知继续原holder等待，不换Process；stdout/stderr分别尝试唯一close，任一未知则父仍持有而不再次close。只有同wait及两个文件close均已返，才可释放活动custody；最后诊断失败不改变这些已证事实或补资格。日志文件自身记录不自证其关闭。

审批pin ABSENT，正确角色在网络前拒绝；预算到限后可能永久UNKNOWN，不能承诺本批内自然收尾，也不通过kill/扩额处理。无真实5037/SDK/设备/旧handle/PID查询/处置/部署或产品重测；审批ABSENT、actualScope/release/once/sourceReview未签发。旧v17主PENDING、旧诊断LOST与H本地30384 RETURN_UNPROVEN三栏独立，未补ACK/退款。用户持续授权已存在，D1未过/M0未启、T07未派、P0/许可/历史FAIL保持。
