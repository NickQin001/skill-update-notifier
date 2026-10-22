# Skill 更新检查 · v0.1.0

一个手动调用的 Skill 更新检查工具：比较已安装文件与明确的公开 GitHub 来源，展示上游变化和本地差异，帮助用户决定是否更新。

本版是早期试用。**只检查和建议，不安装或更新文件。** 自动提醒、使用统计、偏好存储和 SkillHub 来源适配尚未提供。

## 安装包

- `skill-update-notifier/`：完整 Skill 目录，包含入口、说明、Python 脚本和 MIT 许可证。
- `tests/`：行为与本地 Git 测试，不是运行依赖。

将完整 Skill 目录放入已核对的宿主 Skill 目录；不要将整个仓库当作单个 Skill 覆盖安装。具体使用见 [Skill README](skill-update-notifier/README.md) 和 [命令说明](skill-update-notifier/references/usage.md)。

需要 Python 3.10+、Git 和读取目标目录/访问公开来源的权限。没有第三方 Python 依赖。本轮实际验证环境是 Windows 和 Python 3.13；其他系统及各 AI 工具内的自动发现仍待验证。

## 核心判定

本地不同不等于上游有新版。没有可信来源和历史基线时报告缺口；额外本地文件不删除、不自动归入上游更新。历史快照用于区分远端变化与本地差异，提交数不会换算为落后版本数。

## 验证与反馈

```text
python -m unittest discover -s tests -v
```

测试在临时目录运行，只使用隔离样例；不修改用户已安装 Skill。真实联网验证结果与边界见 [VALIDATION.md](VALIDATION.md)。源码公开和结构校验都不等于所有宿主可用或平台审核通过。

反馈建议包含：命令或自然语言请求（先脱敏）、结果是否帮助你决定更新/保留、决定原因。不需要上传完整本地 Skill、私人路径或凭证。

许可为 MIT，见 Skill 目录内 LICENSE。发布包范围见 [PUBLISHING.zh-CN.md](PUBLISHING.zh-CN.md)。
