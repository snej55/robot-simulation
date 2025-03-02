import pygame
import time
import sys

from scripts.scene import Scene

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 640))
        self.dt = 1
        self.last_time = time.time() - 1 / 60
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene = Scene()

    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def update(self):
        pass

    def draw(self):
        pass
    
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

            surf = self.scene.tick()

            self.screen.blit(surf, (0, 0))

            pygame.display.set_caption(f'FPS: {self.clock.get_fps() :.1f}')
            pygame.display.flip()
            self.clock.tick()

if __name__ == '__main__':
    App().run()
