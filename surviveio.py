import pygame
import random
import math
import json
from cryptography.fernet import Fernet
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

pygame.init()

screen_w, screen_h = 700, 700
screen = pygame.display.set_mode((screen_w, screen_h))
clock = pygame.time.Clock()

def derive_key(passphrase):
    salt = b'some_salt'
    kdf = hashlib.pbkdf2_hmac('sha256', passphrase.encode(), salt, 100000, 32)
    return base64.urlsafe_b64encode(kdf)

passphrase = "t0day1s@G00dD4y!"
key = derive_key(passphrase)

cipher_suite = Fernet(key)

file_location = r'encrypted_data.bin'

font = pygame.font.SysFont("Bauhaus 93", 20)
big_font = pygame.font.Font(None, 100)
little_font = pygame.font.SysFont("Bahnschrift", 20)
cool_font = pygame.font.SysFont("Bauhaus 93", 30)
num_font = pygame.font.SysFont("Guttman Haim-Condensed", 20)
big_num_font = pygame.font.SysFont("Guttman Haim-Condensed", 40)
big_stat_font = pygame.font.SysFont("Cooper Black", 30)

# home screen
mouse_effect_list = []

# upgrades
upgrades = ['speed', 'bullet rate', 'damage', 'hp']
next_up = random.choice(upgrades)
upgrade_prices = [40, 70, 50, 100, 30, 50, 50, 25, 20]

# other varibles
enemy_spawn_rate = 99.9

GameRun = False
HomeScreenRun = False
upgradeScreenRun = False
statsScreenRun = False

# items
coins = 150
best_kills = [0, 0, 0]
trophys = 0

set_upgrades = False

# worlds
background_world = [((25, 25, 25), (50, 50, 50)),
                   ((0, 70, 0), (0, 50, 0)),
                   ((0, 0, 0), (25, 25, 25))]
set_world = False
world_open = [(True, 0), (False, 200), (False, 300)]


class TripleGun():
    def __init__(self, player):
        self.x = player.x + player.width / 2
        self.y = player.y + player.height / 2
        self.end_x = 0
        self.end_y = 0
        self.dx = 0
        self.dy = 0
        self.len = 30
        self.color = (0, 255, 0)
        self.timePerShot = 20 - up_list[2]
        if self.timePerShot <= 5:
            self.timePerShot = 5
        self.timePerPar = 0
        self.shotTime = 0

    def render(self, player, special_gun_par_list):
        self.x = player.x + player.width / 2
        self.y = player.y + player.height / 2
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.dx = self.x - mouse_x
        self.dy = self.y - mouse_y
        angle = math.atan2(-self.dy, -self.dx)
        self.end_x = self.x + self.len * math.cos(angle)
        self.end_y = self.y + self.len * math.sin(angle)
        pygame.draw.circle(screen, self.color, (self.x, self.y), 3)
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.end_x, self.end_y))
        if self.timePerPar >= 7:
            special_gun_par = SpecialGunPar(random.uniform(player.x, player.x + player.width), random.uniform(player.y, player.y + player.height))
            special_gun_par_list.append(special_gun_par)
            self.timePerPar = 0
        self.timePerPar += 1

    def shotBullet(self, bullets):
        if self.shotTime >= self.timePerShot:
            for i in range(3):
                bullet = Bullet(self.end_x, self.end_y, -self.dx + (i - 1) * 30, -self.dy + (i - 1) * 30, 2, self.color)
                bullets.append(bullet)
            self.shotTime = 0
        self.shotTime += 1

class DoubleGun():
    def __init__(self, player):
        self.x = player.x + player.width / 2
        self.y = player.y + player.height / 2
        self.end_x1, self.end_y1 = 0, 0
        self.end_x2, self.end_y2 = 0, 0
        self.dx = 0
        self.dy = 0
        self.len = 20
        self.color = (0, 255, 0)
        self.timePerShot = 20 - up_list[2]
        if self.timePerShot <= 5:
            self.timePerShot = 5
        self.shotTime = 0
        self.timePerPar = 0

    def render(self, player, special_gun_par_list):
        self.x = player.x + player.width / 2
        self.y = player.y + player.height / 2
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.dx = self.x - mouse_x
        self.dy = self.y - mouse_y
        angle = math.atan2(-self.dy, -self.dx)
        angle2 = math.atan2(self.dy, self.dx)
        self.end_x1 = self.x + self.len * math.cos(angle)
        self.end_y1 = self.y + self.len * math.sin(angle)
        self.end_x2 = self.x + self.len * math.cos(angle2)
        self.end_y2 = self.y + self.len * math.sin(angle2)
        # draw
        pygame.draw.circle(screen, self.color, (self.x, self.y), 3)
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.end_x1, self.end_y1))
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.end_x2, self.end_y2))

        if self.timePerPar >= 7:
            special_gun_par = SpecialGunPar(random.uniform(player.x, player.x + player.width), random.uniform(player.y, player.y + player.height))
            special_gun_par_list.append(special_gun_par)
            self.timePerPar = 0
        self.timePerPar += 1

    def shotBullet(self, bullets):
        if self.shotTime >= self.timePerShot:
            bullet1 = Bullet(self.end_x1, self.end_y1, -self.dx, -self.dy, 2, self.color)
            bullets.append(bullet1)
            bullet2 = Bullet(self.end_x2, self.end_y2, self.dx, self.dy, 2, self.color)
            bullets.append(bullet2)
            self.shotTime = 0
        self.shotTime += 1



class SpecialGunPar():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.maxRadius = 5
        self.on = False
        self.color = random.choice([(0, 255, 0), (0, 180, 0), (0, 100, 0)])

    def render(self, special_gun_par_list):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        if not self.on:
            self.radius += 0.2
            if self.radius >= self.maxRadius:
                self.on = True
        if self.on:
            self.radius -= 0.2
            if self.radius <= 0:
                special_gun_par_list.remove(self)


class SpecialGun():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.maxSize = self.size
        self.color = (0, 255, 0)
        self.time = 0
        self.timeAlive = 400
        self.timePerPar = 0

    def render(self, special_guns, special_gun_par_list, player, enemies):
        crate_rect = pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size), 2)
        self.time += 1
        self.timePerPar += 1
        if self.time >= self.timeAlive:
            self.size -= 1
            self.x += 0.5
            self.y += 0.5
        if self.size <= 0:
            special_guns.remove(self)
        if self.timePerPar >= 5 and self.size >= self.maxSize:
            special_gun_par = SpecialGunPar(random.uniform(self.x, self.x + self.size), random.uniform(self.y, self.y + self.size))
            special_gun_par_list.append(special_gun_par)
            self.timePerPar = 0
        if crate_rect.colliderect(player.x, player.y, player.width, player.height):
            special_guns.remove(self)
            chance = random.randint(1, 2)
            if chance == 1:
                player.doubleGun = True
            if chance == 2:
                player.tripleGun = True
        for enemy in enemies:
            if crate_rect.colliderect(enemy.x, enemy.y, enemy.radius, enemy.radius):
                self.timePerPar = self.timeAlive

def drawSpecialGun(special_guns, special_gun_par_list, player, enemies):
    for special_gun in special_guns:
        SpecialGun.render(special_gun, special_guns, special_gun_par_list, player, enemies)
    for special_gun_par in special_gun_par_list:
        SpecialGunPar.render(special_gun_par, special_gun_par_list)

def spawnSpecialGun(special_guns, player):
    chance = random.uniform(0, 100)
    if chance >= 99.96 and len(special_guns) < 1 and not player.doubleGun and not player.tripleGun:
        if not player.doubleGun:
            special_gun = SpecialGun(random.uniform(30, screen_w - 30), random.uniform(100, screen_h - 30))
            special_guns.append(special_gun)




def background(color1, color2, size):
    for y in range(int(screen_h / size)):
        for x in range(int(screen_w / size)):
            if (x + y) % 2 != 0:
                pygame.draw.rect(screen, color1, (x * size, y * size, size, size))
            else:
                pygame.draw.rect(screen, color2, (x * size, y * size, size, size))



