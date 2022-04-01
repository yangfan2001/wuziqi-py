import pygame
from pygame.locals import *
from pygame import gfxdraw


class button:
    def __init__(self, surface, start_pos_x, start_pos_y, content):
        self.start_x = start_pos_x
        self.start_y = start_pos_y
        self.button_width = 80
        self.button_hight = 40
        self.surface = surface
        self.font = pygame.font.Font('comic.ttf', 20)
        self.font_zn = pygame.font.Font('zn.ttf', 25)
        self.content = content
        self.draw_button()

    # 画按钮
    def draw_button(self):
        pygame.draw.rect(self.surface, (0, 0, 0),
                         (self.start_x, self.start_y, self.button_width, self.button_hight)
                         , 2, border_radius=5)
        text = self.font_zn.render(self.content, True, (0, 0, 0))
        self.surface.blit(text, (self.start_x + 15, self.start_y + 5))

    def get_clicked(self, event):
        if event.type == MOUSEBUTTONDOWN:
            press = pygame.mouse.get_pressed()
            if press == (True, False, False):
                ori_pos = pygame.mouse.get_pos()  # 原始像素位置
                if self.start_x < ori_pos[0] < self.start_x + self.button_width and \
                        self.start_y < ori_pos[1] < self.start_y + self.button_hight:
                    return True
        return False

    def sense_mouse_motion(self, event):
        if event.type == MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            # 鼠标在按钮控件的范围内时
            if self.start_x < pos[0] < self.start_x + self.button_width and \
                    self.start_y < pos[1] < self.start_y + self.button_hight:
                pygame.draw.rect(self.surface, (255, 255, 255),
                                 (self.start_x, self.start_y, self.button_width, self.button_hight)
                                 , 2, border_radius=5)
            # 鼠标不在按钮控件的范围内时
            else:
                pygame.draw.rect(self.surface, (0, 0, 0),
                                 (self.start_x, self.start_y, self.button_width, self.button_hight)
                                 , 2, border_radius=5)
