# v0.1.0 发布说明

发布定位：**Skill 更新检查（手动试用版）**。技术 slug：`skill-update-notifier`。版本：`0.1.0`；GitHub 发布标签建议 `v0.1.0`，标记预发布。

## 可直接使用的介绍

主动检查已安装 Skill，与确认的公开 GitHub 来源比较，展示上游内容变化、本地差异和证据缺口，辅助决定是否更新。提供 Markdown/JSON 报告，保留本地文件。需要 Python 3.10+ 与 Git；本版不提供自动提醒、使用统计、代为更新或 SkillHub 来源检查。

## 包与目录

- `skill-update-notifier-0.1.0-skillhub.zip`：Skill 文件平铺 ZIP 根目录，包含 SKILL.md、README.md、LICENSE、scripts、references，供平台上传。版本、名称等在实际上传表单中填入对应字段；不臆测平台未公开字段。
- `skill-update-notifier-0.1.0-github.zip`：独立仓库内容，包含项目 README、发布说明、验证摘要、Skill 文件夹及测试。可解压后作为新仓库内容，勿上传整个研发项目目录。
- `SHA256SUMS.txt`：两个 ZIP 的摘要，便于上传前后核验。

上传包不包含本机路径、实验数据库、下载仓库、协议导出、临时样例、审查原始记录或已安装 Skill 副本。

## 发布口径

保留“手动试用版”和依赖说明。不要写成“自动跟踪所有工具”“五次拒绝自动停止”“自动备份更新”或“已经适配 SkillHub 更新源”。在 SkillHub 分发与接入 SkillHub 来源检查是两件事。

GitHub 仓库名可使用 `skill-update-notifier`，最终账号与仓库可用性需要发布时核对。本地准备文件不等于已推送。SkillHub 上传包不等于平台已收录、审核或安全认证。

本版采用 MIT 许可，作者行采用通用 contributors 表述；发布者可在公开前按实际贡献者信息调整。自动化功能仍是项目后续目标，不随本次范围收敛而取消。
