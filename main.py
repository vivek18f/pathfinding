import pygame
import math
from queue import PriorityQueue

from pygame.constants import K_ESCAPE

#window initialization
WIDTH = 800
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding")

#colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self, row, col, width, totalRows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.totalRows = totalRows

    def getPos(self):
        return self.row, self.col

    def isClosed(self):
        return self.color == TURQUOISE

    def isOpen(self):
        return self.color == YELLOW

    def isBarrier(self):
        return self.color == BLACK

    def isStart(self):
        return self.color == GREEN
    
    def isEnd(self):
        return self.color == RED
    
    def reset(self):
        self.color = WHITE

    def makeStart(self):
        self.color = GREEN

    def makeClosed(self):
        self.color = TURQUOISE
    
    def makeOpen(self):
        self.color = YELLOW

    def makeBarrier(self):
        self.color = BLACK
    
    def makeEnd(self):
        self.color = RED

    def makePath(self):
        self.color = BLUE
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width))

    def updateNeighbors(self, grid):
        self.neighbors = []
        if self.row < self.totalRows-1 and not grid[self.row+1][self.col].isBarrier(): #down
            self.neighbors.append(grid[self.row+1][self.col])
            
        if self.row > 0  and not grid[self.row-1][self.col].isBarrier(): #up
            self.neighbors.append(grid[self.row-1][self.col])

        if self.col < self.totalRows-1 and not grid[self.row][self.col+1].isBarrier(): #right
            self.neighbors.append(grid[self.row][self.col+1])

        if self.col > 0 and not grid[self.row][self.col-1].isBarrier(): #left
            self.neighbors.append(grid[self.row][self.col-1])

    def __lt__(self, other):
        return False
        
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)

def reconstructPath(cameFrom, current, grid, rows, width):
    while current in cameFrom:
        current = cameFrom[current]
        current.makePath()
        draw(screen, grid, rows, width)

def algorithm(grid, start, end, rows, width):
    count = 0
    pq = PriorityQueue()
    pq.put((0, count, start))
    cameFrom  = {}
    gScore = {node: float("inf") for row in grid for node in row}
    gScore[start] = 0
    fScore = {node: float("inf") for row in grid for node in row}
    fScore[start] = h(start.getPos(), end.getPos())

    pqHash = {start}

    while not pq.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
        
        current = pq.get()[2]
        pqHash.remove(current)

        if current == end:
            reconstructPath(cameFrom, end, grid, rows, width)
            start.makeStart()
            end.makeEnd()
            return True
        
        for neighbor in current.neighbors:
            tempGScore = gScore[current] + 1

            if tempGScore < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tempGScore
                fScore[neighbor] = tempGScore + h(neighbor.getPos(), end.getPos())

                if neighbor not in pqHash:
                    count += 1
                    pq.put((fScore[neighbor], count, neighbor))
                    pqHash.add(neighbor)
                    neighbor.makeOpen()
        
        draw(screen, grid, rows, width)

        if current != start:
            current.makeClosed()

    return False

def makeGrid(rows, width):
    grid = []
    gap = width // rows
    for i in range (rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    
    return grid

def drawGrid(screen, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(screen, GRAY, (0, i*gap), (width, i*gap))
    for j in range(rows):
        pygame.draw.line(screen, GRAY, (j*gap, 0), (j*gap, width))

def draw(screen, grid, rows, width):
    screen.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(screen)

    drawGrid(screen, rows, width)

    pygame.display.update()

def getClickedPos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y //  gap
    col = x // gap
    
    return row, col

def main(screen, width):
    ROWS = 50

    grid = makeGrid(ROWS, width)

    start = None #start node
    end = None # end node

    run = True

    started = False # whether the algorithm started
    
    while run:
        draw(screen=screen, grid=grid, rows=ROWS, width=width)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
            
            if started:
                continue

            if pygame.mouse.get_pressed()[0]: #left-click
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.makeStart()
                elif not end and node != start:
                    end = node
                    end.makeEnd()
                elif node != start and node != end:
                    node.makeBarrier()

            elif pygame.mouse.get_pressed()[2]: # right-click
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                
                if node == start:
                    start = None
                elif node == end:
                    end = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.updateNeighbors(grid)

                    algorithm(grid, start, end, ROWS, width)
            
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = makeGrid(ROWS, width)

    pygame.quit()

main(screen, WIDTH)