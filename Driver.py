from lineup import Game

default_params = {
    'n': 3,
    's': 3,
    'b': 0,
    't': 60,
    'd1': 2,
    'd2': 4,
    'recommend': False,
    'force': True,
    'play_mode': ('ai', 'ai')
}

class Driver:

    def __init__(self, r=1, game_params=default_params):
        self.count = 2 * r
        self.game = Game(**game_params)

    
    def run(self):
        for _ in range(self.count):
            self.game.play()
    
if __name__ == "__main__":
    d = Driver(r=2)
    d.run()
