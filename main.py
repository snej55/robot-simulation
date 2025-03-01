import pygame, sys, time
from robot import Robot

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((500, 500))
        self.dt = 1
        self.last_time = time.time() - 1 / 60
        self.clock = pygame.time.Clock()
        self.running = True

        self.robot = Robot((50, 50), 0, (10, 20))
    
    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def update(self):
        pass

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.robot.angle += 1 * self.dt
        self.robot.draw(self.screen, (0, 0))

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
            self.clock.tick()

if __name__ == '__main__':
    App().run()
