# Skill Update Notifier

English | [简体中文](README.zh-CN.md)

Review a confirmed public source before you decide whether a skill is worth another look.

**Current version: 0.2.1 — check at use time (用时检查).** The check behaves the same as 0.2.0. The prerelease is [v0.2.1](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.1). Its tag points at `d41023de274b5a84938de3337ec63e56a70669c0`. Assets are `skill-update-notifier-0.2.1-github.zip`, `skill-update-notifier-0.2.1-skillhub.zip`, and `SHA256SUMS.txt`. The previous prerelease remains [v0.2.0](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.0). The tagged [v0.1.1 preview](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.1.1) is the earlier release.

When you name a skill or ask to work by that skill, check that skill at use time. The check is a documented duty, not a platform hook. An optional daily routine complements it and does not replace it. The check still does not install updates, overwrite an install, collect usage statistics, or save reminder preferences.

## What it does

- At use time, checks only the skill you named, not your whole library.
- Consults a confirmed public GitHub repository and subdirectory, or a SkillHub slug. Use-time and routine checks stay on those public sources and do not read your machine unless you allow a local comparison in that session.
- Compares upstream only when the skill body, a known install record, or you in this turn provide the original source URL or SkillHub slug. Otherwise it says the source is unconfirmed and skips the version judgment. It does not guess a same-name repository.
- If it did not read the local install, it does not claim that the local copy is already current.
- After the task you named, adds a short note only when there is an update, the source is unknown, or the local install was not compared. When none of those apply, it adds nothing.
- When you allow a local comparison, separates upstream changes from local differences if a verified historical baseline exists, and writes a Markdown or JSON report.
- Checks SkillHub public version records and file hashes, with optional verified public text diffs and release notes.
- Leaves local files in place, including custom files that are absent upstream. It does not install or overwrite for you.

A different local file is not proof of a newer release. An unknown source, missing baseline, or failed request is reported explicitly. An optional routine covers only library skills whose source is already confirmed, skips Cursor-managed skills, stays quiet when nothing changed, and uses the same public-only default.

## Install

1. Clone this repository, or download the assets from the [v0.2.1 prerelease](https://github.com/NickQin001/skill-update-notifier/releases/tag/v0.2.1). That tag points at `d41023de274b5a84938de3337ec63e56a70669c0`.
2. Copy the complete `skill-update-notifier/` directory into a skill location supported by your AI tool. Keep its `scripts/` and `references/` directories. No hook is required. The Claude Code sample in `SKILL.md` Appendix A is optional.
3. Ask your AI assistant to use the skill, or run the standalone CLI below when you want a local comparison.

Check your tool's actual skill directory first. Back up and review an existing installation before replacing it. The repository root also contains tests and documentation; it is not itself the installable skill directory.

**Requirements:** Python 3.10+ for the CLI, access to the confirmed public source, and Git for GitHub checks. SkillHub checks do not require Git. There are no third-party Python runtime dependencies. The CLI reads the local directory you pass, so run it only after you allow that comparison in the session. The default use-time check does not run the CLI.

Validated environments and limitations are recorded in [VALIDATION.md](VALIDATION.md) (Chinese). Windows with Python 3.13 was tested; other operating systems and automatic skill discovery in individual AI tools remain unverified.

## Ask your AI assistant

> Use the skill I named and finish that task first. Then check only that skill against its confirmed public source. Do not read my machine, do not install or overwrite files, and do not claim my local copy is current. If the source is unknown, say so and skip the version judgment.

Name more than one skill only when each of them should be checked. That still does not scan the rest of the library. The packaged instructions and human-readable CLI messages are currently primarily Chinese; this English guide does not add a CLI language option.

## Standalone CLI

Run these commands from the `skill-update-notifier/` directory only when this session may read the local skill. Replace every angle-bracket placeholder with a value you have verified. `--source-confirmed` declares that you have confirmed the source; it does not discover or verify an installation relationship for you. Without that confirmation, do not point the CLI at a same-name repository and treat the result as a version judgment.

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

These statuses come from a local comparison you allowed. A public-only check does not use them to claim the local copy is current.

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

A use-time or routine check uses the confirmed public GitHub source or SkillHub's public API and does not read the local skill. The CLI, once you allow it, reads the selected local skill without uploading its contents or executing downloaded source code. It does not write to or replace the install. Source ambiguity, inconsistent manifests, and request failures are reported rather than guessed.

To run the isolated tests from the repository root:

```text
python -m unittest discover -s tests -v
```

Use [Issues](https://github.com/NickQin001/skill-update-notifier/issues) to report whether a check helped you decide to update or keep your current skill. Include a redacted command or request, the relevant result, and your reason. Omit credentials, private paths, and complete private skill contents.

License: [MIT](skill-update-notifier/LICENSE). Packaging details: [PUBLISHING.zh-CN.md](PUBLISHING.zh-CN.md) (Chinese).
