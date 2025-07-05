import pgzrun
from pygame import Rect

WIDTH = 800
HEIGHT = 600
TITLE = "Simple Platformer"

GRAVITY = 0.5
JUMP_STRENGTH = 12
GROUND_Y = 500

GAME_STATE_START_SCREEN = -1
GAME_STATE_PLAYING = 0
GAME_STATE_END_SCREEN = 1

game_state = GAME_STATE_START_SCREEN
score = 0
sound_on = True

PHASES = [
    {
        "platforms": [(300, 450, 200, 20), (550, 400, 150, 20)],
        "items": [(400, 450), (625, 400)],
        "enemies": [(350, 450)]
    },
    {
        "platforms": [(150, 450, 100, 20), (400, 380, 180, 20), (650, 300, 120, 20)],
        "items": [(180, 450), (450, 380), (700, 300)],
        "enemies": [(200, 450), (500, 380)]
    },
    {
        "platforms": [(100, 500, 80, 20), (250, 420, 160, 20), (450, 350, 100, 20), (600, 280, 150, 20), (300, 200, 80, 20)],
        "items": [(140, 500), (310, 420), (500, 350), (675, 280), (340, 200)],
        "enemies": [(315, 420), (400, 540), (690, 280)]
    }
]

current_phase_index = 0
platforms = []
items = []
enemies = []

class Player:
    def __init__(self):
        self.idle_sprites = ["idle1", "idle2"]
        self.run_sprites = ["run1", "run2", "run3"]
        self.jump_sprite = "jump"
        self.current_sprite_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.3
        self.image = self.idle_sprites[self.current_sprite_index]
        self.actor = Actor(self.image)
        self.actor.pos = (WIDTH / 6 - 100, GROUND_Y)
        self.speed = 5
        self.is_moving = False
        self.facing_left = False
        self.scale_factor = 0.5
        self.original_width = self.actor.width
        self.original_height = self.actor.height
        self.actor.width = int(self.original_width * self.scale_factor)
        self.actor.height = int(self.original_height * self.scale_factor)
        self.vel_y = 0
        self.is_jumping = False

    def update(self, current_platforms, current_items):
        global current_phase_index, game_state, score
        self.is_moving = False

        if keyboard.a:
            self.actor.x -= self.speed
            self.is_moving = True
            self.facing_left = True
        elif keyboard.d:
            self.actor.x += self.speed
            self.is_moving = True
            self.facing_left = False

        if keyboard.space and not self.is_jumping:
            self.vel_y = -JUMP_STRENGTH
            self.is_jumping = True
            if sound_on:
                sounds.jump.play()

        self.vel_y += GRAVITY
        self.actor.y += self.vel_y

        on_ground = False

        if self.actor.y >= GROUND_Y:
            self.actor.y = GROUND_Y
            self.vel_y = 0
            self.is_jumping = False
            on_ground = True

        for platform in current_platforms:
            if self.vel_y > 0 and self.actor.y + self.actor.height >= platform.top and self.actor.y + self.actor.height <= platform.top + 20:
                if self.actor.x + self.actor.width // 2 > platform.left and self.actor.x - self.actor.width // 2 < platform.right:
                    self.actor.y = platform.top - self.actor.height
                    self.vel_y = 0
                    self.is_jumping = False
                    on_ground = True
                    break

        if not on_ground:
            self.is_jumping = True

        player_rect = Rect(
            (self.actor.x - self.original_width * self.scale_factor / 2,
             self.actor.y - self.original_height * self.scale_factor / 2),
            (self.original_width * self.scale_factor, self.original_height * self.scale_factor)
        )

        for item in current_items:
            item_rect = Rect(
                (item.actor.x - item.actor.width / 2, item.actor.y - item.actor.height / 2),
                (item.actor.width, item.actor.height)
            )
            if item.active and player_rect.colliderect(item_rect):
                item.collect()
                score += 1

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed * 60:
            self.animation_timer = 0
            if self.is_jumping:
                sprite_base = self.jump_sprite
            elif self.is_moving:
                self.current_sprite_index = (self.current_sprite_index + 1) % len(self.run_sprites)
                sprite_base = self.run_sprites[self.current_sprite_index]
            else:
                self.current_sprite_index = (self.current_sprite_index + 1) % len(self.idle_sprites)
                sprite_base = self.idle_sprites[self.current_sprite_index]
            if self.facing_left:
                sprite_base += "_left"
            self.actor.image = sprite_base
            self.actor.width = int(self.original_width * self.scale_factor)
            self.actor.height = int(self.original_height * self.scale_factor)

        if self.actor.x > WIDTH:
            if current_phase_index + 1 < len(PHASES):
                current_phase_index += 1
                load_phase(current_phase_index)
                self.actor.x = WIDTH / 5
                self.actor.y = GROUND_Y
                self.vel_y = 0
                self.is_jumping = False
            else:
                game_state = GAME_STATE_END_SCREEN
                if sound_on and not music.is_playing("fm"):
                    music.play("fm")

    def draw(self):
        self.actor.draw()

class CollectibleItem:
    def __init__(self, x, y):
        self.actor = Actor("item")
        self.actor.pos = (x, y - self.actor.height / 2 - 5)
        self.active = True

    def draw(self):
        if self.active:
            self.actor.draw()

    def collect(self):
        self.active = False
        if sound_on:
            sounds.shine.set_volume(0.3)
            sounds.shine.play()

