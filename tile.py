import pygame
import pymunk


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, window):
        super().__init__()
        self.image = pygame.Surface((800, 80))
        self.image.fill('black')
        self.rect = self.image.get_rect(topleft=pos)
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = pos[0], pos[1]
        self.shape = pymunk.Poly.create_box(self.body, size=self.rect.size)
        self.window = window
        self.shape.friction = 0.18