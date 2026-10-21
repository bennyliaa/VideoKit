# VideoKit 国际化详细设计

版本：V1.0；日期：2026-10-21；状态：设计基线，未实现/未验收。文件位于现有技术需求文档同目录docs根目录。本文补齐界面国际化，不替代[播放子系统设计](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)及[播放数据模型](PLAYBACK_DATA_MODEL_V1.0.md)。

## 1. 范围、决定与状态

首轮正式界面语言：简体中文zh-Hans和英文en；英文为完整默认资源/最终回退。保留扩展语言、RTL、长文本、大字体及辅助功能机制。繁体中文、日语、韩语、阿拉伯语等没有自动成为产品交付语言；RTL测试不等阿语翻译已交付。

四类语言独立：界面UiLocale、字幕SubtitleLanguage、语音识别RecognitionLanguage、翻译TranslationLanguages。变更其中一个不得隐式改另三个。界面英文可以显示日语字幕、识别中文音轨并翻译为法语；该组合只在模型和轨道确实支持时可用，不承诺首轮模型覆盖这些语言。

国际化只重建显示层，不重建播放器、编辑工程或正在进行的导出。翻译内容引擎不是界面资源管理器，禁止运行时借llama.cpp/在线服务自动翻译按钮或错误。沿Flutter+自有VideoKit Theme，SkinKit待正式Flutter支持；Media3/平台播放器、whisper.cpp优先验证、llama.cpp可替换评估保持。主里程碑不变；ASR/翻译仍单列扩展。

项目继续PAUSED_WAITING_USER，D1未过/M0未启。本文及关联修改仅文档工作，不恢复开发测试/设备/自动跟进，所有新验收标PLANNED_NOT_RUN。

## 2. 分层与职责

| 层/组件 | 职责 | 不承担 |
| --- | --- | --- |
| App LocaleController | 读取偏好/系统候选、选择有效locale、切换事务及localeGeneration | 不发播放命令，不选择识别模型 |
| LanguageSettingsRepository | 原子保存4类独立设置、schema迁移/恢复 | 不存媒体凭据/完整字幕正文或模型权重 |
| AppLocalizations/ARB | 类型化消息、参数、复数、日期/数字显示 | 不提供媒体语言能力，不存业务数据 |
| Flutter delegates/Directionality | Material/Cupertino/通用组件、布局方向与语义 | 不镜像媒体帧/编辑坐标 |
| Presentation ErrorMapper | 稳定错误码+类型参数映射文案key | 不把原生异常直接显示给用户 |
| 原生Kit | 语言中立状态/轨道/错误/任务数据 | 不持有Flutter locale/翻译后的终态字符串 |
| Subtitle/ASR/Translation | 各自轨道/识别/目标语言策略与能力 | 不受界面语言切换隐式控制 |

独立原生宿主有自己的locale策略和资源，Kit只提供公共code/参数契约；可选原生UI adapter自行采用平台资源。Flutter资源为App文案权威，不要求把ARB强灌进所有原生组件。系统文件选择器、权限弹窗的语言由操作系统/其配置决定，App不能保证与应用内手选语言一致。

## 3. 四类语言的设置与默认值

| 设置域 | 设置项/默认 | 变更效果与回退 |
| --- | --- | --- |
| 界面 | UiLocalePreference(mode=SYSTEM默认或EXPLICIT,tag?) | 仅locale/方向/格式/文案变化；按第4节解析 |
| 字幕 | primary/secondary SubtitleSelection(mode=OFF/AUTO/TRACK,trackId?,preferredLanguages)；初始AUTO、优先语言列表为空 | AUTO沿当前后端默认/forced字幕规则与原设置，不从UiLocale自动造偏好；TRACK失效warning并按既有默认/关闭规则反馈，OFF不自动打开 |
| 识别 | enabled=false；languageMode=AUTO或EXPLICIT；languageTag? | 仅启用后运行；AUTO依模型真实检测能力，EXPLICIT仅可选模型支持语言；失败不偷偷改另一语言 |
| 翻译 | enabled=false；sourceMode=FROM_TRACK_OR_DETECT；targetLanguageTag=null；provider=LOCAL | 开启需显式选择有效目标语言+可用模型；未选显示需设置，不以UI语言偷偷填目标，不自动联网 |

