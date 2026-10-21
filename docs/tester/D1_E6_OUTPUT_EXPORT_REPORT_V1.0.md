# D1 E6 失败输出只读导出报告 V1.0

2026-10-17；tester。依据 `docs/milestones/D1_E6_OUTPUT_EXPORT_TESTER_REQUIREMENTS_V1.0.md`，仅原平板 HA1Q6WXR/UID10221，一次精确失败产物导出。

**结论：PASS。** 53651B 二进制导出完整，独立本机 SHA 与原生产记录完全一致，设备前后文件身份保持，可交开发只读分析。

| 项目 | 实际证据 |
| --- | --- |
| 设备原路径 | files/e4a_outputs/0ee15550-8952-4639-91ac-83ab9d14d36c.mp4 |
| 原/后 stat | dev64522、inode20174、53651B、UID10221、mode8180、mtime1792225287，前后相同，普通非链接文件 |
| 导出文件 | [failed-output-53651.mp4](/D:/CodexProjects/VideoKit/docs/tester/D1_E6_OUTPUT_EVIDENCE/failed-output-53651.mp4) |
| 本机长度 | 53651B，CREATE_NEW 保存，无转码或文本解码 |
| SHA256 | 20ad48067b3293aa9e6b8f3eacc7543e29edcda8ab19c15cbe438d55c995b6dd |
| 实际通道 | exec-out → run-as com.videokit.app → cat 准确原路径 |
| 原客户端 | 前 stat0.141s、导出0.078s、后 stat0.125s，全部 exit0/实际 wait 返回，stdout/stderr/本机文件真实关闭，无在途或 handle |

本次2次 metadata（上限3），内容导出1次、stdout cap53652B，实际53651B；各次低于15s，本机独立 hash低于2s，全部stderr为空、无截断/溢出/超时。设备输出读取仅该失败产物53651B，metadata stdout共114B，合计原始stdout53765B，低于1MiB。本机原文件 flush/fsync/close 完成后独立读取核长度/SHA，并核后stat一致，没有补拉或备用通道。

没有读取 test_media/预置 fixture/旧归档/原 N2 的0B输出，没有修改设备文件或原账本，没有产品/观察/ABORT/安装/Gradle/信号/手机操作。原账本未在本次另外读取/hash；本次三条设备命令均只读，未以导出结果改写原READY或旧FAIL。

E5C-REG-F01仍为P1，正常MP4回归仍FAIL，导出成功不代表内容验证或解码成功；D1 NOT_PASSED、M0 NOT_STARTED。未运行本机解码器或开展额外媒体分析，后续开发离线分析应按E6需求独立记录工具及证据范围。

证据：[export-independent-review.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E6_OUTPUT_EVIDENCE/export-independent-review.json)、[host-binary-identity.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E6_OUTPUT_EVIDENCE/host-binary-identity.json)、三条原调用attempt/receipt。报告及已核文件路径主动发负责人，由负责人转开发；随后等待完整E6冻结静态复审，无后续设备任务。
