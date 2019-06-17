import pygame
import time
import sys
import random
from pygame.locals import *


class PlayerClass(pygame.sprite.Sprite):  # 玩家类
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.img_ori = "player.png"
        self.img = pygame.image.load(self.img_ori).convert_alpha()
        self.rect = self.img.get_rect()
        self.center_init = [24*9+12, 24*13+12]
        self.rect.center = self.center_init
        self.speed = 4  # 移动速度
        self.lifes = 3  # 生命数
        self.isMove = True  # 记录玩家按键是否成功（为了保证操作的流畅）
        self.direction = [0, 0]  # 玩家按键对应的移动方向
        self.direction_old = [0, -1]  # 上一步移动方向

    def move(self, wallGroup, direction):  # 移动
        self.isMove = True
        # 玩家位置改变
        self.rect.centerx += self.speed*direction[0]
        self.rect.centery += self.speed*direction[1]
        # 如果与墙碰撞到一起，则玩家位置不改变，记录玩家按键不成功
        if pygame.sprite.spritecollide(self, wallGroup, False):
            self.rect.centerx -= self.speed*direction[0]
            self.rect.centery -= self.speed*direction[1]
            self.isMove = False

    def reset(self):  # 重置
        self.rect.center = self.center_init
        self.isMove = True
        self.direction = [0, 0]
        self.direction_old = [0, -1]


class BeanClass(pygame.sprite.Sprite):  # 豆子类
    def __init__(self, isBigger):
        pygame.sprite.Sprite.__init__(self)
        self.img_ori = ["bean1.png", "bean2.png"]
        self.isBigger = isBigger
        # 大豆子
        if isBigger:
            self.img = pygame.image.load(self.img_ori[1]).convert_alpha()
            self.rect = self.img.get_rect()
        # 小豆子
        else:
            self.img = pygame.image.load(self.img_ori[0]).convert_alpha()
            self.rect = self.img.get_rect()


class WallClass(pygame.sprite.Sprite):  # 墙体类
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.img_ori = "wall.png"
        self.img = pygame.image.load(self.img_ori).convert_alpha()
        self.rect = self.img.get_rect()


