class Cell():
	def __init__(self, position, hasBomb = False, hasFlag = False, isClicked = False):
		self.position = position
		self.hasBomb = hasBomb
		self.hasFlag = hasFlag
		self.isClicked = isClicked
		self.numAround = 0

	def getHasBomb(self):
		return self.hasBomb
	
	def getHasFlag(self):
		return self.hasFlag
	
	def getIsClicked(self):
		return self.isClicked
	
	def setIsClicked(self, value: bool):
		self.isClicked = value
	
	def setHasBomb(self, value: bool):
		self.hasBomb = value

	def setNeighbors(self, neighbors):
		self.neighbors = neighbors
		self.setNumAround()

	def getNeighbors(self):
		return self.neighbors
	
	def setNumAround(self):
		self.numAround = 0
		for cell in self.neighbors:
			if cell.getHasBomb():
				self.numAround += 1
	
	def getNumAround(self):
		return self.numAround
	
	def toggleFlag(self):
		self.hasFlag = not self.getHasFlag()

	def getPosition(self):
		return self.position