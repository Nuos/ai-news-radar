"""Read-only regression checks for Nuos links across all tracked text files."""
import json
from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://nuos.github.io/ai-news-radar"
OLD_LINK = re.compile(
    r"(?<![\w.-])LearnPrompt(?:/|%2f)"
    r"|\bLearnPrompt\.github\.io\b"
    r"|https?://news\.(?:LearnPrompt|Nuos)\.pro\b"
    r"|(?:https?://|git@)?(?:www\.)?github\.com[/:]LearnPrompt(?=[/\s\"'?#)]|$)",
    re.IGNORECASE,
)
MIGRATED_FILES = (
    ".claude-plugin/marketplace.json",
    "README.md",
    "README.en.md",
    "docs/GPT_HANDOFF.md",
    "docs/release-notes-v0.9.md",
    "docs/marketing/bole-skill-promo-draft-2026-05-11.md",
    "docs/marketing/bole-skill-wechat-final-2026-05-11.md",
    "docs/marketing/bole-skill-wechat-final-reordered-2026-05-11.md",
    "skills/radar/README.md",
    "skills/radar/SKILL.md",
    "skills/radar/assets/demo.sh",
    "skills/radar/assets/demo.tape",
    "skills/ai-news-radar/README.md",
    "skills/ai-news-radar/SKILL.md",
    "index.html",
    "classic/index.html",
    "legacy/index.html",
    "scripts/generate_feed.py",
    "tests/service-status.test.mjs",
)
# These literal OLD inputs are essential to recognizing upstream configurations
# and verifying their migration. They are not live links or request targets.
# Cap the known matching lines so unrelated new old-owner links cannot silently
# accumulate in these files. No runtime/news/documentation paths are exempted.
LEGACY_INPUT_LIMITS = {
    "scripts/fork_setup.py": 3,
    "tests/test_fork_setup.py": 2,
}


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
    for name, suffix in (("index.html", "/"), ("classic/index.html", "/classic/"), ("legacy/index.html", "/legacy/")):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert f'rel="canonical" href="{SITE}{suffix}"' in text


def test_repository_has_no_unmigrated_links():
    """Fail CI on remaining active old-owner links, not just emit a warning.

    Scan Git-tracked UTF-8 text only, including generated JSON and archived docs.
    Print counts and line numbers, never contents, credentials or untracked files.
    Run with pytest -s to display the successful inventory as well as failures.
    """
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("A Git checkout is required for the repository-wide inventory")
    remaining = []
    legacy_inputs = []
    scanned = 0
    binary = 0
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
            binary += 1
            continue
        if "\0" in text:
            binary += 1
            continue
        scanned += 1
        lines = [number for number, line in enumerate(text.splitlines(), 1)
                 if OLD_LINK.search(line.replace("\\/", "/"))]
        if not lines:
            continue
        match = {"path": name, "matched_lines": len(lines), "first_lines": lines[:12]}
        if name in LEGACY_INPUT_LIMITS and len(lines) <= LEGACY_INPUT_LIMITS[name]:
            legacy_inputs.append(match)
        else:
            remaining.append(match)
    report = {"scanned_text_files": scanned, "binary_files_skipped": binary,
              "remaining_active_link_files": remaining, "intentional_legacy_inputs": legacy_inputs}
    print("Nuos link migration inventory: " + json.dumps(report, ensure_ascii=False))
    assert not remaining, json.dumps(report, ensure_ascii=False, indent=2)
