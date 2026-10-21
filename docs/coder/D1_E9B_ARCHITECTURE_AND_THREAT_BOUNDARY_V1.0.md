# D1 E9B 架构与威胁边界 V1.0

本批仍为合作式有限执行及已批准配置的威胁边界，不扩展为同机恶意进程防护或通用守护框架。保留原非等待 launcher、独立五秒广播响应任务及解码、96原Process操作上限、48资源/6帧/full EOF/1000us等框架门。没有新增device/root/kill/retry/cancel/reset能力。

## 原对象链

LIVE[原handle] → 原non-daemon custodian → 原Store → 已登记walk或file E4Owned → 原Stream/FileChannel。Store 在首个注册表IO前交由监督者持有，Registry也保留。HostManager额外持有原manager+busy callback，不能替代Store原资源检查。HostActivationSession从open前进入相同寿命域，导出路径也适用。所有业务调用结束/失败finally只关闭业务入口并等待真实pcClosed或真实同JVM隔离ACK；UNKNOWN不能转为returned。

walk在register后才allocate；allocate异常可能UNKNOWN，Error可停在ALLOCATING；close异常UNKNOWN，Error可停在CLOSING。全部returned=false。迭代或read失败但原close真实返回时，业务仍失败、资源却可合法归还，允许pcClosed；不能把所有业务失败一律永久保留，也不能把healthy=false误当归还。Store持有原walk直到实际CLOSED，不另建假流补close，不对UNKNOWN第二次close。

## 接入与监听器

同一监督者只使用原IPv4 loopback端口。短锁内先保留总accept名额，原accepted holder先登记，实际accept返回前后均有原对象；实际返回立即计额早于处理请求。SocketTimeout明确未接受时释放在途保留；歧义失败保守消费名额且持有未知原对象，停止后续接入。accepted+reservations不超过128，累计不清零；并发客户端排队不增加额度，TCP握手成功不等于应用实际accept。

128时先标记耗尽，停止accept，原listener close只尝试一次。第128个已接受Socket仍由原holder收尾。listener的CLOSED/UNKNOWN/CLOSING单独参与闭合判定；close未知时即使已实际native close也不得认定Java已返，已native关闭不是证据。达到额度后的监听器即使无法关闭，也不再accept129+。原进程wait/reader/解码/管道及Registry监督继续；没有新端口、预算续期或重启承接。

额度耗尽后状态通道为ACCEPT_BUDGET_EXHAUSTED，原JVM可持续占有未知责任，无法再经该TCP口查询或发CLEANUP；不得声称有限额度支持无限收尾。未来设备批必须事先规划有限查询预算。UNKNOWN以及永久未返可能让JVM长期保持；本批不通过外部强退代替归还。

## 证明范围

有限故障Hooks只切真实生产Store/walk/原listener/Process/共用boundary，元数据环境合成，不替换原业务判定。manager与activation下层入口测试不冒称执行获批设备CLI；CLI仍拒绝Synthetic环境。测试控制器结束专用未知夹具是清理动作，originalCloseAck=false、productionExitAllowed=false。真实Windows内核永久卡死、Android进程/广播/ADB可达性、全调度穷举均未验证。独立tester仍需审查。
