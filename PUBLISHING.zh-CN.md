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
