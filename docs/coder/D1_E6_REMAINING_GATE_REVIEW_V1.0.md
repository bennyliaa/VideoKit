# D1 E6 剩余门复审 V1.0

2026-10-17。本机容器错误复现与修复有证据，实际Android产品验收仍待正式派发。

| 项 | 当前结果 | 仍需证据 |
|---|---|---|
| E5C-REG-F01/P1 | 旧容器5+1/末PTS偏41667µs复现，生产封装回放修复；旧实机原具体branch未补写 | E6实际MP4完整READY及精确新诊断，不能改旧FAIL |
| 严格六帧/末帧/多/少帧/EOF/PTS | 同生产C helper17项PASS | 实际JNI/FFmpeg解码与原输出全链 |
| 内容/映射、诊断/cause/cleanup | 原生产Java17项PASS | 实际真实源thumb/输出内容/完整诊断跨Binder报告 |
| Native/Maven | 仅CPU JNI包装库变、另六库及35坐标不变，原版本/白名单不扩；静态ELF/ZIP16KiB PASS | Android系统实际加载/验证，许可/安全既定审查 |
| 原N2/稳定budget | 结算和原R+S0/归档、53651消费/无pending保持 | 每新host真实最终观察，不靠旧报告放行；无新ABORT |
| G01 | E5C生产锁边界实证接受范围保持，相关核心不变 | 不将其扩称全恢复或产品通过，不重跑已消费根 |
| MP4→AVI→能力→条件cancel | 本批NOT_RUN | 新冻结候选独立复审、同签名保数据部署，准确顺序真实证据/本批两正常receipt |
| 全P0/正式Flutter/独立Kit/框架许可/旧signal | 原未完成/未通过保持 | 原既定产品链与全部验收 |
| D1/M0 | NOT_PASSED/NOT_STARTED | 不能把当前debug原型当正式交付完成 |

所有失败、诊断缺失、owner未实际返回或时限到均停止，不放宽frame/PTS/EOF/visual，不延时、不重跑、删产物、clear、清账、换UUID/账户或自动下一方法。新batch仍保留所有旧消费和失败输出；下一批任何真实损耗按原唯一R/S结算，不能为测试抹账。
