import pygame
import time
import sys

from scripts.scene import Scene

pygame.font.init()

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 640))
        self.dt = 1
        self.last_time = time.time() - 1 / 60
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.Font(pygame.font.match_font("hack"), 20)

        self.cap_fps = False
        self.show_debug_joints = False
        self.scene_num = 0

        self.scene = Scene()

        self.scene_surf = pygame.Surface((0, 0))

    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def update(self):
        self.scene.draw_debug_joints = self.show_debug_joints
        self.scene_surf = self.scene.tick(True)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.scene_surf, (0, 0))
        
        font_surf = self.font.render(f"Scene No.{self.scene_num}", False, (255, 200, 200), (0, 0, 0))
        self.screen.blit(font_surf, (0, self.screen.get_height() - font_surf.get_height()))
    
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
                    if event.key == pygame.K_f:
                        self.cap_fps = not self.cap_fps
                    if event.key == pygame.K_k:
                        self.scene_num += 1
                    if event.key == pygame.K_j:
                        self.scene_num -= 1
                    if event.key == pygame.K_e:
                        self.show_debug_joints = not self.show_debug_joints

            self.draw()
            self.update()

            pygame.display.set_caption(f'Robot Simulation at {self.clock.get_fps() :.1f} FPS. Scene No. {self.scene_num}')
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    App().run()
