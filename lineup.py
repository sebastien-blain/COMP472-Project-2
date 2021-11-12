import time
import random
import math
from logger import Logger


def get_index_from_letter(letter):
    return ord(letter.lower()) - 97


def get_letter_from_index(index):
    return chr(index + 97).upper()


INF = math.inf


class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3

    WHITE = 'X'
    BLACK = 'O'
    BLOCK = 'B'
    EMPTY = '.'

    # DRAW_DICT = {
    #     WHITE: u'\u25CB',
    #     BLACK: u'\u25CF',
    #     BLOCK: u'\u2612',
    #     EMPTY: ' '
    # }

    DRAW_DICT = {
        WHITE: 'X',
        BLACK: 'O',
        BLOCK: 'B',
        EMPTY: '.'
    }


    def __init__(self, n=3, b=0, s=3, t=10, d1=3, d2=3, b_position=None, recommend=True, a=True, play_mode=('h', 'h')):
        if b_position is None:
            b_position = []
        self.recommend = recommend
        self.n = n
        self.b = b
        self.s = s
        self.t = t
        self.d_min = d1
        self.d_max = d2
        self.b_position = b_position
        self.algo = a
        self.play_mode = play_mode
        self.white_str = self.WHITE * self.s
        self.black_str = self.BLACK * self.s
        self.player_turn = self.WHITE
        self.player_x = self.AI if play_mode[0] == 'ai' else self.HUMAN
        self.player_o = self.AI if play_mode[1] == 'ai' else self.HUMAN
        self.initialize_game()

    def initialize_game(self):
        # Initialize a n by n board filled with EMPTY '.'
        self.current_state = [[self.EMPTY for _ in range(self.n)] for _ in range(self.n)]

        self.changes = None
        # Place the blocks in the grid
        if len(self.b_position) > 0:
            self.initialize_with_determined_blocks()
        elif self.b > 0:
            self.initialize_with_random_blocks()

        self.construct_winning_positions()

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
            self.b_position.append(block)
            empty_tiles.remove(block)
            self.current_state[block[0]][block[1]] = self.BLOCK

    def get_empty_tiles(self):
        return [(x, y) for x in range(self.n) for y in range(self.n) if self.current_state[x][y] == self.EMPTY]

    def draw_board(self):
        print('+---+{}'.format('---+' * self.n))
        print('|   |{}'.format(''.join([' {} |'.format(get_letter_from_index(i)) for i in range(self.n)])))
        print('+---+{}'.format('---+' * self.n))
        for index, row in enumerate([[row[col] for row in self.current_state] for col in range(self.n)]):
            print('| {} |{}'.format(index, ''.join([' {} |'.format(self.DRAW_DICT[r]) for r in row])))
            print('+---+{}'.format('---+' * self.n))

    def is_valid(self, px, py):
        if px < 0 or px > self.n - 1 or py < 0 or py > self.n - 1:
            return False
        elif self.current_state[px][py] != self.EMPTY:
            return False
        else:
            return True

    def construct_winning_positions(self):
        cols = [[] for _ in range(self.n)]
        rows = [[] for _ in range(self.n)]
        fdiag = [[] for _ in range(self.n + self.n - 1)]
        bdiag = [[] for _ in range(len(fdiag))]
        min_bdiag = -self.n + 1
        for row in range(self.n):
            for col in range(self.n):
                cols[col].append((col, row))
                rows[row].append((col, row))
                fdiag[row + col].append((col, row))
                bdiag[row - col - min_bdiag].append((col, row))
        possible_win = self.EMPTY * self.s  # "..."
        # Only keep the lines that are bigger than s and that it is possible to win even with blocker
        self.all_lines = [i for i in cols + rows + fdiag + bdiag if len(i) >= self.s and possible_win in ''.join([self.current_state[j[0]][j[1]] for j in i])]
        pos = {}
        # Construct a dictionary of winning lines for each coordinate
        for row in range(self.n):
            for col in range(self.n):
                if self.current_state[col][row] != self.EMPTY:
                    continue
                # We only store winning positions of empty tiles
                pos[(col, row)] = []
                for line in self.all_lines:
                    if (col, row) in line:
                        pos[(col, row)].append(line)
        self.winning_positions = pos

    def is_end(self):
        if self.changes is None:
            return None

        c, r = self.changes
        for line in self.winning_positions[(c, r)]:
            current_line = ''.join([self.current_state[i[0]][i[1]] for i in line])
            if self.white_str in current_line:
                return self.WHITE
            if self.black_str in current_line:
                return self.BLACK

        # If not full board, return None to continue
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
                return px, py
            else:
                print('The move is not valid! Try again.')

    def switch_player(self):
        if self.player_turn == self.WHITE:
            self.player_turn = self.BLACK
        elif self.player_turn == self.BLACK:
            self.player_turn = self.WHITE
        return self.player_turn

    def heuristic1(self):
        result = 0
        for c in range(self.n):
            for r in range(self.n):
                if self.current_state[c][r] == self.WHITE:
                    result -= len(self.winning_positions[(c, r)])
                elif self.current_state[c][r] == self.BLACK:
                    result += len(self.winning_positions[(c, r)])
        return result

    def heuristic2(self):
        result = 0
        for line in self.all_lines:
            str_line = ''.join([self.current_state[c][r] for c,r in line])
            for i in range(self.s):
                white_str = i * self.WHITE
                black_str = i * self.BLACK
                if white_str in str_line:
                    result -= 10 ** i
                if black_str in str_line:
                    result += 10 ** i
        return result

    def heuristic3(self):
        result = 0
        for line in self.all_lines:
            result += line.count(self.WHITE) - line.count(self.BLACK)
        return result

    # Idea
    # if n tiles have the same player, ex: XX is better than X0
    # if 2 tiles are separated by other player, ex: X0X is good for 0 but X.X is good for X
    # number of current winning lines X - O, ex: if X is in a possible lines that could win, give more points but if O is blocking a lines bad for X

    def heuristic_max(self):
        e2 = self.heuristic1()
        return e2

    def heuristic_min(self):
        e2 = self.heuristic2()
        e1 = self.heuristic1() * 1000
        return e1 + e2

    def minimax_n_ply(self, depth, max=False, heuristic=None, start_time=time.time(), allowed_time=10):
        x = None
        y = None
        value = INF
        if max:
            value = -INF
        temp = self.changes
        result = self.is_end()

        if result == self.WHITE:
            return -1000000000, x, y
        elif result == self.BLACK:
            return 1000000000 - 1, x, y
        elif result == self.EMPTY:
            return 0, x, y

        if depth == 0:  # or if time is running out
            return self.heuristic_min if heuristic is None else heuristic, x, y

        for i in range(0, self.n):
            for j in range(0, self.n):
                if self.current_state[i][j] != self.EMPTY:
                    continue
                if max:
                    self.update_board(i, j, self.BLACK)
                    (v, _, _) = self.minimax_n_ply(depth - 1, max=False)
                    if v > value:
                        value = v
                        x = i
                        y = j
                else:
                    self.update_board(i, j, self.WHITE)
                    (v, _, _) = self.minimax_n_ply(depth - 1, max=True)
                    if v < value:
                        value = v
                        x = i
                        y = j
                self.current_state[i][j] = self.EMPTY
        self.changes = temp
        return value, x, y

    def alphabeta_n_ply(self, depth, alpha=-INF, beta=INF, max=False, heuristic=None, start_time=time.time(), allowed_time=10.0):
        # Minimizing for 'X' and maximizing for 'O'
        x = None
        y = None
        value = -INF if max else INF

        temp = self.changes
        childs = [(i, j) for j in range(0, self.n) for i in range(0, self.n) if self.current_state[i][j] == self.EMPTY]
        childs_len = len(childs)
        for (i, j) in childs:
            if self.current_state[i][j] != self.EMPTY:
                continue
            if max:
                self.update_board(i, j, self.BLACK)
                result = self.is_end()
                if result == self.WHITE:
                    v = -1000000000000
                elif result == self.BLACK:
                    v = 1000000000000
                elif result == self.EMPTY:
                    v = 0
                elif start_time + self.t <= time.time() or depth >= self.d_max:  # or if time is running out
                    heuristic = self.heuristic_min if heuristic is None else heuristic
                    v = heuristic()
                else:
                    (v, _, _) = self.alphabeta_n_ply(depth + 1, alpha, beta, max=False, heuristic=heuristic, start_time=start_time, allowed_time=(allowed_time/childs_len))
                if v > value:
                    value = v
                    x = i
                    y = j
            else:
                self.update_board(i, j, self.WHITE)
                result = self.is_end()
                if result == self.WHITE:
                    v = -1000000000000
                elif result == self.BLACK:
                    v = 1000000000000
                elif result == self.EMPTY:
                    v = 0
                elif start_time + self.t <= time.time() or depth >= self.d_min:  # or if time is running out
                    heuristic = self.heuristic_min if heuristic is None else heuristic
                    v = heuristic()
                else:
                    (v, _, _) = self.alphabeta_n_ply(depth + 1, alpha, beta, max=True, heuristic=heuristic, start_time=start_time, allowed_time=(allowed_time/childs_len))
                if v < value:
                    value = v
                    x = i
                    y = j
            self.current_state[i][j] = self.EMPTY
            if max:
                if value >= beta:
                    self.logger.visit_end_node_at_depth(depth)
                    return value, x, y
                if value > alpha:
                    alpha = value
            else:
                if value <= alpha:
                    self.logger.visit_end_node_at_depth(depth)
                    return value, x, y
                if value < beta:
                    beta = value
        self.logger.visit_end_node_at_depth(depth)
        self.changes = temp
        return value, x, y

    def play(self):
        if self.player_x is None:
            self.player_x = self.HUMAN
        if self.player_o is None:
            self.player_o = self.HUMAN

        player_1 = {
            'id': self.WHITE,
            'type': self.play_mode[0],
            'd': self.d_min,
            'a': self.algo,
            'e': 'fun heuristic'
        }
        player_2 = {
            'id': self.BLACK,
            'type': self.play_mode[1],
            'd': self.d_max,
            'a': self.algo,
            'e': 'sad heuristic'
        }
        self.logger = Logger(self.n, self.b, self.s, self.t, self.b_position, player_1, player_2, self.current_state)
        while True:
            self.draw_board()
            if self.check_end():
                return
            start = time.time()
            self.logger.create_stat_move(self.player_turn)
            if not self.algo:
                if self.player_turn == self.WHITE:
                    (m, x, y) = self.minimax_n_ply(depth=0, max=False)
                else:
                    (m, x, y) = self.minimax_n_ply(depth=0, max=True)
            else:
                if self.player_turn == self.WHITE:
                    (m, x, y) = self.alphabeta_n_ply(depth=0, max=False, heuristic=self.heuristic_min, allowed_time=self.t)
                else:
                    (m, x, y) = self.alphabeta_n_ply(depth=0, max=True, heuristic=self.heuristic_max, allowed_time=self.t)
            self.logger.end_stat_move((x, y), m)
            print("Heuristic value: {}".format(m))
            end = time.time()
            if (self.player_turn == self.WHITE and self.player_x == self.HUMAN) or (
                    self.player_turn == self.BLACK and self.player_o == self.HUMAN):
                if self.recommend:
                    print('Evaluation time: {}s'.format(round(end - start, 7)))
                    print('Recommended move: x = {}, y = {}'.format(get_letter_from_index(x), y))
                (x, y) = self.input_move()
            if (self.player_turn == self.WHITE and self.player_x == self.AI) or (self.player_turn == self.BLACK and self.player_o == self.AI):
                print('Evaluation time: {}s'.format(round(end - start, 7)))
                print('Player {} under AI control plays: x = {}, y = {}'.format(self.DRAW_DICT[self.player_turn], get_letter_from_index(x), y))
            self.update_board(x, y, self.player_turn)
            self.switch_player()
            self.logger.compile_move(self.current_state)


def main():
    g = Game(n=5, s=4, b=0, t=10, d1=10, d2=10, recommend=False, a=True, play_mode=('ai', 'ai'))
    g.play()


if __name__ == "__main__":
    main()
