import pygame, sys, time, math, random
from scripts.robot import Robot
from scripts.target import Target

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 640))
        self.dt = 1
        self.last_time = time.time() - 1 / 60
        self.clock = pygame.time.Clock()
        self.running = True

        self.robot = Robot((200, 200), 0, (20, 30))
        self.target = Target((random.randint(200, 400), random.randint(200, 400)), random.random() * 360, (10, 10))

        self.scroll = pygame.Vector2(0, 0)

    # draws grid to show positions more clearly
    def draw_grid(self, size: list, color: tuple):
        tile_size = size
        length = math.ceil(self.screen.get_width() / tile_size[0]) + 2
        height = math.ceil(self.screen.get_height() / tile_size[1]) + 2
        for x in range(length):
            pygame.draw.line(self.screen, color, ((x - 1) * tile_size[0] - (self.scroll[0] % tile_size[0]), 0), ((x - 1) * tile_size[0] - (self.scroll[0] % tile_size[0]), self.screen.get_height()))
        for y in range(height):
            pygame.draw.line(self.screen, color, (0, (y - 1) * tile_size[1] - (self.scroll[1] % tile_size[1])), (self.screen.get_width(), (y - 1) * tile_size[1] - (self.scroll[1] % tile_size[1])))
    
    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def update(self):
        self.robot.set_left_motor(60)
        self.robot.update_motors()

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.draw_grid([20, 20], (220, 220, 220))

        # target
        self.target.draw(self.screen, self.scroll)

        # robot
        self.robot.draw(self.screen, self.scroll)

        if (self.robot.colliding_point(pygame.Vector2(pygame.mouse.get_pos()))):
            pygame.draw.rect(self.screen, (255, 0, 0), (self.screen.get_width() - 100, self.screen.get_height() - 100, 100, 100))
    
    def run(self):
        while self.running:
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.close()

            self.draw()
            self.update()

            pygame.display.set_caption(f'FPS: {self.clock.get_fps() :.1f}')
            pygame.display.flip()
            self.clock.tick(1)

if __name__ == '__main__':
    App().run()
