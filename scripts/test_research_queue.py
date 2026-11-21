"""Offline regression checks for persistent research review and change handling."""

from copy import deepcopy
from datetime import datetime, timedelta, UTC
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from research_queue import (canonical_url, marker, marker_ids, merge_review_state,
                            pending_records, reconcile_queue, record_review, update_queue)

spec = importlib.util.spec_from_file_location("research_review", Path(__file__).with_name("prepare-research-review.py"))
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)

NOW = "2026-11-21T09:00:00+00:00"
LATER = "2026-12-05T09:00:00+00:00"
PAPER = "https://arxiv.org/abs/2611.14815"
PROJECT = "https://research.nvidia.com/labs/sil/projects/birddreams/"
REPO = "https://github.com/NVIDIA/example-world-model"


def observation(url=PAPER, **extra):
    return {"id": "2611.14815", "title": "BirdDreams: A Driving World Model", "url": url,
            "date": "2026-11-10T23:04:58+00:00", "revision": "v1",
            "detail": "public paper", "source": "arXiv cs.CV", **extra}


def paper_page(title="BirdDreams: A Driving World Model"):
    return f'<meta name="citation_title" content="{title}"><a title="Rights to this article" href="https://creativecommons.org/licenses/by/4.0/">license</a>'


class QueueTests(unittest.TestCase):
    def test_source_recency_does_not_override_different_first_seen_times(self):
        base = "https://github.com/NVIDIA/IsaacAutomator/releases/tag/"
        q = update_queue({}, [observation(base + "v4.6.0", date="2026-09-01T00:00:00+00:00")],
                         "2026-11-14T09:00:00+00:00")
        q = update_queue(q, [observation(base + "v4.6.6", date="2026-10-27T00:00:00+00:00")], NOW)
        self.assertEqual([record["url"].rsplit("/", 1)[-1] for record in pending_records(q, NOW)],
                         ["v4.6.0", "v4.6.6"])

    def test_unselected_candidate_survives_recent_window(self):
        q = update_queue({}, [observation()], NOW)
        q = update_queue(q, [], LATER)
        self.assertEqual(len(pending_records(q, LATER)), 1)
        self.assertEqual(next(iter(q["projects"].values()))["first_seen"], NOW)

    def test_poll_dates_do_not_create_semantic_changes(self):
        q = update_queue({}, [observation()], NOW)
        q = update_queue(q, [observation(date=LATER, detected=LATER, detail="another feed wording")], LATER)
        self.assertEqual(len(q["events"]), 1)
        self.assertEqual(next(iter(q["events"].values()))["last_seen"], LATER)

    def test_revision_license_and_access_changes_remain_reviewable(self):
        item = observation("https://huggingface.co/nvidia/example-world-model", revision="a" * 40,
                           license="apache-2.0", gated=False)
        q = update_queue({}, [item], NOW)
        first = pending_records(q, NOW)[0]
        record_review(q, first, "merged", NOW)
        changed = {**item, "gated": "manual", "license": "other", "revision": "b" * 40}
        q = update_queue(q, [changed], LATER)
        records = pending_records(q, LATER)
        self.assertEqual(len(q["events"]), 2)
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0]["_update"])
        self.assertIn("license", records[0]["_change_reasons"][0])

    def test_paper_project_and_hf_paper_are_one_project(self):
        q = update_queue({}, [observation("https://huggingface.co/papers/2611.14815", related_urls=[PROJECT]),
                              observation(PROJECT, related_urls=[PAPER])], NOW)
        self.assertEqual(set(q["projects"]), {"arxiv:2611.14815"})
        records = pending_records(q, NOW)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["url"], PROJECT)
        self.assertEqual(len(records[0]["_event_ids"]), 2)

    def test_author_link_keeps_artifact_provenance_without_fusing_identity(self):
        q = update_queue({}, [observation(REPO, revision="a" * 40)], NOW)
        q = update_queue(q, [observation(PROJECT, related_urls=[PAPER, REPO])], LATER)
        self.assertEqual(set(q["projects"]), {"github:nvidia/example-world-model", "arxiv:2611.14815"})
        self.assertEqual(len(q["events"]), 2)
        self.assertIn(REPO, q["projects"]["arxiv:2611.14815"]["urls"])

    def test_different_papers_sharing_a_dependency_remain_separate(self):
        second = "https://arxiv.org/abs/2611.15000"
        q = update_queue({}, [observation(related_urls=[REPO], model_urls=["https://huggingface.co/nvidia/common-model"]),
                              observation(second, related_urls=[REPO], model_urls=["https://huggingface.co/nvidia/common-model"])], NOW)
        self.assertEqual(len(q["projects"]), 2)
        self.assertEqual(len(pending_records(q, NOW)), 2)

    def test_comparison_paper_cannot_override_primary_paper_identity(self):
        second = "https://arxiv.org/abs/2611.15000"
        q = update_queue({}, [observation(), observation(second, related_urls=[PAPER, PROJECT])], NOW)
        self.assertEqual(len(q["projects"]), 2)
        self.assertEqual(len(pending_records(q, NOW)), 2)

    def test_old_lab_snapshot_only_queues_a_later_semantic_change(self):
        old = observation(PROJECT, discovery_eligible=False, revision="old-links")
        q = update_queue({}, [old], NOW)
        self.assertEqual(len(q["events"]), 0)
        q = update_queue(q, [old], LATER)
        self.assertEqual(len(q["events"]), 0)
        q = update_queue(q, [{**old, "code_urls": [REPO], "revision": "code-added"}], LATER)
        self.assertEqual(len(pending_records(q, LATER)), 1)

    def test_rejected_pr_stays_rejected_but_new_revision_is_pending(self):
        q = update_queue({}, [observation()], NOW)
        eid = next(iter(q["events"]))
        reviews = [{"state": "CLOSED", "mergedAt": None, "body": marker([eid])}]
        reconcile_queue(q, [], [], reviews, NOW)
        self.assertEqual(q["events"][eid]["status"], "rejected")
        q = update_queue(q, [observation(revision="v2")], LATER)
        reconcile_queue(q, [], [], reviews, LATER)
        self.assertEqual(len(pending_records(q, LATER)), 1)
        self.assertEqual(q["events"][eid]["status"], "rejected")

    def test_new_change_waits_for_open_review_and_unblocks_on_merge(self):
        q = update_queue({}, [observation()], NOW)
        old_id = next(iter(q["events"]))
        q = update_queue(q, [observation(revision="v2")], LATER)
        pending = [f'| [paper]({PAPER}) | {marker([old_id])} |']
        reconcile_queue(q, [], pending, [{"state": "OPEN", "body": marker([old_id])}], LATER)
        newer = [e for e in q["events"].values() if e["id"] != old_id][0]
        self.assertTrue(newer["blocked_by_review"])
        self.assertEqual(pending_records(q, LATER), [])
        reconcile_queue(q, pending, [], [{"state": "MERGED", "body": marker([old_id])}], LATER)
        self.assertEqual(len(pending_records(q, LATER)), 1)
        self.assertTrue(pending_records(q, LATER)[0]["_update"])

    def test_baseline_link_is_not_a_permanent_url_exclusion(self):
        q = update_queue({}, [observation()], NOW)
        known = [f'[existing paper]({PAPER})']
        reconcile_queue(q, known, [], [], NOW)
        self.assertEqual(pending_records(q, NOW), [])
        q = update_queue(q, [observation(revision="v2")], LATER)
        reconcile_queue(q, known, [], [], LATER)
        self.assertEqual(len(pending_records(q, LATER)), 1)

    def test_published_project_alias_does_not_hide_new_code(self):
        q = update_queue({}, [observation(related_urls=[PROJECT])], NOW)
        contents = [f'[paper]({PAPER}) [project]({PROJECT})']
        reconcile_queue(q, contents, [], [], NOW)
        q = update_queue(q, [observation(PROJECT, related_urls=[PAPER], code_urls=[REPO], revision="code-added")], LATER)
        reconcile_queue(q, contents, [], [], LATER)
        self.assertEqual(len(pending_records(q, LATER)), 1)
        self.assertIn(REPO, pending_records(q, LATER)[0]["_urls"])

    def test_stale_overlay_preserves_newer_observation_and_source_health(self):
        q = update_queue({}, [observation()], NOW)
        record = pending_records(q, NOW)[0]
        overlay = {"queue": deepcopy(q)}
        record_review(overlay["queue"], record, "proposed", NOW)
        current = {"checked": LATER, "sources": {"live": {"error": None}},
                   "queue": update_queue(q, [observation(revision="v2")], LATER)}
        combined = merge_review_state(current, overlay)
        self.assertEqual(combined["checked"], LATER)
        self.assertEqual(combined["sources"], current["sources"])
        self.assertEqual(len(combined["queue"]["events"]), 2)
        self.assertEqual(len(pending_records(combined["queue"], LATER)), 1)

    def test_older_decision_cannot_overwrite_newer_rejection(self):
        q = update_queue({}, [observation()], NOW)
        seed = pending_records(q, NOW)[0]
        old = deepcopy(q)
        record_review(old, seed, "proposed", NOW)
        record_review(q, seed, "rejected", LATER)
        result = merge_review_state({"queue": q}, {"queue": old})
        self.assertEqual(next(iter(result["queue"]["events"].values()))["status"], "rejected")


