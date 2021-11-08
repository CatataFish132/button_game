from pydub import AudioSegment
from pydub.playback import play


class Board:
    def __init__(self):
        self.speaker = self.Speakers()
        self.buttons = []

    class Button:
        def __init__(self):
            pass

        def light_up(self, color=(255, 255, 255)):
            pass

    class Speakers:
        def __init__(self):
            pass

        def play_mp3(self, filename):
            sound = AudioSegment.from_mp3('sounds/'+filename)
            play(sound)


