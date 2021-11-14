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

    def __init__(self, n=3, b=0, s=3, t=10, d1=3, d2=3, b_position=None, recommend=True, a1=True, a2=True, play_mode=('h', 'h'), heuristic=('e1', 'e2')):
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
        self.algo1 = a1,
        self.algo2 = a2,
        self.play_mode = play_mode
        self.white_str = self.WHITE * self.s
        self.black_str = self.BLACK * self.s
        self.player_turn = self.WHITE
        self.player_x = self.AI if play_mode[0] == 'ai' else self.HUMAN
        self.player_o = self.AI if play_mode[1] == 'ai' else self.HUMAN
        self.player_x_heuristic = (heuristic[0], self.e1) if heuristic[0] == 'e1' else (heuristic[0], self.e2)
        self.player_o_heuristic = (heuristic[1], self.e1) if heuristic[1] == 'e1' else (heuristic[1], self.e2)
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
                self.logger.end_game(self.WHITE)
                print('The winner is {}!'.format(self.WHITE))
            elif self.result == self.BLACK:
                self.logger.end_game(self.BLACK)
                print('The winner is {}!'.format(self.BLACK))
            elif self.result == self.EMPTY:
                self.logger.end_game(self.EMPTY)
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

    def r(self, player_max, player_min):
        return random.randint(0, 1000)

    def e1(self, player_max, player_min):
        # We look if player max has advantage or not
        # Quick heuristic that gives points if there are possible winning lines for maximizing player and removes points for minimizing player
        result = 0
        for line in self.all_lines:
            str_line = ''.join([self.current_state[c][r] for c, r in line])
            for i in range(1, self.s + 1):
                max_str = i * player_max
                min_str = i * player_min
                if max_str in str_line:
                    result += 10 ** i
                if min_str in str_line:
                    result -= 10 ** i
        return result

    def e2(self, player_max, player_min):
        # We look if player max has advantage or not

        result = 0

        # Checks for lines where player_max is about to win or can expend
        min_win1 = player_min * (self.s - 1)
        min_win2 = player_min * (self.s - 2)
        for win_line in self.all_lines:
            # Only keep lines with no blocks that would block a winning line
            str_lines = [i for i in ''.join([self.current_state[c][r] for c, r in win_line]).split(self.BLOCK) if len(i) >= self.s]
            for line in str_lines:
                # Blocks a win from min
                if min_win1+player_max in line or player_max+min_win1 in line:
                    result += 100
                if min_win2+player_max in line or player_max+min_win2 in line:
                    result += 1
                remaining_lines = [i for i in line.split(player_min) if len(i) >= self.s]
                for rem_line in remaining_lines:
                    result += 10 ** rem_line.count(player_max)

        return result

    def minimax_n_ply(self, depth, heuristic, max_depth, max=True, start_time=time.time(), current_time=time.time(), allowed_time=10.0):
        x = None
        y = None
        value = -INF if max else INF
        end = False

        player_max = self.player_turn
        player_min = self.BLACK if self.player_turn == self.WHITE else self.WHITE
        # Look if we are an end node or a leaf node
        result = self.is_end()
        if result == player_max:
            end = True
            value = 1000000000000
        elif result == player_min:
            end = True
            value = -1000000000000
        elif result == self.EMPTY:
            end = True
            value = 0
        elif time.time() - start_time >= self.t or time.time() - start_time >= allowed_time or depth >= max_depth:
            end = True
            value = heuristic(player_max, player_min)
        if end:
            empty_tiles = self.get_empty_tiles()
            empty = empty_tiles[random.randint(0, len(empty_tiles) - 1)] if len(empty_tiles) > 0 else [0, 0]
            self.logger.visit_end_node_at_depth(depth)
            return value, empty[0], empty[1], depth

        temp = self.changes

        childs = [(i, j) for j in range(0, self.n) for i in range(0, self.n) if self.current_state[i][j] == self.EMPTY]
        childs_len = len(childs)
        child_seen = 0
        total_d = 0
        for (i, j) in childs:
            self.update_board(i, j, player_max if max else player_min)
            (v, _, _, d) = self.minimax_n_ply(depth + 1, heuristic, max_depth, max=not max, start_time=start_time, allowed_time=current_time / childs_len)
            child_seen += 1
            total_d += d
            # Restore state
            self.current_state[i][j] = self.EMPTY

            if max:
                if v > value:
                    value = v
                    x = i
                    y = j
            else:
                if v < value:
                    value = v
                    x = i
                    y = j

        self.changes = temp
        if x is None and y is None:
            empty_tiles = self.get_empty_tiles()
            (x, y) = empty_tiles[random.randint(0, len(empty_tiles) - 1)] if len(empty_tiles) > 0 else [0, 0]
        ard = total_d / child_seen if child_seen else depth
        return value, x, y, ard

    def alphabeta_n_ply(self, depth, heuristic, max_depth, alpha=-INF, beta=INF, max=True, start_time=time.time(), current_time=time.time(), allowed_time=10.0):
        # Always try to maximize for the current player
        x = None
        y = None
        value = -INF if max else INF
        end = False

        player_max = self.player_turn
        player_min = self.BLACK if self.player_turn == self.WHITE else self.WHITE
        # Look if we are an end node or a leaf node
        result = self.is_end()
        if result == player_max:
            end = True
            value = 1000000000000
        elif result == player_min:
            end = True
            value = -1000000000000
        elif result == self.EMPTY:
            end = True
            value = 0
        elif time.time() - start_time >= self.t or time.time() - start_time >= allowed_time or depth >= max_depth:
            end = True
            value = heuristic(player_max, player_min)
        if end:
            empty_tiles = self.get_empty_tiles()
            empty = empty_tiles[random.randint(0, len(empty_tiles) - 1)] if len(empty_tiles) > 0 else [0, 0]
            self.logger.visit_end_node_at_depth(depth)
            return value, empty[0], empty[1], depth

        temp = self.changes
        childs = [(i, j) for j in range(0, self.n) for i in range(0, self.n) if self.current_state[i][j] == self.EMPTY]
        childs_len = len(childs)
        child_seen = 0
        total_d = 0
        for (i, j) in childs:
            self.update_board(i, j, player_max if max else player_min)
            (v, _, _, d) = self.alphabeta_n_ply(depth + 1, heuristic, max_depth, alpha=alpha, beta=beta, max=not max, start_time=start_time, allowed_time=current_time/childs_len)
            child_seen += 1
            total_d += d
            # Restore state
            self.current_state[i][j] = self.EMPTY
            # Look for pruning opportunity
            if max:
                if v > value:
                    value = v
                    x = i
                    y = j
                if value >= beta:
                    return value, x, y, total_d / child_seen
                if value > alpha:
                    alpha = value
            else:
                if v < value:
                    value = v
                    x = i
                    y = j
                if value <= alpha:
                    return value, x, y, total_d / child_seen
                if value < beta:
                    beta = value
        self.changes = temp
        if x is None and y is None:
            empty_tiles = self.get_empty_tiles()
            (x, y) = empty_tiles[random.randint(0, len(empty_tiles) - 1)] if len(empty_tiles) > 0 else [0, 0]

        ard = total_d / child_seen if child_seen else depth
        return value, x, y, ard

    def play(self):
        if self.player_x is None:
            self.player_x = self.HUMAN
        if self.player_o is None:
            self.player_o = self.HUMAN

        player_1 = {
            'id': self.WHITE,
            'type': self.play_mode[0],
            'd': self.d_min,
            'a': self.algo1,
            'e': self.player_x_heuristic[0]
        }
        player_2 = {
            'id': self.BLACK,
            'type': self.play_mode[1],
            'd': self.d_max,
            'a': self.algo2,
            'e': self.player_o_heuristic[0]
        }
        self.logger = Logger(self.n, self.b, self.s, self.t, self.b_position, player_1, player_2, self.current_state)
        while True:
            self.draw_board()
            check_end_res = self.check_end()
            if check_end_res:
                return check_end_res
            start = time.time()
            self.logger.create_stat_move(self.player_turn)
            if (self.player_turn == self.WHITE and not self.algo1) or (self.player_turn != self.WHITE and not self.algo2):
                if self.player_turn == self.WHITE:
                    (m, x, y, ard) = self.minimax_n_ply(depth=0, heuristic=self.player_x_heuristic[1], max_depth=self.d_min, max=True, start_time=time.time())
                else:
                    (m, x, y, ard) = self.minimax_n_ply(depth=0, heuristic=self.player_o_heuristic[1], max_depth=self.d_max,  max=True, start_time=time.time())
            else:
                if self.player_turn == self.WHITE:
                    (m, x, y, ard) = self.alphabeta_n_ply(depth=0, heuristic=self.player_x_heuristic[1], max_depth=self.d_min, max=True, start_time=time.time())
                else:
                    (m, x, y, ard) = self.alphabeta_n_ply(depth=0, heuristic=self.player_o_heuristic[1], max_depth=self.d_max,  max=True, start_time=time.time())
            self.logger.end_stat_move((x, y), ard)
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
    g = Game(n=5, s=3, b=10, t=5, d1=6, d2=6, recommend=False, a1=True, a2=True, play_mode=('ai', 'ai'), heuristic=('e2', 'e1'))
    g.play()


if __name__ == "__main__":
    main()
