from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_BRANCH = "main"


@dataclass
class RepoFile:
    path: str
    content: str
    size: int


def fetch_repo_files(
    owner: str,
    repo: str,
    branch: str = DEFAULT_BRANCH,
    path: str = "",
) -> List[RepoFile]:
    """Fetch all text files from a GitHub repository (public, no auth)."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": branch} if branch != DEFAULT_BRANCH else {}

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("GitHub API error: %s", e)
        return []

    items = response.json()
    if not isinstance(items, list):
        items = [items]

    files = []
    for item in items:
        if item["type"] == "file" and _is_text_file(item["name"]):
            content = _fetch_file_content(item)
            if content is not None:
                files.append(RepoFile(
                    path=item["path"],
                    content=content,
                    size=item.get("size", 0),
                ))
        elif item["type"] == "dir":
            # Recurse into directories (one level for now)
            sub_files = fetch_repo_files(owner, repo, branch, item["path"])
            files.extend(sub_files)

    return files


def _fetch_file_content(item: dict) -> Optional[str]:
    """Decode file content from GitHub API response."""
    if "content" in item and item.get("encoding") == "base64":
        try:
            return base64.b64decode(item["content"]).decode("utf-8")
        except (UnicodeDecodeError, Exception):
            return None

    # Fetch full content if not inline
    download_url = item.get("download_url")
    if download_url:
        try:
            r = requests.get(download_url, timeout=10)
            r.raise_for_status()
            return r.text
        except requests.RequestException:
            return None

    return None


def _is_text_file(filename: str) -> bool:
    """Check if a file is likely text (not binary)."""
    text_extensions = {
        ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml",
        ".cfg", ".ini", ".sh", ".bash", ".js", ".ts", ".html",
        ".css", ".xml", ".csv", ".rst", ".gitignore",
    }
    if "." not in filename:
        return filename in (".gitignore", "Makefile", "Dockerfile")
    ext = "." + filename.rsplit(".", 1)[-1].lower()
    return ext in text_extensions


def repo_files_to_dict(files: List[RepoFile]) -> Dict[str, str]:
    """Convert list of RepoFile to {path: content} dict."""
    return {f.path: f.content for f in files}