class droneEffect():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.speed = 4
        self.color = 255
        self.maxRadius = screen_w * 2

    def render(self, drone_effect_list):
        finalColor = (self.color, self.color, self.color)
        pygame.draw.circle(screen, finalColor, (self.x, self.y), self.radius, 1)
        self.radius += self.speed
        if self.radius >= self.maxRadius:
            drone_effect_list.remove(self)

def drawdroneEffect(drone_effect_list):
    for drone_effect in drone_effect_list:
        droneEffect.render(drone_effect, drone_effect_list)


class DroneShot():
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = (255, 255, 255)
        self.radius = 2
        self.speed = 4 + up_list[6]
        self.damage = 2

    def render(self, player, drone_bullets, enemies, enemy_die_list):
        bullet_rect = pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

        angle = math.atan2(self.dy, self.dx)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)

        for enemy in enemies:
            if bullet_rect.colliderect(enemy.x, enemy.y, enemy.radius * 2, enemy.radius * 2):
                enemy.hp -= self.damage
                for i in range(enemy.radius * 5):
                    if enemy.hp <= 0 and enemy.color != (0, 200, 255):
                        speed = 5
                        enemyDie = EnemyDie(enemy.x, enemy.y, random.uniform(-speed, speed), random.uniform(-speed, speed), True, enemy.color)
                        enemy_die_list.append(enemyDie)
                    else:
                        speed = 2
                        enemyDie = EnemyDie(enemy.x, enemy.y, random.uniform(-speed, speed), random.uniform(-speed, speed), False, enemy.color)
                        enemy_die_list.append(enemyDie)
                try:
                    drone_bullets.remove(self)
                except Exception:
                    pass
                if enemy.hp <= 0 and enemy.color == (0, 200, 255):
                    player.droneHp += 1

def drawDroneBullet(player, drone_bullets, enemies, enemy_die_list):
    for drone_bullet in drone_bullets:
        DroneShot.render(drone_bullet, player, drone_bullets, enemies, enemy_die_list)


class Drone():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 10
        self.color = 170
        self.onTime = 0

    def render(self, player, drones, enemies):
        finalColor = (self.color, self.color, self.color)
        if self.color > 0:
            drone_rect = pygame.draw.rect(screen, finalColor, (self.x, self.y, self.size, self.size), 1)

        locations = [(drone_rect.topleft), (drone_rect.topright), (drone_rect.bottomleft), (drone_rect.bottomright)]
        for i in range(4):
            if self.color > 0:
                pygame.draw.circle(screen, finalColor, (locations[i]), self.size / 3, 2)

        for enemy in enemies:
            if drone_rect.colliderect(enemy.x, enemy.y, enemy.radius, enemy.radius):
                drones.remove(self)

        self.onTime += 1
        if self.onTime >= 400:
            self.size -= 1
            self.x += 0.5
            self.y += 0.5
            if self.size <= 0:
                drones.remove(self)
        if drone_rect.colliderect(player.x, player.y, player.width, player.height) and self.color > 20:
            player.drone = True
            player.droneX = self.x
            player.droneY = self.y
            drones.remove(self)

def drawDrone(player, drones, enemies):
    for drone in drones:
        Drone.render(drone, player, drones, enemies)

def spawnDrone(player, drones, enemies):
    chance = random.uniform(0, 100)
    if chance >= 99.9 and not player.drone and len(drones) < 1:
        drone = Drone(random.uniform(30, screen_w - 30), random.uniform(100, screen_h - 30))
        drones.append(drone)
    drawDrone(player, drones, enemies)




class ForceField():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.color = (255, 0, 0)
        self.onTime = 0

    def render(self, player, force_fields, enemies):
        force_field_rect = pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 1)
        self.onTime += 1
        if self.onTime >= 250:
            self.radius -= 0.1
        if force_field_rect.colliderect(player.x, player.y, player.width, player.height):
            player.forceField = True
            force_fields.remove(self)
        for enemy in enemies:
            if force_field_rect.colliderect(enemy.x, enemy.y, enemy.radius, enemy.radius):
                force_fields.remove(self)
                enemies.remove(enemy)

def drawForcefield(player, force_fields, enemies):
    for force_field in force_fields:
        ForceField.render(force_field, player, force_fields, enemies)

def spawnForceField(player, force_fields, enemies):
    chance = random.uniform(0, 100)
    if chance >= 98 and not player.forceField and len(force_fields) < 1:
        force_field = ForceField(random.uniform(30, screen_w - 30), random.uniform(100, screen_h - 30))
        force_fields.append(force_field)
    drawForcefield(player, force_fields, enemies)




class Shield():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.color = 255
        self.finalColor = (0, self.color, self.color)
        self.onTime = 0.5

    def render(self, player, shields, enemies):
        self.finalColor = (0, self.color, self.color)
        shield_rect = pygame.draw.circle(screen, self.finalColor, (self.x, self.y), self.radius, 1)
        if shield_rect.colliderect(player.x, player.y, player.width, player.height) and self.color >= 50:
            shields.remove(self)
            player.shield = True
            player.shieldRadius = 0
        for enemy in enemies:
            if shield_rect.colliderect(enemy.x, enemy.y, enemy.radius, enemy.radius):
                shields.remove(self)

def drawShield(player, shields, enemies):
    for shield in shields:
        Shield.render(shield, player, shields, enemies)

def spawnShield(player, shields, enemies):
    chance = random.uniform(0, 600)
    if chance > 599 and not player.shield and len(shields) < 1:
        shield = Shield(random.uniform(30, screen_w - 30), random.uniform(100, screen_h - 30))
        shields.append(shield)
    drawShield(player, shields, enemies)




class FoodPar():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.speed = 3
        self.color = (209, 176, 29)

    def render(self, food_par_list):
        self.radius += self.speed

        #the 15 is the food width and the food height !!!
        pygame.draw.circle(screen, self.color, (self.x + 15 / 2, self.y + 15 / 2), self.radius, 1)
        if self.radius >= screen_w * 2:
            food_par_list.remove(self)

def drawFoodPar(food_par_list):
    for food_par in food_par_list:
        FoodPar.render(food_par, food_par_list)


class Food():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.width = 15
        self.height = 15

    def render(self, player, lvl_bar, foods, enemies, food_par_list):
        food_rect = pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 2, 5)
        if food_rect.colliderect(player.x, player.y, player.width, player.height):
            foods.remove(self)
            food_par = FoodPar(self.x - self.width / 2, self.y - self.height / 2)
            food_par_list.append(food_par)
            lvl_bar.xp += 2
            hp = player.hp / player.maxHp * 100
            player.hp += player.maxHp / 4
            if player.hp > player.maxHp:
                player.hp = player.maxHp

        for enemy in enemies:
            if food_rect.colliderect(enemy.x, enemy.y, enemy.radius, enemy.radius):
                foods.remove(self)
                enemy.hp = enemy.maxHp

def drawFood(player, lvl_bar, foods, enemies, food_par_list):
    for food in foods:
        Food.render(food, player, lvl_bar, foods, enemies, food_par_list)


def spawnFood(player, lvl_bar, foods, enemies, food_par_list):
    chance = random.uniform(0, 400)
    if chance > 399.5 and len(foods) < 4:
        food = Food(random.uniform(30, screen_w - 30), random.uniform(100, screen_h - 30), (209, 176, 29))
        foods.append(food)
    drawFood(player, lvl_bar, foods, enemies, food_par_list)




def drawUpgrade():
    upgrade_text = font.render(f"+{next_up}", 0, (255, 255, 255))
    screen.blit(upgrade_text, (screen_w / 2 - 30 / 2, 40))

