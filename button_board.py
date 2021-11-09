from pydub import AudioSegment
from pydub.playback import play
import neopixel
import board
import asyncio


class ButtonBoard:
    def __init__(self):
        self.running = True
        self.leds = neopixel.NeoPixel(board.D18, 25)
        self.speaker = self.Speakers()
        self.buttons = []
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.detect_button_presses())
        for i in range(5):
            self.buttons.append([])
            for j in range(5):
                self.buttons[i].append(self.Button(self, i*5+j))

    class Button:
        def __init__(self, button_board, led_pos):
            self.button_board = button_board
            self.led_pos = led_pos
            self.active = False
            self.pressed = False

        def light_up(self, color=(255, 255, 255)):
            self.button_board.leds[self.led_pos] = color

        def activate(self):
            self.light_up((0, 255, 0))
            self.active = True

        def deactivate(self):
            self.light_up((0, 0, 0))
            self.active = False

    class Speakers:
        def __init__(self):
            pass

        def play_mp3(self, filename):
            sound = AudioSegment.from_mp3('sounds/'+filename)
            play(sound)

    async def detect_button_presses(self):
        while self.running:
            pass


ButtonBoard()
