import math
import random
import shapely
import numpy as np
from shapely.geometry import LineString, Point

class Map:
    # Author: Jannick Smeets, Dino Pasic
    # Description: Class representing the full map to be populated with walls and features

    class Wall:
        # Author: Dino Pasic
        # Description: Class that represents each wall within the map

        def __init__(self, x1, y1, x2, y2, is_outer=False):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.is_outer = is_outer

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

    def __init__(self, width, height, grid_size, tile_size, map_complexity):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.tile_size = tile_size

        self.grid_coordinates = []
        self.map_complexity = map_complexity

        self.walls = []
        self.features = []
        self.dust_particles = []

    # Author: Jannick Smeets
    # Description: Executes map generation steps
    def generate(self):
        self.create_grid()
        self.add_outer_walls()
        self.generate_wall(0, np.shape(self.grid_coordinates)[0]-1, 0, np.shape(self.grid_coordinates)[1]-1, 0, 0)
        self.extract_features()

    # Author: Jannick Smeets
    # Description: Creates matrix holding coordinates of grid points
    def create_grid(self):
        horizontal = np.arange(self.tile_size, self.width, self.tile_size)
        vertical = np.arange(self.tile_size, self.height, self.tile_size)
        self.grid_coordinates = np.array([[(x, y) for x in horizontal] for y in vertical])

    def add_wall(self, wall_start, wall_end, is_outer=False):
        self.walls.append(self.Wall(wall_start[0], self.height - wall_start[1], wall_end[0], self.height - wall_end[1], is_outer))

    def add_outer_walls(self):
        self.add_wall(self.grid_coordinates[0][0], self.grid_coordinates[0][-1], True)
        self.add_wall(self.grid_coordinates[0][-1], self.grid_coordinates[-1][-1], True)
        self.add_wall(self.grid_coordinates[-1][-1], self.grid_coordinates[-1][0], True)
        self.add_wall(self.grid_coordinates[-1][0], self.grid_coordinates[0][0], True)

    # Author: Jannick Smeets
    # Description: Recursively generates walls with gaps to create rooms within the map
    def generate_wall(self, v_low, v_high, h_low, h_high, direction, n):
        # stops recursion after certain amount or if wall generation not feasible due to bounds being too small
        if n == self.map_complexity or h_high - h_low <= 1 or v_high - v_low <= 1:
            return

        # randomize horizontal/vertical idx for wall/gap placement + gap size
        h_rand_idx = random.randint(h_low + 1, h_high - 1)
        v_rand_idx = random.randint(v_low + 1, v_high - 1)
        gap_size = random.randint(1, 2)
        
        # 0: vertical wall, 1: horizontal wall
        if direction == 0:
            self.add_wall(self.grid_coordinates[v_low, h_rand_idx], self.grid_coordinates[v_rand_idx, h_rand_idx])
            if (v_rand_idx + gap_size < v_high):
                self.add_wall(self.grid_coordinates[v_rand_idx + gap_size, h_rand_idx], self.grid_coordinates[v_high, h_rand_idx])

            # [recursion] divide area into two rooms, and repeat for horizontal wall
            self.generate_wall(v_low, v_high, h_low, h_rand_idx, 1, n+1)
            self.generate_wall(v_low, v_high, h_rand_idx, h_high, 1, n+1)
        elif direction == 1:
            self.add_wall(self.grid_coordinates[v_rand_idx, h_low], self.grid_coordinates[v_rand_idx, h_rand_idx])
            if (h_rand_idx + gap_size < h_high):
                self.add_wall(self.grid_coordinates[v_rand_idx, h_rand_idx + gap_size], self.grid_coordinates[v_rand_idx, h_high])
            
            # [recursion] divide area into two rooms, and repeat for vertical wall
            self.generate_wall(v_low, v_rand_idx, h_low, h_high, 0, n+1)
            self.generate_wall(v_rand_idx, v_high, h_low, h_high, 0, n+1)

    # Author: Jannick Smeets
    # Description: Calculates the initial coordinates of robot based on starting tile indices
    def calculate_initial_position(self, start_tile):
        # error handling if given starting tile is outside map bounds
        if any(i > j for i, j in zip(start_tile, self.grid_size)) or any(i < j for i, j in zip(start_tile, (1, 1))):
            if start_tile[0] > self.grid_size[0]:
                start_tile = (self.grid_size[0], start_tile[1])
            elif start_tile[0] < 1:
                start_tile = (0, start_tile[1])
            if start_tile[1] > self.grid_size[1]:
                start_tile = (start_tile[0], self.grid_size[1])
            elif start_tile[1] < 1:
                start_tile = (start_tile[0], 1)
            print("WARNING: initial position given was outside map bounds; Robot placed on tile {}.".format(start_tile))
        
        point = self.grid_coordinates[start_tile[1]-1][start_tile[0]-1]
        return (point[0] + (self.tile_size // 2), point[1] + (self.tile_size // 2))

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
    def simulate_dust(self, amount, robot):
        lower_range = self.grid_coordinates[0][0]
        upper_range = self.grid_coordinates[-1][-1]
        n = 0
        while n < amount:
            random_x = random.randint(lower_range[0], upper_range[0])
            random_y = random.randint(lower_range[1], upper_range[1])

            # makes sure that none of the particles fall on walls
            on_wall = False
            for wall in self.walls:
                if shapely.intersects(wall.line, Point(random_x, random_y)):
                    on_wall = True

            # also makes sure no dust is placed at robot's initial location
            if not on_wall and math.dist((robot.x, robot.y), (random_x, random_y)) > robot.radius:
                self.dust_particles.append(self.DustParticle(random_x, random_y))
                n += 1

            
    ## --- unused functions ---

    # def add_wall(self, x1, y1, x2, y2):
    #     self.walls.append(self.Wall(x1, self.height - y1, x2, self.height - y2))

    # def add_square_walls(self, x, y, size):
    #     self.add_wall(x, y, x + size, y)
    #     self.add_wall(x, y + size, x + size, y + size)
    #     self.add_wall(x, y, x, y + size)
    #     self.add_wall(x + size, y, x + size, y + size)

    # def populate_map(self, WIDTH, HEIGHT):
    #     self.add_square_walls(WIDTH*0.1, HEIGHT*0.1, HEIGHT*0.8)
    #     self.add_wall(WIDTH * 0.1, WIDTH * 0.2, HEIGHT * 0.3, HEIGHT * 0.2)
    #     self.add_wall(WIDTH * 0.3, HEIGHT * 0.5, WIDTH * 0.5, HEIGHT * 0.5)
    #     self.add_wall(WIDTH * 0.6, HEIGHT * 0.7, WIDTH * 0.9, HEIGHT * 0.7)
    #     self.add_wall(WIDTH * 0.2, HEIGHT * 0.6, WIDTH * 0.2, HEIGHT * 0.9)
    #     self.add_wall(WIDTH * 0.8, HEIGHT * 0.1, WIDTH * 0.8, HEIGHT * 0.6)
    #     self.add_wall(WIDTH * 0.4, HEIGHT * 0.2, WIDTH * 0.7, HEIGHT * 0.2)
    #     self.add_wall(WIDTH * 0.5, HEIGHT * 0.4, WIDTH * 0.5, HEIGHT * 0.7)
    #     self.add_wall(WIDTH * 0.7, HEIGHT * 0.3, WIDTH * 0.7, HEIGHT * 0.6)
    #     self.add_wall(WIDTH * 0.1, HEIGHT * 0.9, WIDTH * 0.4, HEIGHT * 0.9)
    #     self.add_wall(WIDTH * 0.5, HEIGHT * 0.1, WIDTH * 0.8, HEIGHT * 0.1)
    #     self.add_wall(WIDTH * 0.3, HEIGHT * 0.2, WIDTH * 0.3, HEIGHT * 0.5)

    # def add_hexagon_walls(self, center_x, center_y, size):
    #     #1/6th of a circle
    #     angle_step = math.pi / 3

    #     points = []

    #     for i in range(6):
    #         angle = angle_step * i
    #         x = center_x + size * math.cos(angle)
    #         y = center_y + size * math.sin(angle)
    #         points.append((x, y))

    #     for i in range(6):
    #         x1, y1 = points[i]
    #         x2, y2 = points[(i + 1) % 6]
    #         self.add_wall(x1, y1, x2, y2)
