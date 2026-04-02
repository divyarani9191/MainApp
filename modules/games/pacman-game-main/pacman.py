
from random import choice
from turtle import *
from freegames import floor, vector

# 🔗 MongoDB
from pymongo import MongoClient
from datetime import datetime

# 🔥 MongoDB Atlas CONNECT
uri = "mongodb+srv://emoheal_user:Emoheal123@cluster0.hwezm4z.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

db = client["emohealDB"]
collection = db["game_data"]

# 💾 SAVE FUNCTION
def save_game_data(score):
    data = {
        "user": "Divya",
        "game": "pacman",
        "score": score,
        "source": "game",
        "timestamp": datetime.utcnow()
    }
    collection.insert_one(data)
    print("✅ Pacman Data Saved:", data)

# -------- SOUND --------
try:
    import winsound
    def play_sound():
        winsound.Beep(800, 80)
except:
    def play_sound():
        pass

# ---------------- STATE ----------------
state = {
    'score': 0,
    'running': False,
    'paused': False,
    'show_rules': False
}

path = Turtle(visible=False)
writer = Turtle(visible=False)
menu = Turtle(visible=False)
ui = Turtle(visible=False)

aim = vector(0, 0)
pacman = vector(-40, -80)

ghosts = [
    [vector(-180, 160), vector(4, 0)],
    [vector(-180, -160), vector(0, 4)],
    [vector(100, 160), vector(0, -4)],
    [vector(100, -160), vector(-4, 0)],
]

# ---------------- MAP ----------------
tiles = [
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,
    0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,1,0,0,0,0,
    0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,
    0,1,0,0,1,0,1,0,0,0,1,0,1,0,0,1,0,0,0,0,
    0,1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,0,0,0,0,
    0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,0,0,
    0,1,0,0,1,0,1,1,1,1,1,0,1,0,0,0,0,0,0,0,
    0,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,0,0,0,
    0,0,0,0,1,0,1,1,1,1,1,0,1,0,0,1,0,0,0,0,
    0,0,0,0,1,0,1,0,0,0,1,0,1,0,0,1,0,0,0,0,
    0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,
    0,1,0,0,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,
    0,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,
    0,0,1,0,1,0,1,0,0,0,1,0,1,0,1,0,0,0,0,0,
    0,1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,0,0,0,0,
    0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,
    0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
]

# ---------------- MENU ----------------
def draw_menu():
    clear()
    menu.clear()
    bgcolor("#0a0a23")

    menu.penup()

    menu.goto(0, 120)
    menu.color("cyan")
    menu.write("P  A  C  M  A  N", align="center", font=("Arial", 48, "bold"))

    menu.goto(0, 40)
    menu.color("white")
    menu.write("▶ PLAY GAME", align="center", font=("Arial", 22, "bold"))

    menu.goto(0, -20)
    menu.write("✖ QUIT", align="center", font=("Arial", 22, "bold"))

    menu.goto(0, -80)
    menu.write("ℹ INSTRUCTIONS", align="center", font=("Arial", 20, "bold"))

    if state['show_rules']:
        draw_rules()

def draw_rules():
    rules = [
        "Use Arrow Keys to move",
        "Eat white dots to score",
        "Avoid red ghosts",
        "If caught → Game Over"
    ]

    y = -140
    for r in rules:
        menu.goto(0, y)
        menu.write(r, align="center", font=("Arial", 14))
        y -= 25

# ---------------- CLICK ----------------
def click(x, y):
    if not state['running']:
        if -120 < x < 120 and 20 < y < 60:
            start_game()
        elif -120 < x < 120 and -20 < y < 20:
            bye()
        elif -120 < x < 120 and -100 < y < -60:
            state['show_rules'] = not state['show_rules']
            draw_menu()
    else:
        if -200 < x < -120 and 130 < y < 210:
            toggle_pause()
        elif 50 < x < 250 and 120 < y < 220:
            quit_game()

# ---------------- CONTROLS ----------------
def draw_controls():
    ui.clear()
    ui.penup()
    ui.color("white")

    ui.goto(-180, 180)
    ui.write("Resume" if state['paused'] else "Pause")

    ui.goto(120, 180)
    ui.write("Quit")

# ---------------- GAME ----------------
def square(x, y):
    path.up()
    path.goto(x, y)
    path.down()
    path.begin_fill()
    for _ in range(4):
        path.forward(20)
        path.left(90)
    path.end_fill()

def offset(point):
    x = (floor(point.x, 20) + 200) / 20
    y = (180 - floor(point.y, 20)) / 20
    return int(x + y * 20)

def valid(point):
    index = offset(point)
    if tiles[index] == 0:
        return False
    index = offset(point + 19)
    if tiles[index] == 0:
        return False
    return point.x % 20 == 0 or point.y % 20 == 0

def world():
    bgcolor('black')
    path.color('blue')
    for index in range(len(tiles)):
        tile = tiles[index]
        if tile > 0:
            x = (index % 20) * 20 - 200
            y = 180 - (index // 20) * 20
            square(x, y)
            if tile == 1:
                path.up()
                path.goto(x + 10, y + 10)
                path.dot(2, 'white')

def move():
    if not state['running']:
        return

    if state['paused']:
        draw_controls()
        ontimer(move, 100)
        return

    writer.undo()
    writer.write(state['score'])
    clear()

    if valid(pacman + aim):
        pacman.move(aim)

    index = offset(pacman)

    if tiles[index] == 1:
        play_sound()
        tiles[index] = 2
        state['score'] += 1

        x = (index % 20) * 20 - 200
        y = 180 - (index // 20) * 20

        path.color('blue')
        square(x, y)

    up()
    goto(pacman.x + 10, pacman.y + 10)
    dot(20, 'yellow')

    for point, course in ghosts:
        if valid(point + course):
            point.move(course)
        else:
            options = [vector(4,0), vector(-4,0), vector(0,4), vector(0,-4)]
            plan = choice(options)
            course.x = plan.x
            course.y = plan.y

        up()
        goto(point.x + 10, point.y + 10)
        dot(20, 'red')

    update()
    draw_controls()

    for point, _ in ghosts:
        if abs(pacman - point) < 20:
            quit_game()
            return

    ontimer(move, 80)

def change(x, y):
    if valid(pacman + vector(x, y)):
        aim.x = x
        aim.y = y

# ---------------- EXTRA ----------------
def start_game():
    state['running'] = True
    state['paused'] = False
    state['score'] = 0

    menu.clear()
    writer.clear()

    writer.goto(160, 160)
    writer.color('white')
    writer.write(state['score'])

    world()
    move()

def toggle_pause():
    state['paused'] = not state['paused']

def quit_game():
    bye()
    # ✅ SAVE SCORE TO MONGODB
    save_game_data(state['score'])

# ---------------- SETUP ----------------
setup(width=1.0, height=1.0)
hideturtle()
tracer(False)

listen()
onscreenclick(click)

onkey(lambda: change(5, 0), 'Right')
onkey(lambda: change(-5, 0), 'Left')
onkey(lambda: change(0, 5), 'Up')
onkey(lambda: change(0, -5), 'Down')

draw_menu()
done()
