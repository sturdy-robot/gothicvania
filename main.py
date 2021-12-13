import sys
import pygame
from level import Level


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((800, 600), pygame.SCALED)
        pygame.display.set_caption("Gothicvania")
        self.running = True
        self.level = None
        self.clock = pygame.time.Clock()

    def update(self):
        self.draw()
        self.level.update()

    def draw(self):
        self.window.fill('gray')

    def start(self):
        self.level = Level('data', self.window)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            self.clock.tick(60)
            self.update()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().start()
