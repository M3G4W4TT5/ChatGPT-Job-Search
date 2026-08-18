#!/usr/bin/env python3
"""Validate OpenAI-native repository skills and skills-only plugin metadata."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("lint_skills.py requires PyYAML in a local environment")


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / ".agents" / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FORBIDDEN_RUNTIME_TEXT = {
    "$ARGUMENTS": "slash-command argument variable",
    ".claude/": "Claude runtime path",
    "allowed-tools": "Claude-only frontmatter/tool declaration",
    "WebFetch": "Claude tool name",
    "WebSearch": "Claude tool name",
    "AskUserQuestion": "Claude tool name",
    "Agent tool": "Claude tool name",
    "Read tool": "provider-specific tool name",
    "Write tool": "provider-specific tool name",
    "Edit tool": "provider-specific tool name",
}
RUNTIME_TEXT_SUFFIXES = {".md", ".py", ".ts", ".json", ".yaml", ".yml"}
errors: list[str] = []
BUN_VERSION = "1.3.14"


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_frontmatter(path: Path) -> dict[str, object] | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        errors.append(f"{relative(path)}: missing or malformed YAML frontmatter")
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        errors.append(f"{relative(path)}: invalid YAML: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{relative(path)}: frontmatter must be a mapping")
        return None
    return data


def check_openai_yaml(skill_dir: Path, name: str) -> None:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.is_file():
        errors.append(f"{relative(path)}: missing Desktop metadata")
        return
    raw = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        errors.append(f"{relative(path)}: invalid YAML: {exc}")
        return
    if not isinstance(data, dict) or not isinstance(data.get("interface"), dict):
        errors.append(f"{relative(path)}: interface mapping is required")
        return
    allowed_top = {"interface", "policy"}
    extra_top = set(data) - allowed_top
    if extra_top:
        errors.append(f"{relative(path)}: unsupported top-level keys: {sorted(extra_top)}")
    interface = data["interface"]
    allowed_interface = {"display_name", "short_description", "default_prompt"}
    if set(interface) != allowed_interface:
        errors.append(
            f"{relative(path)}: interface keys must be exactly {sorted(allowed_interface)}"
        )
    for key in allowed_interface:
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{relative(path)}: interface.{key} must be a non-empty string")
        if not re.search(rf"^\s*{re.escape(key)}:\s*\".*\"\s*$", raw, re.MULTILINE):
            errors.append(f"{relative(path)}: interface.{key} must be double-quoted")
    short = interface.get("short_description", "")
    if isinstance(short, str) and not 25 <= len(short) <= 64:
        errors.append(f"{relative(path)}: short_description must be 25-64 characters")
    prompt = interface.get("default_prompt", "")
    if isinstance(prompt, str) and f"${name}" not in prompt:
        errors.append(f"{relative(path)}: default_prompt must mention ${name}")
    policy = data.get("policy")
    if policy is not None:
        if not isinstance(policy, dict) or set(policy) != {"allow_implicit_invocation"}:
            errors.append(f"{relative(path)}: unsupported policy shape")
        elif not isinstance(policy["allow_implicit_invocation"], bool):
            errors.append(f"{relative(path)}: policy flag must be boolean")


def check_skill(skill_dir: Path) -> None:
    path = skill_dir / "SKILL.md"
    data = load_frontmatter(path)
    if data is None:
        return
    if set(data) != {"name", "description"}:
        errors.append(
            f"{relative(path)}: frontmatter keys must be exactly name and description"
        )
    name = data.get("name")
    description = data.get("description")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        errors.append(f"{relative(path)}: invalid kebab-case name")
        return
    if name != skill_dir.name:
        errors.append(f"{relative(path)}: name must match directory {skill_dir.name!r}")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{relative(path)}: description must be a non-empty string")
    elif len(description) > 1024:
        errors.append(f"{relative(path)}: description exceeds 1024 characters")
    for runtime_path in sorted(skill_dir.rglob("*")):
        if (
            not runtime_path.is_file()
            or runtime_path.suffix.lower() not in RUNTIME_TEXT_SUFFIXES
            or "node_modules" in runtime_path.parts
        ):
            continue
        text = runtime_path.read_text(encoding="utf-8")
        for token, label in FORBIDDEN_RUNTIME_TEXT.items():
            if token in text:
                errors.append(
                    f"{relative(runtime_path)}: contains {label}: {token!r}"
                )
        if runtime_path.name == "SKILL.md" and re.search(r"\\\s*$", text, re.MULTILINE):
            errors.append(
                f"{relative(runtime_path)}: contains a Bash line continuation; use PowerShell"
            )
    check_openai_yaml(skill_dir, name)
    manifest = skill_dir / "cli" / "package.json"
    if manifest.is_file():
        try:
            package = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{relative(manifest)}: invalid JSON: {exc}")
        else:
            if package.get("packageManager") != f"bun@{BUN_VERSION}":
                errors.append(f"{relative(manifest)}: packageManager must pin bun@{BUN_VERSION}")
        lockfile = manifest.parent / "bun.lock"
        if not lockfile.is_file():
            errors.append(f"{relative(lockfile)}: required reproducible dependency lockfile is missing")


def check_plugin_manifest() -> None:
    path = ROOT / ".codex-plugin" / "plugin.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f".codex-plugin/plugin.json: {exc}")
        return
    required = {"name", "version", "description", "author", "skills", "interface"}
    if missing := required - set(data):
        errors.append(f".codex-plugin/plugin.json: missing fields {sorted(missing)}")
    if data.get("skills") != "./skills/":
        errors.append(".codex-plugin/plugin.json: skills must be ./skills/")
    if {"apps", "mcpServers", "hooks"}.intersection(data):
        errors.append(".codex-plugin/plugin.json: plugin must remain skills-only")
    version = data.get("version", "")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(".codex-plugin/plugin.json: version must be strict semver")
    interface = data.get("interface")
    if not isinstance(interface, dict) or not interface.get("defaultPrompt"):
        errors.append(".codex-plugin/plugin.json: interface.defaultPrompt is required")


def check_portals(skill_names: set[str]) -> None:
    path = ROOT / "config" / "portals.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"config/portals.json: {exc}")
        return
    portals = data.get("portals") if isinstance(data, dict) else None
    if not isinstance(portals, list):
        errors.append("config/portals.json: portals must be an array")
        return
    configured: list[str] = []
    for index, portal in enumerate(portals):
        if not isinstance(portal, dict):
            errors.append(f"config/portals.json: entry {index} must be an object")
            continue
        name = portal.get("skill")
        if not isinstance(name, str) or name not in skill_names or not name.endswith("-search"):
            errors.append(f"config/portals.json: invalid skill at entry {index}: {name!r}")
        if not isinstance(portal.get("enabled"), bool):
            errors.append(f"config/portals.json: enabled must be boolean at entry {index}")
        configured.append(str(name))
    if len(configured) != len(set(configured)):
        errors.append("config/portals.json: duplicate portal skill")
    discovered = {name for name in skill_names if name.endswith("-search")}
    if set(configured) != discovered:
        errors.append(
            "config/portals.json: configured/discovered portal mismatch: "
            f"configured={sorted(set(configured))}, discovered={sorted(discovered)}"
        )


def check_compatibility(skill_names: set[str]) -> None:
    commands = ROOT / ".claude" / "commands"
    for name in sorted(skill_names - {"job-search-core"}):
        if name.endswith("-search"):
            continue
        path = commands / f"{name}.md"
        if not path.is_file():
            errors.append(f"{relative(path)}: missing compatibility wrapper")
            continue
        text = path.read_text(encoding="utf-8")
        target = f"../../.agents/skills/{name}/SKILL.md"
        if target not in text or "authoritative" not in text:
            errors.append(f"{relative(path)}: wrapper must point to the authoritative native skill")


def main() -> int:
    skill_dirs = sorted(
        path for path in SKILLS_ROOT.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not skill_dirs:
        errors.append("no native skills found under .agents/skills")
    for skill_dir in skill_dirs:
        check_skill(skill_dir)
    names = {path.name for path in skill_dirs}
    check_plugin_manifest()
    check_portals(names)
    check_compatibility(names)
    if errors:
        print(f"lint_skills: {len(errors)} failure(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"lint_skills: OK ({len(skill_dirs)} native skills, plugin metadata, portal registry)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
