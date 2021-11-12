import time


def get_index_from_letter(letter):
    return ord(letter.lower()) - 97


def get_letter_from_index(index):
    return chr(index + 97).upper()


class Stat():
    def __init__(self):
        self.end_time = 0
        self.start_time = 0
        self.evaluation_time = 0
        self.number_of_nodes_at_depth = {}
        self.average_depth = 0
        self.average_recursion_depth = 0


class Logger:

    def __init__(self, n, b, s, t, block_positions, player_1, player_2, board):
        self.stats = []
        self.current_stat = Stat()
        self.filename = "GameTraces/gameTrace-{}{}{}{}.txt".format(n, b, s, t)
        self.n = n
        self.count = 0
        self.board = board
        f = open(self.filename, "w")
        f.write("n={} b={} s={} t={}\n".format(n, b, s, t))
        f.write("blocks={}\n".format(block_positions))
        if player_1['type'] == 'h':
            player_1['type'] = 'HUMAN'
            f.write("\nPlayer 1: HUMAN")
        else:
            player_1['type'] = 'AI'
            f.write("\nPlayer 1: AI d={d} a={a} {e}".format(**player_1))
        if player_2['type'] == 'h':
            player_2['type'] = 'HUMAN'
            f.write("\nPlayer 2: HUMAN\n")
        else:
            player_2['type'] = 'AI'
            f.write("\nPlayer 2: AI d={d} a={a} {e}\n".format(**player_2))
        f.close()
        self.player_1 = player_1
        self.player_2 = player_2

        self.print_board()

    def get_player(self, player):
        if self.player_1['id'] == player:
            return self.player_1
        else:
            return self.player_2

    def print_board(self):
        f = open(self.filename, "a")
        f.write('\n+---+{}\n'.format('---+' * self.n))
        f.write('|   |{}\n'.format(''.join([' {} |'.format(get_letter_from_index(i)) for i in range(self.n)])))
        f.write('+---+{}\n'.format('---+' * self.n))
        for index, row in enumerate([[row[col] for row in self.board] for col in range(self.n)]):
            f.write('| {} |{}\n'.format(index, ''.join([' {} |'.format(r) for r in row])))
            f.write('+---+{}\n'.format('---+' * self.n))
        f.close()

    def compile_move(self, board):
        self.board = board
        f = open(self.filename, "a")
        f.write("\nPlayer {} under {} control plays: {} {}\n".format(self.player['id'], self.player['type'] , get_letter_from_index(self.move[0]), self.move[1]))

        f.write("\ni   Evaluation time: {:.2f}s".format(self.current_stat.end_time - self.current_stat.start_time))
        f.write("\nii  Heuristic evaluations: {:.2f}".format(self.heuristic_score))
        f.write("\niii Evaluations by depth: {}".format(self.current_stat.number_of_nodes_at_depth))
        s = 0
        num = 0
        for i in self.current_stat.number_of_nodes_at_depth:
            num += self.current_stat.number_of_nodes_at_depth[i]
            s += self.current_stat.number_of_nodes_at_depth[i] * i
        f.write("\niv  Average evaluation depth: {:.1f}".format(s/num))

        # TODO: Add ARD

        f.write("\n\nMove #{}".format(self.count))
        f.close()
        self.print_board()

    def create_stat_move(self, player):
        self.count += 1
        self.player = self.get_player(player)
        self.current_stat = Stat()
        self.current_stat.start_time = time.time()

    def visit_end_node_at_depth(self, d):
        if d not in self.current_stat.number_of_nodes_at_depth:
            self.current_stat.number_of_nodes_at_depth[d] = 0
        self.current_stat.number_of_nodes_at_depth[d] += 1

    def end_stat_move(self, move, m):
        self.current_stat.end_time = time.time()
        self.heuristic_score = m
        self.move = move
        self.stats.append(self.current_stat)


    def end_game(self):
        # TODO: Handle end game printing
        return None


