# ENV03 独立核验及两项环境复查报告 V1.0

2026-10-20；设备HA1Q6WXR；新scopeId `f0be73d2-01d2-4775-be6d-b6e55b8b77b3`。

结论：独立机械核验PASS，新鲜本地/tool/default路由/claim门PASS，identity PASS；global为 **ENV_WAIT_OTHER_PROJECT_OCCUPIED**。LendManager仍在平板前台。已执行准确2/2项并停止，无自动重试、部署、M1 ps、M2或产品用例。D1未通过，M0未启动。

## 独立核验

逐项核24行冻结清单及ZIP23成员和准确字节，旧activation33项未变。delivery SHA256 `47f9e9a504c00f4f172357d78c16ede428d3eae72ed1e1e1231c3a4d871f5994`；seal `37fbd2b0f4842099f6ffb27a642eb58d8e22d89b394925abd9ca6b44d70ad302`；ZIP `f20e61cfdcabb9154ec12af09251af295b734afeeabbc6bb48274ed868ac0bd0`。

实际授权原件与包内副本相同，SHA `dcc163aa7f4764a7cef146b33dadf1e5c86793be987efc95aefc1c315fcec44c`；environment-plan `ff23db7cdba88db95af9e9e39af8738fea4be9ec90b3cd9fb73402996051b27d`，policy `a32081b68c811497b122cac63d042816423c1776852bfda7ecfc301f3fb17ee8`。新scope/root、2操作、1MiB文本/1MiB归档、两请求/命令/前项依赖、所有来源pins均匹配；原入口与argv逐字节复用。

直接审原采集器源码：27行精确id槽查找，28行合法id正则检查；后三槽含冒号，精确匹配即被拒绝，删冒号则不匹配任何槽。合法交集仅前两项，拒绝先于上下文/记录写入及141行子进程Start。没有启动入口试探第三项；没有仅凭coder的10项自检放行。机械报告在现场执行前形成：`D:/CodexProjects/VideoKit/docs/tester/D1_ENV03_MECHANICAL_REVIEW_REPORT_V1.0.md`。

## 新鲜前置与身份

一次本地前置核对原registry13项准确字节、无未结claim（guard不存在）、新root及父目录不存在、无路由环境覆盖；仅随后创建本批输出root。一次现有5037监听器/所属进程来源核查：127.0.0.1，PID6804，准确批准adb.exe摘要 `b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f`，文件早于server创建。未启动客户端作额外版本查询、未改变server。

identity完整12段和最终标记齐全。TB138FC/API31/user0，主App17、测试APK观察版本0、fixture1；三APK准确摘要匹配冻结来源。UID10221/10222/10228；数据身份10221:6972、10222:4741、10228:21515。测试APK无额外版本17断言，按准确字节和已审签名/UID/data判断。fixture数据仅本轮记录，无M2要求。

identity原工具自然结束，stdout/stderr、EOF、读任务、pipe/file close、wait、process dispose、元数据与锁真实归还；后续独立调用完成身份语义核验并形成410 B外部completion proof，SHA `733917ae758aefd9ccd1b57f4010fab035b4cfb417c5940cfcf21c866bc8a67f`。随后才进入global，无预造证明。

## 最新占用事实

global完整原文347402 B，头、All known processes、OOM levels、最终mForceBackgroundCheck及EOF完整；来源准确SHA见语义审计文件。原文2230行起：com.lendmanager.app，UID10223、PID31712，curProcState=2、cached=false、foregroundActivities=true，Task256 visible=true；3604及4100行明确top-activity。本轮全文没有instrumentation字样；此事实不能推导空闲。前轮观察到的flexibletest测试进程未出现在本轮已知进程记录中，仍不能消除主App前台占用阻断。

本轮只读取本次授权原文，不追加查询或操作LendManager/测试进程。不停止、kill、force-stop、重启、清数据、安装或降级任何App。global之后未创建completion proof，不授权第三项；即使环境空闲，本批也应在两项后结束。

## 实际结算及归档

| 项目 | 实际 |
|---|---:|
| 已进入 / 操作上限 | 2 / 2 |
| identity原始读取 / 保存 | 23907 / 23907 B |
| global原始读取 / 保存 | 347402 / 347402 B |
| SDK原始读取合计 / 原始保存合计 | 371309 / 371309 B |
| entered、receipt成功写入 | 5019 B |
| 原console / 留存console副本 | 3039 / 3039 B |
| identity外部proof | 410 B |

两次原工具均真实exit0，无未返回session；捕获器firstFailure=null，全部原资源实际归还。SDK读取、保存、控制、转发/副本分列；原始读取无UNKNOWN，无资格超额。原始保存不是读取硬界，未来超额/未知仍须照记，不能将cap或文件大小冒充未知实际读取量。

控制类按既定55296 B采集控制、16384 B本地前置、32768 B报告/结果分别保守保留，覆盖控制记录和分析/报告，不把表中小计冒充全部控制总量。以实际原始371309 B加完整控制预留104448 B计为475757 B，低于独立文本上限；归档按实际逻辑文件核验另存清单，不重复归档整份原文。未指派354304 B不授权额外操作。新预算不继承旧2项/388818 B、旧UNKNOWN/8192或旧409600，旧账本/产物不改、不冲销。

最终账本与证据目录：`D:/CodexProjects/VideoKit/docs/tester/D1_ENV03_REVIEW_EVIDENCE`。准确原始产物：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME01_CAPTURE_EXECUTION/f0be73d2-01d2-4775-be6d-b6e55b8b77b3/outputs`。关键文件为actual-execution-ledger-final-v1.0.json、M1-identity-semantic-audit.json、M1-global-semantic-audit.json及各原工具结果。无本轮pending原采集资源；保留完整原文和凭证，不清理旧UNKNOWN。

本报告主动交负责人接收并协调后续环境安排。ENV03已结束，不自动进入后续测试，不复用本批已消费的2项或旧permit静态状态重跑。
