import os


X_FIELDS = 30
Y_FIELDS = 20
BLOCK_SIZE = 40
WIDTH = BLOCK_SIZE * X_FIELDS
HEIGHT = BLOCK_SIZE * Y_FIELDS
GAME_BOARD_POSITIONS = {(x,y) for x in range(X_FIELDS) for y in range(Y_FIELDS)}
GRAPHICS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}\\graphics"
SOUNDS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}\\sounds"
HIGHSCORE_PATH = ''
HIGHSCORE_PATH_EXPERT = ''
FALLBACK_HIGHSCORE_PATH = f"{os.path.dirname(os.path.abspath(__file__))}\\highscore\\highscores.txt"
FALLBACK_HIGHSCORE_PATH_EXPERT = f"{os.path.dirname(os.path.abspath(__file__))}\\highscore\\highscores_expert.txt"