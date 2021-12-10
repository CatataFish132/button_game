from pydub import AudioSegment
from pydub.playback import play
try:
    import board
    import neopixel
    import digitalio
except (NotImplementedError, ModuleNotFoundError):
    print("running in emulation mode")
    import neopixel_emu as neopixel
    import mockboard as board
    import digitalio
import time
import asyncio
import threading
import serial
import configparser
import RPi.GPIO as GPIO


class ButtonBoard:
    def __init__(self):
        self.running = True
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.speaker = self.Speakers()
        self.serial = serial.Serial(self.config["serial"]["port"], int(self.config["serial"]["speed"]))

        # Creating the buttons
        self.buttons = []
        x = int(self.config["board"]["size_x"])-1
        y = int(self.config["board"]["size_y"])-1
        for i in range(int(self.config["board"]["size_y"])):
            self.buttons.append([])
            for j in range(int(self.config["board"]["size_x"])):
                self.buttons[i].append(self.Button(self, i + j*y + j))

        # creating pins
        x_pins = []
        y_pins = []
        self.x_pins = []
        self.y_pins = []
        x_size = int(self.config["board"]["size_x"])
        y_size = int(self.config["board"]["size_y"])
        usable_pins = [4,17,18,27,18,22,23,24,25,5,6,12,13,19,16,26,20,21]
        usable_pins.sort()
        for i in usable_pins[:x_size]:
            x_pins.append(getattr(board, f"D{i}"))
            GPIO.setup(i, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        for i in usable_pins[x_size:y_size+x_size]:
            y_pins.append(getattr(board, f"D{i}"))
        for x_pin in x_pins:
            self.x_pins.append(digitalio.DigitalInOut(x_pin))
            self.x_pins[-1].direction = digitalio.Direction.INPUT
            self.x_pins[-1].Pull = digitalio.Pull.DOWN
        for y_pin in y_pins:
            self.y_pins.append(digitalio.DigitalInOut(y_pin))
            self.y_pins[-1].direction = digitalio.Direction.OUTPUT
        for i in usable_pins[:x_size]:
            GPIO.setup(i, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
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

    # loop for detecting button presses.
    # TODO: add ability to detect button presses
    def thread_loop(self):
        while self.running:
            for i in range(len(self.y_pins)):
                self.y_pins[i].value = True
                self.y_pins[i-1].value = False
                time.sleep(0.001)
                for j, x_pin in enumerate(self.x_pins):
                    if x_pin.value:
                        self.buttons[i][j].pressed = True
                        # print(f"{i} {j}")
                        # self.buttons[i][j].light_up((255,255,255))
                    else:
                        self.buttons[i][j].pressed = False
                        # self.buttons[i][j].light_up((0,0,0))

    def colour_all_leds(self, colour=(255, 255, 255)):
        for button_row in self.buttons:
            for button in button_row:
                button.light_up(colour)

if __name__ == "__main__":
    ButtonBoard()
