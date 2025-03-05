import pygame, random, math

import numpy as np

from dataclasses import dataclass

pygame.font.init()

from .robot import Robot
from .target import Target
from .physics_world import PhysicsManager

FOV = math.radians(80.0)
LOOK_TIME = 1 # 1 second to check the camera
STEP_RATE = 1/60

# marker info
@dataclass
class TargetInfo:
    distance: float
    bearing_y: float
    ID: int

class Scene:
    def __init__(self, num_targets=4, width=1000, height=640, draw_debug_joints=False):
        """
        Class to handle robot & targets simulation.\n
        display: toggles whether scene should by drawn\n
        num_targets: number of targets to display
        width: width of screen & arena
        height: height of screen & arena
        """
        self.screen = pygame.Surface((width, height))
        self.scroll = pygame.Vector2(0, 0)
        self.draw_debug_joints = draw_debug_joints # toggles whether pymunk debugging objects should be drawn
        self.paused = False
        self.step = 0

        self.font = pygame.font.Font(pygame.font.match_font("consolas"), 14)

        # physics
        self.physics_manager = PhysicsManager(self.screen.get_width(), self.screen.get_height())

        self.robot = Robot((random.random() * 100 + 10, random.random() + 100 + 10), 0, (20, 30))
        self.robot.init(self.physics_manager)

        self.targets = []
        self.num_targets = num_targets
        for t in range(num_targets):
            self.targets.append(Target((random.randint(100, width - 100), random.randint(100, height - 100)), random.random() * 360, (10, 10)))
            self.targets[t].init(self.physics_manager)
        
        self.stall = 1

    # draws grid to show positions more clearly
    def draw_grid(self, size: list, color: tuple):
        tile_size = size
        length = math.ceil(self.screen.get_width() / tile_size[0]) + 2
        height = math.ceil(self.screen.get_height() / tile_size[1]) + 2
        for x in range(length):
            pygame.draw.line(self.screen, color, ((x - 1) * tile_size[0] - (self.scroll[0] % tile_size[0]), 0), ((x - 1) * tile_size[0] - (self.scroll[0] % tile_size[0]), self.screen.get_height()))
        for y in range(height):
            pygame.draw.line(self.screen, color, (0, (y - 1) * tile_size[1] - (self.scroll[1] % tile_size[1])), (self.screen.get_width(), (y - 1) * tile_size[1] - (self.scroll[1] % tile_size[1])))
    
    def see(self) -> list[Target]:
        # self.stall = 0

        angle = self.robot.get_angle()
        upper_bound = math.radians(angle + FOV / 2)
        lower_bound = math.radians(angle - FOV / 2)

        targets_found = []
        for target in self.targets:
            angle2target = math.atan2(target.pos.y - self.robot.pos.y, target.pos.x - self.robot.pos.x)
            if lower_bound < angle2target < upper_bound:
                targets_found.append(target)
        
        return targets_found

    def get_ready(self) -> bool:
        # check if we're done checking sensors
        return self.stall > 1 / STEP_RATE

    def set_motor_left(self, val) -> None:
        if self.get_ready():
            self.robot.set_left_motor(val)
    
    def set_motor_right(self, val) -> None:
        if self.get_ready():
            self.robot.set_right_motor(val)
        
    def stop(self) -> None:
        if self.get_ready():
            self.robot.stop()

    def update(self):
        # self.robot.set_left_motor(-60)
        # self.robot.set_right_motor(60)
        speed = 255
        if pygame.key.get_pressed()[pygame.K_w]:
            self.robot.set_left_motor(speed)
        elif pygame.key.get_pressed()[pygame.K_s]:
            self.robot.set_left_motor(-speed)
        else:
            self.robot.set_left_motor(0)
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.robot.set_right_motor(speed)
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            self.robot.set_right_motor(-speed)
        else:
            self.robot.set_right_motor(0)
        
        self.robot.update_motors()
        
        for target in self.targets:
            target.update()

        self.physics_manager.update(1)

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.draw_grid([20, 20], (220, 220, 220))

        # target
        for target in self.targets:
            target.draw(self.screen, self.scroll)

        # robot
        self.robot.draw(self.screen, self.scroll)

        if self.draw_debug_joints:
            self.physics_manager.draw(self.screen)

        angle = ((self.robot.shape.body.angle + math.pi * 0.5) % (math.pi * 2)) - math.pi
        upper_bound = (angle + FOV / 2) % (math.pi * 2)
        lower_bound = (angle - FOV / 2) % (math.pi * 2)
        if upper_bound < lower_bound:
            lower_bound -= math.pi * 2
        # print(angle, upper_bound, lower_bound)
        robot_pos = self.robot.get_center()

        # debug drawing
        pygame.draw.line(self.screen, (0, 255, 0), robot_pos, (robot_pos[0] + math.cos(upper_bound) * 1000, robot_pos[1] + math.sin(upper_bound) * 1000))
        pygame.draw.line(self.screen, (0, 255, 0), robot_pos, (robot_pos[0] + math.cos(lower_bound) * 1000, robot_pos[1] + math.sin(lower_bound) * 1000))

        for target in self.targets:
            # in radians
            angle2target = math.atan2(target.pos.y - robot_pos[1], target.pos.x - robot_pos[0])
            anglediff = ((angle2target - angle + math.pi) % (math.pi * 2)) - math.pi
            print(f"angle2target: {angle2target}, anglediff: {anglediff}, angle: {angle}")
            if abs(anglediff) < FOV / 2:
                pygame.draw.line(self.screen, (0, 255, 255), robot_pos, (robot_pos[0] + math.cos(angle2target) * 1000, robot_pos[1] + math.sin(angle2target) * 1000))


        self.screen.blit(self.font.render(f"Step: {self.step}", False, (255, 255, 255), (0, 0, 0)), (0, 0))
    
    def get_closest_target(*targets) -> TargetInfo:
        pass
    
    def tick(self, display=False) -> pygame.Surface | None:
        """
        Executes one frame. Returns pygame.Surface if display is set to True
        """
        self.update()
        self.step += 1
        self.stall += STEP_RATE

        if display:
            self.draw()
            return self.screen
        return None