class ReviewTests(unittest.TestCase):
    def test_same_discovery_batch_selects_newest_releases_before_lexical_oldest(self):
        base = "https://github.com/NVIDIA/IsaacAutomator/releases/tag/"
        observations = [observation(base + f"v4.6.{i}", id=str(i), revision=f"v4.6.{i}",
                                    date=f"2026-10-{21 + i:02d}T09:00:00+00:00") for i in range(7)]
        q = update_queue({}, observations, NOW)
        def release(url):
            return {"kind": "release", "url": url, "title": url.rsplit("/", 1)[-1],
                    "prerelease": False, "terms": "MIT", "license": REPO + "/LICENSE", "date": "2026-10-27"}
        with patch.object(review, "verify_release", side_effect=release):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual([record["title"] for record in selected], [f"v4.6.{i}" for i in (6, 5, 4, 3)])
        self.assertEqual(len(pending_records(q, NOW)), 3)

    def test_real_hero_heading_adjacent_name_and_subtitle_spans_keep_word_boundary(self):
        page = review.Page('<h1 id="project-title"><span class="project-name">BirdDreams</span>'
                           '<span class="project-subtitle">A driving world model with '
                           '<span class="keep-phrase">precise ego control</span></span></h1>')
        self.assertEqual(page.heading, "BirdDreams A driving world model with precise ego control")

    def test_no_proposal_still_writes_body_and_decision_overlay(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            catalogs = []
            for lang in ("en", "ko"):
                path = root / f"catalog-{lang}.md"
                path.write_text("")
                catalogs.append((str(path), str(root / f"archive-{lang}.md")))
            state = root / "state.json"
            state.write_text(json.dumps({"checked": NOW, "recent": []}))
            pending = root / "pending"
            pending.mkdir()
            body = root / "body.md"
            args = ["prepare-research-review.py", "--state", str(state), "--pending", str(pending), "--body", str(body)]
            with patch.object(sys, "argv", args), patch.object(review, "PATHS", tuple(catalogs)), \
                    patch.object(review, "request", side_effect=AssertionError("unexpected network request")):
                review.main()
            self.assertIn("0 candidates", body.read_text())
            self.assertEqual(json.loads((root / "review-state.json").read_text())["queue"]["events"], {})

    def test_paper_only_guide_does_not_inherit_paper_license_for_weights(self):
        q = update_queue({}, [observation()], NOW)
        state = {"checked": NOW, "queue": q}
        with patch.object(review, "request", return_value=paper_page()):
            selected = review.candidates(state, set(), q)
        self.assertEqual(len(selected), 1)
        en, ko = (review.render(selected[0], lang) for lang in (0, 1))
        self.assertIn("CC BY 4.0", en)
        self.assertIn("Weight availability unverified", en)
        self.assertIn("가중치 공개 여부 미확인", ko)
        self.assertEqual(marker_ids([en]), marker_ids([ko]))
        self.assertEqual(selected[0]["provenance"]["discovery_url"], PAPER)

    def test_weekly_limit_keeps_unselected_tail_for_later(self):
        observations = [observation(f"https://arxiv.org/abs/2611.{14815 + i}", id=str(i)) for i in range(6)]
        q = update_queue({}, observations, NOW)
        with patch.object(review, "request", return_value=paper_page()):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual(len(selected), 4)
        self.assertEqual(len(pending_records(q, LATER)), 2)

    def test_full_research_quota_does_not_starve_a_later_repo(self):
        observations = [observation(f"https://arxiv.org/abs/2611.{14815 + i}", id=str(i)) for i in range(40)]
        observations.append(observation(REPO))
        q = update_queue({}, observations, NOW)
        repo = {"kind": "repo", "url": REPO, "title": "Example policy", "topic": ("World models", "월드 모델"),
                "terms": "MIT", "license": REPO + "/blob/" + "a" * 40 + "/LICENSE", "revision": "a" * 40,
                "date": "2026-11-20"}
        with patch.object(review, "request", return_value=paper_page()), patch.object(review, "verify_repo", return_value=repo):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual(sum(item["kind"] == "research" for item in selected), 4)
        self.assertEqual(sum(item["kind"] == "repo" for item in selected), 1)

    def test_new_nvidia_project_is_selected_ahead_of_older_nonofficial_papers(self):
        old = [observation(f"https://arxiv.org/abs/2611.{10000 + i}", title="Old Driving World Model", id=str(i))
               for i in range(4)]
        q = update_queue({}, old, "2026-11-14T09:00:00+00:00")
        q = update_queue(q, [observation(related_urls=[PROJECT])], NOW)
        self.assertEqual(pending_records(q, NOW)[0]["url"], PAPER)
        def source(url, json_response=True):
            if url == PROJECT:
                return f'<h1>BirdDreams: A Driving World Model</h1><a href="{PAPER}">Paper</a>'
            return paper_page("BirdDreams: A Driving World Model" if url == PAPER else "Old Driving World Model")
        with patch.object(review, "request", side_effect=source):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual(len(selected), 4)
        self.assertIn(PAPER, [record["url"] for record in selected])
        remaining = pending_records(q, NOW)
        self.assertEqual(len(remaining), 1)
        self.assertIn(remaining[0]["url"], [record["url"] for record in old])

    def test_nonallowlisted_license_change_has_pinned_manual_review_evidence(self):
        q = update_queue({}, [observation(REPO, revision="a" * 40)], NOW)
        record_review(q, pending_records(q, NOW)[0], "merged", NOW)
        q = update_queue(q, [observation(REPO, revision="b" * 40, detail="license changed")], LATER)
        def upstream(url, json_response=True):
            if url.endswith("/commits/main"):
                return {"sha": "b" * 40, "commit": {"committer": {"date": LATER}}}
            if url.endswith("/license?ref=" + "b" * 40):
                return {"license": {"spdx_id": "LicenseRef-Custom"}, "path": "LICENSE"}
            if "raw.githubusercontent.com" in url:
                return "Custom terms"
            return {"private": False, "archived": False, "fork": False, "full_name": "NVIDIA/example-world-model",
                    "description": "World model", "default_branch": "main", "html_url": REPO}
        with patch.object(review, "request", side_effect=upstream):
            selected = review.candidates({"checked": LATER}, {canonical_url(REPO)}, q)
        self.assertEqual(selected, [])
        deferred = [event for event in q["events"].values() if event["status"] == "deferred"][0]
        self.assertIn("LicenseRef-Custom", deferred["reason"])
        self.assertIn("/" + "b" * 40 + "/LICENSE", deferred["verification_notes"][0]["url"])
        self.assertIn("LicenseRef-Custom", "\n".join(review.backlog_lines(q)))

    def test_license_verification_failure_defers_without_oss_claim(self):
        q = update_queue({}, [observation(REPO)], NOW)
        with patch.object(review, "verify_repo", return_value=None):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual(selected, [])
        event = next(iter(q["events"].values()))
        self.assertEqual(event["status"], "deferred")
        self.assertEqual(pending_records(q, NOW), [])
        self.assertEqual(len(pending_records(q, LATER)), 1)

    def test_changed_model_access_replaces_row_in_both_languages(self):
        item = {"kind": "model", "url": "https://huggingface.co/nvidia/example-world-model",
                "title": "nvidia/example-world-model", "topic": ("World models", "월드 모델"),
                "gated": True, "terms": "NVIDIA Open Model License", "license": "https://huggingface.co/nvidia/example-world-model/blob/" + "a" * 40 + "/LICENSE",
                "_update": True, "_event_ids": ["a" * 24]}
        for lang in (0, 1):
            heading = review.SECTIONS["model"][lang]
            text = f'{heading}\n\n| Name | Role | Terms | Source |\n|---|---|---|---|\n| Old model | role | old terms | [source]({item["url"]}) {marker(["b" * 24])} |\n\n## Next section\n'
            output = review.upsert(text, heading, [item], lang, True)
            self.assertNotIn("Old model", output)
            self.assertIn("NVIDIA Open Model License", output)
            self.assertEqual(output.count("| **nvidia/example-world-model** |"), 1)
            self.assertEqual(marker_ids([output]), {"a" * 24})

    def test_curated_rows_preserve_all_license_notes_guides_and_official_links(self):
        q = update_queue({}, [observation(REPO, revision="a" * 40)], NOW)
        record_review(q, pending_records(q, NOW)[0], "merged", NOW)
        q = update_queue(q, [observation(REPO, revision="b" * 40)], LATER)
        seed = pending_records(q, LATER)[0]
        record_review(q, seed, "proposed", LATER)
        item = {"kind": "repo", "url": REPO, "title": "Example world model", "topic": ("World models", "월드 모델"),
                "terms": "Apache-2.0", "license": REPO + "/blob/" + "b" * 40 + "/LICENSE", "revision": "b" * 40,
                "date": "2026-12-05", **{k: v for k, v in seed.items() if k.startswith("_")}}
        texts = {}
        for lang, paths in enumerate(review.PATHS):
            heading = review.SECTIONS["repo"][lang]
            texts[paths[0]] = (f'{heading}\n\n| Project | Role | License | Date | Sources | Guide |\n'
                               '|---|---|---|---|---|---|\n'
                               f'| Curated entry | role | Code MIT; robot assets separate NVIDIA terms; weights gated | yesterday | '
                               f'[repo]({REPO}) · [official](https://research.nvidia.com/labs/example/) | '
                               '[detailed lab](docs/en/example-lab.md) |\n')
            texts[paths[1]] = review.SECTIONS["research"][lang] + '\n'
        before = deepcopy(texts)
        kept = review.protect_curated_updates([item], texts, q, LATER)
        self.assertEqual(kept, [])
        self.assertEqual(texts, before)
        event = q["events"][seed["_event_ids"][0]]
        self.assertEqual(event["status"], "deferred")
        self.assertIn("preserve curated notes", event["reason"])
        self.assertEqual(event["verification_notes"][0]["url"], item["license"])
        self.assertIn("Apache-2.0", "\n".join(review.backlog_lines(q)))
        with self.assertRaises(review.ManualVerification):
            review.upsert(texts[review.PATHS[0][0]], review.SECTIONS["repo"][0], [item], 0, True)

    def test_curated_update_cli_persists_manual_evidence_without_proposed_patch(self):
        q = update_queue({}, [observation(REPO, revision="a" * 40)], NOW)
        record_review(q, pending_records(q, NOW)[0], "merged", NOW)
        q = update_queue(q, [observation(REPO, revision="b" * 40)], LATER)
        seed = pending_records(q, LATER)[0]
        record_review(q, seed, "proposed", LATER)
        item = {"kind": "repo", "url": REPO, "title": "Example world model", "topic": ("World models", "월드 모델"),
                "terms": "Apache-2.0", "license": REPO + "/blob/" + "b" * 40 + "/LICENSE", "revision": "b" * 40,
                "date": "2026-12-05", **{k: v for k, v in seed.items() if k.startswith("_")}}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths, original = [], {}
            for lang in (0, 1):
                catalog, archive = root / f"catalog-{lang}.md", root / f"archive-{lang}.md"
                content = (review.SECTIONS["repo"][lang] + '\n\n| Project | Role | Terms | Date | Source | Guide |\n'
                           '|---|---|---|---|---|---|\n' +
                           f'| Curated | role | Code MIT; asset license separate | yesterday | {REPO} | docs/example.md |\n')
                catalog.write_text(content)
                archive.write_text(review.SECTIONS["research"][lang] + '\n')
                paths.append((str(catalog), str(archive)))
                original[catalog] = catalog.read_bytes()
                original[archive] = archive.read_bytes()
            state, pending, body = root / "state.json", root / "pending", root / "body.md"
            state.write_text(json.dumps({"checked": LATER, "queue": q, "recent": []}))
            pending.mkdir()
            argv = ["prepare-research-review.py", "--state", str(state), "--pending", str(pending), "--body", str(body)]
            with patch.object(sys, "argv", argv), patch.object(review, "PATHS", tuple(paths)), \
                    patch.object(review, "candidates", return_value=[item]):
                review.main()
            self.assertTrue(all(path.read_bytes() == data for path, data in original.items()))
            overlay = json.loads((root / "review-state.json").read_text())
            event = overlay["queue"]["events"][seed["_event_ids"][0]]
            self.assertEqual(event["status"], "deferred")
            self.assertNotIn("proposed", [v["status"] for v in overlay["queue"]["events"].values()])
            self.assertIn("Apache-2.0", body.read_text())
            self.assertIn("b" * 40, body.read_text())

    def test_ambiguous_update_requires_manual_review(self):
        item = {"kind": "research", "url": PAPER, "title": "BirdDreams", "topic": ("World models", "월드 모델"),
                "paper": False, "evidence": [], "_update": True}
        heading = review.SECTIONS["research"][0]
        text = f'{heading}\n\n| Name | Source |\n|---|---|\n| One | {PAPER} |\n| Two | {PAPER} |\n'
        with self.assertRaisesRegex(ValueError, "Multiple existing rows"):
            review.upsert(text, heading, [item], 0, True)

    def test_research_project_discovers_author_linked_code(self):
        q = update_queue({}, [observation(PROJECT, related_urls=[PAPER])], NOW)
        html = f'<h1>BirdDreams: A Driving World Model</h1><a href="{REPO}">Code</a>'
        evidence = {"kind": "repo", "url": REPO, "terms": None}
        with patch.object(review, "request", return_value=html), \
                patch.object(review, "author_artifact", return_value=evidence), \
                patch.object(review, "verify_repo", return_value=None):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["evidence"], [evidence])
        self.assertIn("terms unverified", review.render(selected[0], 0))
        self.assertNotIn("Code availability unverified", review.render(selected[0], 0))

    def test_project_template_footer_and_comparison_links_are_not_its_code(self):
        q = update_queue({}, [observation(PROJECT, related_urls=[PAPER])], NOW)
        template = "https://github.com/nerfies/nerfies.github.io"
        comparison = "https://github.com/nv-tlabs/omni-dreams"
        html = (f'<h1>BirdDreams: A Driving World Model</h1><a href="{comparison}">OmniDreams baseline</a>'
                f'<section id="comparison"><a href="{comparison}">Code</a></section>'
                f'<footer><a href="{template}">Source code</a></footer>')
        with patch.object(review, "request", return_value=html), \
                patch.object(review, "author_artifact", side_effect=AssertionError("unrelated artifact checked")), \
                patch.object(review, "verify_repo", side_effect=AssertionError("unrelated repo proposed")):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["evidence"], [])
        self.assertIn("Code availability unverified", review.render(selected[0], 0))

    def test_official_project_separately_cites_its_verified_paper_license(self):
        q = update_queue({}, [observation(PROJECT, related_urls=[PAPER])], NOW)
        def source(url, json_response=True):
            return paper_page() if url == PAPER else '<h1>BirdDreams: A Driving World Model</h1>'
        with patch.object(review, "request", side_effect=source):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual(selected[0]["url"], PROJECT)
        self.assertEqual(selected[0]["paper_url"], PAPER)
        self.assertIn("CC BY 4.0 \\(paper\\)", review.render(selected[0], 0))
        self.assertIn("가중치 공개 여부 미확인", review.render(selected[0], 1))

    def test_official_paper_button_matches_its_title_without_seed_identity(self):
        q = update_queue({}, [observation(PROJECT, revision="page")], NOW)
        def source(url, json_response=True):
            if url == PAPER:
                return paper_page()
            return f'<h1>BirdDreams: A Driving World Model</h1><a href="{PAPER}">Read the paper</a>'
        with patch.object(review, "request", side_effect=source):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual(selected[0]["paper_url"], PAPER)
        self.assertEqual(selected[0]["paper_terms"], "https://creativecommons.org/licenses/by/4.0/")
        self.assertEqual(selected[0]["topic"][0], "Autonomous driving and scene reconstruction")

    def test_paper_button_cannot_assign_a_different_papers_license(self):
        q = update_queue({}, [observation(PROJECT, revision="page")], NOW)
        def source(url, json_response=True):
            return paper_page("DifferentProject: A Driving World Model") if url == PAPER else (
                f'<h1>BirdDreams: A Driving World Model</h1><a href="{PAPER}">Read the paper</a>')
        with patch.object(review, "request", side_effect=source):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertNotIn("paper_url", selected[0])

    def test_hf_arxiv_discovery_with_baseline_watch_keeps_official_project_link(self):
        q = update_queue({}, [observation(source="Hugging Face Papers", revision="", related_urls=[PROJECT]),
                              observation(related_urls=[PROJECT])], NOW)
        q = update_queue(q, [observation(PROJECT, revision="initial-watch", source="Official project watch",
                                        related_urls=[PAPER], discovery_eligible=False)], NOW)
        self.assertEqual(pending_records(q, NOW)[0]["url"], PAPER)
        def source(url, json_response=True):
            if url == PAPER:
                return (paper_page() + f'<table><tr><td class="comments">Project page: '
                        f'<a href="{PROJECT}">this https URL</a></td></tr></table>')
            if url == PROJECT:
                return ('<h1 id="project-title"><span class="project-name">BirdDreams</span>'
                        '<span class="project-subtitle">A driving world model</span></h1>'
                        f'<a href="{PAPER}">Read the paper</a>')
            raise AssertionError("unexpected source")
        with patch.object(review, "request", side_effect=source):
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["url"], PAPER)
        self.assertEqual(selected[0]["project_url"], PROJECT)
        for lang in (0, 1):
            rendered = review.render(selected[0], lang)
            self.assertIn(PROJECT, rendered)
            self.assertIn(PAPER, rendered)
            self.assertIn("CC BY 4.0", rendered)
            self.assertIn("Project page" if lang == 0 else "프로젝트 페이지", rendered)
            self.assertIn("Weight availability unverified" if lang == 0 else "가중치 공개 여부 미확인", rendered)

    def test_different_project_paper_link_does_not_prove_this_papers_code(self):
        q = update_queue({}, [observation(related_urls=[PROJECT])], NOW)
        other = "https://arxiv.org/abs/2611.15000"
        def source(url, json_response=True):
            if url == PAPER:
                return paper_page() + f'<td class="comments"><a href="{PROJECT}">Project page</a></td>'
            return f'<h1>Different project</h1><a href="{other}">Paper</a><a href="{REPO}">Code</a>'
        with patch.object(review, "request", side_effect=source), \
                patch.object(review, "author_artifact", wraps=review.author_artifact) as artifact:
            selected = review.candidates({"checked": NOW}, set(), q)
        self.assertNotIn("project_url", selected[0])
        self.assertEqual(selected[0]["evidence"], [])
        self.assertNotIn(REPO, [call.args[0] for call in artifact.call_args_list])


if __name__ == "__main__":
    unittest.main()
