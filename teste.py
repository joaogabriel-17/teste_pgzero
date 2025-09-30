from pygame import Rect
import random
import math

WIDTH = 800
HEIGHT = 600


won = False
game_over = False

status = 0  # 0 - menu / 1- jogo
sounds_enabled = True

level = 0
super_zombie = 0

damage_cooldown = 0

zombies = []

menu_options = [
    {'text': 'Iniciar Jogo', 'action': 'start'},
    {'text': 'Sons', 'action': 'toggle_sounds'},
    {'text': 'Sair', 'action': 'quit'},
]

button_width = 300
button_height = 50
button_margin = 20


def draw_menu():
    screen.fill((0, 0, 50))
    screen.draw.text("MEU JOGO", center=(WIDTH // 2, 80),
                     fontsize=60, color="white")

    for i, option in enumerate(menu_options):
        x = WIDTH // 2 - button_width // 2
        y = 180 + i * (button_height + button_margin)
        rect = Rect((x, y), (button_width, button_height))

        screen.draw.filled_rect(rect, (100, 100, 200))
        screen.draw.text(option["text"], center=rect.center,
                         fontsize=35, color="yellow")


class Player(Actor):
    def __init__(self, image, pos):
        super().__init__(image, pos)
        self.speed = 3
        self.health = 100

        self.walk_images = {
            "right": ["player_walk_right1", "player_walk_right2"],
            "left": ["player_walk_left1", "player_walk_left2"]
        }
        self.walk_index = 0
        self.walk_timer = 0
        self.walk_delay = 0.15
        self.direction = "right"

    def move(self):
        moving = False

        if keyboard.left:
            self.x -= self.speed
            self.direction = "left"
            moving = True
        if keyboard.right:
            self.x += self.speed
            self.direction = "right"
            moving = True
        if keyboard.up:
            self.y -= self.speed
            moving = True
        if keyboard.down:
            self.y += self.speed
            moving = True

        if moving:
            self.walk_timer += 1 / 60  # aumenta timer (supondo 60 FPS)

            if self.walk_timer >= self.walk_delay:
                self.walk_timer = 0
                # alterna imagens
                self.walk_index = (self.walk_index +
                                   1) % len(self.walk_images[self.direction])
                self.image = self.walk_images[self.direction][self.walk_index]
        else:
            self.image = "player_stand"


class Zombie(Actor):
    def __init__(self, image, pos):
        super().__init__(image, pos)
        self.speed = 1.5
        self.health = 20

    def move(self, player_pos):
        zombie_x = player_pos[0] - self.x
        zombie_y = player_pos[1] - self.y
        distance = math.hypot(zombie_x, zombie_y)
        if distance != 0:
            zombie_x /= distance
            zombie_y /= distance
            next_x = self.x + zombie_x * self.speed
            next_y = self.y + zombie_y * self.speed

            for other in zombies:
                if other == self:
                    continue
                if math.hypot(other.x - next_x, other.y - next_y) < 20:
                    return  # Não se mover para evitar colisão

            self.x = next_x
            self.y = next_y


class SuperZombie(Zombie):
    def __init__(self, image, pos):
        super().__init__(image, pos)
        self.speed = 2
        self.health = 50

    def move(self, player_pos):
        super_zombie_x = player_pos[0] - self.x
        super_zombie_y = player_pos[1] - self.y
        distance = math.hypot(super_zombie_x, super_zombie_y)
        if distance != 0:
            super_zombie_x /= distance
            super_zombie_y /= distance
            self.x += super_zombie_x * self.speed
            self.y += super_zombie_y * self.speed


def level_init(level_number):
    global zombies, level, super_zombie
    zombies.clear()
    level = level_number
    super_zombie = None

    if level == 1:
        for i in range(5):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            zombies.append(Zombie("zombie_stand", (x, y)))

    elif level == 2:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        super_zombie = SuperZombie('super_zombie_stand', (x, y))


player = Player("player_stand", (100, 100))


def zombie_hit():
    hit_distance = 30
    for zombie in zombies:
        dx = player.x - zombie.x
        dy = player.y - zombie.y
        distance = math.hypot(dx, dy)
        if distance < hit_distance:
            set_player_hurt()
            break


def super_zombie_hit():
    global game_over
    if not super_zombie:
        return
    hit_distance = 30
    dx = player.x - super_zombie.x
    dy = player.y - super_zombie.y
    distance = math.hypot(dx, dy)
    if distance < hit_distance:
        set_player_hurt()


def update():
    global level, game_over, won, damage_cooldown
    if status != 1:
        return

    if won or game_over:
        return

    player.move()

    for zombie in zombies:
        zombie.move((player.x, player.y))

    if damage_cooldown <= 0:
        zombie_hit()
        if level == 2 and super_zombie:
            super_zombie_hit()
        damage_cooldown = 0.5
    else:
        damage_cooldown -= 1/60

    if level == 1 and not zombies:
        level_init(2)

    if level == 2 and super_zombie:
        super_zombie.move((player.x, player.y))

    if level == 2 and super_zombie is None and not zombies:
        won = True

    if player.health <= 0:
        game_over = True


def draw():
    screen.clear()
    if status == 0:
        draw_menu()
    elif won:
        screen.fill((0, 50, 0))
        screen.draw.text("VOCE VENCEU!", center=(
            WIDTH // 2, HEIGHT // 2), fontsize=60, color="yellow")
    elif game_over:
        screen.fill((50, 0, 0))
        screen.draw.text("GAME OVER", center=(
            WIDTH // 2, HEIGHT // 2), fontsize=60, color="red")
    else:
        screen.blit('background', (0, 0))
        player.draw()
        for zombie in zombies:
            zombie.draw()
        if level == 2 and super_zombie and super_zombie.health > 0:
            super_zombie.draw()

        screen.draw.text(
            f"Vida: {player.health}",
            topright=(WIDTH - 20, 20),
            fontsize=30,
            color="red"
        )


def on_mouse_down(pos):
    global status, sounds_enabled, super_zombie

    if status == 1:
        max_distance = 70
        if level == 1:
            for zombie in zombies:
                dx = zombie.x - player.x
                dy = zombie.y - player.y
                distance = math.hypot(dx, dy)
                if distance <= max_distance and zombie.collidepoint(pos):
                    set_zombie_hurt(zombie)
                    return

        if level == 2 and super_zombie:
            dx = super_zombie.x - player.x
            dy = super_zombie.y - player.y
            distance = math.hypot(dx, dy)
            if distance <= max_distance and super_zombie.collidepoint(pos):
                set_super_zombie_hurt()
                return

    if status == 0:  # menu
        for i, option in enumerate(menu_options):
            x = WIDTH // 2 - button_width // 2
            y = 180 + i * (button_height + button_margin)
            rect = Rect((x, y), (button_width, button_height))

            if rect.collidepoint(pos):
                action = option["action"]

                if action == "start":
                    status = 1
                    level_init(1)
                    if sounds_enabled:
                        music.set_volume(0.03)
                        music.play("music")

                elif action == "toggle_sounds":
                    sounds_enabled = not sounds_enabled
                    menu_options[1]["text"] = f"Sons: {'ON' if sounds_enabled else 'OFF'}"

                elif action == "quit":
                    sys.exit()


def on_key_down(key):
    global status
    if status == 1 and key == keys.ESCAPE:
        status = 0


def set_player_hurt():
    player.image = 'player_hurt'
    player.health -= 5
    if sounds_enabled:
        sounds.dano.play()
    clock.schedule_unique(set_player_normal, 0.2)


def set_player_normal():
    player.image = 'player_stand'


def set_zombie_hurt(zombie):
    zombie.image = 'zombie_hurt'
    zombie.health -= 5
    if sounds_enabled:
        sounds.dano.play()
    if zombie.health <= 0:
        if zombie in zombies:
            zombies.remove(zombie)
    else:
        def restore():
            set_zombie_normal(zombie)
        clock.schedule_unique(restore, 0.2)


def set_zombie_normal(zombie):
    if zombie in zombies:
        zombie.image = 'zombie_stand'


def set_super_zombie_hurt():
    global super_zombie
    if not super_zombie:
        return
    super_zombie.image = 'super_zombie_hurt'
    super_zombie.health -= 5
    if sounds_enabled:
        sounds.dano.play()
    if super_zombie.health <= 0:
        super_zombie = None
    else:
        clock.schedule_unique(set_super_zombie_normal, 0.2)


def set_super_zombie_normal():
    global super_zombie
    if super_zombie:
        super_zombie.image = 'super_zombie_stand'
