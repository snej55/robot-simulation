import pygame, math

class Target:
    def __init__(self, pos: pygame.Vector2, angle: float, dimensions: pygame.Vector2):
        self.pos = pygame.Vector2(pos)
        self.angle = angle
        self.dimensions = pygame.Vector2(dimensions)

    def get_center(self) -> pygame.Vector2:
        rect = pygame.Rect(self.pos, self.dimensions)
        center_pos = pygame.Vector2(rect.centerx, rect.centery)
        return center_pos

    # basically the same as Robot().draw(...)
    def draw(self, screen: pygame.Surface, scroll: pygame.Vector2) -> None:
        scroll = pygame.Vector2(scroll)
        surf = pygame.Surface(self.dimensions)
        surf.fill((125, 150, 125))
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
        
        # draw lines for direction (useful for debugging)
        center_pos = self.get_center()
        line_length = self.dimensions.y / 2 # we don't want this one to jut out
        pygame.draw.line(screen, (255, 255, 0), (center_pos.x - scroll.x, center_pos.y - scroll.y), (center_pos.x - scroll.x + math.cos(math.radians(self.angle + 90)) * line_length, center_pos.y - scroll.y - math.sin(math.radians(self.angle + 90)) * line_length))
        pygame.draw.line(screen, (0, 255, 255), (center_pos.x - scroll.x - math.cos(math.radians(self.angle)) * (self.dimensions.x / 2), center_pos.y - scroll.y + math.sin(math.radians(self.angle)) * (self.dimensions.x / 2)),
                                              (center_pos.x - scroll.x + math.cos(math.radians(self.angle)) * (self.dimensions.x / 2), center_pos.y - scroll.y - math.sin(math.radians(self.angle)) * (self.dimensions.x / 2)))