# class for robot in robot simulation
import pygame, math

DRAG = 0.0
SPEED = 1

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
        self.motor_left = max(0, min(val, 255)) * SPEED

    def set_right_motor(self, val) -> None:
        self.motor_right = max(0, min(val, 255)) * SPEED

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
        """
        Moves the robot.\n
        1. Calculate motor positions\n
        2. Update left & right motors\n
        3. Contrain left & right motor positions using verlet integration\n
        4. Calculate robot actual position
        """
        
        center_pos = self.get_center()
        angle = math.radians(self.angle)

        # calculate motor positions & directions
        # left and right sides of robot
        left_motor_pos = pygame.Vector2(center_pos.x - math.cos(angle) * (self.dimensions.x / 2), center_pos.y - math.sin(angle) * (self.dimensions.x / 2))
        right_motor_pos = pygame.Vector2(center_pos.x - math.cos(angle) * -(self.dimensions.x / 2), center_pos.y - math.sin(angle) * -(self.dimensions.x / 2))
        # vector perpendicular to vector between two motors
        motor_direction = right_motor_pos - left_motor_pos
        # normalize
        motor_direction = motor_direction.normalize()
        # get perpendicular vector (NOTE: take account for pygame's inverted coordinate system)
        motor_direction.rotate_ip(-90)
        motor_angle = math.atan2(motor_direction.y, motor_direction.x) # get the angle

        print(f"1. {right_motor_pos} {left_motor_pos}")

        # update left & right motor positions
        motor_left_val = self.motor_left + self.motor_right * DRAG
        left_motor_pos = self.rotate(left_motor_pos, motor_left_val, center_pos)
        # left_motor_pos.x += math.cos(motor_angle) * motor_left_val
        # left_motor_pos.y += math.sin(motor_angle) * motor_left_val

        motor_right_val = self.motor_right + self.motor_left * DRAG
        right_motor_pos = self.rotate(right_motor_pos, motor_right_val, center_pos)
        # right_motor_pos.x += math.cos(motor_angle) * motor_right_val
        # right_motor_pos.y += math.sin(motor_angle) * motor_right_val

        print(f"2. {right_motor_pos} {left_motor_pos}")

        # constrain motor positions
        dx, dy = right_motor_pos.x - left_motor_pos.x, right_motor_pos.y - left_motor_pos.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        difference = self.dimensions.x - distance
        percent = difference / max(0.0000001, distance)
        right_motor_pos.x += dx * percent
        right_motor_pos.y += dy * percent
        left_motor_pos.x -= dx * percent
        left_motor_pos.y -= dy * percent

        print(right_motor_pos, left_motor_pos, self.angle)

        # finally, update the robot
        # recalculate direction & center_pos
        motor_direction = right_motor_pos - left_motor_pos
        motor_direction = motor_direction.normalize()
        motor_direction.rotate_ip(-90)
        motor_angle = math.atan2(motor_direction.y, motor_direction.x)
        # update robot angle
        self.angle = motor_angle
        # get midpoint
        center_pos = left_motor_pos + (right_motor_pos - left_motor_pos) / 2
        # update position
        self.pos.x = center_pos.x - self.dimensions.x / 2
        self.pos.y = center_pos.y - self.dimensions.y / 2

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