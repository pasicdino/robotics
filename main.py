import pygame
import math
from Robot import Robot
from Map import Map

pygame.init()

WIDTH, HEIGHT = 800, 800
FPS = 60 #might need to play with this & power var when handling collisions

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Simulation")

# Create font object
font = pygame.font.SysFont(None, 16)

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Initialize Map and Robot
map_instance = Map()
map_instance.add_square_walls(100, 100, 600)  #Basic map with square walls
robot = Robot(WIDTH // 2, HEIGHT // 2, 100)

# Main loop
running = True
clock = pygame.time.Clock()

# Visualization (adjust for debug)
sensor_lines_visible = True
sensor_values_always_visible = False

while running:
    #limit framerate
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #Control engine using NUMPAD: we can go forward and backward for each motor so take 4,1 as forward/backward for left motor and 6,3 for right motor
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_KP4:
                robot.left_motor(True, True)  #Turn on left motor FORWARD
            if event.key == pygame.K_KP1:
                robot.left_motor(True, False)  #Turn on left motor BACKWARD
            if event.key == pygame.K_KP6:
                robot.right_motor(True, True)  #Turn on right motor FORWARD
            if event.key == pygame.K_KP3:
                robot.right_motor(True, False)  #Turn on right moto BACKWARD
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_KP4, pygame.K_KP1]:
                robot.left_motor(False, True)  #Turn off left_motor
            if event.key in [pygame.K_KP6, pygame.K_KP3]:
                robot.right_motor(False, True)  #Turn off right moto



    #Update robot position and orientation
    robot.update(dt, map_instance.walls)
    robot.update_sensors(map_instance.walls)



    screen.fill(WHITE)

    # Draw walls
    for wall in map_instance.walls:
        pygame.draw.line(screen, BLACK, (wall.x1, wall.y1), (wall.x2, wall.y2), 2)

    #Draw robot + line indicating forward
    pygame.draw.circle(screen, RED, (int(robot.x), HEIGHT - int(robot.y)), robot.radius)
    end_x = robot.x + robot.radius * math.cos(robot.orientation)
    end_y = HEIGHT - (robot.y + robot.radius * math.sin(robot.orientation))
    pygame.draw.line(screen, BLACK, (int(robot.x), HEIGHT - int(robot.y)), (int(end_x), int(end_y)), 2)

    # Draw sensor lines + distance text
    for sensor in robot.sensors:
        if sensor_lines_visible:
            pygame.draw.line(screen, GREEN, (int(sensor.start_coord[0]), HEIGHT - int(sensor.start_coord[1])), (int(sensor.end_coord[0]), int(HEIGHT - sensor.end_coord[1])), 1)
        if sensor_values_always_visible or int(sensor.distance < sensor.init_distance):
            distance_text = font.render(str(int(sensor.distance)), True, BLUE)
            text_rect = distance_text.get_rect(center=(int(sensor.text_coord[0]), HEIGHT - int(sensor.text_coord[1])))
            screen.blit(distance_text, text_rect)

    force_scale = 1  # Adjust this based on how visibly long you want the force vector
    force_end_x = robot.x + robot.velocity_vector[0] * force_scale
    force_end_y = HEIGHT - (robot.y + robot.velocity_vector[1] * force_scale)
    pygame.draw.line(screen, BLUE, (int(robot.x), HEIGHT - int(robot.y)), (int(force_end_x), int(force_end_y)), 2)
    pygame.display.flip()

pygame.quit()
