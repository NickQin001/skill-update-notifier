# Skill 更新检查

[English](README.md) | 简体中文

先了解原来源的变化，再决定是否更新你的 AI Skill。

**当前发布：[v0.1.1 手动只读试用版](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.1.1)。** 比较已安装 Skill 与确认的公开 GitHub 或 SkillHub 来源，查看本地差异，辅助决定是否更新。

本版只检查和提供建议，不安装更新、不定时提醒、不采集使用统计，也不保存提醒偏好。

## 能做什么

- 按明确的公开 GitHub 仓库及子目录，或 SkillHub slug，检查指定 Skill。
- 有可信历史基线时，区分上游变化与本地差异。
- 输出 Markdown 或 JSON 报告，展示文件变化、来源信息和证据缺口。
- 检查 SkillHub 公开版本记录和文件哈希，可选读取经核验的公开文本差异及发布说明。
- 保留全部本地文件，包括上游不存在的自定义文件。

本地不同不等于上游发布了新版。来源未知、缺少基线或请求失败时，会明确报告。

## 安装

1. 下载 [v0.1.1 发布页](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.1.1)中的 GitHub ZIP，或克隆本仓库。
2. 将完整的 `skill-update-notifier/` 目录放入你的 AI 工具支持的 Skill 目录，保留 `scripts/` 和 `references/`。
3. 让 AI 使用这个 Skill，或独立运行下方 CLI。

先核对宿主实际使用的 Skill 目录。已有同名安装时，先备份并审阅差异再决定替换。仓库根目录还包含测试和说明，不应将整个仓库当作一个 Skill 覆盖安装。

**依赖：** Python 3.10+、读取选定本地目录及访问公开来源的权限；GitHub 检查另需 Git，SkillHub 检查不需要 Git。没有第三方 Python 运行依赖。

验证范围见 [VALIDATION.md](VALIDATION.md)。实测环境为 Windows / Python 3.13；其他操作系统和各 AI 工具内的自动发现仍待验证。

## 向 AI 提问

> 使用 skill-update-notifier，检查我指定的 Skill 有没有值得更新的上游变化。先核对安装目录和原来源，说明本地差异，不要直接更新文件。

AI 可以逐项检查多个 Skill，再汇总为表格。包内指令和 CLI 自然语言信息目前主要为中文；英文首页不代表新增了 CLI 语言选项。需要英文总结时，可直接要求 AI 用英文解释结果。

## 独立运行 CLI

在 `skill-update-notifier/` 目录内运行。所有尖括号占位符必须替换为已核验的值；`--source-confirmed` 表示你已确认来源关系，不会替你发现或证明安装来源。

GitHub：

```text
python scripts/check_updates.py "<LOCAL_SKILL_DIRECTORY>" --repo "<PUBLIC_GITHUB_HTTPS_REPOSITORY>" --subdir "<VERIFIED_SKILL_SUBDIRECTORY>" --source-confirmed --format markdown
```

Skill 位于仓库根目录时使用 `--subdir .`。未指定 `--ref` 时解析此次仓库默认 `HEAD`。

SkillHub：

```text
python scripts/check_updates.py "<LOCAL_SKILL_DIRECTORY>" --skillhub-slug "<VERIFIED_SKILLHUB_SLUG>" --source-confirmed --format markdown
```

没有历史基线时可以比较文件，但不能证明相对先前快照出现了新版本。有已核验来源快照时，GitHub 追加 `--baseline <VERIFIED_40_CHARACTER_COMMIT_SHA> --baseline-kind observed`；SkillHub 追加 `--baseline-version "<VERIFIED_SKILLHUB_VERSION>" --baseline-kind observed`。只有安装记录确实对应基线时才使用 `installed`。

用户明确要求与来源关系未确认的其他项目比较时，用 `--compare-only` 替换 `--source-confirmed`。结构化结果使用 `--format json`。完整参数见 [usage.md](skill-update-notifier/references/usage.md)。

## 怎样解读结果

| 状态 | 含义 |
| --- | --- |
| `upstream_changed` | 已确认来源相对可信基线有后续变化；更新前仍需审阅本地差异。 |
| `matches_target` | 本地内容与选定来源快照一致。 |
| `local_difference_only` | 来源 Skill 相对基线未变，只有本地差异。 |
| `baseline_unknown` | 有差异，但缺少可信历史基线。 |
| `source_unknown` / `comparison_only` | 原来源未确认，或只是与另一个项目作比较。 |
| `history_diverged` | 现有历史无法确认普通的向前更新。 |
| `check_failed` | 检查未完成，不能解释为没有更新。 |

提交数不换算为落后版本数。GitHub UTF-8 文本比较忽略 BOM 与换行差异；SkillHub 比较原始字节 SHA256，因此包含这些差异。发布说明是作者提供的信息，不代表改进效果已获独立验证。

## 隐私与反馈

检查器只读选定的本地 Skill，不上传其正文、不执行下载的来源代码。网络访问限定为指定的公开 GitHub 来源或 SkillHub 公开 API；来源歧义、清单不一致和请求失败均明确报告，不猜测映射。

在仓库根目录运行隔离测试：

```text
python -m unittest discover -s tests -v
```

可通过 [Issues](https://github.com/NickQin001/skill-update-notifier/issues)反馈：检查是否帮助你决定更新或保留，以及理由。附上脱敏后的命令或请求与相关结果；不提交凭证、私人路径或完整私有 Skill 内容。

许可：[MIT](skill-update-notifier/LICENSE)。分发包范围：[PUBLISHING.zh-CN.md](PUBLISHING.zh-CN.md)。
