# REAL_FACTS_HOST03 必需pin薄适配

仅修HOST02独立B静态F03，不改冻结HOST01/HOST02/Q07核心。原F01包装器独立新根/F02五项scope公式在HOST02 B限定关闭，保持原行为。原B未动态执行null host pin，不称已经证明真实未授权执行。

## 必需与普通读取

static_config对hostSourceSha256调用require_pin：exact str、非null/非零、lowercase64hex；缺字段由精确schema拒绝。Budget.read_pinned(path,cap,digest)没有可选默认值，在任何路径/文件open前核必需digest，再委托原Budget.read做有界原文件读取/fstat/close和实际SHA比较，无法把None解释成省略。合法格式错hash仍读原文件/原close后拒绝，费用永久保留。

Budget.read(digest=None)继续用于明确无外部期望摘要的bootstrap/普通读取，不默认填当前hash，不给必需pin调用直接使用该可选语义。原approved refs的read_ref也在open前require_pin，再原HANDLE身份前后/长度与无条件SHA比较。其原逻辑已有无条件比较，不冒另一个null跳过漏洞。sourceSeal/probe已有固定常量相等门；保持并转明确read_pinned消费。原fact_preauth.load_pins读seal回调也精确固定path+SEAL；不是改采集核心。完整消费表及AST行号见pin-consumption.json。

所有宿主必需原文件读：外部批准配置、host源、原SEAL/source30、固定probe、原load_pins seal回调、未来SDK固定摘要，均走read_pinned；原三份批准输入走strict read_ref。runtime/helper、FactsBundle/child/Gate内原pins按冻结原契约保持，无证不宣称其他漏洞。

## 配置与根

继续兼容HOST01 V1配置/返回wire schema，新的hostSourceSha256必须绑定HOST03实际host.py。fixed bundled Python入口参数 `-I -X utf8 -B <HOST03绝对路径>\host.py --config <批准原配置> --approved-config-sha256 <外部批准原bytes SHA>`；外部hash与负责人turn是信任输入，工具不发行真实批准。草案approvedfalse/null不可执行；JSON Schema和运行时共同说明约束，不能只靠Schema。

OFFLINE只允许两准确布局：

- `D:\CodexProjects\VideoKit\docs\coder\d1-real-facts-host03\selfchecks\work\<10hex或canonicalUUID>\<mode>`
- `D:\CodexProjects\VideoKit\docs\tester\D1_REAL_FACTS_HOST03_INDEPENDENT_B_EVIDENCE\fixtures\<10hex或canonicalUUID>\<mode>`

mode固定ok/fail/empty/bad/over。要求原字符串绝对canonical反斜杠、无dot/dotdot、无reparse祖先、精确组件及scope/mode两层；run拒已存在leaf，新批scope由正式事前输入冻结。开发不写未来tester根、不改H/S/BASE或原fixture白名单。唯一probe为当前候选selfchecks/probe.py，原字节hash d49ee2f675263186de11a3825b530a5612ed2f3cc09cd3969b765da7647efb7a，既有常量门保持，不自定义argv/派生probe。

LIVE原HOST01_EXECUTION输入/outer根和D1_ANDROID02_CAPTURE_EXECUTION事实home规则保持。原纯validate_scope在三输入接收/自身原file身份后、SDK文件/runtime/Journal/Capture/Gate/Popen/route Native前执行：SHA256(UTF8(planId|policy.entrySha256|productSealSha256|planSha256|runId))。严格原类型/语法及四份scope绑定，不把preauth.entry(facts_entry)替成policy.entry(capture_android02)，不修改输入使其匹配；后层原Gate公式与source/时窗门保持。

## 原API、归还与预算

实际链为admit_config_file→static_config→load_core/verify_inputs→工厂前Registry.check→原runtime→原Capture→原launch再次check→同原Popen→原collect→require_success/origin.require→归档。Registry保存原Popen与完整argv/program/cwd/env(None继承快照hash)/三流/shell=False/close_fds=True；audit不抛异常，Control无外部IO，直接复用冻结原Journal/Native identity/immutable_evidence/FactsBundle，不替换采集/等待/close算法。

成功需同原owner与COMPLETED/require、exit0/failureNone、无截断/未知及原wait/EOF/readers/流/H/Journal/control全部返回；RETURNED_BOUND不是语义成功。只历史归档退出，不candidate/review/qualification/七角色/驻留，不从文件重建Capture。真正未知停止新增保留原owner，不kill/二close/attach/补ACK退款；60秒不是强退未知的理由。

动态一次60秒/50秒停新增、worker1+五有限自然退出probe=6≤8、并发1/retry0、源读256MiB/永久输出4MiB。每普通读先cap/预留L+1再原fstat/SHA/一次close；新增必需格式拒绝发生在open前。runtime每次预留16读7,952,341B，helper返回不冒逐库close监测；每组Journal永久预留600000B，覆盖outer combined262144的hex及有限JSON，原单32768/128条/4MiB门保持，原stream/JSON另逐open预留，不按实际退款。

原LIVE58+A为25,053,680+A，Gate64/256MiB不扩；宿主config/source/SDK文件/runtime/archive另独立域，FactsBundle额外3读14011B/packet≤262144保留。原90whole/30Gate/20checker/15SDK/30outer/10proof与139264/8192/147456/outer262144嵌套限制不扩。

自有process身份沿冻结函数GetProcessTimes/QueryFullProcessImageNameW/GetProcessId；自有file身份沿GetFileInformationByHandle/GetFinalPathNameByHandleW，调用数从原函数完整返回推导，不冒API interceptor。普通fstat另列。真实route4/8 TCP、SDK镜像127ReadFile/SDK/ADB/设备/Gradle/Git不执行，旧05/capture1/锁/PID/session/历史once/FAIL/UNKNOWN不查询改写。

## 自检与交付

prepare只做静态来源/compile/源/config/profile/diff及pin表冻结。自检从原admit实际接收缺失、null、异型/错格式host pin，记录原配置close/费用/原Capture记录与Popen audit0及无输出目录；合法错host pin经原admit→run，实际host原读/close后拒绝。原schema/源码不能由测试驱动预挡替代。

五正负输出场景均实际admit→run(OFFLINE)→原Capture，不只拼组件；根/scope纯模型与自己原ref身份正反保留。原invalid-pin输入及五完整OFFLINE配置在子进程前原bytes/hash接收/冻结，都是合成离线绑定，不造可执行LIVE批准。原Q07 facts正例准确引用已接受独立B，本批不LIVE verify_inputs后部/run，不读SDKexe/DLL，不改fixture根。资源UNKNOWN/真实链接攻击不注入，静态边界如实标记。

完整源差异/必需pin表/原返回/费用/报告整批冻结交负责人，核后一次独立B，再另准确批准真实只读。开发通过不代独立B/LIVE，D1未过/M0未启。
