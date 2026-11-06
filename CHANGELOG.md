# 更新日志

## 0.2.1

升到 0.2.1，以便 SkillHub 接受新的上传。相对 0.2.0 没有产品或行为变化。

文档里仍把 v0.2.0 写成「没有 GitHub Release 或标签」的地方已改正。已有预发布：[v0.2.0](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.0)，标签指向 `15981bfa0fab4457ac12bd0ba126a508d44817ab`，附件为 `skill-update-notifier-0.2.0-github.zip`、`skill-update-notifier-0.2.0-skillhub.zip` 和 `SHA256SUMS.txt`。本版不创建 v0.2.1 的 Release 或标签。

## 0.2.0 — 用时检查

相对 0.1.1：比较脚本仍是只读，仍不代为安装或覆盖。本版改的是何时检查、检查谁、以及默认拿什么当证据。该版本随后已有预发布 [v0.2.0](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.0)，标签指向 `15981bfa0fab4457ac12bd0ba126a508d44817ab`，附件为 `skill-update-notifier-0.2.0-github.zip`、`skill-update-notifier-0.2.0-skillhub.zip` 和 `SHA256SUMS.txt`。

- 用户明确点名某个 Skill，或清楚要求按该 Skill 工作时，在使用时做更新检查。可选每日 Routine 只作补充，不能代替用时检查。用时检查是文档约定、bot 职责或 Routine，不是平台钩子。Grok Bot 没有 PostToolUse，文档不把这一点写成平台会拦截工具调用。
- 用时只检查被点名的 Skill，不扫描整个库。
- 用时检查和 Routine 默认只查公开 GitHub / SkillHub，不读本机。与本地安装比较需要本次会话明确允许。未读本地时不声称「本地已是最新」。
- Routine 与用时检查互补。Routine 只包括用户库中来源已确认的 Skill，排除 Cursor 托管的 Skill；没有变化则保持安静；同样默认不读本机。
- 不自动安装，不覆盖已有安装。先完成点名的主要任务；仅在有更新、来源未确认或未与本地比较时附短建议，没有可说的则不附。
- 正文与宿主无关。附录 A 是 Claude Code 的可选钩子示例，不配置也能安装和使用。附录 B 说明 Grok Bot 只靠文档、bot 职责和 Routine。
- 只有 Skill 正文、已知安装记录或用户本轮给出的原来源 URL / SkillHub slug 才比较上游；否则「来源未确认，跳过版本判断」，不猜测同名仓库。
- 标明本包版本的位置改为 0.2.0。

## 0.1.1

手动只读试用。新增 SkillHub 官方公开 API 只读检查，保留 GitHub 来源检查。不自动提醒，不代为更新。
