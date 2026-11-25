import copy
import unittest
from adaptive_stats import interaction_summary


def fixture():
    def row(seq, paint, capture, resolution, phase):
        return dict(sequence=seq, completed_at_ms=paint, input_view={'captured_at_ms': capture},
                    resolution=resolution, phase=phase, history_frames=4, model_ms=70,
                    round_trip_ms=paint-capture, model_calls=1, reused_reference_slots=0)
    return dict(events=[dict(kind='moving',cycle=0,start_ms=0,end_ms=1000),
                        dict(kind='rest',cycle=0,start_ms=1000,end_ms=3000)],
                rows=[row(1,400,200,[512,288],'preview'), row(2,1700,1400,[1024,576],'refine')],
                motion=[{'at_ms':1100}], presentation=[{'kind':'native-preview','at_ms':100},
                 {'kind':'gpu-preview','at_ms':400}, {'kind':'native-preview','at_ms':2500}])


class PhaseStatistics(unittest.TestCase):
    def test_separate_native_and_ai_and_idle_time(self):
        result=interaction_summary(fixture())
        self.assertEqual(result['delivered_ai_fps_while_moving'],1)
        self.assertEqual(result['browser_preview_fps_while_moving'],1)
        self.assertEqual(result['camera_stop_to_hq_median_ms'],600)
        self.assertEqual(result['pointer_stop_to_hq_median_ms'],700)
        self.assertEqual(result['stops'][0]['redundant_idle_requests'],0)

    def test_browser_preview_only_has_no_ai_latency(self):
        data=fixture();data['rows']=data['rows'][1:]
        result=interaction_summary(data)
        self.assertEqual(result['delivered_ai_fps_while_moving'],0)
        self.assertIsNone(result['moving_capture_to_paint_median_ms'])

    def test_late_stale_hq_is_not_a_valid_stop(self):
        data=fixture();data['rows'][1]['input_view']['captured_at_ms']=1050
        with self.assertRaises(ValueError):interaction_summary(data)

    def test_discarded_reply_is_not_a_painted_frame(self):
        data=fixture();stale=copy.deepcopy(data['rows'][0]);stale['discarded_stale']=True
        data['rows'].insert(0,stale)
        self.assertEqual(interaction_summary(data)['painted_ai_updates_while_moving'],1)


if __name__=='__main__':unittest.main()
