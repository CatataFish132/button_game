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
        if self.config["Game"]["Emulator_mode"] == "True":
            f = lambda: asyncio.run(self.start())
            t1 = threading.Thread(target=f, daemon=True)
            t1.start()
        else:
            asyncio.run(self.start())

    async def start(self):
        # don't listen to the IDE this has to be here
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(await self.on_the_beat())

    async def game_loop(self, difficulty):
        pass

    async def on_the_beat(self):
        self.board.colour_all_leds((0,0,0))
        difficulty = 0
        running = True
        self.loop.create_task(self.another_loop())
        with open("sounds/Valerie.beatmap.txt") as f:
            beatmap = f.read()
            beatmap = beatmap.split("\n")
            for i in range(len(beatmap)):
                beatmap[i] = float(beatmap[i])

        self.board.speaker.play_mp3("Valerie.mp3")
        start_time = time.time()
        while running:
            dtime = time.time() - start_time
            if beatmap[0]-dtime > 0.5:
                await asyncio.sleep(beatmap[0]-dtime-0.5)
            if len(self.active_buttons) < 1:
                while True:
                    i = random.randint(0, len(self.board.buttons)-1)
                    j = random.randint(0, len(self.board.buttons[0])-1)
                    button = self.board.buttons[i][j]
                    if button not in self.active_buttons:
                         break
                button.light_up((255,0,0))
                await asyncio.sleep(0.51)
                button.activate()
                self.active_buttons.append(button)
            beatmap.pop(0)

    async def fast_as_possible(self, amount=1):
        running = True
        self.board.colour_all_leds((0,0,0))
        self.last_button_pressed = None
        while running:
            await asyncio.sleep(0.001)
            if len(self.active_buttons) < amount:
                while True:
                    i = random.randint(0, len(self.board.buttons)-1)
                    j = random.randint(0, len(self.board.buttons[0])-1)
                    button = self.board.buttons[i][j]
                    if button not in self.active_buttons and button != self.last_button_pressed:
                         break
                button.activate()
                self.active_buttons.append(button)

    # this does stuff with inputs. should prob be reworked
    async def another_loop(self):
        while self.running:
            for i, list_buttons in enumerate(self.board.buttons):
                for j, button in enumerate(list_buttons):
                    if button.active and button.pressed:
                        self.active_buttons.remove(button)
                        button.deactivate()
                        self.last_button_pressed = button
            await asyncio.sleep(0.0001)


if __name__ == "__main__":
    Game()
