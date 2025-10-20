import math
import random
import time
from functools import partial

import numpy as np

from board import Board
from bots.evaluation import DefaultEvaluator
from bots.onesteplook import OneStepLookAheadBot
from bots.player import Player
from bots.random import RandomBot
from bots.utils import possible_moves_to_target


class SimulatedAnnealingBot(Player):
    @classmethod
    def factory(cls, *args, **kwargs):
        return partial(cls, *args, **kwargs)

    def __init__(self, piece, *, 
                 seed: int = 120,
                 initial_temperature: float = 100.0,
                 cooling_rate: float = 0.95,
                 min_temperature: float = 0.1,
                 max_iteration: int = 20,
                 timeout_duration_seconds: float = 1.0,
                 max_plan_length: int = 10,
                 verbose: bool = False):
        
        super().__init__(piece)
        self.rng = random.Random()
        self.rng.seed(seed)
        self.evaluator = DefaultEvaluator(piece)
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        self.max_iteration = max_iteration
        self.timeout_duration_seconds = timeout_duration_seconds
        self.max_plan_length = max_plan_length

        self.best_plan: list[int] = []
        self.target_board: Board | None = None
        self.verbose = verbose

    def summon_new_plan(self, board: Board, plan: list[int]) -> list[int]:
        # generate new plan by modifying current plan slightly
        new_plan = plan.copy()
        if len(new_plan) == 0:
            # if current plan is empty, add a random move
            new_plan.append(self.rng.randint(0, board.COLUMN_COUNT - 1))
        else:
            choice = self.rng.random()
            if choice < 0.7 and len(new_plan) > 0:
                # Mutate one move
                i = self.rng.randint(0, len(new_plan) - 1)
                new_plan[i] = self.rng.randint(0, board.COLUMN_COUNT - 1)

            elif choice < 0.85 and len(new_plan) < self.max_plan_length:
                # Insert new move
                i = self.rng.randint(0, len(new_plan))
                new_plan.insert(i, self.rng.randint(0, board.COLUMN_COUNT - 1))

            elif len(new_plan) > 1:
                # Remove one move
                i = self.rng.randint(0, len(new_plan) - 1)
                del new_plan[i]

        return new_plan


    def annealing_loop(self, board: Board):
        current_plan = []
        # generate random initial plan
        while (u := self.rng.random()) < 1 / (len(current_plan) + 1):
            random_move = self.rng.randint(0, board.COLUMN_COUNT - 1)
            current_plan.append(random_move)
        
        def evaluate_plan(plan: list[int]) -> float:
            simulated_board = board.copy_board()
            for move in plan:
                if simulated_board.is_valid_location(move):
                    simulated_board.drop_piece(move, self.piece)
                else:
                    break
            return self.evaluator.score_position(simulated_board)
        
        current_temp = self.initial_temperature
        timeout = False

        # temp loop
        start_time = time.perf_counter()
        while current_temp > self.min_temperature and not timeout:
            for _ in range(self.max_iteration):
                current_score = evaluate_plan(current_plan)
                new_plan = self.summon_new_plan(board, current_plan)
                new_score = evaluate_plan(new_plan)

                # calculate delta
                delta = new_score - current_score
                # acceptance criteria
                if delta > 0:
                    current_plan = new_plan
                else:
                    acceptance_prob = math.exp(delta / current_temp)
                    if self.rng.random() < acceptance_prob:
                        current_plan = new_plan

            current_temp *= self.cooling_rate
            timeout = time.perf_counter() - start_time > self.timeout_duration_seconds
        
        self.best_plan = current_plan
        # assign target board
        local_board = board.copy_board()
        for move in self.best_plan:
            if local_board.is_valid_location(move):
                local_board.drop_piece(move, self.piece)
            else:
                break
        self.target_board = local_board


    def get_move(self, board: Board) -> int:
        solution = -1
        while solution == -1:
            target_board = self.target_board
            if target_board is None:
                if self.verbose:
                    print("No target board")
                self.annealing_loop(board)
                continue

            possible_cols = possible_moves_to_target(board, target_board, verbose=self.verbose)
            if len(possible_cols) == 0:
                self.annealing_loop(board)
                continue

            solution = self.rng.choice(possible_cols)

        return solution
