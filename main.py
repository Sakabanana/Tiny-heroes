import pygame
import random
import math
from boss import Boss, BossBullet

pygame.init()##初始化所有Pygame模板
pygame.key.stop_text_input()##停止文本输入事件，防止运行后键盘输入失效
screen = pygame.display.set_mode((800, 600))##创建游戏窗口并设置大小
pygame.display.set_caption("Tiny Heroes")##设置窗口标题
clock = pygame.time.Clock()##创建帧率控制器

'''
以下内容勿删：
代码写了目录看最后面
空行勿删
空行勿删
空行勿删
boss在同目录其他文件下
手势控制名为gesture_control
部分代码注释为更新后舍弃代码，但可以优化，勿删
以上内容勿删
'''

def get_font(size):
    # 创建一个中文字体兼容的字体获取函数，当前使用黑体，失败就用默认字体
    try:
        return pygame.font.SysFont("simhei", size)
    except:
        return pygame.font.Font(None, size)

# ===================== 美化辅助函数 =====================
def draw_gradient_circle(surface, center, radius, color1, color2):
    """绘制渐变圆形"""
    x, y = int(center[0]), int(center[1])
    for r in range(radius, 0, -1):
        ratio = r / radius
        color = tuple(int(c1 * (1-ratio) + c2 * ratio) for c1, c2 in zip(color1, color2))
        pygame.draw.circle(surface, color, (x, y), r)

def draw_shadow_circle(surface, center, radius, shadow_offset=2):
    """绘制圆形阴影"""
    shadow_surf = pygame.Surface((radius*2 + shadow_offset*2, radius*2 + shadow_offset*2), pygame.SRCALPHA)
    pygame.draw.circle(shadow_surf, (0, 0, 0, 80), (radius + shadow_offset, radius + shadow_offset), radius)
    surface.blit(shadow_surf, (center[0] - radius - shadow_offset, center[1] - radius - shadow_offset))

def draw_3d_cube(surface, rect, color, light_dir=(0.5, 0.5, 1)):
    """绘制3D立方体效果"""
    x, y, w, h = rect
    # 顶面（亮）
    light_color = tuple(min(255, c + 40) for c in color)
    # 右侧面（暗）
    dark_color = tuple(max(0, c - 40) for c in color)
    
    # 绘制阴影
    shadow_offset = 3
    shadow_rect = pygame.Rect(x + shadow_offset, y + shadow_offset, w, h)
    pygame.draw.rect(surface, (0, 0, 0, 60), shadow_rect)
    
    # 绘制主矩形
    pygame.draw.rect(surface, color, rect)
    
    # 绘制顶边和左边（高光）
    pygame.draw.line(surface, light_color, (x, y), (x + w, y), 2)
    pygame.draw.line(surface, light_color, (x, y), (x, y + h), 2)
    
    # 绘制底边和右边（阴影）
    pygame.draw.line(surface, dark_color, (x, y + h), (x + w, y + h), 2)
    pygame.draw.line(surface, dark_color, (x + w, y), (x + w, y + h), 2)

def draw_rounded_rect(surface, color, rect, radius=5, border_width=0, border_color=None):
    """绘制圆角矩形（支持RGBA）"""
    if color is None:
        return
    x, y, w, h = rect
    # 创建临时表面
    temp_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if len(color) == 4:  # RGBA
        pygame.draw.rect(temp_surf, color, (0, 0, w, h), border_radius=radius)
    else:  # RGB
        pygame.draw.rect(temp_surf, color, (0, 0, w, h), border_radius=radius)
    if border_width > 0 and border_color:
        if len(border_color) == 4:  # RGBA
            pygame.draw.rect(temp_surf, border_color, (0, 0, w, h), border_width, border_radius=radius)
        else:  # RGB
            pygame.draw.rect(temp_surf, border_color, (0, 0, w, h), border_width, border_radius=radius)
    surface.blit(temp_surf, (x, y))

def draw_health_bar(surface, x, y, width, height, current, maximum, bg_color=(50, 50, 50), fill_color=(0, 255, 0)):
    """绘制现代化血条"""
    # 背景
    draw_rounded_rect(surface, bg_color, (x, y, width, height), radius=3)
    
    # 填充
    if maximum > 0:
        fill_width = int(width * (current / maximum))
        if fill_width > 0:
            # 渐变效果
            for i in range(fill_width):
                ratio = i / width
                color = tuple(int(fill_color[j] * (1 - ratio * 0.3)) for j in range(3))
                pygame.draw.rect(surface, color, (x + i, y + 1, 1, height - 2))
        
        # 高光
        if fill_width > 2:
            highlight_color = tuple(min(255, c + 60) for c in fill_color)
            pygame.draw.line(surface, highlight_color, (x + 2, y + 1), (x + fill_width - 2, y + 1), 1)
    
    # 边框
    pygame.draw.rect(surface, (255, 255, 255, 100), (x, y, width, height), 1, border_radius=3)
'''
def draw_legend(surface):
    """在右下角绘制游戏图例"""
    # 图例框位置和大小（紧凑版本）
    legend_width = 200
    legend_height = 255
    legend_x = 800 - legend_width - 10
    legend_y = 600 - legend_height - 10
    
    # 绘制半透明背景
    legend_bg = pygame.Surface((legend_width, legend_height), pygame.SRCALPHA)
    legend_bg.fill((20, 20, 30, 220))
    surface.blit(legend_bg, (legend_x, legend_y))
    
    # 绘制边框
    legend_rect = pygame.Rect(legend_x, legend_y, legend_width, legend_height)
    pygame.draw.rect(surface, (255, 255, 255, 100), legend_rect, 2, border_radius=8)
    
    # 标题
    title_font = get_font(20)
    title_text = title_font.render("图例", True, (255, 255, 255))
    surface.blit(title_text, (legend_x + 10, legend_y + 8))
    
    # 绘制分隔线
    pygame.draw.line(surface, (255, 255, 255, 100), 
                    (legend_x + 10, legend_y + 35), 
                    (legend_x + legend_width - 10, legend_y + 35), 1)
    
    # 图例项
    legend_font = get_font(15)
    y_offset = legend_y + 45
    line_spacing = 35
    
    # 1. 玩家
    center = (legend_x + 20, y_offset + 8)
    size = 12
    forward = pygame.Vector2(0, -1)
    right = pygame.Vector2(1, 0)
    points = [
        center + forward * size,
        center - forward * size * 0.5 + right * size * 0.7,
        center - forward * size * 0.5 - right * size * 0.7
    ]
    pygame.draw.polygon(surface, (50, 200, 50), points)
    pygame.draw.polygon(surface, (100, 255, 100), points, 1)
    surface.blit(legend_font.render("= 玩家", True, (255, 255, 255)), (legend_x + 40, y_offset))
    y_offset += line_spacing
    
    # 2. 近战敌人
    enemy_rect = pygame.Rect(legend_x + 8, y_offset, 20, 20)
    draw_3d_cube(surface, enemy_rect, (200, 50, 50))
    surface.blit(legend_font.render("= 近战敌人", True, (255, 255, 255)), (legend_x + 32, y_offset + 3))
    y_offset += line_spacing
    
    # 3. 远程敌人
    draw_gradient_circle(surface, (legend_x + 18, y_offset + 10), 8, (30, 80, 200), (60, 120, 255))
    pygame.draw.circle(surface, (255, 255, 255, 150), (legend_x + 18, y_offset + 10), 8, 1)
    surface.blit(legend_font.render("= 远程敌人", True, (255, 255, 255)), (legend_x + 32, y_offset + 3))
    y_offset += line_spacing
    
    # 4. 陷阱
    x, y = legend_x + 18, y_offset + 10
    pygame.draw.circle(surface, (0, 0, 0, 60), (x + 1, y + 1), 8)
    draw_gradient_circle(surface, (x, y), 8, (255, 100, 100), (200, 30, 30))
    for angle in (0, 60, 120, 180, 240, 300):
        rad = math.radians(angle)
        x1 = x + math.cos(rad) * 6
        y1 = y + math.sin(rad) * 6
        x2 = x + math.cos(rad) * 10
        y2 = y + math.sin(rad) * 10
        pygame.draw.line(surface, (150, 20, 20), (x1, y1), (x2, y2), 2)
    surface.blit(legend_font.render("= 陷阱", True, (255, 255, 255)), (legend_x + 32, y_offset + 3))
    y_offset += line_spacing
    
    # 5. 道具 - 恢复
    draw_gradient_circle(surface, (legend_x + 18, y_offset + 10), 7, (50, 255, 50), (0, 200, 0))
    pygame.draw.circle(surface, (255, 255, 255, 150), (legend_x + 18, y_offset + 10), 7, 1)
    surface.blit(legend_font.render("= 恢复道具", True, (255, 255, 255)), (legend_x + 32, y_offset + 3))
    y_offset += line_spacing
    
    # 6. 道具 - 攻击
    draw_gradient_circle(surface, (legend_x + 18, y_offset + 10), 7, (255, 155, 55), (200, 55, 0))
    pygame.draw.circle(surface, (255, 255, 255, 150), (legend_x + 18, y_offset + 10), 7, 1)
    surface.blit(legend_font.render("= 攻击提升", True, (255, 255, 255)), (legend_x + 32, y_offset + 3))
    y_offset += line_spacing
    
    # 7. 道具 - 速度
    draw_gradient_circle(surface, (legend_x + 18, y_offset + 10), 7, (100, 150, 255), (0, 0, 200))
    pygame.draw.circle(surface, (255, 255, 255, 150), (legend_x + 18, y_offset + 10), 7, 1)
    surface.blit(legend_font.render("= 速度提升", True, (255, 255, 255)), (legend_x + 32, y_offset + 3))
'''
# ===================== 常量 =====================
PLAYER_SPEED = 4#玩家移动速度
ENEMY_SPEED = 2##近战敌人移动速度
RANGED_ENEMY_SPEED = 1.5##远程敌人移动速度
RANGED_SHOOT_COOLDOWN = 120##远程敌人射击冷却
ATTACK_COOLDOWN_TIME = 30##玩家攻击冷却时间
BULLET_SPEED = 10##子弹飞行速度
ITEM_SPAWN_TIME = 300##道具生成间隔
MAX_WAVES = 15  # 默认最大波次数（全局常量，供 spawn_wave 使用）

