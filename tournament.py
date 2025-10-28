import sys
from itertools import permutations


try:
    from board import Board
    from connect4 import connect4
    from game import bot_map, p1_evaluator_type, p2_evaluator_type, name_map
    from bots import *
except ImportError as e:
    print(f"Error importing project files: {e}")
    sys.exit(1)

NUM_MATCHES = 50
BOT_NAMES = [name for name in bot_map.keys() if name != 'human']
EVALUATOR_TYPE = (p1_evaluator_type, p2_evaluator_type)

def run_tournament():
    results = {
        name: {
            'wins': 0,
            'losses': 0,
            'draws': 0
        } for name in BOT_NAMES
    }

    matchups = list(permutations(BOT_NAMES, 2))

    total_games = len(matchups) * NUM_MATCHES
    game_count = 0

    print("=" * 50)
    print("Starting Tournament")
    print(f"Bots: {', '.join(BOT_NAMES)}")
    print(f"Total matchups: {len(matchups)}")
    print(f"Total games: {total_games}")
    print("=" * 50)

    for p1, p2 in matchups:
        p1_wins_matchup = 0
        p2_wins_matchup = 0
        draws_matchup = 0

        print(f"Matchup: {p1} (P1) vs. {p2} (P2)")
        try:
            p1_class = bot_map[p1]
            p1 = p1_class(Board.PLAYER1_PIECE)
            if isinstance(p1, EvaluativeBot):
                p1.set_evaluator_type(EVALUATOR_TYPE[0])

            p2_class = bot_map[p2]
            p2 = p2_class(Board.PLAYER2_PIECE)
            if isinstance(p2, EvaluativeBot):
                p2.set_evaluator_type(EVALUATOR_TYPE[1])
        except Exception as e:
            print(f"\nError creating bots {p1} or {p2}: {e}")
            sys.exit(1)

        for i in range(NUM_MATCHES):
            game_count += 1

            try:
                winner_piece = connect4(p1, p2, ui=False)
            except Exception as e:
                print(f"\nError running game {p1} vs {p2}: {e}")
                winner_piece = -1
            
            print(f"This is {winner_piece}")
            
            if winner_piece == Board.PLAYER1_PIECE:
                p1_wins_matchup += 1
            elif winner_piece == Board.PLAYER2_PIECE:
                p2_wins_matchup += 1
            elif winner_piece == 0: 
                draws_matchup += 1
            
            print(f"Game {i+1}/{NUM_MATCHES} complete. (Overall progress: {game_count*100/total_games:.1f}%)", end="\r")
        
        print(f"Matchup Result: {p1} wins: {p1_wins_matchup} | {p2} wins: {p2_wins_matchup} | Draws: {draws_matchup}")
        print("-" * 20)

        results[p1]['win'] += p1_wins_matchup
        results[p1]['draw'] += draws_matchup
        results[p1]['loss'] += p2_wins_matchup
        
        results[p2]['win'] += p2_wins_matchup
        results[p2]['draw'] += draws_matchup
        results[p2]['loss'] += p1_wins_matchup

    print("\n\n--- FINAL TOURNAMENT REPORT ---")
    print(f"{'Bot':<28} | {'Wins':<6} | {'Losses':<6} | {'Draws':<6} | {'Total':<6}")
    print("-" * 52)

    sorted_bots = sorted(BOT_NAMES, key=lambda name: results[name]['win'], reverse=True)
    
    for bot_name in sorted_bots:
        r = results[bot_name]
        total = r['win'] + r['loss'] + r['draw']
        full_name = name_map.get(bot_name, bot_name)
        print(f"{full_name:<28} | {r['win']:<6} | {r['loss']:<6} | {r['draw']:<6} | {total:<6}")
    print("-" * 52)

if __name__ == "__main__":
    run_tournament()