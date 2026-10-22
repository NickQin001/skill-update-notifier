# v0.1.1 验证摘要

日期：2026-10-22。结论：本版手动只读检查的发布前验证通过，可以作为明确限定范围的早期试用包。这里的通过不代表平台审核、所有宿主兼容或用户收益已得到证明。

## 已完成

| 检查 | 实际结果与边界 |
| --- | --- |
| 40项行为测试 | 全部通过；保留19项 GitHub/本地测试，新增21项 SkillHub 测试，覆盖来源确认、历史基线、字节哈希、重复版本、版本 ID 冲突、清单不一致、请求失败、正文核验及本地修改保护 |
| 独立目录 CLI | 抽离脚本后可以执行，无原型、数据库或其他 Skill 依赖 |
| 官方 Skill 结构校验 | quick_validate 返回 Skill is valid；不代表行为或宿主集成已验证 |
| GitHub ZIP 解压后联网回归 | 公开 own-your-view 旧快照到新标签报告 upstream_changed，同标签报告 matches_target；隔离安装副本字节未变 |
| SkillHub ZIP 解压后联网检查 | 匿名读取官方公开 API，以 multi-search-engine 2.1.5 / 3.0.0 的可核验公开文本构造隔离样例；正确返回 upstream_changed、matches_target、comparison_only，所有样例文件原样保留 |
| SkillHub 真实歧义记录 | find-skill-skillhub 的 1.0.1 有多条公开版本记录，明确拒绝；不取首条冒充唯一版本 |
| 独立B前向审查 | 合成 API 数据验证本地保护、来源未确认不联网、对比模式、错 slug、缺 count、请求期间修改；发现远端缓存忽略范围不一致及版本 ID 冲突 |
| A按审查意见修订 | 两侧统一忽略 .git / __pycache__ 目录并报告忽略项；版本 ID 冲突安全拒绝；两项均采纳 |
| A复跑B样例 | 完整相同但带缓存的样例现返回 matches_target；版本 ID 冲突拒绝，其他保护保持。这是A复跑，不是第二次独立B审查 |

联网验证使用[公开仓库](https://github.com/NickQin001/own-your-view)的已知标签：v0.1.1 对应 `f260aa69e1be152cfca6e68405cd0ce8adb11b93`，v0.1.2 对应 `f78497358680ae80d35b8cc7badff8d85c1c8628`。仅用于固定来源回归，不声称这些标签目前最新，也不检查任何真实安装是否落后。

SkillHub 依据[官方版本与差异接口](https://github.com/Tencent/skillhub/blob/main/docs/api/versions-and-diff.md)和[文件接口](https://github.com/Tencent/skillhub/blob/main/docs/api/files.md)。实测 multi-search-engine 基线1个文件、目标4个文件，新增3个文件并修改 SKILL.md；文本差异截断提示正确出现。另实测 dev-god 1.2.3 → 1.2.4 的 SKILL.md 变化可核验。没有执行这些 Skill 的代码，也没有修改真实安装。

曾遇到公开文件清单可用而对应 ZIP 下载返回404，故默认比较不依赖 ZIP；这不证明第三方下载/安装链路可用。SkillHub API 将来可能改变结构、鉴权或公开数据，无法据本次样本保证所有来源。

## 环境与复跑

实测 Windows、Python 3.13、Git。脚本按 Python 3.10+ 编写，但没有在 Python 3.10 或其他操作系统单独验收。沙箱拒绝临时目录访问，获得工具授权后在本机临时目录复跑成功；没有关闭 TLS 或执行下载代码。

在仓库根目录运行 `python -m unittest discover -s tests -v` 可复跑40项离线测试。联网检查需要有效网络与公开来源，网络失败应返回 check_failed，而非没有更新。默认文件比较与可选差异正文读取分别报告，正文不可用不会抹去已经核验的文件变化。

## 未验证与未提供

AI宿主自动发现/激活、其他操作系统、长期提醒接受程度、真实用户收益、SkillHub上传与平台审核仍待验证。本版根本不提供自动提醒、更新执行、合并、回滚或使用统计，因此没有宣称这些功能通过测试。