# ===================== 得分系统 =====================
SCORE_MELEE_ENEMY = 50  # 击败近战敌人得分
SCORE_RANGED_ENEMY = 80  # 击败远程敌人得分（更高因为更难对付）
SCORE_TRAP = 30  # 摧毁陷阱得分

# Boss 相关分数
BOSS_SCORE = 500

# 全局得分变量（在main函数中初始化）
score = 0
kills_melee = 0
kills_ranged = 0
kills_trap = 0


# ============================================================
#                         玩家类
# ============================================================
class Player(pygame.sprite.Sprite):#定义玩家类，继承自pygame的精灵基类
    def __init__(self):
        super().__init__()
        #玩家基本常量
        self.base_speed = PLAYER_SPEED# 存储玩家的基础移动速度
        self.speed = PLAYER_SPEED# 当前实际移动速度（可能被道具影响）
        self.health = 100# 当前生命值
        self.max_health = 100# 最大生命值上限
        self.damage = 10# 当前攻击伤害值
        self.base_damage = 10# 基础攻击伤害值（无道具加成时）
        self.attack_cooldown = 0# 攻击冷却计时器，0表示可以攻击
        self.attack_range = 60# 近战攻击范围（像素）从50增加到60
        self.facing = pygame.Vector2(1, 0) # 玩家朝向向量，初始朝右
        self.rect = pygame.Rect(400, 300, 10, 10)# 玩家的碰撞矩形，位置(400,300)，大小10x10
        self.power_timer = 0# 攻击力提升道具的剩余时间
        self.speed_timer = 0# 速度提升道具的剩余时间
        #受伤间隔常量
        self.invincible = False
        self.invincible_start_time = 0
        self.invincible_duration = 0
        self.last_hit_time = 0
        self.visible = True
        self.last_blink_time = 0
        self.blink_interval = 100  # 添加闪烁间隔属性

    def draw(self, surface):
        # 如果处于无敌状态且不可见，则不绘制
        if self.invincible and not self.visible:
            return
        # 绘制玩家图案及朝向
        center = pygame.Vector2(self.rect.center)# 获取玩家中心点坐标
        size = 22# 玩家三角形的尺寸
        forward = self.facing.normalize()# 向量标准化，转换为单位向量保存为方向
        right = pygame.Vector2(-forward.y, forward.x)# 计算右方向向量（与朝向垂直）
        # 绘制阴影
        shadow_offset = 3
        shadow_points = [
            center + forward * size + pygame.Vector2(shadow_offset, shadow_offset),
            center - forward * size * 0.5 + right * size * 0.7 + pygame.Vector2(shadow_offset, shadow_offset),
            center - forward * size * 0.5 - right * size * 0.7 + pygame.Vector2(shadow_offset, shadow_offset)
        ]
        pygame.draw.polygon(surface, (0, 0, 0, 100), shadow_points)
        points = [# 定义三角形的三个顶点坐标
            center + forward * size,
            center - forward * size * 0.5 + right * size * 0.7,
            center - forward * size * 0.5 - right * size * 0.7
        ]
        # 根据无敌状态调整颜色
        if self.invincible:
            # 无敌时：金色渐变
            base_color = (255, 215, 0)
            highlight_color = (255, 255, 100)
        else:
            # 正常时：绿色渐变
            base_color = (50, 200, 50)
            highlight_color = (100, 255, 100)
        # 绘制主体（渐变效果）
        pygame.draw.polygon(surface, base_color, points)
        # 绘制高光边缘
        if len(points) >= 3:
            # 计算高光点（在朝向方向的边缘）
            highlight_point = center + forward * size * 0.8
            pygame.draw.circle(surface, highlight_color, (int(highlight_point.x), int(highlight_point.y)), 4)
        # 绘制边框
        pygame.draw.polygon(surface, (255, 255, 255, 150), points, 2)

        ###pygame.draw.polygon(surface, (0, 210, 0), points)#绘制主角颜色

    def update(self, keys):
        # 更新玩家状态，参数keys是键盘按键状态字典
        if self.attack_cooldown > 0:#攻击冷却计时
            self.attack_cooldown -= 1

        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.speed# 计算水平移动量：D键向右，A键向左
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.speed# 计算垂直移动量：S键向下，W键向上

        if dx or dy:
            # 更新朝向为移动方向并标准化
            self.facing = pygame.Vector2(dx, dy).normalize()

        self.rect.x = max(0, min(self.rect.x + dx, 770))# 更新X坐标并限制在屏幕范围内(0-770)
        self.rect.y = max(0, min(self.rect.y + dy, 570))# 更新Y坐标并限制在屏幕范围内(0-570)

        #================受伤无敌帧===================
        # 更新无敌状态
        self.update_invincibility()
        # 更新闪烁效果
        self.update_blink_effect()

        #攻击道具作用效果
        if self.power_timer > 0:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.damage = self.base_damage# 恢复为基础攻击力

        #速度道具提升效果
        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed = self.base_speed

    #==========================受伤无敌帧====================
    def update_invincibility(self):
        """更新无敌状态"""
        current_time = pygame.time.get_ticks()

        # 检查无敌状态是否结束
        if self.invincible and current_time - self.invincible_start_time >= self.invincible_duration:
            self.invincible = False
            self.visible = True  # 确保结束时可见

    def update_blink_effect(self):
        """更新受伤害时的闪烁效果"""
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_blink_time >= self.blink_interval:
                self.visible = not self.visible
                self.last_blink_time = current_time

    def take_damage(self, damage, damage_type):
        """统一的受伤处理方法
        damage_type: "normal"-普通伤害, "melee"-近战伤害, "trap"-陷阱伤害, "bullet"-子弹伤害
        """
        current_time = pygame.time.get_ticks()  # 使用pygame的时间获取

        # 检查是否处于无敌状态
        if self.invincible:
            return False

        # 根据伤害类型设置不同的冷却时间
        cooldown_times = {
            "melee": 500,  # 0.5秒（近战伤害冷却较短）
            "trap": 500,  # 0.5秒（陷阱伤害冷却更短）
            "bullet": 200  # 0.2秒（子弹伤害冷却）
        }

        cooldown = cooldown_times.get(damage_type, 1000)

        # 检查是否在受伤冷却期内
        if current_time - self.last_hit_time < cooldown:
            return False

        # 应用伤害
        self.health = max(0, self.health - damage)
        self.last_hit_time = current_time

        # 开启无敌状态
        self.invincible = True
        self.invincible_start_time = current_time
        self.invincible_duration = 1000  # 1秒无敌时间

        return True

    # 近战攻击方法
    def melee_attack(self, enemies, attack_effects, traps):

        if self.attack_cooldown == 0:
            self.attack_cooldown = ATTACK_COOLDOWN_TIME
            attack_box = pygame.Rect(0, 0, 60, 60)# 创建攻击判定区域（60x60矩形）
            # 设置攻击区域中心位置
            attack_box.center = (
                self.rect.centerx + self.facing.x * self.attack_range,
                self.rect.centery + self.facing.y * self.attack_range
            )
            attack_effects.add(AttackEffect(attack_box))

            # 打敌人
            for enemy in enemies:
                if attack_box.colliderect(enemy.rect):
                    enemy.take_damage(self.damage)

            # 打刺球
            for trap in traps:
                if attack_box.colliderect(trap.rect):
                    trap.take_damage()

            # 打 Boss
            for boss in globals().get('bosses', []):
                if attack_box.colliderect(boss.rect):
                    boss.take_damage(self.damage)

    # 射击方法
    def shoot(self, bullets):
        if self.attack_cooldown == 0:
            self.attack_cooldown = ATTACK_COOLDOWN_TIME
            bullets.add(Bullet(self.rect.centerx, self.rect.centery, self.facing))# 创建子弹并添加到子弹组


# ============================================================
#                        血迹
# ============================================================
'''
class BloodStain(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 0, 0, 90), (15, 15), 15)
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 180

    def update(self):
        self.alpha -= 1
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)
'''


