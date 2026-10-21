# D1 E4A-OWNER 旧接收归属核查及定向收尾要求 V1.0

2026-10-17。T3P观察HA1Q6WXR PID7722/PPID7718/UID10221 tee files/e4_fixtures/basic.mp4，完整诊断未执行。现正式派tester有限核查与条件定向收尾；本条仅覆盖此前批次“不kill”在此准确旧测试receiver上的限制，不修改旧结论或授权其他kill。

只指定平板，用现有T3准确shell通道及原归还记录，新包外D1_E4A_OWNER_EVIDENCE。最多12次metadata命令、各15s/本机收尾2s/证据1MiB，无媒体内容读取/hash/传输。一次采集7722及其准确父7718的/proc身份stat启动ticks、status UID/状态、cmdline、cwd/exe链接、FD0/1/2及输出FD链接和fdinfo位置；FD枚举最多16项，只readlink/fdinfo元数据，不cat任何媒体/pipe或/proc fd内容。父仅准确二PID不递归。权限拒绝/身份变化据实停，不提权为root/绕过SELinux。

确认UID10221、cmdline精确tee原fixture、cwd本app目录、实际输出FD指向已归档basic.mp4.E4AN_PREP01_81407_a790f44f.keep或可证同原fixture inode，且不是产品编码/其他业务，才允许通过run-as同UID发送一次TERM给原7722。信号前同一远端控制命令复核原PID+启动ticks+UID+cmdline+输出FD身份；任项不符/未知不发信号。不能kill父进程/进程组/server/app/其他PID，不能KILL升级或反复TERM，不能全局force-stop。无须再问用户，该授权仅本项目自建遗留传输进程。

TERM后在同原控制handle最多2秒有界观察原身份是否结束；若仍存活/不可观察保UNKNOWN，不加时/升级。原/proc消失仅限原PID/启动identity结束；其FD地址空间不再持有的事实与文件内容/父进程资源分别写，不宣称全部历史owner清零。结束后一次准确UID快照可记录其他残留，发现也不新增kill。若原7722开始已缺失，仅记录原不再可见，不改判原截断原因。

禁止修改/删除/重命名媒体/残件、清cache或预算、手机模拟器、安装/Gradle/Binder/产品/256B诊断。定位与收尾不是重跑诊断或预置许可。交docs/tester/D1_E4A_OWNER_REPORT_V1.0.md，准确已证/未知、原命令/身份/信号实际返回/资源结果、无在途或原handle。完成主动报告，不自行下一批。D1未通过/M0未启动/旧FAIL保持。
