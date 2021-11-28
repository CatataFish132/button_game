class NeoPixel(list):

    def __init__(self, *args, **kwargs):
        super().__init__()
        for i in range(int(args[1])):
            self.append((0, 0, 0))

    def fill(self, colour):
        for i in range(len(self)):
            self.__setitem__(i, colour)
