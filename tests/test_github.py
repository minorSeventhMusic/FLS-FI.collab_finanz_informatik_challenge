from __future__ import annotations

import unittest

from bridge.github_client import (
    CommitInfo,
    RepoFile,
    _is_text_file,
    commits_to_text,
    repo_files_to_dict,
)


class TestGitHubClient(unittest.TestCase):
    def test_is_text_file(self):
        self.assertTrue(_is_text_file("calculator.py"))
        self.assertTrue(_is_text_file("README.md"))
        self.assertTrue(_is_text_file(".gitignore"))
        self.assertFalse(_is_text_file("image.png"))
        self.assertFalse(_is_text_file("data.bin"))

    def test_repo_files_to_dict(self):
        files = [
            RepoFile(path="a.py", content="print('a')", size=10),
            RepoFile(path="b.md", content="# B", size=3),
        ]
        d = repo_files_to_dict(files)
        self.assertEqual(len(d), 2)
        self.assertEqual(d["a.py"], "print('a')")

    def test_commits_to_text(self):
        commits = [
            CommitInfo(
                sha="abc1234",
                message="Fix calculator bug",
                author="Alice",
                date="2026-04-01",
                files_changed=["calculator.py"],
            ),
            CommitInfo(
                sha="def5678",
                message="Add tests",
                author="Bob",
                date="2026-04-02",
                files_changed=["test_calculator.py"],
            ),
        ]
        text = commits_to_text(commits)
        self.assertIn("abc1234", text)
        self.assertIn("Fix calculator bug", text)
        self.assertIn("Alice", text)
        self.assertIn("calculator.py", text)
        self.assertIn("def5678", text)
        self.assertIn("Bob", text)

    def test_commits_to_text_empty(self):
        self.assertEqual(commits_to_text([]), "")

    def test_commit_no_files(self):
        commits = [
            CommitInfo(
                sha="xyz",
                message="Init",
                author="Dev",
                date="2026-01-01",
                files_changed=[],
            ),
        ]
        text = commits_to_text(commits)
        self.assertIn("unknown files", text)


if __name__ == "__main__":
    unittest.main()
