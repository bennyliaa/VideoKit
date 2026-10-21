# D1 E13B metadata-only coder正式需求 V1.0

日期：2026-10-18。来源：负责人正式派发，修复docs/tester/D1_E13A_ARCHITECTURE_REVIEW_REPORT_V1.0.md唯一E13A-F01/P1。旧E13A冻结270项保持，原P1/P2 CLOSED_STATIC_LOCAL结论不重开。

仅修M1/M2/M3 shell及嵌入argv的活动instrumentation证据入口，按Android12/AOSP及E11真实厂商raw采用支持的dumpsys activity processes完整有限段。必须识别完整头尾/活动列表/缺段/格式/诊断错误/截断/过限；空grep或exit0不能证明空闲，跨行/合法活动项不丢。有其他项目活动则环境等待，不抢占、不高频或额外查询。

在既有真实raw上做准确本机metadata解析正反证据：空闲、活动、未知、unsupported、截断；合成或变异必须标明来源，不冒真实设备活动。维持3个直接ADB客户端、每份64KiB/55秒、48操作/总2MiB原分配，不加wrapper/query；无法满足先BLOCKED报告。同步sh/argv/期待/manifest/pins/尺寸和严格只读verify。

新docs/coder/d1e13b元数据覆盖包复用基础E13A三APK/JAR精确字节，v17/sourcev15/signature/全部scope草案不变。无需构建APK/JAR/native/升版，不重跑绑定九组/source/旧套件、不下载SDK。完整交付/diff/原日志/ZIP外seal/只读verify后一次主动报告，tester集中核metadata语义及真实argv一致再由负责人派六方法。

当前无ADB/设备/remote脚本/媒体/实际scope/once，原214483/7R7S/0reserved、107218前缀/全部产物/P0/历史FAIL及D1未过/M0未启保持。
