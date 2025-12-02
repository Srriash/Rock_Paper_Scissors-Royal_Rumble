import random

print (" \033[1;31m Welcome to the rock, paper and scissors world!! \033[0m")
moves = ['rock', 'paper', 'scissors']

player_name = input('Enter your game name: ').upper()
print('\n')
    
print ('\033[1;34m Hello',player_name,'\033[0m','\n')

player_score = 0
computer_score = 0

print ('\033[3m To quit the game, just type "quit" here or later \n \033[0m')
quit_yes = input('\033[33;1m However, press enter to have the best duel you will ever experience in your life \033[0m \n').lower()

is_true = True
while (is_true):
    if quit_yes =='quit':
        break
    
    player_move = input('Pick your move - Rock, Paper or Scissors - ').lower()
        
    if player_move == 'quit':
        break
    if player_move not in moves:
        print('invalid move, try again :)')
        continue

    computer_move = random.choice (moves)

    print ('Computer chose', computer_move)

    if player_move == computer_move:
        print ("It is a tie! Let's go again \n")
        print ('Your score:',player_score)
        print ("Computer's score:", computer_score)
        continue
    elif (player_move == 'rock' and computer_move == 'scissors') or (player_move == 'paper' and computer_move == 'rock') or (player_move == 'scissors' and computer_move == 'paper'):
        print ('YOU WIN!! \n')
        player_score = player_score + 1
        print ('Your score:',player_score)
        print ("Computer's score:", computer_score)
        continue
    else:
        print ('Computer wins! \n')
        computer_score = computer_score + 1
        print ('Your score:',player_score)
        print ("Computer's score:", computer_score)
        continue

if player_score==computer_score==0:
    print('\033[1;31m Just try the game once and I am sure you will love it!! \033[0m')
elif player_score>computer_score:
    print ('You,',player_name,'scored', player_score,'and','the computer scored', computer_score)
    print('\033[1;33m YOU BEAT THE ALMIGHTY COMPUTER!!! \033[0m')
    print('Thank you for playing the game, see you soon!!')
elif player_score<computer_score:
    print ('You,',player_name,'scored', player_score,'and','the computer scored', computer_score)
    print('\033[1;31m A MERE COMPUTER BEAT YOU, HUMAN INTELLIGENCE IS ON THE NOSE DIVE. TRY AGAIN AND PROVE ME WRONG \033[0m')
else:
    print ('You,',player_name,'scored', player_score,'and','the computer scored', computer_score)
    print('\033[34;1m YOU DREW WITH THE COMPUTER, TRY AGAIN AND BEAT IT ONCE FOR ALL \033[0m')


