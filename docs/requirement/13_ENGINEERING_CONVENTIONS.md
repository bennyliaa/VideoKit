# 13 工程规范

版本：V1.1；日期：2026-11-06；对应原需求 §22、§23、§24、§25。

## 1. 仓库结构

```text
VideoKit/
├── build-logic/                 # 约定插件（Android library 配置、依赖规则检查、许可检查）
├── gradle/
│   ├── libs.versions.toml       # 全部依赖精确版本
│   ├── verification-metadata.xml
│   └── wrapper/
├── kit/
│   ├── videokit-api/
│   ├── videokit-core/
│   ├── videokit-playback/
│   ├── videokit-media3/
│   ├── videokit-image/
│   ├── videokit-ui-android/     # 原生宿主嵌入 Flutter UI 的桥接（add-to-app）
│   ├── videokit-timeline/
│   ├── videokit-effects/
│   ├── videokit-tracking/
│   ├── videokit-export/
│   └── videokit-testkit/
├── flutter/                     # Flutter 包工作区（Dart pub workspace）
│   ├── pubspec.yaml             # workspace 根，锁定 Flutter/Dart 版本
│   ├── videokit_api/
│   ├── videokit_ui/
│   ├── videokit_flutter/        # 插件；android/ 目录依赖 kit/ 原生模块
│   ├── videokit_fake/
│   └── videokit_example/        # Flutter 示例 App（含模拟 Browser 宿主）
├── sample-host/                 # 原生示例宿主 App（纯引擎 + add-to-app 嵌入示例）
├── third_party/
│   ├── MANIFEST.json            # 原生库来源与 hash
│   └── models/MODEL_MANIFEST.json
├── tools/                       # 演示数据生成器、评估脚本
├── docs/requirement/            # 本套文档
├── settings.gradle.kts
└── build.gradle.kts
```

- 早期验证代码 `app/`、`spikes/d1c14/` 已归档到 `D:\CodexProjects\VideoKit test-workspace\archive\d1-android-prototype`（只作参考）；新的聚焦验证代码放 `spikes/<S编号>/`。
- `test_media` 不放进仓库。

## 2. 构建

- Gradle Kotlin DSL；公共配置放在 `build-logic` 约定插件中，各模块 `build.gradle.kts` 只写差异。
- Android：`minSdk 31`；`compileSdk`/`targetSdk` 使用工程初始化时的最新稳定 SDK，并写入 Version Catalog；Java/Kotlin 目标 11。
- 依赖：只通过 Version Catalog 引用；`dependencyLocking` 锁定所有配置；`verification-metadata.xml` 校验；禁止动态版本与 Snapshot。
- 依赖规则检查：`videokit-api` 不得依赖 Android UI、Media3、AI 库；`videokit_ui` 只依赖 `videokit_api`（Dart 侧用 `dependency_validator` 或自定义检查）；违反时构建失败。
- 每个 library 模块提供 `consumer-rules.pro`（Consumer R8 规则）。
- 构建变体：`debug`（可开诊断日志、示例 App 演示场景）、`release`（无 Fake、无演示资源、无调试日志）。
- 不要并发运行多个 Gradle 构建共享同一缓存。

### 2.1 Flutter

- Flutter SDK：stable 3.47.7（Dart 3.13.5），本机路径 `D:\CodexProjects\flutter`；版本写入 `flutter/pubspec.yaml` 的 `environment`（`sdk` 与 `flutter` 约束）和 CI 配置，团队使用同一版本（可用 FVM 的 `.fvmrc` 固定）。
- Dart pub workspace 管理全部包；`pubspec.lock` 入库；依赖写精确版本。
- 静态检查：`flutter analyze`，规则集基于 `flutter_lints` 并开启严格模式（`strict-casts`、`strict-raw-types`）；`dart format` 统一格式。
- Pigeon 定义放在 `videokit_flutter/pigeons/`，生成的 Dart 与 Kotlin 代码入库，CI 检查生成结果与定义一致。
- 原生宿主嵌入：`videokit-ui-android` 使用 Flutter add-to-app 的 AAR 产物（`flutter build aar`），产物版本与 Kit AAR 同步。

## 3. 编码规范

- Kotlin 官方风格；ktlint 或 detekt 在 CI 中检查。
- 公共 API：所有公共类型与函数有 KDoc；使用 Kotlin `explicitApi()` 模式；用 Binary Compatibility Validator 生成 API dump，API 变化需在评审中确认版本级别。
- 协程：不使用 `GlobalScope`；会话拥有自己的 `CoroutineScope`，release 时取消；阻塞调用只在 IO 调度器。
- 主线程：禁止网络、解码、AI、编码与文件 I/O；Debug 构建开启 StrictMode 检查。
- 资源：所有句柄用 `use {}` 或显式 close；关闭幂等。
- 错误：内部异常在边界统一转为 `VideoKitStableError`，不把第三方异常抛给宿主。
- Dart：遵循 Effective Dart；公共 API 有 dartdoc；数据类型不可变；不在 build 方法中做 I/O；订阅在 `dispose` 中取消。
- UI：Flutter 组件不写颜色、尺寸、字符串字面量，全部读 Theme Token（ThemeExtension）与 ARB 本地化资源；所有可操作元素设置 `Semantics`。

