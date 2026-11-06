# Skill 更新检查

[English](README.md) | 简体中文

先看已确认的公开来源有没有变化，再自己决定要不要更新。

**当前版本：0.2.1（用时检查）。** 检查方式与 0.2.0 相同。预发布见 [v0.2.1](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.1)，标签指向 `d41023de274b5a84938de3337ec63e56a70669c0`。附件为 `skill-update-notifier-0.2.1-github.zip`、`skill-update-notifier-0.2.1-skillhub.zip` 和 `SHA256SUMS.txt`。上一份预发布仍是 [v0.2.0](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.0)。更早的 [v0.1.1 预发布](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.1.1) 仍保留。

你明确点名某个 Skill，或要求按该 Skill 工作时，就在这次使用中检查这一个 Skill。用时检查是文档约定，不是平台钩子。可选的每日 Routine 只作补充，不能代替用时检查。本版仍不自动安装、不覆盖已有安装、不采集使用统计，也不保存提醒偏好。

## 能做什么

- 用时只检查你点名的 Skill，不扫描整个库。
- 默认只查已确认的公开 GitHub 仓库及子目录，或 SkillHub slug。用时检查和 Routine 都不读本机，除非你在本次会话明确允许比较本地安装。
- 只有 Skill 正文、已知安装记录，或你本轮给出的原来源 URL / SkillHub slug，才与上游比较。否则报告「来源未确认，跳过版本判断」，不猜测同名仓库。
- 未读取本地时，不声称「本地已是最新」。
- 先完成你点名的主要任务。仅在有更新、来源未确认或未与本地比较时附一句短建议；没有这些情况则不附加。
- 你允许本地比较之后：有可信历史基线时区分上游变化与本地差异，并输出 Markdown 或 JSON 报告。
- 检查 SkillHub 公开版本记录和文件哈希，可选读取经核验的公开文本差异及发布说明。
- 保留全部本地文件，包括上游不存在的自定义文件。不代为安装，不覆盖。

本地不同不等于上游发布了新版。来源未知、缺少基线或请求失败时，会明确报告。可选 Routine 只覆盖用户库中来源已确认的 Skill，排除 Cursor 托管的 Skill；没有变化则保持安静，并同样默认不读本机。

## 安装

1. 克隆本仓库，或从 [v0.2.1 预发布](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.1) 下载附件。该标签指向 `d41023de274b5a84938de3337ec63e56a70669c0`。
2. 将完整的 `skill-update-notifier/` 目录放入你的 AI 工具支持的 Skill 目录，保留 `scripts/` 和 `references/`。安装不需要钩子。`SKILL.md` 附录 A 里的 Claude Code 示例是可选的。
3. 让 AI 按该 Skill 工作，或在你想比较本机文件时独立运行下方 CLI。

先核对宿主实际使用的 Skill 目录。已有同名安装时，先备份并审阅差异再决定替换。仓库根目录还包含测试和说明，不应将整个仓库当作一个 Skill 覆盖安装。

**依赖：** CLI 需要 Python 3.10+，以及访问已确认公开来源的网络；GitHub 检查另需 Git，SkillHub 检查不需要 Git。没有第三方 Python 运行依赖。CLI 会读取你传入的本地目录，只在本次允许比较本地时运行。默认的用时检查不运行 CLI。

验证范围见 [VALIDATION.md](VALIDATION.md)。实测环境为 Windows / Python 3.13；其他操作系统和各 AI 工具内的自动发现仍待验证。

## 向 AI 提问

> 先完成我点名的这个 Skill 要做的事。然后只检查这一个 Skill 的公开来源。不要读本机，不要安装或覆盖，也不要说本地已是最新。来源不清楚就写来源未确认，并跳过版本判断。

只有你点了多个 Skill 时才逐项检查那几个，仍然不扫描库里的其他 Skill。包内指令和 CLI 自然语言信息目前主要为中文。需要英文总结时，可直接要求 AI 用英文解释结果。

## 独立运行 CLI

只在本次会话允许读取本地 Skill 时，才在 `skill-update-notifier/` 目录内运行。所有尖括号占位符必须替换为已核验的值；`--source-confirmed` 表示你已确认来源关系，不会替你发现或证明安装来源。来源未确认时，不要把同名仓库交给 CLI，再把结果当成版本判断。

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

下表来自你已允许的本地比较。只查公开来源时，不用这些状态声称「本地已是最新」。

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

用时检查和 Routine 访问已确认的公开 GitHub 来源或 SkillHub 公开 API，不读取本地 Skill。你允许之后，CLI 只读选定目录，不上传正文、不执行下载的来源代码，也不写入或覆盖安装。来源歧义、清单不一致和请求失败均明确报告，不猜测映射。

在仓库根目录运行隔离测试：

```text
python -m unittest discover -s tests -v
```

可通过 [Issues](https://github.com/NickQin001/skill-update-notifier/issues)反馈：检查是否帮助你决定更新或保留，以及理由。附上脱敏后的命令或请求与相关结果；不提交凭证、私人路径或完整私有 Skill 内容。

许可：[MIT](skill-update-notifier/LICENSE)。分发包范围：[PUBLISHING.zh-CN.md](PUBLISHING.zh-CN.md)。
