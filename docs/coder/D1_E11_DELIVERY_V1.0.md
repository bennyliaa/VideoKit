# D1 E11 activation候选交付 V1.0

版本15/D1-E11-ACTIVATION，现有ABI准确role=ACTIVATION（派单ACTIVATE的实现值）。本批完成真实终局只读导出、候选实现/本机检查/一次必要离线双APK构建，状态 BUILT_NOT_DEPLOYED_PENDING_INDEPENDENT_REVIEW。不是安装激活/播放许可；0ADB/设备/真实媒体用例/新迁移/actor2/强停。未签发实际release或当前host grant，两个真实normal receipt未生成。原D1未过/M0未启/长期准入OPEN。

## 真实来源及导出

已接受终局报告原SHA a597bca5c392aaf142f1fa5e74ab4a1aa869fb3cdc367df5005af54e335feaff；688实际输入和217执行manifest行本地精确核验。冻结E10A原生产JAR的--approved-export只调用原registry读路径，输出新source-export/original-export；未调用recordActivationRelease/SEAL/deploy。原registry13文件前后清单/字节SHA一致。其副本仅存新accepted-registry-snapshot，原事件/head不改。原入口read使用READ_WRITE FileChannel但没有写/force/append调用，结论是内容/清单不变，不声称未更新文件系统访问时间。

实际catalog5853B/≤16384B，SHA27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7；head6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5。原kind catalog/version1，registrybbf71f7f-ab67-4bf8-af8f-731a38963e49，migration4f21f71a-bf66-4a44-a287-320f0ae25fde，environment DEVICE_HA1Q6WXR，actorCount1/disposition1 RETURN_VERIFIED_IN_TIME、termination1 ABSENT/actor2全部ABSENT。source-provenance列全部原字段/13文件映射及审查来源。旧补审manifest声明excludes:self但含0B self占位，本批以已接受报告的真实manifest SHA绑定并仅核其余实际行，不把占位当零字节文件验证，不修改旧manifest。

原trust.authorization b54e51203519f11891bcf44f466d019ac447bf48a8a862a698ebd27fc5ac62be、review e8fb76cfac6da5993c7c20638027529188be19e40fe8aae221671cb811ea99f0仅为原N2迁移DAG输入；补审报告a597单独绑定，本批未来安装审批又是独立阶段，不能用原写scope升权。原actor PID22086/UID10221/boot2/start17030020和prepare14 pair是历史事实，非当前现场。完整catalog原样内嵌；新增source HEAD常量与digest/environment共同核，导出器同步输出该字段并通过往返检查，不重造H_actor。

## 实现与安全边界

E9Phase从source-pinned digest/head/environment产生E9Catalog.Trusted；历史catalog只提供终局authority，不授实时proof。E9CurrentObservation仍核当前原guard/fence/13原metadata/完整合法ledger/无pending/精确三控制文件及自己的raw/dup/stream/目录/最后guard真实返回。重复或失败先撤销grant；已知失败且所有holder真返时移出ACTIVE可安全结束，但不授grant；UNKNOWN/在途仍保留ACTIVE。epoch并发检查保持。

新E11测试runner只接受单个受审MP4、AVI、能力拒绝或条件cancel；旧迁移/全类/死亡/隔离故障选项拒绝。每项仍通过原E4DeviceTests @Before当前观察。AVI须本scope MP4回执，能力/cancel须两份不同当前normal报告/输出task，绑定scope、candidate pair、version15/ACTIVATION/catalog/batch及READY/六帧EOF1000us/原owners返回。它只是选择/次序校验，不能认证外部报告来源或替代当前proof；外部受信tester/负责人必须实际核其原证据。无normal receipt可由开发或旧历史回执代填。

runner结束先撤销grant，原观察/会话/encoder slot/legacy原操作未返则不调用platform finish；actual Android finish未实测。旧PREPARE E9AndroidIdentity/事务入口仍因ACTIVATION在首个身份/写IO前拒绝，新host main也在配置读取/ADB之前拒PREPARE会话。

新host批准部署使用独立pinned release的deployActivationDetached，同一原部署gate核字节/source role/ABI/签名/UID/current pair/idle/严格升版/两条install-r一次，无需往原final registry加activation-release。未知或部分安装保守消费，不重试。SHA只绑定真正被批准的文件；没有新密钥/远端根/自选approved bool或网络撤销服务。role REVOKED/未知schema/错pin拒；正式执行者必须使用当时有效的真实批准，静态hash不能认证人类身份或自行证明未撤销。

## 检查与构建

12组定向最终映射，154断言；13次本机验证调用（初10组、增migration router、仅扩展部署组、增export roundtrip），没有机械重跑旧套件或native。使用实际生产模块及真实已接受catalog，UID/inode/目录fsync/设备安装为Windows平台替身；UNKNOWN原Java holder仍未返，测试native facsimile收尾不算close ACK或live grant。SDK桩检查实际新Gradle app公开入口、旧prepare pair拒绝及runtime失败撤销旧本机fixture grant，均无Android运行。runner结束钩子只做实际编译/静态及其所用lifetime方法验证，不冒称真机结束已证。

|组|断言|
|---|---:|
|PARSER|13|
|SELECTION|39|
|DEPLOYMENT|50|
|OBSERVE_SUCCESS|6|
|OBSERVE_REPEAT|8|
|OBSERVE_LEGAL_SUFFIX|6|
|OBSERVE_KNOWN_FAILURE|6|
|OBSERVE_UNKNOWN|5|
|OBSERVE_OVERLAP|7|
|OBSERVE_REVOKE|5|
|ROUTER|2|
|EXPORT_ROUNDTRIP|7|

一次必要main-001离线构建成功，166输入SHA `c136acbd8730cdbb545c960e55234f66bc5d5310fcaca6cb850c669756c8de9e`；无repair/下载/native重编。后补exporter HEAD兼容仅PC工具编译/JAR重封，没有第二次APK构建。原签名5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；7native/35Maven坐标/锁不变，FFmpeg8.0.3/Media3 1.9.3及许可P0不变。

|制品|字节|SHA256|
|---|---:|---|
|app-debug|10659394|`2f323c16e896b0535e80cccce05bbcf3051224f0add279a51392312083e89f48`|
|androidTest|2751249|`e644dce77be6ccb0e7f99d82f2479fc92238aad682bb022bb95835fc015d0bfb`|
|host JAR|275076|`d9db55a43ad690267078f7feec5afba41224db1a4e8afd9bd57a9c20a05d2081`|

host JAR 160生产classes、无测试类，取最终activation-004已测编译；此前生产class差异仅明确host router与exporter，原快照/JAR及源码留存。APK DEX已核完整内嵌Base64和实际catalog字节，未嵌自身APK hash；构建后actual SHA进入独立candidate-binding和release模板，sourceReview/部署派单/approvedRelease/live observation/两normal receipt均null或占位，不能直接交生产CLI。工具早期仅因独立输入表字段名准备失败，未启动原Java；更正后原冻结export分支执行一次。原日志/输入/差异保留。

完整源ZIP及ZIP外seal/只读verify由包外记录给出；E10A及所有原证据冻结不改。原107218/三R三S/0B/S0/53651/53567及oldCloseACKfalse保持；独立Kit/Flutter/原框架严格六帧EOF1000us/全部许可P0不变。本交付不关闭D1或启动M0。
