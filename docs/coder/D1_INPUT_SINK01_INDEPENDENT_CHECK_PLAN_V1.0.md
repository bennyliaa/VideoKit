# INPUT_SINK01 阶段B独立检查入口

2026-10-21；收到负责人完整冻结交测后执行。**本文件不授权设备，不生成scope/activation。** tester阶段A未读新浮动源码；阶段B须先核seal/ZIP/hash，再在外置目录复核。

先核主报告、最新需求补充/阶段A报告db797…、19项映射、源码与原bridge/registry差异、真实Media3 1.9.3 classpath/官方依赖材料/许可、严格锁和metadata、完整构建/自测失败历史、原候选1699文件未变。独立集中报告所有发现，不逐问题派修复。

## 只用现有JDK的原复核入口

冻结 [local_check.py](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/tools/local_check.py) 支持参数：

```text
--review-output D:\CodexProjects\VideoKit\docs\tester\D1_INPUT_SINK01_REVIEW_EVIDENCE\<独立新run>
```

由现有Python执行该脚本；它只读冻结源及随包真实Media3/Guava jars，使用既有JBR javac/java在指定外置目录编译/运行，保存原stdout/stderr/退出回执和source pins。目录须全新；普通coder local模式冻结后拒绝，review模式要求已有freeze，不写候选、不运行Gradle/SDK。生成的4B host fixture也在外置新run，不能复用旧输出。

实际Media3 API来自deps/*.jar，身份受原AAR/verification pin及官方module绑定。明确替身仅为宿主Provider/Sink和URI/errno/worker-rule平台port；禁止写同名Media3接口伪通过。JVM格式validator是受控host port，不因READY/controlled COMMIT字段为true登记实际媒体/业务成功。

## 整批重点

| 独立范围 | 准入/断言 |
|---|---|
| I01–I06 | 精确3+3+1和offset、unknown EOF、2GiB以上/64KiB、溢出/非法count、错误不带path/凭据/原cause；真实DataSpec显式length与越界reason |
| I07–I12 / A01 | 同DataSource重复read、同源两个consumer实际峰≤1（queue0）；两个不同源可并行、第三源拒绝；第一close不整体释放；旧结果不改callerbuffer，完整SourceReleased还需原线程返回；close/open新代、FAILED close不自动重试 |
| S01 / A02 | 底层controlled prefix7抛错时32仅attempt/reservation；SDK下界+UNKNOWN，buffer不rewind重发、首错sticky、禁止READY/COMMIT；已返回与未知分开 |
| S02–S04 | 写前预算/能力拒绝、successful partial、flush/close/reopen/摘要/验证失败；同原close一次，future完成但host线程tail未返不发布返回；真实4B host file不是容器 |
| S05 | 实际Android FD/fsync/MediaCodec/muxer/容器内容路径仅有编译及来源，运行NOT_RUN；不能用平台port替代或自行设备测试 |
| S06 | 关闭、reopen/hash、受控validator、READY、显式host COMMIT分别；abort幂等、不把UNKNOWN改成成功、不无条件退款 |
| F01 | 实际DataSource/Factory/DataSpec与Android/FragmentedMp4Muxer ABI，严格锁/metadata与完整实际消费清单；三个新使用依赖身份/许可是否准入 |

独立负向扩展应保留有限样本≤8MiB、host I/O块≤64KiB、per-source1/queue≤4、总源≤2、输出≤16MiB；用稀疏provider测long，不能分配巨大文件。超时只停止准入并保管同原任务/对象，不kill或换handle，不制造实际永久UNKNOWN。全程0 SDK现场/ADB/5037/设备/占用/旧scope查询；不跑Gradle/共享可变cache。

实际效果、设备FD/容器、RCE/权限危险链和宿主COMMIT仍需以后负责人准确派发；本机PASS不自动D1/M0。完整报告外置后统一回负责人。
