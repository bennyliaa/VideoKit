# HOST_TRANSACTION02 源task/原authority集中绑定

只修01静态F01，不修改原SourceLease/SDK/Media3接口，不替旧开发FAIL或独立8+3有限PASS改状态。新Binding保存sourceTask、原E13SourceGroup及原Identity引用的不可变快照；uid/pid/task/instance/epoch/generation和事务grant/outputVersion逐字段比较。requireSource先核准确字段，再核原group/identity引用；require也逐字段+原引用，绝不以key相等当授权。新registry generation1不是旧authority。

|消费点|绑定/版本义务|计划证据|
|---|---|---|
|Binding constructor/key|捕获原source.task；HTB2长度前缀+精确UTF16 code units/固定整数编码，缓存Base64，私有key最大2048字符|SRC_A/B只变task其余字段相等key不同；含分隔符字段不可拼接别名|
|Binding.requireSource/require|准确字段+同原group/identity，两个Binding包同原authority仍合法|错task与全字段相同但新authority分别拒绝；原authority正例|
|LocalTransaction constructor|requireSource在创建输出目录/注册host/原writer前|实际构造负例，root不存在、host owner不增|
|moveDrainedSource|require(actual)与requireSource(original)在源读/移动IO接纳前；仍需全lease/原worker排空|完整排空后错task/authority实际接口拒绝，source/dest不变、产品IO接纳计数0；原正例移动保持|
|RecoveryRef/queryPublication|准确typed Binding.require在业务query/record读取接纳前；HTX2才解码新key|错task/authority真实readonly入口拒绝，计数不增/record不改；原同grant新wrapper正例|
|LocalFormat|VKH2帧包含HTB2 key完整task；不是授权authority本身|准确格式正例、错task编码/分隔符编码负例、旧VKH1拒绝|
|私有record|HTX2头；旧HTX1准确拒绝，不读/迁移任何旧事务、不新COMMIT|当前实际record v2与原QUERY通过；旧header由共享production version函数纯输入拒绝，非旧事务复活|
|原opaqueTask snapshot|不改TemporaryOutput构造时捕获task/grant的原合同|真实委托host访问器改label后原已捕获grant仍完成校验/READY/COMMIT/QUERY|

authority引用不被序列化为伪造token，不建立新全局源ID表：不同原authority可有完全相同字段编码，但它们不能通过live require/构造/恢复/移动门。record和VKH2是有限数据引用，非可移交授权或真正进程崩溃恢复证明。Binding仅本候选私有host模型，未要求原SDK增加字段。

原8个真实文件case+原authority3回归保持，并预声明4个新增矩阵组。所有局部fileKey/hardlink身份、VKH本地格式与受控validator tag、READY/COMMITTED、UNKNOWN/首错、同原ACK/线程返回门不弱化。R03同bytes物理替换、TOCTOU/原FD竞态与隔离攻击本批未测，不宣布关闭。媒体/压缩音轨/Android/M0/网络/数据库不扩。

动态仅固定新本地命令可交工具require_escalated自动审核，不管理员/改ACL防护/换目录绕过。首次正式单读取之前的原monotonic值在first-read-clock.json；45分钟截止沿同一个counter，不从prepare重起。源码/依赖/完整argv/cwd/显式冻结env hash在实际Popen前order.json固定；env原值不入档、不改全局环境。一个严格JDK编译+一个串行worker，必要最多一次修复；不先跑受限权限探针。
