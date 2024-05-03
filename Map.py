import math

class Map:
    class Wall:
        def __init__(self, x1, y1, x2, y2):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.angle = self.calculate_angle()

        #Neccessary for vector decomposition
        def calculate_angle(self):
            if self.x2 - self.x1 == 0:
                return math.pi / 2 if self.y2 > self.y1 else 3 * math.pi / 2
            else:
                angle = math.atan2(self.y2 - self.y1, self.x2 - self.x1)
                return angle if angle >= 0 else angle + 2 * math.pi

    def __init__(self):
        self.walls = []

    def add_wall(self, x1, y1, x2, y2):
        self.walls.append(self.Wall(x1, y1, x2, y2))

    def add_square_walls(self, x, y, size):
        self.add_wall(x, y, x + size, y)
        self.add_wall(x, y + size, x + size, y + size)
        self.add_wall(x, y, x, y + size)
        self.add_wall(x + size, y, x + size, y + size)

    def populate_map(self, WIDTH, HEIGHT):
        self.add_square_walls(WIDTH*0.1, HEIGHT*0.1, HEIGHT*0.8)
        self.add_wall(WIDTH * 0.1, WIDTH * 0.2, HEIGHT * 0.3, HEIGHT * 0.2)
        self.add_wall(WIDTH * 0.3, HEIGHT * 0.5, WIDTH * 0.5, HEIGHT * 0.5)
        self.add_wall(WIDTH * 0.6, HEIGHT * 0.7, WIDTH * 0.9, HEIGHT * 0.7)
        self.add_wall(WIDTH * 0.2, HEIGHT * 0.6, WIDTH * 0.2, HEIGHT * 0.9)
        self.add_wall(WIDTH * 0.8, HEIGHT * 0.1, WIDTH * 0.8, HEIGHT * 0.6)
        self.add_wall(WIDTH * 0.4, HEIGHT * 0.2, WIDTH * 0.7, HEIGHT * 0.2)
        self.add_wall(WIDTH * 0.5, HEIGHT * 0.4, WIDTH * 0.5, HEIGHT * 0.7)
        self.add_wall(WIDTH * 0.7, HEIGHT * 0.3, WIDTH * 0.7, HEIGHT * 0.6)
        self.add_wall(WIDTH * 0.1, HEIGHT * 0.9, WIDTH * 0.4, HEIGHT * 0.9)
        self.add_wall(WIDTH * 0.5, HEIGHT * 0.1, WIDTH * 0.8, HEIGHT * 0.1)
        self.add_wall(WIDTH * 0.3, HEIGHT * 0.2, WIDTH * 0.3, HEIGHT * 0.5)


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
