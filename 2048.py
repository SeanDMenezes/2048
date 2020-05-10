import random
import msvcrt
import copy
import pygame

# PYGAME CONSTANTS
def enable_constants():
    global CALIBRI
    global SCREEN_SIZE
    global SCREEN
    global WHITE
    global BLACK
    global RED
    
    CALIBRI = pygame.font.SysFont('calibri', 50)
    SCREEN_SIZE = [500, 500]
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)

# GAME CONSTANTS
width = 100
height = 100
SIZE = 4
BLANK ='''
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+
'''

def grid_to_str(grd):
    flatten = list(map(lambda line: "".join(line), grd))
    return ('\n'.join(flatten))      

def str_to_grid(s):
    rows = s.split('\n')
    grd = list(map(list, rows[1:-1]))
    return grd

def generate_grid(vals):
    rv = []
    ind = 0
    for _ in range(SIZE):
        new_row = []
        for _ in range(SIZE):
            new_row.append(Cell(vals[ind]))
            ind += 1
        rv.append(new_row)
    return rv

def default_grid():
    return generate_grid([' '] * 16)
    

class Player():
    def get_move(self, valid_moves):
        raise NotImplementedError
    def draw(self):
        raise NotImplementedError
    def lose(self):
        raise NotImplementedError

class Text(Player):
    def __init__(self):
        super().__init__()

    def get_move(self, valid_moves):
        while 1:
            inp = msvcrt.getch()
            if int(ord(inp)) == 75 and "left" in valid_moves:
                return "left"
            elif int(ord(inp)) == 72 and "up" in valid_moves: 
                return "up"
            elif int(ord(inp)) == 77 and "right" in valid_moves: 
                return "right"
            elif int(ord(inp)) ==  80 and "down" in valid_moves:
                 return "down"
            elif int(ord(inp)) == 113: 
                return "q"
            else: 
                continue

    def draw(self, g):
        print(g)

    def lose(self):
        print("No more moves left!")

class Graphical(Player):
    def __init__(self):
        super().__init__()
        pygame.init()
        enable_constants()
        pygame.display.set_caption("2048")
    
    def get_move(self, valid_moves):
        while 1:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    return "q"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and "up" in valid_moves:
                        return "up"
                    elif event.key == pygame.K_DOWN and "down" in valid_moves:
                        return "down"
                    elif event.key == pygame.K_LEFT and "left" in valid_moves:
                        return "left"
                    elif event.key == pygame.K_RIGHT and "right" in valid_moves:
                        return "right"
                    elif event.key == pygame.K_q:
                        return "q"
                    else:
                        continue

    def draw(self, g):
        g.draw()

    def lose(self):
        font = pygame.font.SysFont('calibri', 40)
        msg = font.render("No more moves left!", True, BLACK)
        SCREEN.blit(msg, [100, 450])
        pygame.display.flip()
        pygame.time.delay(1000)

class AI(Graphical):
    def __init__(self):
        super().__init__()
    
    def get_move(self, valid_moves):
        if "right" in valid_moves:
            return "right"
        elif "down" in valid_moves:
            return "down"
        elif "left" in valid_moves:
            return "left"
        else:
            return "up"        

class Cell:
    def __init__(self, val):
        self.val = val
        self.merged = False
    def __repr__(self):
        return str(self.val)
    def __eq__(self, other):
        return self.val == other.val

