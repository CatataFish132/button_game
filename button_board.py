from pydub import AudioSegment
from pydub.playback import play
try:
    import board
    import neopixel
except NotImplementedError:
    print("running in emulation mode")
    import neopixel_emu as neopixel
    import mockboard as board
import time
import asyncio
import threading
import serial


class ButtonBoard:
    def __init__(self):
        self.running = True

        # if its not running on a pi this will emulate what the NeoPixel library does
        # try:
        self.leds = neopixel.NeoPixel(board.D18, 24)
        # except NameError:
            # self.leds = [(0, 0, 0) for x in range(29)]
        self.speaker = self.Speakers()
        self.serial = serial.Serial("COM4", 115200)

        # Creating the buttons
        self.buttons = []
        for i in range(4):
            self.buttons.append([])
            for j in range(6):
                self.buttons[i].append(self.Button(self, i*6 + j))
        t1 = threading.Thread(target=self.thread_loop, args=(), daemon=True)
        t1.start()

    class Button:
        def __init__(self, button_board, led_pos):
            self.button_board = button_board
            self.led_pos = led_pos
            self.active = False
            self.pressed = False

        # Lights up the button to the desired RGB colour
        def light_up(self, color=(255, 255, 255)):
            r, g, b = color
            s = f"{self.led_pos}:{r}:{g}:{b}\n".encode()
            print(s)
            self.button_board.serial.write(s)

        # Activating the button by turning it to a green colour
        def activate(self):
            self.light_up((0, 255, 0))
            self.active = True

        # Deactivates the button by turning the led off
        def deactivate(self):
            self.light_up((0, 0, 0))
            self.active = False

    class Speakers:
        def __init__(self):
            pass

        # Play an mp3 file that is in the sounds folder
        def play_mp3(self, filename):
            f = lambda sound: play(sound)
            sound = AudioSegment.from_mp3('sounds/' + filename)
            t = threading.Thread(target=f, args=(sound,))
            t.start()
            # play(sound)

    # loop for detecting button presses.
    # TODO: add ability to detect button presses
    def thread_loop(self):
        print("its working i guess")
        while self.running:
            print(self.buttons[0][0].pressed)
            time.sleep(2)

    def colour_all_leds(self, colour=(254, 254, 254)):
        self.leds.fill(colour)
        pass

if __name__ == "__main__":
    ButtonBoard()
