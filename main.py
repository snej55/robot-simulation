import math
import pygame
import time
import sys
import multiprocessing
import os
import pickle
import neat
import tomllib

from scripts.scene import Scene
from scripts.logging import Logger

pygame.font.init()

NUM_TARGETS = 1
RUNS_PER_NET = 5
SCR_WIDTH = 640
SCR_HEIGHT = 640
SAVE_NETS = True

global run_num
run_num = 0

class App:
    """
    Manager for the scenes
    """
    def __init__(self):
        self.screen = pygame.display.set_mode((640, 640))
        self.dt = 1
        self.last_time = time.time() - 1 / 60
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.Font(pygame.font.match_font("hack"), 20)

        self.cap_fps = False
        self.show_debug_joints = False
        self.scene_num = 0

        self.scenes = []
        
        self.scene = Scene(width=self.screen.get_width(), height=self.screen.get_height(), num_targets=NUM_TARGETS)

        self.scene_surf = pygame.Surface((0, 0))

        # NEAT stuff
        self.pop = None # population
        self.pe = None # population evaluator
        self.config = None
        
        # logging
        self.log_file = None
        self.default_stdout = sys.stdout

        self.load_cache()
    
    def load_cache(self):
        try:
            with open("cache.toml", "rb") as f:
                data = tomllib.load(f)
                global run_num
                run_num = int(data["run"]["RUN_NUM"])
        except FileNotFoundError:
            with open("cache.toml", "w") as f:
                f.write(
                    """
                    [run]
                    RUN_NUM = 0
                    """
                )
    
    def init_log(self, local_log_path):
        local_dir = os.path.dirname(__file__)
        log_path = os.path.join(local_dir, local_log_path)
        self.log_file = open(log_path, "w")
        sys.stdout = self.log_file

    def end_log(self):
        sys.stdout = self.default_stdout
        self.log_file.close()
    
    @staticmethod
    def evaluate_genome(genome, config):
        print("Evaluating genome ", genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        print("Created net...")
        fitnesses = []

        for run in range(RUNS_PER_NET):
            sim = Scene(width=SCR_WIDTH, height=SCR_HEIGHT, num_targets=NUM_TARGETS)
            fitness = 1000.0
            while sim.step < 1000.0:
                fitness = 1000.0 - sim.step
                inputs = sim.get_net_inputs()
                output = net.activate(inputs)
                # print(f"Output: {output}")

                if not sim.get_ready():
                    if output[2] >= 0.5:
                        fitness -= 4.0

                surf = sim.tick(output, True)
                
                # check distance
                target = sim.get_closest_target()
                if target:
                    if target.distance < sim.robot.dimensions[0] * 0.7:
                        fitness += 200
                        break
            
            target = sim.get_closest_target()
            fitness += SCR_WIDTH + SCR_HEIGHT
            if target:
                fitness -= target.distance
            else:
                fitness -= SCR_WIDTH + SCR_HEIGHT
            fitnesses.append(max(0, fitness))

            print(f"Run: {run}")

        net_dir = os.path.join(os.path.dirname(__file__), "/nets/")
        global run_num
        run_path = f"R-{run_num}"
        if not (run_path in os.listdir(net_dir)):
            os.mkdir(run_path)
        with open(os.path.join(net_dir, f"/{id(genome)}")) as f:
            pass
        
        return min(fitnesses)

    @staticmethod
    def evaluate_genomes(genomes, config):
        for genome_id, genome in genomes:
            App.evaluate_genome(genome, config)

    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def update(self, NN=None):
        self.scene.draw_debug_joints = self.show_debug_joints
        output = ()
        if NN:
            inputs = self.scene.get_net_inputs()
            output = NN.activate(inputs)

        self.scene_surf = self.scene.tick(output, True)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.scene_surf, (0, 0))
        
        font_surf = self.font.render(f"Scene No.{self.scene_num}", False, (255, 200, 200), (0, 0, 0))
        self.screen.blit(font_surf, (0, self.screen.get_height() - font_surf.get_height()))
    
    def loadNN(self):
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config.conf')
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)
        
        self.pop = neat.Population(self.config)
        stats = neat.StatisticsReporter()
        self.pop.add_reporter(stats)
        self.pop.add_reporter(neat.StdOutReporter(True))

        self.pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), self.evaluate_genome)

    def trainNN(self):
        print("Running...")
        winner = self.pop.run(self.pe.evaluate, 100)

        with open('winner-feedforward', 'wb') as f:
            pickle.dump(winner, f)
        
        self.winner = winner
    
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
                    if event.key == pygame.K_f:
                        self.scene.see()

            self.draw()
            self.update(NN=self.winner)

            pygame.display.set_caption(f'Robot Simulation at {self.clock.get_fps() :.1f} FPS. Scene No. {self.scene_num}')
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    logger = Logger()
    sys.stdout = logger
    app = App()
    app.loadNN()
    app.trainNN()
    app.run()
    logger.close()