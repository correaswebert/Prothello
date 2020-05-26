# Play the Othello game
import os
from Othello import *
from OthelloAI import OthelloAI


def getComputerReadableNotation(move):
    letter, number = move[0], move[1]   # extract coordinates
    x = ord(letter.lower()) - 97
    y = int(number) - 1
    # error made while noting move ... e.g. f55
    # otherwise f5 assumed as per extraction
    if y > 9:
        return (-1, -1)
    return (x, y)


def getHumanReadableNotation(x, y):
    # X -> letter , Y -> number
    move = ""
    move += chr(x+65)
    move += str(y+1)
    return move


def singlePlayerMode(humanFirst=True):
    AI_POWER = 4
    game_field = OthelloAI(humanFirst)

    if not humanFirst:
        game_field.displayBoard()
        game_field.aiPlay(AI_POWER)

    while True:
        # Player's chance
        game_field.displayBoard()
        print("Enter move (eg. 'a6')")
        x, y = getComputerReadableNotation(input(">>> "))
        game_field.checkValidAndMove(x, y)

        # A.I.'s chance
        game_field.displayBoard()
        print("Computer's turn ...")
        x, y = game_field.aiPlay(AI_POWER)

        winner = game_field.isGameOver()
        if winner:
            game_field.displayBoard()
            print(f"{'You' if winner == game_field.HUMAN else 'Computer'} won!")


def twoPlayerMode():
    game_field = Othello()
    while True:
        game_field.displayBoard()

        print("Enter move (eg. 'a6')")
        x, y = getComputerReadableNotation(input(">>> "))
        game_field.checkValidAndMove(x, y)

        winner = game_field.isGameOver()
        if winner:
            game_field.displayBoard()
            print(f"{'Black' if winner == BLACK else 'White'} won!")
            break


def AI_vs_AI():
    # power is the max depth of the game tree searched
    B_POWER = 6
    W_POWER = 6

    moves = []
    game_field = OthelloAI()
    while True:
        winner = game_field.isGameOver()
        if winner != 0:
            game_field.displayBoard()
            print(f"{'Black' if winner == BLACK else 'White'} wins!")
            break

        # Black plays
        game_field.displayBoard()
        try:
            ai_power = B_POWER if game_field.player == BLACK else W_POWER
            x, y = game_field.aiPlay(ai_power)
        except TypeError:
            print(game_field.board)
            break
        move = getHumanReadableNotation(x, y)
        moves.append(('W' if game_field.player == BLACK else 'B', move))

    # for move in moves:
    print(moves)


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print("Enter the mode of play")
    print("Single Player Mode (1)  |  Two Player Mode (2)")
    single_player = input(">>> ") == '1'

    if single_player:
        print("Would you like to start? (y/n)")
        player_first = input(">>> ").lower() == 'y'
        singlePlayerMode(player_first)
    else:
        twoPlayerMode()
