from board import Board
from cell import Cell

class Solver():
	def __init__(self, board: Board, draw):
		self.board = board
		self.width = self.board.getSize()[1]
		self.height = self.board.getSize()[0]
		self.confirmed_bomb_subsets = set()
		self.changed = True
		self.draw = draw


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
				remaining = cell.getNumAround() - flagged

				if flagged == cell.getNumAround():
					for _row, _col in hidden:
						_cell: Cell = self.board.getCell(_row, _col)
						self.board.handleClick(_cell, False)
						self.draw()
						self.changed = True

				if len(hidden) + flagged == cell.getNumAround():
					for _row, _col in hidden:
						_cell: Cell = self.board.getCell(_row, _col)
						self.board.handleClick(_cell, True)
						self.draw()
						self.changed = True

				if len(hidden) + flagged > cell.getNumAround():
					self.confirmed_bomb_subsets.add((frozenset(hidden), remaining))

	
	def advancedLogic(self):
		for row in range(self.height):
			for col in range(self.width):
				cell: Cell = self.board.getCell(row, col)
				if not cell.getIsClicked() or cell.getNumAround() == 0:
					continue

				hidden, flag = self.countHiddenAndFlag(row, col)
				remaining = cell.getNumAround() - flag

				if not hidden:
					continue

				if not remaining:
					for _row, _col in hidden:
						self._mark_safe(_row, _col)
					continue

				if len(hidden) == remaining:
					for _row, _col in hidden:
						self._mark_bomb(_row, _col)
					continue
				
				# New: Debug header
				for _row, _col in self.getNeighborsPos(row, col):
					neighbor: Cell = self.board.getCell(_row, _col)
					if not neighbor.getIsClicked() or neighbor.getNumAround() == 0:
						continue

					n_hidden, n_flag = self.countHiddenAndFlag(_row, _col)
					n_remaining = neighbor.getNumAround() - n_flag
					
					shared = set(hidden) & set(n_hidden)
					if not shared:
						continue  # No shared cells to analyze

					# Calculate maximum bombs that can be placed in shared area
					max_for_cell = min(remaining, len(shared))
					max_for_neighbor = min(n_remaining, len(shared))
					max_possible = min(max_for_cell, max_for_neighbor)
					
					# Calculate required bombs from shared area
					required_cell = remaining - (len(hidden) - len(shared))
					required_neighbor = n_remaining - (len(n_hidden) - len(shared))
					required_from_shared = max(required_cell, required_neighbor, 0)
				

					# Conflict detection
					if required_from_shared == max_possible:
						# New: Safe cell deduction
						if remaining - required_from_shared == 0:
							safe_cells = set(hidden) - shared
							for r, c in safe_cells:
								self._mark_safe(r, c)

						bombs_needed_outside = remaining - required_from_shared
						
						# Get non-shared cells for original cell
						non_shared = set(hidden) - shared
						
						if bombs_needed_outside == len(non_shared):
							for r, c in non_shared:
								self._mark_bomb(r, c)
					
				# Check if hidden cells match a known bomb subset
				for bomb_subset in self.confirmed_bomb_subsets:
					if bomb_subset[0].issubset(set(hidden)) and bomb_subset[0] != set(hidden):
						safe_cells = set(hidden) - bomb_subset[0]
						if cell.getNumAround() == flag + 1:
							for s_row, s_col in safe_cells:
								self.board.handleClick(self.board.getCell(s_row, s_col), False)
								self.draw()
								self.changed = True


	def _mark_safe(self, row, col):
			cell: Cell = self.board.getCell(row, col)
			if not cell.getHasFlag() and not cell.getIsClicked():
					self.board.handleClick(cell, False)
					self.draw()
					self.changed = True

	def _mark_bomb(self, row, col):
			cell: Cell = self.board.getCell(row, col)
			if not cell.getHasFlag():
					self.board.handleClick(cell, True)
					self.draw()
					self.changed = True

	def mineCountLogic(self):
		remaining_bombs = self.board.getFlagToFind()
		if remaining_bombs <= 0:
			return
		# Get all hidden cells and confirmed subsets
		all_hidden = set()
		for row in range(self.height):
			for col in range(self.width):
				cell = self.board.getCell(row, col)
				if not cell.getIsClicked() and not cell.getHasFlag():
					all_hidden.add((row, col))
		# Convert confirmed_bomb_subsets to list of (cells, count)
		subsets = [ (set(s[0]), s[1]) for s in self.confirmed_bomb_subsets ]
		# Find non-overlapping combinations that sum to remaining bombs
		from itertools import combinations
		valid_combinations = []
		
		# Check combinations of increasing size
		for r in range(1, len(subsets) + 1):
			for combo in combinations(subsets, r):
				total = sum(c[1] for c in combo)
				if total != remaining_bombs:
					continue
						
				# Check if all subsets in combo are disjoint
				union = set()
				valid = True
				for s in combo:
					if union & s[0]:
						valid = False
						break
					union |= s[0]
				if valid:
					valid_combinations.append(union)
		# If valid combination found, mark other cells as safe
		for union in valid_combinations:
			safe_cells = all_hidden - union
			if safe_cells:
				for r, c in safe_cells:
					self._mark_safe(r, c)
				return  # Stop after first valid combination

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

		# Now, check if any cell is the only possible bomb for multiple numbers
		for (row, col), count in possible_bombs.items():
			if count > 1:  # If multiple numbers depend on this cell, it must be a bomb
				cell: Cell = self.board.getCell(row, col)
				if not cell.getHasFlag():
					self.board.handleClick(cell, True)  # Flag the bomb
					self.draw()
					self.changed = True
	
	def solve(self):
		while True:
			self.changed = False
			self.confirmed_bomb_subsets.clear()

			self.basicDeduction()
			self.advancedLogic()
			
			if not self.changed: 
				self.mineCountLogic()

			if not self.changed and self.board.getFlagToFind() == 1:
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