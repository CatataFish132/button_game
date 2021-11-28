import pygame
from button_board import ButtonBoard
import threading
from main import Game
import time
import asyncio


class Emulator:
    class Button:

        def __init__(self, emu, pos=(0, 0), index=(0, 0)):
            self.emu = emu
            self.index = index
            self.i, self.j = self.index
            self.color = (255, 255, 255)
            self.pos = pos
            self.image = pygame.Surface((50, 50))
            self.rect = self.image.get_rect()
            self.rect.center = pos
            self.led_pos = emu.board.buttons[self.i][self.j].led_pos
            print(self.led_pos)

        def click(self, event):
            x, y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if self.rect.collidepoint(x, y):
                        self.emu.board.buttons[self.i][self.j].pressed = True
                        return
            self.emu.board.buttons[self.i][self.j].pressed = False

        def show(self):
            pygame.draw.circle(self.image, self.color, center=(25, 25), radius=25)
            self.emu.screen.blit(self.image, self.rect)

        def update(self):
            self.color = self.emu.board.leds[self.led_pos]

    def __init__(self):
        self.game = Game()
        self.board = self.game.board
        pygame.init()
        pygame.font.init()
        self.size = (600, 600)
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.buttons = []
        for i, button_list in enumerate(self.board.buttons):
            for j, button in enumerate(button_list):
                self.buttons.append(self.Button(self, (50 + 100 * j, 50 + 100 * i), (i, j)))
        self.loop()

    def loop(self):
        while True:
            self.screen.fill((105, 105, 105))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                for button in self.buttons:
                    button.click(event)
            for button in self.buttons:
                button.show()
                button.update()
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    Emulator()
