import sys
from itertools import permutations


try:
    from board import Board
    from connect4 import connect4
    from game import bot_map, p1_evaluator_type, p2_evaluator_type, name_map, p1_evaluator_default_type
    from bots import *
except ImportError as e:
    print(f"Error importing project files: {e}")
    sys.exit(1)

NUM_MATCHES = 50
BOT_NAMES = [name for name in bot_map.keys() if name != 'human']
EVALUATOR_TYPE = (p1_evaluator_default_type, p2_evaluator_type)

def run_comparison():

    tournament_result = {
        f"{name}_default vs {name}_custom": {
            f"{name}_default": {
                'win': 0,
                'loss': 0,
                'draw': 0,
                'time_avg': 0,
                'move_avg': 0
            },
            f"{name}_custom": {
                'win': 0,
                'loss': 0,
                'draw': 0,
                'time_avg': 0,
                'move_avg': 0
            }
        } for name in BOT_NAMES
    }

    total_games = len(BOT_NAMES) * NUM_MATCHES
    game_count = 0

    print("=" * 50)
    print("Starting Tournament")
    print(f"Bots: {', '.join(BOT_NAMES)}")
    print(f"Total games: {total_games}")
    print("=" * 50)

    for name in BOT_NAMES:
        p1_wins_matchup = 0
        p2_wins_matchup = 0
        draws_matchup = 0
        tournament_keys = f"{name}_default vs {name}_custom"

        # p1_full_name = name_map.get(p1_name, p1_name)
        # p2_full_name = name_map.get(p2_name, p2_name)

        print(f"Matchup: {name}_default (P1) vs. {name}_custom (P2)")
        try:
            p1_class = bot_map[name]
            p1 = p1_class(Board.PLAYER1_PIECE)
            if isinstance(p1, EvaluativeBot):
                p1.set_evaluator_type(EVALUATOR_TYPE[0])

            p2_class = bot_map[name]
            p2 = p2_class(Board.PLAYER2_PIECE)
            if isinstance(p2, EvaluativeBot):
                p2.set_evaluator_type(EVALUATOR_TYPE[1])
        except Exception as e:
            print(f"\nError creating bots {name}_default or {name}_custom: {e}")
            sys.exit(1)

        time_avg_p1 = 0
        time_avg_p2 = 0

        move_avg_p1 = 0
        move_avg_p2 = 0

        for i in range(NUM_MATCHES):
            game_count += 1

            try:
                winner_piece = connect4(p1, p2, ui=False)
            except Exception as e:
                print(f"\nError running game {name}_default vs {name}_custom: {e}")
                winner_piece = -1
                continue
            
            print(f"This is {winner_piece}")
            
            if winner_piece['winner'] == Board.PLAYER1_PIECE:
                p1_wins_matchup += 1
            elif winner_piece['winner'] == Board.PLAYER2_PIECE:
                p2_wins_matchup += 1
            elif winner_piece['winner'] == 0: 
                draws_matchup += 1

            time_avg_p1 += winner_piece['time_p1']
            time_avg_p2 += winner_piece['time_p2']

            move_avg_p1 += winner_piece['moves_p1']
            move_avg_p2 += winner_piece['moves_p2']
            
            print(f"Game {i+1}/{NUM_MATCHES} complete. (Overall progress: {game_count*100/total_games:.1f}%)", end="\r")
        
        print(f"Matchup Result: {name}_default wins: {p1_wins_matchup} | {name}_custom wins: {p2_wins_matchup} | Draws: {draws_matchup}")
        print("-" * 20)

        tournament_result[tournament_keys][f"{name}_default"]['win'] += p1_wins_matchup
        tournament_result[tournament_keys][f"{name}_default"]['draw'] += draws_matchup
        tournament_result[tournament_keys][f"{name}_default"]['loss'] += p2_wins_matchup
        tournament_result[tournament_keys][f"{name}_default"]['time_avg'] = time_avg_p1 / NUM_MATCHES
        tournament_result[tournament_keys][f"{name}_default"]['move_avg'] = move_avg_p1 / NUM_MATCHES

        tournament_result[tournament_keys][f"{name}_custom"]['win'] += p2_wins_matchup
        tournament_result[tournament_keys][f"{name}_custom"]['draw'] += draws_matchup
        tournament_result[tournament_keys][f"{name}_custom"]['loss'] += p1_wins_matchup
        tournament_result[tournament_keys][f"{name}_custom"]['time_avg'] = time_avg_p2 / NUM_MATCHES
        tournament_result[tournament_keys][f"{name}_custom"]['move_avg'] = move_avg_p2 / NUM_MATCHES

    print("=" * 50)


    print("\n\n--- FINAL TOURNAMENT REPORT ---")
    print(f"{'Bot':<30} | {'Wins':<6} | {'Losses':<6} | {'Draws':<6} | {'Total':<6} | {'Time':<6} | {'Moves':<6}")
    print("-" * 52)

    for matches in tournament_result.keys():
        print(f"Matchup: {matches}")
        for bot_name in matches.split(' vs '):
            full_name = name_map.get(bot_name, bot_name)         
            r = tournament_result[matches][bot_name]
            total = r['win'] + r['loss'] + r['draw']
            time_avg = r['time_avg']
            move_avg = r['move_avg']
            print(f"{full_name:<28} | {r['win']:<6} | {r['loss']:<6} | {r['draw']:<6} | {total:<6} | {time_avg:<6} | {move_avg:<6}")
        print("-" * 52)

if __name__ == "__main__":
    run_comparison()