class BloodStain(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        size = 55  # 【血迹总大小】血迹绘制区域的最大宽度，越大血迹范围越大
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        center = size // 2  # 血迹中心点，用于对称扩散

        import random, math

        # ---------- 颜色 ----------
        deep_red = (110, 0, 0)      # 深血红：主血斑颜色
        mid_red = (150, 20, 20)     # 较亮血红：飞溅颜色层
        alpha_main = 160            # 【主血斑透明度】越高越不透明
        alpha_dots = 120            # 【飞溅透明度】越低越透明

        # ---------- 1) 中心主斑 ----------
        # random.randint(6, 10): 【主血斑大小范围】
        pygame.draw.circle(self.image, (*deep_red, alpha_main),
                           (center, center), random.randint(6, 10))

        # ---------- 2) 中型次级斑 ----------
        # random.randint(2, 3): 【次级血斑数量】
        for _ in range(random.randint(2, 3)):
            r = random.randint(5, 10)     # 【次级血斑大小】
            angle = random.uniform(0, 2 * math.pi)  # 随机方向
            dist = random.randint(8, 10)  # 【距离中心的扩散距离】

            ox = int(math.cos(angle) * dist)  # X 偏移
            oy = int(math.sin(angle) * dist)  # Y 偏移

            pygame.draw.circle(self.image, (*deep_red, alpha_main),
                               (center + ox, center + oy), r)

        # ---------- 3) 小飞溅点 ----------
        # random.randint(3, 4): 【小飞溅点数量】
        for _ in range(random.randint(3, 4)):
            r = random.randint(2, 4)      # 【飞溅点半径】
            angle = random.uniform(0, 2 * math.pi)
            dist = random.randint(10, 18)  # 【飞溅飞出的最大距离】

            ox = int(math.cos(angle) * dist)
            oy = int(math.sin(angle) * dist)

            pygame.draw.circle(self.image, (*mid_red, alpha_dots),
                               (center + ox, center + oy), r)

        # ---------- 淡出参数 ----------
        self.alpha = 200  # 【总透明度起始值】越大血迹越明显

    def update(self):
        self.alpha -= 1  # 【淡出速度】每帧减少多少透明度
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)



# ============================================================
#                        近战敌人
# ============================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 25, 25)# 敌人的碰撞矩形：25x25像素
        self.speed = ENEMY_SPEED# 移动速度（常量ENEMY_SPEED = 2）
        self.health = 40

    def update(self, player):
        # 计算敌人到玩家的方向向量
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(math.hypot(dx, dy), 0.1)

        # 预测下一步位置
        next_x = self.rect.x + self.speed * dx / dist
        next_y = self.rect.y + self.speed * dy / dist

        # 屏幕边界检测
        if next_x < 0:
            next_x = 0
            next_y = self.rect.y + self.speed * dy / dist
        elif next_x + self.rect.width > 800:
            next_x = 800 - self.rect.width
            next_y = self.rect.y + self.speed * dy / dist

        if next_y < 0:
            next_y = 0
            next_x = self.rect.x + self.speed * dx / dist
        elif next_y + self.rect.height > 600:
            next_y = 600 - self.rect.height
            next_x = self.rect.x + self.speed * dx / dist

        self.rect.x = next_x
        self.rect.y = next_y

    def take_damage(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            stains.add(BloodStain(self.rect.centerx, self.rect.centery))# 在死亡位置创建血迹
            # 增加得分
            global score, kills_melee
            score += SCORE_MELEE_ENEMY
            kills_melee += 1
            self.kill()


# ============================================================
#                        远程敌人（圆形）
# ============================================================
class RangedEnemy(pygame.sprite.Sprite):
    MAX_RANGE = 800 // 3  # 攻击最大距离
    MIN_RANGE = 100       # 过近时保持的最小距离

    def __init__(self, x, y):
        super().__init__()
        self.x = x  # 敌人的中心点x坐标
        self.y = y  # 敌人的中心点y坐标
        self.radius = 14  # 敌人的碰撞半径（用于圆形碰撞检测）
        self.speed = RANGED_ENEMY_SPEED  # 移动速度，使用远程敌人速度常量
        self.health = 30  # 生命值，比近战敌人少
        self.cooldown = random.randint(30, RANGED_SHOOT_COOLDOWN)  # 射击冷却时间，初始随机值避免同时射击
        self.rect = pygame.Rect(x - 14, y - 14, 28, 28)  # 碰撞矩形，以中心点为基础计算，大小28x28

    def update(self, player):
        px, py = player.rect.center
        dx = px - self.x
        dy = py - self.y
        dist = max(math.hypot(dx, dy), 0.1)

        # 如果玩家太远，靠近玩家
        if dist > self.MAX_RANGE:
            move_x = dx / dist * self.speed
            move_y = dy / dist * self.speed
        # 如果玩家太近，远离玩家
        elif dist < self.MIN_RANGE:
            move_x = -dx / dist * self.speed
            move_y = -dy / dist * self.speed
        # 在合理范围内保持原地
        else:
            move_x = 0
            move_y = 0

        # 边界检测
        next_x = self.x + move_x
        next_y = self.y + move_y
        if next_x - self.radius < 0:
            next_x = self.radius
        elif next_x + self.radius > 800:
            next_x = 800 - self.radius
        if next_y - self.radius < 0:
            next_y = self.radius
        elif next_y + self.radius > 600:
            next_y = 600 - self.radius

        self.x = next_x
        self.y = next_y
        self.rect.center = (self.x, self.y)

        # 射击逻辑
        self.cooldown -= 1
        if self.cooldown <= 0:
            dx = px - self.x
            dy = py - self.y
            d = math.hypot(dx, dy)
            if d > 0:
                dx /= d
                dy /= d
            enemy_bullets.add(EnemyBullet(self.x, self.y, pygame.Vector2(dx, dy)))
            self.cooldown = RANGED_SHOOT_COOLDOWN

        # 死亡处理
        if self.health <= 0:
            stains.add(BloodStain(self.x, self.y))
            # 增加得分
            global score, kills_ranged
            score += SCORE_RANGED_ENEMY
            kills_ranged += 1
            self.kill()

    def take_damage(self, dmg):
        self.health -= dmg

    def draw(self, screen):
        # 绘制阴影
        draw_shadow_circle(screen, (int(self.x), int(self.y)), self.radius)
        
        # 绘制主体（渐变圆形）
        draw_gradient_circle(screen, (int(self.x), int(self.y)), self.radius, 
                            (30, 80, 200), (60, 120, 255))
        
        # 绘制高光
        highlight_pos = (int(self.x - self.radius * 0.3), int(self.y - self.radius * 0.3))
        pygame.draw.circle(screen, (150, 200, 255), highlight_pos, self.radius // 3)
        
        # 绘制边框
        pygame.draw.circle(screen, (255, 255, 255, 150), (int(self.x), int(self.y)), self.radius, 2)


# ============================================================
#                   玩家子弹
# ============================================================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)# 创建带透明度的表面
        self.rect = self.image.get_rect(center=(x, y))# 设置子弹的矩形碰撞区域，中心点在(x,y)
        self.velocity = direction * BULLET_SPEED# 设置子弹速度向量 = 方向 * 子弹速度常量
        self.rotation = 0
    def draw(self, surface):
        """绘制美化的子弹"""
        center = self.rect.center
        # 绘制发光效果
        for r in range(8, 4, -1):
            alpha = int(100 * (1 - (8-r)/4))
            glow_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 0, alpha), (r, r), r)
            surface.blit(glow_surf, (center[0]-r, center[1]-r))
        # 绘制子弹主体（渐变色）
        draw_gradient_circle(surface, center, 4, (255, 255, 150), (255, 200, 0))
        # 绘制高光
        pygame.draw.circle(surface, (255, 255, 255), (center[0]-1, center[1]-1), 1)
    def update(self, enemies):
        # 根据速度向量更新子弹位置
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        if not (0 <= self.rect.x <= 800 and 0 <= self.rect.y <= 600):
            # 检查子弹是否超出屏幕边界
            self.kill()
        for enemy in enemies:
            # 检测子弹与敌人的碰撞
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(15)
                self.kill()
                return
        for trap in traps:
            # 检测子弹与陷阱的碰撞
            if self.rect.colliderect(trap.rect):
                trap.take_damage()
                self.kill()
                return

# ============================================================
#                   敌人子弹
# ============================================================
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = direction * (BULLET_SPEED * 0.8)  # 敌人子弹稍慢一些
        
    def draw(self, surface):
        """绘制敌人子弹"""
        center = self.rect.center
        # 绘制发光效果
        for r in range(6, 2, -1):
            alpha = int(80 * (1 - (6-r)/4))
            glow_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 100, 100, alpha), (r, r), r)
            surface.blit(glow_surf, (center[0]-r, center[1]-r))
        
        # 绘制子弹主体（渐变色）
        draw_gradient_circle(surface, center, 3, (255, 50, 50), (200, 0, 0))
        
        # 绘制高光
        pygame.draw.circle(surface, (255, 200, 200), (center[0]-1, center[1]-1), 1)
        
    def update(self):
        # 根据速度向量更新子弹位置
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        # 检查子弹是否超出屏幕边界
        if not (0 <= self.rect.x <= 800 and 0 <= self.rect.y <= 600):
            self.kill()

