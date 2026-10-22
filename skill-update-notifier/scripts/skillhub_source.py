"""Read-only adapter for documented anonymous https://api.skillhub.cn APIs.

No installation, credentials, signed download URLs, or local content is sent.
Unknown response fields are discarded, never logged or included in reports.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

API = "https://api.skillhub.cn/api/v1/skills/"
MAX_RESPONSE = 2 * 1024 * 1024


class SkillHubError(Exception):
    """Safe diagnostic without raw responses, credentials, or redirect targets."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def read_json(url):
    if not url.startswith(API):
        raise SkillHubError("SkillHub 请求来源无效")
    for attempt in range(3):
        try:
            request = Request(url, headers={"Accept": "application/json", "User-Agent": "skill-update-notifier/0.1.1"})
            with build_opener(NoRedirect()).open(request, timeout=20) as response:
                data = response.read(MAX_RESPONSE + 1)
            if len(data) > MAX_RESPONSE:
                raise SkillHubError("SkillHub 响应超出大小限制；未完成检查")
            value = json.loads(data)
            if not isinstance(value, dict):
                raise ValueError()
            return value
        except HTTPError as error:
            if (error.code == 429 or 500 <= error.code < 600) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise SkillHubError(f"SkillHub HTTP {error.code}：来源不可访问或请求失败；失败不等于没有更新") from None
        except (URLError, OSError, TimeoutError):
            raise SkillHubError("SkillHub 网络读取失败；未完成检查") from None
        except (ValueError, UnicodeError):
            raise SkillHubError("SkillHub 返回的 JSON 无效；未完成检查") from None


def identifier(value, label):
    # These are accepted input constraints, not a claim about all server names.
    if not isinstance(value, str) or len(value) > 128 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*", value):
        raise SkillHubError(f"SkillHub {label} 格式无法可靠处理")
    return value


def manifest(payload):
    version = identifier(payload.get("version"), "版本号")
    entries = payload.get("files")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 2000 or type(payload.get("count")) is not int or payload["count"] != len(entries):
        raise SkillHubError("SkillHub 文件数量或清单结构无效")
    result, seen, total = {}, set(), 0
    for entry in entries:
        if not isinstance(entry, dict):
            raise SkillHubError("SkillHub 文件记录无效")
        path, size, digest = entry.get("path"), entry.get("size"), entry.get("sha256")
        if (not isinstance(path, str) or not path or path.startswith("/") or
                any(part in ("", ".", "..") for part in path.split("/")) or
                "\\" in path or ":" in path or any(ord(c) < 32 or ord(c) == 127 for c in path) or
                path.casefold() in seen):
            raise SkillHubError("SkillHub 文件路径无效或重复")
        if type(size) is not int or not 0 <= size <= 20 * 1024 * 1024 or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise SkillHubError("SkillHub 文件大小或 SHA256 无效")
        total += size
        seen.add(path.casefold())
        result[path] = {"size": size, "sha256": digest.lower()}
    if "SKILL.md" not in result or total > 64 * 1024 * 1024:
        raise SkillHubError("SkillHub 清单缺少 SKILL.md 或超出总大小限制")
    return version, result


def version_records(payload, slug):
    entries = payload.get("versions")
    if payload.get("slug") != slug or not isinstance(entries, list) or not 1 <= len(entries) <= 10000:
        raise SkillHubError("SkillHub 版本列表与来源不符或结构无效")
    result, seen_ids = [], set()
    for item in entries:
        if not isinstance(item, dict):
            raise SkillHubError("SkillHub 版本记录无效")
        version = identifier(item.get("version"), "版本号")
        if type(item.get("versionId")) is not int or type(item.get("createdAt")) is not int or item["createdAt"] < 0:
            raise SkillHubError("SkillHub 版本标识或发布时间无效")
        if item["versionId"] in seen_ids:
            raise SkillHubError("SkillHub 版本 ID 重复或冲突；无法可靠核验版本记录")
        seen_ids.add(item["versionId"])
        # Changelog remains external untrusted data; no other fields escape.
        changelog = item.get("changelog")
        if changelog is not None and not isinstance(changelog, str):
            raise SkillHubError("SkillHub 更新说明格式无效")
        result.append({"version": version, "createdAt": item["createdAt"], "versionId": item["versionId"],
                       "changelog": (changelog or "")[:4000]})
    return result


def unique_record(records, version):
    found = [item for item in records if item["version"] == version]
    if len(found) != 1:
        raise SkillHubError("SkillHub 所选版本缺失或同一版本号对应多条记录；无法可靠定位，未完成检查")
    return found[0]


