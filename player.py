import pygame
import pyganim
from physics import KinematicBody
from utils import find_file
from pygame.sprite import AbstractGroup


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, window, *groups: AbstractGroup):
        super().__init__(*groups)
        self.window = window
        self.animations = self._get_images()
        self._get_left_images()
        self.current_animation = self.animations["idle_right"]
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.player_speed = 4
        self.body = KinematicBody(mass=10)
        self.facing_right = True
        self.walking = True
        self.attacking = False

    def _get_images(self):
        return {
            "idle_right": self._divide_spritesheet(find_file('gothic-hero-idle.png'), cols=4, time=.25),
            "run_right": self._divide_spritesheet(find_file('gothic-hero-run.png'), cols=12),
            "jump_right": self._divide_spritesheet(find_file('gothic-hero-jump.png'), cols=5, loop=False),
            "attack_right": self._divide_spritesheet(find_file('gothic-hero-attack.png'), cols=6, time=.05, loop=False),
            "hurt_right": self._divide_spritesheet(find_file('gothic-hero-hurt.png'), cols=3, loop=False),
            "jump_attack_right": self._divide_spritesheet(find_file('gothic-hero-jump-attack.png'), cols=6, loop=False),
            "jump_climb_right": self._divide_spritesheet(find_file('gothic-hero-jump.png'), cols=7, loop=False),
        }

    def _get_left_images(self):
        animations = {}
        for animation_key, animation in self.animations.items():
            new_key = animation_key.replace("right", "left")
            animations[new_key] = animation.get_copy()
            animations[new_key].flip(True, False)
            animations[new_key].make_transforms_permanent()

        self.animations.update(animations)

    @staticmethod
    def _divide_spritesheet(image, rows=1, cols=None, time=.1, loop=True):
        images = pyganim.get_images_from_sprite_sheet(image, rows=rows, cols=cols)
        frames = [(img, time) for img in images]
        return pyganim.PygAnimation(frames, loop=loop)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if not self.attacking:
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.current_animation = self.animations["run_right"]
                self.facing_right = True
                self.walking = True
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.current_animation = self.animations["run_left"]
                self.facing_right = False
                self.walking = True
            else:
                self.direction.x = 0
                self.walking = False
                self.attacking = False
                if self.facing_right:
                    self.current_animation = self.animations["idle_right"]
                else:
                    self.current_animation = self.animations["idle_left"]
        if keys[pygame.K_q]:
            self.direction.x = 0
            self.attacking = True
            self.walking = False
            if self.facing_right:
                self.current_animation = self.animations["attack_right"]
            else:
                self.current_animation = self.animations["attack_left"]

        if not self.current_animation.is_finished():
            self.current_animation.play()

    def update(self):
        self.get_input()
        self.rect.x += self.direction.x * self.player_speed
        if (
            self.current_animation
            in [self.animations["attack_right"], self.animations["attack_left"]]
            and self.current_animation.is_finished()
        ):
            self.attacking = False
            self.current_animation.stop()
        self.image = self.current_animation.get_current_frame()
        self.window.blit(self.image, self.rect)
