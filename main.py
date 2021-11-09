from button_board import ButtonBoard


class Game:
    def __init__(self):
        self.board = ButtonBoard()

    def game_loop(self, difficulty):
        pass

    def main_menu(self):
        difficulty = 0
        running = True
        while running:
            pass
        self.game_loop(difficulty)


def main():
    Game()


if __name__ == "__main__":
    main()
