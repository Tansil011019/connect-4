import math
import random
import time
from typing import Callable

from board import Board
from bots.evaluation import DefaultEvaluator, EvaluativeBot
from bots.utils import possible_block_moves_to_target, possible_moves_to_target

class GeneticAlgorithmBotFactory:
    def __init__(
            self,
            seed: int | None = None,
            population_size: int = 1000,
            mutation_rate: float = 0.1,
            timeout_duration_seconds: float = 2.5,
            max_iteration: int = 10000,
            verbose: bool = False,
    ):
        self.seed = seed
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.timeout_duration_seconds = timeout_duration_seconds
        self.max_iteration = max_iteration
        self.verbose = verbose

    def __call__(self, piece: int):
        return GeneticAlgorithmBot(
            piece,
            seed=self.seed,
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            timeout_duration_seconds=self.timeout_duration_seconds,
            verbose=self.verbose
        )

class GeneticAlgorithmBot(EvaluativeBot):
    def __init__(
            self,
            piece,
            seed: int | None = None,
            population_size: int = 100,
            mutation_rate: float = 0.1,
            timeout_duration_seconds: float = 2.5,
            max_iteration: int = 10000,
            verbose: bool = False
    ):
        super().__init__(piece)
        self.set_evaluator_type(DefaultEvaluator)
        
        self.rng = random.Random()
        self.rng.seed(seed)
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.timeout_duration_seconds = timeout_duration_seconds
        self.max_iteration = max_iteration
        self.verbose = verbose

        self.target_board: Board | None = None
        self.anti_target_board: Board | None = None

        self.target_board_list: list[Board] = []
        self.anti_target_board_list: list[Board] = []

    def get_move(self, board):
        try:
            best_cols = self.get_possible_best_moves(board)
            worst_cols = self.get_possible_worst_moves(board)
        except ValueError:
            if self.verbose:
                print("Cannot handle this board (return random move instead):")
                board.print_board()
            
            return self.rng.choices([c for c in range(board.COLUMN_COUNT) if board.is_valid_location(c)])

        if self.verbose:
            print("Best:")
            self.target_board_list[0].print_board()
            print(best_cols)
            print("Worst:")
            self.anti_target_board_list[0].print_board()
            print(worst_cols)

        tier_1_cols = [c for c in best_cols if c not in worst_cols]
        if len(tier_1_cols) > 0:
            return self.rng.choice(tier_1_cols)
        
        tier_2_cols = [c for c in range(board.COLUMN_COUNT) if c not in worst_cols and board.is_valid_location(c)]
        if len(tier_2_cols) > 0:
            return self.rng.choice(tier_2_cols)
        
        return self.rng.choice(best_cols)
    
    def get_possible_best_moves(self, board: Board):
        possible_cols: list[int] = []
        while len(possible_cols) == 0:
            i = 0
            removed_count = 0
            while i < len(self.target_board_list):
                local_possible_cols = possible_moves_to_target(
                    board,
                    self.target_board_list[i],
                    verbose=self.verbose
                )
                if len(local_possible_cols) == 0:
                    self.target_board_list.pop(i)
                    removed_count += 1
                else:
                    for col in local_possible_cols:
                        if col not in possible_cols and board.is_valid_location(col):
                            possible_cols.append(col)
                    i += 1

            removed_count = 1 - len(self.target_board_list)
            if removed_count > 0:
                self.populate_best_individuals(board, removed_count)

        return possible_cols
    
    def get_possible_worst_moves(self, board: Board):
        possible_cols: list[int] = []
        while len(possible_cols) == 0:
            i = 0
            removed_count = 0
            while i < len(self.anti_target_board_list):
                local_possible_cols: list[int] = []

                anti_local_possible_cols: list[int] | None = possible_block_moves_to_target(
                    board,
                    self.anti_target_board_list[i],
                    verbose=self.verbose
                )

                if anti_local_possible_cols is not None:
                    for col in range(board.COLUMN_COUNT):
                        if not board.is_valid_location(col):
                            continue

                        if col not in anti_local_possible_cols:
                            local_possible_cols.append(col)

                if len(local_possible_cols) == 0:
                    self.anti_target_board_list.pop(i)
                    removed_count += 1
                else:
                    for col in local_possible_cols:
                        if col not in possible_cols and board.is_valid_location(col):
                            possible_cols.append(col)
                    i += 1

            removed_count = 1 - len(self.anti_target_board_list)
            if removed_count > 0:
                self.populate_worst_individuals(board, removed_count)

        return possible_cols
    
    def populate_best_individuals(self, board: Board, max_result: int = -1):
        n_filled = board.num_slots_filled
        def evaluation_function(next_board: Board):
            score = self.score_position(next_board)
            return math.exp(score / 10)
        
        board_list = self.get_best_individuals(board, evaluation_function, max_result)
        self.target_board_list.extend(board_list)

    def populate_worst_individuals(self, board: Board, max_result: int = -1):
        n_filled = board.num_slots_filled
        def evaluation_function(next_board: Board):
            score = self.score_position(next_board)
            return math.exp(-score / 10)
        
        board_list = self.get_best_individuals(board, evaluation_function, max_result)
        self.anti_target_board_list.extend(board_list)
    
    def get_best_individuals(
            self,
            board: Board,
            evaluation_function: Callable[[Board], float],
            max_result: int = -1
    ):
        # Generate population
        valid_start = [str(i) for i in range(board.COLUMN_COUNT) if board.is_valid_location(i)]
        population: list[str] = []
        while len(population) < self.population_size:
            # Generate single individual
            individual = ""
            while (u := self.rng.random()) < 1 / (len(individual) + 1):
                random_move = self.rng.choice(valid_start)
                individual += str(random_move)
            population.append(individual)

        # Define fitness
        def fitness(individual: str):
            local_board = board.copy_board()
            try:
                for c in individual:
                    if self.is_terminal_node(local_board):
                        break

                    random_move = int(c)
                    local_board.drop_piece(random_move, local_board.CURR_PLAYER)

            except Exception:
                return 1e-10
            else:
                return evaluation_function(local_board)

        fit_enough = False
        timeout = False

        start_time = time.perf_counter()
        iteration = 0
        while (not fit_enough) and (not timeout):
            weights: list[float] = []
            for individual in population:
                w = fitness(individual)
                weights.append(w)

            # Check if any individual is fit enough.
            fit_enough = max(weights) >= math.exp(10)
            if not fit_enough:
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
                iteration += 1
            
            duration = time.perf_counter() - start_time
            if duration > self.timeout_duration_seconds or iteration == self.max_iteration:
                timeout = True

        final_weights: list[float] = []
        for individual in population:
            w = fitness(individual)
            final_weights.append(w)
        
        population_weight_tuples = [(x, y) for x, y in zip(population, final_weights)]
        population_weight_tuples.sort(key=lambda x: x[1], reverse=True)
        if max_result != -1:
            population_weight_tuples = population_weight_tuples[:max_result]

        local_board_list: list[Board] = []
        for best_individual, _ in population_weight_tuples:
            local_board = board.copy_board()
            try:
                for c in best_individual:
                    move = int(c)
                    local_board.drop_piece(move, local_board.CURR_PLAYER)
            except IndexError:
                if self.verbose:
                    print(f"Warning: Cannot handle {best_individual} in this board:")
                    board.print_board()
                    print("(end of warning)")
            else:
                local_board_list.append(local_board)

        if len(local_board_list) == 0:
            raise ValueError("Unexpected state")
        
        return local_board_list
    
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
