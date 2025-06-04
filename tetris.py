import os
import json
import pygame
import random
import hashlib

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = 10, 20
PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 20

USER_FILE = 'users.json'

# Shapes and colors
S_SHAPE = [['.....',
            '.....',
            '..00.',
            '.00..',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '...0.',
            '.....']]

Z_SHAPE = [['.....',
            '.....',
            '.00..',
            '..00.',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '.0...',
            '.....']]

I_SHAPE = [['..0..',
            '..0..',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '0000.',
            '.....',
            '.....',
            '.....']]

O_SHAPE = [['.....',
            '.....',
            '.00..',
            '.00..',
            '.....']]

J_SHAPE = [['.....',
            '.0...',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..00.',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '...0.',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '.00..',
            '.....']]

L_SHAPE = [['.....',
            '...0.',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '..00.',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '.0...',
            '.....'],
           ['.....',
            '.00..',
            '..0..',
            '..0..',
            '.....']]

T_SHAPE = [['.....',
            '..0..',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '..0..',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '..0..',
            '.....']]

SHAPES = [S_SHAPE, Z_SHAPE, I_SHAPE, O_SHAPE, J_SHAPE, L_SHAPE, T_SHAPE]
SHAPE_COLORS = [ (0,255,0), (255,0,0), (0,255,255),
                 (255,255,0), (255,165,0), (0,0,255), (128,0,128) ]

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0


def create_grid(locked_positions):
    grid = [[(0,0,0) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x,y) in locked_positions:
                grid[y][x] = locked_positions[(x,y)]
    return grid


def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    return positions


def valid_space(piece, grid):
    accepted = [[(x,y) for x in range(GRID_WIDTH) if grid[y][x] == (0,0,0)] for y in range(GRID_HEIGHT)]
    accepted = [x for sub in accepted for x in sub]
    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(GRID_WIDTH//2 - 2, 0, random.choice(SHAPES))


def draw_text_middle(surface, text, size, color, y_offset=0):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - label.get_width()/2, 
                         TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2 + y_offset))


def draw_grid(surface, grid):
    for i in range(GRID_HEIGHT):
        pygame.draw.line(surface, (128,128,128), (TOP_LEFT_X, TOP_LEFT_Y + i*BLOCK_SIZE),
                         (TOP_LEFT_X+PLAY_WIDTH, TOP_LEFT_Y + i*BLOCK_SIZE))
        for j in range(GRID_WIDTH):
            pygame.draw.line(surface, (128,128,128), (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y),
                             (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))


def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc +=1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


def draw_window(surface, grid, score=0, high_score=0):
    surface.fill((50,50,50))
    pygame.draw.rect(surface, (0, 0, 0), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT))
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', True, (255,255,255))
    surface.blit(label, (TOP_LEFT_X - label.get_width() - 10, TOP_LEFT_Y))
    label = font.render(f'Best: {high_score}', True, (255,255,255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH + 10, TOP_LEFT_Y))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j*BLOCK_SIZE,
                                                   TOP_LEFT_Y + i*BLOCK_SIZE,
                                                   BLOCK_SIZE, BLOCK_SIZE), 0)
    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255,0,0), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)


def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump({}, f)
    with open(USER_FILE, 'r') as f:
        return json.load(f)


def save_users(data):
    with open(USER_FILE, 'w') as f:
        json.dump(data, f)


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def login_screen(win, users):
    font = pygame.font.SysFont('comicsans', 40)
    user_text = ''
    pw_text = ''
    active = 'user'
    while True:
        win.fill((0,0,0))
        title = font.render('Login', True, (255,255,255))
        win.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        usr_label = font.render('Username:', True, (255,255,255))
        win.blit(usr_label, (50, 150))
        pygame.draw.rect(win, (255,255,255), (50, 200, 300, 40), 2)
        user_surface = font.render(user_text, True, (255,255,0))
        win.blit(user_surface, (55,205))

        pw_label = font.render('Password:', True, (255,255,255))
        win.blit(pw_label, (50, 270))
        pygame.draw.rect(win, (255,255,255), (50, 320, 300, 40), 2)
        hidden_pw = '*' * len(pw_text)
        pw_surface = font.render(hidden_pw, True, (255,255,0))
        win.blit(pw_surface, (55,325))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active = 'pw' if active == 'user' else 'user'
                elif event.key == pygame.K_RETURN:
                    if user_text:
                        hpw = hash_pw(pw_text)
                        if user_text in users:
                            if users[user_text]['password'] == hpw:
                                return user_text
                        else:
                            users[user_text] = {'password': hpw, 'high_score': 0}
                            save_users(users)
                            return user_text
                elif event.key == pygame.K_BACKSPACE:
                    if active == 'user':
                        user_text = user_text[:-1]
                    else:
                        pw_text = pw_text[:-1]
                else:
                    if active == 'user':
                        user_text += event.unicode
                    else:
                        pw_text += event.unicode


def show_leaderboard(win, users):
    sorted_users = sorted(users.items(), key=lambda x: x[1].get('high_score',0), reverse=True)
    font = pygame.font.SysFont('comicsans', 30)
    run = True
    while run:
        win.fill((0,0,0))
        title = font.render('Leaderboard', True, (255,255,255))
        win.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for i, (name, data) in enumerate(sorted_users[:5]):
            text = font.render(f'{i+1}. {name} - {data.get("high_score",0)}', True, (255,255,0))
            win.blit(text, (50, 120 + i*40))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                run = False


def main(win, user, users):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    score = 0
    high_score = users[user].get('high_score',0)

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        shape_pos = convert_shape_format(current_piece)

        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score, high_score)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "GAME OVER", 40, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            if score > users[user].get('high_score',0):
                users[user]['high_score'] = score
                save_users(users)


def main_menu(win, user, users):
    font = pygame.font.SysFont('comicsans', 40)
    while True:
        win.fill((0,0,0))
        title = font.render('Press P to Play', True, (255,255,255))
        win.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        lb = font.render('Press L for Leaderboard', True, (255,255,255))
        win.blit(lb, (SCREEN_WIDTH//2 - lb.get_width()//2, 260))
        qt = font.render('Press Q to Quit', True, (255,255,255))
        win.blit(qt, (SCREEN_WIDTH//2 - qt.get_width()//2, 320))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    main(win, user, users)
                if event.key == pygame.K_l:
                    show_leaderboard(win, users)
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()


def run_game():
    pygame.init()
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Cartoon Tetris')
    users = load_users()
    user = login_screen(win, users)
    main_menu(win, user, users)

if __name__ == '__main__':
    run_game()
