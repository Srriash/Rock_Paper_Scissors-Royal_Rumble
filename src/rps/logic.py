import random
moves = ['rock', 'paper', 'scissors']

def get_computer_move():
    return random.choice (moves)

def winner_decider(player_move, computer_move):
    if player_move == computer_move:
        return 'tie'
    elif (player_move == 'rock' and computer_move == 'scissors') or (player_move == 'paper' and computer_move == 'rock') or (player_move == 'scissors' and computer_move == 'paper'):
        return 'player'
    else:
        return 'computer'