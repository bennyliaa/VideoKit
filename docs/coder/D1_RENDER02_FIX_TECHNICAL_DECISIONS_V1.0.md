# RENDER02 技术决定

2026-10-20；仅三项修复，主报告和 seal 为准。

1. 采用官方固定 Guava parent 的新来源证据，不把本机观察 hash 追认为旧批准。保留原始 HTTP/校验文件，新增 pin 明标待独立准入。恢复 metadata=true/strict，离线仓库明确描述类型，不用关闭校验或下载新版本解决构建。最终实际 module 解析路径与 Maven POM 对照分栏，不假称最终消费了未消费的 parent。
2. 观察器仅记录现有 Gradle 的 build operation，不改变依赖选择或校验。保留最终327项验证事件清单、192个描述原文与历史 pin 绑定；POM 声明边不当实际消费。负向测试只改独立 overlay 副本，报告准确 SHA mismatch，正式镜像和旧 candidate 不变。
3. drawBitmap 完成与清理 post 分开。原 unlock/post 完成之后才报告成功；没有 bitmap 就 false，cleanupPosts 单列。真实旧 bitmap/post 不丢，旧 epoch 和 `currentAfterPost=false` 保留。若原 canvas/API 抛错或未返，原 sticky unknown/原 owner 保管保持。
4. 手动入口由同包 instrumentation 启动非导出 Activity，先 surface 准备，再开启一次15秒 UI 点击窗；armed 不自动创建 session 或输出声音。只有 UI Listen 可 claim；初始 audible 在 start 前设置，拒绝“运行中静音会话”替代完整三秒。原四自动方法拒绝 manual 参数并维持静音。
5. 7 native、fixture、host、35锁定组件完全复用。使用成熟 Android Canvas/TextureView/AudioTrack 与既有 E13 source/owner，不新增产品框架、外部启动入口或执行权限。新 SBOM 仅将继承的嵌套 CPU JNI E6 标签校准为实际 C14，不改旧报告。

Android 运行、真实听音、完整 D1/P0 和许可判断仍依原门禁；本机受控测试及静态构建不予替代。
