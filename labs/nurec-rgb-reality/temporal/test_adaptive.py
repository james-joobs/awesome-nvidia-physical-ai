import unittest
from adaptive import plan,bootstrap_slots,validate_input_size


class AdaptiveTests(unittest.TestCase):
    def test_preview_cannot_share_the_high_quality_bank(self):
        low,size=plan('adaptive','preview');high,hq=plan('adaptive','refine')
        self.assertNotEqual(low,high);self.assertEqual(size,(512,288));self.assertEqual(hq,(1024,576))
    def test_complete_hq_history_needs_no_bootstrap(self):
        self.assertEqual(bootstrap_slots(4,'temporal','refine'),0)
    def test_only_stationary_temporal_refinement_can_reuse_slots(self):
        self.assertEqual(bootstrap_slots(0,'temporal','refine'),4)
        self.assertEqual(bootstrap_slots(0,'temporal','preview'),0)
        self.assertEqual(bootstrap_slots(0,'independent','refine'),0)
    def test_invalid_phase_is_rejected(self):
        for profile,phase in [('adaptive',None),('adaptive','continuous'),('exact','preview')]:
            with self.assertRaises(ValueError):plan(profile,phase)
    def test_low_resolution_preview_is_not_an_hq_input(self):
        with self.assertRaises(ValueError):validate_input_size('adaptive','refine',(512,288))
        validate_input_size('adaptive','refine',(1024,576))
        validate_input_size('adaptive','preview',(512,288))
