import pygame
import time

class DisplayBox:
    def __init__(self, surface, x, y, name, font, font_zn, width=150, height=150):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.font = font
        self.font_zn = font_zn
        self.text = ''
        self.ai_path = 'aibox.png'
        self.pl_path = 'plbox.png'
        self.end_path = 'end.png'
        self.draw()

    def get_text(self, text):
        self.text = text

    def draw(self, select=0):
        if self.name == 'AI':
            path = self.ai_path
        elif self.name == 'Player':
            path = self.pl_path
        else:
            path = self.end_path
        box_bg = pygame.image.load(path).convert_alpha()
        if path == self.end_path:
            box_bg.set_alpha(30)
        self.surface.blit(box_bg, (self.x, self.y))

        if not select:
            text = self.font_zn.render('      ' + self.text, True, (0, 0, 0))
            self.surface.blit(text, (self.x + 5, self.y + 30))
        elif select == 1:
            text = self.font_zn.render('只能悔一步棋。' + self.text, True, (0, 0, 0))
            self.surface.blit(text, (self.x + 5, self.y + 60))
            text = self.font_zn.render('不能太贪心！' + self.text, True, (0, 0, 0))
            self.surface.blit(text, (self.x + 5, self.y + 90))
        elif select == 2:
            text = self.font_zn.render('   ' + self.text, True, (0, 0, 0))
            self.surface.blit(text, (self.x + 50, self.y + 20))
        elif select == 3:
            text = self.font_zn.render('棋盘是空的。' + self.text, True, (0, 0, 0))
            self.surface.blit(text, (self.x + 5, self.y + 60))
            text = self.font_zn.render('请先下棋！' + self.text, True, (0, 0, 0))
            self.surface.blit(text, (self.x + 5, self.y + 90))