字幕语言是轨道的内容元数据和用户偏好，不等轨道文件名/界面资源tag。媒体元数据unknown/und不等英文；识别AUTO是策略，不是语言tag。翻译源语言应保留来自轨道/用户/检测及可信度来源；冲突时提示选择或停任务，禁止将UI locale当音频语言。

全局偏好为默认，用户显式每会话覆盖只作用该会话；可保存媒体字幕选择的现有PlaybackSnapshot仍按媒体指纹/稳定轨道匹配，不把瞬态trackId跨文件复用。模型能力未知、下载缺失、语言不支持时可保存用户意图但effective状态明确UNAVAILABLE/待配置，不能产生假翻译。

## 4. 界面locale解析与确定性回退

使用BCP47风格的language/script/region规范化标识；持久层存zh-Hans/en等规范tag，Flutter端通过对应Locale字段适配，不把en_US直接当BCP47保存。校验长度/合法子标签并规范大小写，未识别的保留安全诊断，不自行猜测语言。

解析顺序：

1. EXPLICIT：只对用户请求tag做受支持解析；无匹配最终用en并记录EXPLICIT_UNSUPPORTED。仍保留requested，不能把回退en写成用户选择，亦不再读取系统偏好覆盖明确选择。
2. SYSTEM：按操作系统偏好列表顺序，逐项做支持解析，取第一个支持项。列表null/空或均不支持最终en。
3. 单个tag解析：先匹配支持资源完全项，再同language+兼容script的已支持项，再该语言明确默认；不得跨不兼容script。首轮英语任意区域映射en；zh-Hans/zh-CN/zh-SG/无script无region的zh映射zh-Hans；显式Hans优先于region。zh-Hant及未指定script的zh-TW/zh-HK/zh-MO不映射简体，跳至下一系统候选或最终en。其他zh区域未明确可兼容时视不支持，不擅自做简繁转换。
4. effectiveUiLocale必须属于资源manifest已启用的正式locale，不能因Flutter默认算法/系统delegates支持很多语言就对外宣称翻译已完成。使用显式localeListResolution策略并为输出设置supportedLocales，后续新增语言需更新manifest/矩阵。

| 输入 | 首轮结果 |
| --- | --- |
| 手选zh-Hans，系统en-US | zh-Hans |
| SYSTEM，[fr-FR,zh-CN,en-US] | zh-Hans |
| SYSTEM，[zh-Hant-TW,en-GB] | en |
| SYSTEM，[zh-SG] | zh-Hans |
| SYSTEM，[]或仅ja-JP | en |
| 手选已移除fr-FR，系统zh-CN | en，保留requested=fr-FR和原因 |

上表是VideoKit产品政策，不声称等同Flutter内建默认回退。发布语言新增前须复审其script/region规则；不借“语言相同”误用繁简资源。系统语言由平台通知更新，SYSTEM跟随，EXPLICIT不变；Android系统按App语言入口未来若接入，只通过同一LocaleController同步，禁止两个偏好权威循环写。M0至少应用内SYSTEM/EXPLICIT与系统locale观察，平台专用入口按对应阶段另验，不默认已经支持。

## 5. 运行时切换与偏好事务

设置页显示“跟随系统 / 简体中文 / English”，语言名以原生自称帮助用户找回；同时可附当前UI翻译名。选择操作不需要重启App。

切换流程：validate选择→分配switchRequestId/递增localeGeneration→准备完整资源和平台delegates→仅最新请求原子发布UiLocaleSnapshot→更新依赖Localizations的页面/弹窗/语义/格式→持久化偏好并反馈保存结果。资源未就绪保持上一完整快照，不出现半页中英；失败保留原effective，安全提示。快速连选latest-wins，旧异步结果不可写回或覆盖新偏好。

偏好写入串行/原子替换，写前后携revision，旧写即便物理迟返也不得成为最终持久版本。保存失败允许当前会话临时应用，但明确“未保存，重启可能恢复”，标persistenceStatus=FAILED，不能显示已保存。启动读取损坏偏好回SYSTEM并安全记录，不清空媒体工程或其他有效设置；未知schema major隔离读取并回安全默认，不覆盖原记录，待迁移处理。四类设置按域独立校验，坏一个不重置全部。