class Grid:
    def __init__(self, cells=None):
        if cells == None:
            cells = default_grid()
        self.cells = cells
        self.score = 0

    def __repr__(self):
        grid = str_to_grid(BLANK)
        for i in range(SIZE):
            row = 2*i + 1
            for j in range(SIZE):
                num_len = len(repr(self.cells[i][j]))
                if num_len in [1,2]: col = 5*j + 2
                elif num_len in [3,4]: col = 5*j + 1

                for k in range(num_len):
                    grid[row][col + k] = repr(self.cells[i][j])[k]
        return grid_to_str(grid)

    def __eq__(self, other):
        for i in range(SIZE):
            for j in range(SIZE):
                if self.cells[i][j] != other.cells[i][j]:
                    return False
        return True

    def filled(self):
        for i in range(SIZE):
            for j in range(SIZE):
                if self.cells[i][j] == Cell(' '):
                    return False
        return True

    def unmerge(self):
        for i in range(SIZE):
            for j in range(SIZE):
                self.cells[i][j].merged = False
    
    def draw(self):
        SCREEN.fill(WHITE)
        for i in range(4):
            for j in range(4):
                pygame.draw.rect(SCREEN, BLACK, [100*i + 50, 100*j + 50, width, height], 1)
                text = CALIBRI.render(repr(self.cells[j][i]), True, BLACK)
                textRect = text.get_rect()
                textRect.center = 100*i + 100, 100*j + 100
                SCREEN.blit(text, textRect)
        font = pygame.font.SysFont('calibri', 40)
        move_count = font.render("Score: " + str(self.score), True, BLACK)
        SCREEN.blit(move_count, [15, 5])
        pygame.display.flip()

    def move(self, direction):
        '''
        - iterate in the reverse direction of direction
            - i.e. if trying to move down, iterate from bottom up
        - if empty square, continue
        - otherwise, move square as far in the direction as possible
            - if encountered end of board, stop
            - if encountered another square
                - if encountered square is same value, double value of encountered square
                - otherwise stop
        '''
        row = list(range(SIZE))
        col = list(range(SIZE))
        reverse = False
        if direction in ["right", "down"]:
            col = list(reversed(col))
        if direction in ["up", "down"]:
            reverse = True
        for i in row:
            for j in col:
                if reverse: x, y = j, i
                else: x, y = i, j
                # empty case
                if self.cells[x][y] == Cell(' '):
                    continue
                # otherwise cell is non-empty and should be moved
                if direction == "left":
                    for k in list(reversed(range(y))):
                        # empty cell, can move here
                        if self.cells[x][k] == Cell(' '):
                            self.cells[x][k] = self.cells[x][k + 1]
                            self.cells[x][k + 1] = Cell(' ')
                        # cell is same value, can move here and double my value
                        elif self.cells[x][k] == self.cells[x][k + 1] and not self.cells[x][k].merged:
                            self.cells[x][k] = Cell(2 * self.cells[x][k].val)
                            self.cells[x][k + 1] = Cell(' ')
                            self.cells[x][k].merged = True
                            self.score += self.cells[x][k].val
                            break
                        # cell is different value, can't move
                        else:
                            break
                elif direction == "right":
                    for k in list(range(y + 1, 4)):
                        if self.cells[x][k] == Cell(' '):
                            self.cells[x][k] = self.cells[x][k - 1]
                            self.cells[x][k - 1] = Cell(' ')
                        elif self.cells[x][k] == self.cells[x][k - 1] and not self.cells[x][k].merged:
                            self.cells[x][k] = Cell(2 * self.cells[x][k].val)
                            self.cells[x][k - 1] = Cell(' ')
                            self.cells[x][k].merged = True
                            self.score += self.cells[x][k].val
                            break
                        else:
                            break
                elif direction == "up":
                    for k in list(reversed(range(x))):
                        if self.cells[k][y] == Cell(' '):
                            self.cells[k][y] = self.cells[k + 1][y]
                            self.cells[k + 1][y] = Cell(' ')
                        elif self.cells[k][y] == self.cells[k + 1][y] and not self.cells[k][y].merged:
                            self.cells[k][y] = Cell(2 * self.cells[k][y].val)
                            self.cells[k + 1][y] = Cell(' ')
                            self.cells[k][y].merged = True
                            self.score += self.cells[k][y].val
                            break
                        else:
                            break
                elif direction == "down":
                    for k in list(range(x + 1, 4)):
                        if self.cells[k][y] == Cell(' '):
                            self.cells[k][y] = self.cells[k - 1][y]
                            self.cells[k - 1][y] = Cell(' ')
                        elif self.cells[k][y] == self.cells[k - 1][y] and not self.cells[k][y].merged:
                            self.cells[k][y] = Cell(2 * self.cells[k][y].val)
                            self.cells[k - 1][y] = Cell(' ')
                            self.cells[k][y].merged = True
                            self.score += self.cells[k][y].val
                            break
                        else:
                            break
        self.unmerge()


def play(g=Grid()):
    '''
    - initialize grid to be empty
    - begin loop here
    - place either 2 or 4 in a random empty square
    - print grid
    - initialize valid moves to [up, down, left, right]
    - for each valid move, if the move causes no change, remove it
        - make the move, compare it to original, revert the move
    - if there are no moves left, player loses
    - otherwise, player makes move, valid if it's in list
    - loop back to start
    '''

    p = Graphical() # oneof Text, AI, Graphical
    running = 1
    while running == 1:
        if not g.filled():
            pos = random.randint(0, 15)
            new = random.choice([2]*9 + [4])
            if g.cells[pos // SIZE][pos % SIZE] != Cell(' '):
                continue
            g.cells[pos // SIZE][pos % SIZE] = Cell(new)
        p.draw(g)
        # print(g)

        all_moves = ["up", "down", "left", "right"]
        valid_moves = []
        for m in all_moves:
            og_cells = copy.deepcopy(g.cells)
            og_score = g.score
            g.move(m)
            #g.unmerge()
            if g.cells != og_cells:
                valid_moves.append(m)
            g.cells = og_cells
            g.score = og_score
        
        if len(valid_moves) == 0:
            p.lose()
            running = 0
            continue

        direction = p.get_move(valid_moves)
        if direction == "q":
            running = 0
        else:
            g.move(direction)
            #g.unmerge()
        
    pygame.quit()

# g = Grid(generate_grid([2,4,2,4,4,2,4,2]*2)) - setting up a losing board
play()
