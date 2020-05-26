"""Othello AI implementation"""

from Othello import *

INF = float("inf")


class OthelloAI(Othello):

    def __init__(self, humanFirst=True):
        super().__init__()
        self.COMP = WHITE if humanFirst else BLANK
        self.HUMAN = BLACK if humanFirst else WHITE

    def evaluateBoard(self, board, player):
        """
        Heuristic that weights corner tiles and edge tiles as positive
        adjacent to corners (if the corner is not yours) as negative
        Weights other tiles as one point
        """
        score = 0

        # easier to track value changes rather than going to specific parts of code
        NORMAL = 1              # average square
        EDGE = 5                # good square
        CORNER_EDGES = -10      # depends on the situation
        CORNER = 25             # most precious square
        PASS_PENALTY = 50       # if no moves available (subtracted from score)

        # Go through all the tiles
        for x in range(self.spanX):
            for y in range(self.spanY):
                value = NORMAL

                # check if tiles present adjacent to every corner, three each
                tiles_near_corner = (
                    (x == 0 and y == 1) or (x == 1 and 0 <= y <= 1),  # TL corner
                    (x == 0 and y == 6) or (x == 1 and 6 <= y <= 7),  # TR corner
                    (x == 7 and y == 1) or (x == 6 and 0 <= y <= 1),  # BL corner
                    (x == 7 and y == 6) or (x == 6 and 6 <= y <= 7))  # BR corner
                corners = (board[0][0], board[7][0], board[0][7], board[7][7])

                # if corner belongs to us then no use placing tiles there
                for corner, ce_tiles in zip(corners, tiles_near_corner):
                    if ce_tiles is False:   # no corner edge tile
                        continue
                    if corner == player:
                        value = CORNER_EDGES
                    else:
                        value = -CORNER_EDGES

                # evaluate corners and edges (not including corner)
                if any((x == 0 and 1 < y < 6,
                        x == 7 and 1 < y < 6,
                        y == 0 and 1 < x < 6,
                        y == 7 and 1 < x < 6)):
                    value = EDGE
                elif any((x == 0 and y == 0,
                          x == 0 and y == 7,
                          x == 7 and y == 0,
                          x == 7 and y == 7)):
                    value = CORNER

                # add if location belongs to player
                if board[x][y] == player:
                    score += value
                # subtract if location belongs to opponent
                elif board[x][y] == -player:
                    score -= value

        # reward the AI for keeping higher score
        # otherwise punish it
        Bpoints, Wpoints = self.scoreboard(board)
        if player == BLACK:
            if Bpoints > Wpoints:
                score += min(10, Bpoints - Wpoints)
            else:
                score -= max(5, Bpoints - Wpoints)

        if player == WHITE:
            if Bpoints < Wpoints:
                score += min(10, Wpoints - Bpoints)
            else:
                score -= max(5, Wpoints - Bpoints)

        # penalize the AI if no moves are available
        available_moves = len(self.getValidMoves(board, player))
        if available_moves == 0:
            score -= PASS_PENALTY
        else:
            score += min(5, available_moves)

        return score

    # MiniMax Algo with Alpha-Beta pruning
    def minimax(self, state, depth, player, alpha=-INF, beta=INF):
        """
        create a game tree of given depth

        alpha is the losing factor in the best case
        beta is the winning factor in the worst case

        try to keep alpha as low as possible and beta as high
        as soon as beta <= alpha, prune that branch
        """

        if depth == 0 or self.isGameOver(state):
            # as game is over, move can't be provided in base case
            return (None, None, self.evaluateBoard(state, player))

        # 'best' is a list of move and score (best ones returned)
        if player == self.COMP:
            # set worst score for Computer to improve on :: -inf
            best = (None, None, -INF)
        else:
            # set the best score assuming player is pro :: +inf
            best = (None, None, INF)

        # TODO: the game tree is re-evaluated after every 'real' move
        # we can memoize that info to speed up the process and increase the
        # search depth, picking up from where we left off
        # TODO: the branches of other potential moves must be pruned
        for cell in self.getValidMoves(state):
            # extract coordinates
            x, y = cell
            # temporarily set the (x,y) position as player's number (-1 / +1)
            state[x][y] = player
            stateVal = self.minimax(state, depth-1, -player, alpha, beta)[2]
            # return board to original state
            state[x][y] = BLANK

            if player == self.COMP:
                if stateVal > best[2]:
                    # computer is improving, update the best move and score
                    best = *cell, stateVal
                # update losing-factor alpha
                alpha = max(alpha, best[2])

            else:
                # update to the best move and score human may make
                # prepares the computer for the worst
                # and at best hope for draw
                if stateVal < best[2]:
                    best = *cell, stateVal
                # update winning-factor beta
                beta = min(beta, best[2])

            # if winning is not possible, then skip that branch
            if beta <= alpha:
                break

        return best

    def aiPlay(self, ai_power=8):
        x, y, _ = self.minimax(self.board, depth=ai_power, player=self.COMP)
        self.checkValidAndMove(x, y)
        return x, y

    def getStatString(self, board, player):
        """add the win_factor to the status"""
        score_p1, score_p2 = self.scoreboard()
        score_p1, score_p2 = str(score_p1), str(score_p2)

        # as the players are switched as soon as move is made
        # 1 is WHITE and -1 is BLACK instead... hence the -ve sign
        # '*' indicates current player
        p1_stat = " *W: " if player == -WHITE else " W: "
        p2_stat = "*B: " if player == -BLACK else "B: "

        B_win = self.evaluateBoard(board, BLACK)
        W_win = -self.evaluateBoard(board, WHITE)
        try:
            win_factor = round(
                (B_win + W_win) / (math.fabs(B_win) + math.fabs(W_win)),
                ndigits=2)
        except ZeroDivisionError:
            win_factor = 0.
        win_factor = str(win_factor). \
            center(4*self.spanY - 4 - len(score_p1 + score_p2), ' ')

        return p1_stat + score_p1 + win_factor + p2_stat + score_p2 + "\n\n"
