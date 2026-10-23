# 固定 facts 预授权与运行时填充边界

`reference/fact-preauth-schema.json`为封闭字段表；Python原校验另严格拒绝重复/大小写重复、额外字段、整数布尔/浮点替代、非规范UTC、错源/错scope/错设备/错动作/错预算与失效窗口。JSON Schema的integer语义单独不能排除1.0，不能替代运行时校验。binding的整数身份来自原Gate，不接受调用方填充。

入口 `tools/facts_entry.py --template <准确文件> --approved-template-sha256 <负责人外部给定SHA> --policy <准确规范字节文件>` 必须三项显式提供。模板生成不给权力。hash参数是受信启动方的批准输入，程序验证其与收到的字节相等；本方案没有签名、密钥、外部来源鉴别或IPC，不能从hash本身证明某人确实批准。不得把同调用者计算的hash冒充外部批准。实际LIVE须另派准确模板/外部hash/新批，当前未执行。离线负例固定原批准hash后修改caller模板，证明自生成新字节不会沿用旧外批；这不证明真实外部往返。

模板固定sourceSeal/gate/collector/binder/facts-entry/runtime/SDK/factPlan、policy字节摘要、唯一scope/plan/run/nonce、home/output、LIVE或OFFLINE_FIXTURE、负责人线程与turn、UTC有效区间不超过90秒、设备HA1Q6WXR/TB138FC/API31/user0、固定七query与原90/30/15/10秒、SDK1/并发1/retry0与stdout139264/stderr8192/合147456。不允许任意shell、额外查询、目标七角色、安装、媒体、系统服务或资格发行。template.entrySha256是facts-entry源码；policy.entrySha256仍是原capture PS，校验明确区分二者。

同原PreparedFacts对象唯一创建原Gate，构造时即消耗进程内scope/plan/run/nonce admission；跨进程相同模板仍绑定同一全新输出home，重复prepare不能覆写原输出。LIVE claim固定原共享路径。无失败退款/rearm。prepare后同owner绑定原scope/generation/holder/file-id/route/proof/receipt/ticks，接收时逐字重核该原binding、当前Gate及原文件证明。没有合成legacy authority/approval。没有等待人或跨窗口填充实时hash。

新回执`GLOBAL_IDLE_FACT_CAPTURE_V2`使用authorizationKind/externalPreauthSha256/runtimeBindingSha256；旧V1保留authoritySha256/approvalSha256。两种授权只进入同一原私有capture体；等待/reader/stream/H/claim原生命周期不重造。body返回、claim释放和外层真实退出分列；候选中的writer-close未证明标记、原FAIL/UNKNOWN不改。

本批不把V2 facts接入资格接收器，因而没有新qualification V2路径或真实资格输出。未来若开发该适配，仍须负责人独立核真实facts/HOME窄政策、目标source/scope/plan、原返回及不超过300秒新鲜期，另立完整开发批。原V1资格45矩阵/17条件正例本批回归，不可用预授权代替资格。

IO采用原Gate/source与control账本、原Capture/Journals，并在整批计划中保守预留三套原Gate source上限及解释器/PS导入/驱动/控制读取；预留总905969664字节，小于1GiB。该数是静态保守预算，不能表述为实际测量的全部物理IO。新增template/policy、binding创建和receiver载荷都计账；内存再核不冒充物理文件重读。输出含源码/证据/ZIP合计须小于16MiB。无免费源重读或重复ACK。
