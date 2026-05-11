import pygame
import random

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60

# Цвета
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 150, 0)

# Направления
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

class Tank:
    """Базовый класс для танков (игрок и враги)"""
    def __init__(self, x, y, color, speed=2):
        self.x = x
        self.y = y
        self.direction = UP
        self.speed = speed
        self.cooldown = 0
        self.color = color
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.alive = True
        self.invincible_frames = 0

    def move(self, walls, tanks):
        dx, dy = 0, 0
        if self.direction == UP:
            dy = -self.speed
        elif self.direction == RIGHT:
            dx = self.speed
        elif self.direction == DOWN:
            dy = self.speed
        elif self.direction == LEFT:
            dx = -self.speed

        new_rect = pygame.Rect(self.x + dx, self.y + dy, TILE_SIZE, TILE_SIZE)
        can_move = True

        for wall in walls:
            if new_rect.colliderect(wall.rect):
                can_move = False
                break

        if can_move:
            for tank in tanks:
                if tank != self and tank.alive:
                    if new_rect.colliderect(tank.rect):
                        can_move = False
                        break

        if can_move:
            self.x += dx
            self.y += dy
            self.rect.x = self.x
            self.rect.y = self.y

        self.x = max(0, min(SCREEN_WIDTH - TILE_SIZE, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - TILE_SIZE, self.y))
        self.rect.x = self.x
        self.rect.y = self.y

    def shoot(self):
        if self.cooldown <= 0:
            bullet_x = self.x + TILE_SIZE // 2 - 2
            bullet_y = self.y + TILE_SIZE // 2 - 2

            if self.direction == UP:
                bullet_x = self.x + TILE_SIZE // 2 - 2
                bullet_y = self.y
            elif self.direction == RIGHT:
                bullet_x = self.x + TILE_SIZE
                bullet_y = self.y + TILE_SIZE // 2 - 2
            elif self.direction == DOWN:
                bullet_x = self.x + TILE_SIZE // 2 - 2
                bullet_y = self.y + TILE_SIZE
            elif self.direction == LEFT:
                bullet_x = self.x
                bullet_y = self.y + TILE_SIZE // 2 - 2

            bullet = Bullet(bullet_x, bullet_y, self.direction, self)
            self.cooldown = 30
            return bullet
        return None

    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.rect(screen, self.color, (self.x, self.y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, TILE_SIZE, TILE_SIZE), 2)

        gun_x, gun_y = self.x + TILE_SIZE // 2, self.y + TILE_SIZE // 2
        if self.direction == UP:
            pygame.draw.line(screen, BLACK, (gun_x, gun_y), (gun_x, gun_y - 20), 4)
        elif self.direction == RIGHT:
            pygame.draw.line(screen, BLACK, (gun_x, gun_y), (gun_x + 20, gun_y), 4)
        elif self.direction == DOWN:
            pygame.draw.line(screen, BLACK, (gun_x, gun_y), (gun_x, gun_y + 20), 4)
        elif self.direction == LEFT:
            pygame.draw.line(screen, BLACK, (gun_x, gun_y), (gun_x - 20, gun_y), 4)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.invincible_frames > 0:
            self.invincible_frames -= 1

    def hit(self):
        if self.invincible_frames <= 0:
            self.alive = False
            return True
        return False


class EnemyTank(Tank):
    """Вражеский танк с ИИ (красный)"""
    def __init__(self, x, y):
        super().__init__(x, y, RED, speed=1)
        self.change_dir_timer = random.randint(30, 90)
        self.shoot_timer = random.randint(60, 120)

    def update(self, walls, enemies, player):
        super().update()

        self.change_dir_timer -= 1
        if self.change_dir_timer <= 0:
            self.direction = random.randint(0, 3)
            self.change_dir_timer = random.randint(30, 90)

        self.move(walls, enemies + [player])

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            bullet = self.shoot()
            self.shoot_timer = random.randint(60, 120)
            return bullet
        return None


class Bullet:
    def __init__(self, x, y, direction, owner):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 5
        self.active = True
        self.rect = pygame.Rect(x, y, 4, 4)
        self.owner = owner

    def move(self):
        if self.direction == UP:
            self.y -= self.speed
        elif self.direction == RIGHT:
            self.x += self.speed
        elif self.direction == DOWN:
            self.y += self.speed
        elif self.direction == LEFT:
            self.x -= self.speed

        self.rect.x = self.x
        self.rect.y = self.y

        if (self.x < 0 or self.x > SCREEN_WIDTH or
                self.y < 0 or self.y > SCREEN_HEIGHT):
            self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, 4, 4))


class Wall:
    def __init__(self, x, y, breakable=True):
        self.x = x
        self.y = y
        self.breakable = breakable
        self.color = BROWN if breakable else GRAY
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, TILE_SIZE, TILE_SIZE), 1)


