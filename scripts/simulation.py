from .scene import Scene

NUM_TARGETS = 1

class Simulation:
    def __init__(self, width, height):
        self.scene = Scene(num_targets=NUM_TARGETS, width=width, height=height)
    
    def step(self, output, disp=False):
        # output: (
        #   motor_left,
        #   motor_right,
        # )
        self.scene.set_motor_left(output[0])
        self.scene.set_motor_right(output[1])
        surf = self.scene.tick(display=disp)
        return surf