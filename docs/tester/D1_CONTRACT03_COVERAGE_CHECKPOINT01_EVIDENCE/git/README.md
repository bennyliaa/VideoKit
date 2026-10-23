# CONTRACT03 离线 WIP 审阅检查点

本目录只保存本次准确白名单、排除依据和 Git 检查。测试报告/原证据冻结后才开始 Git 阶段。原98/开发484/A408/B744及新29项完整清单保持本地原样；Git清单不替换它们。

限定状态：A400/400已接受；B10组PASS、9/11故障精确命中，原两个失败保留；单字节source门替代覆盖已由负责人接受。本轮唯一补尝试因tester缺失BACKEND在许可生成前失败，物化内过期目标仍未覆盖；原资源已返回，无新资源UNKNOWN。实际SDK/设备0，D1未过/M0未启。草稿PR不构成产品验收。

候选及驱动来源限定为本次原冻结清单中的VideoKit自有代码、测试输入、报告、patch和小型证据元数据。引用AOSP等上游的URL/hash元数据保留，原始上游源文件/第三方分发及运行时不入本次提交，不增加再分发权利主张。排除媒体、ZIP、二进制、缓存、原始大采集流、秘密和local.properties。新PREAUTH浮动代码及工作单一并排除，不代表其实现通过；协调文档中已有的规划引用按原字节保留。

whitelist.json固定数据文件的相对路径、原字节SHA256、Git blob SHA1和来源。excluded.json逐文件记录检查范围内的排除理由，并列出从未进入候选集的根级排除规则。review-checks.json记录来源/大小/秘密/许可与基线检查。build_inventory.py和verify_stage.py为本次文件检查工具，不执行产品测试。

三个清单控制文件不对自身作循环hash。最终准确stage-plan.json另存本地，包含全部待stage文件（含上述控制文件）的hash；pathspec.nul和后续检查/交付回执也仅存本地，不进入自身清单。提交后最终SHA与草稿PR在同级交付报告和负责人消息中记录。

远端快照不包含所有本地历史二进制/运行时/依赖，不承诺独立复现。各报告保留原FAIL/NOT_RUN/UNKNOWN与本地路径，不重写原manifest或证据以迎合Git。

首版stage实际失败：Git for Windows无法打开aux保留名称目录，原件由Python/PowerShell仍可读取；失败后index为空。未关闭NTFS路径保护、未重命名或修改原件。最终使用whitelist-v2.json、excluded-v2.json、review-checks-v2.json和本地stage-plan-v2.json；v2按完整Windows保留名规则排除相关路径，并重新固定两个本次Git检查工具/说明的最终字节。首版清单与pathspec仅保留本地，不作为本次提交清单。
