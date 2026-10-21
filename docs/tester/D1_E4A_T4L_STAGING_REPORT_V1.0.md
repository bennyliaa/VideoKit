# D1 E4A-T4L 暂存准入集中只读定位报告 V1.0

日期：2026-10-17，约10:28—10:31；设备：HA1Q6WXR；批次：D1-E4A-T4L-TABLET-20261017。依据 `docs/milestones/D1_E4A_T4L_TESTER_REQUIREMENTS_V1.0.md`，执行同批固定 shell/app 两份完整只读清单。

**结论：定位完成，两种暂存候选均未满足双身份准入。** 当前 shell UID2000 正确，原 base 的最先不满足门是 `test -d`（逐项清单中 `test -e` 也为1），stat 原错误为 No such file or directory。app UID10221/pwd 正确，但原 base、stage 和 Download 均返回 Permission denied。Download 只有 shell 视图检查通过，不能据此换路；未建目录、传输、改权限或启动下一批。T4P 原失败结果保持，D1 NOT_PASSED、M0 NOT_STARTED。

## 1. 固定脚本审查与执行

脚本仅使用 shell 内建/id/pwd/test/printf、toybox stat、head-c0读取/dev/null、空输入sha256sum、set-C无写子shell及只读df-k。无set-e；每个检查输出STEP_BEGIN/STEP_END及原rc，子项失败后继续固定授权清单，未临时替换设备命令。

执行前集中语法及无写/兼容审查PASS：

| 脚本 | SHA256 | 本机 sh -n |
| --- | --- | --- |
| shell-checklist.sh | 59880c299136e5a68eaf73a32c2fd129639c529358879fa654168c6bf1c53318 | 0 |
| app-checklist.sh | df65d211038e02434da7e57ba52f565a0aa3ba854c5bffe6fcc58879cf492408 | 0 |

本机初次 Git shell 语法检查在隔离环境启动时被 MSYS NtCreateDirectoryObject ACCESS_DENIED 拒绝，没有设备调用；同一集中语法检查以主机权限完成。df设备兼容性事先未假定，原支持/拒绝事实由本轮清单保存。

两个设备命令均固定 `adb -s HA1Q6WXR shell -n -T -e none`，app命令再带 `run-as com.videokit.app`，脚本整体准确引用，无payload stdin。每个身份仅执行一次。

## 2. 原始身份及全部路径检查

shell：id rc0、UID2000；pwd rc0、`/`。app：id rc0、UID10221；pwd rc0、`/data/user/0/com.videokit.app`；原身份和pwd比较均rc0。

准确路径：base=`/storage/emulated/0/Android/data/com.videokit.app/files`；stage=base下`e4_stage_T4P_TABLET_20261017_once`；Download=`/storage/emulated/0/Download`；internal=`files/e4_diag_T4P_TABLET_20261017_once`。本轮只查询目录元数据/权限，没有列目录或打开文件内容。

下表为原 `test` 返回值；L列是“是symlink”的正向测试，不能将拒绝访问时的L=1解释为已证明非symlink。

| 身份/对象 | -e | -d | -L | -r | -w | -x | stat rc/原错误 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shell/base | 1 | 1 | 1 | 1 | 1 | 1 | 1 / No such file or directory |
| shell/stage | 1 | 1 | 1 | 1 | 1 | 1 | 1 / No such file or directory |
| shell/Download | 0 | 0 | 1 | 0 | 0 | 0 | 0 / 见原stat |
| app/base | 1 | 1 | 1 | 1 | 1 | 1 | 1 / Permission denied |
| app/stage | 1 | 1 | 1 | 1 | 1 | 1 | 1 / Permission denied |
| app/Download | 1 | 1 | 1 | 1 | 1 | 1 | 1 / Permission denied |
| app/files | 0 | 0 | 1 | 0 | 0 | 0 | 0 / 见原stat |
| app/internal | 1 | 1 | 1 | 1 | 1 | 1 | 1 / No such file or directory |

shell stage、app stage、app internal 的 `test ! -e` 与 `test ! -L` 均rc0。但app stage伴随父路径权限拒绝，**不能以否定test成功证明它实际上不存在或安全可创建**。app internal在可访问files下，原stat显示No such file；本轮没有创建它。原base在shell视图没有成功目录观察，app视图被拒绝；不能拼接两视图错误推断全局不存在或具体SELinux/FUSE拒绝层。

