from board import Board
from cell import Cell

class Solver():
	def __init__(self, board: Board):
		self.board = board
		self.width = self.board.getSize()[1]
		self.height = self.board.getSize()[0]
		self.confirmed_bomb_subsets = []
		self.changed = True


	def getNeighborsPos(self, row, col):
		'''Return a list of coordinate of all neighbors'''
		cell: Cell = self.board.getCell(row, col)
		neighbor: Cell
		position: list[(int, int)]= []
		for neighbor in cell.getNeighbors():
			position.append(neighbor.getPosition())

		return position


	def countHiddenAndFlag(self, row, col):
		hidden = []
		flagged = 0

		for _row, _col in self.getNeighborsPos(row, col):
			cell: Cell = self.board.getCell(_row, _col)
			if not cell.getIsClicked():
				if cell.getHasFlag():
					flagged += 1
				else:
					hidden.append((_row, _col))
		return hidden, flagged


	def basicDeduction(self):
		for row in range(self.height):
			for col in range(self.width):
				cell: Cell = self.board.getCell(row, col)
				if not cell.getIsClicked() or cell.getNumAround() == 0:
					continue

				hidden, flagged = self.countHiddenAndFlag(row, col)

				if flagged == cell.getNumAround():
					for _row, _col in hidden:
						_cell: Cell = self.board.getCell(_row, _col)
						self.board.handleClick(_cell, False)
						self.changed = True

				if len(hidden) + flagged == cell.getNumAround():
					for _row, _col in hidden:
						_cell: Cell = self.board.getCell(_row, _col)
						self.board.handleClick(_cell, True)
						self.changed = True

				if len(hidden) + flagged > cell.getNumAround():
					self.confirmed_bomb_subsets.append(set(hidden))

	
	def advancedLogic(self):
		for row in range(self.height):
			for col in range(self.width):
				cell: Cell = self.board.getCell(row, col)
				if not cell.getIsClicked() or cell.getNumAround() == 0:
					continue

				hidden, flag = self.countHiddenAndFlag(row, col)


				for _row, _col in self.getNeighborsPos(row, col):
					neighbor: Cell = self.board.getCell(_row, _col)
					if not neighbor.getIsClicked() or neighbor.getNumAround() == 0:
						continue

					neighbor_hidden, neighbor_flag = self.countHiddenAndFlag(_row, _col)

					# Get bomb diff
					bomb_diff = (cell.getNumAround() - flag) - (neighbor.getNumAround() - neighbor_flag)
					extra_hidden = len(set(hidden) - set(neighbor_hidden))

					# Debug

					# print('-------------------')
					# print(f"Cell ({row}, {col}) [{cell.getNumAround()}] has {flag} flags.")
					# print(f"Neighbor ({_row}, {_col}) [{neighbor.getNumAround()}] has {neighbor_flag} flags.")
					# print(f"Hidden around cell ({row}, {col}): {hidden}")
					# print(f"Hidden around neighbor ({_row}, {_col}): {neighbor_hidden}")
					# print(f"Subset match: {set(neighbor_hidden).issubset(set(hidden))}")
					# print(f"Bomb difference: {bomb_diff} | Extra hidden: {extra_hidden}")


					# ✅ If all remaining bombs are in `neighbor_hidden`, `hidden - neighbor_hidden` is SAFE
					if set(neighbor_hidden).issubset(set(hidden)) and bomb_diff == 0:
						for h_row, h_col in set(hidden) - set(neighbor_hidden):
							h_cell: Cell = self.board.getCell(h_row, h_col)
							if not h_cell.getHasFlag() and not h_cell.getIsClicked():
								# print(f'Reveal safe cell at ({h_row}, {h_col})')
								self.board.handleClick(h_cell, False)
								self.changed = True


					# 🚩 If the number of remaining bomb is equal to neighbor_hidden, flag them
					if set(neighbor_hidden).issubset(set(hidden)):
						if bomb_diff == 0 and len(neighbor_hidden) == (neighbor.getNumAround() - neighbor_flag):
							# Flag all in neighbor_hidden
							for h_row, h_col in neighbor_hidden:
								h_cell: Cell = self.board.getCell(h_row, h_col)
								if not h_cell.getHasFlag():
									# print(f'Flagging bomb at ({h_row, h_col})')
									self.board.handleClick(h_cell, True)
									self.changed = True

						elif bomb_diff > 0 and bomb_diff == extra_hidden:
							# Flag all extra bombs outside neighbor_hidden
							for h_row, h_col in set(hidden) - set(neighbor_hidden):
								h_cell: Cell = self.board.getCell(h_row, h_col)
								if not h_cell.getHasFlag():
									# print(f'Flagging extra bomb at ({h_row}, {h_col})')
									self.board.handleClick(h_cell, True)
									self.changed = True
									
						
				# Check if hidden cells match a known bomb subset
				for bomb_subset in self.confirmed_bomb_subsets:
					if bomb_subset.issubset(set(hidden)) and bomb_subset != set(hidden):
						safe_cells = set(hidden) - bomb_subset
						if cell.getNumAround() == flag + 1:
							for s_row, s_col in safe_cells:
								self.board.handleClick(self.board.getCell(s_row, s_col), False)
								self.changed = True


	def singleBombLogic(self):
		"""Checks for cases where exactly one bomb must be in one specific cell."""
		possible_bombs = {}  # Maps (row, col) → count of how many numbers rely on this cell

		for row in range(self.height):
			for col in range(self.width):
				cell: Cell = self.board.getCell(row, col)

				if not cell.getIsClicked() or cell.getNumAround() == 0:
					continue

				hidden, flagged = self.countHiddenAndFlag(row, col)

				if (cell.getNumAround() - flagged) == 1:  # Only run when exactly 1 bomb is left
					for h_row, h_col in hidden:
						if (h_row, h_col) not in possible_bombs:
							possible_bombs[(h_row, h_col)] = 0
						possible_bombs[(h_row, h_col)] += 1  # Track how many numbers depend on this cell
	
	def solve(self):
		while True:
			self.changed = False
			self.confirmed_bomb_subsets = []

			self.basicDeduction()
			self.advancedLogic()

			if self.board.getFlagToFind() == 1:
				self.singleBombLogic()
			
			if not self.changed:
				break

		for row in range(self.height):
			for col in range(self.width):
				cell: Cell = self.board.getCell(row, col)
				if cell.getHasBomb() and cell.getIsClicked():
					print('WRONG')
					return False
				if not cell.getIsClicked() and not cell.getHasFlag():
					return False
				
		return True