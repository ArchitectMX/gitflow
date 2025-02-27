import pygame
import math
import random
import json
from os import path

# Инициализация PyGame
pygame.init()
pygame.mixer.init()

# Константы
WIDTH = 1200
HEIGHT = 800
FPS = 60
POWERUP_TIME = 5000

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Инициализация окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический Шутер")
clock = pygame.time.Clock()

# Загрузка изображений
game_folder = path.dirname(__file__)
img_folder = path.join(game_folder, 'img')
sound_folder = path.join(game_folder, 'sounds')

def load_image(file):
    return pygame.image.load(path.join(img_folder, file)).convert_alpha()

def load_sound(file):
    return pygame.mixer.Sound(path.join(sound_folder, file))

# Ресурсы
background = pygame.transform.scale(load_image('starfield.png'), (WIDTH, HEIGHT))
player_img = load_image('playerShip1_orange.png')
bullet_img = load_image('laserRed16.png')
enemy_images = [
    load_image('enemyBlack1.png'),
    load_image('enemyBlue2.png'),
    load_image('enemyGreen3.png'),
    load_image('enemyRed4.png')
]
explosion_anim = {
    'lg': [load_image(f'regularExplosion0{i}.png') for i in range(9)],
    'sm': [load_image(f'sonarExplosion0{i}.png') for i in range(9)],
    'player': [load_image(f'playerExplosion0{i}.png') for i in range(9)]
}
powerup_images = {
    'shield': load_image('shield_gold.png'),
    'gun': load_image('bolt_gold.png')
}

# Звуки
shoot_sound = load_sound('pew.ogg')
expl_sounds = [load_sound(f'expl{i}.ogg') for i in range(1, 3)]
player_die_sound = load_sound('expl4.ogg')
powerup_sound = load_sound('powerup.ogg')
boom_sound = load_sound('boom.ogg')
pygame.mixer.music.load(path.join(sound_folder, 'fone.ogg'))
pygame.mixer.music.play(loops=-1)  # Запуск фоновой музыки

# Глобальные переменные групп спрайтов
all_sprites = None
mobs = None
bullets = None
powerups = None
player = None
score = 0

# Классы
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.orig_image = pygame.transform.scale(player_img, (50, 38))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()
        self.rot = 0  # текущий угол поворота

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_UP]:
            self.speedy = -8
        if keystate[pygame.K_DOWN]:
            self.speedy = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()

        # Определяем целевой угол поворота по горизонтальному движению:
        target_angle = 0
        if self.speedx < 0:
            target_angle = 15
        elif self.speedx > 0:
            target_angle = -15
        else:
            target_angle = 0

        # Плавное приближение к целевому углу
        self.rot += (target_angle - self.rot) * 0.2

        # Поворот изображения
        new_image = pygame.transform.rotate(self.orig_image, self.rot)
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect(center=old_center)

        # Обновляем позицию
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Ограничение по границам экрана
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1, bullet2)
                bullets.add(bullet1, bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(enemy_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if (self.rect.top > HEIGHT + 10 or
            self.rect.left < -25 or
            self.rect.right > WIDTH + 20):
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect(center=center)


class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


# Функции
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def show_go_screen():
    screen.blit(background, (0, 0))
    draw_text(screen, "КОСМИЧЕСКИЙ ШУТЕР", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Стрелки для движения, Пробел для стрельбы", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Нажмите любую клавишу для начала", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


def newmob():
    global all_sprites, mobs
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


# Основная игра
def main_game():
    global all_sprites, mobs, bullets, powerups, player, score
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    for i in range(8):
        newmob()
    score = 0

    running = True
    while running:
        clock.tick(FPS)
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False

        # Обновление спрайтов
        all_sprites.update()

        # Проверка столкновений пуль с мобами
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            score += 50 - hit.radius  # Увеличиваем счёт
            random.choice(expl_sounds).play()  # Проигрываем случайный звук взрыва
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            newmob()

            # Проверка столкновений игрока с мобами
        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            player.shield -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            newmob()
            boom_sound.play()  # Звук взрыва игрока
            if player.shield <= 0:
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                player.hide()
                player.lives -= 1
                player.shield = 100
                pygame.time.delay(1000)
                if player.lives <= 0:
                    running = False
                    break

        # Проверка столкновений игрока с апгрейдами
        if not player.hidden:
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit in hits:
                if hit.type == 'shield':
                    player.shield += random.randrange(10, 30)
                    if player.shield > 100:
                        player.shield = 100
                if hit.type == 'gun':
                    player.powerup()
                powerup_sound.play()

        # Рендеринг
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)
        draw_shield_bar(screen, 5, 5, player.shield)

        # Рисуем жизни
        for i in range(player.lives):
            img = pygame.transform.scale(player_img, (25, 19))
            img.set_colorkey(BLACK)
            screen.blit(img, (WIDTH - 100 + 30 * i, 10))

        pygame.display.flip()

    return True  


def show_game_over_screen():
    screen.blit(background, (0, 0))
    draw_text(screen, "GAME OVER", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, f"Score: {score}", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press any key to restart", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                return False
            if event.type == pygame.KEYUP:
                waiting = False
    return True


game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        restarted = main_game()
        if not restarted:
            running = False
        else:
            game_over = True
            show_game_over_screen()

pygame.quit()
