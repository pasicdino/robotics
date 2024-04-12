class Map:
    def __init__(self):
        self.walls = []

    def add_wall(self, x1, y1, x2, y2):
        self.walls.append((x1, y1, x2, y2))

    def add_square_walls(self, x, y, size):
        self.add_wall(x, y, x + size, y)
        self.add_wall(x, y + size, x + size, y + size)
        self.add_wall(x, y, x, y + size)
        self.add_wall(x + size, y, x + size, y + size)


