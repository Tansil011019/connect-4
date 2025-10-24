import numpy as np

from board import Board

def possible_moves_to_target(current_board: Board, target_board: Board, verbose: bool = False) -> list[int]:
    curr_board_data = current_board.get_board()
    target_board_data = target_board.get_board()
    difference = curr_board_data != target_board_data
    if np.all(~difference):
        if verbose:
            print("No difference")
        
        return []
    
    conflict_elements = difference & (curr_board_data != current_board.EMPTY)
    if np.any(conflict_elements):
        if verbose:
            print("Conflict exists")
        
        return []

    possible_cols: list[int] = []
    for col in range(current_board.COLUMN_COUNT):
        rows = np.where(difference[:, col])[0].tolist()
        if len(rows) == 0:
            continue

        row = min(rows)
        if target_board_data[row, col] == current_board.CURR_PLAYER:
            possible_cols.append(col)
        
    return possible_cols

def possible_block_moves_to_target(current_board: Board, target_board: Board, verbose: bool = False) -> list[int] | None:
    curr_board_data = current_board.get_board()
    target_board_data = target_board.get_board()
    difference = curr_board_data != target_board_data
    if np.all(~difference):
        if verbose:
            print("No difference")
        
        return None
    
    conflict_elements = difference & (curr_board_data != current_board.EMPTY)
    if np.any(conflict_elements):
        if verbose:
            print("Conflict exists")
        
        return None

    possible_cols: list[int] = []
    for col in range(current_board.COLUMN_COUNT):
        rows = np.where(difference[:, col])[0].tolist()
        if len(rows) == 0:
            continue

        row = min(rows)
        if target_board_data[row, col] == current_board.PREV_PLAYER:
            possible_cols.append(col)
        
    return possible_cols
