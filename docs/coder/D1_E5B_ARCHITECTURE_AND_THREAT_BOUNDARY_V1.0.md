# D1 E5B 原资源打开与架构边界 V1.0

2026-10-17。处理E5A-F01，不回退旧E5-F01/F02静态支持。保持压缩解析普通isolated CPU、同UID codec故障边界、真实六帧/isolated EOF/PTS/缩略图、flags与实际STARTED ACK及trace。:e4_codec不是权限/RCE沙箱；独立Kit/Flutter/P0不因此完成。

## 专用现存与全新创建入口

E5BGuard.existing只调用IO.openExistingNoFollow；Android为O_RDWR|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK，明确没有O_CREAT/O_TRUNC。正常新owner/lease只能经E5BGuard.createNew，Android另用O_CREAT|O_EXCL|O_NOFOLLOW、0600，不能复用孤立旧文件。不存在“exists成功后MODE_CREATE”的回退。旧AndroidLease.exclusiveInto工厂无调用者后已移除；仅增现有JNI的注册PFD lock/unlock桥，不改native二进制。

Guard在任何open前注册，描述符结构先存raw，再存dup，再设置dup FD_CLOEXEC。fstat核实际raw；JNI flock在共享同一open-file-description的dup上，因此身份属于实际被锁对象。close逐实际unlock/dup.close/raw.close尝试并存状态，任何未知不重试，原资源保持可达。尚未取得锁的准入失败不重复作关闭前fence校验，实际FD正常关闭可如实归还，但操作失败不授予资格。

## 句柄角色与身份

现存入口先lstat NOFOLLOW核普通文件/预期UID/长度，再非创建打开。对实际打开FD fstat核同角色，dev/inode/UID须与打开前路径和指定历史身份一致；锁前后verify重做fstat、lstat和fence读取。owner必须0B，lease必须36B且实际FD读取最多37B与准确UUID逐字节相同。非普通节点、符号链接、错误长度/fence/UID、缺失、替代inode或路径/句柄不一致均拒绝。

O_NONBLOCK避免路径类型竞态变为FIFO等时无界阻塞；类型仍必须fstat普通文件，未读取不合角色的数据。fence只写已锁的lease原FD，前后复核身份/长度/epoch，不通过路径重新打开写。任何身份变化或真实close失败不得成为live proof。

恢复在实际取得旧N2 owner/lease且未修改前，把两原FD的dev/inode/UID写成82B guard.identity，绑定原task。旧N2 lease仍须准确原epoch；记录不允许来自caller布尔或随意替代文件。之后fence、S前和关闭前复核原guards。观察读记录和已ABORTED journal当前fence，再取得指定原身份的两existing guards，元数据前后均核记录不变；文件同字节但inode不同也拒绝。旧E5A无此记录的部分恢复状态不能倒填，必须BLOCKED另审。

## 全部相关消费者

原N2恢复、最终观察、当前E4FencedTask.workerLeaseClear/READY/abort都走existing。新任务initialize owner及首次issue lease才走createNew；记录lease身份后不再创建原锁。abort把现存lease成功获取移到任何ABORT_PENDING journal修改之前，避免缺lease还改原journal。WorkerLease接已授权PFD并核epoch，本来不按路径创建。正常transfer打开是READ_ONLY/WRITE_ONLY，无CREATE。原input/输出哈希、before/anchor/complete读取加NOFOLLOW；新metadata仍明确CREATE_NEW。

还移除“现存ledger RandomAccessFile rw可补建”的路径。恢复及预算已有ledger使用READ/WRITE/NOFOLLOW FileChannel和原实际FileLock；只有全新预算初始化单独CREATE_NEW，原header/R/S/哈希链/累计消费和实际force/close保持。缺失/链接不补文件，不换账户或目录。

## 原准入、收尾与证据边界

E5AAdmission固定N2预算新host默认拒绝、完成文件不提供许可，E5ALifecycle原owner/CONTROL真实归还或首次30秒绝对截止仍保持。源码与E5A逐字节核验；仅跑定点close UNKNOWN/新host观察与late-deadline，不重新执行全部历史模型。新guard身份失败不会让预算R/S或live grant出现；正常健康现存资源仍可通过当前真实返回资格后reserve。

观察现有文件force从14增为15（新增guard.identity），两次metadata读回仍有界；guard record82B、owner record≤256B、proof≤2048B、ledger≤128KiB、输出hash≤2MiB，无递归设备扫描。恢复holder仍≤32，观察≤48，另保预算校验holder与目录barrier≤16。原R/S/失败产物、guard文件和前像保留。

本机用真实Windows FileChannel句柄，经本机JBR内核属性包装读volume/fileIndex绑定，而非文件名布尔；Windows范围锁是本机替身，不是Android flock。UID映射与目录FD替身是模型。两个实际Junction代表重解析拒绝，但不等真正文件SymbolicLink；当前普通/提升环境均Win1314，因此真实符号链接本地证据NOT_RUN。Android public API已离线编译，真实Android symlink/fstat/flock及掉电语义仍未执行，不能外推。