def upgrade(player, gun):
    global next_up
    if next_up == 'speed' and player.speed < 15:
        player.speed += 0.2
    if next_up == 'bullet rate' and gun.timePerShot > 10:
        gun.timePerShot -= 2
    if next_up == 'damage' and gun.damage < 20:
        gun.damage += 0.5
    if next_up == 'hp' and player.hp < 200:
        player.hp += 0.5

    chance = random.randint(1, 3)
    if chance == 1 and player.speed < 15:
        next_up = 'speed'
    if chance == 2 and gun.timePerShot > 10:
        next_up = 'bullet rate'
    if chance == 3 and gun.damage < 20:
        next_up = 'damage'
    if chance == 4 and player.hp < 200:
        next_up == 'hp'


class LevelUpEffect():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        colors = [(0, 200, 0), (200, 100, 0), (200, 0, 0)]
        self.color = random.choice(colors)
        self.radius = 4
        self.xvel = random.uniform(1, 3)
        self.yvel = random.uniform(-3, 3)

    def render(self, level_up_effect_list):
        self.x += self.xvel
        self.y += self.yvel
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        if self.x > screen_w or self.y < 0:
            level_up_effect_list.remove(self)


def drawLevelUpEffect(level_up_effect_list):
    for level_up_effect in level_up_effect_list:
        LevelUpEffect.render(level_up_effect, level_up_effect_list)


class Level():
    def __init__(self, x, y, xp, lvl):
        self.x = x
        self.y = y
        self.xp = xp
        self.lvl = lvl
        self.color = (0, 200, 0)
        self.lineColor = (0, 150, 0)

    def render(self, player, gun, level_up_effect_list):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, screen_w - 200, 20), 1, 5)

        # level up
        if self.xp >= 25 * self.lvl:
            self.xp = 0
            self.lvl += 1
            upgrade(player, gun)
            for i in range(30):
                level_up_effect = LevelUpEffect(self.x + screen_w - 200, self.y + 20 / 2)
                level_up_effect_list.append(level_up_effect)
        # color change
        if self.xp <= (25 * self.lvl / 3):
            self.color = (0, 200, 0)
            self.lineColor = (0, 150, 0)
        elif self.xp <= (25 * self.lvl / 1.5):
            self.color = (200, 100, 0)
            self.lineColor = (150, 50, 0)
        elif self.xp >= (25 * self.lvl / 1.5):
            self.color = (200, 0, 0)
            self.lineColor = (150, 0, 0)
        green_bar_rect = pygame.draw.rect(screen, self.color, (self.x + 1, self.y + 1, (self.xp * ((screen_w - 200) / (25 * self.lvl))) - 2, 20 - 2), 0, 5)
        bar = pygame.draw.rect(screen, (255, 255, 255), (self.x + green_bar_rect.width - 2.5, self.y - green_bar_rect.height + 14, 5, 30), 0, 10)
        amount = 15
        for i in range(int(green_bar_rect.width / amount)):
            if i > 0:
                pygame.draw.line(screen, self.lineColor, (self.x + i * amount, self.y + green_bar_rect.height), (self.x + i * amount + 5, self.y + 1), 5)




def drawMouse(x, y, width, height, color):
    pygame.mouse.set_visible(False)
    pygame.draw.circle(screen, (255, 0, 0), (x, y), 2)
    pygame.draw.circle(screen, color, (x + width, y - height), 5, 2, True)
    pygame.draw.circle(screen, color, (x + width, y + height), 5, 2, 0, 0, 0, True)
    pygame.draw.circle(screen, color, (x - width, y - height), 5, 2, 0, True)
    pygame.draw.circle(screen, color, (x - width, y + height), 5, 2, 0, 0, True)


def drawKills(player):
    kills_text = font.render(f"{player.kills}", 0, (255, 255, 255))
    screen.blit(kills_text, (100, 40))



class EnemyDie():
    def __init__(self, x, y, xvel, yvel, die, color):
        self.x = x
        self.y = y
        self.xvel = xvel
        self.yvel = yvel
        self.die = die
        if not self.die:
            self.radius = 1.3
        else:
            self.radius = 2
        self.color = color

    def render(self, enemy_die_list):
        if self.die:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
            self.x += self.xvel
            self.y += self.yvel
            if 2 > self.xvel > -2 and 2 > self.yvel > -2:
                enemy_die_list.remove(self)
        else:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
            self.x += self.xvel
            self.y += self.yvel

        if self.x > screen_w or self.x < 0 or self.y > screen_h or self.y < 0:
            try:
                enemy_die_list.remove(self)
            except Exception:
                pass


def drawEnemyDie(enemy_die_list):
    for enemyDie in enemy_die_list:
        EnemyDie.render(enemyDie, enemy_die_list)



class Enemy():
    def __init__(self, x, y, radius, hp, damage, color, speed, xpGive):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.dx = 0
        self.dy = 0
        self.damage = damage + up_list[0]
        self.hp = hp
        self.maxHp = hp
        self.collide = False
        self.color = color
        self.xpGive = xpGive

        self.forceAttack = 0

        self.shotingCountRate = 0
        self.shotingRate = 50

    def render(self, player, gun, lvl_bar, enemies, shields, bullets, enemy_die_list, player_par_list, enemy_bullets):
        enemy_rect = pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 2)

        self.dx = (player.x + player.width / 2) - self.x
        self.dy = (player.y + player.height / 2) - self.y
        angle = math.atan2(self.dy, self.dx)

        for enemy in enemies:
            if enemy_rect.colliderect(enemy.x, enemy.y, enemy.radius, enemy.radius) and enemy != self:
                self.collide = True
                self.x += 1
                self.y += 1
                enemy.x -= 1
                enemy.y -= 1

        for shield in shields:
            if enemy_rect.colliderect(shield.x, shield.y, shield.radius, shield.radius):
                shields.remove(shield)

        if self.collide:
            self.collide = False
        elif not self.collide and not self.color == (127, 0, 255):
            self.x += self.speed * math.cos(angle)
            self.y += self.speed * math.sin(angle)

        if enemy_rect.colliderect(player.x, player.y, player.width, player.height):
            enemies.remove(self)
            if player.hp >= 0 and not player.shield:
                if self.color != (127, 0, 255):
                    player.hp -= self.damage
                else:
                    player.hp -= self.damage * 5
                if player.drone:
                    player.droneHp -= 2
            for i in range(30):
                if not player.shield:
                    player_par = PlayerPar(player.x, player.y, player.color)
                    player_par_list.append(player_par)
                elif player.shield:
                    player_par = PlayerPar(player.x, player.y, (0, 255, 255))
                    player_par_list.append(player_par)
            if player.shield:
                player.shield = False

        for bullet in bullets:
            enemy_big_rect = pygame.Rect(self.x, self.y, self.radius * 3, self.radius * 3)
            if enemy_big_rect.colliderect(bullet.x, bullet.y, bullet.radius * 2, bullet.radius * 2):
                self.hp -= gun.damage + up_list[0]
                for i in range(20):
                    if self.hp <= 0 and self.color != (0, 200, 255):
                        speed = 5
                        enemyDie = EnemyDie(self.x, self.y, random.uniform(-speed, speed), random.uniform(-speed, speed), True, self.color)
                        enemy_die_list.append(enemyDie)
                    else:
                        speed = 2
                        enemyDie = EnemyDie(self.x, self.y, random.uniform(-speed, speed), random.uniform(-speed, speed), False, self.color)
                        enemy_die_list.append(enemyDie)
                bullets.remove(bullet)

        if self.hp <= 0:
            try:
                enemies.remove(self)
            except Exception:
                pass
            player.kills += 1
            lvl_bar.xp += random.uniform(self.xpGive / 3, self.xpGive)
            if self.color == (0, 200, 255):
                if player.hp < 100:
                    player.hp += 10
                    for i in range(30):
                        player_par = PlayerPar(player.x, player.y, self.color)
                        player_par_list.append(player_par)
                    if player.hp > 100:
                        player.hp = 100

        if self.color == (127, 0, 255):
            Enemy.shotingEnemy(self, player, enemy_bullets)

    def drawEnemyHp(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.x - self.radius, self.y - self.radius * 2, self.radius * 2, 2))
        pygame.draw.rect(screen, self.color, (self.x - self.radius, self.y - self.radius * 2, self.hp * self.radius / (self.maxHp / 2), 2))

    def shotingEnemy(self, player, enemy_bullets):
        dx = player.x - self.x
        dy = player.y - self.y
        angle = math.atan2(dy, dx)
        angle2 = math.atan2(-dy, -dx)
        dis = dx**2 + dy**2
        distance = math.sqrt(dis)
        if distance > 100:
            self.x += self.speed * math.cos(angle)
            self.y += self.speed * math.sin(angle)
        if distance < 75:
            self.x += self.speed * math.cos(angle2)
            self.y += self.speed * math.sin(angle2)
        self.shotingCountRate += 1
        if self.shotingCountRate >= self.shotingRate and distance < 150:
            dx = player.x - self.x
            dy = player.y - self.y
            enemy_bullet = EnemyBullet(self.x, self.y, dx, dy, 3, self.color, player, self.damage)
            enemy_bullets.append(enemy_bullet)
            self.shotingCountRate = 0


