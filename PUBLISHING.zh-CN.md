# 发布说明

当前包版本是 **0.2.1**（用时检查，行为与 0.2.0 相同）。GitHub 预发布标签为 [`v0.2.1`](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.1)，指向 `d41023de274b5a84938de3337ec63e56a70669c0`。没有把 0.2.1 上传到 SkillHub。SkillHub 上已有 0.2.0。上一份预发布仍是 [`v0.2.0`](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.0)。

## v0.2.1 发布物

- `skill-update-notifier-0.2.1-skillhub.zip`：6 个文件，`SKILL.md` 在 ZIP 根目录，另有 README.md、LICENSE、`references/usage.md` 与两个脚本。供以后上传，不等于平台已收录或审核。
- `skill-update-notifier-0.2.1-github.zip`：Skill 目录、离线测试和项目说明。
- `SHA256SUMS.txt`：两个 ZIP 的摘要，附在同一 GitHub Release。

## v0.2.0 发布物

- `skill-update-notifier-0.2.0-skillhub.zip`：6 个文件，`SKILL.md` 在 ZIP 根目录，另有 README.md、LICENSE、`references/usage.md` 与两个脚本。这是 v0.2.0 Release 上的上传包。SkillHub 现已有 0.2.0，不等于平台安全认证。
- `skill-update-notifier-0.2.0-github.zip`：Skill 目录、离线测试和项目说明。
- `SHA256SUMS.txt`：两个 ZIP 的摘要，附在同一 GitHub Release。

行为以 [SKILL.md](skill-update-notifier/SKILL.md) 和 [CHANGELOG.md](CHANGELOG.md) 为准。下面的 v0.1.1 包名、标签和上传清单保持为历史记录。

以下保留为 v0.1.1 的历史发布口径。

# v0.1.1 发布说明

发布定位：**Skill 更新检查（手动试用版）**。Slug：`skill-update-notifier`。版本：`0.1.1`；GitHub 标签 `v0.1.1`，标记预发布。

## 可直接使用的介绍

显示名称：Skill 更新检查

描述：主动检查已安装 Skill，与确认的公开 GitHub 或 SkillHub 来源比较，展示上游内容变化、本地差异、发布说明及证据缺口，辅助决定是否更新。提供 Markdown/JSON 报告，保留本地文件。需要 Python 3.10+，GitHub 来源另需 Git；本版不自动提醒、不采集使用频率、不代为更新。

变更说明：新增 SkillHub 官方公开 API 只读检查，支持来源 slug、历史基线及目标版本；比较公开文件 SHA256 与本地文件，显示公开发布说明和可核验的版本间文本差异。处理重复版本号、文件清单不一致及接口失败，避免把本地差异或读取失败误报为更新结论。保留 GitHub 来源检查。

## 包与目录

- `skill-update-notifier-0.1.1-skillhub.zip`：6 个文件平铺 ZIP 根目录，包含 SKILL.md、README.md、LICENSE、两个脚本与命令说明，供平台上传。
- `skill-update-notifier-0.1.1-github.zip`：12 个文件，包含项目说明、Skill 文件夹及离线测试。勿上传整个研发项目目录。
- `SHA256SUMS.txt`：两个 ZIP 的摘要，便于上传前后核验。

上传包不包含本机路径、实验数据库、下载仓库、协议导出、临时样例、审查原始记录或已安装 Skill 副本。

## 发布口径

保留“手动试用版”和依赖说明。不要写成“自动跟踪所有工具”“五次拒绝自动停止”或“自动备份更新”。已接入 SkillHub 公开来源检查，不等于本工具已在 SkillHub 上传、收录或通过审核。v0.1.0 保留为历史发布，不覆盖旧标签与附件。

公开仓库：[NickQin001/skill-update-notifier](https://github.com/NickQin001/skill-update-notifier)。本地准备文件不等于已推送；以实际 GitHub 发布状态为准。SkillHub 上传包不等于平台已收录、审核或安全认证。

本版采用 MIT 许可，作者行采用通用 contributors 表述；发布者可在公开前按实际贡献者信息调整。自动化功能仍是项目后续目标，不随本次范围收敛而取消。
