# -*- coding: UTF-8 -*-
# drawing.py

# 导入需要的模块
import pygame
import sys
import button
import copy
import numpy as np
import time
import displaybox
from pygame.locals import *
from pruning_algorithm import PruningAlg
import random

white_win = 2
black_win = 1

class interface:
    # 定义颜色
    def __init__(self):
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.background = (184, 134, 11)
        self.start_point = 40
        self.end_point = 640
        self.black_chess = 1
        self.white_chess = 2
        self.blank_space = 0
        # 五子棋棋盘
        self.board = [[0] * 15 for i in range(15)]
        self.visit = [[False] * 15 for i in range(15)]
        # 初始化pygame
        pygame.init()
        # 屏幕框设置
        self.screen = pygame.display.set_mode((800, 700))
        # 字体设置
        self.font = pygame.font.Font('comic.ttf', 20)
        self.font_zn = pygame.font.Font('zn.ttf', 22)
        # 图片路径
        self.background_path = 'background2.png'
        self.black_key_path = 'black.png'  # 棋子像素为30*30
        self.white_key_path = 'white.png'
        self.win_path = 'win.jpeg'
        # 设置窗口标题
        pygame.display.set_caption('五子棋')
        # 设置背景颜色
        self.screen.fill(self.white)
        # 加载并转换图像
        self.keyboard = pygame.image.load(self.background_path).convert()
        # 棋盘背景像素700*700
        self.screen.blit(self.keyboard, (0, 0))
        # 图片加载
        self.black_key = pygame.image.load(self.black_key_path).convert_alpha()
        self.white_key = pygame.image.load(self.white_key_path).convert_alpha()
        self.draw_board(self.start_point, self.end_point)
        # 设置按钮
        self.button1 = button.button(self.screen, 680, 150, '重来')
        self.button2 = button.button(self.screen, 680, 200, '悔棋')
        self.button3 = button.button(self.screen, 680, 250, '退出')
        self.last_board = self.board
        # 显示框
        self.ai_box = displaybox.DisplayBox(self.screen, 640, 300, 'AI', self.font, self.font_zn)
        self.pl_box = displaybox.DisplayBox(self.screen, 640, 480, 'Player', self.font, self.font_zn)
        self.end_pos = [0, 0]
        self.algorithm = PruningAlg(ctrl_side=self.white_chess)

    # 绘制棋盘
    def draw_board(self, start, end):
        # 在(start,start)和(end,end)之间绘制一个棋盘，需要保证start=end-600 棋盘像素为600*600
        # 可用范围为(start + 20, end - 20), 两列之间相差40像素
        up_limit = start + 10
        down_limit = end - 10
        pygame.draw.aaline(self.screen, self.black, [up_limit, up_limit], [up_limit, down_limit], True)
        pygame.draw.aaline(self.screen, self.black, [up_limit, up_limit], [down_limit, up_limit], True)
        pygame.draw.aaline(self.screen, self.black, [down_limit, up_limit], [down_limit, down_limit], True)
        pygame.draw.aaline(self.screen, self.black, [up_limit, down_limit], [down_limit, down_limit], True)
        pygame.draw.aaline(self.screen, self.black, [up_limit + 10, up_limit + 10], [up_limit + 10, down_limit - 10],
                           True)
        pygame.draw.aaline(self.screen, self.black, [up_limit + 10, up_limit + 10], [down_limit - 10, up_limit + 10],
                           True)
        pygame.draw.aaline(self.screen, self.black, [down_limit - 10, up_limit + 10],
                           [down_limit - 10, down_limit - 10], True)
        pygame.draw.aaline(self.screen, self.black, [up_limit + 10, down_limit - 10],
                           [down_limit - 10, down_limit - 10], True)
        start_point = up_limit + 10
        end_point = down_limit - 10
        for i in range(1, 15):
            pygame.draw.aaline(self.screen, self.black, [start_point + 40 * i, start_point],
                               [start_point + 40 * i, end_point],
                               True)
        for i in range(1, 15):
            pygame.draw.aaline(self.screen, self.black, [start_point, start_point + 40 * i],
                               [end_point, start_point + 40 * i],
                               True)
        # 打点
        pygame.draw.circle(self.screen, self.black, center=[start_point + 280, start_point + 280], radius=5)
        pygame.draw.circle(self.screen, self.black, center=[start_point + 120, start_point + 120], radius=5)
        pygame.draw.circle(self.screen, self.black, center=[start_point + 440, start_point + 120], radius=5)
        pygame.draw.circle(self.screen, self.black, center=[start_point + 120, start_point + 440], radius=5)
        pygame.draw.circle(self.screen, self.black, center=[start_point + 440, start_point + 440], radius=5)

        x = start_point - 40
        for i in range(15):
            y = i * 40 + start_point - 15
            text = self.font.render(str(15 - i), True, self.black)
            self.screen.blit(text, (x, y))

        y = end_point + 15
        for i in range(15):
            x = i * 40 + start_point - 5
            text = self.font.render(chr(ord('A') + i), True, self.black)
            self.screen.blit(text, (x, y))

    # 将鼠标点击的像素位置能够转化为其在五子棋矩阵中的行列
    def translate_pos(self, old_pos, start_point):
        pos = [(old_pos[0] - start_point - 20) % 40, (old_pos[1] - start_point - 20) % 40]
        new_pos = [(old_pos[0] - start_point - 20) // 40, (old_pos[1] - start_point - 20) // 40]

        if pos[0] > 20:
            pos[0] = 40 - pos[0]
            new_pos[0] = new_pos[0] + 1

        if pos[1] > 20:
            pos[1] = 40 - pos[1]
            new_pos[1] = new_pos[1] + 1

        # 设定响应范围半径50像素
        if pos[0] * pos[0] + pos[1] * pos[1] < 50:
            if 0 <= new_pos[0] <= 14 and 0 <= new_pos[1] <= 14:
                return new_pos
        return [-1, -1]

    # 将五子棋矩阵中的行列转换成放置棋子图片的像素位置
    def place_key_pos(self, old_pos, start_point):
        return [old_pos[0] * 40 - 15 + start_point + 20, old_pos[1] * 40 - 15 + start_point + 20]

    # 将五子棋矩阵行列转换成(字母+数字)坐标
    def get_show_pos(self, pos):
        return [chr(ord('A') + pos[0]), 15 - pos[1]]

    # 更新棋盘
    def update_board(self):
        for i in range(15):
            for j in range(15):
                if not self.visit[i][j]:
                    if self.board[i][j] == self.black_chess:
                        self.move(self.black_key, (j, i))
                        self.visit[i][j] = True
                    if self.board[i][j] == self.white_chess:
                        self.move(self.white_key, (j, i))
                        self.visit[i][j] = True

    # 根据五子棋矩阵行列下一步棋
    def move(self, key, pos):
        # key:棋子图片(已经加载)
        # pos:棋盘矩阵位置
        # 查看棋盘状态并修改
        place_pos = self.place_key_pos(pos, self.start_point)  # 放置棋子图片位置
        self.screen.blit(key, place_pos)

    # 检测是否胜利
    def check_win(self):
        win_status = False
        lose_status = False
        # 检索横向棋盘
        for i in range(15):
            j = 0
            while j < 15:
                if self.board[i][j]:
                    count = 0
                    chess_type = self.board[i][j]
                    while chess_type == self.board[i][j]:
                        count += 1
                        j += 1
                        if chess_type != self.board[i][j]:
                            j -= 1
                            break
                        if j == 15:
                            break
                    if count >= 5:
                        if chess_type == self.black_chess:
                            win_status = True
                        if chess_type == self.white_chess:
                            lose_status = True
                j += 1
        # 检索竖向棋盘
        for i in range(15):
            j = 0
            while j < 15:
                if self.board[j][i]:
                    count = 0
                    chess_type = self.board[j][i]
                    while chess_type == self.board[j][i]:
                        count += 1
                        j += 1
                        if chess_type != self.board[j][i]:
                            j -= 1
                            break
                        if j == 15:
                            break
                    if count >= 5:
                        if chess_type == self.black_chess:
                            win_status = True
                        if chess_type == self.white_chess:
                            lose_status = True
                j += 1
        # 检索上半部分斜对角线
        for i in range(15):
            j = 0
            while j <= i:
                if self.board[j][i - j]:
                    count = 0
                    chess_type = self.board[j][i - j]
                    while chess_type == self.board[j][i - j]:
                        count += 1
                        j += 1
                        if chess_type != self.board[j][i - j]:
                            j -= 1
                            break
                        if j == 15:
                            break
                    if count >= 5:
                        if chess_type == self.black_chess:
                            win_status = True
                        if chess_type == self.white_chess:
                            lose_status = True
                j += 1
        for i in range(15):
            j = 0
            while j <= 14 - i:
                if self.board[i + j][j]:
                    count = 0
                    chess_type = self.board[i + j][j]
                    while chess_type == self.board[i + j][j]:
                        count += 1
                        j += 1
                        if chess_type != self.board[i + j][j]:
                            j -= 1
                            break
                        if j == 15 - i:
                            break
                    if count >= 5:
                        if chess_type == self.black_chess:
                            win_status = True
                        if chess_type == self.white_chess:
                            lose_status = True
                j += 1
        # 检索下半部分对角线
        for i in range(15):
            j = 0
            while j <= 14 - i:
                if self.board[i + j][14 - j]:
                    count = 0
                    chess_type = self.board[i + j][14 - j]
                    while chess_type == self.board[i + j][14 - j]:
                        count += 1
                        j += 1
                        if chess_type != self.board[i + j][14 - j]:
                            j -= 1
                            break
                        if j == 15 - i:
                            break
                    if count >= 5:
                        if chess_type == self.black_chess:
                            win_status = True
                        if chess_type == self.white_chess:
                            lose_status = True
                j += 1
        for i in range(15):
            j = 0
            while j <= 14 - i:
                if self.board[j][i + j]:
                    count = 0
                    chess_type = self.board[j][i + j]
                    while chess_type == self.board[j][i + j]:
                        count += 1
                        j += 1
                        if chess_type != self.board[j][i + j]:
                            j -= 1
                            break
                        if j == 15 - i:
                            break
                    if count >= 5:
                        if chess_type == self.black_chess:
                            win_status = True
                        if chess_type == self.white_chess:
                            lose_status = True
                j += 1
        if win_status:
            return black_win
        if lose_status:
            return white_win
        else:
            return False

    # 重新画界面 覆盖原有界面
    def draw_again(self):
        self.screen.fill(self.white)
        self.screen.blit(self.keyboard, (0, 0))
        self.draw_board(self.start_point, self.end_point)
        self.button1.draw_button()
        self.button2.draw_button()
        self.button3.draw_button()
        self.ai_box.get_text('')
        self.pl_box.get_text('')
        self.ai_box.draw()
        self.pl_box.draw()

    # 重新开始游戏
    def restart(self):
        for i in range(15):
            for j in range(15):
                self.board[i][j] = 0
                self.visit[i][j] = False
        self.algorithm = PruningAlg(ctrl_side=self.white_chess)
        self.draw_again()

    # 棋盘对于鼠标动作的反馈 包含棋盘的变化以及ai算法
    def board_react(self, event):
        if event.type == MOUSEBUTTONDOWN:
            press = pygame.mouse.get_pressed()
            if press == (True, False, False):
                ori_pos = pygame.mouse.get_pos()  # 原始像素位置
                press_pos = self.translate_pos(ori_pos, self.start_point)  # 点击处棋盘矩阵行列
                # 点击在了棋盘上：
                if not press_pos == [-1, -1]:
                    # 重复落子
                    if self.visit[press_pos[1]][press_pos[0]]:
                        return 0
                    # 黑棋落子
                    self.last_board = copy.deepcopy(self.board)
                    self.board[press_pos[1]][press_pos[0]] = self.black_chess
                    print(self.get_show_pos(press_pos))
                    # board = get_next_step_ai() it is a function that return a board
                    # print(np.array(self.board))
                    # 黑棋落子即显示，增强交互性
                    self.update_board()
                    show_pl_pos = self.get_show_pos(press_pos)
                    self.pl_box.get_text(str(show_pl_pos[1]) + '行' + str(show_pl_pos[0]) + '列')
                    self.pl_box.draw()
                    pygame.display.update()
                    # 检查是否获胜或者失败
                    self.update_board()
                    if self.check_win() == white_win:
                        print("lost!")
                        return white_win
                    elif self.check_win() == black_win:
                        print("win")
                        return black_win

                    # 白棋落子
                    self.ai_box.get_text('计算中')
                    self.ai_box.draw()
                    pygame.display.update()
                    choice = self.algorithm.startSearch(np.array(self.board))
                    self.board[choice[0]][choice[1]] = self.white_chess
                    show_ai_pos = self.get_show_pos((choice[1], choice[0]))
                    self.ai_box.get_text(str(show_ai_pos[1]) + '行' + str(show_ai_pos[0]) + '列')
                    self.ai_box.draw()
                    # print(np.array(self.board))
                    self.update_board()
                    # 检查是否获胜或者失败
                    if self.check_win() == white_win:
                        print("lost!")
                        return white_win
                    elif self.check_win() == black_win:
                        print("win")
                        return black_win
                    return 0
                return 0
            return 0
        return 0

    # 显示悔棋之后的棋局内容
    def show_last_board(self):
        self.draw_again()
        for i in range(15):
            for j in range(15):
                self.visit[i][j] = False
        if self.board == [[0] * 15 for i in range(15)]:
            self.pl_box.draw(select=3)
        elif self.board == self.last_board:
            self.pl_box.draw(select=1)
        # 之后要显示一个提示
        self.board = self.last_board.copy()
        self.update_board()

    # 显示按钮对鼠标事件的相应
    def button_react(self, event):
        if self.button1.get_clicked(event):
            self.restart()
        if self.button2.get_clicked(event):
            self.show_last_board()
        if self.button3.get_clicked(event):
            pygame.quit()
            sys.exit()
        self.button1.sense_mouse_motion(event)
        self.button2.sense_mouse_motion(event)
        self.button3.sense_mouse_motion(event)

    # 结束之后的反应
    def end_react(self, status):
        if status == black_win:
            text = '赢'
        else:
            text = '输'

        end_box = displaybox.DisplayBox(self.screen, 180, 220, '', self.font, self.font_zn)
        end_box.get_text('你' + text + '了! 想要再来一局吗？')
        end_box.draw(select=2)

        button_1 = button.button(self.screen, 200, 400, '重来')
        button_2 = button.button(self.screen, 480, 400, '退出')
        for event in pygame.event.get():
            if event.type == QUIT:
                # 退出pygame
                pygame.quit()
                # 退出系统
                sys.exit()

            if button_1.get_clicked(event):
                self.restart()
                return 1
            if button_2.get_clicked(event):
                pygame.quit()
                sys.exit()
            button_1.sense_mouse_motion(event)
            button_2.sense_mouse_motion(event)
            pygame.display.update()
        return 0

    def solution(self):
        # 程序主循环
        while True:
            # 获取事件
            for event in pygame.event.get():
                # 判断事件是否为退出事件
                if event.type == QUIT:
                    # 退出pygame
                    pygame.quit()
                    # 退出系统
                    sys.exit()
                # 棋盘响应
                status = self.board_react(event)
                while status != 0:
                    end = self.end_react(status)
                    if end:
                        break

                # 按钮响应
                self.button_react(event)

            # 绘制屏幕内容
            pygame.display.update()


a = interface()
a.solution()