class Enemy:
    def __init__(self, x, y):
        self.sprites = ["teste", "teste2"]
        self.current_sprite = 0
        self.animation_timer = 0
        self.animation_speed = 0.3
        self.actor = Actor(self.sprites[self.current_sprite])
        self.actor.pos = (x, y - self.actor.height / 2)
        self.direction = 1
        self.speed = 1
        self.range = 60
        self.start_x = self.actor.x

    def update(self):
        self.actor.x += self.direction * self.speed
        if abs(self.actor.x - self.start_x) > self.range:
            self.direction *= -1
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed * 60:
            self.animation_timer = 0
            self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
            self.actor.image = self.sprites[self.current_sprite]

    def draw(self):
        self.actor.draw()

player = Player()

def load_phase(index):
    global platforms, items, enemies
    platforms.clear()
    items.clear()
    enemies.clear()
    phase_data = PHASES[index]
    for p in phase_data["platforms"]:
        platforms.append(Rect((p[0], p[1]), (p[2], p[3])))
    for i in phase_data["items"]:
        items.append(CollectibleItem(i[0], i[1]))
    for e in phase_data["enemies"]:
        enemies.append(Enemy(e[0], e[1]))

def reset_game():
    global current_phase_index, score, game_state
    current_phase_index = 0
    score = 0
    game_state = GAME_STATE_PLAYING
    load_phase(current_phase_index)
    player.actor.pos = (WIDTH / 5, GROUND_Y)
    player.vel_y = 0
    player.is_jumping = False
    if sound_on:
        music.stop()

load_phase(current_phase_index)

start_buttons = [
    Rect((WIDTH // 2 - 100, 200), (200, 50)),
    Rect((WIDTH // 2 - 100, 300), (200, 50)),
    Rect((WIDTH // 2 - 100, 400), (200, 50))
]

def draw():
    screen.clear()
    if game_state == GAME_STATE_START_SCREEN:
        screen.fill((0, 0, 50))
        screen.draw.text("Menu Principal", center=(WIDTH/2, 100), fontsize=60, color="white")
        screen.draw.filled_rect(start_buttons[0], "darkgreen")
        screen.draw.text("Começar o jogo", center=start_buttons[0].center, fontsize=30, color="white")
        screen.draw.filled_rect(start_buttons[1], "darkblue")
        screen.draw.text("Música ON/OFF", center=start_buttons[1].center, fontsize=30, color="white")
        screen.draw.filled_rect(start_buttons[2], "darkred")
        screen.draw.text("Saída", center=start_buttons[2].center, fontsize=30, color="white")
    elif game_state == GAME_STATE_PLAYING:
        screen.blit("background", (0, 0))
        screen.blit("ground", (0, GROUND_Y + 40))
        for p in platforms:
            screen.draw.filled_rect(p, (139, 69, 19))
        player.draw()
        for item in items:
            item.draw()
        for enemy in enemies:
            enemy.draw()
        screen.draw.text(f"Maçãs: {score}", topleft=(10, 10), fontsize=30, color="white")
    elif game_state == GAME_STATE_END_SCREEN:
        screen.blit("final-background", (0, 0))
        screen.draw.text("Fim de Jogo!", center=(WIDTH / 2, HEIGHT / 2 - 50), fontsize=60, color="yellow")
        screen.draw.text(f"Número de maçãs pegas: {score}", center=(WIDTH / 2, HEIGHT / 2 + 10), fontsize=40, color="white")
        screen.draw.text("Pressione R para jogar novamente", center=(WIDTH / 2, HEIGHT / 2 + 100), fontsize=30, color="lightgray")

def update():
    global game_state
    if game_state == GAME_STATE_START_SCREEN:
        if sound_on and not music.is_playing("bgm"):
            music.play("bgm")
    elif game_state == GAME_STATE_PLAYING:
        player.update(platforms, items)
        for enemy in enemies:
            enemy.update()
        player_rect = Rect(
            (player.actor.x - player.original_width * player.scale_factor / 2,
             player.actor.y - player.original_height * player.scale_factor / 2),
            (player.original_width * player.scale_factor, player.original_height * player.scale_factor)
        )
        for enemy in enemies:
            enemy_rect = Rect(
                (enemy.actor.x - enemy.actor.width / 2, enemy.actor.y - enemy.actor.height / 2),
                (enemy.actor.width, enemy.actor.height)
            )
            if player_rect.colliderect(enemy_rect):
                game_state = GAME_STATE_END_SCREEN
                if sound_on and not music.is_playing("fm"):
                    music.play("fm")
                break

def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == GAME_STATE_START_SCREEN:
        if start_buttons[0].collidepoint(pos):
            game_state = GAME_STATE_PLAYING
            if sound_on:
                music.stop()
        elif start_buttons[1].collidepoint(pos):
            sound_on = not sound_on
            music.stop()
        elif start_buttons[2].collidepoint(pos):
            exit()

def on_key_down(key):
    global game_state
    if game_state == GAME_STATE_END_SCREEN and key == keys.R:
        reset_game()

pgzrun.go()
