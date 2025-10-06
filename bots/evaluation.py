from board import Board

class EvaluatableBot:
	def __init__(self, piece: int):
		self.bot_piece = piece
		if self.bot_piece == 1:
			self.opp_piece = 2
		else:
			self.opp_piece = 1
		self.evaluator: Evaluator = DefaultEvaluator(piece)

	def score_position(self, board: Board) -> float:
		return self.evaluator.score_position(board)

	def is_terminal_node(self, board: Board) -> bool:
		"""
		Is the board represents terminal node?

		Args:
			board: The current state of board to analyze

		Returns:
			Boolean.
		"""
		return (
			board.winning_move(self.bot_piece)
			or board.winning_move(self.opp_piece)
			or len(board.get_valid_locations()) == 0
		)
	
	def set_evaluator_type(self, evaluator_type: type):
		if not issubclass(evaluator_type, Evaluator):
			raise ValueError("Not an Evaluator.")
		
		self.evaluator = evaluator_type(self.bot_piece)

class Evaluator:
	def __init__(self, piece: int):
		self.bot_piece = piece
		if self.bot_piece == 1:
			self.opp_piece = 2
		else:
			self.opp_piece = 1

	def score_position(self, board: Board, bot_piece: int, ) -> float:
		"""
		Return the score position of board.

		Args:
			board: The current state of board to analyze

		Returns:
			Score. (generally float, but can be int)
		"""

		raise NotImplementedError

class DefaultEvaluator(Evaluator):
	def evaluate_window(self, board, window):
		score = 0
		if window.count(self.bot_piece) == 4:
			score += 100
		elif window.count(self.bot_piece) == 3 and window.count(board.EMPTY) == 1:
			score += 5
		elif window.count(self.bot_piece) == 2 and window.count(board.EMPTY) == 2:
			score += 2

		if window.count(self.opp_piece) == 3 and window.count(board.EMPTY) == 1:
			score -= 4

		return score

	def score_position(self, board):
		score = 0

		## Score center column
		center_array = [int(i) for i in list(board.get_board()[:, board.COLUMN_COUNT//2])]
		center_count = center_array.count(self.bot_piece)
		score += center_count * 3

		## Score Horizontal
		for r in range(board.ROW_COUNT):
			row_array = [int(i) for i in list(board.get_board()[r,:])]
			for c in range(board.COLUMN_COUNT-3):
				window = row_array[c:c+board.WINDOW_LENGTH]
				score += self.evaluate_window(board, window)

		## Score Vertical
		for c in range(board.COLUMN_COUNT):
			col_array = [int(i) for i in list(board.get_board()[:,c])]
			for r in range(board.ROW_COUNT-3):
				window = col_array[r:r+board.WINDOW_LENGTH]
				score += self.evaluate_window(board, window)

		## Score positive sloped diagonal
		for r in range(board.ROW_COUNT-3):
			for c in range(board.COLUMN_COUNT-3):
				window = [board.get_board()[r+i][c+i] for i in range(board.WINDOW_LENGTH)]
				score += self.evaluate_window(board, window)

		## Score negative sloped diagonal
		for r in range(board.ROW_COUNT-3):
			for c in range(board.COLUMN_COUNT-3):
				window = [board.get_board()[r+3-i][c+i] for i in range(board.WINDOW_LENGTH)]
				score += self.evaluate_window(board, window)

		return score

class FlatEvaluator(Evaluator):
	def score_position(self, board):
		return 0.0
