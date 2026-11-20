"""Scenario actuator, intentionally independent of the sensor controller.

Continuous, finite-speed kinematic targets drive the obstacle in PhysX.
"""

def ramp(t, start, duration):
    return max(0., min(1., (t-start)/duration))


def position(scenario, time_s):
    if scenario == 'gate':
        y = 2.7 * (1-ramp(time_s, 2., 1.8)) + 2.7*ramp(time_s, 8., 1.8)
        return [.35, y, .3]
    return [.4, -2.7 + 1.75*ramp(time_s, 2., 2.), .3]


def size(scenario):
    return [.22, 3.4, .6] if scenario == 'gate' else [.6, .6, .6]