### 3.1 国际化（机制从第一天建好；第一版语言：简体中文，英文后续整批加入）

| 规则 | 要求 |
| --- | --- |
| 文案来源 | Flutter 界面文字只来自 ARB；模板文件为 `app_zh.arb`，第一版只维护中文；CI 检查组件引用的 key 全部存在且无空值。key 用英文语义命名（如 `playerPlay`、`errorSourceDisconnected`）。已有的英文 ARB 草稿可保留但不验收 |
| 禁止硬编码 | 组件中不得出现用户可见的字符串字面量（自定义 lint 拦截，见 [14](14_M0_DETAILED_DESIGN.md) §11.3）；包括按钮、提示、读屏标签（`Semantics`）、错误文案 |
| 原生 Kit | 不含用户可见文案；只输出稳定错误码与参数，由 `videokit_ui` 按 Locale 解析。日志与诊断用英文，格式化代码与数字时用 `Locale.ROOT`，不受设备语言影响 |
| 拼接与复数 | 不用字符串拼接组句；带变量的句子用 ICU 占位符，数量用 ICU 复数/选择语法 |
| 格式化 | 时间、日期、数字、文件大小、时长按当前 Locale（`intl`）；时间码使用等宽数字 |
| 布局 | 预留文本伸缩：英文通常比中文长 30–50%，按钮与标签不固定宽度；方向无关写法（`EdgeInsetsDirectional`），为将来 RTL 预留 |
| 默认与回退 | 英文加入前，任何系统语言都显示中文（回退语言为中文）；英文加入后改为跟随系统语言、不支持时回退英文；宿主可指定语言并覆盖部分文案 |
| 验收 | 第一版：golden 与走查覆盖中文，并用伪本地化（自动把中文拉长约 40%）检查截断与换行，代替英文的布局检查 |
| 新增语言 | 英文在 VK-M6 后、VK-M7 前作为独立批次加入（见 [12](12_MILESTONES.md) §1.1）；之后按需增加。只新增 ARB 文件与对应 golden，不改组件代码 |

## 4. 日志与隐私（§22）

| 构建 | 规则 |
| --- | --- |
| Release | 无永久用户操作日志；错误通过脱敏回调交给宿主；不写本地日志文件 |
| Debug | 诊断日志可开关（默认关闭）；不记录凭据、完整路径、完整媒体名、媒体内容、人脸数据 |

- 日志统一经 `VideoKitLogger` 接口，宿主可替换；默认实现在 Release 为空实现。
- 媒体标识在日志中只用 mediaToken 的哈希前缀。
- 网络：Kit 不声明 `INTERNET` 权限（模型下载不在 V1.0 范围）；CI 检查合并后的 manifest。

## 5. 原生代码

- 原生代码（OpenCV 等）只在 tracking 模块；JNI 边界做长度、范围、空指针检查。
- 原生库与模型来源登记在 `third_party/`；构建脚本可复现。
- 对解析或处理不可信输入的原生代码进行模糊测试（损坏媒体、截断文件）。

## 6. 版本与分支

- 语义版本：`MAJOR.MINOR.PATCH`；所有 Kit artifact 同版本发布。
- 分支：`main` 为稳定分支；功能分支 `feature/<里程碑>-<主题>`；修复分支 `fix/<主题>`。
- 合并：通过 Pull Request，CI 全绿，至少一人评审。不强制推送 `main`。
- 提交信息：`<类型>(<模块>): <说明>`，类型如 feat、fix、docs、test、build、refactor。
- 发布：打 tag `vX.Y.Z`，附变更记录、SBOM、SHA-256。

## 7. 提交检查清单

提交前确认：

1. 不包含密钥、凭据、`local.properties`、私有路径。
2. 不包含 `test_media` 样本、大型二进制或构建产物（APK、AAR、`.so` 只在发布流程产生）。
3. 新增依赖已写入 Version Catalog、锁文件与校验文件，并通过许可检查。
4. 公共 API 变更已更新 API dump 与文档。
5. 相关测试已添加或更新并通过。

## 8. CI

| 阶段 | 内容 |
| --- | --- |
| 静态检查 | ktlint/detekt、`flutter analyze`、依赖规则、API dump 比对、Pigeon 生成一致性、许可扫描 |
| 构建 | 全部原生模块 debug + release；Flutter 包 `flutter analyze`；`videokit_example` 与 `sample-host` |
| 测试 | JVM 单元测试、Kotlin 契约测试（Fake）、Flutter widget 与 golden 测试、Dart 契约测试（Fake） |
| 产物 | AAR、Flutter 包、APK、SHA-256、SBOM |
| 设备测试 | 真机/云设备上的原生集成测试、Flutter `integration_test`、add-to-app 嵌入测试，按里程碑触发 |