class EnermyClass(pygame.sprite.Sprite):  # 怪物类
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.img_ori = ["enermy1.png", "enermy2.png", "enermy3.png"]
        self.img = pygame.image.load(self.img_ori[0]).convert_alpha()
        self.rect = self.img.get_rect()
        self.weak_time = 0  # 剩余虚弱的时间
        self.being = True  # 是否活着
        self.speed = 3  # 速度
        self.center_init = [24*9+12, 24*9+12]  # 初始中心位置
        self.rect.center = self.center_init
        self.direction = (0, -1)  # 当移动的方向
        self.dir_can_move_old = ()  # 记录上一步可以移动的方向
        self.dir_changed = False  # 记录上一步是否改变了方向

    def be_eaten(self):  # 被吃掉
        self.being = False
        self.weak_time = 0
        self.img = pygame.image.load(self.img_ori[2]).convert_alpha()

    def reset(self):  # 重置
        self.rect.center = self.center_init
        self.being = True
        self.dir_changed = False
        self.direction = (0, -1)
        self.img = pygame.image.load(self.img_ori[0]).convert_alpha()

    def move(self, player, wallGroup):  # 移动
        # 判断能移动的方向
        dir_can_move = set()  # 能移动的方向
        for direction in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            self.rect.centerx += self.speed*direction[0]
            self.rect.centery += self.speed*direction[1]
            if not pygame.sprite.spritecollide(self, wallGroup, False):
                dir_can_move.add(direction)
            self.rect.centerx -= self.speed*direction[0]
            self.rect.centery -= self.speed*direction[1]
        # 如果能移动的方向和上一步能移动的方向相同，或者上一步刚变了方向，则保持方向不变
        if dir_can_move == self.dir_can_move_old or self.dir_changed == True:
            self.rect.centerx += self.speed*self.direction[0]
            self.rect.centery += self.speed*self.direction[1]
            self.dir_can_move_old = dir_can_move
            self.dir_changed = False
            return
        else:
            self.dir_can_move_old = dir_can_move

        prob_follow_player = 0.75  # 追踪玩家的概率
        # 在存活状态下，如果随机数大于追踪玩家的概率，或处于虚弱状态，则不追踪
        if self.being and (random.random() > prob_follow_player or self.weak_time > 0):
            # 如果有多个可移动的方向，且上一步的反方向在其中，则移除上一步的反方向
            if len(dir_can_move) > 1 and (self.direction[0]*-1, self.direction[1]*-1) in dir_can_move:
                dir_can_move.remove(
                    (self.direction[0]*-1, self.direction[1]*-1))
            # 在可移动的方向中随机选择一个方向作为当前移动方向
            self.direction = random.choice(list(dir_can_move))
            self.dir_changed = True
        # 否则，追踪目标
        else:
            # 目标的中心坐标（如果存活，追踪玩家；如果被吃掉，追踪初始位置）
            target_pos = player.rect.center if self.being else self.center_init
            dir_to_target = set()  # 面向目标的方向
            dir_to_target_can_move = set()  # 面向目标的方向中可以移动的方向
            if target_pos[0]-self.rect.centerx > 0:
                dir_to_target.add((1, 0))
            elif target_pos[0]-self.rect.centerx < 0:
                dir_to_target.add((-1, 0))
            if target_pos[1]-self.rect.centery > 0:
                dir_to_target.add((0, 1))
            elif target_pos[1]-self.rect.centery < 0:
                dir_to_target.add((0, -1))
            elif not self.being:  # 被吃掉状态下，如果y与初始y值相同，增加朝向上方的方向
                dir_to_target.add((0, -1))
            # 朝向目标的方向与能移动的方向的交集
            dir_to_target_can_move = dir_to_target & dir_can_move
            # 如果在面向目标的方向中存在可以移动的方向
            if dir_to_target_can_move:
                # 如果这些方向大于1，且前一步的反方向在其中，则将其移除（确保怪物不来回移动）
                if len(dir_to_target_can_move) > 1 and (self.direction[0]*-1, self.direction[1]*-1) in dir_to_target_can_move:
                    dir_to_target_can_move.remove(
                        (self.direction[0]*-1, self.direction[1]*-1))
                self.direction = random.choice(list(dir_to_target_can_move))
                self.dir_changed = True
           # 如果在面向目标的方向中不存在可以移动的方向，则在能移动的方向中选择
            else:
                # 如果这些方向大于1，且前一步的反方向在其中，则将其移除（确保怪物不来回移动）
                if len(dir_can_move) > 1 and (self.direction[0]*-1, self.direction[1]*-1) in dir_can_move:
                    dir_can_move.remove(
                        (self.direction[0]*-1, self.direction[1]*-1))
                self.direction = random.choice(list(dir_can_move))
                self.dir_changed = True
        # 玩家位置改变
        self.rect.centerx += self.speed*self.direction[0]
        self.rect.centery += self.speed*self.direction[1]
        return

    def be_weak(self):  # 变虚弱
        self.weak_time = 300
        self.img = pygame.image.load(self.img_ori[1]).convert_alpha()

    def weak_time_sub_1(self):  # 虚弱时间-1
        self.weak_time -= 1
        if self.weak_time == 0:
            self.img = pygame.image.load(self.img_ori[0]).convert_alpha()
        elif self.weak_time < 20:
            self.img = pygame.image.load(self.img_ori[1]).convert_alpha()
        elif self.weak_time < 40:
            self.img = pygame.image.load(self.img_ori[0]).convert_alpha()
        elif self.weak_time < 60:
            self.img = pygame.image.load(self.img_ori[1]).convert_alpha()
        elif self.weak_time < 80:
            self.img = pygame.image.load(self.img_ori[0]).convert_alpha()
        elif self.weak_time < 100:
            self.img = pygame.image.load(self.img_ori[1]).convert_alpha()
        elif self.weak_time < 120:
            self.img = pygame.image.load(self.img_ori[0]).convert_alpha()


