import pygame
import math
from Robot import Robot
from Map import Map

pygame.init()

WIDTH, HEIGHT = 800, 800
FPS = 60 #No issues regarding collusions with this timestep & power combination so i suggest to just stick with this
#Might want to speed it up when doing some learning but we will cross that bridge when we get there

#Boilerplate pygame code
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Simulation")

font = pygame.font.SysFont(None, 16)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
running = True
clock = pygame.time.Clock()

#Init map, and robot
map = Map()
map.add_hexagon_walls(WIDTH // 2, HEIGHT // 2, 300)
map.extract_features()
robot = Robot(WIDTH // 2, HEIGHT // 2, 100)


#Enable or disable force vector sensor, sensor value, and motor value visibility
force_vector_visible = False
sensor_lines_visible = False
sensor_values_always_visible = False

def engine_control():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #Control engine using NUMPAD: we can go forward and backward for each motor so take 4,1 as forward/backward for left motor and 6,3 for right motor
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_KP4:
                robot.left_motor(True, True)  # Turn on left motor FORWARD
            if event.key == pygame.K_KP1:
                robot.left_motor(True, False)  # Turn on left motor BACKWARD
            if event.key == pygame.K_KP6:
                robot.right_motor(True, True)  # Turn on right motor FORWARD
            if event.key == pygame.K_KP3:
                robot.right_motor(True, False)  # Turn on right moto BACKWARD
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_KP4, pygame.K_KP1]:
                robot.left_motor(False, True)  # Turn off left_motor
            if event.key in [pygame.K_KP6, pygame.K_KP3]:
                robot.right_motor(False, True)  # Turn off right motor


def draw_walls():
    #Redraw map
    for wall in map.walls:
        pygame.draw.line(screen, BLACK, (wall.x1, wall.y1), (wall.x2, wall.y2), 2)

def draw_features():
    #Draw small black circle on each feature position
    for feature in map.features:
        pygame.draw.circle(screen, BLACK, (feature.x, feature.y), feature.radius, 0)


def draw_robot():
    #Draw robot + line indicating forward
    pygame.draw.circle(screen, RED, (int(robot.x), HEIGHT - int(robot.y)), robot.radius)
    end_x = robot.x + robot.radius * math.cos(robot.orientation)
    end_y = HEIGHT - (robot.y + robot.radius * math.sin(robot.orientation))
    pygame.draw.line(screen, BLACK, (int(robot.x), HEIGHT - int(robot.y)), (int(end_x), int(end_y)), 2)


def draw_sensors():
    #Draw sensor lines + distance text
    for sensor in robot.sensors:
        if sensor_lines_visible:
            pygame.draw.line(screen, GREEN, (int(sensor.start_coord[0]), HEIGHT - int(sensor.start_coord[1])),
                             (int(sensor.end_coord[0]), int(HEIGHT - sensor.end_coord[1])), 1)
        if sensor_values_always_visible or int(sensor.distance < sensor.init_distance):
            distance_text = font.render(str(int(sensor.distance)), True, BLUE)
            text_rect = distance_text.get_rect(center=(int(sensor.text_coord[0]), HEIGHT - int(sensor.text_coord[1])))
            screen.blit(distance_text, text_rect)


def draw_motor_values():
    motor_text_scale = robot.radius * 0.5
    left_motor_text_x = robot.x - motor_text_scale * math.sin(robot.orientation)
    left_motor_text_y = robot.y + motor_text_scale * math.cos(robot.orientation)
    right_motor_text_x = robot.x + motor_text_scale * math.sin(robot.orientation)
    right_motor_text_y = robot.y - motor_text_scale * math.cos(robot.orientation)
    left_motor_text = font.render(str(robot.v_left), True, BLACK)
    right_motor_text = font.render(str(robot.v_right), True, BLACK)
    left_text_rect = left_motor_text.get_rect(center=(int(left_motor_text_x), HEIGHT - int(left_motor_text_y)))
    right_text_rect = right_motor_text.get_rect(center=(int(right_motor_text_x), HEIGHT - int(right_motor_text_y)))
    screen.blit(left_motor_text, left_text_rect)
    screen.blit(right_motor_text, right_text_rect)


def draw_force_vector():
    #Draw force vector
    if force_vector_visible:
        force_scale = 1
        force_end_x = robot.x + robot.velocity_vector[0] * force_scale
        force_end_y = HEIGHT - (robot.y + robot.velocity_vector[1] * force_scale)
        pygame.draw.line(screen, BLUE, (int(robot.x), HEIGHT - int(robot.y)), (int(force_end_x), int(force_end_y)), 2)

def draw_feature_lines(detected_features):
    for feature in detected_features:
        pygame.draw.line(screen, GREEN, (int(feature.x), HEIGHT - int(feature.y)), ((int(robot.x), int(HEIGHT - robot.y))), 1)


while running:
    #limit framerate
    dt = clock.tick(FPS) / 1000.0

    engine_control()
    robot.update(dt, map.walls)
    robot.update_sensors(map.walls)
    detected_features = robot.sense_features(map.features)

    screen.fill(WHITE)

    draw_walls()
    draw_features()
    draw_feature_lines(detected_features)
    draw_robot()
    draw_sensors()
    draw_motor_values()
    draw_force_vector()

    pygame.display.flip()

pygame.quit()
