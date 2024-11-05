import pygame


class GameAI:
    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((1300, 800))
        pygame.display.set_caption("Game AI")
        self.fps = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.water = [
            [
                pygame.transform.scale(pygame.image.load(f"images/w{i}.png"), (27, 27))
                for i in range(1, 4)
            ],
            0,
        ]
        self.time = 0

    def Run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            if self.water[1] == 3:
                self.water[1] = 0
            self.win.fill((100, 100, 255))
            self.win.blit(self.water[0][self.water[1]], (100, 100))
            self.win.blit(self.water[0][self.water[1]], (100, 127))
            self.win.blit(self.water[0][self.water[1]], (100, 154))
            if self.time % 15 == 0:
                self.water[1] += 1

            self.fps.tick(60)
            self.time += 1
            pygame.display.update()


if "__main__" == __name__:
    run = GameAI()
    run.Run()
