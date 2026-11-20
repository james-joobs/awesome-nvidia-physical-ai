"""Sensor-map behavior checks with no simulator or GPU dependencies."""
import math
import unittest
from navigation import Navigator


def scan(pose, wall_x=None):
    depths, points = [], []
    for i in range(180):
        angle = pose[2]-math.pi+2*math.pi*i/180
        dx, dy = math.cos(angle), math.sin(angle)
        distance = (wall_x-pose[0])/dx if wall_x is not None and dx > .0001 else 2.5
        hit = .05 <= distance < 2.5 and abs(pose[1]+distance*dy) < 2.
        depths.append(distance if hit else 2.5)
        points.append([wall_x, pose[1]+distance*dy, .48] if hit else [0., 0., 0.])
    return depths, points


class DynamicMapping(unittest.TestCase):
    def test_opened_barrier_is_cleared_and_route_recovers(self):
        nav = Navigator();pose = (-1., 0., 0.)
        nav.update(pose, *scan(pose, 0.), 1.)
        self.assertFalse(nav.path)
        self.assertGreater(len(nav.hits), 10)
        nav.update(pose, *scan(pose), 1.1)
        self.assertTrue(nav.path)
        self.assertGreater(nav.stats['cleared'], 10)
        self.assertFalse(nav.hits)

    def test_closer_surface_does_not_clear_occluded_old_surface(self):
        nav = Navigator();pose = (-1., 0., 0.)
        nav.update(pose, *scan(pose, .3), 1.)
        original = set(nav.hits)
        nav.update(pose, *scan(pose, -.2), 1.1)
        self.assertTrue(original.intersection(nav.hits))
        nav.update(pose, *scan(pose, -.2), 3.2)
        self.assertGreater(nav.stats['expired'], 0)

    def test_stale_or_repeated_frame_stops(self):
        nav = Navigator();pose = (-1., 0., 0.)
        nav.update(pose, *scan(pose), 1.)
        self.assertGreater(nav.command(pose, 2.5, .0)[0], 0)
        self.assertEqual(nav.command(pose, 2.5, .26), (0., 0., 'sensor-stop'))
        self.assertFalse(nav.update(pose, *scan(pose), 1.))
        self.assertEqual(nav.command(pose, 2.5, .01)[:2], (0., 0.))

    def test_new_close_obstacle_brakes_both_wheels(self):
        nav = Navigator();pose = (-1., 0., 0.)
        nav.update(pose, *scan(pose, -.3), 1.)
        self.assertEqual(nav.command(pose, .7, 0), (0., 0., 'obstacle-brake'))
        self.assertEqual(nav.command(pose, .7, .1)[:2], (0., 0.))

    def test_robot_can_leave_a_quantized_inflation_margin(self):
        nav = Navigator(goal=(-1.3, 0.));pose = (-.43, 0., math.pi)
        nav.update(pose, *scan(pose, 0.), 1.)
        self.assertTrue(nav.path)
        self.assertTrue(all(p[0] < 0 for p in nav.path))
        self.assertGreater(nav.command(pose, 2.5, 0)[0], 0)

    def test_terminal_approach_uses_axle_offset(self):
        nav = Navigator();pose = (1.2, 0., 0.)
        nav.update(pose, *scan(pose), 1.)
        v, _, phase = nav.command(pose, 2.5, 0)
        self.assertGreater(v, 0)
        self.assertEqual(phase, 'final-approach')


if __name__ == '__main__':
    unittest.main()
