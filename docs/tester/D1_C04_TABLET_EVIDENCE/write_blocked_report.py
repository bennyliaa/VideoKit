import json, pathlib, re
base=pathlib.Path(__file__).resolve().parent
rows=[]
results=[]
for cls in ['C04DeviceTests','C04IsolatedDeviceTests']:
    text=(base/(cls+'.java')).read_text(encoding='utf-8')
    for method in re.findall(r'@Test\s+public\s+void\s+(\w+)\(',text):
        results.append(dict(candidateId='D1-20261005-C04',serial='HA1Q6WXR',className=cls,method=method,result='NOT_RUN',reason='WAITING_FOR_TABLET: target serial absent during bounded preflight'))
        rows.append('| '+cls+' | '+method+' | NOT_RUN | 平板未连接，设备前置阻断 |')
assert len(results)==23
(base/'entry-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
report='''# D1 C04 平板测试报告 V1.0

记录时间：2026-10-05 12:11～12:13，Asia/Shanghai。候选：D1-20261005-C04。需求：docs/milestones/D1_C04_TABLET_TESTER_REQUIREMENTS_V1.0.md。

状态：WAITING_FOR_TABLET。目标平板 HA1Q6WXR 未连接；有界身份检查返回 device not found，设备列表仅 emulator-5558。23 个设备入口全部 NOT_RUN，设备批次未开始。没有通过/失败数量可支持 C04 能力判断，D1 仍未通过，C04 仍 NOT_READY，不进入 M0。已请求用户重新连接平板；重连后继续本轮任务，不以旧 C03 结果代替。

## 已完成的离线门禁

冻结时点 2026-10-05T12:06:25.396182+08:00；独立运行只读冻结核验工具，5 个产物、97 个证据文件、ZIP 100 个源码文件及对应源码 hash 全部通过。源码 ZIP SHA256 37088cfc579db1f9ac7ad567d78d12ba1d6cd71fd21b5b4c9023c21fc4943402；freeze-summary SHA256 3085520db7458d3bf2da45df0361b2ede350b3b9b02ab1be84cc63a93bf9a472。

三份 APK 独立验证同签名，证书 SHA256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f，与本任务 C03 证书一致。实际已安装包身份尚未重新核验，不能仅凭历史身份直接更新。

| APK | SHA256 |
| --- | --- |
| app-debug.apk | f2d3a9473f27f5281a0214e04a821bca7a6fc579a5f9a1d9ffb50c539e62e937 |
| app-debug-androidTest.apk | c70362b629030f4a27e66a51a50e69b5e4834f7e54718d23682ab2b6969a8c13 |
| worker-debug.apk | ad1f9785218bb996c5b25c8f24eeb7e1080101c7690b0ec857f5a51a4d90fdc5 |

[冻结检查](D1_C04_TABLET_EVIDENCE/freeze-check.json)、[连接检查](D1_C04_TABLET_EVIDENCE/connection-preflight.txt)，三份签名日志和按 ZIP 原字节提取的测试源码见同证据目录。

## 更新与素材前置状态

未更新或安装任何包，未运行 Gradle，未操作手机或模拟器，未清数据或修改冻结件。由于平板不在线，当前包身份、C03 账本、恢复点、可用空间及源锁无法新采集。先前 C03 报告和证据目录保留，但不是更新前的新备份；重连后必须先保存包路径/身份和账本/恢复文件，再执行已授权保留数据更新。

冻结 DeviceFixtures.java 明确读取 files/d1_c04_fixtures，不能直接把 d1_c03_fixtures 当作当前输入。重连后可对旧私有副本重新核验，并在授权 App 私有范围生成 C04 副本、验证目标长度及 SHA，保留 C03 原目录；如需使用 C04 传输工具，只按实际已完成的设备与数据审查参数执行。当前没有复制素材，也没有把 C03 hash 当作新目标 hash。

## 23 入口覆盖

| 类 | 方法 | 结果 | 原因 |
| --- | --- | --- | --- |
'''+ '\n'.join(rows)+'''

[结构化入口状态](D1_C04_TABLET_EVIDENCE/entry-results.json)。上述入口尚未触发；NOT_RUN 是设备前置阻断，不代表产品断言失败。

## 重连后的执行顺序与判定

先 NORMAL broker、宿主正常导出及 companion 正常导出。只有对应正常能力通过才执行相关精确注入、实际 sample 后取消/死亡、第二槽存活和跨 owner 恢复；前置失败保留完整 cause/stack 与分阶段日志，并继续独立入口。普通 isolated codec API 拒绝必须到达正确身份/租约和实际 createEncoderByType 阶段，不能以 bind 失败冒充。

播放包括 MP4、AVI 无 SRT、AVI 有 SRT、MKV；取帧先 MP4 2 秒，再 AVI 10 秒及同时间点回退。自动静音、READY、轨道或 cue 数不能证明实际声音/字形/同步。只有非静音测试页明确准备好再请求用户观察；不更改全局音量。失败的锁/源排空未知仍 quarantine，不清理恢复材料。

## 集中剩余问题

没有本轮设备证据可关闭 PHONE-C02-01～04 或 TABLET-C03-01～04。C04 的 AVI、无声、导出1001、隔离 NORMAL/启动和取帧改善仍待实测；T01/T02、实际死亡恢复与完整隔离边界仍未验证。旧 C03 平板 MKV 人工“有声音，字幕正常”仅支持旧候选，手机无声仍待手机修复补测。没有生成新的 C04 cause/样本/输出/死亡/排空证据。

本次受连接前置阻断，等待指定平板重连；不无限轮询，不自动改用其他设备或候选。设备原数据未改动，故本轮没有新的播放需要停止或输出需要清理。
'''
(base.parent/'D1_C04_TABLET_TEST_REPORT_V1.0.md').write_text(report,encoding='utf-8')
print('Saved report and 23 NOT_RUN entries')
