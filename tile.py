import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, window):
        super().__init__()
        self.image = pygame.Surface((800, 80))
        self.image.fill('green')
        self.rect = self.image.get_rect(topleft=pos)
        self.window = window

