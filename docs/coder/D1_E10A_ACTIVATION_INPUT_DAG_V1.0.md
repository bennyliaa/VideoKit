# D1 E10A 后续activation输入DAG V1.0

本批不导出真实H_actor/策略、不建activation、不执行安装或grant。这里只给出已存在生产工具的可复用输入关系，避免随机token或hash循环。

依赖顺序：

1. 真实负责人终局迁移scope原字节 → authorization SHA；接受的E10A审查原SHA → preparePlan.sourceReview/config.review。
2. scope SHA + 固定descriptor + 实际新registry/migration + E9B固定APK SHA → canonical preparePlan SHA → packed plan/config SHA。配置只引用已经存在的输入，scope不反向包含config SHA。执行者在正式派单授权的模板内一次生成/归档这些文件及独立input-index，不生成随机token、不另起授权框架。
3. 新actor实际采样 → 外部BOUND(reserve actor hash/plan SHA) → 设备intent/payload/commit → 原COMMIT return + 独立normalfinish → 实际final event head → catalog(H_actor) → checkpoint → final seal。最终checkpoint/seal不反写旧events，避免哈希环。
4. 原写批资源全部终局且独立final审查通过后，负责人另行发activation源准备/构建scope；可信activationTrust只引用真实plan/authority/review/registryPath/已确认head。现有E9HostActivationSession --approved-export <真实activationTrust> <配置SHA> <新输出目录>，经原监督者和finalCatalog门导出E9BuildPolicy.java+final.acceptance.json。导出不要求尚未存在的activation APK SHA；没有最终catalog时不能先导出假placeholder构建。
5. 后续新候选复制E10A已冻结修复后source/native/dependency配置，不修改E9B原目录，只替换经过审核的BuildPolicy生成源，标ROLE=ACTIVATION/真实CATALOG_BASE64及SHA/SOURCE_ENVIRONMENT=DEVICE_HA1Q6WXR/GATE_ABI1；新版本必须>14。保留已核独立Kit/Flutter/严格6帧EOF1000us及所有许可门。记录精确source/native继承、35坐标7库不变、当前最终输入snapshot；在新的正式构建派单下才一次必要离线双APK构建+签名/角色/ABI/行为门审计。这个阶段的版本/Hash/兼容pair目前未知，不填写假值。
6. 新activation APK及test实际构建审查后才生成activationRelease（head/catalog/实际app/test/signer/ACTIVATION/abi1/version>14/sourceReview/environment），CREATE_NEW登记到原final registry。release不进入catalog的源head链，catalog不要求这些未来APK SHA，所以无循环。原HostActivationSession --approved-deploy <activationTrust> <pin> <release> <pin> <app> <test> 仅在新部署派单授权时使用；它在记录release前已持有原Store/监督者，未知安装不重试。当前不填release、不调用CLI。
7. 真正部署前确认全部登记actor已终局且无未知参与者；固定双APK install-r精确pair门、UID/签名/数据保留及安装后实测，禁-d/卸载clear/以安装杀未知actor。旧prepare test面对activation app role拒绝迁移入口；新activation runner也不能开COMMIT写。
8. 后续每个新host使用受信内嵌catalog并完成实际当前原guard/fence、全部intent/payload/commit、档案/完整ledger/无pending和本host原资源返回观察，才可能该host grant；不能由catalog年龄、某个磁盘commit或上次host grant代替当前门。缺/旧scope/错actor/未知均拒绝。完整catalog来自真实终局不是“已获产品许可”。

E10A复用本批version14 PREPARE/JAR进行计划；新候选已按共享输入变化完成一次必要离线构建，未安装；上述未来构建说明不是一次新构建授权，不复制签名密钥进包，FFmpeg许可P0及Framework发布/独立Kit/Flutter门没有因SBOM无差异而解除。


本批新增取消出口不生成final catalog、不授actor2资格；P2拒绝保持原归档R0供ACK。后续activation release版本必须严格高于本批PREPARE14，原E10 BLOCKED报告不可填为sourceReview；仅未来真正接受的E10A及真实终局独立审定可进入授权DAG。当前phase/grant/许可门未开。
