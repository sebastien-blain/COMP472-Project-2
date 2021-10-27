import time
import random
import numpy as np


def get_index_from_letter(letter):
    return ord(letter.lower()) - 97


def get_letter_from_index(index):
    return chr(index + 97).upper()


class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3
    COUNT = 0

    WHITE = 'X'
    BLACK = 'O'
    BLOCK = 'B'
    EMPTY = '.'

    DRAW_DICT = {
        WHITE: u'\u25CB',
        BLACK: u'\u25CF',
        BLOCK: u'\u2612',
        EMPTY: ' '
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
        # self.current_state = np.empty((self.n, self.n), dtype=str)
        # self.current_state.fill(self.EMPTY)
        self.current_state = [[self.EMPTY for _ in range(self.n)] for _ in range(self.n)]
        self.changes = None
        # Place the blocks in the grid
        if self.b_position is not None:
            self.initialize_with_determined_blocks()
        elif self.b > 0:
            self.initialize_with_random_blocks()

        self.player_turn = self.WHITE

    def update_board(self, x, y, player):
        self.current_state[x][y] = player
        self.changes = (x, y)

    def initialize_with_determined_blocks(self):
        for (x, y) in self.b_position:
            self.current_state[x][y] = self.BLOCK

    def initialize_with_random_blocks(self):
        empty_tiles = self.get_empty_tiles()
        for i in range(self.b):
            block = empty_tiles[random.randint(0, len(empty_tiles) - 1)]
            empty_tiles.remove(block)
            self.current_state[block[0]][block[1]] = self.BLOCK

    def get_empty_tiles(self):
        return [(x, y) for x in range(self.n) for y in range(self.n) if self.current_state[x][y] == self.EMPTY]

    def draw_board(self):
        print('+---+{}'.format('---+' * self.n))
        print('|   |{}'.format(''.join([' {} |'.format(get_letter_from_index(i)) for i in range(self.n)])))
        print('+---+{}'.format('---+' * self.n))
        for index, row in enumerate([self.current_state[:][i] for i in range(self.n)]):
            print('| {} |{}'.format(index, ''.join([' {} |'.format(self.DRAW_DICT[r]) for r in row])))
            print('+---+{}'.format('---+' * self.n))

    def is_valid(self, px, py):
        if px < 0 or px > self.n - 1 or py < 0 or py > self.n - 1:
            return False
        if self.current_state[py][px] != self.EMPTY:
            return False
        else:
            return True

    def is_end(self):
        if self.changes is None:
            return None

        white_str = str(self.WHITE) * self.s
        black_str = str(self.BLACK) * self.s

        r, c = self.changes
        horizontal = ''.join(self.current_state[r])
        if white_str in horizontal:
            return self.WHITE
        if black_str in horizontal:
            return self.BLACK

        vertical = ''.join([i[c] for i in self.current_state])
        if white_str in vertical:
            return self.WHITE
        if black_str in vertical:
            return self.BLACK

        if self.s != self.n or r == c or r+c == self.n-1:
            diag1 = ''.join(np.diagonal(self.current_state, offset=(c - r)).tolist())
            if white_str in diag1:
                return self.WHITE
            if black_str in diag1:
                return self.BLACK

            diag2 = ''.join(np.diagonal(np.rot90(self.current_state), offset=-self.n + (c + r) + 1).tolist())        
            if white_str in diag2:
                return self.WHITE
            if black_str in diag2:
                return self.BLACK

        # Full board
        if any( self.EMPTY in sublist for sublist in self.current_state):
            return None

        # It's a tie!
        return self.EMPTY

    def check_end(self):
        self.result = self.is_end()
        # Printing the appropriate message if the game has ended
        if self.result is not None:
            if self.result == self.WHITE:
                print('The winner is {}!'.format(self.WHITE))
            elif self.result == self.BLACK:
                print('The winner is {}!'.format(self.BLACK))
            elif self.result == self.EMPTY:
                print("It's a tie!")
            self.initialize_game()
        return self.result

    def input_move(self):
        while True:
            print('Player {}, enter your move:'.format(self.player_turn))
            px = input('enter the x coordinate: ')
            try:
                px = int(px)
            except ValueError:
                if len(px.strip()) == 0:
                    px = 'z'
                px = get_index_from_letter(px)

            py = input('enter the y coordinate: ')
            try:
                py = int(py)
            except ValueError:
                if len(py.strip()) == 0:
                    py = 'z'
                py = get_index_from_letter(py)
            if self.is_valid(px, py):
                return py, px
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
        temp = self.changes
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        self.COUNT += 1
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
                        self.update_board(i, j, self.BLACK)
                        (v, _, _) = self.minimax(max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.update_board(i, j, self.WHITE)
                        (v, _, _) = self.minimax(max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = self.EMPTY
        self.changes = temp
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
            print(self.COUNT-1)
            self.COUNT = 0
            end = time.time()
            if (self.player_turn == self.WHITE and player_x == self.HUMAN) or (
                    self.player_turn == self.BLACK and player_o == self.HUMAN):
                if self.recommend:
                    print('Evaluation time: {}s'.format(round(end - start, 7)))
                    print('Recommended move: x = {}, y = {}'.format(get_letter_from_index(x), y))
                (x, y) = self.input_move()
            if (self.player_turn == self.WHITE and player_x == self.AI) or (self.player_turn == self.BLACK and player_o == self.AI):
                print('Evaluation time: {}s'.format(round(end - start, 7)))
                print('Player {} under AI control plays: x = {}, y = {}'.format(self.player_turn, x, y))
            self.update_board(x, y, self.player_turn)
            self.switch_player()


def main():
    g = Game(n=3,s=3, recommend=False)
    # g.play(algo=Game.ALPHABETA, player_x=Game.AI, player_o=Game.AI)
    g.play(algo=Game.MINIMAX, player_x=Game.AI, player_o=Game.AI)


if __name__ == "__main__":
    main()
