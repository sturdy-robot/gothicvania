import pygame
import pymunk

from player import Player
from tile import Tile


class Level:
    def __init__(self, leveldata, window):
        self.space = pymunk.Space()
        self.space.gravity = (0, 500)
        self.player = pygame.sprite.GroupSingle(Player((0, 0), window))
        self.level = leveldata
        self.window = window
        self.platform = pygame.sprite.Group()
        self.platform.add(Tile((300, 500), self.window))
        for sprite in self.platform.sprites():
            self.space.add(sprite.body, sprite.shape, self.player.sprite.body, self.player.sprite.shape)
        self.coll_handler = self.space.add_default_collision_handler()
        self.coll_handler.pre_solve = self.col_pre_solve
        self.coll_handler.begin = self.col_begin
        self.coll_handler.post_solve = self.col_post
        self.coll_handler.separate = self.col_separate
        self.font = pygame.font.Font(None, 20)
        self.debug_messages = []

    @staticmethod
    def col_pre_solve(arbiter, space, data):
        print("pre_solve")
        return True

    @staticmethod
    def col_begin(arbiter, space, data):
        print("begin")
        return True

    @staticmethod
    def col_post(arbiter, space, data):
        print("post")
        return True

    @staticmethod
    def col_separate(arbiter, space, data):
        print("separate")
        return True

    def display_debug(self, info, y=10, x=780):
        display_surf = pygame.display.get_surface()
        debug_surf = self.font.render(str(info), True, 'white', 'black')
        debug_rect = debug_surf.get_rect(topright=(x, y))
        display_surf.blit(debug_surf, debug_rect)

    def get_debug_messages(self):
        self.debug_messages.append(self.player.sprite.body.position)
        self.debug_messages.append((self.player.sprite.rect.x, self.player.sprite.rect.y))
        self.debug_messages.append([
            self.player.sprite.rect.topleft,
            self.player.sprite.rect.bottomleft,
            self.player.sprite.rect.topright,
            self.player.sprite.rect.bottomright
        ])
        for v in self.player.sprite.shape.get_vertices():
            x, y = v.rotated(self.player.sprite.shape.body.angle) + self.player.sprite.shape.body.position
            self.debug_messages.append((int(x), int(y)))
        for sprite in self.platform.sprites():
            self.debug_messages.append(sprite.body.position)
            self.debug_messages.append((sprite.rect.x, sprite.rect.y))
            self.debug_messages.append(sprite.rect.size)
            self.debug_messages.append([
                sprite.rect.topleft,
                sprite.rect.bottomleft,
                sprite.rect.topright,
                sprite.rect.bottomright
            ])
            for v in sprite.shape.get_vertices():
                x, y = v.rotated(sprite.shape.body.angle) + sprite.shape.body.position
                self.debug_messages.append((int(x), int(y)))

    def update(self):
        self.space.step(1/60)
        self.space.reindex_shapes_for_body(self.player.sprite.body)
        self.platform.draw(self.window)
        self.player.update()
        self.player.draw(self.window)
        self.get_debug_messages()
        for i, debug_message in enumerate(self.debug_messages):
            self.display_debug(debug_message, i * 18)
        self.debug_messages.clear()
