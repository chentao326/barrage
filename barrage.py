# -*- coding: utf-8 -*-

import pygame
import sys
from pygame\
    .locals import *
import random
import math
import csv
import neuro_evolution
import pandas as pd

BACKGROUND = (190, 190, 190)  # 背景颜色
SCREEN_SIZE = (680, 880)  # 屏幕大小   宽 ， 高

class Car():
    def __init__(self, car_image):
        self.car_image = car_image
        self.rect = car_image.get_rect()

        self.width = self.rect[2]
        self.height = self.rect[3]
        self.x = SCREEN_SIZE[0] / 2 - self.width / 2
        self.y = SCREEN_SIZE[1] - self.height

        self.move_x = 0
        self.speed = 2

        self.alive = True

    def update(self):
        self.x += self.move_x * self.speed

    def draw(self, screen):
        screen.blit(self.car_image, (self.x, self.y, self.width, self.height))

    def is_dead(self, stone):
        if self.x < -self.width or self.x + self.width > SCREEN_SIZE[0] + self.width:
            return True
        for stone in stone:
            if self.collision(stone):
                return True
        return False

    def collision(self, stone):
        if not (
                self.x > stone.x + stone.width or self.x + self.width < stone.x or self.y > stone.y + stone.height or self.y + self.height < stone.y):
            return True
        else:
            return False

    def get_inputs_values(self, stones, input_size=4):
        inputs = []

        for i in range(input_size):
            inputs.append(0.0)

        inputs[0] = (self.x * 1.0 / SCREEN_SIZE[0])
        index = 1
        for stone in stones:
            inputs[index] = stone.x * 1.0 / SCREEN_SIZE[0]
            index += 1
            inputs[index] = stone.y * 1.0 / SCREEN_SIZE[1]
            index += 1
        if len(stones) > 0 and self.x < stones[0].x:
            inputs[index] = -1.0
            index += 1
        else:
            inputs[index] = 1.0

        return inputs

# 定义障碍物

class Stone():

    def __init__(self, stone_image):
        self.enemy_image = stone_image
        self.rect = stone_image.get_rect()

        self.width = self.rect[2]
        self.height = self.rect[3]
        self.x = random.choice(range(0, int(SCREEN_SIZE[0] - self.width / 2), 71))
        self.y = 0

    def update(self):
        self.y += 5  # 障碍物的速度

    def draw(self, screen):
        screen.blit(self.enemy_image, (self.x, self.y, self.width, self.height))

    def is_out(self):
        return True if self.y >= SCREEN_SIZE[1] else False

class Game():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('弹幕游戏')  # 弹幕游戏名称

        self.ai = neuro_evolution.NeuroEvolution()
        self.generation = 0

        self.max_stones = 1
        # 加载车和障碍物图片
        self.car_image = pygame.image.load('car.png').convert_alpha()
        self.stones_image = pygame.image.load('stone.png').convert_alpha()

    def start(self):
        self.score = 0
        self.cars = []
        self.stones = []

        self.gen = self.ai.next_generation()
        for i in range(len(self.gen)):
            car = Car(self.car_image)
            self.cars.append(car)

        self.generation += 1
        self.alives = len(self.cars)

    def update(self, screen):
        for i in range(len(self.cars)):
            if self.cars[i].alive:
                inputs = self.cars[i].get_inputs_values(self.stones)
                res = self.gen[i].feed_forward(inputs)
                if res[0] < 0.45:
                    self.cars[i].move_x = -1
                elif res[0] > 0.55:
                    self.cars[i].move_x = 1

                self.cars[i].update()
                self.cars[i].draw(screen)

                if self.cars[i].is_dead(self.stones) == True:
                    self.cars[i].alive = False
                    self.alives -= 1
                    self.score -= 2
                    self.ai.network_score(self.score, self.gen[i])
                    if self.is_ai_all_dead():
                        self.start()

        self.gen_stones()

        for i in range(len(self.stones)):
            self.stones[i].update()
            self.stones[i].draw(screen)
            if self.stones[i].is_out():
                del self.stones[i]
                break

        self.score += 1

        print("alive:{}, generation:{}, score:{}".format(self.alives, self.generation, self.score))

    def run(self, FPS=1000):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(BACKGROUND)

            self.update(self.screen)

            pygame.display.update()
            self.clock.tick(FPS)

    def gen_stones(self):
        if len(self.stones) < self.max_stones:
            enemy = Stone(self.stones_image)
            self.stones.append(enemy)

    def is_ai_all_dead(self):
        for car in self.cars:
            if car.alive:
                return False
        return True


game = Game()
game.start()
game.run()