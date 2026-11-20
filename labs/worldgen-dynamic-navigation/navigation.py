"""Refresh an observed obstacle map and supervise motion from range scans.

No obstacle poses, actor schedule, or simulator handles enter this module.
This is a small planar educational controller, not a safety-certified stack.
"""
import heapq
import math
from static_navigation import Navigator as StaticNavigator


class Navigator(StaticNavigator):
    memory_seconds = 2.0
    clear_margin = .10
    radius = .52  # 0.425 m axle-centered footprint plus tracking margin.
    axle_offset = .10

    def __init__(self, goal=(1.3, 0.)):
        self.body_goal = tuple(goal)
        # Desired final chassis heading is +X. Plan the actual rotation center.
        super().__init__((goal[0]+self.axle_offset, goal[1]))
        self.observed = {}
        self.depths = None
        self.front_min = self.nearest = 2.5
        self.brake_until = -1.
        self.brake_latched = False
        self.stats = {'cleared': 0, 'expired': 0, 'occupied': 0}

    def control_pose(self, pose):
        x, y, yaw = pose
        return (x+self.axle_offset*math.cos(yaw), y+self.axle_offset*math.sin(yaw), yaw)

    def update(self, pose, depths, endpoints, sim_time):
        if (not depths or len(depths) != len(endpoints)
                or not all(math.isfinite(v) and .05 <= v <= 2.5001 for v in depths)
                or self.last_time is not None and sim_time <= self.last_time):
            self.path = []
            return False
        new_hits = {self.cell(point): (point[0], point[1], sim_time)
                    for distance, point in zip(depths, endpoints)
                    if distance < 2.499 and all(math.isfinite(q) for q in point[:2])}
        x, y, yaw = pose
        cleared = expired = 0
        # Compare each old surface with the nearest current beam. A longer beam
        # observes free space through that old location. Miss positions are zero
        # in the SDK, so they must never be treated as a real XYZ measurement.
        for cell, (px, py, stamp) in list(self.observed.items()):
            if cell in new_hits:
                continue
            distance = math.hypot(px-x, py-y)
            angle = (math.atan2(py-y, px-x)-yaw+math.pi) % (2*math.pi)
            index = int(round(angle/(2*math.pi)*len(depths))) % len(depths)
            if distance + self.clear_margin < depths[index]:
                del self.observed[cell]
                cleared += 1
            elif sim_time-stamp > self.memory_seconds:
                del self.observed[cell]
                expired += 1
        self.observed.update(new_hits)
        self.hits = set(self.observed)
        # Reuse the baseline's inflation and A*, but replace its permanent map
        # with the updated observations before every plan.
        result = super().update(self.control_pose(pose), depths, endpoints, sim_time)
        self.depths = list(depths)
        n = len(depths)
        self.front_min = min(d for i, d in enumerate(depths)
                             if abs(-math.pi+2*math.pi*i/n) < math.radians(25))
        self.nearest = min(depths)
        if self.front_min < .75 and not self.brake_latched:
            self.brake_until = sim_time + .6
            self.brake_latched = True
        if self.front_min > .95:
            self.brake_latched = False
        self.stats = {'cleared': cleared, 'expired': expired, 'occupied': len(self.observed)}
        return result

    def plan(self, start):
        # Quantization/turning can put the robot's center one cell inside the
        # inflated margin. Permit leaving this known self cell, while retaining
        # actual measured occupied cells and every neighboring blocked cell.
        source = self.cell(start)
        if source not in self.hits:
            self.blocked.discard(source)
        goal = self.cell(self.goal)
        if not self.allowed(source) or not self.allowed(goal):
            return []
        # Prefer continuity with the last sensor-generated plan. This prevents
        # tiny scan/grid changes from flipping between equally short detours.
        history = [self.cell(point) for point in self.path]
        penalties = {}
        queue = [(math.dist(source, goal), 0., source)]
        costs, parents = {source: 0.}, {}
        while queue:
            _, cost, node = heapq.heappop(queue)
            if cost > costs[node]:
                continue
            if node == goal:
                route = [node]
                while route[-1] != source:
                    route.append(parents[route[-1]])
                return [self.point(cell) for cell in reversed(route)]
            for dx, dy in ((1,-1),(1,0),(1,1),(0,-1),(0,1),(-1,-1),(-1,0),(-1,1)):
                neighbor = (node[0]+dx, node[1]+dy)
                if not self.allowed(neighbor):
                    continue
                if dx and dy and (not self.allowed((node[0]+dx,node[1])) or not self.allowed((node[0],node[1]+dy))):
                    continue
                if neighbor not in penalties:
                    penalties[neighbor] = .08*min(10, min((abs(neighbor[0]-p[0])+abs(neighbor[1]-p[1]) for p in history), default=0))
                candidate = cost+math.hypot(dx,dy)+penalties[neighbor]
                if candidate < costs.get(neighbor, float('inf')):
                    costs[neighbor] = candidate
                    parents[neighbor] = node
                    heapq.heappush(queue, (candidate+math.dist(neighbor,goal), candidate, neighbor))
        return []

    def command(self, pose, front_min, sensor_age):
        if self.last_time is None or sensor_age > .25:
            return 0., 0., 'sensor-stop'
        now = self.last_time + sensor_age
        if self.nearest < .39:
            return 0., 0., 'close-obstacle-stop'
        if now < self.brake_until:
            return 0., 0., 'obstacle-brake'
        control = self.control_pose(pose)
        v, omega, phase = super().command(control, self.front_min, sensor_age)
        distance = math.dist(control[:2], self.goal)
        if phase == 'goal' and distance > .08:
            error = math.atan2(math.sin(math.atan2(self.goal[1]-control[1], self.goal[0]-control[0])-pose[2]),
                               math.cos(math.atan2(self.goal[1]-control[1], self.goal[0]-control[0])-pose[2]))
            v = min(.12, .9*distance)*max(0., math.cos(error)) if abs(error) < .65 else 0.
            omega, phase = max(-.8, min(.8, 2.8*error)), 'final-approach'
        elif phase == 'goal' and abs(pose[2]) > .08:
            v, omega, phase = 0., max(-.8, min(.8, -2*pose[2])), 'align-at-goal'
        if phase == 'no-path':
            return 0., 0., 'wait-for-path'
        if self.front_min < .58:
            return 0., omega, 'turn-clear' if abs(omega) > .05 else 'obstacle-stop'
        return v, omega, phase
