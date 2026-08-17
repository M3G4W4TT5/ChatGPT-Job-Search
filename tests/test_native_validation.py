import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]


class NativeValidators(unittest.TestCase):
    def run_tool(self, name: str):
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_skill_linter_passes_repository(self):
        result = self.run_tool("lint_skills.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("21 native skills", result.stdout)

    def test_security_guard_passes_repository(self):
        result = self.run_tool("security_guards.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("privacy", result.stdout)

    def test_environment_check_is_valid_json_and_read_only(self):
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "tools" / "check_environment.ps1"),
                "-Json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["expected_origin"], "https://github.com/M3G4W4TT5/ChatGPT-Job-Search.git")
        self.assertEqual(data["expected_upstream"], "https://github.com/MadsLorentzen/ai-job-search.git")
        if data["origin"] is not None:
            self.assertTrue(data["origin_configured"])
        if data["upstream"] is not None:
            self.assertTrue(data["upstream_configured"])
        self.assertEqual({tool["name"] for tool in data["tools"]}, {
            "git", "python", "bun", "lualatex", "xelatex", "pdfinfo", "pdftotext", "pdftoppm"
        })


class PluginPackaging(unittest.TestCase):
    def setUp(self):
        self.output = ROOT / "dist" / "test-plugin-package"
        self.sentinel = (
            ROOT
            / ".agents"
            / "skills"
            / "apply"
            / f".env.codex-package-test-{uuid4().hex}"
        )
        shutil.rmtree(self.output, ignore_errors=True)
        if self.sentinel.exists():
            self.fail(f"refusing to overwrite existing sentinel path: {self.sentinel}")
        self.sentinel.write_text("PACKAGE_SENTINEL=must_not_ship\n", encoding="utf-8")
        self.addCleanup(shutil.rmtree, self.output, True)
        self.addCleanup(self.sentinel.unlink, missing_ok=True)

    def test_package_contains_skills_and_no_private_state(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "package_plugin.py"), "--output", "dist/test-plugin-package"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("assembled 21 skills", result.stdout)
        manifest = json.loads(
            (self.output / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertFalse({"apps", "mcpServers", "hooks"}.intersection(manifest))
        self.assertTrue((self.output / "AGENTS.md").is_file())
        self.assertTrue((self.output / "config" / "portals.json").is_file())
        self.assertTrue((self.output / "cv" / "main_example.tex").is_file())
        self.assertTrue((self.output / "cover_letters" / "cover_example.tex").is_file())
        self.assertTrue((self.output / "skills" / "apply" / "SKILL.md").is_file())
        packaged_skills = [path for path in (self.output / "skills").iterdir() if path.is_dir()]
        self.assertEqual(len(packaged_skills), 21)
        for skill in packaged_skills:
            self.assertTrue((skill / "agents" / "openai.yaml").is_file(), skill.name)
        self.assertIn("Mads Lorentzen", (self.output / "README.md").read_text(encoding="utf-8"))
        self.assertFalse(list(self.output.rglob(".env*")))
        self.assertFalse(list(self.output.rglob("*.pdf")))
        self.assertFalse(list(self.output.rglob("*.aux")))
        self.assertFalse(list(self.output.rglob("*.out")))
        self.assertFalse(list(self.output.rglob("bun.lock")))
        for private in ("profile", "documents", "job_scraper", "reports", "salary_data.json"):
            self.assertFalse((self.output / private).exists())


if __name__ == "__main__":
    unittest.main()
