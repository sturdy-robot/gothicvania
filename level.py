import pygame
from player import Player


class Level:
    def __init__(self, leveldata, window):
        self.player = pygame.sprite.GroupSingle(Player((400, 300), window))
        self.level = leveldata
        self.window = window

    def update(self):
        self.player.update()
        self.player.draw(self.window)