def drawEnemy(player, gun, lvl_bar, enemies, shields, bullets, enemy_die_list, player_par_list, enemy_bullets):
    for enemy in enemies:
        Enemy.render(enemy, player, gun, lvl_bar, enemies, shields, bullets, enemy_die_list, player_par_list, enemy_bullets)
        Enemy.drawEnemyHp(enemy)



def spawnEnemy(player, enemies):
    global enemy_spawn_rate
    chance = random.uniform(0, 100)
    enemy_spawn_rate -= 1 / 10000
    if chance >= enemy_spawn_rate:
        locations = [(random.uniform(0, screen_w), -20), (random.uniform(0, screen_w), screen_h + 20), (-20, random.uniform(0, screen_h)), (screen_w + 20, random.uniform(0, screen_h))]
        loc = random.choice(locations)
        x, y = loc
        chance = random.uniform(0, 100)
        # x, y, radius, hp, damage, color, speed, xp
        if world_choose.selectedWorld == 1:
            if chance >= 60:
                enemy = Enemy(x, y, 7, 15, 7, (255, 165, 0), 0.7, 12)
            else:
                enemy = Enemy(x, y, 5, 10, 5, (0, 200, 0), 1, 8)
        if world_choose.selectedWorld == 2:
            if chance >= 70:
                enemy = Enemy(x, y, 10, 7, 2, (0, 200, 255), 0.4, 0)
            else:
                enemy = Enemy(x, y, 3, 5, 10, (255, 255, 255), 2, 17)
        if world_choose.selectedWorld == 3:
            if chance >= 80:
                enemy = Enemy(x, y, 6, 17, 5, (127, 0, 255), 1.2, 15)
            else:
                enemy = Enemy(x, y, 7, 15, 7, (255, 165, 0), 0.7, 12)
        enemies.append(enemy)


class EnemyBullet():
    def __init__(self, x, y, dx, dy, radius, color, player, damage):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.color = color
        self.speed = 5
        self.player = player
        self.damage = damage

    def render(self, enemy_bullets, player_par_list):
        enemy_bullet_rect = pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        angle = math.atan2(self.dy, self.dx)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        if enemy_bullet_rect.colliderect(self.player.x, self.player.y, self.player.width, self.player.height):
            enemy_bullets.remove(self)
            self.player.hp -= self.damage
            if self.player.drone:
                self.player.droneHp -= 2
            for i in range(30):
                if not self.player.shield:
                    player_par = PlayerPar(self.player.x, self.player.y, self.player.color)
                    player_par_list.append(player_par)
                elif self.player.shield:
                    player_par = PlayerPar(self.player.x, self.player.y, (0, 255, 255))
                    player_par_list.append(player_par)
            if self.player.shield:
                self.player.shield = False


def drawEnemyBullet(enemy_bullets, player_par_list):
    for enemy_bullet in enemy_bullets:
        EnemyBullet.render(enemy_bullet, enemy_bullets, player_par_list)



class Bullet():
    def __init__(self, x, y, dx, dy, radius, color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.speed = 5 + up_list[3]
        self.color = color

    def render(self, bullets):
        angle = math.atan2(self.dy, self.dx)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

        if self.x > screen_w or self.x < 0 or self.y > screen_h or self.y < 0:
            bullets.remove(self)

def drawBullet(bullets):
    for bullet in bullets:
        Bullet.render(bullet, bullets)



class Gun():
    def __init__(self, x, y, width, damage):
        self.x = x
        self.y = y
        self.width = width
        self.damage = damage
        self.length = 20
        self.dx = 0
        self.dy = 0
        self.end_x = 0
        self.end_y = 0
        self.time = 0
        self.timePerShot = 50 - up_list[2]
        if self.timePerShot <= 20:
            self.timePerShot = 20

    def render(self, player):
        self.x = player.x + player.width / 2
        self.y = player.y + player.height / 2

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.dx = mouse_x - self.x
        self.dy = mouse_y - self.y
        angle = math.atan2(self.dy, self.dx)

        self.end_x = self.x + self.length * math.cos(angle)
        self.end_y = self.y + self.length * math.sin(angle)

        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (self.end_x, self.end_y), 1)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.width)

    def shot(self, bullets):
        if self.time >= self.timePerShot:
            bullet = Bullet(self.end_x, self.end_y, self.dx, self.dy, 2, (255, 255, 0))
            bullets.append(bullet)
            self.time = 0
        self.time += 1

def shotButton(gun, shotOnSpace_var, bullets):
    keys = pygame.key.get_pressed()
    if shotOnSpace_var:
        if keys[pygame.K_SPACE]:
            Gun.shot(gun, bullets)
    else:
        Gun.shot(gun, bullets)



class PlayerPar():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.speed = 5
        self.xvel = random.uniform(-self.speed, self.speed)
        self.yvel = random.uniform(-self.speed, self.speed)
        self.radius = 2.5

    def render(self, player, player_par_list):
        self.x += self.xvel
        self.y += self.yvel
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

        if -2 < self.yvel < 2 and -2 < self.xvel < 2:
            player_par_list.remove(self)

def drawPlayerPar(player, player_par_list):
    for player_par in player_par_list:
        PlayerPar.render(player_par, player, player_par_list)



