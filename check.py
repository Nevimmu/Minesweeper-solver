import pyautogui
import time
import win32api, win32con

from board import Board
from cell import Cell

class Check():
	def __init__(self, board: Board):
		self.board: Board = board
		self.width = self.board.getSize()[1]
		self.height = self.board.getSize()[0]
		self.startX = 1430 - ((self.width//2) * 32)
		self.startY = 180
		self.optionStartX = 1200
		self.optionStartY = self.startY + self.height * 32


	def click(self, x, y):
		win32api.SetCursorPos((x, y))
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

	def keyPress(self, key):
		pyautogui.keyDown(key)
		time.sleep(.1)
		pyautogui.keyUp(key)

	def getCellStatus(self, row, col):
		cell: Cell = self.board.getCell(row, col)

	def options(self, status):
		match status:
			case '1':
				offset = 0
			case '2':
				offset = 1
			case '3':
				offset = 2
			case '4':
				offset = 3
			case '5':
				offset = 4
			case '6':
				offset = 5
			case '7':
				offset = 6
			case '8':
				offset = 7
			case '0':
				offset = 8
			case 'True':
				offset = 9

		self.click(self.optionStartX + (40 * offset), self.optionStartY)
		

	def checkBoard(self):
		x, y = pyautogui.position()
		# Reset board
		self.click(1000, 700)
		self.keyPress('F2')
		for row in range(self.height):
			for col in range(self.width):
				cell: Cell = self.board.getCell(row, col)

				if cell.getHasFlag():
					self.options(str(cell.getHasFlag()))
					self.click(self.startX + (col * 32), self.startY + (row * 32))

				if not cell.getIsClicked():
					continue

				self.options(str(cell.getNumAround()))
				self.click(self.startX + (col * 32), self.startY + (row * 32))

		# Find next move
		self.click(1373, 150)

		# Return to start
		self.click(x, y)
		self.click(x, y)
