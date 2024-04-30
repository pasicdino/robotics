import math
from shapely.geometry import LineString

class Map:
    class Wall:
        def __init__(self, x1, y1, x2, y2):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.line = LineString([(x1, y1), (x2, y2)])
            self.vector_normalized = self.normalize_wall_vector()
            self.angle = self.calculate_angle()

        #Neccessary for vector decomposition
        def calculate_angle(self):
            if self.x2 - self.x1 == 0:
                return math.pi / 2 if self.y2 > self.y1 else 3 * math.pi / 2
            else:
                angle = math.atan2(self.y2 - self.y1, self.x2 - self.x1)
                return angle if angle >= 0 else angle + 2 * math.pi
            
        #Calculate normalized vector of wall for collision handling
        def normalize_wall_vector(self):
            wall_vector = (self.x2 - self.x1, self.y2 - self.y1)
            wall_vector_normalized = (
                wall_vector[0] / math.hypot(wall_vector[0], wall_vector[1]),
                wall_vector[1] / math.hypot(wall_vector[0], wall_vector[1])
            )
            return wall_vector_normalized

    def __init__(self):
        self.walls = []

    def add_wall(self, x1, y1, x2, y2):
        self.walls.append(self.Wall(x1, y1, x2, y2))

    def add_square_walls(self, x, y, size):
        self.add_wall(x, y, x + size, y)
        self.add_wall(x, y + size, x + size, y + size)
        self.add_wall(x, y, x, y + size)
        self.add_wall(x + size, y, x + size, y + size)

    def add_hexagon_walls(self, center_x, center_y, size):
        #1/6th of a circle
        angle_step = math.pi / 3

        points = []

        for i in range(6):
            angle = angle_step * i
            x = center_x + size * math.cos(angle)
            y = center_y + size * math.sin(angle)
            points.append((x, y))

        for i in range(6):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % 6]
            self.add_wall(x1, y1, x2, y2)
