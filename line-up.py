import time
import random


def get_index_from_letter(letter):
    return ord(letter.lower()) - 97


def get_letter_from_index(index):
    return chr(index + 97).upper()


class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3

    WHITE = 1
    BLACK = 2
    BLOCK = 9
    EMPTY = 0

    DRAW_DICT = {
        WHITE: u'\u25CB',
        BLACK: u'\u25CF',
        BLOCK: u'\u2612',
        EMPTY: '.'
    }

    def __init__(self, n=3, b=0, s=3, b_position=None, recommend=True):
        self.recommend = recommend
        self.n = n
        self.b = b
        self.s = s
        self.b_position = b_position
        self.initialize_game()

    def initialize_game(self):
        # Initialize a n by n board filled with EMPTY '.'
        self.current_state = [[self.EMPTY for _ in range(self.n)] for _ in range(self.n)]
        # Place the blocks in the grid
        if self.b_position is not None:
            for (x, y) in self.b_position:
                self.current_state[x][y] = self.BLOCK
        elif self.b > 0:
            # Place blocks at random
            empty_tiles = self.get_empty_tiles()
            for i in range(self.b):
                block = empty_tiles[random.randint(0, len(empty_tiles) - 1)]
                empty_tiles.remove(block)
                self.current_state[block[0]][block[1]] = self.BLOCK
        # Player X always plays first
        self.player_turn = self.WHITE

    def get_empty_tiles(self):
        return [(x, y) for x in range(self.n) for y in range(self.n) if self.current_state[x][y] == self.EMPTY]

    def draw_board(self):
        print()
        for y in range(0, self.n):
            for x in range(0, self.n):
                print(F'{self.DRAW_DICT[self.current_state[x][y]]}', end="")
            print()
        print()

    def is_valid(self, px, py):
        if px < 0 or px > self.n - 1 or py < 0 or py > self.n - 1:
            return False
        elif self.current_state[px][py] != self.EMPTY:
            return False
        else:
            return True

    def is_end(self):
        # TODO: Change this function to be more generic and depend on the parameter s (winning line-up size)
        # Vertical win
        for i in range(0, self.n):
            if (self.current_state[0][i] != self.EMPTY and
                    self.current_state[0][i] == self.current_state[1][i] and
                    self.current_state[1][i] == self.current_state[2][i]):
                return self.current_state[0][i]
        # Horizontal win
        for i in range(0, self.n):
            if self.current_state[i] == [self.WHITE, self.WHITE, self.WHITE]:
                return self.WHITE
            elif self.current_state[i] == [self.BLACK, self.BLACK, self.BLACK]:
                return self.BLACK
        # Main diagonal win
        if (self.current_state[0][0] != self.EMPTY and
                self.current_state[0][0] == self.current_state[1][1] and
                self.current_state[0][0] == self.current_state[2][2]):
            return self.current_state[0][0]
        # Second diagonal win
        if (self.current_state[0][2] != self.EMPTY and
                self.current_state[0][2] == self.current_state[1][1] and
                self.current_state[0][2] == self.current_state[2][0]):
            return self.current_state[0][2]
        # Is whole board full?
        for i in range(0, self.n):
            for j in range(0, self.n):
                # There's an empty field, we continue the game
                if self.current_state[i][j] == self.EMPTY:
                    return None
        # It's a tie!
        return '.'

    def check_end(self):
        self.result = self.is_end()
        # Printing the appropriate message if the game has ended
        if self.result is not None:
            if self.result == self.WHITE:
                print('The winner is {}!'.format(self.WHITE))
            elif self.result == self.BLACK:
                print('The winner is {}!'.format(self.BLACK))
            elif self.result == '.':
                print("It's a tie!")
            self.initialize_game()
        return self.result

    def input_move(self):
        while True:
            print(F'Player {self.player_turn}, enter your move:')
            px = input('enter the x coordinate: ')
            try:
                px = int(px)
            except ValueError:
                px = get_index_from_letter(px)

            py = input('enter the y coordinate: ')
            try:
                py = int(py)
            except ValueError:
                py = get_index_from_letter(py)
            if self.is_valid(px, py):
                return px, py
            else:
                print('The move is not valid! Try again.')

    def switch_player(self):
        if self.player_turn == self.WHITE:
            self.player_turn = self.BLACK
        elif self.player_turn == self.BLACK:
            self.player_turn = self.WHITE
        return self.player_turn

    def minimax(self, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        if result == self.WHITE:
            return -1, x, y
        elif result == self.BLACK:
            return 1, x, y
        elif result == '.':
            return 0, x, y
        for i in range(0, self.n):
            for j in range(0, self.n):
                if self.current_state[i][j] == self.EMPTY:
                    if max:
                        self.current_state[i][j] = self.BLACK
                        (v, _, _) = self.minimax(max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = self.WHITE
                        (v, _, _) = self.minimax(max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = self.EMPTY
        return value, x, y

    def alphabeta(self, alpha=-2, beta=2, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        if result == self.WHITE:
            return -1, x, y
        elif result == self.BLACK:
            return 1, x, y
        elif result == self.EMPTY:
            return 0, x, y
        for i in range(0, self.n):
            for j in range(0, self.n):
                if self.current_state[i][j] == self.EMPTY:
                    if max:
                        self.current_state[i][j] = self.BLACK
                        (v, _, _) = self.alphabeta(alpha, beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = self.WHITE
                        (v, _, _) = self.alphabeta(alpha, beta, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = self.EMPTY
                    if max:
                        if value >= beta:
                            return value, x, y
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return value, x, y
                        if value < beta:
                            beta = value
        return value, x, y

    def play(self, algo=None, player_x=None, player_o=None, d1=3, d2=3, t=None):
        if algo is None:
            algo = self.ALPHABETA
        if player_x is None:
            player_x = self.HUMAN
        if player_o is None:
            player_o = self.HUMAN
        while True:
            self.draw_board()
            if self.check_end():
                return
            start = time.time()
            if algo == self.MINIMAX:
                if self.player_turn == self.WHITE:
                    (_, x, y) = self.minimax(max=False)
                else:
                    (_, x, y) = self.minimax(max=True)
            else:  # algo == self.ALPHABETA
                if self.player_turn == self.WHITE:
                    (m, x, y) = self.alphabeta(max=False)
                else:
                    (m, x, y) = self.alphabeta(max=True)
            end = time.time()
            if (self.player_turn == self.WHITE and player_x == self.HUMAN) or (
                    self.player_turn == self.BLACK and player_o == self.HUMAN):
                if self.recommend:
                    print(F'Evaluation time: {round(end - start, 7)}s')
                    print(F'Recommended move: x = {get_letter_from_index(x)}, y = {y}')
                (x, y) = self.input_move()
            if (self.player_turn == self.WHITE and player_x == self.AI) or (self.player_turn == self.BLACK and player_o == self.AI):
                print(F'Evaluation time: {round(end - start, 7)}s')
                print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')
            self.current_state[x][y] = self.player_turn
            self.switch_player()


def main():
    g = Game(n=3, recommend=True)
    g.play(algo=Game.ALPHABETA, player_x=Game.AI, player_o=Game.AI)
    g.play(algo=Game.MINIMAX, player_x=Game.AI, player_o=Game.AI)


if __name__ == "__main__":
    main()
