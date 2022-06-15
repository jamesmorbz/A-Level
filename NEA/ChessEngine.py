import math
import copy

class GameState():
    def __init__(self):
        # board is 8x8 2D List, each element of the list has 2 characters
        # First character == colour (b = black ,w = white)
        # second character == piece
        # R == rook, N == knight, B == bishop, Q == Queen, K == king, P == pawn
        # -- == empty space
        # start board
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.AIturn = False
        self.moveLog = []
        # Define the King locations for both sides as it is used in identifying checks and invalid moves
        self.wKingLoc = (7, 4)
        self.bKingLoc = (0, 4)

        # These are defined and set to false as either can be changed to the bool True in order to end the game
        self.checkMate = False
        self.stalemate = False

        # Enpassant is also defined but is not set to a Bool as enpassant is not something that is as simple
        # as "true" or "false" but can occur multiple times per game give the perfect set of circumstances
        self.enpassantPossible = ()

        self.currentCastlingRight = castleRights(True, True, True, True)
        self.castleRightsLog = [castleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    # Function defined for making the move, self represents the instance of the class. By using the “self” keyword we
    # can access the attributes and methods of the class in python. It binds the attributes with the given arguments.
    def makeMove(self, move):
        # Makes the square from which the piece is moving clear
        self.board[move.startRow][move.startCol] = '--'
        # Moves the piece from Starting Square to Finishing Square
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # Adds the move to the move log
        self.moveLog.append(move)
        # Changes which side it is to move
        self.whiteToMove = not self.whiteToMove
        # Checks whether either king has been moved
        if move.pieceMoved == 'wK':
            self.wKingLoc = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.bKingLoc = (move.endRow, move.endCol)

        # Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # Making it so you can perform enpassant, remember Rank 2 = Rank 1 in python indexing from 0
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        # Update castling rights - whenever king or rook move is played
        self.updateCastleRights(move)
        self.castleRightsLog.append(castleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            # removing move form log
            move = self.moveLog.pop()
            # reversing make move
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # Switching wether it is white or black to move
            self.whiteToMove = not self.whiteToMove
            # Checking wether either King has moved depending if it is white or black to move
            if move.pieceMoved == 'wK':
                self.wKingLoc = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.bKingLoc = (move.startRow, move.startCol)

            # undoing enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # undoing castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            # undoing castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = castleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # gets all move
        moves = self.getAllMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.wKingLoc[0], self.wKingLoc[1], moves)
        else:
            self.getCastleMoves(self.bKingLoc[0], self.bKingLoc[1], moves)
        # goes backwords through the list
        for i in range(len(moves) - 1, -1, -1):
            # makes the move and changes turn
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # sees if that previous move puts the player in check
                moves.remove(moves[i])
            # changes turn back and undoes the move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        # # Checks if there are any valid moves (either: stalemate or checkmate)
        if len(moves) == 0:
            # # If there are no valid moves and the king is in check it must be checkmate, If there are no valid
            # moves and the king is not in check then it must be stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.stalemate = True

        # all the valid moves
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    def inCheck(self):
        # checks which turn
        if self.whiteToMove:
            # returns a bool and checks if the whiite king is under attack
            return self.squareUnderAttack(self.wKingLoc[0], self.wKingLoc[1])
        else:
            # then checks black king
            return self.squareUnderAttack(self.bKingLoc[0], self.bKingLoc[1])

    def squareUnderAttack(self, r, c):
        # sees opponent moves by changing turn gets all there moves and changes back turn
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllMoves()
        self.whiteToMove = not self.whiteToMove
        # checks all moves and sees if the end square is the square entered in the function
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllMoves(self):
        # initialising the move list
        moves = []
        # going through each element in the list
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                # checking piece colour
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    # using dictionary to reduce if statements
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        # white pawn moves
        if self.whiteToMove:
            # checking if square above is empty
            if self.board[r - 1][c] == '--':
                # if it is we append that as a valid move
                moves.append(Move((r, c), (r - 1, c), self.board))
                # checks if the piece hasn't been moved so it can do a double move
                if r == 6 and self.board[r - 2][c] == '--':
                    moves.append(Move((r, c), (r - 2, c), self.board))
            # captures to the left        
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            # captures to the right
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        # black pawn moves
        else:
            if self.board[r + 1][c] == '--':
                # checking if square below is empty
                moves.append(Move((r, c), (r + 1, c), self.board))
                # checks if the piece hasn't been moved so it can do a double move
                if r == 1 and self.board[r + 2][c] == '--':
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # captures to the left
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            # captures to the right
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        # directions up, down, left and right(not in that order)
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        # conditional expression in order to get opponents colour
        oppColour = 'b' if self.whiteToMove else 'w'
        # goes through each direction
        for d in directions:
            # loops 8 times length/width of the board as a rook can move 8 squares
            for i in range(1, 8):
                # adds a factor of the direction
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                # checks if the final position is off the board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    # checks if it can move to that end square by checking if it is empty
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == oppColour:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                # breaks if it of the board
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        # directions the bishop ccan move in (diaganols)
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        # gets opponents colour
        oppColour = 'b' if self.whiteToMove else 'w'
        # goes through the directions
        for d in directions:
            # iterates 8 times
            for i in range(1, 8):
                # multiplies the end position by i
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                # checks if the endSq is off the board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    # if the endSq is empty it is a valid move
                    if endPiece == '--':
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # if there is an opponents piece we can take it then breaks out of that direction
                    elif endPiece[0] == oppColour:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    # if it is a friendly piece then you can no longer go in that direction so we be break
                    else:
                        break
                # breaks if it off the board
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        # can move in all directions so we use the rook and bishop valid move checks
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKnightMoves(self, r, c, moves):
        # knight moves
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        # gets ally colour
        allyColour = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColour:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getKingMoves(self, r, c, moves):
        # king can only move 1 square but any direction
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
        # easier to check if the 
        allyColour = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            # checks if off the board
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColour:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


    def minimax(self, depth, alpha, beta, isMaximiser):
        reqDepth = copy.deepcopy(depth)
        tempCheckmate = copy.deepcopy(self.checkMate)
        tempStalemate = copy.deepcopy(self.stalemate)
        moves = self.getValidMoves()

        # checking if it has reached the bottom of the branch or stalemate or checkmate
        if depth == 0 or ((self.checkMate or self.stalemate) and len(moves) == 0):
            # gets the evaluation
            value = self.boardEval()
            self.checkMate = copy.deepcopy(tempCheckmate)
            self.stalemate = copy.deepcopy(tempStalemate)
            # returns the evaluation and reqDepth to achieve that position
            return value, reqDepth

        elif isMaximiser:
            maxEval = -math.inf
            moves = self.getValidMoves()
            for move in moves:
                self.makeMove(move)
                eval, reqDepth = self.minimax(depth - 1, alpha, beta, False)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                self.undoMove()
                # if alpha <= beta
                if beta <= alpha:
                    break
            self.checkMate = copy.deepcopy(tempCheckmate)
            self.stalemate = copy.deepcopy(tempStalemate)
            return maxEval, reqDepth
        else:
            minEval = math.inf
            moves = self.getValidMoves()
            for move in moves:
                self.makeMove(move)
                eval, reqDepth = self.minimax(depth - 1, alpha, beta, True)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                self.undoMove()

                # if beta <= alpha:
                if alpha <= beta:
                    break
            self.checkMate = copy.deepcopy(tempCheckmate)
            self.stalemate = copy.deepcopy(tempStalemate)
            return minEval, reqDepth

    def getBestMove(self, depth):
        tempCheckmate = copy.deepcopy(self.checkMate)
        tempStalemate = copy.deepcopy(self.stalemate)
        tempCastle = copy.deepcopy((self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                    self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        self.AIturn = True

        bestScore = math.inf
        moves = self.getValidMoves()

        for move in moves:
            self.makeMove(move)
            initValue = self.boardEval()
            if initValue == -math.inf:
                bestMove = copy.deepcopy(move)
                self.undoMove()
                return bestMove

            score, reqDepth = self.minimax(depth, -math.inf, math.inf, False)

            if depth - reqDepth == 1:
                if score == -math.inf:
                    bestMove = copy.deepcopy(move)
                    self.undoMove()
                    return bestMove
            elif depth - reqDepth == 2:
                if score == -math.inf:
                    bestMove = copy.deepcopy(move)
                    self.undoMove()
                    return bestMove

            if score < bestScore:
                bestScore = score
                bestMove = copy.deepcopy(move)
                self.undoMove()
            else:
                self.undoMove()

        self.AIturn = False
        self.checkMate = copy.deepcopy(tempCheckmate)
        self.stalemate = copy.deepcopy(tempStalemate)
        self.currentCastlingRight = castleRights(tempCastle[0], tempCastle[1], tempCastle[2], tempCastle[3])

        return bestMove

    def boardEval(self):
        moves = self.getValidMoves()
        if len(moves) == 0:

            if self.whiteToMove and self.checkMate:
                self.printBoard()
                self.printLog()
                print("Black checkmate")
                return -math.inf
            elif self.whiteToMove and self.checkMate:
                print("White checkmate")
                return math.inf
            elif self.stalemate:
                return 0
        # Pawns
        wPpieceSquare = [[0, 0, 0, 0, 0, 0, 0, 0],
                         [50, 50, 50, 50, 50, 50, 50, 50],
                         [10, 10, 20, 25, 25, 20, 10, 10],
                         [5, 5, 10, 100, 100 , 10, 5, 5],
                         [3, 3, 10, 100, 100, 10, 3, 3],
                         [5, -5, -10, 0, 60, -10, -5, 5],
                         [5, 10, 10, 10, 10, 10, 10, 5],
                         [0, 0, 0, 0, 0, 0, 0, 0]]

        # Knights
        wNpieceSquare = [[-50, -40, -30, -30, -30, -30, -40, -50],
                         [-40, -20, 0, 0, 0, 0, -20, -40],
                         [-30, 20, 0, 0, 0, 0, 20, -30],
                         [-30, 5, 5, 5, 5, 5, 5, -30],
                         [-30, 5, 5, 5, 5, 5, 5, -30],
                         [-30, 20, 20, 10, 10, 20, 20, -30],
                         [-40, -20, 0, 20, 20, 0, -20, -40],
                         [-50, -40, -30, -30, -30, -30, -40, -50]]

        # Bishops
        wBpieceSquare = [[-20, -10, -10, -10, -10, -10, -10, -20],
                         [-10, 0, 0, 0, 0, 0, 0, -10],
                         [-10, 0, 5, 10, 10, 5, 0, -10],
                         [-10, 5, 5, 10, 10, 5, 5, -10],
                         [-10, 0, 10, 10, 10, 10, 0, -10],
                         [-10, 10, 10, 10, 10, 10, 10, -10],
                         [-10, 5, 0, 0, 0, 0, 5, -10],
                         [-20, -10, -10, -10, -10, -10, -10, -20]]

        # Rooks
        wRpieceSquare = [[0, 0, 0, 0, 0, 0, 0, 0],
                         [5, 10, 10, 10, 10, 10, 10, 5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [0, 0, 0, 5, 5, 0, 0, 0]]

        # Queens
        wQpieceSquare = [[-20, -10, -10, -5, -5, -10, -10, -20],
                         [-10, 0, 0, 0, 0, 0, 0, -10],
                         [-10, 0, 5, 5, 5, 5, 0, -10],
                         [-5, 0, 5, 5, 5, 5, 0, -5],
                         [0, 0, 5, 5, 5, 5, 0, -5],
                         [-10, 5, 5, 5, 5, 5, 0, -10],
                         [-10, 0, 5, 0, 0, 0, 0, -10],
                         [-20, -10, -10, -5, -5, -10, -10, -20]]

        # King
        wKpieceSquare = [[-30, -40, -40, -50, -50, -40, -40, -30],
                         [-30, -40, -40, -50, -50, -40, -40, -30],
                         [-30, -40, -40, -50, -50, -40, -40, -30],
                         [-30, -40, -40, -50, -50, -40, -40, -30],
                         [-20, -30, -30, -40, -40, -30, -30, -20],
                         [-10, -20, -20, -20, -20, -20, -20, -10],
                         [20, 20, 0, -10, -10, -10, 20, 40],
                         [30, 50, 40, -10, 0, 20, 50, 30]]

        bPpieceSquare = self.reversePiece(wPpieceSquare)
        bNpieceSquare = self.reversePiece(wNpieceSquare)
        bBpieceSquare = self.reversePiece(wBpieceSquare)
        bRpieceSquare = self.reversePiece(wRpieceSquare)
        bQpieceSquare = self.reversePiece(wQpieceSquare)
        bKpieceSquare = self.reversePiece(wKpieceSquare)

        values = {'wP': 100, 'wR': 500, 'wN': 300, 'wB': 300, 'wQ': 900, 'wK': 20000,
                  'bP': -100, 'bR': -500, 'bN': -300, 'bB': -300, 'bQ': -900, 'bK': -20000}
        score = 0
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece != '--':
                    score += values[self.board[r][c]]
                    # Pawns
                    if piece == 'wP':
                        score += wPpieceSquare[r][c]
                    elif piece == 'bP':
                        score += bPpieceSquare[r][c]
                    # Knights
                    elif piece == 'wN':
                        score += wNpieceSquare[r][c]
                    elif piece == 'bN':
                        score += bNpieceSquare[r][c]
                    # Bishops
                    elif piece == 'wB':
                        score += wBpieceSquare[r][c]
                    elif piece == 'bB':
                        score += bBpieceSquare[r][c]
                    # Rooks
                    elif piece == 'wR':
                        score += wRpieceSquare[r][c]
                    elif piece == 'bR':
                        score += bRpieceSquare[r][c]
                    # Queens
                    elif piece == 'wQ':
                        score += wQpieceSquare[r][c]
                    elif piece == 'bQ':
                        score += bQpieceSquare[r][c]
                    # Kings
                    elif piece == 'wK':
                        score += wKpieceSquare[r][c]
                    elif piece == 'bK':
                        score += bKpieceSquare[r][c]

        return score
        print(score)


    def reversePiece(self, l):
        newList = []
        for row in l:
            newList.insert(0, row)
        for r in range(8):
            for c in range(8):
                newList[r][c] = newList[r][c] * -1

        return newList

    def printBoard(self):
        for x in range(8):
            print(self.board[x])

    def printLog(self):
        for x in self.moveLog:
            print(x.moveID)


class castleRights():

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    # able to allow chess notation to python array location
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        # start location/square
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        # end location/square
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        # piece moved/captured
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # bool to see if either black or white pawn has been moved to the end row
        self.isPawnPromotion = (
                (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7))

        self.isEnpassantMove = isEnpassantMove

        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        self.isCastleMove = isCastleMove

        # to compare the moves
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # move class Object Equality
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    # with use of the fileToRank dictionaries we can print out the move in chess notation (e2e4)
    def getChessNot(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
