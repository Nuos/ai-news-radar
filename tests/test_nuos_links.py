"""Read-only checks for the staged Nuos link migration; never rewrite files."""
import json
from pathlib import Path
import re
import subprocess
import warnings

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://nuos.github.io/ai-news-radar"
OLD_LINK = re.compile(
    r"(?<![\w.-])LearnPrompt(?:/|%2f)"
    r"|\bLearnPrompt\.github\.io\b"
    r"|https?://news\.(?:LearnPrompt|Nuos)\.pro\b"
    r"|https?://(?:www\.)?github\.com/LearnPrompt(?=[/\s\"'?#)]|$)",
    re.IGNORECASE,
)
MIGRATED_FILES = (
    ".claude-plugin/marketplace.json",
    "README.md",
    "README.en.md",
    "docs/GPT_HANDOFF.md",
    "skills/radar/README.md",
    "skills/radar/SKILL.md",
    "skills/radar/assets/demo.sh",
    "skills/ai-news-radar/SKILL.md",
    "index.html",
    "classic/index.html",
    "scripts/generate_feed.py",
)


def test_migrated_files_do_not_restore_upstream_link_owners():
    for name in MIGRATED_FILES:
        text = (ROOT / name).read_text(encoding="utf-8").replace("\\/", "/")
        assert not OLD_LINK.search(text), f"Old repository/site link in {name}"


def test_nuos_runtime_entrypoints_agree():
    marketplace = json.loads((ROOT / MIGRATED_FILES[0]).read_text(encoding="utf-8"))
    assert marketplace["owner"]["url"] == "https://github.com/Nuos"
    assert marketplace["plugins"][0]["homepage"] == "https://github.com/Nuos/ai-news-radar"
    skill = (ROOT / "skills/radar/SKILL.md").read_text(encoding="utf-8")
    assert f"BASE_URL={SITE}/data" in skill
    for name, suffix in (("index.html", "/"), ("classic/index.html", "/classic/")):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert f'rel="canonical" href="{SITE}{suffix}"' in text


def test_report_remaining_tracked_link_migration_work():
    """Inventory remaining paths, including migration fixtures, without failing CI.

    Only Git-tracked files are read. The report contains counts and line numbers,
    never file contents, credentials, or untracked local files.
    """
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("A Git checkout is required for the repository-wide inventory")
    remaining = []
    scanned = 0
    for raw_name in tracked.split(b"\0"):
        if not raw_name:
            continue
        name = raw_name.decode("utf-8")
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "\0" in text:
            continue
        scanned += 1
        lines = [number for number, line in enumerate(text.splitlines(), 1)
                 if OLD_LINK.search(line.replace("\\/", "/"))]
        if lines:
            remaining.append({"path": name, "matched_lines": len(lines), "first_lines": lines[:12]})
    if remaining:
        warnings.warn("Nuos link migration inventory: " + json.dumps(
            {"scanned_text_files": scanned, "remaining": remaining}, ensure_ascii=False,
        ), UserWarning, stacklevel=1)
