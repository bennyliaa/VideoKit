# E11-R1 最终架构边界

继承E11 source-pinned真实catalog→每host当前guard/fence/完整合法ledger/无pending/实际原holder返回→进程内epoch grant链；历史catalog、测试选择或normal receipt不代替live proof。原6帧/fullEOF/1000us/生命周期门未改，Android runner/UNKNOWN finish仍未实机验证。

部署链改为：新的人类明确授权+真正接受的E11 source/release→新canonical deployment config（内含固定dispatchRecord）和其原SHA→原同JVM supervisor持有独立once原holder→CREATE_NEW/force/readback/真close→原精确APK/source/ABI/UID/idle/升版/同签名两install-r门→原Process/pipe真实归还。原final registry只读，不追加release/events/head。持久一次记录替代原registry CREATE_NEW闩锁，不能只凭进程内计数；未知不能换JVM/同config换路径重试。

记录只在未来新E11执行目录，≤4096B；配置pin绑定唯一绝对路径，既存父目录，不在旧registry内。没有新secret/密钥/远端根/审批bool，原N2授权只是历史DAG来源，不能授权新安装。若人为换路径，就是改变配置SHA，需要新的明确审定范围，不能作为自动恢复。记录无完成/close声明，力求只保留原先的一次派发强度；不声称SHA可认证人类批准或抵抗root/恶意同UID/自洽回滚。

E4Owned mutable IO在open前登记；并发FileAlreadyExists明确无FD，其他UNKNOWN/在途原对象保留。已知业务失败真返只允许失败安全结束，不授准入。force之后close未知也不能安装；marker存在使另一进程拒绝。原supervisor/96操作/128accept/5s控制55s一般响应、无强停取消、不可重放语义保持。文件force不额外证明Windows目录项在任意掉电模型下的持久性。
