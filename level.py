import pygame

from player import Player
from tile import Tile


class Level:
    def __init__(self, leveldata, window):
        # Level-related data
        self.gravity = -1
        self.level = leveldata

        # Window to draw
        self.window = window

        # Sprites and sprite groups
        self.platform = pygame.sprite.Group()
        self.platform.add(Tile((0, 520), self.window))
        self.player = pygame.sprite.GroupSingle(Player((15, 200), window))

        # Debug-related info
        self.font = pygame.font.Font(None, 20)
        self.debug_messages = []

    def display_debug(self, info, y=10, x=780):
        display_surf = pygame.display.get_surface()
        debug_surf = self.font.render(str(info), True, 'white', 'black')
        debug_rect = debug_surf.get_rect(topright=(x, y))
        display_surf.blit(debug_surf, debug_rect)

    def get_debug_messages(self):
        # Get player debug messages
        self.debug_messages.append((self.player.sprite.rect.x, self.player.sprite.rect.y))
        self.debug_messages.append([
            self.player.sprite.rect.topright,
            self.player.sprite.rect.bottomright,
            self.player.sprite.rect.bottomleft,
            self.player.sprite.rect.topleft
        ])

        # Get tile debug messages
        for sprite in self.platform.sprites():
            self.debug_messages.append((sprite.rect.x, sprite.rect.y))
            self.debug_messages.append(sprite.rect.size)
            self.debug_messages.append([
                sprite.rect.topright,
                sprite.rect.bottomright,
                sprite.rect.bottomleft,
                sprite.rect.topleft
            ])

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collision_sprites = self.platform.sprites()

        for sprite in collision_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def update(self):
        self.vertical_movement_collision()
        # Update sprites
        self.platform.draw(self.window)
        self.player.update()
        self.player.draw(self.window)

        # Debug messages
        self.get_debug_messages()
        for i, debug_message in enumerate(self.debug_messages):
            self.display_debug(debug_message, i * 18)
        self.debug_messages.clear()
