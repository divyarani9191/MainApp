
import pygame, sys
import os
import random
from pymongo import MongoClient
from datetime import datetime



window = None


# ── INIT ─────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# ── MUSIC ────────────────────────────────────────────────────────────────────
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.set_volume(0.5)

# ── SOUNDS ───────────────────────────────────────────────────────────────────
cut_sound  = pygame.mixer.Sound("cut.mp3")
bomb_sound = pygame.mixer.Sound("bomb.mp3")

# ── MONGODB ──────────────────────────────────────────────────────────────────
uri = "mongodb+srv://emoheal_user:Emoheal123@cluster0.hwezm4z.mongodb.net/?retryWrites=true&w=majority"
client     = MongoClient(uri)
db         = client["emohealDB"]
collection = db["game_data"]

current_emotion = "happy"
current_song    = "Calm Music"

def save_game_data(score):
    data = {
        "user"      : "Divya",
        "score"     : score,
        "game"      : "Ninja-Fruit",
        "source"    : "Game",
        "timestamp" : datetime.utcnow()
    }
    collection.insert_one(data)
    print("✅ Game Data Saved:", data)

# ── WINDOW  (fullscreen, auto laptop resolution) ──────────────────────────────
info   = pygame.display.Info()
WIDTH  = info.current_w
HEIGHT = info.current_h
FPS    = 12

pygame.display.set_caption('Fruit-Ninja Game -- PRO')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock       = pygame.time.Clock()

# ── COLOURS ──────────────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0  )

# ── GAME VARIABLES  (original) ───────────────────────────────────────────────
player_lives = 3
score        = 0
fruits       = ['melon', 'orange', 'pomegranate', 'guava', 'bomb']

# ── ASSETS ───────────────────────────────────────────────────────────────────
background = pygame.transform.scale(pygame.image.load('back.jpg'), (WIDTH, HEIGHT))
font       = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 42)

# ── HELPER: draw centred text ─────────────────────────────────────────────────
def draw_text(display, text, size, x, y, color=WHITE):
    try:
        f = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), size)
    except Exception:
        f = pygame.font.SysFont('comicsansms', size)
    surf = f.render(text, True, color)
    rect = surf.get_rect()
    rect.midtop = (x, y)
    display.blit(surf, rect)

# ── HELPER: draw lives ────────────────────────────────────────────────────────
def draw_lives(display, x, y, lives, image):
    for i in range(lives):
        img = pygame.image.load(image)
        display.blit(img, (x + 35 * i, y))

# ── BUTTON CLASS ─────────────────────────────────────────────────────────────
# Positions are always by CENTER (cx, cy) so layout is screen-size independent
class Button:
    def __init__(self, text, cx, cy, w, h,
                 bg, bg_hover, border, text_color=WHITE, font_size=34):
        self.text       = text
        self.rect       = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.bg         = bg
        self.bg_hover   = bg_hover
        self.border     = border
        self.text_color = text_color
        self.font_size  = font_size

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        col     = self.bg_hover if hovered else self.bg

        # filled rounded rect
        pygame.draw.rect(surface, col,        self.rect, border_radius=14)
        # border
        pygame.draw.rect(surface, self.border, self.rect, 2, border_radius=14)

        try:
            f = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), self.font_size)
        except Exception:
            f = pygame.font.SysFont('comicsansms', self.font_size)
        txt = f.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))

# ── BUTTON PRESETS ────────────────────────────────────────────────────────────
# Green  – Play / Play Again
BTN_GREEN  = dict(bg=(34,139,34),  bg_hover=(50,180,50),  border=(144,238,144))
# Red    – Quit
BTN_RED    = dict(bg=(180,30,30),  bg_hover=(220,50,50),  border=(255,160,160))
# Blue   – Resume
BTN_BLUE   = dict(bg=(25,90,170),  bg_hover=(40,130,220), border=(135,190,255))
# Dark   – Pause icon button (in-game)
BTN_DARK   = dict(bg=(30,30,30,180), bg_hover=(60,60,60), border=(180,180,180))

# ── FRUIT GENERATOR  (original logic, only WIDTH/HEIGHT now dynamic) ──────────
data = {}