def fetch_source(slug, target=None, baseline=None, reader=None):
    reader = reader or read_json
    slug = identifier(slug, "slug")
    if target is not None:
        identifier(target, "目标版本号")
    if baseline is not None:
        identifier(baseline, "基线版本号")
    base_url = API + quote(slug, safe="")
    records = version_records(reader(base_url + "/versions"), slug)
    suffix = "?" + urlencode({"version": target}) if target else ""
    selected, files = manifest(reader(base_url + "/files" + suffix))
    if target and selected != target:
        raise SkillHubError("SkillHub 文件清单返回了不同的目标版本")
    record = unique_record(records, selected)
    if not target:
        pinned, pinned_files = manifest(reader(base_url + "/files?" + urlencode({"version": selected})))
        if pinned != selected or pinned_files != files:
            raise SkillHubError("SkillHub 默认版本与固定版本清单不一致；请重试")
    old, forward, old_record = None, None, None
    if baseline:
        old_record = unique_record(records, baseline)
        old_version, old = manifest(reader(base_url + "/files?" + urlencode({"version": baseline})))
        if old_version != baseline:
            raise SkillHubError("SkillHub 基线文件清单版本不符")
        if baseline == selected and old != files:
            raise SkillHubError("SkillHub 同一版本在检查期间出现不同文件清单；请重试")
        forward = baseline == selected or old_record["createdAt"] < record["createdAt"]
    ambiguous = len({item["version"] for item in records}) != len(records)
    warnings = ["公开列表含重复版本号；未使用歧义版本，落后版本数未知"] if ambiguous else []
    # Only count the public records in this request, never all releases ever made.
    newer = None
    times = [item["createdAt"] for item in records]
    if old_record and forward and not target and not ambiguous and len(set(times)) == len(times):
        if record["createdAt"] == max(times):
            newer = [item["version"] for item in sorted(records, key=lambda x: x["createdAt"])
                     if old_record["createdAt"] < item["createdAt"] <= record["createdAt"]]
    def comparison_scope(tree):
        if tree is None:
            return None, []
        ignored = sorted(name for name in tree if any(part in {".git", "__pycache__"} for part in name.split("/")[:-1]))
        return {name: item for name, item in tree.items() if name not in ignored}, ignored
    files, ignored_target = comparison_scope(files)
    old, ignored_baseline = comparison_scope(old)
    return {"source": base_url, "version": selected, "files": files, "baseline_files": old,
            "forward": forward, "changelog": record["changelog"], "warnings": warnings,
            "ignored_target_files": ignored_target, "ignored_baseline_files": ignored_baseline,
            "published_versions_after_baseline": newer}


def raw_hashes(files):
    return {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}


def hashes(files):
    return {name: info["sha256"] for name, info in files.items()}


def delta(left, right):
    return {"added": sorted(right.keys() - left.keys()), "removed": sorted(left.keys() - right.keys()),
            "modified": sorted(name for name in left.keys() & right.keys() if left[name] != right[name])}


def source_text_diff(snapshot, baseline, reader=None):
    """At most 10 changed paths; verify returned public text against manifest hashes."""
    import difflib
    reader = reader or read_json
    before, after = snapshot["baseline_files"], snapshot["files"]
    changes = delta(hashes(before), hashes(after))
    names = sorted(sum(changes.values(), []))
    output, warnings, budget = [], [], 12000
    for name in names[:10]:
        try:
            url = snapshot["source"] + "/diff/file?" + urlencode({"base": baseline, "target": snapshot["version"], "path": name})
            data = reader(url)
            if (data.get("slug") != snapshot["source"].rsplit("/", 1)[-1] or data.get("base") != baseline or
                    data.get("target") != snapshot["version"] or data.get("path") != name or data.get("tooLarge") is not False):
                raise SkillHubError("diff 范围或大小无法验证")
            texts = []
            for key, manifest_files in (("baseFile", before), ("targetFile", after)):
                item = data.get(key)
                expected = manifest_files.get(name)
                if not isinstance(item, dict) or item.get("exists") is not bool(expected):
                    raise SkillHubError("diff 文件存在性不符")
                if expected is None:
                    texts.append("")
                    continue
                value = item.get("text")
                if not isinstance(value, str) or "\x00" in value:
                    raise SkillHubError("diff 未提供可验证文本")
                raw = value.encode("utf-8")
                if (item.get("sha256") != expected["sha256"] or item.get("size") != expected["size"] or
                        len(raw) != expected["size"] or hashlib.sha256(raw).hexdigest() != expected["sha256"]):
                    raise SkillHubError("diff 文本与文件清单不符")
                texts.append(value)
            diff = "".join(difflib.unified_diff(texts[0].splitlines(True), texts[1].splitlines(True),
                                             fromfile="baseline/" + name, tofile="target/" + name))
            output.append(diff[:budget])
            budget -= len(diff)
            if budget <= 0:
                warnings.append("公开文本差异已截断至 12000 字符")
                break
        except SkillHubError:
            warnings.append("部分公开文本差异无法核验；文件哈希比较结果仍有效")
    if len(names) > 10:
        warnings.append("仅尝试读取前 10 个变化文件的公开文本差异")
    return "".join(output), sorted(set(warnings))
