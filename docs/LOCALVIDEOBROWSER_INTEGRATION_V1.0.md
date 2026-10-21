# LocalVideoBrowser 与 VideoKit 集成设计

版本：V1.0；日期：2026-10-05；状态：契约评审草案。

## 1. 适配结构

Browser feature → Browser playback/editor contract → adapter:videokit → 发布的 VideoKit API/AAR。BrowserMediaSource、MediaPlayHobby、业务 token 与 Kit DTO 的映射全部留在 adapter。LocalVideosBrowser 目录名和 LocalVideoBrowser 文档名不进入 Kit 类型名。

SMB/HTTPS 连接、认证及实际路径由 Browser resolver 持有；对 Kit 仅提供随机读取 factory。SDK 不直接访问 NAS、不完整下载远程视频、不保存凭据。Kit内部 sourceId 是会话/工程句柄身份；mediaToken 是宿主身份桥梁，均不解释 contentId。

## 2. 播放与资源租约流程

1. Browser 用 contentId 查最新 fileInstanceId 并取得只读租约。
2. adapter 创建 SourceDescriptor 和初始快照，创建会话并 bind。
3. Kit 为探测、播放或编辑分别打开句柄；Browser 租约追踪所有消费者。
4. 标签等物理事务进入 Browser 持久队列，Kit 仅渲染 pending。
5. 切换/退出/锁定释放相应资源，Kit 发 SourceReleased；Browser 确认整个租约引用计数归零。
6. Browser 执行队列中的移动/复制/改名，再更新索引。重新打开必须 resolver 提供新源；禁止沿过期路径重连。

同一媒体有多个槽位、探测和编辑任务时，释放一个播放会话不等于全部文件可移动。回调丢失后可查询 SDK 资源报告；进程死亡需由 Browser 清理 broker 句柄及恢复队列。

## 3. 状态与导航

MediaPlayHobby ↔ PlaybackSnapshot 完整往返，未知可选字段保留扩展数据；Browser 以 contentId+SINGLE 或 contentId+VIDEO_BOX(id) 保存，Kit 不理解 scope。图片的视频字段为空。保存失败不阻止 release。

右侧邻近媒体条由 Browser 查询前二/后二、分页和滚动。Kit 提供通用 overlay slot 与 controlsVisible；宿主列表和动作同步隐藏。图片滑动只产生导航请求，Browser 重新解析源和租约。请求含 generation，过期导航结果不得覆盖当前媒体。

HostAction渲染actionId/HostTextRef/icon/enabled/selected/pending/badge/priority/placement；原labelKey仅在adapter转换。回调只传 actionId、sessionId、mediaToken、requestId。标签与收藏失败轻量反馈，播放不停止；重复请求由宿主去重。

30% 观看计数由 Browser 根据有效观看区间和会话事件计算，每会话最多一次，不能仅检查 position/duration。

## 4. 多槽与锁定

PlaybackCoordinator 管理布局、批次、媒体顺序和快照；SDK 只返回会话资源与能力。默认手机 4、平板 9、视频硬上限 12。预算不足时 Browser 决定静态占位/减少活跃数/离屏暂停，其他槽继续。

音频命令采用 audioEpoch，由 Browser 唯一协调；声音槽移出后全静音。LOCKED 必须可同步隐藏画面并暂停/静音或释放，且不能被迟到恢复命令解除。后台服务的声明、启动与用户授权属于宿主，SDK 不擅自启动长期服务。

## 5. 编辑与输出事务

Browser 提供一个或多个只读源、allowedCapabilities、ExportPreset、临时 Sink；Kit 只写授权目标，返回 OutputToken、sourceTokens、editProjectId 与技术元数据。

markReady 后 Browser 再做存在/长度/可打开/权限/空间/文件版本验证及用户确认，再进入文件事务。新输出继承名称和业务身份，原件删除或 `_dump_日期` 改名以及配对管理均由 Browser 处理。Kit 不持有永久删除能力，不修改业务记录。

## 6. 可移除与故障回退

Browser 默认 CI 用 Fake 或已发布 artifact。构建配置可排除 adapter:videokit，基础 contract 保留 Media3/图片临时实现。AAR 直接静态引用不能靠 catch 解决缺失，需通过 build flavor/依赖注入装配实现，运行时加载失败回退另做故障验证。

SDK 初始化与重任务不能阻塞 Browser 启动/浏览。普通 SDK 异常可映射回退；进程内原生崩溃无法被普通异常捕获，按系统架构隔离 Spike 验证，不宣称天然安全。

## 7. 必须通过的契约

凭据与 NAS 地址不穿透；2GiB+ 范围读取；偏好往返与作用域隔离；HostAction 超时；邻近条同步；多媒体全部租约归零后物理事务；唯一音频；锁定优先；OutputSink 独占写入；源字节和路径不变；AAR 移除可构建；Fake/真实同套测试。关联原文第 26.7 节，不以示例宿主测试代替 Browser 适配测试。

## 8. 文本与输出补全契约

HostTextRef及host resolver按[统一契约](API_DATA_CONTRACT_V1.0.md)：namespace=HOST/KIT、typedArgs/version，宿主本地化自己的动作，语言变更只推textRevision不重发业务动作或媒体bind，超时/缺key安全占位并禁用不明操作。

输出按[生命周期与恢复](OUTPUT_LIFECYCLE_AND_RECOVERY_V1.0.md)提供验证只读租约/可查询幂等状态，未知原markReady不得再发第二物理调用。所有probe/playback/image/edit/tracking/asr消费者聚合真返后才允许宿主文件事务；文本翻译无源句柄时不伪添源消费者。数据schema/宿主权限与原COMMIT边界不变。HOST-01/02在M2/M7验收。
