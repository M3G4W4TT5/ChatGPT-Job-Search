#!/usr/bin/env python3
"""Guard public/private boundaries and executable package surfaces."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
FORBIDDEN_SCRIPTS = {"preinstall", "install", "postinstall", "prepare", "prepack"}
REQUIRED_IGNORE_RULES = {
    "profile/**",
    "!profile/.gitkeep",
    "salary_data.json",
    "/job_scraper/",
    "*_BehavioralReport.pdf",
    "linkedin_Profile.pdf",
    "cv/main_*.*",
    "!cv/main_example.tex",
    "cv/*.txt",
    "cover_letters/cover_*.*",
    "cover_letters/Cover_*.*",
    "documents/**",
    "!documents/README.md",
    "!documents/**/",
    "job_search_tracker.csv",
    "/gmail_sync/",
    "/reports/",
    "/upskill/",
    ".env",
    ".env.*",
    "/dist/",
}
ALLOWED_NEGATIONS = {
    "!profile/.gitkeep",
    "!cover_letters/OpenFonts/fonts/**",
    "!cv/main_example.tex",
    "!cover_letters/cover_example.tex",
    "!documents/README.md",
    "!documents/**/",
    "!documents/**/.gitkeep",
}
PRIVATE_TRACKED_PREFIXES = {
    "profile/": {"profile/.gitkeep"},
    "documents/": {
        "documents/README.md",
        "documents/applications/.gitkeep",
        "documents/cv/.gitkeep",
        "documents/diplomas/.gitkeep",
        "documents/linkedin/.gitkeep",
        "documents/postings/.gitkeep",
        "documents/references/.gitkeep",
    },
    "job_scraper/": {"job_scraper/.gitkeep"},
    "gmail_sync/": set(),
    "reports/": set(),
    "upskill/": {"upskill/.gitkeep"},
}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "OpenAI key": re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}"),
}


def public_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    if result.returncode:
        errors.append(f"git public-file inventory failed: {result.stderr.strip()}")
        return []
    return [line for line in result.stdout.splitlines() if line]


def check_authority_and_plugin() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    required = [
        ".agents/skills/",
        "untrusted",
        "never fabricate",
        "Portable Work mode",
        "independent",
    ]
    for phrase in required:
        if phrase.lower() not in agents.lower():
            errors.append(f"AGENTS.md: missing authority/safety phrase {phrase!r}")
    if (ROOT / ".claude" / "settings.json").exists():
        errors.append(".claude/settings.json: pre-approved provider permissions are forbidden")
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    forbidden = {"apps", "mcpServers", "hooks"}.intersection(manifest)
    if forbidden:
        errors.append(f"plugin manifest must remain skills-only: {sorted(forbidden)}")


def check_gitignore() -> None:
    lines = [line.strip() for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()]
    rules = set(lines)
    for rule in sorted(REQUIRED_IGNORE_RULES - rules):
        errors.append(f".gitignore: required private-data rule missing: {rule!r}")
    for line in lines:
        if line.startswith("!") and line not in ALLOWED_NEGATIONS:
            errors.append(f".gitignore: unreviewed re-include rule: {line!r}")

    probes = [
        "profile/candidate-profile.md",
        "salary_data.json",
        "job_search_tracker.csv",
        "documents/cv/private.pdf",
        "documents/applications/example/outcome.md",
        "documents/resume.docx",
        "job_scraper/results.json",
        "reports/private.html",
        "upskill/private.json",
        "dist/chatgpt-job-search/skills/setup/SKILL.md",
    ]
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", *probes],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    ignored = set(result.stdout.splitlines())
    for probe in probes:
        if probe not in ignored:
            errors.append(f".gitignore: private probe is not ignored: {probe}")

    public_probe = ".agents/skills/upskill/agents/openai.yaml"
    public_result = subprocess.run(
        ["git", "check-ignore", "--no-index", public_probe],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    if public_result.returncode == 0:
        errors.append(f".gitignore: native public metadata is ignored: {public_probe}")


def check_tracked_private_data(tracked: list[str]) -> None:
    for path in tracked:
        normalized = path.replace("\\", "/")
        for prefix, allowed in PRIVATE_TRACKED_PREFIXES.items():
            if normalized.startswith(prefix) and normalized not in allowed:
                errors.append(f"tracked private-path content: {normalized}")
    forbidden_exact = {
        "job_search_tracker.csv",
        "salary_data.json",
        "gmail_sync.json",
    }
    for path in forbidden_exact.intersection(tracked):
        errors.append(f"tracked private file: {path}")

    for path in tracked:
        normalized = path.replace("\\", "/")
        if normalized.startswith("cv/") and normalized != "cv/main_example.tex":
            errors.append(f"tracked generated CV content: {normalized}")
        if normalized.startswith("cover_letters/"):
            allowed = normalized in {
                "cover_letters/cover.cls",
                "cover_letters/cover_example.tex",
            } or normalized.startswith("cover_letters/OpenFonts/fonts/")
            if not allowed:
                errors.append(f"tracked generated cover-letter content: {normalized}")


def check_manifests() -> None:
    manifests = [
        path for path in ROOT.glob(".agents/**/package.json") if "node_modules" not in path.parts
    ]
    if not manifests:
        errors.append("no portal CLI package manifests found")
    for path in manifests:
        rel = path.relative_to(ROOT).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{rel}: invalid JSON: {exc}")
            continue
        scripts = data.get("scripts", {}) if isinstance(data, dict) else {}
        if not isinstance(scripts, dict):
            errors.append(f"{rel}: scripts must be an object")
            continue
        if bad := FORBIDDEN_SCRIPTS.intersection(scripts):
            errors.append(f"{rel}: forbidden lifecycle scripts: {sorted(bad)}")
        if "trustedDependencies" in data:
            errors.append(f"{rel}: trustedDependencies is forbidden")


def check_access_boundaries(public: list[str]) -> None:
    portals = json.loads((ROOT / "config" / "portals.json").read_text(encoding="utf-8"))[
        "portals"
    ]
    linkedin = next((item for item in portals if item.get("skill") == "linkedin-search"), None)
    if not linkedin or linkedin.get("enabled") is not False:
        errors.append("config/portals.json: linkedin-search must remain disabled")
    linkedin_dir = ROOT / ".agents" / "skills" / "linkedin-search"
    if any(path.startswith(".agents/skills/linkedin-search/cli/") for path in public):
        errors.append("linkedin-search: automated CLI is forbidden")
    linkedin_text = "\n".join(
        path.read_text(encoding="utf-8") for path in linkedin_dir.rglob("*.md")
    )
    if (
        "jobs-guest" in linkedin_text
        or "Do not run automated LinkedIn scraping" not in linkedin_text
        or "user-controlled" not in linkedin_text
    ):
        errors.append("linkedin-search: missing user-controlled access boundary")

    for path in ROOT.glob(".agents/skills/*-search/cli/src/**/*.ts"):
        if "node_modules" in path.parts:
            continue
        if "Mozilla/5.0" in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(ROOT).as_posix()}: impersonating user agent")


def check_secrets(tracked: list[str]) -> None:
    for name in tracked:
        path = ROOT / name
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{name}: possible {label}")


def check_licence() -> None:
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "MIT License" not in text or "Copyright (c) 2026 Mads Lorentzen" not in text:
        errors.append("LICENSE: original MIT licence or copyright notice changed")


def main() -> int:
    tracked = public_files()
    check_authority_and_plugin()
    check_gitignore()
    check_tracked_private_data(tracked)
    check_manifests()
    check_access_boundaries(tracked)
    check_secrets(tracked)
    check_licence()
    if errors:
        print(f"security_guards: {len(errors)} failure(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("security_guards: OK (authority, privacy, manifest, lifecycle, secret, licence guards)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
