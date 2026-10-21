# D1 E11 coder requirements V1.0

2026-10-18，用户最新明确继续推进开发，负责人正式派activation候选准备/实现/本机自检/一次必要离线构建。先落本需求及独立tester需求，不启用子代理。当前仅开发，旧暂停设备激活/播放限制仍在，恢复开发不等于安装激活许可。

基线为E10A冻结实现及docs/tester/D1_E10A_FINAL_READONLY_REVIEW_REPORT_V1.0.md（SHA a597bca5c392aaf142f1fa5e74ab4a1aa869fb3cdc367df5005af54e335feaff）。只读核实际M4f21f71a-bf66-4a44-a287-320f0ae25fde registry、独立终局DAG和来源，原head6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5/catalog27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7（5853B）。不改原registry/events/head，不重新SEAL。原入口若会写原证据或要求设备则不运行，提供独立只读export适配，新文件仅新E11目录。

新版本>14，采用现有ABI准确角色ACTIVATION（派单ACTIVATE的实现值），嵌入实际catalog/policy；关闭prepare可写迁移路由和旧test错pair入口，未知schema/错误catalog/head/未审或撤销release拒绝。APK不嵌自身hash，实际签名APK SHA在构建后独立release绑定，无新密钥/远端根。每host必须真实核当前guard/fence/完整合法账本前缀+settled后缀/无pending/自己原holder实际返回才grant，历史catalog不发liveproof；观察重复/失败撤销保持。

补受变更实际activation public入口/部署gate/source/ABI/错pair/错head/catalog/schema/release/重复观察等本机有限自检，不全量重跑旧套件/native。一次必要离线主双APK构建，复用7native/35依赖。完整四文档、实际导出来源/字段/pins、差异/原自检输入日志、构建签名双APK/JAR来源/SBOM、ZIP外seal/只读verify，集中主动报告负责人。

设备附录只拟未来同签名保数据14→activation、当前观察→MP4/AVI/能力/条件cancel准确顺序和本批两个normal receipt条件，不执行。0ADB/设备/媒体读写/新迁移/actor2/强停。原107218/三R三S/全部产物/oldCloseACKfalse、Framework/独立Kit/Flutter/严格六帧EOF1000us和全部许可P0保持；D1未过/M0未启/长期准入OPEN。
