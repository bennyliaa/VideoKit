# D1 E13H 固定只读角色契约 V1.0

2026-10-18。公开main只接受--describe或--g-readonly；后者无参数可传exe/serial/PID/shell，因无法排除server替换重启路径在创建owner/网络前硬拒绝。PowerShell也只接受准确Java/JAR/G角色/固定根/原scope、32768B host cap并硬拒绝，旧case/deploy角色拒绝。所有下面的组合链和前置目前仅包内离线原型，不能从公开CLI绕入；不是新可用产品入口。

固定argv1：SDK adb.exe -H127.0.0.1 -P5037 -sHA1Q6WXR shell -T，最后单一固定脚本完整dumpsys activity processes及ps -A -w -o UID,PID,PPID,NAME,ARGS，显式AM/PS begin/end和exit码。无截取/grep/部分行充完整；超过64KiB/10秒、非零/格式不识别/权限拒绝/其他active instrumentation即停止。大设备完整AM输出可能超64KiB，这种情形只拒绝，不追加命令或提高cap。实际API31格式与/proc权限未验证。

第二argv不能输入PID，由完整第一raw推导：唯一全局active instrumentation组件、mFinished=false、准确原runtime SHA/原batch D1-E13A-SOURCE-20261018/class/method；对应原mRunningProcesses中的com.videokit.app/u0a221必须与全局ps中UID10221/准确name/args/存在父进程一致。原am客户端须UID2000及准确完整scope argv、有效shell父UID。仅选择这两个明确角色PID；不能因未选择fixture/codec断言它们不存在或已归还。重复/缺失/异UID或其他instrumentation拒绝。

argv2只拼接已验证正整数PID到固定/proc路径，读取boot_id及这两个PID的stat/status/cmdline，逐项shell失败退出；检查完整边界、同PID/PPID/全四UID/准确argv/正start ticks。新start ticks与boot_id是第二切片身份，不证明两次间绝无复用，更不构成终止授权。未知/proc拒绝不fallback，不任意shell注入。

组合Chain先持有原supervisor并retainAuthority(同Chain)再启动child，沿用既审E9PcSupervisor Process/唯一reader、8×4096 archive、E4Owned close/actual原线程join。第一命令或解析失败/超资格，不第二命令，finally closeIngressAndSupervise可交isolation，非daemon原custodian继续保管同原对象。生产没有接出可执行once/审批入口，不会绕过旧pending gate；旧DISPOSITION_SHA ABSENT保持。

版本原型仅host:version、生产默认127.0.0.1:5037，单次≤1KiB/2秒资格；按固定OKAY+0004+4hex解析候选0029，不接受任意服务。E4Owned原Socket与唯一reader/非daemon keeper在allocate前登记；调用者超时不关在途socket，keeperjoin实际reader后才退责任，close未知继续保管，不二close。测试仅显式包内临时端口影子，生产CLI拒绝所以原型未连实际server。其输出与request共≤28B远低1KiB，未知/不完整/版本不匹配拒绝。未把预检插入生产dispatch，也未把候选41冒确切SDK构建证明。

无新产品安全ACK、无OS沙箱承诺、无行政终止记录。本轮ADB/实际5037/原exec42537读取/设备/处置/安装/部署/方法重测均0。旧主任务最后PENDING/UNKNOWN，独立诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN未解除，实际根因NOT_UNIQUELY_DETERMINED。E13F及历史冻结不改；用户持续设备授权已存在，当前限制来自准确范围与原任务未决。D1 NOT_PASSED / M0 NOT_STARTED，T07未派、P0/许可保持。
