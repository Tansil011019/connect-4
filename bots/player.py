from board import Board

class Player:
    def __init__(self, piece: int):
        """
        Initialize player.

        Args:
            piece: Type of piece the player will use. Only 1 and 2 are valid.
        """
        self.piece = piece

    def get_move(self, board: Board) -> int:
        """
        Given a current state of board (game), return a move.

        Args:
            board: Current state of board (game)
        
        Returns:
            out: Index of column for move, started by zero (max: board.COLUMN_COUNT - 1)
        """
        raise NotImplementedError
