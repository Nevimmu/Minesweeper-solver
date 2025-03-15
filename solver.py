from itertools import combinations

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
						self._mark_safe(_row, _col)
					continue

				if len(hidden) + flagged == cell.getNumAround():
					for _row, _col in hidden:
						self._mark_bomb(_row, _col)
					continue

				
				if len(hidden) + flagged > cell.getNumAround():
					new_subset = (frozenset(hidden), remaining)
					
					subsets_to_add = [new_subset]
					processed = set()
					
					# Check against existing subsets
					for existing in list(self.confirmed_bomb_subsets):
						existing_cells, existing_bombs = existing
						
						# New subset is a SUPERSET of an existing subset
						if existing_cells.issubset(new_subset[0]):
							# Deduce a new subset for the difference
							diff_cells = new_subset[0] - existing_cells
							diff_bombs = new_subset[1] - existing_bombs
							if diff_bombs > 0 and diff_cells:
								new_diff_subset = (frozenset(diff_cells), diff_bombs)
								subsets_to_add.append(new_diff_subset)
							# Remove the existing subset (will be replaced)
							self.confirmed_bomb_subsets.remove(existing)
							processed.add(existing)
						
						# New subset is a SUBSET of an existing subset
						elif new_subset[0].issubset(existing_cells):
							# Deduce a new subset for the difference
							diff_cells = existing_cells - new_subset[0]
							diff_bombs = existing_bombs - new_subset[1]
							if diff_bombs > 0 and diff_cells:
								new_diff_subset = (frozenset(diff_cells), diff_bombs)
								subsets_to_add.append(new_diff_subset)
							# Remove the existing superset
							self.confirmed_bomb_subsets.remove(existing)
							processed.add(existing)
					
					# Add all new subsets (original + deduced differences)
					for subset in subsets_to_add:
						if subset not in self.confirmed_bomb_subsets:
							self.confirmed_bomb_subsets.add(subset)
					
					# Re-add processed subsets that weren't replaced
					for s in processed:
						if s not in self.confirmed_bomb_subsets:
							self.confirmed_bomb_subsets.add(s)

	
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
				
				# 4-1
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
						# Safe cell deduction
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
					

				# Set and subset logic
				applicable_subsets = []
				total_subset_bombs = 0

				# Sort subsets by size (largest first) to prioritize maximal subsets
				sorted_subsets = sorted(self.confirmed_bomb_subsets, key=lambda x: len(x[0]), reverse=True)

				for bomb_subset in sorted_subsets:
					subset_cells, subset_bomb_count = bomb_subset
					
					# Check if subset is valid and not redundant
					if subset_cells.issubset(hidden) and len(subset_cells) != len(hidden):
						# Check if this subset is NOT contained in any already added subset
						is_redundant = any(subset_cells.issubset(added[0]) for added in applicable_subsets)
						
						if not is_redundant:
							# Check if any existing subset is contained in this one (replace if smaller)
							applicable_subsets = [s for s in applicable_subsets if not s[0].issubset(subset_cells)]
							
							applicable_subsets.append(bomb_subset)
							total_subset_bombs += subset_bomb_count
				
				
				# Safe cells
				if applicable_subsets:
					all_subset_cells = set().union(*[s[0] for s in applicable_subsets])
					safe_cells = set(hidden) - all_subset_cells
					remaining_after_subsets = remaining - total_subset_bombs
					
					# Subsets account for ALL bombs -> remaining cells are safe
					if total_subset_bombs == remaining and safe_cells:
						for s_row, s_col in safe_cells:
								self._mark_safe(s_row, s_col)
					
					# Remaining cells MUST be bombs
					elif remaining_after_subsets == len(safe_cells) and safe_cells:
						for r_row, r_col in safe_cells:
							self._mark_bomb(r_row, r_col)

				# Check if the sum of subset bombs matches the cell's remaining bombs
				if total_subset_bombs == remaining and applicable_subsets:
					# Get all cells covered by the subsets
					all_subset_cells = set().union(*[s[0] for s in applicable_subsets])
					
					# Deduce safe cells outside these subsets
					safe_cells = set(hidden) - all_subset_cells
					if safe_cells:
						for s_row, s_col in safe_cells:
							self._mark_safe(s_row, s_col)

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
			for row in range(self.height):
				for col in range(self.width):
					cell: Cell = self.board.getCell(row, col)
					if not cell.getIsClicked():
						self._mark_safe(row, col)
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
		remaining_bombs = self.board.getFlagToFind()
		if remaining_bombs != 1:  # Only run when exactly 1 bomb is left
			return
		possible_bombs = {}  # Maps (row, col) → count of dependencies
		for row in range(self.height):
			for col in range(self.width):
				cell: Cell = self.board.getCell(row, col)
				if not cell.getIsClicked() or cell.getNumAround() == 0:
					continue
				hidden, flagged = self.countHiddenAndFlag(row, col)
				needed = cell.getNumAround() - flagged
				# Only consider cells needing exactly 1 bomb
				if needed == 1:
					for h_row, h_col in hidden:
						possible_bombs[(h_row, h_col)] = possible_bombs.get((h_row, h_col), 0) + 1
		# Find cells with the highest dependency count
		if possible_bombs:
			max_count = max(possible_bombs.values())
			candidates = [pos for pos, count in possible_bombs.items() if count == max_count]
			# Only mark if ONE candidate dominates
			if len(candidates) == 1:
				row, col = candidates[0]
				self._mark_bomb(row, col)
	
	def solve(self):
		while True:
			self.changed = False
			self.confirmed_bomb_subsets.clear()

			self.basicDeduction()
			self.advancedLogic()
			
			if not self.changed: 
				self.mineCountLogic()

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