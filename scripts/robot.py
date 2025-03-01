# class for robot in robot simulation
import pygame, math

class Robot:
    def __init__(self, pos: pygame.Vector2, angle: float, dimensions: pygame.Vector2) -> None:
        self.pos = pygame.Vector2(pos)
        self.angle = angle
        self.dimensions = pygame.Vector2(dimensions)

        # left & right motor values to simulate real life robot
        self.motor_left = 0.0
        self.motor_right = 0.0
    
    def stop(self) -> None:
        self.motor_left = 0.0
        self.motor_right = 0.0
    
    def set_left_motor(self, val) -> None:
        # max analog value for motor is 255
        self.motor_left = max(0, min(val, 255))

    def set_right_motor(self, val) -> None:
        # "" ""
        self.motor_right = max(0, min(val, 255))

    def get_center(self) -> pygame.Vector2:
        rect = pygame.Rect(self.pos, self.dimensions)
        center_pos = pygame.Vector2(rect.centerx, rect.centery)
        return center_pos

    @staticmethod
    def rotate(point: pygame.Vector2, angle: float, center: pygame.Vector2) -> pygame.Vector2:
        """
        Rotates a 2D coordinate around a pivot point\n
        Point: point to rotate around\n
        Angle: angle to rotate by in degrees\n
        Center: pivot point
        """
        angle = math.radians(angle)
        # sin & cos values
        s = math.sin(angle)
        c = math.cos(angle)

        # tranform to be relative to origin
        point.x -= center.x
        point.y -= center.y

        # rotate around origins
        new_x = point.x * c - point.y * s
        new_y = point.x * s + point.y * c

        # move back to center
        point.x = new_x + center.x
        point.y = new_y + center.y

        return point
    
    def colliding_point(self, point: pygame.Vector2) -> bool:
        # define rect to collide with
        rect = pygame.Rect(self.pos, self.dimensions)
        # define pos to rotate point around (pivot point)
        center_pos = pygame.Vector2(rect.centerx, rect.centery)
        # point to collide with
        collide_point = self.rotate(point, self.angle, center_pos)
        # check for actual collision
        return rect.collidepoint(collide_point.x, collide_point.y)
    
    def update_motors(self) -> None:
        pass

    def draw(self, screen: pygame.Surface, scroll: pygame.Vector2) -> None:
        scroll = pygame.Vector2(scroll)
        surf = pygame.Surface(self.dimensions)
        surf.fill((100, 100, 100))
        """
        We don't need a colorkey in the general sense, but
        otherwise pygame.transform.rotate() will fill in any
        gaps with the average value from the surface (white)
        """
        surf.set_colorkey((255, 255, 255))
        rot_surf = pygame.transform.rotate(surf, self.angle)
        # draw rotated rect
        screen.blit(rot_surf, (self.pos.x - scroll.x - rot_surf.get_width() / 2 + surf.get_width() / 2,
                               self.pos.y - scroll.y - rot_surf.get_height() / 2 + surf.get_height() / 2))
        
        # draw lines for direction
        center_pos = self.get_center()
        line_length = self.dimensions.y / 2 + 10
        pygame.draw.line(screen, (255, 0, 0), (center_pos.x - scroll.x, center_pos.y - scroll.y), (center_pos.x - scroll.x + math.cos(math.radians(self.angle + 90)) * line_length, center_pos.y - scroll.y - math.sin(math.radians(self.angle + 90)) * line_length))
        pygame.draw.line(screen, (0, 0, 255), (center_pos.x - scroll.x - math.cos(math.radians(self.angle)) * (self.dimensions.x / 2), center_pos.y - scroll.y + math.sin(math.radians(self.angle)) * (self.dimensions.x / 2)),
                                              (center_pos.x - scroll.x + math.cos(math.radians(self.angle)) * (self.dimensions.x / 2), center_pos.y - scroll.y - math.sin(math.radians(self.angle)) * (self.dimensions.x / 2)))