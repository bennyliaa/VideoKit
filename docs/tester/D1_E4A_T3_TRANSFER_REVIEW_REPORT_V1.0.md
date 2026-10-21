# D1 E4A-T3 features修复独立复审报告 V1.0

日期：2026-10-17。依据 D1_E4A_T3_TESTER_REQUIREMENTS_V1.0.md。

**结论：SUPPORTED_FOR_SEPARATE_ONE_SHOT_T3P_DIAGNOSTIC。原 E4AT2P-F01 获得生产代码及已有离线证据支持修复，未发现新的静态阻断。支持范围仅为另行派发的新 T3P 一次256B合成诊断；设备兼容性及实际收发仍未验证，不支持媒体补传或产品测试。D1未通过、M0未启动，P0/历史FAIL保持。**

## 1. 冻结身份

| 项目 | 核验结果 |
|---|---|
| 外 seal SHA-256 | 4fbeef4948c8615e406b0e3a778d1c499c7a8c6fc133dc75822972a5a38e6628 |
| 源 ZIP SHA-256 | eb7a66f8e693efb9c1256a52e32a2d978154cfb122cf0dd7aabb416c9c1c084c |
| 已检查的只读 verifier | PASS，57源/59不可变；精确文件集、归档成员/内容及最终语义证据一致；物理2,126,266 B/68文件，逻辑归档861,674 B |
| tester独立审计 | PASS，见D1_E4A_T3_EVIDENCE/audit.py、identity-and-offline-evidence-audit.json |
| 原220B绑定 | 与tester实际T2P stdout逐字节相同；SHA05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce；原收据总量、完整prefixHex与摘要一致 |
| 历史保持 | 旧T2/T2P报告/产品冻结及原文件保持；exact_process.py与T1/T2字节相同 |

本轮仅静态及已有证据审查；未导入解析器进行新回放，未执行内存诊断/fake重跑、ADB、设备、真实媒体或Gradle。另阅读引用上游ps源码以集中核对接口，不是设备命令执行。无在途执行。

## 2. E4AT2P-F01修复复核

生产 diagnose_once.call 在保存原收据后调用 command_response.complete_stdout；features再直接调用parse_features，不是仅测试脚本修复。新响应门同时核：

- 原PROCESS_IO_COMPLETE_ONLY、ownership RETURNED、原exit0且已观察、firstError为None、errors为空、creationUnknown为false；
- 实际flush、stdin close、source close、writer返回及stdin关闭异常为空；原T1全局owner/线程门不变；
- stdout/stderr的drain close已返回、无错误、前缀未截留；从完整prefixHex还原原字节并独立匹配总长度与SHA；stderr必须完整为空。

不完整、原非零/错误、关闭未知或截留不能因解码后文本包含shell_v2而通过。这个门只观察原记录，不执行额外关闭或IO，也不推断远端所有权归还。

parse_features使用ASCII完整匹配及明确CRLF/LF/逗号分隔，生成精确token集合，仍要求精确shell_v2。原220B CRLF现有回归通过，LF、逗号、混合、单项、重复项均有已有证据；shell_v20/noshell_v2/shell_v2_extra/大小写不同不作匹配。空响应、BOM、非ASCII、空格、孤立CR、控制字符拒绝。连续/结尾分隔允许，前导分隔拒绝；未因本次修复改成子串或宽松strip后猜测。

限定token为字母/数字/下划线；未来CLI如出现其他格式会停止，不应由tester自行放宽重跑。当前已给定真实原输出在此范围内。原T2P误判不能改成设备不支持，已消费的旧attempt及原结果不修改。

## 3. 67项证据的实际范围

main-001一次离线批次、零测试修复补跑，共67条记录且全部passed；绑定五个生产/检查输入、原220B与原日志。封存核验器的LF/CRLF比较修正单独保存，不是67项重跑或生产变化；冻结后的逐字节哈希仍严格核验。

已有证据直接导入生产响应门/特征解析器：原收据成功和旧假拒复现、明确分隔和相似token拒绝、原响应退出/关闭/截留/长度/摘要/stderr等26组变异均有对应断言。另有7个features流程内存场景及1个其余自有标记CRLF合同场景；这些transport只是返回合成收据，没有启动子进程、运行shell/ADB、打开payload或写设备。