class Player():
    def __init__(self, x, y, width, height, hp):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hp = hp + up_list[4]
        self.maxHp = self.hp
        self.speed = 1 + (up_list[1] / 10)
        self.xvel = 0
        self.yvel = 0
        self.kills = 0
        self.color = (255, 0, 0)

        self.shield = False
        self.shieldRadius = 0

        self.forceField = False
        self.forceFieldRadius = 0
        self.forceFieldOn = False
        self.forceFieldMaxRadius = 60
        self.forceFieldDamage = 2

        self.drone = False
        self.droneDamage = 3
        self.droneDX = 0
        self.droneDY = 0
        self.droneX = 0
        self.droneY = 0
        self.droneTimePerShot = 0
        self.droneBulletRate = 30 - up_list[5]
        self.droneHp = 10 + up_list[7]

        self.doubleGun = False
        self.doubleGunTime = 0
        self.doubleGunMaxTime = 2000

        self.tripleGun = False
        self.tripleGunTime = 0
        self.tripleGunMaxTime = 2000

    def render(self):
        global coins, best_kills, trophys
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 1, 3)
        if self.hp <= 0:
            coins += self.kills * up_list[8]
            trophys += round(self.kills / 2)
            enemy_spawn_rate = 99.9
            for i in range(world_choose.selectedWorld):
                if i + 1 == world_choose.selectedWorld:
                    if self.kills > best_kills[i]:
                        best_kills[i] = self.kills
            HomeScreenRun = True
            GameRun = False
            saveDB()
            HomeScreen(HomeScreenRun)

    def PlayerShield(self):
        if self.shield:
            if self.shieldRadius < 15:
                self.shieldRadius += 0.8
            pygame.draw.circle(screen, (0, 255, 255), (self.x + self.width / 2, self.y + self.height / 2), self.shieldRadius, 1)

    def PlayerForceField(self, enemies, enemy_die_list):
        if self.forceField:
            force_field_rect = pygame.draw.circle(screen, self.color, (self.x + self.width / 2, self.y + self.height / 2), self.forceFieldRadius, 1)
            if not self.forceFieldOn:
                self.forceFieldRadius += 0.8
                if self.forceFieldRadius >= self.forceFieldMaxRadius:
                    self.forceFieldOn = True
            if self.forceFieldOn:
                self.forceFieldRadius -= 0.02
                if self.forceFieldRadius <= 0:
                    self.forceField = False
                    self.forceFieldRadius = 0
                    self.forceFieldOn = False
                    self.forceFieldMaxRadius = 60
            for enemy in enemies:
                enemy.forceAttack += 1
                if force_field_rect.colliderect(enemy.x, enemy.y, enemy.radius, enemy.radius) and enemy.forceAttack >= 50:
                    enemy.hp -= self.forceFieldDamage
                    enemy.forceAttack = 0
                    if enemy.hp <= 0:
                        for i in range(30):
                            speed = 10
                            enemyDie = EnemyDie(enemy.x, enemy.y, random.uniform(-speed, speed), random.uniform(-speed, speed), True, enemy.color)
                            enemy_die_list.append(enemyDie)

    def PlayerDrone(self, enemies, drone_bullets, drone_effect_list):
        if self.drone:
            drone_rect = pygame.draw.rect(screen, (255, 255, 255), (self.droneX, self.droneY, 10, 10), 1)

            locations = [(drone_rect.topleft), (drone_rect.topright), (drone_rect.bottomleft), (drone_rect.bottomright)]
            for i in range(4):
                pygame.draw.circle(screen, (255, 255, 255), (locations[i]), 10 / 3, 2)

            self.droneDX = (self.x + self.width / 2) - self.droneX
            self.droneDY = (self.y + self.height / 2) - self.droneY
            angle = math.atan2(self.droneDY, self.droneDX)
            distance = (self.droneDX*self.droneDX + self.droneDY*self.droneDY) / 100

            if distance > 20:
                self.droneX += self.speed * 0.9 * math.cos(angle)
                self.droneY += self.speed * 0.9 * math.sin(angle)

            self.droneTimePerShot += 1

            for enemy in enemies:
                dx = enemy.x - self.droneX
                dy = enemy.y - self.droneY
                distance = (dx*dx + dy*dy) / 100
                if distance < 100 and self.droneTimePerShot > self.droneBulletRate:
                    drone_bullet = DroneShot(self.droneX + 5, self.droneY + 5, dx, dy)
                    drone_bullets.append(drone_bullet)
                    self.droneTimePerShot = 0

            pygame.draw.rect(screen, (255, 0, 0), (self.droneX, self.droneY - 10, 10, 3))
            pygame.draw.rect(screen, (255, 255, 255), (self.droneX, self.droneY - 10, self.droneHp, 3))
            if self.droneHp <= 0:
                self.drone = False
                self.droneHp = 10
                drone_effect = droneEffect(self.droneX, self.droneY)
                drone_effect_list.append(drone_effect)

    def doubleGun(self, double_gun, bullets, special_gun_par):
        if self.doubleGun:
            DoubleGun.render(double_gun, self, special_gun_par)
            DoubleGun.shotBullet(double_gun, bullets)
            self.doubleGunTime += 1
            if self.doubleGunTime >= self.doubleGunMaxTime:
                self.doubleGun = False
                self.doubleGunTime = 0

    def tripleGun(self, triple_gun, bullets, special_gun_par):
        if self.tripleGun:
            TripleGun.render(triple_gun, self, special_gun_par)
            TripleGun.shotBullet(triple_gun, bullets)
            self.tripleGunTime += 1
            if self.tripleGunTime >= self.tripleGunMaxTime:
                self.tripleGun = False
                self.tripleGunTime = 0


    def moveRight(self):
        if self.x < screen_w - self.width:
            self.xvel = self.speed
    def moveLeft(self):
        if self.x > 0:
            self.xvel = -self.speed
    def moveUp(self):
        if self.y > 0:
            self.yvel = -self.speed
    def moveDown(self):
        if self.y < screen_h - self.height:
            self.yvel = self.speed

    def move(self):
        if abs(self.xvel) == abs(self.yvel):
            self.xvel /= math.sqrt(2)
            self.yvel /= math.sqrt(2)
        self.x += self.xvel
        self.y += self.yvel
        self.yvel = 0
        self.xvel = 0

    def drawHp(self):
        pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y - 10, self.width, 5), 0, 5)
        pygame.draw.rect(screen, (150, 0, 0), (self.x, self.y - 10,(self.hp * self.width / self.maxHp), 5), 0, 5)

def playerMovement(player):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        Player.moveRight(player)
    if keys[pygame.K_a]:
        Player.moveLeft(player)
    if keys[pygame.K_w]:
        Player.moveUp(player)
    if keys[pygame.K_s]:
        Player.moveDown(player)
    if keys[pygame.K_d] or keys[pygame.K_a] or keys[pygame.K_w] or keys[pygame.K_s]:
        Player.move(player)




def Game(GameRun):

    # all game objects
    bullets = []
    enemies = []
    foods = []
    shields = []
    force_fields = []
    drones = []
    drone_bullets = []
    special_guns = []
    enemy_bullets = []

    # particles lists
    enemy_die_list = []
    player_par_list = []
    food_par_list = []
    drone_effect_list = []
    special_gun_par_list = []
    level_up_effect_list = []

    player = Player(screen_w / 2 - 10, screen_h / 2 - 10, 20, 20, 100)
    gun = Gun(player.x - player.width / 2, player.y - player.height / 2, 4, 5)
    lvl_bar = Level(100, 10, 0, 1)
    double_gun = DoubleGun(player)
    triple_gun = TripleGun(player)


    while GameRun:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()


        for i in range(world_choose.selectedWorld):
            if i + 1 == world_choose.selectedWorld:
                background(background_world[i][0], background_world[i][1], 25)

        # player
        Player.render(player)
        playerMovement(player)
        Player.drawHp(player)
        Player.PlayerShield(player)
        Player.PlayerForceField(player, enemies, enemy_die_list)
        Player.PlayerDrone(player, enemies, drone_bullets, drone_effect_list)
        drawdroneEffect(drone_effect_list)
        Player.doubleGun(player, double_gun, bullets, special_gun_par_list)
        Player.tripleGun(player, triple_gun, bullets, special_gun_par_list)

        # gun
        if not player.doubleGun and not player.tripleGun:
            Gun.render(gun, player)

        # bullet
        drawBullet(bullets)
        if not player.doubleGun and not player.tripleGun:
            shotButton(gun, False, bullets)

        # enemy
        spawnEnemy(player, enemies)
        drawEnemy(player, gun, lvl_bar, enemies, shields, bullets, enemy_die_list, player_par_list, enemy_bullets)
        drawEnemyBullet(enemy_bullets, player_par_list)

        # particles
        drawEnemyDie(enemy_die_list)
        drawPlayerPar(player, player_par_list)
        drawFoodPar(food_par_list)

        # info
        drawKills(player)

        # mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        drawMouse(mouse_x, mouse_y, 1, 1, (255, 255, 255))

        # level / upgrades
        Level.render(lvl_bar, player, gun, level_up_effect_list)
        drawUpgrade()
        drawLevelUpEffect(level_up_effect_list)

        # food
        spawnFood(player, lvl_bar, foods, enemies, food_par_list)

        # shield
        spawnShield(player, shields, enemies)

        # force field
        spawnForceField(player, force_fields, enemies)

        # drone
        spawnDrone(player, drones, enemies)
        drawDroneBullet(player, drone_bullets, enemies, enemy_die_list)

        # special guns
        spawnSpecialGun(special_guns, player)
        drawSpecialGun(special_guns, special_gun_par_list, player, enemies)

        pygame.display.update()
        clock.tick(120)


