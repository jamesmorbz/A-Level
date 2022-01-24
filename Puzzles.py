import math
import copy

class GameStatePuzzles():
    def __init__(self):
        # board is 8x8 2D List, each element of the list has 2 characters
        # First character == colour (b = black ,w = white)
        # second character == piece
        # R == rook, N == knight, B == bishop, Q == Queen, K == king, P == pawn
        # -- == empty space
        # start board
        self.board = [
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "wR"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["bK", "--", "wK", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"]]

        self.whiteToMove = True
        self.moveLog = []

        # These are defined and set to false as either can be changed to the bool True in order to end the game
        self.checkMate = False
        self.stalemate = False

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

    def printBoard(self):
        for x in range(8):
            print(self.board[x])

    def printLog(self):
        for x in self.moveLog:
            print(x.moveID)

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

    # with use of the fileToRank dictionaries we can print out the move in chess notation (e2e4)
    def getChessNot(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]