class Base:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.destroyed = False

    def draw(self, screen):
        if not self.destroyed:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, TILE_SIZE, TILE_SIZE))
            center_x = self.x + TILE_SIZE // 2
            center_y = self.y + TILE_SIZE // 2
            pygame.draw.circle(screen, BLACK, (center_x, center_y), TILE_SIZE // 3)
            pygame.draw.polygon(screen, BLACK, [(center_x, center_y - 10), (center_x - 5, center_y), (center_x + 5, center_y)])
            pygame.draw.rect(screen, BLACK, (self.x + TILE_SIZE//4, self.y + TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//4))
        else:
            pygame.draw.rect(screen, BLACK, (self.x, self.y, TILE_SIZE, TILE_SIZE))

    def destroy(self):
        self.destroyed = True


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Battle City")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)  # для правил
        self.reset_game()

    def reset_game(self):
        # Игрок появляется в правом нижнем углу, отступ от границ
        self.player_start_x = SCREEN_WIDTH - 2 * TILE_SIZE   # 720
        self.player_start_y = SCREEN_HEIGHT - 2 * TILE_SIZE  # 520
        self.player = Tank(self.player_start_x, self.player_start_y, GREEN)
        self.player.alive = True
        self.player.invincible_frames = 60
        self.lives = 3

        self.bullets = []

        self.walls = []
        self.create_walls()

        base_x = SCREEN_WIDTH // 2 - TILE_SIZE // 2
        base_y = SCREEN_HEIGHT - TILE_SIZE * 2
        self.base = Base(base_x, base_y)

        self.enemies = []
        # ИЗМЕНЕНО: 20 врагов вместо 5
        self.enemies_to_spawn = 20
        self.spawn_timer = 0
        self.spawn_delay = 60

        self.score = 0
        self.game_over = False
        self.victory = False
        self.show_rules = False  # НОВОЕ: флаг отображения правил
        self.spawn_enemy()

    def create_walls(self):
        # Границы (неразрушаемые)
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            self.walls.append(Wall(x, 0, False))
            self.walls.append(Wall(x, SCREEN_HEIGHT - TILE_SIZE, False))
        for y in range(TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE, TILE_SIZE):
            self.walls.append(Wall(0, y, False))
            self.walls.append(Wall(SCREEN_WIDTH - TILE_SIZE, y, False))

        # Защита базы: разрушаемые стены (кирпичи) вокруг
        base_x = SCREEN_WIDTH // 2 - TILE_SIZE // 2
        base_y = SCREEN_HEIGHT - TILE_SIZE * 2
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                wall_x = base_x + i * TILE_SIZE
                wall_y = base_y + j * TILE_SIZE
                if 0 <= wall_x < SCREEN_WIDTH and 0 <= wall_y < SCREEN_HEIGHT:
                    self.walls.append(Wall(wall_x, wall_y, True))

        # Случайные разрушаемые стены (кирпичи) – исключаем позицию спавна игрока
        player_spawn_rect = pygame.Rect(self.player_start_x, self.player_start_y, TILE_SIZE, TILE_SIZE)
        for _ in range(50):
            x = random.randint(2, (SCREEN_WIDTH // TILE_SIZE) - 3) * TILE_SIZE
            y = random.randint(2, (SCREEN_HEIGHT // TILE_SIZE) - 3) * TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if rect.colliderect(player_spawn_rect):
                continue
            if (abs(x - self.player_start_x) > 100 or abs(y - self.player_start_y) > 100) and \
               not (base_x - TILE_SIZE <= x <= base_x + TILE_SIZE*2 and
                    base_y - TILE_SIZE <= y <= base_y + TILE_SIZE*2):
                self.walls.append(Wall(x, y, True))

        # Неразрушаемые стены (бетон) – случайные
        for _ in range(20):
            x = random.randint(2, (SCREEN_WIDTH // TILE_SIZE) - 3) * TILE_SIZE
            y = random.randint(2, (SCREEN_HEIGHT // TILE_SIZE) - 3) * TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if rect.colliderect(player_spawn_rect):
                continue
            if (abs(x - self.player_start_x) > 100 or abs(y - self.player_start_y) > 100) and \
               not (base_x - TILE_SIZE <= x <= base_x + TILE_SIZE*2 and
                    base_y - TILE_SIZE <= y <= base_y + TILE_SIZE*2):
                self.walls.append(Wall(x, y, False))

    def spawn_enemy(self):
        if self.enemies_to_spawn > 0:
            # Увеличим количество попыток, чтобы избежать бесконечного цикла
            for _ in range(50):
                x = random.choice([TILE_SIZE, SCREEN_WIDTH//2 - TILE_SIZE//2, SCREEN_WIDTH - TILE_SIZE*2])
                y = TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                collision = False
                for wall in self.walls:
                    if rect.colliderect(wall.rect):
                        collision = True
                        break
                for enemy in self.enemies:
                    if rect.colliderect(enemy.rect):
                        collision = True
                        break
                if rect.colliderect(self.player.rect):
                    collision = True
                if not collision:
                    enemy = EnemyTank(x, y)
                    self.enemies.append(enemy)
                    self.enemies_to_spawn -= 1
                    return
            # Если не нашли место, просто спавним в углу
            x = TILE_SIZE
            y = TILE_SIZE
            enemy = EnemyTank(x, y)
            self.enemies.append(enemy)
            self.enemies_to_spawn -= 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self.reset_game()
                if event.key == pygame.K_SPACE and not self.game_over and self.player.alive:
                    bullet = self.player.shoot()
                    if bullet:
                        self.bullets.append(bullet)
                # НОВОЕ: показ правил по клавише E
                if event.key == pygame.K_e:
                    self.show_rules = not self.show_rules

        if not self.game_over and self.player.alive:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player.direction = UP
                self.player.move(self.walls, [self.player] + self.enemies)
            if keys[pygame.K_RIGHT]:
                self.player.direction = RIGHT
                self.player.move(self.walls, [self.player] + self.enemies)
            if keys[pygame.K_DOWN]:
                self.player.direction = DOWN
                self.player.move(self.walls, [self.player] + self.enemies)
            if keys[pygame.K_LEFT]:
                self.player.direction = LEFT
                self.player.move(self.walls, [self.player] + self.enemies)

        return True

    def update(self):
        if self.game_over:
            return

        self.player.update()
        if not self.player.alive:
            self.lives -= 1
            if self.lives > 0:
                # Возрождение на той же позиции
                self.player = Tank(self.player_start_x, self.player_start_y, GREEN)
                self.player.alive = True
                self.player.invincible_frames = 60
                self.bullets = [b for b in self.bullets if b.owner != self.player]
            else:
                self.game_over = True
                return

        if self.enemies_to_spawn > 0:
            if self.spawn_timer <= 0:
                self.spawn_enemy()
                self.spawn_timer = self.spawn_delay
            else:
                self.spawn_timer -= 1

        bullets_to_add = []
        for enemy in self.enemies[:]:
            if not enemy.alive:
                self.enemies.remove(enemy)
                self.score += 100
                continue
            bullet = enemy.update(self.walls, self.enemies, self.player)
            if bullet:
                bullets_to_add.append(bullet)

        self.bullets.extend(bullets_to_add)

        for bullet in self.bullets[:]:
            bullet.move()

            hit_wall = False
            for wall in self.walls[:]:
                if bullet.rect.colliderect(wall.rect):
                    if wall.breakable:
                        self.walls.remove(wall)
                    bullet.active = False
                    hit_wall = True
                    break
            if hit_wall:
                self.bullets.remove(bullet)
                continue

            if not self.base.destroyed and bullet.rect.colliderect(self.base.rect):
                self.base.destroy()
                bullet.active = False
                self.bullets.remove(bullet)
                self.game_over = True
                continue

            if bullet.owner != self.player and self.player.alive and bullet.rect.colliderect(self.player.rect):
                if self.player.hit():
                    self.bullets.remove(bullet)
                    continue

            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if isinstance(bullet.owner, EnemyTank) and isinstance(enemy, EnemyTank):
                        continue
                    if bullet.owner != enemy and bullet.rect.colliderect(enemy.rect):
                        if enemy.hit():
                            pass
                        bullet.active = False
                        self.bullets.remove(bullet)
                        break

            if not bullet.active and bullet in self.bullets:
                self.bullets.remove(bullet)

        # Проверка победы: уничтожены все враги и больше нет в очереди
        if len(self.enemies) == 0 and self.enemies_to_spawn == 0:
            self.victory = True
            self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        for wall in self.walls:
            wall.draw(self.screen)

        self.base.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.player.alive:
            if self.player.invincible_frames > 0 and (pygame.time.get_ticks() // 100) % 2 == 0:
                pass
            else:
                self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        lives_text = self.font.render(f"Жизни: {self.lives}", True, GREEN)
        self.screen.blit(lives_text, (10, 50))

        enemies_left = len(self.enemies) + self.enemies_to_spawn
        enemies_text = self.font.render(f"Осталось уничтожить: {enemies_left}", True, GREEN)
        self.screen.blit(enemies_text, (10, 90))

        instr_text = self.small_font.render("Стрелки: движение, Пробел: стрельба, R: перезапуск, E: правила", True, BLUE)
        self.screen.blit(instr_text, (SCREEN_WIDTH//2 - 280, SCREEN_HEIGHT - 40))

        if self.show_rules:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            rules = [
                "ПРАВИЛА ИГРЫ:",
                "1. Управляйте зелёным танком с помощью стрелок.",
                "2. Стреляйте по красным вражеским танкам (Пробел).",
                "3. Уничтожьте все 20 вражеских танков для победы.",
                "4. Защищайте белую базу внизу экрана.",
                "5. Кирпичные стены можно разрушать, бетонные - нет.",
                "6. У вас 3 жизни. При столкновении с врагом или его пулей вы теряете жизнь.",
                "7. Нажмите R для перезапуска игры.",
                "8. Нажмите E, чтобы закрыть это окно."
            ]
            y_offset = SCREEN_HEIGHT // 2 - 100
            for line in rules:
                text = self.small_font.render(line, True, WHITE)
                self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_offset))
                y_offset += 25

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            if self.victory:
                msg = self.font.render("ПОБЕДА! Нажмите R для новой игры", True, GREEN)
            else:
                msg = self.font.render("ПОРАЖЕНИЕ! Нажмите R для новой игры", True, RED)
            self.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()