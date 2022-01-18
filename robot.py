from button_board import ButtonBoard
import asyncio
import threading
import time
import random
import configparser


class Game:
    def __init__(self):
        self.board = ButtonBoard()
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.running = True
        self.active_buttons = []
        self.next_i = 0
        self.next_j = 0
        if self.config["Game"]["Emulator_mode"] == "True":
            f = lambda: asyncio.run(self.start())
            t1 = threading.Thread(target=f, daemon=True)
            t1.start()
        else:
            asyncio.run(self.start())

    async def start(self):
        # don't listen to the IDE this has to be here
        self.board.colour_all_leds((0,0,0))
        for button_row in self.board.buttons:
            for button in button_row:
                button.deactivate()
        self.last_button_pressed = None
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(await self.robot())

    def deactivate_all_buttons(self):
        for button_row in self.board.buttons:
            for button in button_row:
                button.deactivate()
    
    def reset_board(self):
        self.deactivate_all_buttons()
        self.board.colour_all_leds((0,0,0))
        self.last_button_pressed = None


    async def robot(self, *args, **kwargs):
        running = True
        self.reset_board()
        detection_loop = self.loop.create_task(self.another_loop())
        while running:
            await asyncio.sleep(0.001)
            if len(self.active_buttons == 0):
                if self.next_j < 4:
                    self.next_j = self.next_j + 1
                else:
                    self.next_j = 0
                    if self.next_i < 3:
                        self.next_i = self.next_i+1
                    else:
                        self.next_i = 0
                    self.board.buttons[self.next_i][self.next_j].activate()
                    self.active_buttons.append(self.board.buttons[self.next_i][self.next_j])
        detection_loop.cancel()

    # this does stuff with inputs. should prob be reworked
    async def another_loop(self):
        while self.running:
            log_file = open("button_logs.txt", "a")
            wrong_file = open("wrong_button.txt", "a")
            for i, list_buttons in enumerate(self.board.buttons):
                for j, button in enumerate(list_buttons):
                    if button.active and button.pressed:
                        button.detected = True
                        self.active_buttons.remove(button)
                        button.deactivate()
                        log_file.write(",".join(str(i), str(j))+"\n")
                        print(i, j)
                    elif not button.active and button.pressed and not button.detected:
                        button.detected = True
                        log_file.write(",".join(str(i), str(j))+"\n")
                        wrong_file.write(",".join(str(i), str(j))+"\n")
                        self.active_buttons.pop(0).deactivate()
                        if j < 4:
                            next_j = j + 1
                            next_i = i
                        else:
                            next_j = 0
                            if i < 3:
                                next_i = i+1
                            else:
                                next_i = 0
                        self.board.buttons[next_i][next_j].activate()
                        self.active_buttons.append(self.board.buttons[next_i][next_j])
                        print("error detected")
                    elif not button.pressed:
                        button.detected = False
            await asyncio.sleep(0.0001)

if __name__ == "__main__":
    Game()