class WorldChoose():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 100
        self.height = 50
        self.world = 1
        self.selectedWorld = self.world
        self.selectColor = (255, 255, 0)
        self.leftSize = 40
        self.rightSize = 40
        self.maxSize = self.rightSize + 10
        self.minSize = self.rightSize
        self.leftX = self.x + 105
        self.leftY = self.y + 5
        self.rightX = self.x - 45
        self.rightY = self.y + 5

    def render(self):
        world_rect = pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height), 1)
        world_text = font.render(f"World {self.world}", 0, (255, 255, 255))
        screen.blit(world_text, (self.x + 10, self.y + 12))
        if self.selectedWorld == self.world:
            self.selectColor = (0, 200, 0)
        else:
            self.selectColor = (200, 0, 0)

        # world get
        if not world_open[self.world - 1][0]:
            self.selectColor = (200, 200, 0)
            mouse_pos = pygame.mouse.get_pos()
            if world_rect.collidepoint(mouse_pos):
                if world_open[self.world - 1][1] >= 1000000:
                    cost_p = f"{world_open[self.world - 1][1] / 1000000:.0f}M"
                elif world_open[self.world - 1][1] >= 1000:
                    cost_p = f"{world_open[self.world - 1][1] / 1000:.0f}K"
                else:
                    cost_p = f"{world_open[self.world - 1][1]:.0f}"
                cost_text = font.render(f"{cost_p}-World {self.world - 1}", 0, (200, 200, 0))
                screen.blit(cost_text, (mouse_pos[0] - 50, self.y - 24))

        # draw inside border
        pygame.draw.rect(screen, self.selectColor, (self.x + 1, self.y + 1, self.width - 2, self.height - 2), 2)

        locations = [((self.x + 150 - 15, self.y + 25), (self.x + 100 + 10, self.y + 10)), ((self.x + 155 - 20, self.y + 25), (self.x + 100 + 10, self.y + 40)),
                    ((self.x - 50 + 15, self.y + 25), (self.x - 10, self.y + 10)), ((self.x - 50 + 15, self.y + 25), (self.x - 10, self.y + 40))]
        for i in range(len(locations)):
            pygame.draw.line(screen, (255, 255, 255), locations[i][0], locations[i][1])
        left = pygame.draw.rect(screen, (255, 255, 255), (self.leftX, self.leftY, self.leftSize, self.leftSize), 1, 10)
        right = pygame.draw.rect(screen, (255, 255, 255), (self.rightX, self.rightY, self.rightSize, self.rightSize), 1, 10)
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]
        if left.collidepoint(mouse_pos):
            if self.leftSize < self.maxSize:
                self.leftSize += 1
                self.leftX -= 0.5
                self.leftY -= 0.5
        else:
            if self.leftSize > self.minSize:
                self.leftSize -= 1
                self.leftX += 0.5
                self.leftY += 0.5
        if right.collidepoint(mouse_pos):
            if self.rightSize < self.maxSize:
                self.rightSize += 1
                self.rightX -= 0.5
                self.rightY -= 0.5
        else:
            if self.rightSize > self.minSize:
                self.rightSize -= 1
                self.rightX += 0.5
                self.rightY += 0.5
        for i in range(len(world_open)):
            if i != 0 and not world_open[i][0]:
                if world_open[i][1] <= best_kills[i - 1]:
                    world_open[i] = (True, world_open[i][1])

    def click(self):
        left = pygame.Rect(self.leftX, self.leftY, self.leftSize, self.leftSize)
        right = pygame.Rect(self.rightX, self.rightY, self.rightSize, self.rightSize)
        mouse_pos = pygame.mouse.get_pos()
        if left.collidepoint(mouse_pos):
            if self.world < 3:
                self.world += 1
        if right.collidepoint(mouse_pos):
            if self.world > 1:
                self.world -= 1
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if rect.collidepoint(mouse_pos) and world_open[self.world - 1][0]:
            self.selectedWorld = self.world


class StatsButton():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 35
        self.color = (255, 255, 255)
        self.insideColor = (0, 255, 0)
        self.maxSize = self.size + 10
        self.minSize = self.size
        self.speed = 2

    def render(self, statsScreenRun):
        global HomeScreenRun, mouse_effect_list
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]

        if statsScreenRun:
            self.insideColor = (0, 255, 255)
        else:
            self.insideColor = (0, 0, 0)

        pygame.draw.rect(screen, self.insideColor, (self.x + 1, self.y + 1, self.size - 2, self.size - 2), 2, 2)
        stats_button_rect = pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size), 1, 5)

        locations = [(self.x + self.size / 4, (self.y + self.size / 4)), (self.x + self.size / 4, self.y + (self.size / 4 * 2)),
                    (self.x + self.size / 4, self.y + (self.size / 4 * 3))]

        for i in range(len(locations)):
            pygame.draw.circle(screen, self.color, locations[i], 2, 1)
            pygame.draw.rect(screen, self.color, (locations[i][0] + 5, locations[i][1] - 1.5, self.size / 2, 3), 1, 3)

        if stats_button_rect.collidepoint(mouse_pos):
            if self.size < self.maxSize:
                self.size += self.speed
                self.x -= self.speed / 2
                self.y -= self.speed / 2
            if mouse_press and not statsScreenRun:
                statsScreenRun = True
                upgradeScreenRun = False
                HomeScreenRun = False
                StatsScreen(statsScreenRun)
        else:
            if self.size > self.minSize:
                self.size -= self.speed
                self.x += self.speed / 2
                self.y += self.speed / 2

class UpgradeButton():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 35
        self.color = (255, 255, 255)
        self.insideColor = (0, 255, 0)
        self.maxSize = self.size + 10
        self.minSize = self.size
        self.speed = 2

    def render(self, upgradeScreenRun):
        global HomeScreenRun, mouse_effect_list
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]

        if upgradeScreenRun:
            self.insideColor = (0, 255, 255)
        else:
            self.insideColor = (0, 0, 0)

        pygame.draw.rect(screen, self.insideColor, (self.x + 1, self.y + 1, self.size - 2, self.size - 2), 2, 2)
        upgrade_button_rect = pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size), 1, 5)

        locations = [((self.x + self.size / 2, self.y + 10), (self.x + 10, self.y + 15)),
                     ((self.x + self.size / 2, self.y + 10), (self.x + self.size - 10, self.y + 15)),
                     ((self.x + self.size / 2, self.y + 10), (self.x + self.size / 2, self.y + self.size - 10))
                    ]
        for i in range(3):
            pygame.draw.aaline(screen, self.color, locations[i][0], locations[i][1])

        if upgrade_button_rect.collidepoint(mouse_pos):
            if self.size < self.maxSize:
                self.size += self.speed
                self.x -= self.speed / 2
                self.y -= self.speed / 2
            if mouse_press and not upgradeScreenRun:
                upgradeScreenRun = True
                statsScreenRun = False
                HomeScreenRun = False
                UpgradeScreen(upgradeScreenRun)
        else:
            if self.size > self.minSize:
                self.size -= self.speed
                self.x += self.speed / 2
                self.y += self.speed / 2



class HomeButton():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 50
        self.color = (255, 255, 255)
        self.insideColor = (0, 255, 0)
        self.maxSize = self.size  + 10
        self.minSize = self.size
        self.speed = 2

    def render(self, HomeScreenRun):
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]

        if HomeScreenRun:
            self.insideColor = (0, 255, 255)
        else:
            self.insideColor = (0, 0, 0)

        pygame.draw.rect(screen, self.insideColor, (self.x + 1, self.y + 1, self.size - 2, self.size - 2), 2, 2)
        home_button_rect = pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size), 1, 5)

        locations = [((self.x + self.size / 2, self.y + 10), (self.x + 5, self.y + 20)),
                     ((self.x + self.size / 2, self.y + 10), (self.x + self.size - 5, self.y + 20)),
                     ((self.x + 5, self.y + 20), (self.x + self.size - 5, self.y + 20)),
                     ((self.x + 10, self.y + 20), (self.x + 10, self.y + self.size - 10)),
                     ((self.x + self.size - 10, self.y + 20), (self.x + self.size - 10, self.y + self.size - 10)),
                     ((self.x + 10, self.y + self.size - 10), (self.x + self.size - 10, self.y + self.size - 10))
                    ]
        for i in range(6):
            pygame.draw.line(screen, self.color, locations[i][0], locations[i][1
            ])

        if home_button_rect.collidepoint(mouse_pos):
            if self.size < self.maxSize:
                self.size += self.speed
                self.x -= self.speed / 2
                self.y -= self.speed / 2
            if mouse_press and not HomeScreenRun:
                HomeScreenRun = True
                upgradeScreenRun = False
                HomeScreen(HomeScreenRun)
        else:
            if self.size > self.minSize:
                self.size -= self.speed
                self.x += self.speed / 2
                self.y += self.speed / 2



