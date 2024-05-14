import math
import random
from shapely.geometry import LineString, Point

class Map:
    # Author: Dino Pasic, Jannick Smeets
    # Description: Class representing the full map to be populated with walls and features

    class Wall:
        # Author: Dino Pasic
        # Description: Class that represents each wall within the map

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
        
    class Feature:
        # Author: Jannick Smeets
        # Description: Class representing each feature within the map

        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.point = Point((x, y))

            self.radius = 5
    
    class DustParticle:
        # Author: Jannick Smeets
        # Description: Class representing each dust particle within the map

        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.point = Point((x, y))
            self.collected = False
            self.size = random.randint(1, 2)

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.features = []
        self.dust_particles = []

    def add_wall(self, x1, y1, x2, y2):
        self.walls.append(self.Wall(x1, self.height - y1, x2, self.height - y2))

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

    # Author: Jannick Smeets
    # Description: Extracts map features/landmarks using vertices of wall lines
    def extract_features(self):
        existing_features = []
        for wall in self.walls:
            if (wall.x1, wall.y1) not in existing_features:
                existing_features.append((wall.x1, wall.y1))
                self.features.append(self.Feature(wall.x1, wall.y1))
            if (wall.x2, wall.y2) not in existing_features:
                existing_features.append((wall.x2, wall.y2))
                self.features.append(self.Feature(wall.x2, wall.y2))

    # Author: Jannick Smeets
    # Description: Randomly distributes particles within the confines of the map
    def simulate_dust(self, amount):
        lower_range = (self.width*0.1, self.height*0.1)
        upper_range = (self.width*0.1+self.height*0.8, self.height*0.1+self.height*0.8)

        for n in range(amount):
            self.dust_particles.append(self.DustParticle(random.randint(lower_range[0], upper_range[0]), random.randint(lower_range[1], upper_range[1])))

            
