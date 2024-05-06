import math
from shapely.geometry import LineString, Point

class WallSensor:
    # Author: Jannick Smeets
    # Description: Class representing a sensor of the robot for detecting walls

    def __init__(self, degrees, robot):
        self.angle = math.radians(degrees)  
        self.robot = robot
        self.length = 120
        self.text_pos = 10

        self.init_distance = self.length-robot.radius
        self.distance = self.init_distance

        self.start_coord = []
        self.end_coord = []
        self.text_coord = []

        self.sensor_line = None
        
        self.update_lines()


    def update_lines(self):
        #calculate start coordinates of sensor
        start_x = self.robot.x + self.robot.radius * math.cos(self.robot.orientation + self.angle)
        start_y = self.robot.y + self.robot.radius * math.sin(self.robot.orientation + self.angle)
        
        #calculate end coordinates of sensor
        end_x = self.robot.x + self.length * math.cos(self.robot.orientation + self.angle)
        end_y = self.robot.y + self.length * math.sin(self.robot.orientation + self.angle)

        #calculates location where to put distance as text
        text_x = self.robot.x + (self.robot.radius + self.text_pos) * math.cos(self.robot.orientation + self.angle)
        text_y = self.robot.y + (self.robot.radius + self.text_pos) * math.sin(self.robot.orientation + self.angle)

        self.start_coord = [start_x, start_y]
        self.end_coord = [end_x, end_y]
        self.text_coord = [text_x, text_y]

        #LineString used for finding intersection
        self.sensor_line = LineString([(self.robot.x, self.robot.y), (self.end_coord[0], self.end_coord[1])])

    def check_intersect(self, walls):
        wall_distances = [self.init_distance] * len(walls)  #list of distances to all walls from sensor

        for idx, wall in enumerate(walls):
            intersection = self.sensor_line.intersection(wall.line)     #finds intersection between wall and sensor line

            if intersection:
                wall_distances[idx] = self.calc_distance(intersection.coords[0], self.start_coord)  #calcs distance between intersection and start point of sensor (the robot)
            else:
                wall_distances[idx] = self.init_distance    #sets distance back to initial distance

        self.distance = min(wall_distances) #finds smallest distance of sensor to any wall

    def calc_distance(self, p1, p2):
        #Calculates distance between two points
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            

class FeatureSensor:
    # Author: Jannick Smeets
    # Description: Class representing the omni-directional sensor of the robot for detecting features

    def __init__(self, sensor_length, robot):
        self.robot = robot
        self.length = sensor_length

    #Senses for features within sensor range and calculates relative bearing
    def sense_features(self, map_walls, map_features):
        detected_features = []
        for feature_idx, feature in enumerate(map_features):
            exact_distance = Point(self.robot.x, self.robot.y).distance(feature.point)  #Distance between robot and feature
            if exact_distance < self.length:
                if self.check_intersect(feature, map_walls):
                    vector = (feature.x - self.robot.x, feature.y - self.robot.y)
                    bearing = math.atan2(vector[0], vector[1])  #Bearing relative to map perspective (in radians)
                    relative_bearing = (bearing + self.robot.orientation - math.pi/2) % 2*math.pi #Bearing relative to robot orientation (-π/2 offset)
                    detected_features.append([exact_distance, relative_bearing, feature])
        return detected_features

    #Checks if line of sight from robot to detected feature is intersected by wall
    def check_intersect(self, feature, map_walls):
        line_of_sight = LineString([(self.robot.x, self.robot.y),(feature.x, feature.y)])
        for wall in map_walls:
            if not feature.point.intersection(wall.line):
                if line_of_sight.intersection(wall.line):
                    return False
        return True