def drawItem(x, y, item, color):
    pygame.draw.rect(screen, (255, 255, 255), (x, y, 150, 50), 1, 5)
    if color == (200, 200, 0):
        text = f"{item:.0f}"
    else:
        text = f"{item:.1f}"
    item_text = big_num_font.render(text, 0, color)
    screen.blit(item_text, (x + 7, y - 1))



class MouseEffect():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.color = 255
        self.speed = 5

    def render(self):
        finalColor = (self.color, self.color, self.color)
        if self.color > 0:
            pygame.draw.circle(screen, finalColor, (self.x, self.y), self.radius, 1)
        self.radius += self.speed
        if self.radius > screen_w * 2:
            mouse_effect_list.remove(self)

def drawMouseEffect():
    for mouse_effect in mouse_effect_list:
        MouseEffect.render(mouse_effect)



class PlayButton():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (255, 255, 255)
        self.maxSize = width + 50
        self.minSize = width
        self.speed = 4

    def render(self):
        mouse_pos = pygame.mouse.get_pos()

        play_button_rect = pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 3, 10)
        play_text = big_font.render(f"Play", 0, self.color)
        screen.blit(play_text, (self.x + self.width / 2 - 75, self.y + self.height / 2 - 35))

        if play_button_rect.collidepoint(mouse_pos):
            if self.width < self.maxSize:
                self.width += self.speed
                self.height += self.speed
                self.x -= self.speed / 2
                self.y -= self.speed / 2
        else:
            if self.width > self.minSize:
                self.width -= self.speed
                self.height -= self.speed
                self.x += self.speed / 2
                self.y += self.speed / 2

    def click(self):
        mouse_pos = pygame.mouse.get_pos()
        play_button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if play_button_rect.collidepoint(mouse_pos):
            mouse_effect_list.clear()
            GameRun = True
            HomeScreenRun = False
            Game(GameRun)



def HomeScreen(HomeScreenRun):
    global up_list, world_choose, set_world

    # upgrades
    if not set_upgrades:
        damage_up = 0
        speed_up = 0
        bullet_rate_up = 0
        bullet_speed_up = 0
        hp_up = 0
        drone_bullet_rate_up = 0
        drone_bullet_speed_up = 0
        drone_hp_up = 0
        coin_multiple_up = 1
        up_list = [damage_up, speed_up, bullet_rate_up, bullet_speed_up, hp_up, drone_bullet_rate_up, drone_bullet_speed_up,
        drone_hp_up, coin_multiple_up]

    if not set_world:
        world_choose = WorldChoose(screen_w / 2 - 50, screen_h / 2 + 100)
        set_world = True

    play_button = PlayButton(screen_w / 2 - 100, screen_h / 2 - 50, 200, 100)
    pygame.mouse.set_visible(True)

    home_button = HomeButton(screen_w / 2 - 25, screen_h - 55)
    upgrade_button = UpgradeButton(screen_w / 2 + 25 + 32, screen_h - 40)
    stats_button = StatsButton(screen_w / 2 - 75 - (35 / 2), screen_h - 40)

    createDB()
    load()

    while HomeScreenRun:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_effect = MouseEffect(mouse_x, mouse_y)
                mouse_effect_list.append(mouse_effect)
                WorldChoose.click(world_choose)
                PlayButton.click(play_button)

        for i in range(world_choose.selectedWorld):
            if i + 1 == world_choose.selectedWorld:
                background(background_world[i][0], background_world[i][1], 50)

        # buttons
        PlayButton.render(play_button)
        HomeButton.render(home_button, HomeScreenRun)
        UpgradeButton.render(upgrade_button, upgradeScreenRun)
        StatsButton.render(stats_button, statsScreenRun)
        WorldChoose.render(world_choose)

        # mouse
        drawMouseEffect()

        # items
        drawItem(20, 20, coins, (255, 215, 0))
        for i in range(world_choose.selectedWorld):
            if i + 1 == world_choose.selectedWorld:
                drawItem(190, 20, best_kills[i], (200, 200, 0))


        pygame.display.update()
        clock.tick(120)





class HomeUpgrades():
    def __init__(self, x, y, name, price, pricePerUpgrade, upByUpgrade):
        self.x = x
        self.y = y
        self.name = name
        self.price = price
        self.pricePerUpgrade = pricePerUpgrade
        self.upByUpgrade = upByUpgrade
        self.width = 155
        self.height = 100
        self.color = (255, 255, 255)
        self.bckColor = (255, 0, 0)
        self.buttonWidth = 30
        self.buttonMaxWidth = self.buttonWidth
        self.buttonHeight = 20
        self.buttonX = self.x + 10
        self.buttonY = self.y + self.height - 30
        self.textColor = (0, 0, 0)

    def render(self, up):
        global coins, damage_up, speed_up, bullet_rate_up, hp_up, drone_bullet_rate_up
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]

        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 2, 5)
        upgrade_name = cool_font.render(self.name, 0, (255, 255, 255))
        screen.blit(upgrade_name, (self.x + 10, self.y + 10))

        upgrade_text = num_font.render(f"{up:.2f}", 0, (255, 255, 255))
        screen.blit(upgrade_text, (self.x + 10, self.y + 40))

        if coins >= self.price:
            self.bckColor = (0, 190, 0)
        else:
            self.bckColor = (190, 0, 0)

        pygame.draw.rect(screen, self.bckColor, (self.buttonX + 1, self.buttonY + 1, self.buttonWidth - 2, self.buttonHeight - 2), 0, 10)
        button = pygame.draw.rect(screen, self.color, (self.buttonX, self.buttonY, self.buttonWidth, self.buttonHeight), 1, 10)

        if self.price >= 1000000:
            price_p = f"{self.price / 1000000:.2f}M"
        elif self.price >= 1000:
            price_p = f"{self.price / 1000:.2f}K"
        else:
            price_p = f"{self.price:.2f}"
        prise_text = little_font.render(price_p, 0, (255, 255, 255))
        screen.blit(prise_text, (self.x + 40, self.y + self.height - 29))

        if button.collidepoint(mouse_pos):
            if self.buttonWidth > self.buttonMaxWidth - 5:
                self.buttonWidth -= 1
                self.buttonHeight -= 1
                self.buttonX += 0.5
                self.buttonY += 0.5
        else:
            if self.buttonWidth < self.buttonMaxWidth:
                self.buttonWidth += 1
                self.buttonHeight += 1
                self.buttonX -= 0.5
                self.buttonY -= 0.5

    def click(self):
        global coins, up_list, upgrade_prices
        button = pygame.Rect(self.buttonX, self.buttonY, self.buttonWidth, self.buttonHeight)
        mouse_pos = pygame.mouse.get_pos()
        if button.collidepoint(mouse_pos) and coins >= self.price:
            coins -= self.price
            if not self.name == 'coins':
                self.price += self.pricePerUpgrade
            else:
                self.price *= self.pricePerUpgrade
            if self.name == 'damage':
                up_list[0] += self.upByUpgrade
                upgrade_prices[0] = self.price
            if self.name == 'speed':
                up_list[1] += self.upByUpgrade
                upgrade_prices[1] = self.price
            if self.name == 'BR':
                up_list[2] += self.upByUpgrade
                upgrade_prices[2] = self.price
            if self.name == 'BS':
                up_list[3] += self.upByUpgrade
                upgrade_prices[3] = self.price
            if self.name == 'HP':
                up_list[4] += self.upByUpgrade
                upgrade_prices[4] = self.price
            if self.name == 'drone BR':
                up_list[5] += self.upByUpgrade
                upgrade_prices[5] = self.price
            if self.name == 'drone BS':
                up_list[6] += self.upByUpgrade
                upgrade_prices[6] = self.price
            if self.name == 'drone HP':
                up_list[7] += self.upByUpgrade
                upgrade_prices[7] = self.price
            if self.name == 'coins':
                up_list[8] += self.upByUpgrade
                upgrade_prices[8] = self.price
            saveDB()