两条成功stat的原格式为 `%d,%i,%s,%u,%f,%Y`：

| 对象 | 原stat | 模式与访问事实 |
| --- | --- | --- |
| shell/Download | `104,4459,3488,0,41f8,1792201679` | 目录，权限位0770，呈现UID0；实际shell UID2000的r/w/x测试均0 |
| app/files | `64522,7392,3488,10221,41ff,1792202151` | 目录，权限位0777，呈现UID10221；实际app的r/w/x测试均0 |

Download df 原挂载为 `/dev/fuse`，因此其呈现mode/UID须与实际身份访问结果分列。0770/UID0既不否认shell实测rwx，也不证明app可访问，更不能当作私有目录或root风险的单独证据。app/files的stat在内部路径观察到，不归类为Download的FUSE模式。未查询GID、ACL或SELinux标签，不猜拒绝根因。

## 3. 工具及空间原返回

两个身份的head-c0 /dev/null、空输入sha256sum、空SHA比较、set-C子shell均rc0；空SHA均为 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，没有读取设备文件内容。stat格式在各自可访问路径有成功原返回，故不能把base失败一概归为stat工具不支持。

Download df：shell rc0，原输出 `/dev/fuse 113511244 27299772 86080400 25% /storage/emulated`（1K-blocks）；可用86080400KiB。app df rc1，仅标题，原stderr `df: '/storage/emulated/0/Download': Permission denied`；app可用空间UNKNOWN，不用shell空间代替app可用性。

## 4. 原调用、回执处理与实际预算

| 原记录 | 原exit | elapsed | stdout/stderr | 实际STEP数 | 所有权 |
| --- | --- | --- | --- | --- | --- |
| shell-original.json | 0 | 1.125s | 1651B / 218B | 29 | RETURNED |
| app-original.json | 0 | 1.609s | 2431B / 389B | 46 | RETURNED |

两个原stdout均完整CHECKLIST_END，子rc和stderr原值完整保存。metadata共2≤6，各≤15s，本机归还观察2s。每流16KiB、完整保留16KiB，均未截断；两原记录8299B/11287B，均小于64KiB；审计写入前全部证据47833B，小于1MiB。无timeout、owned-child终止或creationUnknown；stdin/source/writer/flush及两输出close均实际返回，原退出已观察；retainedLocalOwners0、无在途，历史远端UNKNOWN_NOT_CLEARED。

tester本机处理缺陷如实披露：原driver将完整CRLF结尾按LF字符串匹配，误拒绝已完成shell回执并在执行app前停下。依据本任务允许安全完成其余授权只读项的要求，仅修正本机结束符判断并执行尚未开始的app清单；**shell未重跑、远端脚本SHA未改、未换命令、未增加设备清单**。原attempt.json/result.json保留；continuation独立留痕。原local-review中stepCount预测少算1，实际逐BEGIN/END审计为29/46，采用后者，不回填原记录。以上不是产品失败。

设备文件变更0，producer/push/copy0，payload stdin0，文件内容读取0（仅/dev/null空探针），真实媒体/旧残件/cache/budget/proc访问0，手机/安装/产品/Gradle0，signal0。无补建base/父目录、chmod、root、manifest修改、清理或下一批执行。

## 5. 证据及交付

证据目录 `docs/tester/D1_E4A_T4L_EVIDENCE` 包括两份准确脚本、local-review.json、原调用JSON、stdout/stderr原字节文本、原attempt/result、app continuation记录及audit-summary.json。audit.py仅核验本机现有回执，逐STEP配对、长度/SHA及归还PASS，不调用设备。

原记录SHA256：shell `facce2b24fdd4c010263da57cb752843e18655e1739d01e4fea49285ddb34f5d`；app `0446ed1495079a1bf89d189290b9d6ae7e31e011f655a4e496ae9bf40c87591d`。

本轮集中只读清单已完成并主动报告负责人。两种候选均无现成双视图准入证据；具体权限拒绝层仍UNKNOWN，后续方案须另行派发。T4P不回填通过，设备截断原因及SDK源码映射不因此关闭，P0及历史FAIL保持。
