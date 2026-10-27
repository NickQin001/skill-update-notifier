# Skill Update Notifier

English | [简体中文](README.zh-CN.md)

Review upstream changes before updating your AI skills.

**Current release: [v0.1.1 — manual, read-only preview](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.1.1).** Compare an installed skill with its confirmed public GitHub or SkillHub source, inspect local differences, and decide whether to update.

This release checks files and offers guidance. It does not install updates, schedule reminders, collect usage statistics, or save reminder preferences.

## What it does

- Checks a specified skill against a confirmed public GitHub repository and subdirectory, or a SkillHub slug.
- Separates upstream changes from local differences when a verified historical baseline is available.
- Produces Markdown or JSON reports with file changes, source details, and evidence gaps.
- Checks SkillHub public version records and file hashes, with optional verified public text diffs and release notes.
- Preserves local files, including custom files that are absent upstream.

A different local file is not proof of a newer release. An unknown source, missing baseline, or failed request is reported explicitly.

## Install

1. Download the GitHub ZIP from the [v0.1.1 release](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.1.1), or clone this repository.
2. Copy the complete `skill-update-notifier/` directory into a skill location supported by your AI tool. Keep its `scripts/` and `references/` directories.
3. Ask your AI assistant to use the skill, or run the standalone CLI below.

Check your tool's actual skill directory first. Back up and review an existing installation before replacing it. The repository root also contains tests and documentation; it is not itself the installable skill directory.

**Requirements:** Python 3.10+, permission to read the selected local skill and access its public source, and Git for GitHub checks. SkillHub checks do not require Git. There are no third-party Python runtime dependencies.

Validated environments and limitations are recorded in [VALIDATION.md](VALIDATION.md) (Chinese). Windows with Python 3.13 was tested; other operating systems and automatic skill discovery in individual AI tools remain unverified.

## Ask your AI assistant

> Use skill-update-notifier to check whether my selected skill has upstream changes worth reviewing. Confirm its local directory and original source first, explain local differences, and summarize the findings in English. Do not update files.

The assistant can check several skills individually and combine the results into a table. The packaged instructions and human-readable CLI messages are currently primarily Chinese; this English guide does not add a CLI language option.

## Standalone CLI

Run these commands from the `skill-update-notifier/` directory. Replace every angle-bracket placeholder with a value you have verified. `--source-confirmed` declares that you have confirmed the source; it does not discover or verify an installation relationship for you.

GitHub:

```text
python scripts/check_updates.py "<LOCAL_SKILL_DIRECTORY>" --repo "<PUBLIC_GITHUB_HTTPS_REPOSITORY>" --subdir "<VERIFIED_SKILL_SUBDIRECTORY>" --source-confirmed --format markdown
```

Use `--subdir .` when the skill is at the repository root. Without `--ref`, the check resolves the repository's current default `HEAD`.

SkillHub:

```text
python scripts/check_updates.py "<LOCAL_SKILL_DIRECTORY>" --skillhub-slug "<VERIFIED_SKILLHUB_SLUG>" --source-confirmed --format markdown
```

Without a historical baseline, the checker can compare files but cannot establish that a new upstream version has appeared since an earlier snapshot. If you have a verified previous source snapshot, add `--baseline <VERIFIED_40_CHARACTER_COMMIT_SHA> --baseline-kind observed` for GitHub, or `--baseline-version "<VERIFIED_SKILLHUB_VERSION>" --baseline-kind observed` for SkillHub. Use `installed` only when an installation record establishes that baseline.

For an explicitly requested comparison with another project whose relationship is unconfirmed, replace `--source-confirmed` with `--compare-only`. Use `--format json` for structured results. Full options are in [usage.md](skill-update-notifier/references/usage.md) (Chinese).

## Read the result

| Status | Meaning |
| --- | --- |
| `upstream_changed` | The confirmed source changed after the verified baseline; review local differences before updating. |
| `matches_target` | Local contents match the selected source snapshot. |
| `local_difference_only` | The source skill is unchanged from the baseline; local contents differ. |
| `baseline_unknown` | Differences exist, but there is no verified historical baseline. |
| `source_unknown` / `comparison_only` | The original source is unconfirmed, or this is only a comparison with another project. |
| `history_diverged` | The available history does not establish a normal forward update. |
| `check_failed` | The check did not complete; this does not mean there are no updates. |

Commit counts are not treated as counts of missed versions. GitHub UTF-8 text comparisons ignore BOM and line-ending differences; SkillHub compares raw-byte SHA256 hashes, so those differences are included. Release notes are the author's statements, not independent evidence of improvement.

## Privacy and feedback

The checker reads the selected local skill without uploading its contents or executing downloaded source code. It accesses the specified public GitHub source or SkillHub's public API. Source ambiguity, inconsistent manifests, and request failures are reported rather than guessed.

To run the isolated tests from the repository root:

```text
python -m unittest discover -s tests -v
```

Use [Issues](https://github.com/NickQin001/skill-update-notifier/issues) to report whether a check helped you decide to update or keep your current skill. Include a redacted command or request, the relevant result, and your reason. Omit credentials, private paths, and complete private skill contents.

License: [MIT](skill-update-notifier/LICENSE). Packaging details: [PUBLISHING.zh-CN.md](PUBLISHING.zh-CN.md) (Chinese).
