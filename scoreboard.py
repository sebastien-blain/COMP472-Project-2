from config import configs
import importlib
lineup = importlib.import_module('line-up')
Game = lineup.Game

default_params = {
    'n': 5,
    's': 3,
    'b': 10,
    't': 5,
    'd1': 6,
    'd2': 6,
    'recommend': False,
    'a1': True,
    'a2': True,
    'play_mode': ('ai', 'ai'),
    'heuristic': ('e1', 'e2')
}

class Scoreboard:

    def __init__(self, r=1, game_params=default_params):
        self.filename = "Scoreboards/scoreboard.txt"
        self.game_params = game_params
        self.og_heuristic = (game_params['heuristic'][0], game_params['heuristic'][1])
        self.count = 2 * r
        self.write_params()

    def write_params(self):
        f = open(self.filename, "a")
        f.write("#############\nSERIE START\n#############\n")
        f.write("n={} b={} s={} t={}\n".format(self.game_params['n'], self.game_params['b'], self.game_params['s'], self.game_params['t']))
        f.write("\nPlayer 1: d={} a={}".format(self.game_params['d1'], self.game_params['a1']))
        f.write("\nPlayer 2: d={} a={}\n".format(self.game_params['d2'], self.game_params['a2']))
        f.write("\n{} games\n".format(self.count))
        f.close()

    def swap_params(self):
        self.game_params['d1'], self.game_params['d2'] = self.game_params['d2'], self.game_params['d1']
        self.game_params['a1'], self.game_params['a2'] = self.game_params['a2'], self.game_params['a1']
        self.game_params['heuristic'] = (self.game_params['heuristic'][1], self.game_params['heuristic'][0])

    def end_game(self):
        count = self.game.logger.count
        stats = self.game.logger.stats

        avg_time = 0
        heuristic_count = 0
        total_states = 0
        avg_eval_depth = 0
        total_states_at_each_depth = {}
        avg_recursion_depth = 0
        total_moves = count
        for stat in stats:
            avg_time += stat.end_time - stat.start_time
            avg_recursion_depth += stat.ard
            heuristic_count += stat.heuristic_count
            total_states += sum([stat.eval_at_depth[i] for i in stat.eval_at_depth])

            s = 0
            num = 0
            for depth, value in stat.eval_at_depth.items():
                s += depth * value
                num += value
            avg_eval_depth += s/num

            for i in stat.eval_at_depth:
                if i not in total_states_at_each_depth:
                    total_states_at_each_depth[i] = 0
                total_states_at_each_depth[i] += stat.eval_at_depth[i]

        avg_time /= len(stats)
        avg_recursion_depth /= len(stats)
        avg_eval_depth /= len(stats)

        return {
            "avg_time": avg_time,
            "total_states": heuristic_count,
            "total_states_at_each_depth": total_states_at_each_depth,
            "avg_eval_depth": avg_eval_depth,
            "avg_recursion_depth": avg_recursion_depth,
            "total_moves": total_moves
        }

    def run(self):
        res = {
            "p1_winner": 0,
            "p2_winner": 0,
            "avg_time": 0,
            "total_states": 0,
            "total_states_at_each_depth": {},
            "avg_eval_depth": 0,
            "avg_recursion_depth": 0,
            "total_moves": 0
        }

        for i in range(0, self.count):
            self.game = Game(**self.game_params)            
            result = self.game.play()

            if result == self.game.WHITE and i%2 == 0:
                res['p1_winner'] += 1
            if result == self.game.BLACK and i%2 == 0:
                res['p2_winner'] += 1
            if result == self.game.BLACK and i%2 != 0:
                res['p1_winner'] += 1
            if result == self.game.WHITE and i%2 != 0:
                res['p2_winner'] += 1

            end_res = self.end_game()

            for k, v in end_res.items():
                if type(v) is dict:
                    for k1, v1 in v.items():
                        res[k][k1] = res[k][k1] + v1 if k1 in res[k] else v1
                else:
                    res[k] += v

            self.swap_params()
        for k1, v1 in res['total_states_at_each_depth'].items():
            res['total_states_at_each_depth'][k1] = v1 / self.count

        f = open(self.filename, "a")
        f.write("\nTotal wins for heuristic {}: {} ({:.2f}%)".format(self.og_heuristic[0], res['p1_winner'], (res['p1_winner']/self.count)*100))
        f.write("\nTotal wins for heuristic {}: {} ({:.2f}%)\n".format(self.og_heuristic[1], res['p2_winner'], (res['p2_winner']/self.count)*100))

        f.write("\ni    Average evaluation time: {:.2f}s".format(res['avg_time']/self.count))
        f.write("\nii   Total heuristic evaluations: {}".format(res['total_states']/self.count))
        f.write("\niii  Evaluations by depth: {}".format(res['total_states_at_each_depth']))
        f.write("\niv   Average evaluation depth: {:.1f}".format(res['avg_eval_depth']/self.count))
        f.write("\nv    Average recursion depth: {:.1f}".format(res['avg_recursion_depth']/self.count))
        f.write("\nvi   Average moves per game: {:.2f}\n\n".format(res['total_moves']/self.count))
        f.close()

if __name__ == "__main__":
    for c in configs:
        d = Scoreboard(r=5, game_params=c)
        d.run()
