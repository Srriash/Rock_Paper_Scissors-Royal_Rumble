import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rps.logic import get_computer_move, winner_decider

moves = ['rock', 'paper', 'scissors']
def test_get_computer_move():
    for _ in range(10):
        computer_move = get_computer_move()
        assert computer_move in moves, f"Invalid computer move: {computer_move}"
    print("get_computer_move() passed.")
def test_winner_decider ():
    assert winner_decider ('rock','rock')=='tie'
    assert winner_decider ('paper','paper')=='tie'
    assert winner_decider ('scissors','scissors')=='tie'
    assert winner_decider("scissors", "scissors") == "tie"
    assert winner_decider("rock", "scissors") == "player"
    assert winner_decider("paper", "rock") == "player"
    assert winner_decider("scissors", "paper") == "player"
    assert winner_decider("scissors", "rock") == "computer"
    assert winner_decider("rock", "paper") == "computer"
    assert winner_decider("paper", "scissors") == "computer"
    print("winner_decider() passed.")
if __name__ == "__main__":
    test_get_computer_move()
    test_winner_decider()
    print("All tests passed.")
