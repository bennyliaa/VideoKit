# PREAUTH20与FACTS V2阶段A审阅检查点

PREAUTH20及ENV02已获负责人接受限定离线B9/9；新V2只有字段建议和160条计划矩阵，全部NOT_RUN。原失败/恢复/图遗漏/UNKNOWN不改；SDK/设备/D1未过，M0未启。新草稿PR依赖#1且base为PR1分支，不合并发布。

逐文件whitelist.json为原字节SHA256及Git blob SHA1；excluded.json保留排除理由，完整本地manifest不改。最终stage-plan.json在本地记录含控制清单文件的hash，避免自身hash循环。Git后验/DELIVERY亦留本地并发负责人；不声称远端包含全部历史二进制、raw载荷或运行时。新V2浮动代码与工作单均排除。
