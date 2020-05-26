# Python Othello implementation
import os
import math


# TODO: make these class variables
BLACK = 1
WHITE = -1
BLANK = 0


class Othello:

    def __init__(self, spanX=8, spanY=8):
        self.board = [[BLANK]*spanY for _ in range(spanX)]
        self.player = BLACK     # Black plays first

        self.spanX = spanX      # Board height
        self.spanY = spanY      # Board width

        # Traditional Othello starting position
        if spanX == spanY == 8:
            self.board[3][4] = self.board[4][3] = BLACK
            self.board[3][3] = self.board[4][4] = WHITE

    # Returns (board, player)
    def setBoardAndPlayer(self, board=None, player=None):
        """
        Returns the actual game board and current player if None provided

        If AI used then it generates intermediate boards in game tree while
        also switching the player...
        As this should not affect the actual board and current player,
        use this helper function to take care even if AI used
        """
        if board is None:
            board = self.board
        if player is None:
            player = self.player
        return board, player

    # Returns a list of location tuples
    def findNeighbours(self, x, y, board=None):
        """Determines the locations with pieces adjacent to the given square"""
        board, _ = self.setBoardAndPlayer(board)

        neighbours = []
        # min/max take care of the edge cases
        for i in range(max(0, x-1), min(x+2, self.spanX)):
            for j in range(max(0, y-1), min(y+2, self.spanY)):
                if board[i][j] != BLANK:
                    neighbours.append((i, j))
        return neighbours

    # Return values  --->  0: invalid | 1: valid | -1: move made
    def checkValidAndMove(self, x, y, only_check_valid=False, board=None, player=None):
        """Returns a board after making a move according to Othello rules"""
        VALID = 1
        INVALID = 0
        MOVE_MADE = -1

        # if no board is provided then intention is to play the move
        keepOriginalBoardStatic = False if board is None else True
        # if no board provided then use main board
        board, player = self.setBoardAndPlayer(board, player)

        # location must be on the board
        if not (0 <= x < self.spanX and 0 <= y < self.spanY):
            return INVALID

        # location must be empty
        if board[x][y] != BLANK:
            return INVALID

        # Determining the neighbours to the square
        neighbours = self.findNeighbours(x, y)
        # move must have neighbours
        if neighbours == []:
            return INVALID

        # we still don't know if move is Othello compliant
        valid_move = False
        # create only if move to be made
        if not only_check_valid:
            # Which tiles to convert
            convert = []

        # For all the generated neighbours, determine if they form a line
        # If a line is formed, add it to the convert list
        for neighbour in neighbours:
            neighX, neighY = neighbour

            # If neighbour colour is same as player colour, can't form a line
            if board[neighX][neighY] == player:
                continue
            # The path of each individual line
            path = []

            # Determining direction to move
            deltaX = neighX - x
            deltaY = neighY - y

            # While we are in the bounds of the board update neighbour
            while 0 <= neighX < self.spanX and 0 <= neighY < self.spanY:
                # If we reach a blank tile, there's no line formed
                if board[neighX][neighY] == BLANK:
                    break

                path.append((neighX, neighY))
                # If we reach a tile of the player's colour, a line is formed
                if board[neighX][neighY] == player:
                    if only_check_valid:
                        return VALID
                    # Append all of our path nodes to the convert list
                    for node in path:
                        convert.append(node)
                    valid_move = True
                    break

                # Move the tile in current direction
                neighX += deltaX
                neighY += deltaY

        # move is not Othello compliant
        if only_check_valid:
            return int(valid_move)

        # play the move on the board
        board[x][y] = player
        # Convert all the appropriate tiles
        for tile in convert:
            board[tile[0]][tile[1]] = player

        # in case AI used, it will evaluate many boards
        # but only one of them is final, so don't alter the original board
        if keepOriginalBoardStatic:
            return board

        # alter the board and switch player as no (board,player) args given
        self.board = board
        self.player = -self.player      # switch player
        self.isPassTurn()
        return MOVE_MADE

    # Returns True if turn is 'passable' otherwise False
    def isPassTurn(self, board=None, player=None, only_test=False):
        board, player = self.setBoardAndPlayer(board, player)

        if self.getValidMoves(board, player) == []:
            if not only_test:
                self.player = -self.player      # player switched
            return True
        return False

    # Returns list of location tuples
    def getValidMoves(self, board=None, player=None):
        """Finds all the valid moves according to Othello rules"""
        # if no board provided then use main board
        board, player = self.setBoardAndPlayer(board, player)

        possible_moves = []
        # iterate through all the locations
        for x in range(self.spanX):
            for y in range(self.spanY):
                # location is empty and has neighbours
                if board[x][y] == BLANK and self.findNeighbours(x, y, board):
                    possible_moves.append((x, y))
        # can't use for loop simply as removing alters indices
        # also we go for last-to-first approach
        # first-to-last approach similar to for-loop, have to handle special cases
        x = len(possible_moves) - 1
        while x >= 0:
            if not self.checkValidAndMove(*possible_moves[x],
                                          only_check_valid=True,
                                          board=board, player=player):
                possible_moves.remove(possible_moves[x])   # Invalid move
            x -= 1
        return possible_moves

    # Returs (Bscore, Wscore)
    def scoreboard(self, board=None):
        if board is None:
            board = self.board
        black_score, white_score = 0, 0
        for row in board:
            black_score += row.count(BLACK)
            white_score += row.count(WHITE)
        return black_score, white_score

    # BUG: doesn't account for drawn games
    # RETURNS  --->  0: Game is On | 1: Black wins | -1: White wins
    def isGameOver(self, board=None):
        board, _ = self.setBoardAndPlayer(board)

        bcounter = 0
        wcounter = 0
        for row in board:
            for elem in row:
                if elem == BLANK:
                    return 0
                elif elem == WHITE:
                    wcounter += 1
                else:
                    bcounter += 1
        return BLACK if bcounter > wcounter else WHITE

    # in case of no UTF-8 support in terminal, an alternate ANSI string provided
    # also make sure to replace strings with the ANSI `|`
    def getBoardString(self, board):
        """gets the board as a string to be printed"""
        # add number row
        board_string = ' ' * 5
        for i in range(1, self.spanY+1):
            board_string += str(i) + "   "

        # start board
        # board_string += "\n   +---+---+---+---+---+---+---+---+\n"
        board_string += "\n   ┌───┬───┬───┬───┬───┬───┬───┬───┐\n"

        # to indicate the valid moves with '*'
        valid_moves = self.getValidMoves()
        for x in range(self.spanX):
            board_string += f' {chr(x+65)} │'      # add letter column

            for y in range(self.spanY):
                elem = board[x][y]
                if elem == BLACK:
                    board_string += " ◼ │"
                elif elem == WHITE:
                    board_string += " ◻ │"
                elif (x, y) in valid_moves:
                    board_string += " * │"
                else:
                    board_string += "   │"

            # board_string += "\n   +---+---+---+---+---+---+---+---+\n"
            if x != 7:
                board_string += "\n   ├───┼───┼───┼───┼───┼───┼───┼───┤\n"

        # board_string += "\n   +---+---+---+---+---+---+---+---+\n"
        board_string += "\n   └───┴───┴───┴───┴───┴───┴───┴───┘\n"

        return board_string

    def getStatString(self, board, player):
        """gets the score of the player and tells whose chance it is"""
        score_p1, score_p2 = self.scoreboard()
        score_p1, score_p2 = str(score_p1), str(score_p2)

        # as the players are switched as soon as move is made
        # 1 is WHITE and -1 is BLACK instead... hence the -ve sign
        # '*' indicates current player
        p1_stat = " *W: " if player == -WHITE else " W: "
        p2_stat = "*B: " if player == -BLACK else "B: "
        padding = ' ' * (4*self.spanY - 4 - len(score_p1 + score_p2))

        return p1_stat + score_p1 + padding + p2_stat + score_p2 + "\n\n"

    def displayBoard(self, board=None, player=None):
        """For Terminal representation of the board and status line"""
        os.system("cls" if os.name == "nt" else "clear")
        board, player = self.setBoardAndPlayer(board, player)

        stats_string = self.getStatString(board, player)
        board_string = self.getBoardString(board)

        print(stats_string + board_string)
