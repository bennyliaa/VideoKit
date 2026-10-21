# D1 E13A tester正式需求 V1.0

日期：2026-10-18。来源：负责人正式修复派发。独立整包复审P1/P2，不以E13文件完整性PASS当设备准入。

P1逐原connection核bind进入/实际正常false、true、SecurityException/其他异常返回，必须同原connection一次必要unbind/forget；回调在途与unbind在途/异常独立计账，只有实际归还才resourcesReturned。核生产SenderService与E13PermissionProbe共同实际接线，直接生产平台替身证据分界；未知强保同原owner，不重bind/重复unbind/换对象。普通UID运行仍NOT_RUN，无endpoint不声称内部onTransact。

P2核默认verify/help纯读，无先写文件/证据/复制/构建；写封装必须显式子命令。独立核旧E13 seal/367项及历史原误调用后字节不变，不作为功能FAIL。新候选v17/source接受v15；审所有source/签名制品/hostJAR来源/一次主构建与必要repair留痕/SBOM/ZIP外seal及真实只读verify。

M1/M2/M3采用既有34固定stat/18control pins，精确新pair/fixture/字段及argv脚本，三个直接受管ADB客户端，不加额外Java wrapper或查询。48操作/2MiB及source原预算不增；不足先BLOCKED报告。当前无设备/媒体/实际scope/once，新完整冻结静态复审后再由负责人正式派实测。旧214483/7R7S/0reserved及107218前缀、产物/P0/历史FAIL与UNKNOWN保持，D1 NOT_PASSED/M0 NOT_STARTED。