UI切换只增加localeGeneration，不改变sessionId/bindingGeneration/timelineEpoch，不seek/pause/rebind、不清字幕/模型缓存、不取消ASR或翻译、不改导出参数。路由、滚动位置、编辑选择和输入中草稿保持；弹窗/菜单/Tooltip/Semantics采用最新资源，不能只刷新设置页。通知/系统已发布消息可能需平台重新发布，实施前明确能力，不在文档冒已生效。

字幕语言变更由SubtitleCoordinator发轨道/偏好命令；识别语言变更只取消识别任务并增recognitionConfigRevision/task generation，翻译目标或provider变化只取消对应翻译并增translationConfigRevision。普通播放不中断；不为局部语言设置无故提升全局timelineEpoch。真正Seek/换媒体/换音轨仍遵播放设计的generation/epoch失效规则。所有取消保持原调用/缓冲实际归还后才释放预算。

## 6. ARB资源管理与文案规范

采用Flutter flutter_localizations、gen_l10n和intl的成熟机制；工程具体SDK/包版本及生成参数实施前固定，不照官方示例引入any/latest依赖。建议目录apps/videokit-app/lib/l10n/，app_en.arb作为template与完整回退，app_zh_Hans.arb简体，配l10n.yaml；只是规划，不在本次创建App源码。

key按功能稳定命名，如playbackPause、subtitleTrackUnknown、settingsLanguageFollowSystem、exportFailed。每key有英文基文、简中文、@metadata(description/placeholder type/样例/上下文)。禁止用整句或后端异常作key、禁止拼接句子/按英文语序拼碎片。ICU plural/select保留other，参数名与类型各语言一致；媒体显示名/路径是动态参数，不能当可执行格式字符串。富文本交互用类型化片段而非翻译任意HTML。

所有用户可见文本纳资源：按钮、菜单、空态/加载/禁用原因、Toast/对话框、权限引导、错误/警告、无障碍label/hint/value、快捷键说明、演示标识和模型设置。品牌/技术ID/用户文件名/许可证原文不机械翻译；许可页标题国际化但原许可证完整保留。模型下载/在线服务同意文案不能依未审机器翻译自动上线。

构建门：正式en/zh-Hans key集合完整、空白翻译0、重复JSON key0、placeholder名称/类型一致、ICU语法与other分支有效、生成未翻译报告为空。检查未使用/废弃key，删除需同步所有资源；生成代码不手改。硬编码检查允许品牌/样本/日志例外白名单并记录理由，不把所有字符串都误报。

消息回退：gen_l10n的具体继承行为需固定SDK验证，禁止假定支持任意运行时key链。本产品在资源构建时保证zh-Hans与en完整；有意未支持locale通过locale解析整体回退en。运行时未知错误码映射已有genericError，不向用户显示raw key/异常/空白。已知key缺失/损坏属于构建或加载失败，不能以静默英文替代绕过发布检查。无需另造动态下载语言包解析器；首轮资源离线随App发行，未来语言包另评审签名/回滚。

## 7. 文本、数字、日期与媒体语言

界面复数/数字/日历日期按effectiveUiLocale格式化；时区由宿主/系统现有策略，切换语言不能改时区或业务值。文件大小统一单位策略、同值跨语言只变格式；排序/搜索如需语言相关排序须显式测试，不能靠标签字符串更改媒体身份。

媒体时间轴/时长使用固定明确的HH:mm:ss（小时需要时显示）、LTR数字分隔显示；不把毫秒时长当日历DateTime，字幕源格式时间戳/PTS数值和导出内容不因UI语言改写。字幕语言名可本地化展示，持久化仍BCP47/轨道identity；未知为“未知语言”资源，不猜英文。

界面字体默认系统字体与合法回退，覆盖中英和当前媒体文本；字幕字体按内容语言/用户字幕样式选择，不从UI字体强推。缺字/组合字符/emoji/换行按grapheme处理，不能按字节截断。外文字体新增需许可与大小预算，不把字体打入Core。

## 8. RTL、双向文本和无障碍

