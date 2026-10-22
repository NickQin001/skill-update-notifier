# 命令与判定说明

版本 0.1.0。仅手动只读检查；不需要本项目的 prototype、lab、数据库或任何其他 Skill。

## 运行

依赖：Python 3.10+、Git；仅在 Windows / Python 3.13 上做本轮实测，其他系统与宿主待验证。以包内脚本实际路径运行，或进入本 Skill 目录运行以下命令。所有尖括号参数是用户环境占位符，必须先核对再替换，不能原样执行。

```text
python scripts/check_updates.py "<LOCAL_SKILL_DIRECTORY>"
```

不提供来源时不会联网，返回“来源待确认”。已核对原来源时：

```text
python scripts/check_updates.py "<LOCAL_SKILL_DIRECTORY>" --repo "<PUBLIC_GITHUB_HTTPS_REPOSITORY>" --subdir "<VERIFIED_SKILL_SUBDIRECTORY>" --source-confirmed --format markdown
```

默认 `--ref HEAD` 表示此次远端默认分支，输出解析后的完整提交。也可以传入已核对分支、`refs/tags/<TAG>` 或完整提交 SHA。指定旧标签只检查该标签，不表示它是最新发行版。

Skill 在仓库根目录时使用 `--subdir .`；根目录与子目录均支持。只在指定路径内查找文件，不搜索同名目录来猜路径。

来源关系未确认、但用户主动要求对比时，把 `--source-confirmed` 换成 `--compare-only`。两者互斥；不提供任何一个时不会联网。前者表示调用者已有来源证据，工具不会从名字推断来源。

有历史证据时增加：

```text
--baseline <VERIFIED_40_CHARACTER_COMMIT_SHA> --baseline-kind observed --show-upstream-diff
```

`observed` 是过去看见的来源快照；`installed` 是有安装证据的历史原始内容。两者均要保证仓库和子目录对应当前 Skill。不能因为目录现状与某提交相似就伪造安装记录。首次检查输出的 `target_commit` 可以作为未来的 observed 比较基线；工具不自动持久化或覆盖用户记录。

`--format json` 返回本工具自定义结构。报告到标准输出；需要保存时选用已核对且不在已安装 Skill 内的工作目录，避免覆盖已有文件。

## 状态

| status | 含义 |
| --- | --- |
| source_unknown | 未确认原来源，未联网 |
| comparison_only | 主动对比其他来源，不认定为同一 Skill 的新版 |
| matches_target | 内容与所选目标一致；不反推最初安装来源 |
| baseline_unknown | 存在差异，缺少历史基线，更新方向未知 |
| history_diverged | 基线不是目标的祖先，可能回退或分叉 |
| local_difference_only | 来源 Skill 相对基线未变，只有本地不同 |
| upstream_changed | 原来源 Skill 相对历史基线发生了后续内容变化；仍需审阅本地差异 |
| check_failed | 检查未完成，不能按无更新处理 |

退出码 0 表示完成一次判定（可能是来源未知）；2 表示参数或读取失败。是否有更新应看 status，而非只看退出码。

`local_vs_target` 的 added/removed/modified 表示本地相对目标多出/缺少/不同；`upstream_changes` 表示目标相对基线新增/删除/修改。它们不是相同方向。无 installed 基线时，`local_changes_from_baseline` 为 null，不把本地差异归咎于用户修改。

## 比较与网络范围

比较整个 Skill 子目录，包含脚本、资料与二进制文件；忽略目录 `.git`、`__pycache__`，本地忽略列表会记录在 JSON 中。UTF-8 文本忽略 BOM 与 CRLF/LF 差异，二进制按原字节比较。时间戳和执行权限差异不属于本版内容判定。

本版拒绝内部符号链接/Junction、Git 子模块、大小写冲突、超大文件；用户明确选定的根目录兼容链接可解析后只读。单 Skill 上限 2000 文件、单文件20MiB、合计64MiB。Git 获取所选 ref 的历史以核验祖先关系，仓库网络下载量不受上述 Skill 文件限制，大仓库可能较慢；命令超时90秒，失败明确报告。

仅访问用户明确指定的公开 GitHub HTTPS 仓库；禁用凭据助手与交互登录，不支持私有仓库、其他域名或 SkillHub 来源适配。获取到临时 bare 仓库，不检出、不执行下载内容；临时副本正常退出时清理，异常终止可能留下系统临时文件。没有持久缓存，也不提供自动定期检查。

版本信息仅报告显式选择的标签、简单顶层 `version` 或缩进式 `metadata.version` 标量，不声称完整版本发现。复杂 YAML 声明无法可靠解析时显示“版本信息未能可靠识别”，不声称作者没提供。没有识别到声明时，“版本号未提供”也仅限此次检查范围，未枚举全部发布记录或其他文件的版本信息。未知版本不能自行编号。检查完成后来源仍可能继续更新，所有结论只针对本次固定快照。
