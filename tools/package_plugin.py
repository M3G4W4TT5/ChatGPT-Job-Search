"""Assemble the tracked native skills into an OpenAI skills-only plugin bundle."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/ai-job-search"),
        help="new or empty output directory (default: dist/ai-job-search)",
    )
    return parser.parse_args()


def copy_tracked_tree(repo: Path, relative_source: Path, destination: Path) -> None:
    """Copy only git-tracked files from a public support directory."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", relative_source.as_posix()],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    prefix = repo / relative_source
    for raw_name in result.stdout.split(b"\0"):
        if not raw_name:
            continue
        source = repo / raw_name.decode("utf-8")
        if source.is_symlink():
            raise RuntimeError(f"refusing packaged symlink: {source.relative_to(repo)}")
        target = destination / source.relative_to(prefix)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source_skills = repo / ".agents" / "skills"
    manifest = repo / ".codex-plugin" / "plugin.json"
    output = (repo / parse_args().output).resolve()

    if not source_skills.is_dir() or not manifest.is_file():
        print("missing native skills or plugin manifest", file=sys.stderr)
        return 2

    if output == repo or repo not in output.parents:
        print("output must be a directory inside the repository", file=sys.stderr)
        return 2
    if output.exists() and any(output.iterdir()):
        print(f"output is not empty: {output}", file=sys.stderr)
        return 2

    data = json.loads(manifest.read_text(encoding="utf-8"))
    forbidden = {"apps", "mcpServers", "hooks"}.intersection(data)
    if forbidden:
        print(f"skills-only manifest contains forbidden components: {sorted(forbidden)}", file=sys.stderr)
        return 2
    if data.get("skills") != "./skills/":
        print("plugin manifest must use ./skills/", file=sys.stderr)
        return 2

    output.mkdir(parents=True, exist_ok=True)
    (output / ".codex-plugin").mkdir()
    shutil.copy2(manifest, output / ".codex-plugin" / "plugin.json")
    for filename in ("AGENTS.md", "LICENSE"):
        shutil.copy2(repo / filename, output / filename)
    shutil.copy2(repo / "PLUGIN_README.md", output / "README.md")
    (output / "config").mkdir()
    shutil.copy2(repo / "config" / "portals.json", output / "config" / "portals.json")
    (output / "cv").mkdir()
    shutil.copy2(repo / "cv" / "main_example.tex", output / "cv" / "main_example.tex")
    (output / "cover_letters").mkdir()
    for filename in ("cover_example.tex", "cover.cls"):
        shutil.copy2(repo / "cover_letters" / filename, output / "cover_letters" / filename)
    copy_tracked_tree(
        repo,
        Path("cover_letters/OpenFonts"),
        output / "cover_letters" / "OpenFonts",
    )
    copy_tracked_tree(repo, Path(".agents/skills"), output / "skills")

    skill_count = sum(1 for path in (output / "skills").iterdir() if (path / "SKILL.md").is_file())
    print(f"assembled {skill_count} skills at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
