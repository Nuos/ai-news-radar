#!/usr/bin/env python3
"""Configure this public fork and verify its deployed snapshot (standard library only)."""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

DEFAULT_SITE = "https://nuos.github.io/ai-news-radar"
DEFAULT_REPOSITORY = "Nuos/ai-news-radar"
CONFIG_PATHS = ("index.html", "classic/index.html", "scripts/generate_feed.py", "skills/radar/SKILL.md")


def normalize_site(value: str) -> str:
    value = value.rstrip("/")
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or any(c in value for c in "\n\r\"'<>")):
        raise ValueError("site URL must be a plain HTTPS URL without credentials, query or fragment")
    return value


def configure(root: Path, site: str, repository: str) -> list[str]:
    site = normalize_site(site)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be owner/name")
    # Validate everything before writing. Do not remove a user's custom domain.
    cname = root / "CNAME"
    if cname.exists() and cname.read_text(encoding="utf-8").strip() not in ("", "news.learnprompt.pro"):
        raise ValueError("custom CNAME detected; review Pages settings before configuring this fork")
    updates: dict[str, str] = {}
    for name in CONFIG_PATHS:
        path = root / name
        original = path.read_text(encoding="utf-8")
        updated = original
        for old in ("https://news.learnprompt.pro", "https://news.Nuos.pro", "https://learnprompt.github.io/ai-news-radar"):
            updated = updated.replace(old, site)
        updated = updated.replace("https://raw.githubusercontent.com/LearnPrompt/ai-news-radar/", f"https://raw.githubusercontent.com/{repository}/")
        if name.endswith("index.html"):
            updated = updated.replace("https://github.com/LearnPrompt/ai-news-radar", f"https://github.com/{repository}")
        if name == "skills/radar/SKILL.md":
            updated, count = re.subn(r"(?m)^BASE_URL=\S+$", f"BASE_URL={site}/data", updated)
            if count != 1:
                raise ValueError("expected exactly one radar BASE_URL setting")
        if updated != original:
            updates[name] = updated
    readme_path = root / "README.md"
    original = readme_path.read_text(encoding="utf-8")
    notice = (
        "<!-- nuos-deployment:start -->\n"
        "> **Nuos 自托管配置**：[打开本站](" + site + "/) · "
        "[运行记录](https://github.com/" + repository + "/actions/workflows/update-news.yml) · "
        "[部署说明](docs/NUOS_DEPLOYMENT.md)。本分支按每小时第 17 分（UTC）更新，"
        "使用公开信源，无 API Key 也可运行。未启用付费源或邮箱；下方保留上游项目说明。\n"
        "<!-- nuos-deployment:end -->\n\n"
    )
    body = re.sub(r"\A<!-- nuos-deployment:start -->.*?<!-- nuos-deployment:end -->\n*", "", original, flags=re.S)
    if notice + body != original:
        updates["README.md"] = notice + body
    for name, text in updates.items():
        (root / name).write_text(text, encoding="utf-8")
    if cname.exists():
        cname.unlink()
    (root / ".nojekyll").touch()
    return sorted(updates)


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("snapshot generated_at must include timezone")
    return result


def verify(root: Path, site: str, attempts: int, delay: float) -> None:
    site = normalize_site(site)
    expected = timestamp(json.loads((root / "data/latest-24h.json").read_text(encoding="utf-8"))["generated_at"])
    endpoints = ("", "classic/", "data/latest-24h.json", "data/daily-brief.json", "data/source-status.json", "data/stories-merged.json", "data/feed.xml")
    last_error = "not attempted"
    for attempt in range(1, attempts + 1):
        try:
            results: dict[str, object] = {}
            for endpoint in endpoints:
                url = f"{site}/{endpoint}?verify={time.time_ns()}"
                request = urllib.request.Request(url, headers={"User-Agent": "ai-news-radar-deployment-check", "Cache-Control": "no-cache"})
                with urllib.request.urlopen(request, timeout=30) as response:
                    if urllib.parse.urlsplit(response.url).netloc != urllib.parse.urlsplit(site).netloc:
                        raise ValueError("unexpected redirect to another host")
                    payload = response.read()
                if endpoint.endswith(".json"):
                    parsed = json.loads(payload)
                    if not isinstance(parsed, dict):
                        raise ValueError(f"{endpoint}: expected JSON object")
                    results[endpoint] = parsed
                elif endpoint.endswith(".xml"):
                    if ET.fromstring(payload).tag != "rss":
                        raise ValueError("feed.xml is not an RSS feed")
                elif b"AI News Radar" not in payload:
                    raise ValueError(f"{endpoint}: missing site title")
            latest = results["data/latest-24h.json"]
            if timestamp(latest["generated_at"]) < expected:
                raise ValueError("Pages still serves the previous snapshot")
            if int(latest.get("total_items", 0)) <= 0:
                raise ValueError("deployed snapshot is empty")
            report = {
                "site": site + "/", "checked_endpoints": len(endpoints),
                "generated_at": latest["generated_at"], "total_items": latest.get("total_items"),
                "source_count": latest.get("source_count"),
                "successful_sites": results["data/source-status.json"].get("successful_sites"),
                "failed_sites": results["data/source-status.json"].get("failed_sites"),
            }
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            print(f"Deployment check {attempt}/{attempts}: {last_error}")
            if attempt < attempts:
                time.sleep(delay)
    raise SystemExit(f"Deployment was not verified: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("configure", "verify"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--site-url", default=DEFAULT_SITE)
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--attempts", type=int, default=18)
    parser.add_argument("--delay", type=float, default=10)
    args = parser.parse_args()
    if args.attempts < 1 or args.delay < 0:
        parser.error("attempts must be positive and delay must be nonnegative")
    if args.command == "configure":
        print("Configured fork files:", ", ".join(configure(args.root, args.site_url, args.repository)) or "already configured")
    else:
        verify(args.root, args.site_url, args.attempts, args.delay)


if __name__ == "__main__":
    main()
