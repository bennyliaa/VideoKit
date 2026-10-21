# D1 E4A-N 有限真机测试需求 V1.0

2026-10-17。E4A独立复审支持有条件交接，现正式授权tester独占设备执行本批，无需另问用户设备授权。只测冻结D1-20261017-E4A，freeze a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d；final目录app SHA e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f、test SHA 1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be。不改包、不Gradle，不操作旧C14结果。

## 现场和授权

仅一次设备清单查询，手机U4999DLBNRR89DOR与平板HA1Q6WXR分别只读确认身份/API31+/ARM64/连接授权/enabled/空间/既有安装签名及缓存。串行手机→平板，设备缺失记录环境阻断，不轮询或催连接；手机仍系统禁用不强启/卸载/换包名绕过，继续合格平板。不得操作其他设备。

符合条件时，先保留可读旧安装身份、缓存/输出/既有预算anchor/marker及证据，允许同包同签名保留数据安装final双APK。安装失败不卸载清数据重试。历史输出不删除凑空间。每设备稳定e4BudgetIdentity：手机 530758aa-9254-45ee-9142-771f4d176341；平板 730a73e1-50e1-4198-a515-047104f00e31。若已有anchor必须保留并报告，不能换UUID/目录/reset；未知marker直接阻断。本批batch手机D1-E4A-N-PHONE-20261017，平板D1-E4A-N-TABLET-20261017。

允许从授权test_media精确定位basic.mp4、subtitle.avi，核对冻结计划大小/SHA，预置各设备files/e4_fixtures对应路径各一次（已相同不重复复制）。原源只读不修改；各设备复制最多736803758B，前后完整hash读取单列实际量。路径或身份不匹配即阻断，不猜替代样本。设备空间不足保守停止。

## 唯一批次顺序

每合格设备精确选择方法，各一次，禁止整class：normalMp4SixRealFrames、normalAviSixRealFrames、capabilityDenialDoesNotOpenSource、binderRefusesBeforeBeginAndOversizeParcel。先正常两项，任一失败/UNKNOWN/PENDING或未证owner归还立即停止依赖encoder，保留原结果；只有可证明独立且不复用未知资源的拒绝探针可继续，报告理由。

正常原receipt落盘后，tester作为独立审核者核对同设备/冻结身份、六真实输入/样本/isolated EOF/PTS/画面及原Source/Sink/callback/CONTROL/许可实际归还，计算真实receipt SHA并记录准入。两正常成立且无pending、额度足够，才在同一整批执行cancelRejectsWrongEpochOversizeAndLateFrame一次，绑定该同设备receipt SHA；否则BLOCKED。此为负责人明确允许的条件调度，不接受仅格式字符串作为前置。取消固定原30s，不续时重跑。

本批不执行selfKill、nativeSegv、closeUnproven三quarantine，也不其他fault/压力测试。原8计划的后三项保持NOT_RUN另派，不以重建host洗未知许可。

## 限额与报告

沿冻结device_plan全部预算：CPU2/encoder1/queue2、四提案12s、正常60s、取消30s、单输出2MiB/累计4MiB且预留2MiB，128记录/256事件、ledger128KiB/其他metadata128KiB、每方法日志4MiB/设备整批32MiB。原预算消费只增不减，接近或不足即停止，所有失败产物/UNKNOWN强留。正常与取消等本批五项前后fixture全hash最多1475702128B/设备，另计源首次主机核验、预置和CPU请求；按实际方法记录，不读未执行方法。输出hash每产物最多6MiB。不得将数组估算当RSS，记录实际原PID/UID/实例、codec硬软、Image路径、资源/预算R/S/marker及峰值可得性。

交docs/tester/D1_E4A_N_DEVICE_TEST_REPORT_V1.0.md，手机/平板各五项PASS/FAIL/BLOCKED/NOT_RUN及原证据、receipt准入、资源/源hash/实际字节预算、无在途或未证清单。全部批次结束一次主动报告负责人；重大阻断可提前报告。不补跑求PASS，不自动派下一批。D1未通过/M0未启动，原P0/历史FAIL/C14待测保持。
