import pygame, random, math

pygame.font.init()

from .robot import Robot
from .target import Target
from .physics_world import PhysicsManager

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

        self.robot = Robot((200, 200), 0, (20, 30))
        self.robot.init(self.physics_manager)

        self.targets = []
        self.num_targets = num_targets
        for t in range(num_targets):
            self.targets.append(Target((random.randint(200, 400), random.randint(200, 400)), random.random() * 360, (10, 10)))
            self.targets[t].init(self.physics_manager)

    # draws grid to show positions more clearly
    def draw_grid(self, size: list, color: tuple):
        tile_size = size
        length = math.ceil(self.screen.get_width() / tile_size[0]) + 2
        height = math.ceil(self.screen.get_height() / tile_size[1]) + 2
        for x in range(length):
            pygame.draw.line(self.screen, color, ((x - 1) * tile_size[0] - (self.scroll[0] % tile_size[0]), 0), ((x - 1) * tile_size[0] - (self.scroll[0] % tile_size[0]), self.screen.get_height()))
        for y in range(height):
            pygame.draw.line(self.screen, color, (0, (y - 1) * tile_size[1] - (self.scroll[1] % tile_size[1])), (self.screen.get_width(), (y - 1) * tile_size[1] - (self.scroll[1] % tile_size[1])))
    
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
        
        self.screen.blit(self.font.render(f"Step: {self.step}", False, (255, 255, 255), (0, 0, 0)), (0, 0))
    
    def tick(self, display=False) -> pygame.Surface | None:
        """
        Executes one frame. Returns pygame.Surface if display is set to True
        """
        self.update()
        self.step += 1

        if display:
            self.draw()
            return self.screen