def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"
    side = random.choice(['left', 'right', 'center'])

    if side == 'left':
         
         x = random.randint(0, WIDTH//3)
         speed_x = random.randint(5, 15)

    elif  side == 'right':

        x = random.randint(2*WIDTH//3, WIDTH-100)
        speed_x = random.randint(-15, -5)

    else: 
     # center
        x = random.randint(WIDTH//3, 2*WIDTH//3)
        speed_x = random.randint(-10, 10)

    data[fruit] = {
    'img'    : pygame.image.load(fruit_path),
    'x'      : x,
    'y'      : HEIGHT,
    'speed_x': speed_x,
    'speed_y': random.randint(-80, -60),
    'throw'  : random.random() >= 0.5,   # thoda zyada fruits aayenge
    't'      : 0,
    'hit'    : False,
}

for fruit in fruits:
    generate_random_fruits(fruit)

# ── DARK OVERLAY HELPER ───────────────────────────────────────────────────────
def draw_overlay(alpha=140):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, alpha))
    gameDisplay.blit(ov, (0, 0))

# ─────────────────────────────────────────────────────────────────────────────
# START SCREEN  – replaces "Press any key to start"
#   Title  : vertical 25 % of screen
#   Buttons: vertical 52 % and 64 % of screen  (nice gap, centred)
# ─────────────────────────────────────────────────────────────────────────────
def show_start_screen():
    CX   = WIDTH  // 2
    BW, BH = int(WIDTH * 0.22), int(HEIGHT * 0.09)   # button size % of screen

    #btn_play = Button("  Play Game", CX, int(HEIGHT * 0.56), BW, BH, **BTN_GREEN)
    #btn_quit = Button("  Quit",      CX, int(HEIGHT * 0.68), BW, BH, **BTN_RED)
    btn_play  = Button("  Play Game", CX, int(HEIGHT * 0.52), BW, BH, **BTN_GREEN)
    btn_rules = Button("  Instructions", CX, int(HEIGHT * 0.64), BW, BH, **BTN_BLUE)
    btn_quit  = Button("  Quit", CX, int(HEIGHT * 0.76), BW, BH, **BTN_RED)
    

    title_y    = int(HEIGHT * 0.22)
    title_size = int(HEIGHT * 0.13)   # big title, scales with screen

    waiting = True
    while waiting:
        gameDisplay.blit(background, (0, 0))
        draw_overlay(130)

        draw_text(gameDisplay, "FRUIT NINJA", title_size, CX, title_y)
        btn_play.draw(gameDisplay)
        btn_rules.draw(gameDisplay)
        btn_quit.draw(gameDisplay)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if btn_play.is_clicked(event):
                waiting = False
            if btn_rules.is_clicked(event):   # ✅ FIX
                show_instructions_screen()
            if btn_quit.is_clicked(event):
                pygame.quit(); sys.exit()

        clock.tick(30)
def show_instructions_screen():
    CX = WIDTH // 2
    BW, BH = int(WIDTH * 0.22), int(HEIGHT * 0.09)

    btn_back = Button("  Back", CX, int(HEIGHT * 0.80), BW, BH, **BTN_BLUE)

    title_size = int(HEIGHT * 0.09)
    text_size  = int(HEIGHT * 0.045)

    while True:
        gameDisplay.blit(background, (0, 0))
        draw_overlay(160)

        draw_text(gameDisplay, "HOW TO PLAY", title_size, CX, int(HEIGHT * 0.15))

        # Instructions text
        instructions = [
            "• Move mouse to slice fruits",
            "• Each fruit gives +1 score",
            "• Avoid bombs 💣 (lose life)",
            "• You have 3 lives",
            "• Game ends when lives = 0",
            "• Click pause button to stop game"
        ]

        y_offset = int(HEIGHT * 0.30)
        for line in instructions:
            draw_text(gameDisplay, line, text_size, CX, y_offset)
            y_offset += int(HEIGHT * 0.07)

        btn_back.draw(gameDisplay)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if btn_back.is_clicked(event):
                return

        clock.tick(30)
# ─────────────────────────────────────────────────────────────────────────────
# PAUSE SCREEN  – called when pause icon clicked during game
# ─────────────────────────────────────────────────────────────────────────────
def show_pause_screen():
    CX   = WIDTH  // 2
    BW, BH = int(WIDTH * 0.22), int(HEIGHT * 0.09)

    btn_resume = Button("  Resume", CX, int(HEIGHT * 0.52), BW, BH, **BTN_BLUE)
    btn_quit   = Button("  Quit",   CX, int(HEIGHT * 0.64), BW, BH, **BTN_RED)

    paused_size = int(HEIGHT * 0.10)
    paused_y    = int(HEIGHT * 0.36)

    while True:
        draw_overlay(160)

        draw_text(gameDisplay, "PAUSED", paused_size, CX, paused_y)
        btn_resume.draw(gameDisplay)
        btn_quit.draw(gameDisplay)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 'resume'
            if btn_resume.is_clicked(event):
                return 'resume'
            if btn_quit.is_clicked(event):
                return 'quit'

        clock.tick(30)

# ─────────────────────────────────────────────────────────────────────────────
# GAME OVER SCREEN  – replaces "Press any key" at game end
# ─────────────────────────────────────────────────────────────────────────────
def show_gameover_screen():
    
    pygame.mixer.music.stop()
    save_game_data(score)
    

    CX   = WIDTH  // 2
    BW, BH = int(WIDTH * 0.22), int(HEIGHT * 0.09)

    btn_play = Button("  Play Again", CX, int(HEIGHT * 0.56), BW, BH, **BTN_GREEN)
    btn_quit = Button("  Quit",       CX, int(HEIGHT * 0.68), BW, BH, **BTN_RED)
    title_y    = int(HEIGHT * 0.22)
    title_size = int(HEIGHT * 0.11)
    score_y    = int(HEIGHT * 0.42)
    score_size = int(HEIGHT * 0.065)

    waiting = True
    while waiting:
        gameDisplay.blit(background, (0, 0))
        draw_overlay(150)

        draw_text(gameDisplay, "GAME OVER",       title_size, CX, title_y)
        draw_text(gameDisplay, f"Score : {score}", score_size, CX, score_y)
        btn_play.draw(gameDisplay)
        btn_quit.draw(gameDisplay)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_play.is_clicked(event):
                waiting = False
            if btn_quit.is_clicked(event):
                pygame.quit(); sys.exit()

        clock.tick(30)

# ─────────────────────────────────────────────────────────────────────────────
# PAUSE ICON BUTTON  (shown in top-right during gameplay)
# Two vertical bars drawn with pygame – no emoji needed
# ─────────────────────────────────────────────────────────────────────────────
ICON_SIZE = int(HEIGHT * 0.07)      # square button, 7 % of screen height
ICON_X    = WIDTH  - ICON_SIZE - int(WIDTH * 0.02)   # right margin 2 %
ICON_Y    = int(HEIGHT * 0.02)                        # top margin 2 %
icon_rect = pygame.Rect(ICON_X, ICON_Y, ICON_SIZE, ICON_SIZE)

def draw_pause_icon(surface):
    hovered = icon_rect.collidepoint(pygame.mouse.get_pos())
    bg_col  = (80, 80, 80) if hovered else (30, 30, 30)
    # semi-transparent bg
    s = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
    s.fill((*bg_col, 200))
    surface.blit(s, (ICON_X, ICON_Y))
    pygame.draw.rect(surface, (200, 200, 200), icon_rect, 2, border_radius=8)

    # two pause bars
    bar_w = max(4, ICON_SIZE // 6)
    bar_h = ICON_SIZE // 2
    bar_y = ICON_Y + ICON_SIZE // 4
    bar1_x = ICON_X + ICON_SIZE // 3 - bar_w
    bar2_x = ICON_X + ICON_SIZE * 2 // 3
    pygame.draw.rect(surface, WHITE, (bar1_x, bar_y, bar_w, bar_h), border_radius=2)
    pygame.draw.rect(surface, WHITE, (bar2_x, bar_y, bar_w, bar_h), border_radius=2)

def pause_icon_clicked(event):
    return (event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and icon_rect.collidepoint(event.pos))

# ─────────────────────────────────────────────────────────────────────────────
# LOOP CONTROL  (original variables kept exactly)
# ─────────────────────────────────────────────────────────────────────────────
first_round  = True
game_over    = True
game_running = True

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOOP  (original structure kept exactly, only show_* calls updated)
# ─────────────────────────────────────────────────────────────────────────────
while game_running:

    if game_over:
        if first_round:
            show_start_screen()
            first_round = False
        else:
            show_gameover_screen()

        pygame.mixer.music.play(-1)
        player_lives = 3
        score        = 0
        game_over    = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

        # ── pause icon click ──────────────────────────────────────────────
        if pause_icon_clicked(event):
            pygame.mixer.music.pause()
            action = show_pause_screen()
            if action == 'quit':
                game_running = False
            else:
                pygame.mixer.music.unpause()

    # ── background ───────────────────────────────────────────────────────────
    gameDisplay.blit(background, (0, 0))

    # ── score  (original) ────────────────────────────────────────────────────
    score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
    gameDisplay.blit(score_text, (0, 0))

    # ── lives  (original) ────────────────────────────────────────────────────
    draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

    # ── pause icon ───────────────────────────────────────────────────────────
    draw_pause_icon(gameDisplay)

    # ── fruits  (original logic, untouched) ──────────────────────────────────
    for key, value in data.items():
        if value['throw']:
            value['x'] += value['speed_x']
            value['y'] += value['speed_y']
            value['speed_y'] += value['t']
            value['t'] += 1

            if value['y'] <= 800:
                gameDisplay.blit(value['img'], (value['x'], value['y']))
            else:
                generate_random_fruits(key)

            mouse = pygame.mouse.get_pos()

            if not value['hit'] and value['x'] < mouse[0] < value['x'] + 60 and value['y'] < mouse[1] < value['y'] + 60:

                if key == 'bomb':
                    bomb_sound.play()
                    player_lives -= 1

                    if player_lives <= 0:
                        game_over = True

                    img_path = "images/explosion.png"
                else:
                    cut_sound.play()
                    score += 1
                    img_path = "images/half_" + key + ".png"

                value['img']     = pygame.image.load(img_path)
                value['speed_x'] += 10
                value['hit']      = True
        else:
            generate_random_fruits(key)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()