import pygame
from pygame.sprite import AbstractGroup

import pyganim
from debug_status import DEBUG_STATUS
from utils import find_file


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, window: pygame.Surface, *groups: AbstractGroup):
        super().__init__(*groups)
        self.window = window

        # Animations
        self.animations = self._get_images()
        self._get_left_images()
        self.current_animation = self.animations["idle_right"]

        # Player Sprite and Rect
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(bottomleft=pos)

        # Collision
        self.debug_rect = pygame.Rect(self.rect.topleft, (38, self.rect.height))
        self.collision_debug = pygame.Surface(self.debug_rect.size)

        # Player variables
        self.player_speed = 5.0
        self.gravity = 0.8
        self.jump_speed = -20
        self.direction = pygame.math.Vector2(0, 0)

        # Player status
        self.facing_right = True
        self.walking = False
        self.jumping = False
        self.attacking = False
        self.on_ground = False
        self.on_ceiling = False

        # Debug status
        self.debug = DEBUG_STATUS

    def _get_images(self):
        # images = self.extract_images(find_file('warrior.png'), rows=17, cols=6)
        # return {
        #     "idle_right": self.__get_image_and_remove_from_list(images, 6, time=.2),
        #     "run_right": self.__get_image_and_remove_from_list(images, 8),
        #     "attack_right": self.__get_image_and_remove_from_list(images, 12, time=.05, loop=False),
        #     "death_right": self.__get_image_and_remove_from_list(images, 11, time=.5),
        #     "hurt_right": self.__get_image_and_remove_from_list(images, 4),
        #     "jump_right": self.__get_image_and_remove_from_list(images, 3, time=.6),
        # }
        # old sprites
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
        """Flips the player sprites from the right to left"""
        animations = {}
        for animation_key, animation in self.animations.items():
            new_key = animation_key.replace("right", "left")
            animations[new_key] = animation.get_copy()
            animations[new_key].flip(True, False)
            animations[new_key].make_transforms_permanent()

        self.animations.update(animations)

    @staticmethod
    def extract_images(image, rows=1, cols=1):
        return pyganim.get_images_from_sprite_sheet(image, rows=rows, cols=cols)

    def __get_image_and_remove_from_list(self, images: list, amount: int, time=.1, loop=True):
        """Gets images and removes them from the list."""
        imgs = []
        for i in range(amount):
            img = images[i]
            imgs.append(img)

        for img in imgs:
            images.remove(img)

        frames = [(img, time) for img in imgs]
        return pyganim.PygAnimation(frames, loop)

    def __extract_images_with_row_col_division(self, image, rows=1, cols=1):
        """Gets spritesheets and divides them into rows.
        Useful for sprites that have a defined amount of cols for animations.
        """
        images = pyganim.get_images_from_sprite_sheet(image, rows=rows, cols=cols)
        k, m = divmod(len(images), cols)
        return [
            images[i * k + min(i, m): (i + 1) * k + min(i + 1, m)]
            for i in range(cols)
        ]

    def __get_spritesheet_rows(self, list_images: list, row: int, time=.1, loop=True):
        frames = [(img, time) for img in list_images[row]]
        return pyganim.PygAnimation(frames, loop=loop)

    def _divide_spritesheet(self, image, rows=1, cols=None, time=.1, loop=True):
        """Get images from spritesheet, turning them into Pyganimation object."""
        images = self.extract_images(image, rows, cols)
        frames = [(img, time) for img in images]
        return pyganim.PygAnimation(frames, loop=loop)

    def set_animation(self, animation):
        animation = f"{animation}_right" if self.facing_right else f"{animation}_left"
        self.current_animation = self.animations[animation]

    def get_input(self):
        keys = pygame.key.get_pressed()

        if not self.attacking:
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.facing_right = True
                if self.on_ground:
                    self.walking = True
                self.set_animation("run")
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.facing_right = False
                if self.on_ground:
                    self.walking = True
                self.set_animation("run")
            else:
                self.direction.x = 0
                self.walking = False
                self.attacking = False
                if self.on_ground:
                    self.set_animation("idle")

        if keys[pygame.K_q]:
            self.direction.x = 0
            self.attacking = True
            self.walking = False
            self.set_animation("attack")

        if keys[pygame.K_SPACE] and self.on_ground:
            self.attacking = False
            self.walking = False
            self.jumping = True
            self.set_animation("jump")
            self.jump()

        if not self.current_animation.is_finished():
            self.current_animation.play()

        self.rect.size = self.image.get_size()

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def debug_code(self):
        self.debug_rect.size = self.rect.size
        self.debug_rect.x = self.rect.x
        self.debug_rect.y = self.rect.y
        self.collision_debug = pygame.Surface(self.debug_rect.size)
        pygame.draw.rect(self.window, 'red', self.debug_rect, 1)

    def jump(self):
        self.direction.y = self.jump_speed

    def check_animation(self):
        if (
                self.current_animation
                in
                [
                    self.animations["attack_right"],
                    self.animations["attack_left"],
                    self.animations["jump_right"],
                    self.animations["jump_left"]
                ]
                and self.current_animation.is_finished()
        ):
            self.attacking = False
            self.jumping = False
            self.current_animation.stop()

        self.image = self.current_animation.get_current_frame()

    def move(self):
        self.rect.x += self.direction.x * self.player_speed

    def update(self):
        self.get_input()
        self.move()
        self.check_animation()
        if self.debug:
            self.debug_code()
        self.window.blit(self.image, self.rect)
