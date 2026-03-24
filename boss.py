import pygame
import math
import random

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.radius = 36
        self.rect = pygame.Rect(int(x - self.radius), int(y - self.radius), self.radius * 2, self.radius * 2)
        self.speed = 0.8
        self.max_health = 180
        self.health = self.max_health
        self.shoot_cooldown = 45
        self.shoot_timer = random.randint(30, self.shoot_cooldown)
        self.melee_damage = 10
        self.type = "boss"

    def update(self, player):
        # 简单地朝玩家慢速移动
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(math.hypot(dx, dy), 0.1)
        self.rect.x += int(self.speed * dx / dist)
        self.rect.y += int(self.speed * dy / dist)

        # 边界限制
        self.rect.x = max(0, min(self.rect.x, 800 - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, 600 - self.rect.height))

        # 射击逻辑：返回 BossBullet 给调用者（主循环负责加入组）
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_cooldown
            px, py = player.rect.center
            dx = px - self.rect.centerx
            dy = py - self.rect.centery
            d = math.hypot(dx, dy)
            if d == 0:
                d = 0.1
            dir_vec = pygame.Vector2(dx / d, dy / d)
            return BossBullet(self.rect.centerx, self.rect.centery, dir_vec)
        return None

    def take_damage(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.kill()
            return True
        return False

    def draw(self, surface):
        center = (int(self.rect.centerx), int(self.rect.centery))
        # 阴影
        shadow_surf = pygame.Surface((self.radius * 2 + 6, self.radius * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 100), (self.radius + 3, self.radius + 3), self.radius)
        surface.blit(shadow_surf, (center[0] - self.radius - 3, center[1] - self.radius - 3))

        # 渐变圆体
        for r in range(self.radius, 0, -1):
            ratio = r / self.radius
            color = (
                int(200 * (1 - ratio) + 120 * ratio),
                int(60 * (1 - ratio) + 100 * ratio),
                int(60 * (1 - ratio) + 200 * ratio),
            )
            pygame.draw.circle(surface, color, center, r)

        # 血条
        bar_w, bar_h = 120, 10
        bx = center[0] - bar_w // 2
        by = center[1] - self.radius - 18
        pygame.draw.rect(surface, (40, 40, 40), (bx, by, bar_w, bar_h))
        fill = max(0, int(bar_w * (self.health / max(1, self.max_health))))
        pygame.draw.rect(surface, (255, 80, 80), (bx, by, fill, bar_h))
        pygame.draw.rect(surface, (255, 255, 255, 150), (bx, by, bar_w, bar_h), 1)


class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.velocity = direction * 6

    def draw(self, surface):
        center = self.rect.center
        for r in range(8, 4, -1):
            alpha = int(60 * (1 - (8 - r) / 4))
            glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 150, 50, alpha), (r, r), r)
            surface.blit(glow, (center[0] - r, center[1] - r))
        pygame.draw.circle(surface, (255, 170, 60), center, 6)

    def update(self):
        self.rect.x += int(self.velocity.x)
        self.rect.y += int(self.velocity.y)
        if not (0 <= self.rect.x <= 800 and 0 <= self.rect.y <= 600):
            self.kill()