# ============================================================
#                        血迹
# ============================================================
'''
class BloodStain(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 0, 0, 90), (15, 15), 15)
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 180

    def update(self):
        self.alpha -= 1
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)
'''

# ============================================================
#                    刺球
# ============================================================
class SpikeTrap(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.warning_time = 60# 警告时间（帧数），在此期间陷阱不会造成伤害
        self.health = 2#需要2次攻击才能摧毁
        self.x = x
        self.y = y
        self.radius = 10#半径大小
        self.rect = pygame.Rect(x-10, y-10, 20, 20)# 碰撞矩形，以中心点为基础计算

    def update(self):
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        # 根据警告状态选择颜色
        if self.warning_time > 0:
            base_color = (255, 200, 0)
            spike_color = (200, 150, 0)
        else:
            base_color = (255, 50, 50)
            spike_color = (180, 30, 30)
        
        # 绘制阴影
        shadow_offset = 2
        pygame.draw.circle(screen, (0, 0, 0, 80), 
                          (self.x + shadow_offset, self.y + shadow_offset), self.radius)
        
        # 绘制主体（渐变圆形）
        draw_gradient_circle(screen, (self.x, self.y), self.radius, 
                            tuple(min(255, c + 30) for c in base_color), base_color)
        
        # 绘制6个方向的尖刺（每60度一个）
        for angle in (0, 60, 120, 180, 240, 300):
            rad = math.radians(angle)
            x1 = self.x + math.cos(rad) * 8
            y1 = self.y + math.sin(rad) * 8
            x2 = self.x + math.cos(rad) * 14
            y2 = self.y + math.sin(rad) * 14
            # 尖刺有渐变效果
            pygame.draw.line(screen, spike_color, (x1, y1), (x2, y2), 3)
            pygame.draw.line(screen, tuple(min(255, c + 50) for c in spike_color), 
                            (x1, y1), (int((x1+x2)/2), int((y1+y2)/2)), 2)
        
        # 绘制中心高光
        pygame.draw.circle(screen, tuple(min(255, c + 60) for c in base_color), 
                          (self.x - 2, self.y - 2), 3)
        
        # 绘制边框
        pygame.draw.circle(screen, (255, 255, 255, 150), (self.x, self.y), self.radius, 2)

        if self.warning_time > 0:
            self.warning_time -= 1

    def take_damage(self):
        self.health -= 1#需要2次攻击才能摧毁
        if self.health <= 0:
            # 增加得分
            global score, kills_trap
            score += SCORE_TRAP
            kills_trap += 1
            self.kill()


# ============================================================
#                   近战特效
# ============================================================
class AttackEffect(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.rect = rect
        self.timer = 15# 效果持续时间（帧数）
        self.max_timer = 15

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
    
    def draw(self, surface):
        """绘制美化的攻击特效"""
        if self.timer <= 0:
            return
        
        # 计算淡出效果
        alpha = int(200 * (self.timer / self.max_timer))
        center = self.rect.center
        
        # 绘制冲击波效果
        for i in range(3):
            radius = self.rect.width // 2 + (self.max_timer - self.timer) * 3 + i * 5
            alpha_layer = int(alpha * (1 - i * 0.3))
            if alpha_layer > 0:
                glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 255, 255, alpha_layer), (radius, radius), radius, 2)
                surface.blit(glow_surf, (center[0] - radius, center[1] - radius))
        
        # 绘制中心亮点
        center_radius = 8 - (self.max_timer - self.timer) * 0.5
        if center_radius > 0:
            pygame.draw.circle(surface, (255, 255, 200, alpha), center, int(center_radius))


# ============================================================
#                  道具
# ============================================================
class Pickup(pygame.sprite.Sprite):
    def __init__(self, x, y, color, effect):
        super().__init__()
        self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
        self.color = color
        self.effect = effect
        self.bob_offset = 0  # 用于上下浮动动画
        self.bob_speed = 0.1
        
    def update(self):
        """更新浮动动画"""
        self.bob_offset += self.bob_speed
        if self.bob_offset > math.pi * 2:
            self.bob_offset = 0
            
    def draw(self, surface):
        """绘制美化的道具"""
        center_x = self.rect.centerx
        center_y = self.rect.centery + int(math.sin(self.bob_offset) * 3)  # 上下浮动
        
        # 绘制阴影
        shadow_offset = 2
        pygame.draw.circle(surface, (0, 0, 0, 60), 
                          (center_x + shadow_offset, center_y + shadow_offset), 10)
        
        # 绘制发光效果
        for r in range(16, 10, -1):
            alpha = int(50 * (1 - (16-r)/6))
            glow_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha), (r, r), r)
            surface.blit(glow_surf, (center_x-r, center_y-r))
        
        # 绘制主体（渐变圆形）
        draw_gradient_circle(surface, (center_x, center_y), 10, 
                            tuple(min(255, c + 40) for c in self.color), self.color)
        
        # 绘制高光
        highlight_pos = (center_x - 3, center_y - 3)
        pygame.draw.circle(surface, tuple(min(255, c + 80) for c in self.color), 
                          highlight_pos, 3)
        
        # 绘制边框
        pygame.draw.circle(surface, (255, 255, 255, 200), (center_x, center_y), 10, 2)

    def apply(self, player):
        if self.effect == "heal":
            player.health = min(player.max_health, player.health + 20) # 治疗效果：恢复20点生命值，不超过最大生命值
        elif self.effect == "power":
            player.damage = player.base_damage + 10# 力量提升：增加10点攻击力，持续600帧（10秒）
            player.power_timer = 600
        elif self.effect == "speed":
            player.speed = player.base_speed * 1.3# 速度提升：增加30%移动速度，持续600帧（10秒）
            player.speed_timer = 600

        self.kill()


# ============================================================
#           敌人防止重叠（推开系统）
# ============================================================
def separate_enemies(enemies):
    enemy_list = list(enemies)
    for i in range(len(enemy_list)):
        for j in range(i+1, len(enemy_list)):
            e1 = enemy_list[i]
            e2 = enemy_list[j]
            if e1.rect.colliderect(e2.rect):
                dx = e1.rect.centerx - e2.rect.centerx
                dy = e1.rect.centery - e2.rect.centery
                dist = max(math.hypot(dx, dy), 0.1)
                push_x = dx / dist
                push_y = dy / dist
                e1.rect.x += push_x
                e1.rect.y += push_y
                e2.rect.x -= push_x
                e2.rect.y -= push_y

# ============================================================
#                  敌人遇到边界
# ============================================================

'''
def move_enemy(enemy_rect, vx, vy, screen_width, screen_height):
    # 移动敌人
    enemy_rect.x += vx
    enemy_rect.y += vy

    # 左右边界
    if enemy_rect.left < 0:
        enemy_rect.left = 0
        vx = 0  # 沿边滑动
    elif enemy_rect.right > screen_width:
        enemy_rect.right = screen_width
        vx = 0

    # 上下边界
    if enemy_rect.top < 0:
        enemy_rect.top = 0
        vy = 0
    elif enemy_rect.bottom > screen_height:
        enemy_rect.bottom = screen_height
        vy = 0

    return vx, vy
    
'''


# ============================================================
#                  波次逻辑
# ============================================================
def spawn_enemy_at(kind):
    # 在屏幕范围内随机生成敌人位置（避开边缘50像素）
    x = random.randint(50, 750)
    y = random.randint(50, 550)
    if kind == "melee":
        enemies.add(Enemy(x, y))
    else:
        enemies.add(RangedEnemy(x, y))
def spawn_pickup(pickups):
    # 在屏幕范围内随机生成道具位置
    x, y = random.randint(50, 750), random.randint(50, 550)
    item_type = random.choice(["heal", "power", "speed"])
    color = {"heal": (0, 255, 0), "power": (200, 55, 0), "speed": (0, 0, 255)}[item_type]
    pickups.add(Pickup(x, y, color, item_type))

def spawn_wave(wave):
    # 第一波特殊处理：只生成4个近战敌人
    global bosses
    # 如果是最后一波（Boss 波），生成 Boss 并返回
    # 使用全局常量 MAX_WAVES（若不存在则回退到 15）
    max_w = globals().get('MAX_WAVES', 15)
    if 'bosses' in globals() and wave == max_w:
        #enemies.empty()
        bosses.add(Boss(400, 150))
        return
    if wave == 1:
        for _ in range(4):
            spawn_enemy_at("melee")
        return
    # 后续波次：50%概率生成4个近战敌人，50%概率生成3近战+2远程
    if random.random() < 0.5:
        for _ in range(4):
            spawn_enemy_at("melee")
    else:
        for _ in range(3):
            spawn_enemy_at("melee")
        for _ in range(2):
            spawn_enemy_at("ranged")
    # 每3波生成一次陷阱
    if wave % 3 == 0:
        for _ in range(3):
            traps.add(SpikeTrap(random.randint(60, 740), random.randint(60, 540)))
            traps.add(SpikeTrap(random.randint(60, 740), random.randint(60, 540)))


