# C12 注册握手与绑定撤销设计

2026-10-16。输入为 C11 最终报告和 C12 正式需求，编号 C11-T01、C11-T02、C11-ENV01。只完成本机验证，实际 Binder/解绑/正常帧尚待设备证明。

## 已证事实与根因边界

C11 MP4/AVI 各三个隔离进程实际 onBind 报 CPU_REGISTRATION_REJECTED，随后死亡并被系统重建；App 无注册记录，最终未知绑定/槽保留。原注册代码要求 flags 恰为0，是静态兼容性缺陷；第118行合并了 transact=false、ACK错误、尾随数据，未保存实际接收flags。因此不能声称设备已证 flags=16、AppOps位或某个权限拒绝为唯一根因。具体运行分支须用C12新日志证明，不重写历史FAIL。

## 固定握手及认证

RegistrationProtocol 仅使用 primitive 字段。正常 REGISTER=1，合法worker回报已观察到的致命注册错误 FAILURE=2；仍使用同一私有registrar与同一Service，没有新增组件/权限。请求最大512字节，descriptor、内核 caller PID/UID、task/epoch、endpoint、末尾数据逐项验证。实际PID须正数、非host，UID须满足原普通isolated范围且非host；不接受PID0，不从请求体采信caller身份。

同步条件是 `(flags & FLAG_ONEWAY)==0`。其余框架metadata位不作为异步授权或业务指令；未知code、descriptor错误、会话/身份/endpoint错误仍拒绝。oneway含任何metadata组合均不执行登记/回报，不写业务reply。其他自有Binder入口已检查，没有另一处要求flags恰0；CPU控制继续沿用按oneway位判断及UID/PID/session校验，历史legacy协议不扩展。

同步reply恰16字节：MAGIC 0x564b5232、VERSION1、result枚举、generation。OK/DUPLICATE/RETIRED分别为0/1/2，成功generation为1～4；错误10～28且generation=0。错误枚举区分ONEWAY/CODE/DESCRIPTOR/INPUT/SESSION/IDENTITY/ENDPOINT/DUPLICATE_IDENTITY/OVERFLOW/CALLBACK，以及TRANSACT_FALSE、REPLY_LENGTH/MAGIC/VERSION/TRAILING/ENUM/GENERATION、TRANSPORT/MISSING。双方不通过不可信异常反序列化还原错误，不使用readException处理注册reply。

每次registrar入口记录真实code/flags/caller PID/UID/input_bytes及固定result/generation，只记录宿主自己的task/epoch，不写来包的任意字符串、路径或异常内容。worker分开记录固定应答错误。合法致命失败回报携带同一认证session/内核身份与端点，先保留首次REGISTER原因、立即撤销Source并终止等待结果，再尝试登记为撤销端点并链接真实死亡；即使记录溢出也不能丢掉已收到的首次原因。失败回报自身不可达时宿主仍可能只能记录CONNECT timeout，worker本地原始分支独立保留，不伪造跨进程已知原因。

重复的同端点/同身份返回相同generation，只链接一次DeathRecipient；重复端点身份冲突拒绝。正常首次身份不改，终态/FAILURE端点不能被重新选为primary。额外端点只有HELLO/STOP，无START/broker/source token/FFmpeg配额。MAX_WORKERS=4继续仅为历史/异常端点记录上限，全局仍2个CPU任务槽，溢出永久quarantine。

## 撤销与释放分离

BindingRevocation 单独保存 bind issued/in_flight/accepted/uncertain、revoke requested、unbind attempts/pending/closed/result。取消立刻设置终态、撤销Source、提交STOP并请求独立UNBINDS执行器；不等待注册、HELLO或allDead后才安排解绑。UNBINDS为2线程/4队列，与连接/RPC/STOP/额外端点撤销分离。Context.unbindService 不在client或workers锁内调用，主线程cancel不做同步IPC/等待。

cancel早于bind返回时保留撤销意图，真实bind返回accepted或异常uncertain后立即安排；真实bind调用仍在途时不假装已完成，预算保留。未发起绑定、明确bind=false仍沿用原未创建证明；bind异常/超时/解绑成功均不推导未创建。HELLO失败、明确null/binding-died、未知连接和CONNECT超时同样请求撤销；未知端点不放宽身份认证。

解绑成功仅置binding_closed=true和UNBOUND_WAIT_DEATH；所有已登记worker仍必须有各自实际DeathRecipient，注册表为空的accepted/uncertain绑定保持未知计数≥1，即使解绑已成功。未知/溢出、Source/回调/RPC/STOP/解绑仍在途或失败均不释放槽。重复cancel不重叠提交也不悄悄重试失败；显式recover可重试解绑，累计最多3次，真实调用返回才减少pending。三次失败仍quarantine，不能声称重建已停止或借系统finished-inst/ps空补PASS。

start不再在等待期间持有对象锁，使用一次性AtomicBoolean门禁，终态/重复启动不复活；清理预算不因争抢start监视器延长。Source及既有第一异常/cleanup suppressed逻辑保持。

## 验证和未证限制

本机 Registration/Binding/Generation/Trace及旧host规则测试分层记录；纯模型不是实际Binder。新增真实隔离进程metadata/oneway/坏请求探针、坏ACK与尾随数据、注册在途取消、迟到bind返回、解绑失败显式恢复等Android方法只编译。LocalHostIdentity方法是Android本地Binder负例，不能冒充跨进程错误kernel UID已测；远端隔离正例和拒绝探针另有真实Service路径。

原STOP_STALL/ACK-loss测试新增可控解绑闸门，仅在这些Debug方法显式配置，用于保留实际STOP在途/响应丢失的反例窗口，finally释放；生产cancel不持有此闸门。未知注册/迟到bind用例没有该解绑闸门，必须看到实际解绑已完成而注册仍在途、slot仍保留，以及另一任务继续完成。调试闸门最多10秒，超时失败不清零任何未知预算。

C11的原OS status/trace分栏、最多3条流、读/close pending隔离、严格signal0 UNKNOWN/FAIL全部保持，C12没有更改取证判定依据。原C10/C11未执行的代次/trace路径在正常前置恢复后才单次验证；依赖失败立即阻断，不无限修复重跑碰运气。系统回调/创建顺序和OEM行为仍须新设备证据，binding_closed后出现未知新进程/登记应判生命周期失败并停止调度，不能引用旧slot释放记录掩盖。

手机C11-ENV01仍独立环境阻断；用户已在正确设置页且没有启用按钮，不重复要求找按钮，不绕过系统控制。D1未通过，不进入M0。
