import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d

FRICTION = 0.7

# a class for managing the physics of the robots & target
class PhysicsManager:
    def __init__(self, arena_width, arena_height) -> None:
       # set up pymunk
        self.space = pymunk.Space()
        self.space.iterations = 10
        self.space.sleep_time_threshold = 0.5

        self.static_body = self.space.static_body
        self.init(arena_width, arena_height)

        self.draw_options = None

    def init(self, width, height) -> None:
        # set up arena
        shape = pymunk.Segment(self.static_body, (1, 1), (1, height), 1.0)
        self.space.add(shape)
        shape.elasticity = 1
        shape.friction = 1

        shape = pymunk.Segment(self.static_body, (width, 1), (width, height), 1.0)
        self.space.add(shape)
        shape.elasticity = 1
        shape.friction = 1

        shape = pymunk.Segment(self.static_body, (1, 1), (width, 1), 1.0)
        self.space.add(shape)
        shape.elasticity = 1
        shape.friction = 1

        shape = pymunk.Segment(self.static_body, (1, height), (width, height), 1.0)
        self.space.add(shape)
        shape.elasticity = 1
        shape.friction = 1
    
    @staticmethod
    def get_pos(x, y):
        return Vec2d(x, y)

    def add_box(self, size, mass, pos: Vec2d):
        body = pymunk.Body()
        self.space.add(body)

        body.position = pos

        shape = pymunk.Poly.create_box(body, size, 0.0)
        shape.mass = mass
        shape.friction = FRICTION
        self.space.add(shape)

        return shape
    
    def update(self, time_step):
        # update bodies
        self.space.step(time_step)
    
    def set_draw_options(self, surf):
        self.draw_options = pymunk.pygame_util.DrawOptions(surf)
        return self.draw_options

    def draw(self, screen):
        if not self.draw_options:
            self.set_draw_options(screen)
        self.space.debug_draw(self.draw_options)