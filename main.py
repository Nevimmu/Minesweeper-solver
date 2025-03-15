from game import Game
from board import Board

size = (9, 10)
cellSize = 50
nbBomb = 15

# size = (32, 18)
# cellSize = 30
# nbBomb = 150

screenSize = (size[1] * cellSize, size[0] * cellSize)

board = Board(size, nbBomb)
game = Game(board, screenSize)
game.run()


