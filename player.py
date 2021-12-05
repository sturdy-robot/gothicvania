import pygame
import pyganim
from utils import find_file
from pygame.sprite import AbstractGroup


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, window, *groups: AbstractGroup):
        super().__init__(*groups)
        self.window = window
        self.animations = self._get_images()
        self._get_left_images()
        self.current_animation = self.animations["idle_right"]
        self.image = self.current_animation.getCurrentFrame()
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.player_speed = 4
        self.facing = True
        self.attacking = True

    def _get_images(self):
        return {
            "idle_right": self._divide_spritesheet(find_file('gothic-hero-idle.png'), cols=4, time=.25),
            "run_right": self._divide_spritesheet(find_file('gothic-hero-run.png'), cols=12),
            "jump_right": self._divide_spritesheet(find_file('gothic-hero-jump.png'), cols=5),
            "attack_right": self._divide_spritesheet(find_file('gothic-hero-attack.png'), cols=6),
            "hurt_right": self._divide_spritesheet(find_file('gothic-hero-hurt.png'), cols=3),
            "jump_attack_right": self._divide_spritesheet(find_file('gothic-hero-jump-attack.png'), cols=6),
            "jump_climb_right": self._divide_spritesheet(find_file('gothic-hero-jump.png'), cols=7),
        }

    def _get_left_images(self):
        animations = {}
        for animation_key, animation in self.animations.items():
            new_key = animation_key.replace("right", "left")
            animations[new_key] = animation.getCopy()
            animations[new_key].flip(True, False)
            animations[new_key].makeTransformsPermanent()

        self.animations.update(animations)

    @staticmethod
    def _divide_spritesheet(image, rows=1, cols=None, time=.1):
        images = pyganim.getImagesFromSpriteSheet(image, rows=rows, cols=cols)
        frames = [(img, time) for img in images]
        return pyganim.PygAnimation(frames)

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.current_animation = self.animations["run_right"]
            self.facing = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.current_animation = self.animations["run_left"]
            self.facing = False
        else:
            self.direction.x = 0
            if self.facing:
                self.current_animation = self.animations["idle_right"]
            else:
                self.current_animation = self.animations["idle_left"]

    def update(self):
        self.get_input()
        self.rect.x += self.direction.x * self.player_speed
        if not self.current_animation.isFinished():
            self.current_animation.play()
        self.image = self.current_animation.getCurrentFrame()
        self.window.blit(self.image, self.rect)
