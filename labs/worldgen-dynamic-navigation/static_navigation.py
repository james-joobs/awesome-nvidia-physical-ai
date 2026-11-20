"""Small, inspectable scan-to-grid planner; no simulator or scene access.

Inputs are robot pose, a goal, and measured range endpoints. Unknown cells are
optimistically traversable inside a known, flat test boundary. No SLAM is done.
"""
import heapq
import math


class Navigator:
    resolution = .05
    radius = .43  # Circumscribed robot footprint plus tracking margin.
    bounds = (-2.5, -2., 2.5, 2.)

    def __init__(self, goal=(1.3, 0.)):
        self.goal = tuple(goal)
        self.hits = set()
        self.path = []
        self.replans = 0
        self.blocked = set()
        self.last_time = None

    def cell(self, point):
        return tuple(int(round((point[i] - self.bounds[i]) / self.resolution)) for i in (0, 1))

    def point(self, cell):
        return tuple(self.bounds[i] + cell[i] * self.resolution for i in (0, 1))

    def allowed(self, cell):
        x, y = self.point(cell)
        return (self.bounds[0] + self.radius <= x <= self.bounds[2] - self.radius
                and self.bounds[1] + self.radius <= y <= self.bounds[3] - self.radius
                and cell not in self.blocked)

    def line_free(self, start, end):
        n = max(1, math.ceil(math.dist(start, end) / (self.resolution / 2)))
        return all(self.allowed(self.cell([start[j] + (end[j] - start[j]) * i / n for j in (0, 1)]))
                   for i in range(n + 1))

    def update(self, pose, depths, endpoints, sim_time):
        """Only measured endpoints within range become occupied cells."""
        if not depths or len(depths) != len(endpoints):
            self.path = []
            return False
        if self.last_time is not None and sim_time <= self.last_time:
            self.path = []
            return False
        self.last_time = sim_time
        for distance, point in zip(depths, endpoints):
            if math.isfinite(distance) and .05 <= distance < 2.499 and all(math.isfinite(q) for q in point[:2]):
                self.hits.add(self.cell(point))
        n = math.ceil(self.radius / self.resolution)
        offsets = [(i, j) for i in range(-n, n+1) for j in range(-n, n+1)
                   if math.hypot(i, j) * self.resolution <= self.radius + self.resolution / 2]
        self.blocked = {(x+i, y+j) for x, y in self.hits for i, j in offsets}
        self.path = self.plan(pose[:2])
        self.replans += 1
        return bool(self.path)

    def plan(self, start):
        source, goal = self.cell(start), self.cell(self.goal)
        if not self.allowed(source) or not self.allowed(goal):
            return []
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
                return [self.point(c) for c in reversed(route)]
            for dx, dy in ((1, -1), (1, 0), (1, 1), (0, -1), (0, 1), (-1, -1), (-1, 0), (-1, 1)):
                neighbor = (node[0]+dx, node[1]+dy)
                if not self.allowed(neighbor):
                    continue
                if dx and dy and (not self.allowed((node[0]+dx, node[1])) or not self.allowed((node[0], node[1]+dy))):
                    continue
                candidate = cost + math.hypot(dx, dy)
                if candidate < costs.get(neighbor, float('inf')):
                    costs[neighbor] = candidate
                    parents[neighbor] = node
                    heapq.heappush(queue, (candidate + math.dist(neighbor, goal), candidate, neighbor))
        return []

    def command(self, pose, front_min, sensor_age):
        x, y, yaw = pose
        distance = math.dist((x, y), self.goal)
        if distance < .12:
            return 0., 0., 'goal'
        if sensor_age > .25 or not self.path:
            return 0., 0., 'sensor-stop' if sensor_age > .25 else 'no-path'
        target = self.path[0]
        for point in self.path:
            if math.dist((x, y), point) <= .40 and self.line_free((x, y), point):
                target = point
        error = math.atan2(math.sin(math.atan2(target[1]-y, target[0]-x)-yaw),
                           math.cos(math.atan2(target[1]-y, target[0]-x)-yaw))
        omega = max(-1.1, min(1.1, 2.8*error))
        speed = min(.32, .9*distance) * max(0., math.cos(error)) if abs(error) < .65 else 0.
        if front_min < .46:
            speed = 0.
        return speed, omega, 'follow-scan-path'
