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
        y_b1 = int(self.config["board"]["size_y"])/2 - 1


        # TODO fix this shiiiit
        for i in range(int(self.config["board"]["size_y"])):
            self.buttons.append([])
            for j in range(int(self.config["board"]["size_x"])):
                if i < 3:
                    self.buttons[i].append(self.Button(self, i + j*y_b1 + j))
                else:
                    temp_i = i-y_b1-1
                    temp_i = temp_i - 2
                    temp_i = -1*temp_i
                    self.buttons[i].append(self.Button(self, 23-temp_i-j*y_b1 - j))

        # creating pins
        x_pins = []
        y_pins = []
        self.x_pins = []
        self.y_pins = []
        x_size = int(self.config["board"]["size_x"])
        y_size = int(self.config["board"]["size_y"])
        usable_pins = [4,18,27,22,23,24,25,5,6,12,19,26,20,21]
        usable_pins.sort()
        for i in usable_pins[:x_size]:
            if i == 6:
                i = 26
            x_pins.append(getattr(board, f"D{i}"))
            GPIO.setup(i, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
            print("xsize: ",i)
        for i in usable_pins[x_size:y_size+x_size]:
            if i == 21:
                i = 24
            y_pins.append(getattr(board, f"D{i}"))
            print("ysize: ",i)
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
            self.activated_time = 0
            self.detected = False

        # Lights up the button to the desired RGB colour
        def light_up(self, color=(255, 255, 255)):
            r, g, b = color
            s = f"{self.led_pos}:{r}:{g}:{b}\n".encode()
            self.button_board.serial.write(s)

        # Activating the button by turning it to a green colour
        def activate(self, colour=(0, 255, 0)):
            self.light_up(colour)
            self.active = True
            self.activated_time = time.time()

        # Deactivates the button by turning the led off
        def deactivate(self):
            self.light_up((0, 0, 0))
            self.active = False
            return time.time() - self.activated_time

    class Speakers:
        def __init__(self):
            self.bad = AudioSegment.from_wav('sounds/bad.wav')
            self.good= AudioSegment.from_wav('sounds/good.wav')

        # Play an mp3 file that is in the sounds folder
        def play_mp3(self, filename):
            f = lambda sound: play(sound)
            sound = AudioSegment.from_mp3('sounds/' + filename)
            t = threading.Thread(target=f, args=(sound,))
            t.start()

        def play_wav(self, filename):
            f = lambda sound: play(sound)
            sound = AudioSegment.from_wav('sounds/' + filename)
            t = threading.Thread(target=f, args=(sound,))
            t.start()
    
        def play_sound(self, sound):
            f = lambda sound: play(sound)
            t = threading.Thread(target=f, args=(sound,))
            t.start()
        
        def play_good(self):
            self.play_sound(self.good)

        def play_bad(self):
            self.play_sound(self.bad)


    # loop for detecting button presses.
    def thread_loop(self):
        while self.running:
            for i in range(len(self.y_pins)):
                # test
                self.y_pins[i].value = True
                self.y_pins[i-1].value = False
                # for i in range(len(self.y_pins)):
                #    self.y_pins[i].value = True
                time.sleep(0.001)
                #TODO
                #time.sleep(0.01)
                #time.sleep(0.1)
                for j, x_pin in enumerate(self.x_pins):
                    if x_pin.value:
                        if j == 2:
                            print(f"test [{i}] [{j}] ")
                        self.buttons[i][j].pressed = True
                    else:
                        self.buttons[i][j].pressed = False

    def colour_all_leds(self, colour=(255, 255, 255)):
        for button_row in self.buttons:
            for button in button_row:
                button.light_up(colour)

if __name__ == "__main__":
    ButtonBoard()
