import unittest
from stats import interaction_summary


def record():
    return {'before': {'now': 0}, 'after': {'now': 3000}, 'rows': [
        {'completed_at_ms': t, 'model_ms': 100, 'round_trip_ms': 150, 'history_frames': 4}
        for t in (500, 1500, 2500)], 'frame_timestamps_ms': list(range(0, 3000, 20))}


class LatencyTests(unittest.TestCase):
    def test_delivered_fps_does_not_invert_model_or_request_time(self):
        result = interaction_summary(record())
        self.assertEqual(result['delivered_ai_fps'], 1)
        self.assertEqual(result['native_presented_fps'], 50)
        self.assertEqual(result['temporal_model_median_ms'], 100)

    def test_stale_responses_do_not_become_displayed_ai_frames(self):
        data = record()
        data['rows'].insert(1, {**data['rows'][0], 'completed_at_ms': 800, 'discarded_stale': True})
        self.assertEqual(interaction_summary(data)['painted_ai_updates'], 3)

    def test_context_free_startup_is_not_v5_latency(self):
        data = record()
        data['rows'][0].update(history_frames=0, model_ms=9000, round_trip_ms=9500)
        result = interaction_summary(data)
        self.assertEqual(result['temporal_capture_to_paint_median_ms'], 150)
        self.assertGreater(result['capture_to_paint_p95_ms'], 150)

    def test_duplicate_paint_timestamps_are_rejected(self):
        data = record()
        data['rows'][1]['completed_at_ms'] = 500
        with self.assertRaises(ValueError):
            interaction_summary(data)


if __name__ == '__main__':
    unittest.main()
