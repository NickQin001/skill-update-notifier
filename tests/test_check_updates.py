import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parents[1] / "skill-update-notifier"
SCRIPT = PACKAGE / "scripts/check_updates.py"
spec = importlib.util.spec_from_file_location("check_updates", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
OLD = {"SKILL.md": b"---\nname: test\n---\nold\n"}
NEW = {"SKILL.md": b"---\nname: test\n---\nnew\n"}


class BehaviorTests(unittest.TestCase):
    def test_real_update_with_verified_ancestry(self):
        r = checker.evaluate(OLD, NEW, confirmed=True, baseline=OLD, ancestor=True, kind="installed")
        self.assertEqual(r["status"], "upstream_changed")
        self.assertEqual(r["message"], "内容已更新，版本号未提供")
        self.assertFalse(checker.changed(r["local_changes_from_baseline"]))

    def test_same_current_source(self):
        r = checker.evaluate(NEW, NEW, confirmed=True)
        self.assertEqual(r["status"], "matches_target")

    def test_extra_local_file_never_proves_update(self):
        local = dict(NEW, **{"CONTEXT-FORMAT.md": b"keep me"})
        self.assertEqual(checker.evaluate(local, NEW, confirmed=True)["status"], "baseline_unknown")
        r = checker.evaluate(local, NEW, confirmed=True, baseline=NEW, ancestor=True, kind="installed")
        self.assertEqual(r["status"], "local_difference_only")
        self.assertEqual(r["local_vs_target"]["added"], ["CONTEXT-FORMAT.md"])

    def test_local_edits_separate_from_upstream_update(self):
        local = {"SKILL.md": b"local customized", "mine.txt": b"private"}
        r = checker.evaluate(local, NEW, confirmed=True, baseline=OLD, ancestor=True, kind="installed")
        self.assertEqual(r["status"], "upstream_changed")
        self.assertEqual(r["local_changes_from_baseline"]["added"], ["mine.txt"])
        self.assertEqual(r["local_changes_from_baseline"]["modified"], ["SKILL.md"])

    def test_observed_not_installation_baseline(self):
        r = checker.evaluate(OLD, NEW, confirmed=True, baseline=OLD, ancestor=True, kind="observed")
        self.assertEqual(r["status"], "upstream_changed")
        self.assertIsNone(r["local_changes_from_baseline"])

    def test_missing_and_rewritten_history_not_new_version(self):
        self.assertEqual(checker.evaluate(OLD, NEW, confirmed=True)["status"], "baseline_unknown")
        self.assertEqual(checker.evaluate(OLD, NEW, confirmed=True, baseline=OLD, ancestor=False)["status"], "history_diverged")

    def test_same_name_and_same_content_do_not_prove_source(self):
        self.assertEqual(checker.evaluate(NEW, NEW, confirmed=False)["status"], "comparison_only")

    def test_binary_and_line_endings(self):
        local = {"SKILL.md": b"\xef\xbb\xbftext\r\n", "asset.bin": b"\xff\x00"}
        target = {"SKILL.md": b"text\n", "asset.bin": b"\xff\x00"}
        self.assertFalse(checker.changed(checker.compare(local, target)))
        target["asset.bin"] = b"\xfe\x00"
        self.assertEqual(checker.compare(local, target)["modified"], ["asset.bin"])

    def test_explicit_tag_is_reported_but_not_version_count(self):
        r = checker.evaluate(OLD, NEW, confirmed=True, baseline=OLD, ancestor=True, ref="refs/tags/v2")
        self.assertEqual(r["target_version"], "v2")

    def test_metadata_version_and_unrecognized_declaration(self):
        files = {"SKILL.md": b'---\nname: test\nmetadata:\n  version: "0.1.0"\n---\nbody\n'}
        self.assertEqual(checker.version_info(files), ("0.1.0", "declared_scalar"))
        complex_files = {"SKILL.md": b'---\nmetadata: {version: "2.0"}\n---\nbody\n'}
        self.assertEqual(checker.version_info(complex_files), (None, "unrecognized"))
        r = checker.evaluate(OLD, complex_files, confirmed=True, baseline=OLD, ancestor=True)
        self.assertEqual(r["message"], "内容已更新，版本信息未能可靠识别")

    def test_credentials_and_paths_refused(self):
        for url in ["https://user:secret@github.com/a/b", "file:///tmp/repo", "https://github.com/a/b?token=secret"]:
            with self.assertRaises(checker.CheckError):
                checker.github_url(url)
        for path in ["../a", "/root", "a/../b", "a\nb"]:
            with self.assertRaises(checker.CheckError):
                checker.file_path(path)

    def test_private_local_content_never_in_default_report(self):
        local = {"SKILL.md": b"SECRET_LOCAL_SENTINEL"}
        r = checker.base_report("demo")
        r.update(checker.evaluate(local, NEW, confirmed=True))
        self.assertNotIn("SECRET_LOCAL_SENTINEL", checker.markdown(r))
        self.assertNotIn("SECRET_LOCAL_SENTINEL", json.dumps(r))

    def test_source_unknown_no_network(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "SKILL.md").write_bytes(OLD["SKILL.md"])
            args = checker.parser().parse_args([temp])
            def fail(*args):
                self.fail("Unexpected network request")
            self.assertEqual(checker.check(args, fetcher=fail)["status"], "source_unknown")

    def test_unconfirmed_source_no_network(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "SKILL.md").write_bytes(OLD["SKILL.md"])
            args = checker.parser().parse_args([temp, "--repo", "https://github.com/example/skills", "--subdir", "skill"])
            self.assertEqual(checker.check(args, fetcher=lambda *a: self.fail("Unexpected network"))["status"], "source_unknown")

    def test_local_change_during_fetch_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "SKILL.md"
            file.write_bytes(OLD["SKILL.md"])
            args = checker.parser().parse_args([temp, "--repo", "https://github.com/example/skills", "--subdir", "skill", "--source-confirmed"])
            def fetch(*a):
                file.write_bytes(b"user changed during fetch")
                return {"commit": "a" * 40, "files": NEW, "baseline_files": None, "baseline_is_ancestor": None}
            with self.assertRaises(checker.CheckError):
                checker.check(args, fetcher=fetch)
            self.assertEqual(file.read_bytes(), b"user changed during fetch")

    def test_failure_is_not_no_update(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "SKILL.md").write_bytes(OLD["SKILL.md"])
            with patch.object(checker, "check", side_effect=checker.CheckError("fetch failed")), patch("builtins.print") as output:
                self.assertEqual(checker.main([temp, "--format", "json"]), 2)
                self.assertEqual(json.loads(output.call_args.args[0])["status"], "check_failed")

    def test_clean_directory_cli_no_project_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            detached = path / "detached.py"
            detached.write_bytes(SCRIPT.read_bytes())
            skill = path / "one-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_bytes(OLD["SKILL.md"])
            proc = subprocess.run([sys.executable, "-X", "utf8", str(detached), str(skill), "--format", "json"],
                                  cwd=path, capture_output=True, encoding="utf-8", timeout=20)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["status"], "source_unknown")
            self.assertEqual((skill / "SKILL.md").read_bytes(), OLD["SKILL.md"])