def main():  # 主程序
    # 地图
    map_wall = [[1]*19] +\
        [[1]+[2]+[0]*15+[2]+[1]] +\
        [[1]*3+[0]+[1]*5+[0]+[1]*5+[0]+[1]*3] +\
        [[1]+[0]*17+[1]] +\
        [[1]+[0]+[1]*3+[0]+[1]*7+[0]+[1]*3+[0]+[1]] +\
        [[1]+[0]*17+[1]] +\
        [[1]*3+[0]+[1]*5+[0]+[1]*5+[0]+[1]*3] +\
        [[1]+[0]*17+[1]] +\
        [[1]+[0]+[1]+[0]+[1]+[0]+[1]+[0]+[1]*3+[0]+[1]+[0]+[1]+[0]+[1]+[0]+[1]] +\
        [[1]+[0]+[1]+[0]+[1]+[0]+[1]+[0]+[3]+[3]+[1]+[0]+[1]+[0]+[1]+[0]+[1]+[0]+[1]] +\
        [[1]+[0]+[1]+[0]+[1]+[0]+[1]+[0]+[1]*3+[0]+[1]+[0]+[1]+[0]+[1]+[0]+[1]] +\
        [[1]+[0]*17+[1]] +\
        [[1]*3+[0]+[1]*5+[0]+[1]*5+[0]+[1]*3] +\
        [[1]+[0]*17+[1]] +\
        [[1]+[0]+[1]*3+[0]+[1]*7+[0]+[1]*3+[0]+[1]] +\
        [[1]+[0]*17+[1]] +\
        [[1]*3+[0]+[1]*5+[0]+[1]*5+[0]+[1]*3] +\
        [[1]+[2]+[0]*15+[2]+[1]] +\
        [[1]*19]

    # 游戏初始化
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Eat the beans")

    # 创建玩家精灵
    player = PlayerClass()
    # 创建墙体精灵组
    wallGroup = pygame.sprite.Group()
    # 创建豆子精灵组
    beanGroup = pygame.sprite.Group()
    for i in range(len(map_wall)):
        for j in range(len(map_wall[0])):
            if map_wall[i][j] == 1:
                wall = WallClass()
                wall.rect.center = (24*i+12, 24*j+12)
                wallGroup.add(wall)
            elif map_wall[i][j] == 0:
                bean = BeanClass(False)
                bean.rect.center = (24*i+12, 24*j+12)
                beanGroup.add(bean)
            elif map_wall[i][j] == 2:
                bean = BeanClass(True)
                bean.rect.center = (24*i+12, 24*j+12)
                beanGroup.add(bean)

    # 创建怪物精灵组
    enermyGroup = pygame.sprite.Group()
    for i in range(4):
        enermy = EnermyClass()
        enermyGroup.add(enermy)

    # 时钟
    clock = pygame.time.Clock()

    # 生命数的显示
    font = pygame.font.Font(None, 40)
    life1_txt = font.render(u'Lifes: ', True, (255, 0, 0))
    life1_txt_rect = life1_txt.get_rect()
    life1_txt_rect.topleft = (
        0, screen.get_rect().height - life1_txt_rect.height)
    life2_txt = font.render(u'0', True, (255, 0, 0))
    life2_txt_rect = life2_txt.get_rect()
    life2_txt_rect.topleft = (life1_txt_rect.right,
                              screen.get_rect().height - life1_txt_rect.height)

    # 分数
    Scores = 0
    # 分数的显示
    font = pygame.font.Font(None, 40)
    score1_txt = font.render(u'Scores: ', True, (255, 0, 0))
    score1_txt_rect = score1_txt.get_rect()
    score1_txt_rect.topleft = (
        200, screen.get_rect().height - life1_txt_rect.height)
    score2_txt = font.render(u'0', True, (255, 0, 0))
    score2_txt_rect = score2_txt.get_rect()
    score2_txt_rect.topleft = (
        score1_txt_rect.right, screen.get_rect().height - life1_txt_rect.height)

    # 主循环
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            sys.exit()

        # 绘制背景
        screen.fill((0, 0, 0))
        # 绘制墙体
        for each in wallGroup:
            screen.blit(each.img, each.rect)
        # 绘制豆子
        for each in beanGroup:
            screen.blit(each.img, each.rect)

        # 如果有按键，则改变对应的移动方向
        if keys[pygame.K_UP]:
            player.direction = [0, -1]
        elif keys[pygame.K_DOWN]:
            player.direction = [0, 1]
        elif keys[pygame.K_LEFT]:
            player.direction = [-1, 0]
        elif keys[pygame.K_RIGHT]:
            player.direction = [1, 0]
        # 玩家朝按键对应的移动方向移动
        player.move(wallGroup, player.direction)
        # 如果移动成功，则前一步的移动方向改为当前移动方向
        if player.isMove:
            player.direction_old = player.direction
        # 如果移动不成功，则朝前一步的移动方向移动
        else:
            player.move(wallGroup, player.direction_old)
        # 绘制玩家
        screen.blit(player.img, player.rect)

        # 每个怪物的操作
        for each in enermyGroup:
            # 怪物的移动
            each.move(player, wallGroup)
            if each.weak_time > 0:
                # 减少怪物的虚弱时间
                each.weak_time_sub_1()
            # 如果被吃掉的怪物回到了初始位置，则复活
            if not each.being and each.rect.centerx == each.center_init[0] and each.rect.centery == each.center_init[1]:
                each.reset()
            # 绘制怪物
            screen.blit(each.img, each.rect)

        # 判断玩家是否与豆子组碰撞
        list_collide = pygame.sprite.spritecollide(player, beanGroup, False)
        for each in list_collide:
            if not pygame.sprite.collide_rect_ratio(0.5)(each, player):
                continue
            Scores += 1
            beanGroup.remove(each)
            # 如果是大豆子
            if each.isBigger == True:
                for each_enermy in enermyGroup:
                    if each_enermy.being:
                        each_enermy.be_weak()

        # 判断玩家是否与怪物组碰撞
        list_collide = pygame.sprite.spritecollide(player, enermyGroup, False)
        for each in list_collide:
            if not pygame.sprite.collide_rect_ratio(0.5)(each, player):
                continue
            # 如果不是虚弱或被吃掉的怪物
            if each.weak_time == 0 and each.being:
                player.lifes -= 1
                if player.lifes == 0:
                    break
                player.reset()
                for each_enermy in enermyGroup:
                    each_enermy.reset()
                time.sleep(1)
                break
            # 如果是虚弱的怪物
            elif each.weak_time > 0:
                Scores += 10
                each.be_eaten()

        # 如果玩家生命数为0
        if player.lifes == 0:
            font = pygame.font.Font(None, 40)
            content = font.render(u'You Lose!', True, (255, 0, 0))
            rect = content.get_rect()
            rect.center = (screen.get_rect().width/2,
                           screen.get_rect().height/2)
            screen.blit(content, rect)

        # 如果豆子吃完了
        if len(beanGroup) == 0:
            font = pygame.font.Font(None, 40)
            content = font.render(u'You Win!', True, (255, 0, 0))
            rect = content.get_rect()
            rect.center = (screen.get_rect().width/2,
                           screen.get_rect().height/2)
            screen.blit(content, rect)

        # 绘制生命数
        screen.blit(life1_txt, life1_txt_rect)
        font = pygame.font.Font(None, 40)
        life2_txt = font.render(
            str(player.lifes), True, (255, 0, 0))
        screen.blit(life2_txt, life2_txt_rect)

        # 绘制分数
        screen.blit(score1_txt, score1_txt_rect)
        font = pygame.font.Font(None, 40)
        score2_txt = font.render(
            str(Scores), True, (255, 0, 0))
        screen.blit(score2_txt, score2_txt_rect)

        # 画面更新
        # pygame.display.flip()
        pygame.display.update()
        # 设置每秒的帧数
        clock.tick(32)

        if player.lifes == 0 or len(beanGroup) == 0:
            break

    # 游戏结束界面
    restart_img = pygame.image.load('restart.png').convert_alpha()
    restart_rect = restart_img.get_rect()
    restart_rect.center = (screen.get_rect().width/2,
                           screen.get_rect().height/2+30)
    screen.blit(restart_img, restart_rect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            sys.exit()
        # 重玩
        if keys[K_SPACE]:
            main()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < restart_rect.right and mouse_pos[0] > restart_rect.left and\
                    mouse_pos[1] < restart_rect.bottom and mouse_pos[1] > restart_rect.top:
                main()


if __name__ == '__main__':
    main()
