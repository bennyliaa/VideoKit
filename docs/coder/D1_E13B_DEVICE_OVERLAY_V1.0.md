# D1 E13B 设备计划覆盖说明 V1.0

日期：2026-10-18。METADATA_ONLY_REVIEW，不是派单。只将E13A的三metadata脚本/argv、INSTRUMENTATION记录语义、期待及pins替换成新release/metadata内容。基础E13A三APK/JAR、v17/sourcev15、ACTIVATION/ABI1、签名、六方法顺序、batch及scope草案不改；原E13A冻结不动。

优先使用本覆盖包的three-client-manifest/expected-baseline及M1/M2/M3 sh、argv JSON，禁止继续使用旧unsupported入口。每份一个现有受管直接adb.exe客户端，完整remote脚本在最后一个精确argv字符串中；无push脚本或新PC Java/Python wrapper。三个record/cap上界仍70/53512、18/27588、71/56360，每份≤65536B/原GENERAL55秒。原部署1+32、六entry6+六instrument6+metadata3=48；原文本1638400B+余458752B=2MiB保持。

ACTIVE或BLOCKED会在完整INSTRUMENTATION记录后停止当前客户端，M整体没有后续成功尾；不能把环境等待的部分M当完整预检通过。环境占用稍后有限复查仍需计账，不增加免费客户端/查询，不改预算。M1之前原controller占用/独占证据不明亦等待，他项目活动不得抢占。

只有静态复审通过、负责人真实设备scope明确绑定本overlay manifest/ZIP/seal和原E13A实际制品后，才能执行三份及后续六方法。现有长真机授权有效无需重问，但本批当前无设备、remote脚本、媒体、scope或once派发。

原214483/7R7S/0reserved、107218前缀/18control/34stat/ledger/inventory/产物/fence/oldCloseACKfalse保持。非零媒体只stat；本地复用的四份历史process raw只是文本，不是媒体payload。没有新输出/READY/R/S，没有APK/JAR/native构建或升版。
