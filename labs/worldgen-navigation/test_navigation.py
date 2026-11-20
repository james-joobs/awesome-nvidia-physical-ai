"""Behavior checks for planning from observations, independent of Isaac Sim."""
import math
import unittest
from navigation import Navigator


def observations(lower=False, upper=False):
    # A dense synthetic scan of facing surfaces; scene geometry is never an API input.
    points = [[-.225, y/100, .48] for y in range(-40, 41, 2)]
    if lower:
        points += [[-.225, y/100, .48] for y in range(-125, -64, 2)]
    if upper:
        points += [[-.225, y/100, .48] for y in range(65, 126, 2)]
    return [math.dist((-1.3, 0), p[:2]) for p in points], points


class ScanPlanning(unittest.TestCase):
    def test_new_observation_changes_route_without_waypoints(self):
        nav = Navigator()
        nav.update((-1.3, 0, 0), [2.5], [[1.2, 0, .48]], 1.)
        self.assertTrue(all(abs(p[1]) < .01 for p in nav.path))
        nav.update((-1.3, 0, 0), *observations(), 2.)
        self.assertTrue(max(abs(p[1]) for p in nav.path) > .8)
        self.assertTrue(all(nav.allowed(nav.cell(p)) for p in nav.path))

    def test_side_is_determined_by_measured_obstruction(self):
        lower, upper = Navigator(), Navigator()
        lower.update((-1.3, 0, 0), *observations(lower=True), 1.)
        upper.update((-1.3, 0, 0), *observations(upper=True), 1.)
        self.assertGreater(max(p[1] for p in lower.path), .8)
        self.assertLess(min(p[1] for p in upper.path), -.8)

    def test_missing_or_stale_scan_stops(self):
        nav = Navigator()
        self.assertEqual(nav.command((-1.3, 0, 0), 2.5, 1.)[:2], (0., 0.))
        nav.update((-1.3, 0, 0), [2.5], [[1.2, 0, .48]], 1.)
        self.assertEqual(nav.command((-1.3, 0, 0), 2.5, .26)[:2], (0., 0.))

    def test_complete_barrier_does_not_produce_a_path(self):
        nav = Navigator()
        points = [[-.225, y/100, .48] for y in range(-200, 201, 2)]
        nav.update((-1.3, 0, 0), [1.]*len(points), points, 1.)
        self.assertFalse(nav.path)
        self.assertEqual(nav.command((-1.3, 0, 0), 1., 0.)[:2], (0., 0.))


if __name__ == '__main__':
    unittest.main()
