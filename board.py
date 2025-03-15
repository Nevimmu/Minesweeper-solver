import random
import time

from cell import Cell

class Board():
	def __init__(self, size, nbBombs):
		self.size = size
		self.nbBombs = nbBombs
		self.seed = self.getSeed() 
		print(self.seed)
		self.lost = False
		self.numClicked = 0
		self.numNonBombs = size[0] * size[1] - nbBombs
		self.setBoard()
		self.flagged = 0

	def getSeed(self):
		return int(time.time())

	def setBoard(self):
		self.board = []
		for r in range(self.size[0]):
			row = []
			for c in range(self.size[1]):
				cell = Cell((r, c))
				row.append(cell)
			self.board.append(row)

	def setBombs(self, startPosition):
		seed = self.seed
		# seed = 123
		random.seed(seed)
		self.bombsLocation = []
		# Get the neighbors of the startPosition
		banZone = self.getListOfNeighborsPosition(startPosition)

		for bomb in range(self.nbBombs):
			bombLoc = self.createBomb(banZone)
			cell = self.getCell(bombLoc[0], bombLoc[1])
			cell.setHasBomb(True)
			self.bombsLocation.append(bombLoc)
		
		# self.printBoard()
		self.setNeighbors()

	def createBomb(self, banZone):
		position = (random.randrange(0, self.size[0]), random.randrange(0, self.size[1]))
		if (position not in self.bombsLocation) and (position not in banZone):
			return position
		else:
			return self.createBomb(banZone)

	def getSize(self):
		return self.size
	
	def getNbBombs(self):
		return self.nbBombs
	
	def getCell(self, row, col):
		return self.board[row][col]
	
	def setNeighbors(self):
		for row in range(self.size[0]):
			for col in range(self.size[1]):
				cell = self.getCell(row, col)
				neighbors = self.getListOfNeighbors((row, col))
				cell.setNeighbors(neighbors)

	def getListOfNeighbors(self, index):
		neighbors = []
		for row in range(index[0] - 1, index[0] + 2):
			for col in range(index[1] - 1, index[1] + 2):
				out_of_bound = row < 0 or row >= self.size[0] or col < 0 or col >= self.size[1]
				same = row == index[0] and col == index[1]
				if out_of_bound or same:
					continue
				neighbors.append(self.getCell(row, col))

		return neighbors
	
	def getListOfNeighborsPosition(self, index):
		neighbors = []
		for row in range(index[0] - 1, index[0] + 2):
			for col in range(index[1] - 1, index[1] + 2):
				out_of_bound = row < 0 or row >= self.size[0] or col < 0 or col >= self.size[1]
				same = row == index[0] and col == index[1]
				if out_of_bound or same:
					continue
				neighbors.append((row, col))

		neighbors.append(index)
		return neighbors
	

	def handleClick(self, cell: Cell, flag):
		"""
		Handle the click \n
		True for Flag \n
		False for Reveal
		"""
		if not flag and cell.getHasFlag():
			return
		
		if cell.getIsClicked():
			if cell.getNumAround() == self.countFlags(cell):
				for neighbor in cell.getNeighbors():
					if not neighbor.getIsClicked():
						self.handleClick(neighbor, 0)
		
		if flag and not cell.getIsClicked():
			cell.toggleFlag()
			if cell.getHasFlag():
				self.flagged += 1
				return
			self.flagged -= 1
			return
		
		if not cell.getIsClicked():
			self.numClicked += 1
		
		cell.setIsClicked(True)
		
		if cell.getHasBomb():
			self.lost = True
			return
		
		if cell.getNumAround() != 0:
			return
		
		for neighbor in cell.getNeighbors():
			if not neighbor.getIsClicked():
				self.handleClick(neighbor, 0)

	def getFlagToFind(self):
		return self.nbBombs - self.flagged

	def countFlags(self, cell: Cell):
		flags = 0
		for neighbor in cell.getNeighbors():
			if neighbor.getHasFlag():
				flags += 1
		return flags
	
	def getLost(self):
		return self.lost
	
	def getWon(self):
		return self.numNonBombs == self.numClicked

	def printBoard(self):
		print('--------------\r')
		for row in range(self.size[0]):
			print('\r')
			for col in range(self.size[1]):
				if self.board[row][col].getHasBomb() == True:
					print('x', end='')
					continue
				print('O', end='')
		print('\r--------------')
				

class BoardBis(Board):
	def getSeed(self):
		return 123