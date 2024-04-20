import math

class Map:
    class Wall:
        def __init__(self, x1, y1, x2, y2):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.angle = self.calculate_angle()

        def calculate_angle(self):
            if self.x2 - self.x1 == 0:  #Vertical wall
                return math.pi / 2 if self.y2 > self.y1 else 3 * math.pi / 2
            else:
                angle = math.atan2(self.y2 - self.y1, self.x2 - self.x1)
                return angle if angle >= 0 else angle + 2 * math.pi

    def __init__(self):
        self.walls = []

    def add_wall(self, x1, y1, x2, y2):
        self.walls.append(self.Wall(x1, y1, x2, y2))

    def add_square_walls(self, x, y, size):
        # Add walls to form a square
        self.add_wall(x, y, x + size, y)           # Bottom wall
        self.add_wall(x, y + size, x + size, y + size)  # Top wall
        self.add_wall(x, y, x, y + size)           # Left wall
        self.add_wall(x + size, y, x + size, y + size)  # Right wall