布局用start/end和Directional对齐，文本方向依UI locale；首轮无RTL产品语言，测试build提供独立debug locale/delegate或Directionality入口，不污染正式supportedLocales。伪本地化资源同样仅测试产物，不能让用户误选未翻译语言。

镜像：导航返回/前进、页面对齐、抽屉/焦点逻辑按语义方向；播放/暂停、音量符号、媒体画面、缩放/遮罩坐标不自动镜像。播放进度时间轴、编辑时间轴和快退/快进组合保持时间增大向右的LTR媒体语义，使用局部Directionality与可访问描述，不因全App RTL倒转实际seek量。字幕文本依其自身语言/双向算法，不能用界面RTL强制整句反转。

文件名、路径、URL、媒体时间码、混合中英数字显示用方向隔离，避免双向控制符伪装来源；原数据不静默删改，诊断转义危险控制符。长文件名可省略但安全提示/保存目标/错误关键操作有完整可访问路径，不能把“覆盖”与“保存新文件”截到无法辨别。

手机/平板/横竖屏/分屏下，中英与伪扩展文本（目标至少原英文长度约1.5倍的测试样本）不溢出；允许自适应换行/滚动，不能靠缩字强塞。100/130/200%文字缩放，原48dp触摸/焦点/读屏要求保持。读屏label与视觉文案语义一致，无图标只有英文硬编码；locale切换后焦点不丢到背景，必要时只播报一次切换完成，不重复打断视频声音。

## 9. Kit错误、资源与隐私边界

Kit输出StructuredError(code,stage,typedArgs,sessionId/requestId等)语言中立；Presentation ErrorMapper使用已登记key与类型参数本地化。sdkDiagnostic与用户message分离；缓存错误对象，不缓存翻译后长句，切换语言重新映射。日志/机器判定稳定code不翻译，不能靠比较中文字符串走业务分支。

字幕/识别/翻译内容不进入ARB、不作为UI语言资源；截图/日志语料用授权或合成数据，字幕正文、模型提示、完整NAS路径/密钥不默认上传日志。界面资源切换完全离线；在线翻译默认关闭且不能因为语言不支持而自动启用，切换语言也不授网络权限。

## 10. 设置数据模型

详见[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)。四域requested/effective、来源、能力状态分离；ui localeGeneration只服务显示，识别/翻译config revision独立于播放epoch。global默认与session override有明确继承，保存用户语言意图和实际模型能力，不能用一个locale字段兼管四域。

## 11. 主里程碑映射（编号及退出条件不变）

| 原阶段 | 阶段内任务/证据 |
| --- | --- |
| M0 | M0-I18N01资源/locale/偏好基础，M0-I18N02完整Flutter UI中英/伪本地化/RTL/大字体与四域设置演示；演示扩展禁用/未实现明确标识 |
| M1–M3 | 播放/图片/多实例真实接回时验证语言切换不重绑/不丢状态；轨道显示与语言偏好、宿主本地化错误 |
| M4–M6 | 编辑/跟踪/导出文案、关键错误、输出安全提示和切换不中断任务 |
| M7 | 独立Kit稳定语言中立API，原生宿主自行本地化，无Flutter/ARB强依赖 |
| M8 | 全正式App中英资源/切换/RTL/无障碍/回归矩阵及最终资源门 |
| M9 | Apple/Windows各自系统locale/窗口/平台弹窗及资源集成验证，不由Android推断 |
| M10 | 语言清单、许可、资源覆盖/人工审校及验收证据归档 |

ASR/翻译语言实机/模型质量属于原EXT-ASR/EXT-TR单列扩展；M0只建类型/明确演示，不提前装模型，不新增D1退出要求。每批仍负责人选1–3主阶段说明范围，开发自测整包冻结后独立集中测试，子任务不是逐问题交测单位。暂停期间上述均不派发。

## 12. 验收矩阵

