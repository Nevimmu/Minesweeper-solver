import pygame
import os
import time

from board import Board
from board import BoardBis
from cell import Cell
from solver import Solver

class Game():
	def __init__(self, board, screenSize):
		self.board = board
		self.screenSize = screenSize
		self.cellSize = self.screenSize[0] // self.board.getSize()[1], self.screenSize[1] // self.board.getSize()[0]
		self.loadImages()

	def run(self):
		pygame.init()
		icon = pygame.image.load('images/flag.png')
		pygame.display.set_icon(icon)
		pygame.display.set_caption('Minesweeper solver')
		self.screen = pygame.display.set_mode(self.screenSize)
		running = True
		started = False

		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				if event.type == pygame.MOUSEBUTTONDOWN:
					button = event.button
					if button == 1 or button == 3:
						position = pygame.mouse.get_pos()
						if started == False:
							self.board.setBombs(self.getIndex(position))
							solver = Solver(self.board, self.draw)
							started = True
						flag = True if button == 3 else False
						self.handleClick(position, flag)
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_r:
						self.board = Board(self.board.getSize(), self.board.getNbBombs())
						started = False
					if event.key == pygame.K_s:
						canSolve = solver.solve()
						if canSolve:
							print('No guess')
						else:
							print('Guess :(')
						pass
					if event.key == pygame.K_a:
						self.board = BoardBis(self.board.getSize(), self.board.getNbBombs())
						started = False
					if event.key == pygame.K_t:
						solver.basicDeduction()
					if event.key == pygame.K_y:
						solver.advancedLogic()
					if event.key == pygame.K_u:
						solver.mineCountLogic()

			self.draw()
			if self.board.getWon():
				print('you won')
				time.sleep(.5)
				self.board = Board(self.board.getSize(), self.board.getNbBombs())
				started = False
		pygame.quit()

	def draw(self):
		topLeft = (0, 0)
		for row in range(self.board.getSize()[0]):
			for col in range(self.board.getSize()[1]):
				cell = self.board.getCell(row, col)
				image = self.getImage(cell)
				self.screen.blit(image, topLeft)
				topLeft = topLeft[0] + self.cellSize[0], topLeft[1]
			topLeft = 0, topLeft[1] + self.cellSize[1]
		pygame.display.flip()

	def getImage(self, cell: Cell):
		string = 'empty-block'
		if cell.getIsClicked():
			string = 'bomb-at-clicked-block' if cell.getHasBomb() else str(cell.getNumAround())
		if cell.getHasFlag():
			string = 'flag'

		
		if self.board.getLost():
			if cell.getHasBomb() and not cell.getIsClicked():
				string = 'unclicked-bomb'
			if cell.getHasFlag() and not cell.getHasBomb():
				string = 'wrong-flag'

		return self.images[string]

	def loadImages(self):
		self.images = {}
		for fileName in os.listdir('images'):
			image = pygame.image.load(f'images/{fileName}')
			image = pygame.transform.scale(image, self.cellSize)
			self.images[fileName.split('.')[0]] = image

	def handleClick(self, position, flag):
		if self.board.getLost():
			return
		index = self.getIndex(position)
		cell = self.board.getCell(index[0], index[1])
		self.board.handleClick(cell, flag)

	def getIndex(self, position):
		return position[1] // self.cellSize[1], position[0] // self.cellSize[0]
	