# ============================================================
#                   教学界面
# ============================================================
def draw_animated_background(time_offset):
    """绘制动态渐变背景（与主菜单相同）"""
    for y in range(600):
        color_value = int(30 + 20 * math.sin(y / 100 + time_offset))
        pygame.draw.line(screen, (color_value, color_value + 10, color_value + 20), (0, y), (800, y))

def wait_for_enter():
    # 创建一个无限循环，等待玩家按下回车键
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        pygame.display.flip()# 更新屏幕显示（保持当前画面）
        clock.tick(60)# 控制帧率为60FPS


def tutorial_screen():
    time_offset = 0
    font = get_font(36)

    # ----------- ① 玩家介绍 -----------
    running = True
    while running:
        time_offset += 0.02
        draw_animated_background(time_offset)
        
        text = font.render("这是你：使用 W A S D 移动", True, (255, 255, 255))
        screen.blit(text, (50, 50))
        text1 = font.render("使用J 射击，K 近战攻击", True, (255, 255, 255))
        screen.blit(text1, (50, 100))
        
        # 画玩家图（美化版本）
        center = pygame.Vector2(200, 240)
        size = 25
        forward = pygame.Vector2(0, -1)
        right = pygame.Vector2(1, 0)
        points = [
            center + forward * size,
            center - forward * size * 0.5 + right * size * 0.7,
            center - forward * size * 0.5 - right * size * 0.7
        ]
        # 阴影
        shadow_points = [p + pygame.Vector2(3, 3) for p in points]
        pygame.draw.polygon(screen, (0, 0, 0, 100), shadow_points)
        # 主体
        pygame.draw.polygon(screen, (50, 200, 50), points)
        pygame.draw.polygon(screen, (100, 255, 100), points, 2)

        hint_font = get_font(20)
        hint_alpha = int(180 + 75 * math.sin(time_offset * 5))
        text2 = hint_font.render("按 ENTER 继续", True, (255, 255, 255))
        text2.set_alpha(hint_alpha)
        screen.blit(text2, (580, 540))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False
        
        pygame.display.flip()
        clock.tick(60)

    # ----------- ② 敌人介绍 -----------
    running = True
    while running:
        time_offset += 0.02
        draw_animated_background(time_offset)
        
        screen.blit(font.render("这是敌人：分为近战 和 远程", True, (255, 255, 255)), (60, 50))

        # 近战（美化版本）
        melee_rect = pygame.Rect(150, 200, 30, 30)
        draw_3d_cube(screen, melee_rect, (200, 50, 50))
        screen.blit(font.render("近战", True, (255, 255, 255)), (150, 240))

        # 远程（美化版本）
        draw_gradient_circle(screen, (350, 215), 15, (30, 80, 200), (60, 120, 255))
        pygame.draw.circle(screen, (255, 255, 255, 150), (350, 215), 15, 2)
        screen.blit(font.render("远程", True, (255, 255, 255)), (330, 240))

        hint_alpha = int(180 + 75 * math.sin(time_offset * 5))
        text2 = hint_font.render("按 ENTER 继续", True, (255, 255, 255))
        text2.set_alpha(hint_alpha)
        screen.blit(text2, (280, 540))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False
        
        pygame.display.flip()
        clock.tick(60)



    # ----------- ③ 道具介绍 -----------
    running = True
    while running:
        time_offset += 0.02
        draw_animated_background(time_offset)

        screen.blit(font.render("道具：", True, (255, 255, 255)), (60, 50))

        # 恢复道具（美化）
        heal_y = 200 + int(3 * math.sin(time_offset * 3))
        draw_gradient_circle(screen, (130, heal_y), 10, (50, 255, 50), (0, 200, 0))
        screen.blit(font.render("恢复道具", True, (255, 255, 255)), (150, 195))

        # 攻击提升（美化）
        power_y = 260 + int(3 * math.sin(time_offset * 3 + 1))
        draw_gradient_circle(screen, (130, power_y), 10, (255, 155, 55), (200, 55, 0))
        screen.blit(font.render("攻击提升", True, (255, 255, 255)), (150, 255))

        # 速度提升（美化）
        speed_y = 320 + int(3 * math.sin(time_offset * 3 + 2))
        draw_gradient_circle(screen, (130, speed_y), 10, (100, 150, 255), (0, 0, 200))
        screen.blit(font.render("速度提升", True, (255, 255, 255)), (150, 315))

        hint_alpha = int(180 + 75 * math.sin(time_offset * 5))
        text2 = hint_font.render("按 ENTER 继续", True, (255, 255, 255))
        text2.set_alpha(hint_alpha)
        screen.blit(text2, (280, 540))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False
        
        pygame.display.flip()
        clock.tick(60)


    # ----------- ④ 刺球介绍 -----------
    running = True
    while running:
        time_offset += 0.02
        draw_animated_background(time_offset)
        
        screen.blit(font.render("这是刺球：会伤害你，可被近战或子弹打掉", True, (255, 255, 255)), (60, 50))

        # 刺球示例（美化版本）
        x, y = 200, 220
        # 阴影
        pygame.draw.circle(screen, (0, 0, 0, 80), (x + 2, y + 2), 12)
        # 主体渐变
        draw_gradient_circle(screen, (x, y), 12, (255, 100, 100), (200, 30, 30))
        # 尖刺
        for angle in (0, 60, 120, 180, 240, 300):
            rad = math.radians(angle)
            x1 = x + math.cos(rad) * 9
            y1 = y + math.sin(rad) * 9
            x2 = x + math.cos(rad) * 15
            y2 = y + math.sin(rad) * 15
            pygame.draw.line(screen, (150, 20, 20), (x1, y1), (x2, y2), 3)
        # 高光
        pygame.draw.circle(screen, (255, 150, 150), (x - 2, y - 2), 4)
        # 边框
        pygame.draw.circle(screen, (255, 255, 255, 150), (x, y), 12, 2)

        hint_alpha = int(180 + 75 * math.sin(time_offset * 5))
        text2 = hint_font.render("按 ENTER 继续", True, (255, 255, 255))
        text2.set_alpha(hint_alpha)
        screen.blit(text2, (280, 540))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False
        
        pygame.display.flip()
        clock.tick(60)

    # ----------- ⑤ 得分规则说明 -----------
    running = True
    while running:
        time_offset += 0.02
        draw_animated_background(time_offset)
        
        # 标题
        title_font = get_font(40)
        title_text = title_font.render("得分规则", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(400, 60))
        # 发光效果
        for i in range(3):
            glow_alpha = int(60 - i * 20)
            glow_surf = title_font.render("得分规则", True, (255, 255, 200))
            glow_surf.set_alpha(glow_alpha)
            screen.blit(glow_surf, (title_rect.x + i, title_rect.y + i))
        screen.blit(title_text, title_rect)
        
        # 得分规则列表
        rules_font = get_font(28)
        score_font = get_font(32)
        
        y_start = 130
        line_height = 70
        
        # 近战敌人得分
        melee_rect = pygame.Rect(150, y_start, 30, 30)
        draw_3d_cube(screen, melee_rect, (200, 50, 50))
        melee_text = rules_font.render("击败近战敌人", True, (255, 255, 255))
        screen.blit(melee_text, (200, y_start + 5))
        score_text = score_font.render(f"= {SCORE_MELEE_ENEMY} 分", True, (255, 215, 0))
        screen.blit(score_text, (450, y_start + 2))
        
        # 远程敌人得分
        y_start += line_height
        draw_gradient_circle(screen, (165, y_start + 15), 15, (30, 80, 200), (60, 120, 255))
        pygame.draw.circle(screen, (255, 255, 255, 150), (165, y_start + 15), 15, 2)
        ranged_text = rules_font.render("击败远程敌人", True, (255, 255, 255))
        screen.blit(ranged_text, (200, y_start + 5))
        score_text = score_font.render(f"= {SCORE_RANGED_ENEMY} 分", True, (255, 215, 0))
        screen.blit(score_text, (450, y_start + 2))
        
        # 陷阱得分
        y_start += line_height
        x, y = 165, y_start + 15
        pygame.draw.circle(screen, (0, 0, 0, 80), (x + 2, y + 2), 12)
        draw_gradient_circle(screen, (x, y), 12, (255, 100, 100), (200, 30, 30))
        for angle in (0, 60, 120, 180, 240, 300):
            rad = math.radians(angle)
            x1 = x + math.cos(rad) * 9
            y1 = y + math.sin(rad) * 9
            x2 = x + math.cos(rad) * 15
            y2 = y + math.sin(rad) * 15
            pygame.draw.line(screen, (150, 20, 20), (x1, y1), (x2, y2), 3)
        trap_text = rules_font.render("摧毁陷阱", True, (255, 255, 255))
        screen.blit(trap_text, (200, y_start + 5))
        score_text = score_font.render(f"= {SCORE_TRAP} 分", True, (255, 215, 0))
        screen.blit(score_text, (450, y_start + 2))
        
        # 提示文字
        hint_alpha = int(180 + 75 * math.sin(time_offset * 5))
        text2 = hint_font.render("按 ENTER 开始游戏", True, (255, 255, 255))
        text2.set_alpha(hint_alpha)
        hint_rect = text2.get_rect(center=(400, 520))
        screen.blit(text2, hint_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False
        
        pygame.display.flip()
        clock.tick(60)


def countdown_before_start(seconds=3):
    clock = pygame.time.Clock()
    font = get_font(80)
    small_font = get_font(36)

    start_ticks = pygame.time.get_ticks()  # 获取初始时间
    current_number = seconds # 记录当前应该显示的数字

    running = True
    while running:
        screen.fill((227,227,227))  # 背景色
        draw_grid(screen) # 绘制网格背景
        elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000

        number_to_show = seconds - elapsed_seconds
        if number_to_show > 0:
            screen.blit(font.render(str(number_to_show), True, (255, 255, 255)), (400-40, 220))
            screen.blit(small_font.render("准备开始！", True, (255, 255, 255)), (300, 320))
        else:
            running = False  # 倒计时结束

        pygame.display.flip()
        clock.tick(60)  # 每秒刷新60帧


# ============================================================
#                   手势控制规则页
# ============================================================
def gesture_rules_screen():
    font_title = get_font(50)
    font_text = get_font(30)
    
    running = True
    time_offset = 0
    
    while running:
        time_offset += 0.02
        draw_animated_background(time_offset)
        
        # 标题
        title = font_title.render("手势模式规则说明", True, (255, 215, 0))
        screen.blit(title, (200, 50))
        
        # 右手说明
        y = 120
        screen.blit(font_text.render("右手控制移动：", True, (100, 255, 255)), (100, y))
        y += 40
        screen.blit(font_text.render("  向右移动：右手向右", True, (255, 255, 255)), (100, y))
        y += 40
        screen.blit(font_text.render("  向左移动：右手向左", True, (255, 255, 255)), (100, y))
        y += 40
        screen.blit(font_text.render("  向上移动：右手向上", True, (255, 255, 255)), (100, y))
        y += 40
        screen.blit(font_text.render("  向下移动：右手向下", True, (255, 255, 255)), (100, y))
        
        # 左手说明
        y += 60
        screen.blit(font_text.render("左手控制攻击：", True, (255, 100, 100)), (100, y))
        y += 40
        screen.blit(font_text.render("  左手未出现在屏幕中：近战攻击", True, (255, 255, 255)), (100, y))
        y += 40
        screen.blit(font_text.render("  左手出现在屏幕中：远程射击", True, (255, 255, 255)), (100, y))
        
        # 继续提示
        hint_alpha = int(180 + 75 * math.sin(time_offset * 5))
        hint_surf = font_text.render("按 ENTER 继续", True, (255, 255, 255))
        hint_surf.set_alpha(hint_alpha)
        screen.blit(hint_surf, (300, 520))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False
                
        pygame.display.flip()
        clock.tick(60)

# ============================================================
#                   控制方式选择页
# ============================================================
def control_selection_screen():
    font_title = get_font(50)
    font_option = get_font(40)
    font_hint = get_font(24)
    
    selected = 0 # 0: Keyboard, 1: Gesture
    running = True
    time_offset = 0
    
    while running:
        time_offset += 0.02
        draw_animated_background(time_offset)
        
        # 标题
        title = font_title.render("选择控制方式", True, (255, 215, 0))
        screen.blit(title, (250, 80))
        
        # 选项
        color0 = (255, 255, 0) if selected == 0 else (200, 200, 200)
        color1 = (255, 255, 0) if selected == 1 else (200, 200, 200)
        
        opt0 = font_option.render("1. 键盘控制 (Keyboard)", True, color0)
        opt1 = font_option.render("2. 摄像头手势控制 (Camera)", True, color1)
        
        screen.blit(opt0, (180, 220))
        screen.blit(opt1, (180, 300))
        
        # 箭头指示
        if selected == 0:
            screen.blit(font_option.render("->", True, (255, 255, 0)), (130, 220))
        else:
            screen.blit(font_option.render("->", True, (255, 255, 0)), (130, 300))
            
        # 提示
        hint = font_hint.render("使用 W/S 或 上/下 键选择，按 ENTER 确认", True, (255, 255, 255))
        screen.blit(hint, (200, 450))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "gesture" if selected == 1 else "keyboard"
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    selected = 0
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    selected = 1
                if event.key == pygame.K_1:
                    selected = 0
                if event.key == pygame.K_2:
                    selected = 1
                    
        pygame.display.flip()
        clock.tick(60)

# ============================================================
#                   主菜单
# ============================================================
def main_menu():
    font = get_font(72)
    font2 = get_font(28)
    
    # 背景动画变量
    time_offset = 0

    running = True
    while running:
        time_offset += 0.02
        # 绘制渐变背景
        for y in range(600):
            color_value = int(30 + 20 * math.sin(y / 100 + time_offset))
            pygame.draw.line(screen, (color_value, color_value + 10, color_value + 20), (0, y), (800, y))
        
        # 绘制标题（带阴影和发光效果）
        title_text = font.render("Tiny Heroes", True, (255, 255, 255))
        title_shadow = font.render("Tiny Heroes", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(400, 220))
        
        # 发光效果
        for i in range(3):
            glow_alpha = int(50 - i * 15)
            glow_surf = font.render("Tiny Heroes", True, (150, 200, 255))
            glow_surf.set_alpha(glow_alpha)
            screen.blit(glow_surf, (title_rect.x + i, title_rect.y + i))
        
        # 阴影
        screen.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        # 主文字
        screen.blit(title_text, title_rect)
        
        # 提示文字（闪烁效果）
        hint_alpha = int(180 + 75 * math.sin(time_offset * 5))
        hint_surf = font2.render("按下 ENTER 开始游戏", True, (255, 255, 255))
        hint_surf.set_alpha(hint_alpha)
        hint_rect = hint_surf.get_rect(center=(400, 380))
        screen.blit(hint_surf, hint_rect)
        
        # 装饰性元素
        for i in range(5):
            x = 100 + i * 150
            y = 500 + int(20 * math.sin(time_offset * 3 + i))
            draw_gradient_circle(screen, (x, y), 8, (100, 150, 200), (50, 100, 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        pygame.display.flip()
        clock.tick(60)

# ============================================================
#                   手势按键包装器
# ============================================================
class GestureKeyWrapper:
    def __init__(self, actions, real_keys):
        self.actions = actions
        self.real_keys = real_keys
    
    def __getitem__(self, key):
        # 优先响应手势，同时也支持键盘混合操作
        if key == pygame.K_d: return self.actions.get("move_right", False) or self.real_keys[key]
        if key == pygame.K_a: return self.actions.get("move_left", False) or self.real_keys[key]
        if key == pygame.K_w: return self.actions.get("move_up", False) or self.real_keys[key]
        if key == pygame.K_s: return self.actions.get("move_down", False) or self.real_keys[key]
        return self.real_keys[key]

# ============================================================
#                 游戏主循环
# ============================================================
def main():
    # 导入手势控制器
    try:
        from gesture_control import GestureController
    except ImportError:
        print("Warning: gesture_control module not found or dependencies missing.")
        GestureController = None

    main_menu()
    tutorial_screen()
    
    # 将手势规则和选择放到教程之后
    gesture_rules_screen()
    control_mode = control_selection_screen()
    
    gesture_controller = None
    if control_mode == "gesture":
        if GestureController:
            print("Initializing Gesture Controller...")
            gesture_controller = GestureController()
            if not gesture_controller.cap.isOpened():
                 print("Error: Camera could not be opened.")
                 gesture_controller = None
        else:
            print("Error: Cannot start gesture mode because module is missing.")
            control_mode = "keyboard"

    countdown_before_start(3)

    #===========================================================
    last_melee_damage_time = 0  # 近战伤害上次触发时间
    last_trap_damage_time = 0  # 陷阱伤害上次触发时间
    melee_damage_interval = 500  # 近战伤害间隔0.5秒
    trap_damage_interval = 300  # 陷阱伤害间隔0.3秒

    global stains, enemy_bullets, traps, enemies
    global bosses, boss_bullets
    player = Player()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    stains = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    bosses = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    traps = pygame.sprite.Group()
    pickups = pygame.sprite.Group()
    attack_effects = pygame.sprite.Group()

    if not gesture_controller:
        wave = 1
        max_waves = 15
        wave_timer = 0
        wave_interval = 15 * 60  # 15秒
        spawn_wave(wave)
    else:
        wave = 1
        max_waves = 5
        wave_timer = 0
        wave_interval = 15 * 60  # 15秒
        spawn_wave(wave)

    game_time = 0
    item_timer = 0

    running = True
    game_over = False
    font = get_font(36)

    victory = False  # 新增标志
    
    # ===================== 得分系统初始化 =====================
    global score, kills_melee, kills_ranged, kills_trap
    score = 0
    kills_melee = 0
    kills_ranged = 0
    kills_trap = 0

    gesture_actions = {}
    gesture_img = None
    last_gesture_shoot = False
    last_gesture_melee = False
    last_auto_shoot_time = 0  # 用于跟踪自动射击的时间

    while running:
        # 获取手势输入
        if gesture_controller:
            raw_img, gesture_actions = gesture_controller.process_frame()
            if raw_img is not None:
                gesture_img = gesture_controller.get_pygame_image(raw_img)
                # 调试：如果图像转换失败，打印错误
                if gesture_img is None and raw_img is not None:
                    print("Warning: Failed to convert camera image to pygame surface")

        # 处理所有游戏事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # ESC键退出游戏
                if event.key == pygame.K_ESCAPE:
                    running = False
                # 游戏结束时按R键重新开始
                if game_over and event.key == pygame.K_r:
                    if gesture_controller:
                        gesture_controller.release()
                    return main()
                # 游戏进行中的按键处理
                if not game_over:
                    # K键近战攻击 (键盘)
                    if event.key == pygame.K_k:
                        player.melee_attack(enemies, attack_effects, traps)
                    # J键射击 (键盘)
                    if event.key == pygame.K_j:
                        player.shoot(bullets)

        # 游戏进行中的逻辑更新
        if not game_over:
            # 手势攻击触发
            if gesture_controller:
                current_shoot = gesture_actions.get("shoot", False)
                current_melee = gesture_actions.get("melee", False)
                
                # 处理远程攻击（左手出现时）
                if current_shoot and not last_gesture_shoot:
                    player.shoot(bullets)
                
                # 处理近战攻击（状态变化时触发）
                if current_melee and not last_gesture_melee:
                    player.melee_attack(enemies, attack_effects, traps)
                
                # 处理自动射击（左手不出现时，每隔0.2秒射击一次）
                if current_melee:  # 当处于近战状态（左手不出现）时
                    current_time = pygame.time.get_ticks()
                    if current_time - last_auto_shoot_time > 200:  # 200毫秒 = 0.2秒
                        player.shoot(bullets)
                        last_auto_shoot_time = current_time
                
                last_gesture_shoot = current_shoot
                last_gesture_melee = current_melee

            game_time += 1
            wave_timer += 1
            item_timer += 1

            if wave_timer >= wave_interval and wave < max_waves:
                wave += 1
                wave_timer = 0
                spawn_wave(wave)

            if item_timer >= ITEM_SPAWN_TIME:
                spawn_pickup(pickups)
                item_timer = 0

            real_keys = pygame.key.get_pressed()
            keys = GestureKeyWrapper(gesture_actions, real_keys)
            player.update(keys)

            enemies.update(player)
            bullets.update(enemies)
            for b in list(bullets):
                for boss in list(bosses):
                    if b.rect.colliderect(boss.rect):
                        boss.take_damage(15)
                        b.kill()
                        break
            stains.update()
            enemy_bullets.update()
            boss_bullets.update()
            for boss in list(bosses):
                new_b = boss.update(player)
                if new_b is not None:
                    boss_bullets.add(new_b)
            attack_effects.update()
            for trap in traps:
                trap.update()

            separate_enemies(enemies)

            '''# 玩家碰撞伤害检测
            for enemy in pygame.sprite.spritecollide(player, enemies, False):
                player.health -= 0.4  # 近战敌人持续伤害

            for b in pygame.sprite.spritecollide(player, enemy_bullets, True):
                player.health -= 5  # 敌人子弹单次伤害

            for trap in pygame.sprite.spritecollide(player, traps, False):
                if trap.warning_time <= 0:  # 只有激活的陷阱才造成伤害
                    player.health -= 0.5  # 陷阱持续伤害
            '''

            # ================= 玩家碰撞伤害检测 =================
            current_time = pygame.time.get_ticks()

            # 近战敌人伤害（间隔触发）
            if current_time - last_melee_damage_time >= melee_damage_interval:
                for enemy in pygame.sprite.spritecollide(player, enemies, False):
                    if player.take_damage(5, "melee"):
                        last_melee_damage_time = current_time
                        break  # 一次只触发一个敌人的伤害

            # Boss 的近战接触伤害（间隔触发）
            if current_time - last_melee_damage_time >= melee_damage_interval:
                for boss in list(bosses):
                    if player.rect.colliderect(boss.rect):
                        if player.take_damage(getattr(boss, 'melee_damage', 10), "melee"):
                            last_melee_damage_time = current_time
                            break

            # 敌人子弹伤害（单次触发）
            for bullet in pygame.sprite.spritecollide(player, enemy_bullets, True):
                player.take_damage(5, "bullet")

            # Boss 子弹伤害
            for bullet in pygame.sprite.spritecollide(player, boss_bullets, True):
                player.take_damage(8, "bullet")

            # 陷阱伤害（间隔触发）
            if current_time - last_trap_damage_time >= trap_damage_interval:
                for trap in pygame.sprite.spritecollide(player, traps, False):
                    if trap.warning_time <= 0 and player.take_damage(5, "trap"):
                        last_trap_damage_time = current_time
                        break  # 一次只触发一个陷阱的伤害

            # 道具拾取检测
            for pickup in pygame.sprite.spritecollide(player, pickups, False):
                pickup.apply(player)  # 应用道具效果

            # 统计 Boss 是否在本帧开始时存在，用于在 Boss 死亡时给予分数和血迹
            #（取第一个引用，以便在其 kill() 后仍能获取位置）
            boss_ref = next(iter(bosses), None)

            # 游戏胜利/失败条件判断
            remaining_enemies = len(enemies) + len(globals().get('bosses', []))
            # 胜利条件：到达最大波次且所有敌人都被消灭
            if wave == max_waves and remaining_enemies == 0:
                game_over = True
                victory = True
            # 失败条件：玩家生命值耗尽
            elif player.health <= 0:
                game_over = True
                victory = False

        # 绘制
        draw_grid(screen)  # 网格函数内部已经填充背景

        # 绘制血迹效果（使用精灵组的批量绘制方法）
        stains.draw(screen)
        
        # 绘制攻击特效
        for effect in attack_effects:
            effect.draw(screen)

        # 遍历所有敌人并分别绘制
        for enemy in enemies:
            # 远程敌人有自定义的绘制方法
            if isinstance(enemy, RangedEnemy):
                enemy.draw(screen)
            else:
                # 近战敌人：3D立方体效果
                draw_3d_cube(screen, enemy.rect, (200, 50, 50))
                # 添加高光点
                highlight_x = enemy.rect.x + enemy.rect.width // 4
                highlight_y = enemy.rect.y + enemy.rect.height // 4
                pygame.draw.circle(screen, (255, 150, 150), (highlight_x, highlight_y), 3)

        # 绘制 Boss（如果存在）
        for boss in list(bosses):
            boss.draw(screen)

        # 绘制 Boss 的子弹
        for bb in list(boss_bullets):
            if hasattr(bb, 'draw'):
                bb.draw(screen)

        # 绘制所有陷阱
        for trap in traps:
            trap.draw(screen)

        # 绘制玩家发射的子弹（需要单独遍历因为可能有自定义逻辑）
        for bullet in bullets:
            bullet.draw(screen)

        # 绘制敌人发射的子弹（需要自定义绘制）
        for bullet in enemy_bullets:
            bullet.draw(screen)

        # 绘制所有道具（需要自定义绘制和更新）
        for pickup in pickups:
            pickup.update()
            pickup.draw(screen)

        # 最后绘制玩家，确保玩家在最上层
        player.draw(screen)

        # 绘制摄像头画面（如果开启手势控制）
        if gesture_controller:
            # 即使 gesture_img 为 None 也绘制一个占位框，提示正在获取画面
            cam_w, cam_h = 240, 180
            cam_x = 800 - cam_w - 10
            cam_y = 10
            
            # 绘制边框和背景
            pygame.draw.rect(screen, (0, 0, 0), (cam_x-2, cam_y-2, cam_w+4, cam_h+4))
            pygame.draw.rect(screen, (20, 20, 20), (cam_x, cam_y, cam_w, cam_h))
            
            if gesture_img:
                try:
                    # 缩放画面
                    scaled_img = pygame.transform.scale(gesture_img, (cam_w, cam_h))
                    screen.blit(scaled_img, (cam_x, cam_y))
                except Exception as e:
                    # 如果缩放失败，显示错误信息
                    error_font = get_font(16)
                    error_text = error_font.render("Image Error", True, (255, 0, 0))
                    screen.blit(error_text, (cam_x + 70, cam_y + 80))
            else:
                # 显示加载中文字
                loading_font = get_font(20)
                loading_text = loading_font.render("Camera Loading...", True, (255, 255, 255))
                text_rect = loading_text.get_rect(center=(cam_x + cam_w//2, cam_y + cam_h//2))
                screen.blit(loading_text, text_rect)

            pygame.draw.rect(screen, (255, 255, 255), (cam_x, cam_y, cam_w, cam_h), 2)
            
            # 绘制详细的手势识别信息
            info_font = get_font(16)
            info_y = cam_y + cam_h + 5
            
            # 1. 画面中的手
            hands_text = "画面中的手: " + (" ".join(gesture_controller.detected_hands) if gesture_controller.detected_hands else "无")
            hands_surf = info_font.render(hands_text, True, (255, 255, 255))
            screen.blit(hands_surf, (cam_x + 5, info_y))
            info_y += 20
            
            # 2. 左手攻击状态（黄色）
            left_attack_text = f"左手攻击: {gesture_controller.left_hand_attack}"
            left_attack_surf = info_font.render(left_attack_text, True, (0, 255, 255))
            screen.blit(left_attack_surf, (cam_x + 5, info_y))
            info_y += 20
            
            # 3. 右手运动方向（蓝色）
            right_movement_text = f"右手运动: {gesture_controller.right_hand_movement if gesture_controller.right_hand_movement else '无'}"
            right_movement_surf = info_font.render(right_movement_text, True, (255, 150, 50))
            screen.blit(right_movement_surf, (cam_x + 5, info_y))

        # 显示剩余敌人数量
        #screen.blit(font.render(f"敌人剩余: {remaining_enemies}", True, (0, 0, 0)), (10, 130))
        '''
        # 绘制现代化UI面板
        ui_panel_rect = pygame.Rect(10, 10, 200, 190)
        # 绘制半透明背景
        ui_bg = pygame.Surface((200, 190), pygame.SRCALPHA)
        ui_bg.fill((20, 20, 30, 220))
        screen.blit(ui_bg, (10, 10))
        # 绘制边框
        pygame.draw.rect(screen, (255, 255, 255, 100), ui_panel_rect, 2, border_radius=8)
        '''
        # 绘制血条
        ui_font = get_font(24)
        #screen.blit(ui_font.render("生命值", True, (255, 255, 255)), (20, 15))
        draw_health_bar(screen, 20, 15, 110, 20, player.health, player.max_health, 
                       bg_color=(50, 20, 20), fill_color=(0, 255, 100))
        screen.blit(get_font(18).render(f"{int(player.health)}/{player.max_health}", True, (255, 255, 255)), (135, 17))
        
        # 绘制波次信息
        screen.blit(ui_font.render(f"波次: {wave}/{max_waves}", True, (255, 255, 255)), (20, 45))
        
        # 绘制时间信息
        screen.blit(ui_font.render(f"时间: {game_time // 60}s", True, (255, 255, 255)), (20, 75))
        
        # 绘制得分信息（金色高亮）
        score_font = get_font(24)
        screen.blit(score_font.render(f"得分: {score}", True, (255, 215, 0)), (20, 105))
        
        # 绘制道具效果指示（放在UI面板下方）
        effect_y_start = 210
        if player.power_timer > 0:
            effect_font = get_font(16)
            alpha = int(200 + 55 * math.sin(pygame.time.get_ticks() / 200))
            effect_surf = effect_font.render(f"⚔ 攻击提升 {player.power_timer // 60}s", True, (255, 215, 0))
            effect_surf.set_alpha(alpha)
            screen.blit(effect_surf, (20, effect_y_start))
            effect_y_start += 25
        
        if player.speed_timer > 0:
            effect_font = get_font(16)
            alpha = int(200 + 55 * math.sin(pygame.time.get_ticks() / 200))
            effect_surf = effect_font.render(f"⚡ 速度提升 {player.speed_timer // 60}s", True, (100, 200, 255))
            effect_surf.set_alpha(alpha)
            screen.blit(effect_surf, (20, effect_y_start))

        # 游戏结束/胜利显示（美化版本，包含得分统计）
        if game_over:
            # 绘制半透明遮罩
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))
            
            # 绘制得分统计面板
            stats_panel = pygame.Rect(200, 100, 400, 400)
            stats_bg = pygame.Surface((400, 400), pygame.SRCALPHA)
            stats_bg.fill((30, 35, 45, 240))
            screen.blit(stats_bg, (200, 100))
            pygame.draw.rect(screen, (255, 255, 255, 150), stats_panel, 3, border_radius=10)
            
            y_offset = 130
            
            if victory:
                # 胜利消息
                victory_font = get_font(44)
                text = victory_font.render("游戏胜利！", True, (100, 255, 100))
                text_rect = text.get_rect(center=(400, y_offset))
                shadow_surf = victory_font.render("游戏胜利！", True, (0, 0, 0))
                screen.blit(shadow_surf, (text_rect.x + 3, text_rect.y + 3))
                screen.blit(text, text_rect)
                y_offset += 50
            else:
                # 失败消息
                defeat_font = get_font(44)
                text = defeat_font.render("游戏结束", True, (255, 100, 100))
                text_rect = text.get_rect(center=(400, y_offset))
                shadow_surf = defeat_font.render("游戏结束", True, (0, 0, 0))
                screen.blit(shadow_surf, (text_rect.x + 3, text_rect.y + 3))
                screen.blit(text, text_rect)
                y_offset += 50
            
            # 显示总分
            total_score_font = get_font(36)
            total_score_text = total_score_font.render(f"总分: {score}", True, (255, 215, 0))
            total_score_rect = total_score_text.get_rect(center=(400, y_offset))
            screen.blit(total_score_text, total_score_rect)
            y_offset += 60
            
            # 显示详细统计
            stats_font = get_font(24)
            stats_items = [
                (f"近战敌人: {kills_melee} × {SCORE_MELEE_ENEMY} = {kills_melee * SCORE_MELEE_ENEMY}", (255, 150, 150)),
                (f"远程敌人: {kills_ranged} × {SCORE_RANGED_ENEMY} = {kills_ranged * SCORE_RANGED_ENEMY}", (150, 150, 255)),
                (f"陷阱: {kills_trap} × {SCORE_TRAP} = {kills_trap * SCORE_TRAP}", (255, 200, 100)),
            ]
            
            for stat_text, stat_color in stats_items:
                text_surf = stats_font.render(stat_text, True, stat_color)
                text_rect = text_surf.get_rect(center=(400, y_offset))
                screen.blit(text_surf, text_rect)
                y_offset += 35
            
            # 提示文字
            hint_font = get_font(24)
            hint_text = hint_font.render("按 R 重新开始", True, (255, 255, 255))
            hint_rect = hint_text.get_rect(center=(400, y_offset + 40))
            hint_alpha = int(180 + 75 * math.sin(pygame.time.get_ticks() / 300))
            hint_surf = hint_font.render("按 R 重新开始", True, (255, 255, 255))
            hint_surf.set_alpha(hint_alpha)
            screen.blit(hint_surf, hint_rect)

        # 在这一帧更新结束后，检测 Boss 是否刚刚死亡，给予奖励分数和血迹
        try:
            if 'boss_ref' in locals() and boss_ref is not None and not boss_ref.alive():
                stains.add(BloodStain(boss_ref.rect.centerx, boss_ref.rect.centery))
                score += BOSS_SCORE
                for bb in list(globals().get('boss_bullets', [])):
                    bb.kill()
                boss_ref = None
        except Exception:
            pass

        pygame.display.flip()
        clock.tick(60)

    if gesture_controller:
        gesture_controller.release()
    pygame.quit()


# 绘制网格（美化版本）
def draw_grid(surface):
    # 深色背景
    surface.fill((35, 40, 50))
    
    # 绘制网格线（更柔和）
    for x in range(0, 801, 50):
        pygame.draw.line(surface, (60, 65, 75, 100), (x, 0), (x, 600), 1)
    for y in range(0, 601, 50):
        pygame.draw.line(surface, (60, 65, 75, 100), (0, y), (800, y), 1)
    
    # 绘制主要网格线（更明显）
    for x in range(0, 801, 200):
        pygame.draw.line(surface, (80, 85, 95, 150), (x, 0), (x, 600), 2)
    for y in range(0, 601, 200):
        pygame.draw.line(surface, (80, 85, 95, 150), (0, y), (800, y), 2)


if __name__ == "__main__":
    main()


'''
以下是顺序目录
1.中文字体兼容24-32
2.美化辅助函数32-87
3，绘制血条88-109
4.速度冷却常量、得分常量201-223
5.玩家类227-417
    其中：255-297玩家图形，298-330更新状态，331-381受伤无敌帧与减血，384-417近战攻击与远程攻击触发方式
6.血迹422-480
7.近战敌人486-529
    其中：503-516屏幕边界检测
8.远程敌人535-621
    其中边界检测568-582
9.玩家子弹627-665
10.敌人子弹670-699
11.刺球703-767
12.近战特效772-805
13.道具811-866
14.敌人防止重叠871-886
15.波次逻辑922-964
16.教学界面970-1247，手势控制规则页1252-1301，控制方式选择1305-1358
17.主菜单1363-1416
18.手势按键包装器1420-1431
19.游戏主循环1436-1900+

以下是类别目录
1.美化设计
    中文字体兼容24-32
    美化辅助函数32-87
    绘制血条88-109
    血迹422-480
    近战特效772-805
2.主菜单与教程界面
    教学界面970-1247，手势控制规则页1252-1301，控制方式选择1305-1358
    主菜单1363-1416
3.主循环
    游戏主循环1436-1900+
4.玩家（含道具）
    速度冷却常量、得分常量201-223
    玩家类227-417
        其中：255-297玩家图形，298-330更新状态，331-381受伤无敌帧与减血，384-417近战攻击与远程攻击触发方式
    玩家子弹627-665
    道具811-866
5.敌人（含刺球）
    速度冷却常量、得分常量201-223
    近战敌人486-529,其中,屏幕边界检测503-516
    远程敌人535-621,其中,边界检测568-582
    敌人子弹670-699
    刺球703-767
    敌人防止重叠871-886
7.机制
    波次逻辑922-964
8.手势相关
    手势按键包装器1420-1431
'''