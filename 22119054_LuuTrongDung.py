import pygame
import random
import numpy as np
from collections import deque
import math


class GameAI:
    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Game AI")
        self.fps = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.menu = True
        self.createMap = False
        self.isDragging = False
        self.mouseThroughRect = []
        self.rectMenu = [
            pygame.Rect(500, 100, 200, 100),
            pygame.Rect(500, 300, 200, 100),
            pygame.Rect(500, 500, 200, 100),
        ]
        self.textMenu = ["Start", "Create Map", "Exit"]
        self.textCreateMap = [
            "Press and drag the mouse to",
            "select the region",
            "after selected a region",
            "Press 1 to set the start position",
            "Press 2 to set the end position",
            "Press 3 to create a wall",
            "Press 4 to delete",
        ]
        self.sizeMap = [29, 29]
        self.rectMap = []
        self.running = True
        self.time = 0
        self.start = False
        self.end = False
        self.map = np.ones((self.sizeMap[0], self.sizeMap[1]), dtype=int)
        self.sizeImage = [27, 27]
        self.posStart = [5, 5]
        self.posEnd = [26, 19]
        self.movePlayer = 0
        self.player = [5, 5]
        self.textPlayer = "Player"
        self.vec = [0, 0]
        self.playerFinish = False
        self.activeAllBots = [pygame.rect.Rect(870, 200, 20, 20), (255, 0, 0), False]
        self.info = {
            "dfs": [
                [],
                0,
                False,
                pygame.transform.scale(
                    pygame.image.load("images/dfs.png"),
                    (self.sizeImage[0], self.sizeImage[1]),
                ),
                (255, 0, 0),
                pygame.rect.Rect(870, 1 * 100 + 150, 20, 20),
                False,
                "Dfs",
            ],
            "bfs": [
                [],
                0,
                False,
                pygame.transform.scale(
                    pygame.image.load("images/bfs.png"),
                    (self.sizeImage[0], self.sizeImage[1]),
                ),
                (255, 0, 0),
                pygame.rect.Rect(870, 2 * 100 + 150, 20, 20),
                False,
                "Bfs",
            ],
            "hillclimbing": [
                [],
                0,
                False,
                pygame.transform.scale(
                    pygame.image.load("images/hillclimbing.png"),
                    (self.sizeImage[0], self.sizeImage[1]),
                ),
                (255, 0, 0),
                pygame.rect.Rect(870, 3 * 100 + 150, 20, 20),
                False,
                "Hcb",
            ],
            # "greedy": [[], 0, False, pygame.transform.scale(pygame.image.load("images/greedy.png"), (self.sizeImage[0], self.sizeImage[1])), (255, 0, 0), pygame.rect.Rect(870, 3*100 + 150, 20, 20), False, "Greedy"],
            # "aStar": [[], 0, False, pygame.transform.scale(pygame.image.load("images/astar.png"), (self.sizeImage[0], self.sizeImage[1])), (255, 0, 0), pygame.rect.Rect(870, 5*100 + 150, 20, 20), False, "A*"]
        }

        self.dx = 45
        self.dy = 10
        self.images = [
            pygame.transform.scale(
                pygame.image.load("images/finish.png"),
                (self.sizeImage[0], self.sizeImage[1]),
            ),
            pygame.transform.scale(
                pygame.image.load("images/10.png"),
                (self.sizeImage[0], self.sizeImage[1]),
            ),
            pygame.transform.scale(
                pygame.image.load("images/player.png"),
                (self.sizeImage[0], self.sizeImage[1]),
            ),
            pygame.transform.scale(pygame.image.load("images/bg.png"), (1220, 800)),
        ]

    # Algorithm
    def Dfs(self):
        self.info["dfs"][0].append(tuple(self.posStart))
        depth = [tuple(self.posStart)]
        moves = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        visited = set()
        visited.add(tuple(self.posStart))

        while self.info["dfs"][0][-1] != tuple(self.posEnd):
            x, y = self.info["dfs"][0][-1]
            foundMove = False
            random.shuffle(moves)
            random.shuffle(moves)
            for d in moves:
                nx, ny = x + d[0], y + d[1]
                if 0 <= nx < self.sizeMap[0] and 0 <= ny < self.sizeMap[1]:
                    if (nx, ny) not in visited and self.map[nx][ny] != 1:
                        visited.add((nx, ny))
                        self.info["dfs"][0].append((nx, ny))
                        depth.append((nx, ny))
                        foundMove = True
                        break

            if not foundMove:
                if depth:
                    depth.pop()
                if depth:
                    self.info["dfs"][0].append(depth[-1])
                else:
                    break

    def Bfs(self):
        queue = deque([tuple(self.posStart)])
        visited = set()
        visited.add(tuple(self.posStart))
        parent = {}
        parent[tuple(self.posStart)] = None
        moves = [(0, -1), (-1, 0), (0, 1), (1, 0)]

        while queue:
            x, y = queue.popleft()
            if (x, y) == tuple(self.posEnd):
                break
            random.shuffle(moves)
            for d in moves:
                nx, ny = x + d[0], y + d[1]

                if 0 <= nx < self.sizeMap[0] and 0 <= ny < self.sizeMap[1]:
                    if (nx, ny) not in visited and self.map[nx][ny] != 1:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        parent[(nx, ny)] = (x, y)

        current = tuple(self.posEnd)
        while current:
            self.info["bfs"][0].append(current)
            try:
                current = parent[current]
            except:
                return False
        self.info["bfs"][0].reverse()
        return True

    def Heuristic(self, current):
        return abs(current[0] - self.posEnd[0]) + abs(current[1] - self.posEnd[1])

    def FindIntersection(self, current, visited):
        moves = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        temp = []

        for d in moves:
            x, y = current[0] + d[0], current[1] + d[1]
            if (
                0 <= x < self.sizeMap[0]
                and 0 <= y < self.sizeMap[1]
                and (x, y) not in visited
                and self.map[x][y] == 0
            ):
                temp.append([x, y])
                visited.add(tuple([x, y]))

        intersection = None

        for i in temp:
            path = [i]
            count = None

            while count != 0:
                x, y = path[-1]
                count = 0
                a = None

                for d in moves:
                    nx, ny = x + d[0], y + d[1]
                    if (
                        0 <= nx < self.sizeMap[0]
                        and 0 <= ny < self.sizeMap[1]
                        and (nx, ny) not in visited
                        and self.map[nx][ny] == 0
                    ):
                        if [nx, ny] == self.posEnd:
                            return [[nx, ny], 0, path[:]]
                        count += 1
                        a = [nx, ny]

                if count >= 2:
                    heuristic = self.Heuristic([x, y])
                    if intersection is None or intersection[1] > heuristic:
                        intersection = [[x, y], heuristic, path[:]]
                    break
                elif count == 1:
                    visited.add(tuple(a))
                    path.append(a)
        return intersection

    def Hillclimbing(self):
        visited = set()
        visited.add(tuple(self.posStart))
        current = self.posStart
        self.info["hillclimbing"][0].append(tuple(current))

        while True:
            a = self.FindIntersection(current, visited)
            if a is None:
                return
            elif a[1] == 0:
                for i in a[2]:
                    self.info["hillclimbing"][0].append(tuple(i))
                self.info["hillclimbing"][0].append(tuple(self.posEnd))
                return
            current = a[0]
            for i in a[2]:
                self.info["hillclimbing"][0].append(tuple(i))
            visited.add(tuple(current))

    def Greedy(self):
        pass

    def AStar(self):
        pass

    ## Stactic Display
    def CreateMap(self):
        moves = [(0, -2), (-2, 0), (0, 2), (2, 0)]
        stack = []
        self.map[self.posStart[0]][self.posStart[1]] = 0
        self.map[self.posEnd[0]][self.posEnd[1]] = 0
        random.shuffle(moves)
        for dx, dy in moves:
            nx, ny = self.posStart[0] + dx, self.posStart[1] + dy
            if 1 <= nx < self.sizeMap[0] - 1 and 1 <= ny < self.sizeMap[1] - 1:
                self.map[nx][ny] = 0
                self.map[self.posStart[0] + dx // 2][self.posStart[1] + dy // 2] = 0
                stack.append([nx, ny])

        self.map[self.posStart[0] + 3][self.posStart[1]] = 0
        self.map[self.posStart[0] - 3][self.posStart[1]] = 0

        while stack:
            random.shuffle(moves)
            random.shuffle(moves)
            x, y = stack[-1]
            for i in moves:
                nx, ny = x + i[0], y + i[1]
                if nx == self.posEnd[0] and ny == self.posEnd[1]:
                    return

                if (
                    1 <= nx < self.sizeMap[0] - 1
                    and 1 <= ny < self.sizeMap[1] - 1
                    and self.map[nx][ny] == 1
                ):
                    self.map[nx][ny] = 0
                    self.map[x + (i[0] // 2)][y + (i[1] // 2)] = 0
                    stack.append([nx, ny])
                    break
            else:
                stack.pop()

    def CheckCreateMap(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not self.isDragging:
                self.isDragging = True

            elif event.type == pygame.MOUSEBUTTONUP and self.isDragging:
                self.isDragging = False

            elif event.type == pygame.MOUSEMOTION and self.isDragging:
                mousePos = pygame.mouse.get_pos()
                for row in self.rectMap:
                    for rect in row:
                        if (
                            rect.collidepoint(mousePos)
                            and rect not in self.mouseThroughRect
                        ):
                            self.mouseThroughRect.append(rect)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    if self.Bfs():
                        self.Dfs()
                        self.Hillclimbing()
                        self.menu = False
                        self.createMap = False
                    else:
                        font = pygame.font.Font(None, 80)
                        font.bold = True
                        textRender = font.render("No Way", True, (255, 0, 0))
                        self.win.blit(
                            textRender, ((1200 - textRender.get_size()[0]) // 2, 400)
                        )
                        pygame.display.update()
                        pygame.time.delay(2000)
                elif event.key == pygame.K_ESCAPE and self.createMap:
                    self.map = np.ones((self.sizeMap[0], self.sizeMap[1]), dtype=int)
                    self.createMap = False
                    self.posStart = [5, 5]
                    self.posEnd = [26, 19]

                elif (
                    event.key == pygame.K_1
                    and not self.isDragging
                    and len(self.mouseThroughRect) == 1
                ):
                    for i in range(0, len(self.rectMap)):
                        for j in range(0, len(self.rectMap)):
                            if self.rectMap[i][j] == self.mouseThroughRect[0]:
                                self.map[self.posStart[0]][self.posStart[1]] = 0
                                self.posStart[0] = i
                                self.posStart[1] = j
                                self.player[0] = j
                                self.player[1] = i
                                self.map[self.posStart[0]][self.posStart[1]] = 0
                                self.start = False
                                self.mouseThroughRect.clear()
                                return

                elif (
                    event.key == pygame.K_2
                    and not self.isDragging
                    and len(self.mouseThroughRect) == 1
                ):
                    for i in range(0, len(self.rectMap)):
                        for j in range(0, len(self.rectMap)):
                            if self.rectMap[i][j] == self.mouseThroughRect[0]:
                                self.map[self.posEnd[0]][self.posEnd[1]] = 0
                                self.posEnd[0] = i
                                self.posEnd[1] = j
                                self.map[self.posEnd[0]][self.posEnd[1]] = 0
                                self.end = False
                                self.mouseThroughRect.clear()
                                return

                elif (
                    event.key == pygame.K_3
                    and not self.isDragging
                    and len(self.mouseThroughRect) > 0
                ):
                    for i in range(0, len(self.rectMap)):
                        for j in range(0, len(self.rectMap)):
                            if self.rectMap[i][j] in self.mouseThroughRect:
                                self.map[i][j] = 1
                    self.mouseThroughRect.clear()
                elif (
                    event.key == pygame.K_4
                    and not self.isDragging
                    and len(self.mouseThroughRect) > 0
                ):
                    for i in range(0, len(self.rectMap)):
                        for j in range(0, len(self.rectMap)):
                            if self.rectMap[i][j] in self.mouseThroughRect:
                                self.map[i][j] = 0
                    self.mouseThroughRect.clear()

    def RenderMenu(self):
        self.win.blit(self.images[3], (0, 0))
        for i in range(0, len(self.rectMenu)):
            self.font.bold = False
            textRender = self.font.render(self.textMenu[i], True, (0, 0, 0))
            size = textRender.get_size()
            self.win.blit(
                textRender,
                (
                    400 + (400 - size[0]) / 2,
                    self.rectMenu[i].centery - textRender.get_size()[1] // 2,
                ),
            )

    def RenderText(self):
        rect = pygame.rect.Rect(
            self.dx + self.sizeImage[0] * self.sizeMap[0] + 20,
            0,
            self.win.get_size()[0]
            - (55 + self.dx + self.sizeImage[0] * self.sizeMap[0]),
            800,
        )
        pygame.draw.rect(self.win, (10, 10, 10), rect, 2, 5)
        self.font.bold = False
        textRender = self.font.render(
            "Time: " + str(self.time // 60) + "s", True, (0, 0, 0)
        )
        self.win.blit(
            textRender, (rect.centerx - textRender.get_size()[0] // 2, self.dy)
        )
        pygame.draw.rect(
            self.win, (self.activeAllBots[1]), self.activeAllBots[0], 10, 4
        )
        dy = 0
        textRender = self.font.render(self.textPlayer, True, (0, 0, 0))
        self.win.blit(textRender, (self.sizeImage[0] * self.sizeMap[0] + 130, dy + 147))
        if not self.playerFinish:
            self.win.blit(
                self.images[2], (self.sizeImage[0] * self.sizeMap[0] + 270, dy + 145)
            )
        for i, j in self.info.items():
            dy += 100
            textRender = self.font.render(self.info[i][7], True, (0, 0, 0))
            self.win.blit(
                textRender, (self.sizeImage[0] * self.sizeMap[0] + 130, dy + 147)
            )
            if not self.info[i][2]:
                pygame.draw.rect(self.win, self.info[i][4], self.info[i][5], 10, 4)
                self.win.blit(
                    self.info[i][3],
                    (self.sizeImage[0] * self.sizeMap[0] + 270, dy + 145),
                )

    def RenderTextCreateMap(self):
        font = pygame.font.Font(None, 28)
        pygame.draw.rect(self.win, (255, 0, 0), pygame.rect.Rect(870, 120, 305, 200), 3)
        for i in range(0, len(self.textCreateMap)):
            textRender = font.render(self.textCreateMap[i], True, (0, 0, 0))
            if i > 1:
                self.win.blit(textRender, (880, i * 20 + 170))
            else:
                self.win.blit(textRender, (880, i * 20 + 130))

    def CheckMouseMenu(self, mousePos, click):
        cursorHand = False
        for i in range(0, len(self.rectMenu)):
            if self.rectMenu[i].collidepoint(mousePos) and click:
                if i == 0:
                    self.map = np.ones((self.sizeMap[0], self.sizeMap[1]), dtype=int)
                    self.menu = False
                    self.CreateMap()
                    self.Dfs()
                    self.Bfs()
                    self.Hillclimbing()
                    # self.Greedy()
                    # print(self.info["hillclimbing"][0])
                    # self.AStart()
                elif i == 1:
                    self.map = np.zeros((self.sizeMap[0], self.sizeMap[1]), dtype=int)
                    self.createMap = True
                    for i in range(0, self.sizeMap[0]):
                        temp = []
                        for j in range(0, self.sizeMap[1]):
                            temp.append(
                                pygame.Rect(
                                    j * self.sizeImage[0] + self.dx,
                                    i * self.sizeImage[1] + self.dy,
                                    self.sizeImage[1],
                                    self.sizeImage[1],
                                )
                            )
                        self.rectMap.append(temp)
                    return
                elif i == 2:
                    self.running = False

            if self.rectMenu[i].collidepoint(mousePos):
                self.font.bold = True
                cursorHand = True
                textRender = self.font.render(self.textMenu[i], True, (255, 165, 0))
                size = textRender.get_size()
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.win.blit(
                    textRender,
                    (
                        400 + (400 - size[0]) / 2,
                        self.rectMenu[i].centery - textRender.get_size()[1] // 2,
                    ),
                )

        if not cursorHand:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    ## Logic
    def MovePlayer(self):
        if self.map[self.player[1] + self.vec[1]][
            self.player[0] + self.vec[0]
        ] == 0 and (self.vec[0] != 0 or self.vec[1] != 0):
            self.movePlayer += 1
            self.player[0] += self.vec[0]
            self.player[1] += self.vec[1]

        if (
            self.player[0] == self.posEnd[1]
            and self.player[1] == self.posEnd[0]
            and not self.playerFinish
        ):
            self.textPlayer += "  STEP: " + str(self.movePlayer)
            self.playerFinish = True

    def CheckWinBot(self):
        for i, j in self.info.items():
            if self.info[i][1] == len(self.info[i][0]) - 1 and not self.info[i][2]:
                if self.info[i][0][-1] == tuple(self.posEnd):
                    self.info[i][7] += " YES STEP: " + str(len(self.info[i][0]) - 1)
                    self.info[i][2] = True
                else:
                    self.info[i][7] += " NO STEP: " + str(len(self.info[i][0]) - 1)
                    self.info[i][2] = True

    def CheckOnBot(self, mousePos):
        if self.activeAllBots[0].collidepoint(mousePos):
            if self.activeAllBots[2]:
                self.activeAllBots[1] = (255, 0, 0)
                self.activeAllBots[2] = False
                for i, j in self.info.items():
                    self.info[i][4] = (255, 0, 0)
                    self.info[i][6] = False

            elif not self.activeAllBots[2]:
                self.activeAllBots[1] = (0, 255, 0)
                self.activeAllBots[2] = True
                for i, j in self.info.items():
                    self.info[i][4] = (0, 255, 0)
                    self.info[i][6] = True
            return
        for i, j in self.info.items():
            if self.info[i][5].collidepoint(mousePos):
                if self.info[i][6]:
                    self.info[i][4] = (255, 0, 0)
                    self.info[i][6] = False
                elif not self.info[i][6]:
                    self.info[i][4] = (0, 255, 0)
                    self.info[i][6] = True

    def MoveBots(self):
        for i, j in self.info.items():
            if not self.info[i][2] and self.info[i][6] and self.time % 10 == 0:
                self.info[i][1] += 1

    def CheckEndGame(self):
        if self.playerFinish:
            for i, j in self.info.items():
                if not self.info[i][2]:
                    return False

            textRender = self.font.render("End Game", True, (255, 0, 0))
            self.win.blit(
                textRender,
                (
                    (self.win.get_size()[0] - textRender.get_size()[0]) // 2,
                    (self.win.get_size()[1] - textRender.get_size()[1]) // 2,
                ),
            )
            pygame.display.update()
            return True

        return False

    ## Dynamic Display
    def DrawRectMap(self):
        pygame.draw.rect(
            self.win,
            (10, 10, 10),
            (self.dx - 10, 0, self.sizeMap[0] * self.sizeImage[0] + 20, 800),
            2,
            5,
        )
        for i in range(0, len(self.rectMap)):
            for j in range(0, len(self.rectMap)):
                if self.rectMap[i][j] in self.mouseThroughRect:
                    pygame.draw.rect(self.win, (0, 200, 0), self.rectMap[i][j], 16, 5)

                elif not self.start and [i, j] == self.posStart:
                    pygame.draw.rect(
                        self.win, (30, 144, 255), self.rectMap[i][j], 16, 5
                    )

                elif not self.end and [i, j] == self.posEnd:
                    pygame.draw.rect(self.win, (0, 0, 128), self.rectMap[i][j], 16, 5)

                elif self.map[i][j] == 1:
                    pygame.draw.rect(self.win, (220, 20, 60), self.rectMap[i][j], 16, 5)

                pygame.draw.rect(self.win, (0, 0, 0), self.rectMap[i][j], 1, 5)

    def DrawMap(self):
        pygame.draw.rect(
            self.win,
            (10, 10, 10),
            (self.dx - 10, 0, self.sizeMap[0] * self.sizeImage[0] + 20, 800),
            2,
            5,
        )
        for i in range(0, self.sizeMap[0]):
            for j in range(0, self.sizeMap[1]):
                if self.map[i][j] == 1:
                    self.win.blit(
                        self.images[1],
                        (
                            j * self.sizeImage[0] + self.dx,
                            i * self.sizeImage[1] + self.dy,
                        ),
                    )
                else:
                    pygame.draw.rect(
                        self.win,
                        (0, 0, 0),
                        pygame.rect.Rect(
                            j * self.sizeImage[0] + self.dx,
                            i * self.sizeImage[1] + self.dy,
                            self.sizeImage[0],
                            self.sizeImage[1],
                        ),
                        1,
                        3,
                    )

        self.win.blit(
            self.images[0],
            (
                self.posEnd[1] * self.sizeImage[0] + self.dx,
                self.posEnd[0] * self.sizeImage[1] + self.dy,
            ),
        )

    def DrawPlayer(self):
        self.win.blit(
            self.images[2],
            (
                self.player[0] * self.sizeImage[0] + self.dx,
                self.player[1] * self.sizeImage[1] + self.dy,
            ),
        )

    def DrawBot(self):
        for i, j in self.info.items():
            self.win.blit(
                j[3],
                (
                    j[0][j[1]][1] * self.sizeImage[0] + self.dx,
                    j[0][j[1]][0] * self.sizeImage[1] + self.dy,
                ),
            )

    ##
    def Run(self):
        while self.running:
            if not self.menu:
                self.vec[0], self.vec[1] = 0, 0
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                    if event.type == pygame.KEYDOWN:
                        if not self.playerFinish:
                            if event.key == pygame.K_a:
                                self.vec[0] = -1
                            elif event.key == pygame.K_d:
                                self.vec[0] = 1
                            elif event.key == pygame.K_w:
                                self.vec[1] = -1
                            elif event.key == pygame.K_s:
                                self.vec[1] = 1

                        if event.key == pygame.K_ESCAPE and not self.menu:
                            self.menu = True
                            for i, j in self.info.items():
                                self.info[i][0].clear()
                                self.info[i][1] = 0
                                self.info[i][2] = False
                                self.info[i][6] = False
                                self.info[i][4] = (255, 0, 0)
                            break

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mousePos = pygame.mouse.get_pos()
                        self.CheckOnBot(mousePos)

                if self.menu:
                    continue

                if self.CheckEndGame():
                    pygame.time.delay(5000)
                    self.running = False

                self.win.fill((240, 248, 255))
                self.DrawMap()
                self.DrawBot()
                self.CheckWinBot()
                self.MovePlayer()
                self.DrawPlayer()
                self.MoveBots()
                self.RenderText()
                self.fps.tick(60)
                self.time += 1
            else:
                if self.createMap:
                    self.win.fill((240, 248, 255))
                    self.DrawRectMap()
                    self.RenderTextCreateMap()
                    self.CheckCreateMap()
                    pygame.display.update()
                    continue

                self.RenderMenu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    mousePos = pygame.mouse.get_pos()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.CheckMouseMenu(mousePos, True)
                self.CheckMouseMenu(mousePos, False)
            pygame.display.update()


if "__main__" == __name__:
    run = GameAI()
    run.Run()
