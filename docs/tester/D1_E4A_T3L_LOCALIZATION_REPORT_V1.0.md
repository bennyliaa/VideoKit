# D1 E4A-T3L BEGIN后只读定位报告 V1.0

日期：2026-10-17 10:05。依据D1_E4A_T3L_TESTER_REQUIREMENTS_V1.0.md，仅HA1Q6WXR/UID10221/原pwd与准确合成目标。

**结论：只读定位完成；当前合成文件26B，摘要与预期输入前26B一致，具体截断层次仍UNKNOWN。当前UID/pwd、目录/目标角色及set-C兼容性正常；当前256计数守卫不成立。没有写入/重接收或信号，T3R原缺END和NOT_ADMITTED保持，不能用本次旧文件hash补成原诊断通过。**

## 1. 集中无写审查与范围

新包外目录 `docs/tester/D1_E4A_T3L_EVIDENCE` 保存两份准确实发脚本。一次本机集中静态范围及Git shell -n语法检查均PASS；核无mkdir、文件输出重定向、重接收或信号，UID/step处理只用shell内建。绑定脚本SHA：

| 脚本 | SHA-256 |
|---|---|
| read_guards.sh | b1dd044223c6693492c4e862d0f7a0678e8a615219f1aa3cd28ad2aa577c1acf |
| read_receiver.sh | 4a048565986e25a9bb7e6fff53afbfe7602939143c1b4e512cc89f7bdc77a77b |

实际2条metadata客户端命令，固定shell -T -e none及原T1强关闭pump；第一次逐项角色/选项、一次受限SHA和前后stat，第二次只尝试原PID16643。未修改冻结工具或现场，未查手机/模拟器/其他进程、媒体fixture或父目录内容。原实发脚本与本机审查文本相同。

## 2. 当前各原守卫表达式返回

本次原UID10221、pwd /data/user/0/com.videokit.app，两命令实际上下文一致。以下是**只读复核时**的表达式返回，不是未记录的T3R原执行瞬间返回：

| 表达式/范围 | 原rc | 解释 |
|---|---:|---|
| UID与pwd等值 | 各0 | 当前角色匹配 |
| files -d / -L | 0 / 1 | 目录，非symlink |
| 准确诊断目录 -d / -L | 0 / 1 | 目录，非symlink |
| 准确目标 -e / -L / -f | 0 / 1 / 0 | 存在、普通文件、非symlink |
| 当前原noclobber“目标不存在”守卫 | 1 | 文件现已存在；不能因此倒推接收前就存在或原失败发生在该门 |
| 当前stat数量等于256 | 1 | 当前size26，与预期256不符 |

准确路径为 `files/e4_diag_T3P_TABLET_20261017_once/payload256.bin`，沿T3R获准复用的内部T3P目录，不新增或重建目录。

无写子shell内set -C原rc0、flags含C、set -o原rc0且noclobber on。没有向任何文件重定向输出或重执行cat；该子作用域不改变外部现场。此证据不支持“当前set-C不受支持”的说法，但也不伪造T3R缺失的逐步骤回执。

## 3. 受限文件hash与变化检查

在确认普通非symlink、UID10221且size26在0..256B范围内后，才执行**一次**sha256sum。没有超界内容读取或第二次hash。

| 目标元数据 | hash前/后两次原stat，全部相同 |
|---|---|
| dev / inode | 64522 / 7123 |
| UID / mode | 10221 / 8180（普通文件） |
| size | 26B |
| mtime | 1792202151 |
| SHA-256（一次，rc0） | b858da80d8a57dc546905fd147612ebddd3c9188620405d058f9ee5ab1e6bc52 |

以上摘要与本机按既定`bytes(range(256))`计算的前26B（0x00..0x19）摘要一致；本机没有重新读取设备文件或真实媒体来比较。预期下一个字节索引26，值为0x1A；当前落盘边界与此位置一致。前后可用stat字段未见变化，故可以报告本次窗口中的26B前缀摘要；不将秒级元数据相同当作对任意历史并发修改的绝对证明。

## 4. 原接收PID的一次观察

仅一次尝试准确`/proc/16643/stat`，原rc1：

```text
cat: /proc/16643/stat: No such file or directory
```

后续status/cmdline/cwd/exe及最多4个FD链接全部跳过，实际FD链接调用0；没有重复缺失探测、父进程/递归或信号。只记准确PID在该次查询不可见，不据此清零全部旧远端owner；没有原启动ticks等更多生命周期证据。

## 5. 已证与未知原因分栏

| 已证事实 | 尚不能确认 |
|---|---|
| T3R主机曾完整提交256B；T3L当前新文件26B且等预期前缀 | 具体在哪个主机/ADB/设备接收层丢掉后续字节 |
| 首个未落盘预期字节为0x1A | 不能仅凭边界指定具体函数、文本模式或SDK实现 |
| 当前n=256比较会返回1，可与原exit1/无END现象相容 | 原T3R没有记录当时n及子步骤，不能把当前测试返回写成原执行回执 |
| 当前角色、普通文件及set-C检查正常 | 不能补造T3R的END/独立PROOF或把原NOT_ADMITTED改PASS |
| 当前合成文件的26B摘要一致 | 不能据此解释原MP4的81,407B问题、证明两者同因或验证真实媒体 |
| 原PID当前stat未见 | 不能认定全部历史远端资源已归还 |

这把定位重点收敛到合成输入的0x1A边界及实际传输路径；进一步指定层次仍需负责人另行安排静态或准确有限证据。本批不自动修代码、修改目录、改期望或再传payload。

## 6. 实际预算、资源与交接

metadata2/上限5；准确目标stat2次（前/后各1），SHA1次、合成内容逻辑读取26B/上限256；producer0、payload写入0、媒体内容/hash0、信号0。无mkdir、删除、改名、安装、Gradle、Binder、预算/产品方法或自动下一批。

两原客户端耗时0.453/0.188秒，stdout1550/198B，stderr均0，完整未截留；内部预期false或/proc错误的rc单独记录，未被set-e吞掉，不以外层exit0改写为每个子步骤成功。未达15秒/本机共同收尾2秒或证据1MiB；实际目录总量见review-summary.json。

所有原本机stdin/source/writer/drain/wait及线程均归还，retainedLocalOwners=0，无在途Job或保留handle。旧远端状态保持UNKNOWN_NOT_CLEARED。准确脚本、原两调用、逐step/选项/前后stat/SHA/proc原返回及audit/manifest均已保存；审计仅解析原字节。旧T3R报告SHA保持。

本次hash只能是新的只读定位证据，不能回填原T3R END、重标原诊断通过或授权媒体恢复。完整结果主动交负责人；D1未通过、M0未启动，P0/历史FAIL及旧报告保持。