class RealGitTests(unittest.TestCase):
    def test_skill_at_repository_root(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            checker.git(repo, "init")
            (repo / "SKILL.md").write_bytes(NEW["SKILL.md"])
            checker.git(repo, "add", ".")
            checker.git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "root skill")
            sha = checker.git(repo, "rev-parse", "HEAD").stdout.decode().strip()
            self.assertEqual(checker.read_git_tree(repo, sha, "."), NEW)

    def test_git_subdirectory_changes_not_whole_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            checker.git(repo, "init")
            folder = repo / "skills/demo"
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_bytes(OLD["SKILL.md"])
            def commit(message):
                checker.git(repo, "add", ".")
                checker.git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", message)
                return checker.git(repo, "rev-parse", "HEAD").stdout.decode().strip()
            first = commit("initial")
            (repo / "unrelated.txt").write_text("other skill", encoding="utf-8")
            second = commit("unrelated")
            before = checker.read_git_tree(repo, first, "skills/demo")
            after = checker.read_git_tree(repo, second, "skills/demo")
            self.assertFalse(checker.changed(checker.compare(before, after)))
            (folder / "SKILL.md").write_bytes(NEW["SKILL.md"])
            third = commit("real skill change")
            newest = checker.read_git_tree(repo, third, "skills/demo")
            ancestor = checker.git(repo, "merge-base", "--is-ancestor", first, third).returncode == 0
            self.assertEqual(checker.evaluate(before, newest, confirmed=True, baseline=before, ancestor=ancestor)["status"], "upstream_changed")


if __name__ == "__main__":
    unittest.main()
