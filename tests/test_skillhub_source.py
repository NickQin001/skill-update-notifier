"""Offline fixtures use fictional slug demo explicitly, never live source claims."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

SCRIPTS = Path(__file__).resolve().parents[1] / "skill-update-notifier/scripts"
sys.path.insert(0, str(SCRIPTS))
import skillhub_source as hub
spec = importlib.util.spec_from_file_location("hub_checker", SCRIPTS / "check_updates.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
OLD = b"---\nname: demo\n---\nold\n"
NEW = b"---\nname: demo\n---\nnew\n"


def file_list(version, data):
    return {"version": version, "count": 1, "files": [{"path": "SKILL.md", "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}]}


def records():
    return {"slug": "demo", "versions": [
        {"versionId": 2, "version": "2.0.0", "createdAt": 200, "changelog": "new rules"},
        {"versionId": 1, "version": "1.0.0", "createdAt": 100, "changelog": "initial"}],
        "unknownPrivateField": "DO_NOT_PRINT_SENTINEL"}


def reader(url):
    if url.endswith("/versions"):
        return records()
    version = parse_qs(urlsplit(url).query).get("version", ["2.0.0"])[0]
    return file_list(version, OLD if version == "1.0.0" else NEW)


class SkillHubTests(unittest.TestCase):
    def run_check(self, local=OLD, extra=(), data_reader=reader):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "SKILL.md"
            file.write_bytes(local)
            args = checker.parser().parse_args([temp, "--skillhub-slug", "demo", "--format", "json", *extra])
            with patch.object(hub, "read_json", side_effect=data_reader):
                report = checker.check(args)
            self.assertEqual(file.read_bytes(), local)
            self.assertFalse(report["updates_performed"])
            return report

    def test_unknown_source_never_contacts_marketplace(self):
        self.assertEqual(self.run_check(data_reader=lambda url: self.fail("unexpected request"))["status"], "source_unknown")

    def test_missing_baseline_not_new_update(self):
        r = self.run_check(extra=("--source-confirmed",))
        self.assertEqual(r["status"], "baseline_unknown")

    def test_real_forward_classification_and_installed_count(self):
        r = self.run_check(extra=("--source-confirmed", "--baseline-version", "1.0.0", "--baseline-kind", "installed"))
        self.assertEqual(r["status"], "upstream_changed")
        self.assertEqual(r["upstream_changes"]["modified"], ["SKILL.md"])
        self.assertFalse(checker.changed(r["local_changes_from_baseline"]))
        self.assertEqual(r["published_versions_after_baseline"], ["2.0.0"])
        self.assertIn("1 个后续版本", r["versions_behind"])
        self.assertNotIn("DO_NOT_PRINT_SENTINEL", json.dumps(r))

    def test_observed_count_not_installed(self):
        r = self.run_check(extra=("--source-confirmed", "--baseline-version", "1.0.0"))
        self.assertIsNone(r["local_changes_from_baseline"])
        self.assertTrue(r["versions_behind"].startswith("未知"))

    def test_identical_but_unconfirmed_is_comparison_only(self):
        self.assertEqual(self.run_check(NEW, ("--compare-only",))["status"], "comparison_only")

    def test_same_current_no_update(self):
        self.assertEqual(self.run_check(NEW, ("--source-confirmed",))["status"], "matches_target")

    def test_same_upstream_local_edit_not_update(self):
        r = self.run_check(b"PRIVATE_LOCAL_SENTINEL", ("--source-confirmed", "--baseline-version", "2.0.0", "--baseline-kind", "installed"))
        self.assertEqual(r["status"], "local_difference_only")
        self.assertNotIn("PRIVATE_LOCAL_SENTINEL", checker.markdown(r))

    def test_raw_line_endings_reported(self):
        r = self.run_check(NEW.replace(b"\n", b"\r\n"), ("--source-confirmed", "--baseline-version", "2.0.0"))
        self.assertEqual(r["status"], "local_difference_only")
        self.assertIn("原始字节", r["comparison_method"])

    def test_pinned_target_not_latest_count(self):
        r = self.run_check(extra=("--source-confirmed", "--baseline-version", "1.0.0", "--target-version", "2.0.0", "--baseline-kind", "installed"))
        self.assertTrue(r["versions_behind"].startswith("未知"))

    def test_reverse_history_not_new(self):
        r = self.run_check(NEW, ("--source-confirmed", "--target-version", "1.0.0", "--baseline-version", "2.0.0"))
        self.assertEqual(r["status"], "history_diverged")

    def test_first_version_list_entry_not_default_latest(self):
        def reordered(url):
            data = reader(url)
            if url.endswith("/versions"):
                data["versions"].reverse()
            return data
        self.assertEqual(hub.fetch_source("demo", reader=reordered)["version"], "2.0.0")

    def test_duplicate_selected_version_refused(self):
        def duplicate(url):
            data = reader(url)
            if url.endswith("/versions"):
                data["versions"].append(dict(data["versions"][0], versionId=3))
            return data
        with self.assertRaisesRegex(hub.SkillHubError, "多条记录"):
            hub.fetch_source("demo", reader=duplicate)

    def test_unrelated_duplicate_warns_and_no_count(self):
        def duplicate(url):
            data = reader(url)
            if url.endswith("/versions"):
                data["versions"] += [{"versionId": i, "version": "0.0.1", "createdAt": i, "changelog": ""} for i in (3, 4)]
            return data
        result = hub.fetch_source("demo", baseline="1.0.0", reader=duplicate)
        self.assertTrue(result["warnings"])
        self.assertIsNone(result["published_versions_after_baseline"])

    def test_default_and_pinned_mismatch_refused(self):
        def inconsistent(url):
            if url.endswith("/files?version=2.0.0"):
                return file_list("2.0.0", OLD)
            return reader(url)
        with self.assertRaisesRegex(hub.SkillHubError, "不一致"):
            hub.fetch_source("demo", reader=inconsistent)

    def test_conflicting_version_ids_refused(self):
        data = records()
        data["versions"][1]["versionId"] = data["versions"][0]["versionId"]
        with self.assertRaisesRegex(hub.SkillHubError, "ID 重复"):
            hub.version_records(data, "demo")

    def test_remote_ignored_dirs_not_false_missing_files(self):
        def with_cache(url):
            data = reader(url)
            if "/files" in url:
                data["files"].append({"path": "__pycache__/sample.pyc", "size": 1, "sha256": hashlib.sha256(b"x").hexdigest()})
                data["count"] += 1
            return data
        r = self.run_check(NEW, ("--source-confirmed", "--baseline-version", "2.0.0"), with_cache)
        self.assertEqual(r["status"], "matches_target")
        self.assertEqual(r["ignored_target_files"], ["__pycache__/sample.pyc"])
        self.assertEqual(r["local_vs_target"]["removed"], [])

    def test_bad_manifest_and_history_refused(self):
        for key, values in [("path", ["../x", "/x", "a//b", "a\\b", "a\nb"]), ("size", [-1, True, 21 * 1024 * 1024]), ("sha256", ["bad", None])]:
            for value in values:
                data = file_list("2.0.0", NEW)
                data["files"][0][key] = value
                with self.subTest(key=key, value=value), self.assertRaises(hub.SkillHubError):
                    hub.manifest(data)
        data = file_list("2.0.0", NEW)
        data["count"] = 2
        with self.assertRaises(hub.SkillHubError):
            hub.manifest(data)
        with self.assertRaises(hub.SkillHubError):
            hub.version_records({"slug": "other", "versions": []}, "demo")

    def test_http_failures_sanitized_and_retry_bounded(self):
        for code, tries in [(401, 1), (404, 1), (302, 1), (429, 3), (500, 3)]:
            op = MagicMock()
            op.open.side_effect = HTTPError(hub.API + "demo/files", code, "PRIVATE_SENTINEL", {}, None)
            with patch.object(hub, "build_opener", return_value=op), patch.object(hub.time, "sleep"), self.assertRaises(hub.SkillHubError) as error:
                hub.read_json(hub.API + "demo/files")
            self.assertEqual(op.open.call_count, tries)
            self.assertNotIn("PRIVATE_SENTINEL", str(error.exception))

    def test_network_and_invalid_json_safe(self):
        op = MagicMock()
        op.open.side_effect = URLError("PRIVATE_SENTINEL")
        with patch.object(hub, "build_opener", return_value=op), self.assertRaises(hub.SkillHubError) as error:
            hub.read_json(hub.API + "demo/files")
        self.assertNotIn("PRIVATE_SENTINEL", str(error.exception))
        for payload in [b"not-json", b"[]", b"x" * (hub.MAX_RESPONSE + 1)]:
            op = MagicMock()
            op.open.return_value.__enter__.return_value.read.return_value = payload
            with patch.object(hub, "build_opener", return_value=op), self.assertRaises(hub.SkillHubError):
                hub.read_json(hub.API + "demo/files")

    def test_public_text_diff_verified_and_tamper_refused(self):
        snapshot = hub.fetch_source("demo", baseline="1.0.0", reader=reader)
        data = {"slug": "demo", "base": "1.0.0", "target": "2.0.0", "path": "SKILL.md", "tooLarge": False}
        for key, raw in [("baseFile", OLD), ("targetFile", NEW)]:
            data[key] = {"exists": True, "text": raw.decode(), "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}
        diff, warnings = hub.source_text_diff(snapshot, "1.0.0", reader=lambda _: data)
        self.assertIn("+new", diff)
        self.assertFalse(warnings)
        data["targetFile"]["text"] = "UNVERIFIED_SENTINEL"
        diff, warnings = hub.source_text_diff(snapshot, "1.0.0", reader=lambda _: data)
        self.assertEqual(diff, "")
        self.assertTrue(warnings)

    def test_local_edit_during_request_preserved_and_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "SKILL.md"
            path.write_bytes(OLD)
            args = checker.parser().parse_args([temp, "--skillhub-slug", "demo", "--source-confirmed"])
            def mutate(url):
                path.write_bytes(b"new local edit")
                return reader(url)
            with patch.object(hub, "read_json", side_effect=mutate), self.assertRaises(checker.CheckError):
                checker.check(args)
            self.assertEqual(path.read_bytes(), b"new local edit")


if __name__ == "__main__":
    unittest.main()