def UpgradeScreen(upgradeScreenRun):
    global set_upgrades, upgrades_list, up_list, upgrade_prices

    home_button = HomeButton(screen_w / 2 - 25, screen_h - 55)
    upgrade_button = UpgradeButton(screen_w / 2 + 25 + 32, screen_h - 40)
    stats_button = StatsButton(screen_w / 2 - 75 - (35 / 2), screen_h - 40)


    if not set_upgrades:
        damage_upgrade = HomeUpgrades(20, 100, 'damage', upgrade_prices[0], 20, 0.1)
        speed_upgrade = HomeUpgrades(190, 100, 'speed', upgrade_prices[1], 50, 0.2)
        bullet_rate_upgrade = HomeUpgrades(360, 100, 'BR', upgrade_prices[2], 25, 0.1)
        bullet_speed_upgrade = HomeUpgrades(530, 100, 'BS', upgrade_prices[3], 50, 0.1)
        Hp_upgrade = HomeUpgrades(20, 220, 'HP', upgrade_prices[4], 15, 0.4)
        drone_bullet_rate_upgrade = HomeUpgrades(190, 220, 'drone BR', upgrade_prices[5], 50, 0.1)
        drone_bullet_speed_upgrade = HomeUpgrades(360, 220, 'drone BS', upgrade_prices[6], 100, 0.1)
        drone_hp_upgrade = HomeUpgrades(530, 220, 'drone HP', upgrade_prices[7], 25, 0.1)
        coin_multiple_upgrade = HomeUpgrades(20, 340, 'coins', upgrade_prices[8], 2, 1)
        set_upgrades = True
        upgrades_list = (
         damage_upgrade, speed_upgrade, bullet_rate_upgrade, bullet_speed_upgrade, Hp_upgrade,
         drone_bullet_rate_upgrade, drone_bullet_speed_upgrade, drone_hp_upgrade, coin_multiple_upgrade)

    while upgradeScreenRun:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_effect = MouseEffect(mouse_x, mouse_y)
                mouse_effect_list.append(mouse_effect)
                for upgrade in upgrades_list:
                    HomeUpgrades.click(upgrade)

        for i in range(world_choose.selectedWorld):
            if i + 1 == world_choose.selectedWorld:
                background(background_world[i][0], background_world[i][1], 50)

        # buttons
        HomeButton.render(home_button, HomeScreenRun)
        UpgradeButton.render(upgrade_button, upgradeScreenRun)
        StatsButton.render(stats_button, statsScreenRun)

        # mouse
        drawMouseEffect()

        # items
        drawItem(20, 20, coins, (255, 215, 0))

        # upgrades
        for i in range(len(up_list)):
            HomeUpgrades.render(upgrades_list[i], up_list[i])

        pygame.display.update()
        clock.tick(120)


def drawStats(stat, x, y, name, color):
    pygame.draw.rect(screen, (255, 255, 255), (x, y, 100, 50), 1, 10)
    if stat > 1000000:
        stats_p = f"{stat / 1000000:.0f}M"
    elif stat > 1000:
        stats_p = f"{stat / 1000:.0f}K"
    else:
        if not name == 'TROPHY':
            stats_p = f"{stat:.1f}"
        else:
            stats_p = f"{stat:.0f}"
    stat_text = big_stat_font.render(f"{stats_p}", 0, color)
    screen.blit(stat_text, (x + 5, y + 5))
    stats_name = font.render(f"{name}", 0, (255, 255, 255))
    screen.blit(stats_name, (x, y - 25))

def drawStatsPlayer():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.rect(screen, (200, 0, 0), (screen_w / 2 - 100, screen_h / 2 - 100, 200, 200), 2, 30)
    dx = mouse_x - (screen_w / 2)
    dy = mouse_y - (screen_h / 2)
    angle = math.atan2(dy, dx)
    gun_x = (screen_w / 2) + 150 * math.cos(angle)
    gun_y = (screen_h / 2) + 150 * math.sin(angle)
    pygame.draw.line(screen, (255, 255, 255), (screen_w / 2, screen_h / 2), (gun_x, gun_y))
    pygame.draw.circle(screen, (255, 255, 255), (screen_w / 2, screen_h / 2), 30)


def StatsScreen(statsScreenRun):

    home_button = HomeButton(screen_w / 2 - 25, screen_h - 55)
    upgrade_button = UpgradeButton(screen_w / 2 + 25 + 32, screen_h - 40)
    stats_button = StatsButton(screen_w / 2 - 75 - (35 / 2), screen_h - 40)

    while statsScreenRun:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_effect = MouseEffect(mouse_x, mouse_y)
                mouse_effect_list.append(mouse_effect)

        for i in range(world_choose.selectedWorld):
            if i + 1 == world_choose.selectedWorld:
                background(background_world[i][0], background_world[i][1], 50)

        # buttons
        HomeButton.render(home_button, HomeScreenRun)
        UpgradeButton.render(upgrade_button, upgradeScreenRun)
        StatsButton.render(stats_button, statsScreenRun)

        drawStatsPlayer()
        # hp
        drawStats(up_list[4] + 100, screen_w / 2 - 50, screen_h / 2 - 200, 'HP', (0, 200, 0))
        # speed
        drawStats(1 + up_list[1], screen_w / 2 + 150, screen_h / 2 - 50, 'SPEED', (0, 200, 200))
        # damage
        drawStats(5 + up_list[0], screen_w / 2 - 250, screen_h / 2 - 50, 'DAMAGE', (200, 0, 0))
        # trophy
        drawStats(trophys, screen_w / 2 - 50, screen_h / 2 + 200, 'TROPHY', (200, 200, 0))

        # mouse
        drawMouseEffect()

        # items
        drawItem(20, 20, coins, (255, 215, 0))
        for i in range(world_choose.selectedWorld):
            if i + 1 == world_choose.selectedWorld:
                drawItem(190, 20, best_kills[i], (200, 200, 0))

        pygame.display.update()
        clock.tick(120)




def createDB():
    try:
        with open(file_location, 'r') as file:
            pass
    except FileNotFoundError:
        with open(file_location, 'w'):
            pass

def saveDB():
    # set data to save here
    data_to_encrypt = {
        "up_list": up_list,
        "coins": coins,
        "best_kills": best_kills,
        "upgrade_prices": upgrade_prices,
        "trophys": trophys
    }

    json_data = json.dumps(data_to_encrypt).encode()
    encrypted_data = cipher_suite.encrypt(json_data)

    with open(file_location, 'wb') as file:
        file.write(encrypted_data)

def load():
    global up_list, coins, best_kills, upgrade_prices, trophys
    try:
        with open(file_location, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        json_decoded = json.loads(decrypted_data.decode())
        # load all data here
        up_list = json_decoded.get("up_list", [])
        coins = json_decoded.get("coins", 0)
        best_kills = json_decoded.get("best_kills", 0)
        upgrade_prices = json_decoded.get("upgrade_prices", [])
        trophys = json_decoded.get("trophys", 0)
    except Exception:
        pass

if __name__ == '__main__':
    HomeScreenRun = True
    HomeScreen(HomeScreenRun)
