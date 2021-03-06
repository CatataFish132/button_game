from button_board import ButtonBoard
import asyncio
import threading
import time
import random
import configparser
from gtts import gTTS

class Game:
    def __init__(self):
        self.board = ButtonBoard()
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.running = True
        self.active_buttons = []
        self.reaction_time_list = []
        self.score = 0
        self.players = [{"reaction_time_list": [], "score": 0, "active_buttons": []}, {"reaction_time_list": [], "score": 0, "active_buttons": []}]
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
        self.loop.run_until_complete(await self.menu())

    async def game_loop(self, difficulty):
        pass

    def deactivate_all_buttons(self):
        for button_row in self.board.buttons:
            for button in button_row:
                button.deactivate()
    
    def reset_board(self):
        self.deactivate_all_buttons()
        self.board.colour_all_leds((0,0,0))
        self.last_button_pressed = None

    # a menu that executes the function in the dictionary if the tuple in the key is pressed
    async def menu(self):
        menu_dict = {(0,0): (self.fast_as_possible, 2), (0,2): (self.on_the_beat, None),
                    (2,0): (self.multiplayer, None)}
        while True:
            self.reset_board()
            for i, j in menu_dict.keys():
                self.board.buttons[i][j].activate()
            stop = False
            while not stop:
                for key, value in menu_dict.items():
                    i, j = key
                    if self.board.buttons[i][j].pressed:
                        self.reset_board()
                        func, argument = value
                        await func(argument)
                        stop = True
                        break



    async def on_the_beat(self, *args, **kwargs):
        self.board.colour_all_leds((0,0,0))
        difficulty = 0
        running = True
        button_detection = self.loop.create_task(self.another_loop())
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
                    if button not in self.active_buttons and button != self.last_button_pressed:
                         break
                button.light_up((255,0,0))
                await asyncio.sleep(0.51)
                button.activate()
                self.active_buttons.append(button)
            beatmap.pop(0)
            if len(beatmap) == 0:
                break
        button_detection.cancel()
        self.active_buttons = []
        total_reaction = 0
        for reaction_time in self.reaction_time_list:
            total_reaction += reaction_time
        print("average reaction time: ", total_reaction/len(self.reaction_time_list))
        print("score: ", self.score)

    async def fast_as_possible(self, *args, **kwargs):
        running = True
        start_time = time.time()
        self.reset_board()
        detection_loop = self.loop.create_task(self.another_loop())
        amount = args[0]
        while running:
            await asyncio.sleep(0.001)
            if time.time() - start_time > 20:
                running = False
            if len(self.active_buttons) < amount:
                while True:
                    i = random.randint(0, len(self.board.buttons)-1)
                    j = random.randint(0, len(self.board.buttons[0])-1)
                    button = self.board.buttons[i][j]
                    if button not in self.active_buttons and button != self.last_button_pressed:
                         break
                button.activate()
                self.active_buttons.append(button)
        detection_loop.cancel()
        self.board.colour_all_leds((255,255,255))
        s = f"your score is {self.score}"
        tts = gTTS(s, lang='en')
        tts.save("sounds/score.mp3")
        self.board.speaker.play_mp3("score.mp3")

        self.active_buttons = []

    async def multiplayer(self, *args, **kwargs):
        running = True
        start_time = time.time()
        self.reset_board()
        detection_loop = self.loop.create_task(self.two_player_loop())
        while running:
            await asyncio.sleep(0.001)
            if time.time() - start_time > 20:
                running = False
            for k, player in enumerate(self.players):
                if len(player["active_buttons"]) < 1:
                    while True:
                        j = random.randint(0, len(self.board.buttons[0])-1)
                        if k == 0:
                            i = random.randint(0, len(self.board.buttons)/2-1)
                        if k == 1:
                            i = random.randint(len(self.board.buttons)/2, len(self.board.buttons)-1)
                        button = self.board.buttons[i][j]
                        if button not in self.active_buttons and button != self.last_button_pressed:
                            break
                    if k == 0:
                        button.activate((0,0,255))
                    if k == 1:
                        button.activate()
                    player["active_buttons"].append(button)

        detection_loop.cancel()
        # print score
        player_1_total = 0
        player_2_total = 0
        for reaction_time in self.players[0]["reaction_time_list"]:
            player_1_total += reaction_time
        for reaction_time in self.players[1]["reaction_time_list"]:
            player_2_total += reaction_time
        
        if self.players[0]["score"] > self.players[1]["score"]:
            self.board.colour_all_leds((0,0,255))
        elif self.players[1]["score"] > self.players[0]["score"]:
            self.board.colour_all_leds((0,255,0))   
        else:
            self.board.colour_all_leds((255,255,255))

        s =f"the scores are green {self.players[1]['score']}. blue {self.players[0]['score']}"
        tts = gTTS(s, lang='en')
        tts.save("sounds/score.mp3")
        self.board.speaker.play_mp3("score.mp3")

        time.sleep(3)
        for player in self.players:
            player["active_buttons"] = []

    # this does stuff with inputs. should prob be reworked
    async def another_loop(self):
        self.reaction_time_list = []
        self.score = 0
        while self.running:
            for i, list_buttons in enumerate(self.board.buttons):
                for j, button in enumerate(list_buttons):
                    if button.active and button.pressed:
                        time1 = time.time()
                        self.board.speaker.play_good()
                        print(time1-time.time())
                        button.detected = True
                        self.active_buttons.remove(button)
                        reaction_time = button.deactivate()
                        self.reaction_time_list.append(reaction_time)
                        #self.score += (1/reaction_time)
                        self.score += 1
                        self.last_button_pressed = button
                    elif not button.active and button.pressed and not button.detected:
                        button.detected = True
                        time1 = time.time()
                        self.board.speaker.play_bad()
                        print(time1 - time.time())
                    elif not button.pressed:
                        button.detected = False
            await asyncio.sleep(0.0001)

    async def two_player_loop(self):
        for i in range(2):
            self.players[i]["reaction_time_list"] = []
            self.players[i]["score"] = 0
        while self.running:
            for i, list_buttons in enumerate(self.board.buttons):
                for j, button in enumerate(list_buttons):
                    if button.active and button.pressed:
                        self.board.speaker.play_good()
                        for player in self.players:
                            if button in player["active_buttons"]:
                                player["active_buttons"].remove(button)
                                reaction_time = button.deactivate()
                                player["reaction_time_list"].append(reaction_time)
                                player["score"] += 1#(1/reaction_time)
                                self.last_button_pressed = button
            await asyncio.sleep(0.0001)


if __name__ == "__main__":
    Game()
