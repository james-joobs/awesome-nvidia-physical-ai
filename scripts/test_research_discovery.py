"""Offline regressions for publication source shapes observed in November 2026.

Fixtures below retain only the minimal public metadata needed for the parser;
they are not full-page copies and never execute downloaded JavaScript.
"""

from datetime import UTC, datetime, timedelta
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from xml.etree import ElementTree


sys.path.insert(0, str(Path(__file__).resolve().parent))
SPEC = importlib.util.spec_from_file_location("research_discovery", Path(__file__).with_name("collect-research.py"))
monitor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitor)
BIRD_TITLE = "BirdDreams: Joint Perspective and BEV Video Generation for a Plausible, Reactive Driving World Model"
BIRD_PROJECT = "https://research.nvidia.com/labs/sil/projects/birddreams/"
BIRD_PAPER = "https://arxiv.org/abs/2611.14815"


class ResearchDiscoveryTests(unittest.TestCase):
    def test_arxiv_cv_entry_is_collected_with_publication_and_version(self):
        root = ElementTree.fromstring(f'''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
          <id>http://arxiv.org/abs/2611.14815v1</id><title>{BIRD_TITLE}</title>
          <published>2026-11-10T23:04:58Z</published><updated>2026-11-10T23:04:58Z</updated>
          <category term="cs.CV"/><link href="{BIRD_PAPER}"/>
        </entry></feed>''')
        with patch.object(monitor, "fetch", return_value=root) as fetch:
            rows = list(monitor.arxiv_papers(datetime(2026, 8, 23, tzinfo=UTC)))
        self.assertEqual(rows[0]["paper_id"], "2611.14815")
        self.assertEqual(rows[0]["revision"], "v1")
        self.assertEqual(rows[0]["published_at"], "2026-11-10T23:04:58Z")
        self.assertIn("cs.CV", monitor.PAPER_QUERY)
        self.assertIn("cs.LG", monitor.PAPER_QUERY)
        self.assertIn("driving+world+model", fetch.call_args.args[0])

    def test_sil_data_script_handles_comments_escapes_and_trailing_commas(self):
        script = r'''const PUBLICATIONS_DATA = [
          {"title":"A video world model", "paper":"https://arxiv.org/abs/2611.14815",
           "abstract":"LaTeX {\em text}, literal comma, } and \\em",
           "project":"https://research.nvidia.com/labs/sil/projects/birddreams/",
           "code":"https://github.com/NVIDIA/shared-runtime", // source has comments
          },
        ]; function unrelatedCode() { throw new Error("must never execute"); }'''
        html = '<script src="/labs/sil/publications/publications.js" async></script>'
        with patch.object(monitor, "fetch", side_effect=[html, script]):
            rows = list(monitor.sil_publications(datetime(2026, 8, 23, tzinfo=UTC)))
        self.assertEqual(rows[0]["url"], BIRD_PROJECT)
        self.assertEqual(rows[0]["paper_id"], "2611.14815")
        self.assertIsNone(rows[0]["published_at"])
        self.assertEqual(rows[0]["date_kind"], "unknown")
        self.assertEqual(rows[0]["source_month"], "2026-11")
        self.assertNotIn("https://github.com/NVIDIA/shared-runtime", rows[0]["identity_urls"])

    def test_sil_http_success_without_data_is_not_collection_success(self):
        with patch.object(monitor, "fetch", return_value="<h1>Publications</h1>"):
            with self.assertRaisesRegex(ValueError, "data script missing"):
                list(monitor.sil_publications(datetime(2026, 8, 23, tzinfo=UTC)))

    def test_gear_reads_named_next_chunk_instead_of_empty_page_props(self):
        page = '''<script id="__NEXT_DATA__">{"props":{"pageProps":{"publicationsData":{}}}}</script>
          <script src="/labs/gear/_next/static/chunks/pages/publications-123abc.js"></script>'''
        script = '''function render(){return [{title:"A robot world model",paperLink:"https://arxiv.org/abs/2611.12345",projectLink:"/labs/gear/newmodel/",codeLink:"https://github.com/NVIDIA/runtime"}]}'''
        with patch.object(monitor, "fetch", side_effect=[page, script]):
            rows = list(monitor.gear_publications(datetime(2026, 8, 23, tzinfo=UTC)))
        self.assertEqual(rows[0]["url"], "https://research.nvidia.com/labs/gear/newmodel/")
        self.assertEqual(rows[0]["code_urls"], ["https://github.com/NVIDIA/runtime"])

    def test_old_undated_publication_is_snapshotted_but_baselined(self):
        record = monitor.research_record(
            {"title": "An earlier world model", "paper": "https://arxiv.org/abs/2001.12345"},
            "https://research.nvidia.com/labs/sil/publications/", {"paper": "paper"})
        record = monitor.backfill_status(record, datetime(2026, 8, 23, tzinfo=UTC))
        self.assertFalse(record["discovery_eligible"])
        self.assertEqual(record["source_month"], "2020-01")
        self.assertIsNone(record["published_at"])

    def test_srl_scheme_relative_links_are_resolved_and_talk_template_skipped(self):
        root = ElementTree.fromstring('''<rss><channel>
          <item><title>Example Talk</title><link>//research.nvidia.com/labs/srl/talk/example/</link><pubDate>Sat, 01 Jun 2030 13:00:00 +0000</pubDate></item>
          <item><title>A robot policy</title><link>//research.nvidia.com/labs/srl/publication/policy/</link><pubDate>Sun, 01 Nov 2026 00:00:00 +0000</pubDate></item>
        </channel></rss>''')
        with patch.object(monitor, "fetch", return_value=root):
            rows = list(monitor.srl_publications(datetime(2026, 8, 23, tzinfo=UTC)))
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["url"].startswith("https://"))

    def test_hf_paper_promoted_after_submission_keeps_both_dates_and_identity(self):
        now = datetime.now(UTC)
        submission = (now - timedelta(days=30)).isoformat()
        promotion = now.isoformat()
        calls = []

        def fetch(url, *_args, **_kwargs):
            calls.append(url)
            if "/api/daily_papers" in url:
                return [{"paper": {"id": "2611.14815", "title": BIRD_TITLE, "summary": "driving world model", "submittedOnDailyAt": promotion}}]
            return {"publishedAt": submission, "submittedOnDailyAt": promotion, "projectPage": BIRD_PROJECT}

        with patch.object(monitor, "fetch", side_effect=fetch):
            rows = list(monitor.hf_papers(now - timedelta(days=1)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["published_at"], submission)
        self.assertEqual(rows[0]["listed_at"], promotion)
        self.assertEqual(set(rows[0]["identity_urls"]), {BIRD_PROJECT, BIRD_PAPER})
        self.assertEqual(sum("/api/papers/" in url for url in calls), 1)

    def test_partial_pagination_keeps_discoveries_but_not_success_watermark(self):
        now = datetime(2026, 11, 21, tzinfo=UTC)
        before = (now - timedelta(days=1)).isoformat()

        def source(_cutoff):
            yield monitor.entry("bird", BIRD_TITLE, BIRD_PROJECT, "1970-01-01", "official source")
            raise monitor.SourceLimit("more pages")

        previous = {"sources": {"lab": {"last_success": before, "items": {}}}}
        state = monitor.collect(previous, now, [("lab", source, ())])
        self.assertEqual(state["sources"]["lab"]["error"], "PaginationLimit")
        self.assertEqual(state["sources"]["lab"]["last_success"], before)
        self.assertEqual(state["recent"][0]["url"], BIRD_PROJECT)
        self.assertTrue(state["queue"]["projects"])

    def test_new_source_uses_ninety_day_backfill(self):
        now = datetime(2026, 11, 21, tzinfo=UTC)
        seen = []

        def source(cutoff):
            seen.append(cutoff)
            return []

        monitor.collect({}, now, [("new", source, ())])
        self.assertEqual((now - seen[0]).days, 90)

    def test_official_sitemap_does_not_require_a_keyword_in_the_project_name(self):
        root = ElementTree.fromstring('''<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://research.nvidia.com/publication/2026-11_new-project-name</loc><lastmod>2026-11-20</lastmod></url>
        </urlset>''')
        with patch.object(monitor, "fetch", return_value=root):
            rows = list(monitor.nvidia_research(datetime(2026, 8, 23, tzinfo=UTC)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date_kind"], "modified")

    def test_hf_uses_latest_available_edition_and_complete_list_metadata(self):
        now = datetime.now(UTC)
        listed = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        calls = []

        def fetch(url, *_args, **_kwargs):
            calls.append(url)
            self.assertIn("/api/daily_papers", url)
            return [{"paper": {"id": "2611.14815", "title": BIRD_TITLE, "projectPage": BIRD_PROJECT,
                               "submittedOnDailyAt": listed, "publishedAt": "2026-11-10T00:00:00Z"}}]

        with patch.object(monitor, "fetch", side_effect=fetch):
            rows = list(monitor.hf_papers(now - timedelta(days=1)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(calls, ["https://huggingface.co/api/daily_papers"])

    def test_pagination_never_follows_an_unexpected_host(self):
        with patch.object(monitor, "fetch", return_value=([{"id": "x"}], {"Link": '<https://example.org/private>; rel="next"'})):
            generator = monitor.paged("https://api.github.com/orgs/NVIDIA/repos?per_page=100")
            self.assertEqual(next(generator), [{"id": "x"}])
            with self.assertRaisesRegex(ValueError, "unexpected API pagination"):
                next(generator)

    def test_capped_scan_resumes_next_page_and_preserves_original_watermark(self):
        now = datetime(2026, 11, 21, tzinfo=UTC)
        initial = "https://api.github.com/orgs/NVIDIA/repos?per_page=100"
        following = initial + "&page=2"
        fetched = []

        def fetch(url, **_kwargs):
            fetched.append(url)
            return ([{"id": "first"}], {"Link": f'<{following}>; rel="next"'}) if url == initial else ([{"id": "second"}], {})

        def source(_cutoff, continuation=None):
            for page in monitor.paged(initial, continuation=continuation):
                for value in page:
                    yield monitor.entry(value["id"], value["id"], f"https://github.com/NVIDIA/{value['id']}", "2026-11-20", "new repository")

        with patch.object(monitor, "fetch", side_effect=fetch), patch.object(monitor, "MAX_PAGES", 1):
            first = monitor.collect({}, now, [("repos", source, ())])
            self.assertEqual(first["sources"]["repos"]["continuation"]["next_url"], following)
            second = monitor.collect(first, now + timedelta(days=1), [("repos", source, ())])
        self.assertEqual(fetched, [initial, following])
        self.assertIsNone(second["sources"]["repos"]["error"])
        self.assertNotIn("continuation", second["sources"]["repos"])
        self.assertEqual(second["sources"]["repos"]["last_success"], now.isoformat())
        self.assertEqual(len(second["queue"]["projects"]), 2)

    def test_github_release_pagination_accepts_canonical_numeric_repository_id(self):
        initial = "https://api.github.com/repos/NVIDIA-NeMo/Evaluator/releases?per_page=100"
        numeric = "https://api.github.com/repositories/1008648645/releases?per_page=100&page=2"
        replies = [([{"id": "first"}], {"Link": f'<{numeric}>; rel="next"'}), ([{"id": "second"}], {})]
        with patch.object(monitor, "fetch", side_effect=replies) as fetch:
            pages = list(monitor.paged(initial))
        self.assertEqual(len(pages), 2)
        self.assertEqual(fetch.call_args.args[0], numeric)
        self.assertFalse(monitor.pagination_target("https://api.github.com/user/repos", initial))

    def test_project_watch_rotation_reaches_items_beyond_the_cap(self):
        projects, events = {}, {}
        for index in range(41):
            pid = f"arxiv:2611.{index:05d}"
            url = f"https://research.nvidia.com/labs/sil/projects/project-{index:02d}/"
            projects[pid] = {"urls": [url]}
            events[str(index)] = {"project_id": pid, "status": "pending", "record": {}}
        previous = {"queue": {"projects": projects, "events": events}}
        first = list(monitor.project_sources(previous))
        self.assertEqual(len(first), 40)
        previous["project_checks"] = {args[0]: "2026-11-21T00:00:00+00:00" for _, _, args in first}
        following = list(monitor.project_sources(previous))
        self.assertEqual(following[0][2][0], "https://research.nvidia.com/labs/sil/projects/project-40/")

    def test_project_watch_ignores_comparison_and_footer_resources(self):
        html = f'''<nav><a href="https://github.com/NVIDIA/nav-template">GitHub</a></nav>
          <h1>BirdDreams</h1><a href="{BIRD_PAPER}">Read the paper</a>
          <a href="https://research.nvidia.com/labs/sil/projects/omnidreams-blog/">OmniDreams</a>
          <section class="comparison"><a href="https://github.com/NVIDIA/comparison">Code</a></section>
          <a href="https://github.com/NVIDIA/current-project">Code</a>
          <a href="https://huggingface.co/nvidia/current-project">Model weights</a>
          <footer><a href="https://github.com/NVIDIA/page-template">Code</a></footer>'''
        with patch.object(monitor, "fetch", return_value=html):
            rows = monitor.official_project(BIRD_PROJECT, "2611.14815", (), datetime(2026, 11, 21, tzinfo=UTC))
        self.assertEqual(rows[0]["code_urls"], ["https://github.com/NVIDIA/current-project"])
        self.assertEqual(rows[0]["model_urls"], ["https://huggingface.co/nvidia/current-project"])
        self.assertEqual(rows[0]["identity_urls"], [BIRD_PROJECT, BIRD_PAPER])

    def test_project_watch_retains_empty_snapshot_then_detects_code_addition(self):
        base = f'<h1>BirdDreams</h1><a href="{BIRD_PAPER}">Paper</a>'
        now = datetime(2026, 11, 21, tzinfo=UTC)
        with patch.object(monitor, "fetch", return_value=base):
            first = monitor.collect({}, now, [("watch", monitor.official_project, (BIRD_PROJECT, "2611.14815", ()))])
        self.assertFalse(first["queue"]["events"])
        with patch.object(monitor, "fetch", return_value=base + '<a href="https://github.com/NVIDIA/new-project">Code</a>'):
            second = monitor.collect(first, now + timedelta(days=1), [("watch", monitor.official_project, (BIRD_PROJECT, "2611.14815", ()))])
        self.assertEqual(len(second["queue"]["events"]), 1)
        self.assertEqual(next(iter(second["queue"]["events"].values()))["status"], "pending")

    def test_one_malformed_source_does_not_abort_other_sources(self):
        def broken(_cutoff):
            raise AttributeError("unexpected upstream shape")

        state = monitor.collect({}, datetime(2026, 11, 21, tzinfo=UTC), [("broken", broken, ()), ("ok", lambda _cutoff: [], ())])
        self.assertEqual(state["sources"]["broken"]["error"], "AttributeError")
        self.assertIsNone(state["sources"]["ok"]["error"])


if __name__ == "__main__":
    unittest.main()
