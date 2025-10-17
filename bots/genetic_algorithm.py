import math
import random
import time

import numpy as np

from board import Board
from bots.evaluation import DefaultEvaluator
from bots.onesteplook import OneStepLookAheadBot
from bots.player import Player
from bots.random import RandomBot

class GeneticAlgorithmBotFactory:
    def __call__(self, *args, **kwds):
        return GeneticAlgorithmBot(*args, **kwds)

class GeneticAlgorithmBot(Player):
    def __init__(self, piece, seed: int = 120):
        super().__init__(piece)
        self.rng = random.Random()
        self.rng.seed(seed)
        self.evaluator = DefaultEvaluator(piece)
        self.population_size = 100  # Ganti nanti ke 100.
        self.mutation_rate = 0.1
        self.timeout_duration_seconds = 1.0

        self.best_individual = ""
        self.target_board: Board | None = None

    def get_move(self, board, verbose: bool = False):
        solution = -1
        while solution == -1:
            if self.target_board is None:
                if verbose:
                    print("No target board")
                self.update_best_individual(board)
                continue
                
            curr_board_data = board.get_board()
            target_board_data = self.target_board.get_board()
            difference = curr_board_data != target_board_data
            if np.all(~difference):
                if verbose:
                    print("No difference")
                self.update_best_individual(board)
                continue
            
            conflict_elements = difference & (curr_board_data != board.EMPTY)
            if np.any(conflict_elements):
                if verbose:
                    print("Conflict exists")
                self.update_best_individual(board)
                continue

            possible_cols: list[int] = []
            for col in range(board.COLUMN_COUNT):
                rows = np.where(difference[:, col])[0].tolist()
                if len(rows) == 0:
                    continue

                row = min(rows)
                if target_board_data[row, col] == board.CURR_PLAYER:
                    possible_cols.append(col)

            if len(possible_cols) == 0:
                if verbose:
                    print("No possible move")
                self.update_best_individual(board)
                continue

            solution = self.rng.choice(possible_cols)

        return solution

    def update_best_individual(self, board: Board):
        # Generate population
        population: list[str] = []
        for _ in range(self.population_size):
            # Generate single individual
            individual = ""
            while (u := self.rng.random()) < 1 / (len(individual) + 1):
                random_move = self.rng.randint(0, board.COLUMN_COUNT - 1)
                individual += str(random_move)
            population.append(individual)

        # Define fitness
        def fitness(individual: str):
            local_board = board.copy_board()
            try:
                for c in individual:
                    random_move = int(c)
                    local_board.drop_piece(random_move, local_board.CURR_PLAYER)
            except Exception:
                return 0.0
            else:
                score = self.evaluator.score_position(local_board)
                return math.exp(score / 10)

        fit_enough = False
        timeout = False

        start_time = time.perf_counter()
        while (not fit_enough) and (not timeout):
            # Get weights
            weights: list[float] = []
            for individual in population:
                w = fitness(individual)
                weights.append(w)

            population_2: list[str] = []
            for _ in range(len(population)):
                parent_1, parent_2 = self.rng.choices(population, weights, k=2)
                
                # Reproduce
                n = min(len(parent_1), len(parent_2))
                c = self.rng.randint(1, n)
                child = parent_1[:c] + parent_2[c:]

                if self.rng.random() < self.mutation_rate:
                    # Mutate
                    random_index = self.rng.randint(0, len(child) - 1)
                    random_move = self.rng.randint(0, board.COLUMN_COUNT - 1)
                    child = child[:random_index] + str(random_move) + child[random_index+1:]
                
                population_2.append(child)

            population = population_2

            # Check if any individual is fit enough.
            fit_enough = any(
                fitness(individual) >= math.exp(10)
                for individual in population
            )

            duration = time.perf_counter() - start_time
            if duration > self.timeout_duration_seconds:
                timeout = True

            # print(max(fitness(individual) for individual in population))
        
        self.best_individual = max(population, key=fitness)

        local_board = board.copy_board()
        for c in self.best_individual:
            move = int(c)
            local_board.drop_piece(move, local_board.CURR_PLAYER)
        
        self.target_board = local_board
    
if __name__ == "__main__":
    board = Board(1)
    bot_1 = GeneticAlgorithmBot(board.PLAYER1_PIECE, seed=None)
    bot_2 = GeneticAlgorithmBot(board.PLAYER2_PIECE, seed=None)
    
    while board.search_result(board.PLAYER1_PIECE) is None:
        board.print_board()
        print("Turn:", board.CURR_PLAYER)
        if board.CURR_PLAYER == board.PLAYER1_PIECE:
            move = bot_1.get_move(board)
            board.drop_piece(move, board.PLAYER1_PIECE)
        else:
            move = bot_2.get_move(board)
            board.drop_piece(move, board.PLAYER2_PIECE)
    board.print_board()
    print(board.search_result(board.PLAYER1_PIECE))
