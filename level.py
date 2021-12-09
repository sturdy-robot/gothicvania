import pygame
import pymunk
from player import Player
from tile import Tile


class Level:
    def __init__(self, leveldata, window):
        self.space = pymunk.Space()
        self.space.gravity = (0, 1)
        self.player = pygame.sprite.GroupSingle(Player((400, 300), window))
        self.level = leveldata
        self.window = window
        self.platform = pygame.sprite.Group()
        self.platform.add(Tile((0, 500), self.window))
        self.space.add(self.player.sprite.body, self.player.sprite.shape)
        for sprite in self.platform.sprites():
            self.space.add(sprite.body, sprite.shape)

    def update(self):
        self.space.step(1/60)
        self.platform.draw(self.window)
        self.player.update()
        self.player.draw(self.window)
