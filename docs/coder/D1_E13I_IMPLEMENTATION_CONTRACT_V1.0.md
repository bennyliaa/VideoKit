# D1 E13I 原对象与协议契约 V1.0

2026-10-18；最小角色适配E4Owned与既审archive模式，不建立通用ADB客户端。E13IIdentity只保留既审准确G身份门/脚本，删除SDK命令工厂及版本原型；原183 F类准确沿用。E13IArchive仅将原process归档适配为socket wire及EOF/协议EXIT分栏，不伪造Process PID/exit。

## 先登记、单一关闭与实际线程返

Batch静态强持，在once/force/close前启动非daemon原keeper；准确intent原FileChannel归还后才能连server。每Op在allocate/connect/write/read前登记OWNERS，拥有唯一reader、原Socket、借用流、原archive writer和非daemon keeper。InputStream/OutputStream不自行close，唯一E4Owned<Socket> close只在原读取EOF/实际IO异常返回后执行；解析错误而shell可能仍运行时，同reader先drain至自然EOF/IO返回，无强关、二reader或重连。

reader与archive writer体内flag不自证线程结束。keeper join同一原reader，在原writer外确认其实际终止并join、每原文件close均返，才认物理资源归还；caller也join该keeper后才可资格成功/第二查询。Socket close失败或文件UNKNOWN，原keeper无限强持，不二close；资格10秒只能封依赖并返回PENDING，不能取消调用/线程。原writer尾通知未返时不能提前认资源归还。facts是提前快照，自身close/线程return不由该文件自证。

## 精确协议与固定白名单

仅固定127.0.0.1:5037，精确host:transport:HA1Q6WXR→同Socket shell,v2,raw:fixedScript。length为4个ASCII hex，status只OKAY/FAIL，FAIL限定256B且不fallback。shell帧5字节（ID+LE uint32，目标Android arm64 LE范围）；ID只接收1(stdout)、2(stderr)、3(EXIT)，EXIT必须长度1；无stdin需求仅发送一次4号零payload close-stdin。status/帧均逐字节读全，读碎片不当一帧；整数先校验再固定4096B块读，未审长度不申请大数组。单帧及两通道累计≤65536、帧数≤256；重复EXIT、EXIT后额外数据、未知ID、截断、EOF无EXIT均拒绝。

合法EXIT0与EOF仍分别必需，stderr非空不通过。EXIT无EOF资格失败保原Socket；EOF无EXIT虽物理归还但查询失败。第一query.run完成并实际join后才完整解析global instrumentation/ps，从准确旧scope/batch/class/method、app UID10221与am UID2000及父关系推导两个PID；无任意外部PID接口。第二读boot_id/stat/status/cmdline核准确UID/PPID/argv/start ticks，只是第二切片，不作旧owner ACK/终止许可；其他instrumentation/格式权限未知/全量超cap拒绝，fixture/codec未匹配仍UNKNOWN。

## 有界账及留存

Batch固定base116736B（host8192+exec65536+Java32768+observer8192+intent2048），每query预留72704B（双向wire70656+两metadata各1024），最多两query总262144B，不退款。wire记录发送意图（是否write返回另栏）及实际收到的handshake/status/FAIL/frame/payload；没有另写stdout/stderr副本，console只摘要。wire中的TX意图不是实际全部已发ACK；incomingWire/intendedTx/chargedWire及writesEntered/Returned分开。retainedWire是保留尝试的上界，queue offered/written及文件长度是不同事实；失败时不得冒完整持久化。

wire/帧/记录超限立即失败，不扩大留存：同原reader仍固定4096B buffer自然drain，截断/丢弃明确标记且保全部预留，不无限增长内存或补空raw；未留存实际流量可能超过cap，不能称实际全部接收预算成功。archive8×4096有界队列、原wire cap70656，queue满/落盘异常停依赖；尚在途保持原对象。所有资格都不是强制平台截止。once/current release/真实scope/sourceReview未签发，现审批pin ABSENT，无生产执行。

本轮实际5037/设备/SDK/旧handle读取/处置/安装/部署/产品重测均0。旧v17主任务最后PENDING/UNKNOWN、旧ps诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN、E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN三栏独立；本轮不查历史PID、不补ACK、不退款。用户持续测试授权已存在，原任务未决与本阶段范围继续限制执行。D1 NOT_PASSED / M0 NOT_STARTED，T07未派，P0/许可与旧候选不变。
