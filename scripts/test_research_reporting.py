"""Report the persistent backlog even when daily discovery is quiet."""

import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from research_queue import update_queue

spec = importlib.util.spec_from_file_location("research_reporting", Path(__file__).with_name("collect-research.py"))
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class ReportTests(unittest.TestCase):
    def test_waiting_project_survives_quiet_day_without_duplicate_cards(self):
        first = "2026-11-13T09:00:00+00:00"
        checked = "2026-11-21T09:00:00+00:00"
        item = {"id": "2611.14815", "url": "https://arxiv.org/abs/2611.14815",
                "title": "BirdDreams: Driving World Model", "date": "2026-11-10T00:00:00+00:00",
                "revision": "v1", "detail": "paper", "source": "arXiv"}
        queue = update_queue({}, [item], first)
        queue = update_queue(queue, [{**item, "revision": "v2"}], checked)
        output = collector.report({"checked": checked, "changes": 0, "recent": [],
                                   "queue": queue, "sources": {}})
        self.assertIn("최근 7일에 발견한 변경이 없습니다", output)
        self.assertIn("대기 중인 프로젝트 1개 · 전체 검토 사건 2개", output)
        self.assertEqual(output.count("[BirdDreams:"), 1)
        self.assertIn("최초 발견 2026-11-13", output)

    def test_incomplete_pagination_is_not_reported_as_source_success(self):
        output = collector.report({"checked": "2026-11-21T09:00:00+00:00", "changes": 0,
            "recent": [], "sources": {"arXiv": {"last_success": None,
                "error": "PaginationLimit", "continuation": {"start": 500}}}})
        self.assertIn("확인 성공 0개", output)
        self.assertIn("PaginationLimit", output)
        self.assertIn("다음 실행에서 후속 조회", output)
        self.assertIn("기록 없음", output)


if __name__ == "__main__":
    unittest.main()