| ID | 场景/边界 | 合格证据与要求 |
| --- | --- | --- |
| I18N-01 | 新装/SYSTEM/空系统列表/多候选/显式未知 | 第4节真值表全符合，requested/effective/reason可核 |
| I18N-02 | zh-Hans/CN/SG、Hant/TW/HK、en区域 | script不误配，繁体不冒简体已支持，系统候选顺序正确 |
| I18N-03 | 中英运行切换/快速连选/弹窗/读屏 | 最新请求胜，页面同一localeGeneration，路径/输入草稿/焦点保留 |
| I18N-04 | SYSTEM系统变更与EXPLICIT不跟随 | 平台通知或可控Fake验证，双设置入口无写回循环 |
| I18N-05 | 重启/写失败/损坏/旧schema/未来major | 原子持久化，临时生效与失败明确，各域不互相重置 |
| I18N-06 | 四域交叉设置/轨道与模型不支持 | UI变更不改另三域；ASR/翻译关闭或未配置不假可用、不自动联网 |
| I18N-07 | 切换时播放/seek/编辑/导出/识别进行中 | 会话/媒体epoch未因UI变化改变，原任务不中断；扩展任务试验只在其已准入阶段 |
| I18N-08 | 资源键/重复/空译/ICU/参数/other/硬编码 | en/zh-Hans全部正式key完整、类型一致，生成/资源静态门通过，人工文案审校 |
| I18N-09 | 未知错误码/语言切换中的错误事件 | generic已本地化，原code/参数不变，不露raw异常/凭据/key |
| I18N-10 | 日期/数字/复数/时区/时长 | 格式正确，业务值/PTS/原字幕时间码不变，零/一/多/边界覆盖 |
| I18N-11 | RTL/混排路径/媒体时间轴/字幕 | 布局正确，时间轴LTR与字幕自身方向，媒体/遮罩不镜像，安全操作可辨 |
| I18N-12 | 中英/伪长文/100-130-200%字/手机平板 | 无裁关键文本/溢出，触摸区/键鼠焦点/读屏真实UI截图和检查 |
| I18N-13 | 离线启动/切换/模型缺失/网络负例 | UI无需联网，语言操作不触发下载、翻译服务或麦克风 |
| I18N-14 | 独立原生宿主与平台系统弹窗 | Kit无Flutter依赖，宿主可翻译同稳定码；系统弹窗语言边界明确 |
| I18N-15 | 发布资源清单/测试locale隔离 | 仅en/zh-Hans正式启用，伪locale/RTL入口不入发布设置，新增语言按相同门准入 |

所有当前结果PLANNED_NOT_RUN。M0允许Fake证明设置与显示状态，不代真实播放/模型验证；M8及对应真实阶段补运行证据。报告分静态、Fake、实际UI、实际媒体与未运行，不能用“编译成功/支持RTL”代矩阵通过。固定候选/版本/locale真值/截图和原状态前后对照，集中报告缺陷。

## 13. 资源工作流与新增语言

需求key/文案上下文→en模板+zh-Hans人工翻译→占位符/术语审校→资源生成与静态门→widget/Fake→实际UI/读屏/媒体回归→冻结候选/独立报告。开发和测试要求各保存，资源变更随受影响模块同批，不能为每条文案单独编译交接。

新增语言需明确范围/语言tag+script/翻译审校负责人/字体与许可/复数和方向/平台delegates/回退真值/完整矩阵及包大小；通过后才入supportedLocales。术语表覆盖播放/暂停/缓冲/字幕/识别/翻译/源不变/临时输出/保存等，禁止把READY翻译成业务“已保存成功”。法律/隐私文案单独审校，不能依自动翻译替代。

## 14. 技术参考与未决项

2026-10-21官方入口：[Flutter国际化](https://docs.flutter.dev/ui/internationalization)、[locale列表解析](https://api.flutter.dev/flutter/widgets/WidgetsApp/localeListResolutionCallback.html)、[Localizations与重建](https://api.flutter.dev/flutter/widgets/Localizations-class.html)。引用支持框架机制，产品回退、原子偏好和不重建媒体属于VideoKit自行定义的契约，不能冒为Flutter自动保证。

待实施前冻结：准确Flutter/intl版本及生成参数、偏好存储实现/迁移样本、资源完整key清单/术语、系统按App语言入口支持范围、各插件系统消息本地化能力、字幕与模型语言清单。首次数据schema发布前复核字段与C ABI映射。项目仍暂停，不因此修改已冻结D1候选、旧账本/FAIL/UNKNOWN或恢复自动跟进。