内存场景中的成功状态、UID10221/PID123、submitted256与独立SHA都是合成合同，不是设备/文件/系统资源实证；七个features场景中“进入第二调用”也只表示特征准入通过，不表示原run-as已执行。实际检查脚本创建的子进程0、payload读取0；外层一次Python检查解释器不混算成内部fake进程。旧43/63/72均未重跑、未叠加。

## 4. 剩余命令兼容性集中反馈

| 命令/门 | 已有静态或合同支持 | 仍需另批现场证据 |
|---|---|---|
| features | 真实220B离线回归，完整原响应门及精确token | 新批次真实响应、原客户端/资源返回 |
| context、DIRECTORY | 自有printf字段、实际UID/pwd先输出后比较；CRLF内存合同 | run-as实际UID10221、原pwd、权限与files非symlink，新目录独占成功 |
| ps | 一次UID选择及PID/PPID/UID/ARGS字段解析，原shell自身排除、旧cat/tee/sh/mksh线索停止 | OEM列/权限/语法及可见性；未知/不支持不得替换命令求通过；未见线索仍不能清旧UNKNOWN |
| 三历史stat | 只三个准确叶路径、无-L；原rc/输出保留，不将错误解释成ABSENT | OEM默认lstat语义及本次原返回；不追加内容hash或扫描来确认 |
| BEGIN/END | 精确nonce/UID/pwd/path/同正PID/256计数、完整双行；CRLF合同 | 原接收端真实执行、全字节输入及原返回 |
| 独立PROOF | 新命令角色/普通非symlink目标、stat256及SHA精确比对；CRLF合同 | 新设备文件实际内容与独立摘要 |

所查上游Toybox明确有-u选择以及UID/PID/PPID/ARGS字段，支持接口提案；这不建立与平板OEM实现的对应关系。[上游固定ps源码](https://android.googlesource.com/platform/external/toybox/+/08dc20a/toys/posix/ps.c)

其余remote_command与原T2仅新目录/nonce及文本换行差异；tester独立规范文本换行后比较一致。生产脚本及解析门未因猜测OEM格式被改宽。T2P在features就停止，因此不存在后续命令已经设备通过的历史证据；表中未知须在原准确合同下首次观察，不能以本次67条替代。

## 5. 新T3P准确范围及条件

新批次D1-E4A-T3P-TABLET-20261017；仅HA1Q6WXR、user0/com.videokit.app、期望UID10221及pwd /data/user/0/com.videokit.app。新目录files/e4_diag_T3P_TABLET_20261017_once，唯一payload256.bin，nonce E4T3P_TABLET_20261017_ONCE，新包外证据目录D1_E4A_T3P_EVIDENCE。沿用E4T2标记前缀只是协议名称，新身份严格由nonce/目录/批次区分，不重用T2P。

固定shell_v2与shell -T -e none、无legacy fallback。一次合成输入0..255，SHA40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880；无真实媒体参数。计划6metadata+1producer，上限20/1，每命令15秒及共同本机收尾2秒，日志1MiB、每原记录64KiB。stdout/stderr各16KiB计数门/4KiB前缀，超额最多额外一个16KiB块即拒绝；主机prehash+stream计划512B、独立设备hash256B，均非已发生用量。

旧历史只允许以下准确no-L stat，既有81,407B残件已经归档，不恢复改名：

```text
files/e4_fixtures/basic.mp4
files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep
files/e4_fixtures/.basic.E4AT1P_TABLET_20261017_once.part
```

执行仍须负责人另行正式派发，外seal/准确导入及新证据目录在开始前绑定。权限、功能、原输出、旧接收线索、上下文或标记/独立证明任一步不符合即保首因停止；不改期望、不加时、不补跑、不换路、不删产物。UNKNOWN保原解释器/Job/handle，只观察实际原归还；不以退出工具或未见进程清零旧远端未知。

不手机/模拟器/安装/Gradle/Binder/预算marker/MP4AVI或产品正常取消故障。合成成功也不自动媒体恢复或产品下一批。当前executionAuthorized=false、设备NOT_RUN；T1P远端退出码、SDK精确源码映射、旧81,407B截断和旧远端资源完全归还均UNKNOWN。D1未通过、M0未启动，原P0/历史FAIL及旧报告保持。
