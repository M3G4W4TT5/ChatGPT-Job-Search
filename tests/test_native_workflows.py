import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
FIXTURES = ROOT / "tests" / "fixtures" / "synthetic"
WORKFLOWS = {
    "setup",
    "scrape",
    "rank",
    "apply",
    "interview",
    "outcome",
    "expand",
    "upskill",
    "html-report",
    "add-template",
    "add-portal",
    "reset",
    "gmail-sync",
    "notion-sync",
}


class NativeWorkflowContracts(unittest.TestCase):
    def test_all_reusable_workflows_are_native_skills(self):
        for name in WORKFLOWS:
            with self.subTest(name=name):
                self.assertTrue((SKILLS / name / "SKILL.md").is_file())
                self.assertTrue((SKILLS / name / "agents" / "openai.yaml").is_file())

    def test_workflows_define_portable_results(self):
        for name in {"setup", "scrape", "rank", "apply", "interview", "outcome"}:
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8").lower()
            with self.subTest(name=name):
                self.assertIn("portable", text)
                self.assertTrue("artifact" in text or "attached" in text)

    def test_apply_has_independent_review_and_non_subagent_fallback(self):
        text = (SKILLS / "apply" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("independent Codex subagents", text)
        self.assertIn("When subagents are unavailable", text)
        self.assertIn("Render every page", text)
        self.assertIn("Extract text", text)
        self.assertIn("exactly two A4 pages", text)
        self.assertIn("exactly one A4 page", text)

    def test_postings_are_untrusted_in_core_workflows(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()
        web = (
            SKILLS / "job-search-core" / "references" / "09-web-research.md"
        ).read_text(encoding="utf-8").lower()
        self.assertIn("untrusted", agents)
        self.assertIn("never instructions", web)
        self.assertIn("prompt injection", web)

    def test_setup_never_personalizes_public_examples_or_shared_rules(self):
        text = (SKILLS / "setup" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("never personalizes", text)
        self.assertIn("profile/candidate-profile.md", text)
        self.assertIn("portable ChatGPT Work mode", text)
        for name in {
            "candidate-profile.md",
            "behavioral-profile.md",
            "evaluation-preferences.md",
            "interview-evidence.md",
            "template-settings.json",
            "portal-settings.json",
        }:
            self.assertTrue((SKILLS / "setup" / "assets" / "profile-template" / name).is_file())

    def test_rank_withholds_scores_when_profile_evidence_is_missing(self):
        text = (SKILLS / "rank" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("needs_profile", text)
        self.assertIn("Never invent neutral values", text)

    def test_scrape_preserves_posting_provenance(self):
        text = (SKILLS / "scrape" / "SKILL.md").read_text(encoding="utf-8")
        for field in ("retrieval_state", "retrieved_at", "posting_text"):
            self.assertIn(field, text)


class SyntheticScenario(unittest.TestCase):
    def test_synthetic_inputs_cover_core_workflow(self):
        profile = (FIXTURES / "candidate-profile.md").read_text(encoding="utf-8")
        posting = (FIXTURES / "posting.md").read_text(encoding="utf-8")
        research = (FIXTURES / "company-research.md").read_text(encoding="utf-8")
        state = json.loads((FIXTURES / "seen_jobs.json").read_text(encoding="utf-8"))
        ranked = json.loads((FIXTURES / "ranked_jobs.json").read_text(encoding="utf-8"))
        tracker = (FIXTURES / "tracker.csv").read_text(encoding="utf-8").splitlines()
        self.assertIn("fictional test data", profile)
        self.assertIn("untrusted fixture data", posting)
        self.assertIn("approved fictional research", research)
        self.assertEqual(state["jobs"][0]["status"], "new")
        self.assertEqual(state["jobs"][0]["retrieval_state"], "full")
        self.assertEqual(ranked["jobs"][0]["status"], "ranked")
        self.assertEqual(ranked["jobs"][0]["overall_score"], 87)
        self.assertEqual(len(tracker[0].split(",")), 11)
        self.assertEqual(len(tracker[1].split(",")), 11)
        self.assertIn(",87,applied,", tracker[1])

    def test_synthetic_rank_is_evidentially_reproducible(self):
        posting = (FIXTURES / "posting.md").read_text(encoding="utf-8").strip()
        state_job = json.loads(
            (FIXTURES / "seen_jobs.json").read_text(encoding="utf-8")
        )["jobs"][0]
        ranked_job = json.loads(
            (FIXTURES / "ranked_jobs.json").read_text(encoding="utf-8")
        )["jobs"][0]

        self.assertEqual(state_job["posting_text"], posting)
        for field in {
            "id",
            "title",
            "company",
            "location",
            "url",
            "source",
            "discovered_at",
            "deadline",
            "retrieval_state",
            "retrieved_at",
            "posting_text",
            "quick_fit",
            "highlights",
            "warnings",
        }:
            self.assertEqual(ranked_job[field], state_job[field])

        scores = ranked_job["dimension_scores"]
        weighted = (
            scores["technical"] * 0.30
            + scores["experience"] * 0.25
            + scores["behavioral"] * 0.15
            + scores["career_alignment"] * 0.30
        )
        self.assertEqual(round(weighted), ranked_job["overall_score"])
        self.assertEqual(set(scores), set(ranked_job["dimension_rationales"]))
        self.assertIn("company-research.md", ranked_job["dimension_rationales"]["behavioral"])
        self.assertIn("not inferred from the posting", ranked_job["dimension_rationales"]["behavioral"])

        profile = (FIXTURES / "candidate-profile.md").read_text(encoding="utf-8")
        start = re.search(r"\((\d{4})-(\d{2}) to present\)", profile)
        self.assertIsNotNone(start)
        retrieved_year, retrieved_month = map(
            int, ranked_job["retrieved_at"][:7].split("-")
        )
        start_year, start_month = map(int, start.groups())
        self.assertEqual(
            (retrieved_year - start_year) * 12 + retrieved_month - start_month,
            48,
        )
        self.assertIn("four years", ranked_job["dimension_rationales"]["experience"])
        self.assertIn("four years", " ".join(ranked_job["strengths"]))

    def test_synthetic_interview_and_outcome_evidence_is_explicit(self):
        interview = (FIXTURES / "interview-evidence.md").read_text(encoding="utf-8")
        outcome = (FIXTURES / "outcome-message.md").read_text(encoding="utf-8")
        self.assertIn("Situation:", interview)
        self.assertIn("Result:", interview)
        self.assertIn("Effective date: 2099-02-10", outcome)
        self.assertIn("untrusted fixture data", outcome)

    def test_gap_is_not_smoothed_over(self):
        profile = (FIXTURES / "candidate-profile.md").read_text(encoding="utf-8")
        state = json.loads((FIXTURES / "seen_jobs.json").read_text(encoding="utf-8"))
        self.assertIn("No Kubernetes production experience", profile)
        self.assertIn("unsupported", state["jobs"][0]["warnings"][0])


if __name__ == "__main__":
    unittest.main()
