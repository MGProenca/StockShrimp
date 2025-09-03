import copy


class CastleRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks  # White king side castle
        self.wqs = wqs
        self.bks = bks  # Black king side castle
        self.bqs = bqs


class Move:
    ranksToRows = {'1': 7, '2': 6, '3': 5,
                   '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a': 0, 'b': 1, 'c': 2,
                   'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassantMove=False, pawnPromotion=False, castleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn promotion
        # self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        self.pawnPromotion = pawnPromotion
        # En passant
        self.enpassantMove = enpassantMove
        self.castleMove = castleMove
        if self.enpassantMove:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'

        # print(
        #     f"Move created: {self.startRow, self.startCol} to {self.endRow, self.endCol}")
        # print(
        #     f'flag values, enpassantMove: {self.enpassantMove}, pawnPromotion: {self.pawnPromotion}, castleMove: {self.castleMove}')

    def encodeMove(self):
        start_index = self.startRow * 8 + self.startCol
        end_index = self.endRow * 8 + self.endCol
        return [
            start_index,
            end_index,
            int(self.enpassantMove),
            int(self.pawnPromotion),
            int(self.castleMove)
        ]

    def __eq__(self, other):
        if isinstance(other, Move):
            return (self.startRow == other.startRow and self.startCol == other.startCol and
                    self.endRow == other.endRow and self.endCol == other.endCol)
        return False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.getChessNotation()} ({self.pieceMoved} -> {self.pieceCaptured})"

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


class GameState:
    def __init__(self):
        # self.board = [
        #     ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
        #     ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
        #     ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        # ]
        self.board = [
            ['--', 'bR', '--', 'bK', '--', '--', '--', 'bR'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', 'wK', '--', '--', '--']
        ]
        # self.board = [
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', 'wp', '--', '--', '--', '--', 'bp', '--'],
        #     ['--', '--', '--', '--', '--', 'bK', '--', 'bp'],
        #     ['--', '--', '--', '--', '--', '--', '--', 'wK']
        # ]
        self.whiteToMove = True  # True if it's white's turn, False if it's
        self.moveLog = []
        self.whiteKingLocation = (7, 4)  # Initial position of the white king
        self.blackKingLocation = (0, 4)  # Initial position of the black
        for r in range(1, len(self.board[0])):
            for c in range(1, len(self.board[1])):
                if self.board[r][c] == 'wK':
                    self.whiteKingLocation = (r, c)
                elif self.board[r][c] == 'bK':
                    self.blackKingLocation = (r, c)
        self.checkmate = False  # True if the game is in checkmate
        self.stalemate = False  # True if the game is in stalemate
        self.inCheck = False  # True if the current player is in check
        self.pins = []  # List of pinned pieces
        self.checks = []  # List of checks on the current player
        self.enpassantPossible = ()  # Coordinates for where en passant capture is possible
        # White king side, white queen side, black king side, black queen side
        
        self.currentCastleRights = CastleRights(False, False, False, False)
        # self.currentCastleRights = CastleRights(True, True, True, True)
        # self.caslteRightsLog = [self.currentCastleRights]
        self.castleRightsLog = [CastleRights(
            self.currentCastleRights.wks, self.currentCastleRights.wqs,
            # List to keep track of castle rights after each move
            self.currentCastleRights.bks, self.currentCastleRights.bqs)]
        self.drawMoveCounter = 0  # Counter for 50-move rule

    def makeMove(self, move: Move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove  # Switch turns
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion
        if move.pawnPromotion:
            # promotedPiece = input('Promote to Q, R, B or N: ')
            promotedPiece = 'Q'  # For simplicity, always promote to Queen
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + \
                promotedPiece

        # En passant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = (
                (move.startRow + move.endRow) // 2, move.startCol)
            print(f"En passant possible at: {self.enpassantPossible}")
        else:
            self.enpassantPossible = ()
            # print('Resetting en passant possible')
        if move.enpassantMove:
            # print(f"En passant move: {move.endRow}, {move.endCol}")
            # Remove the captured pawn
            self.board[move.startRow][move.endCol] = '--'

        # Caslting

        if move.castleMove:
            if move.endCol - move.startCol == 2:  # King side castle
                # Move rook to the left
                self.board[move.endRow][move.endCol -
                                        1] = move.pieceMoved[0] + 'R'
                # Remove rook from the left
                self.board[move.endRow][move.endCol + 1] = '--'

            else:  # queenside castle
                # Move rook to the right
                self.board[move.endRow][move.endCol +
                                        1] = move.pieceMoved[0] + 'R'
                # Remove rook from the right
                self.board[move.endRow][move.endCol - 2] = '--'
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(
            self.currentCastleRights.wks, self.currentCastleRights.wqs,
            # List to keep track of castle rights after each move
            self.currentCastleRights.bks, self.currentCastleRights.bqs))
        
        # 50-move rule UNDO NOT IMPLEMENTED
        self.drawMoveCounter += 1
        if move.pieceMoved[1] == 'p' or move.pieceCaptured != '--':
            self.drawMoveCounter = 0

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo enpassant
            if move.enpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                # Restore en passant square
                self.enpassantPossible = (move.endRow, move.endCol)
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            if move.castleMove:
                if move.endCol - move.startCol == 2:  # King side castle
                    # Move rook back to the right
                    self.board[move.endRow][move.endCol +
                                            1] = move.pieceMoved[0] + 'R'
                    # Remove rook from the left
                    self.board[move.endRow][move.endCol-1] = '--'
                else:  # queenside castle
                    # Move rook to left corner
                    self.board[move.endRow][move.endCol -
                                            2] = move.pieceMoved[0] + 'R'
                    # Remove rook from left of king
                    self.board[move.endRow][move.endCol+1] = '--'

            # Castlerights
            self.castleRightsLog.pop()
            self.currentCastleRights = copy.deepcopy(self.castleRightsLog[-1])

            # 50-move rule
            self.drawMoveCounter -= 1


    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastleRights.wks = False
            self.currentCastleRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastleRights.bks = False
            self.currentCastleRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastleRights.wqs = False  # White queen side rook moved
                elif move.startCol == 7:
                    self.currentCastleRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastleRights.bqs = False  # White queen side rook moved
                elif move.startCol == 7:
                    self.currentCastleRights.bks = False
        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastleRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastleRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastleRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastleRights.bks = False

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            enemy_color = 'b'
            ally_color = 'w'
            startRow, startCol = self.whiteKingLocation
        else:
            enemy_color = 'w'
            ally_color = 'b'
            startRow, startCol = self.blackKingLocation

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1),
                      # Vertical, Horizontal, Diagonal
                      (-1, 1), (1, -1), (1, 1))
        for j, dir in enumerate(directions):
            possiblePin = ()
            for i in range(1, len(self.board[0])):
                endRow = startRow + dir[0] * i
                endCol = startCol + dir[1] * i
                if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == ally_color and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, dir[0], dir[1])
                        else:  # second ally, no pin or check possible in this direction
                            break

                    # 1) vertical or horizontal an its a rook
                    # 2) diagonal and its a bishop
                    # 3) 1 sq diagonal and its a pawn
                    # 4) any direction and queen
                    # 5) 1 sq in any direction and king
                    elif endPiece[0] == enemy_color:  # Enemy piece
                        pieceType = endPiece[1]
                        if (0 <= j <= 3 and pieceType == 'R') or \
                            (4 <= j <= 7 and pieceType == 'B') or \
                            (i == 1 and pieceType == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or \
                            (pieceType == 'Q') or \
                                (i == 1 and pieceType == 'K'):

                            if possiblePin == ():  # no blocks, so its check
                                inCheck = True
                                checks.append((endRow, endCol, dir[0], dir[1]))
                                break
                            else:  # piece blocking, so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece but not a check
                            break
                else:  # out of bounds
                    break
        knightMoves = ((-2, -1), (-1, -2), (1, -2), (2, -1),
                       (2, 1), (1, 2), (-1, 2), (-2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemy_color and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow, kingCol = self.whiteKingLocation
        else:
            kingRow, kingCol = self.blackKingLocation

        if self.inCheck:
            if len(self.checks) == 1:  # Single check, block or move king
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow, checkCol = check[0], check[1]
                checkDir = (check[2], check[3])  # Direction of the check
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # Squares where the king can move to escape check
                if pieceChecking[1] == 'N':  # Knight check, cant block
                    # Knight can be captured
                    validSquares = [(checkRow, checkCol)]
                else:  # Rook, Bishop, Queen or King check
                    for i in range(1, len(self.board[0])):
                        validSquare = (
                            kingRow + checkDir[0] * i, kingCol + checkDir[1] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # remove moves that don't block or move the king
                # go backwards when removing from list
                for i in range(len(moves) - 1, -1, -1):
                    # does not move king, so must block or capture
                    if moves[i].pieceMoved[1] != 'K':
                        # move does not block or captures
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:  # Double check, must move king
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # Not in check, get all possible moves
            moves = self.getAllPossibleMoves()

        # Updates engame flags
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
                return moves
            self.stalemate = True
        
        if self.drawMoveCounter >= 100:
            self.stalemate = True

        return moves

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # Rows
            for c in range(len(self.board[r])):  # Columns in curr row
                color_turn = self.board[r][c][0]  # Get the color of the piece
                if (color_turn == 'w' and self.whiteToMove) or (color_turn == 'b' and not self.whiteToMove):
                    piece_type = self.board[r][c][1]
                    # print('PIECE:', piece_type)
                    if piece_type == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece_type == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece_type == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece_type == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece_type == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece_type == 'K':
                        self.getKingMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        pawnPromotion = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])  # Remove the pin from the list
                break

        if self.whiteToMove:
            enemy_color = 'b'
            move_dir = -1
            endrow = 0
            startrow = 6
        else:
            enemy_color = 'w'
            move_dir = 1
            endrow = 7
            startrow = 1

        print('PAWN CHECKING')
        if self.board[r+move_dir][c] == '--':  # 1 sq move
            # Not pinned or pinned in the same direction
            if not piecePinned or pinDirection == (move_dir, 0):
                if r+move_dir == endrow:
                    pawnPromotion = True
                    print("Pawn promotion!", pawnPromotion)
                moves.append(Move((r, c), (r+move_dir, c),
                             self.board, pawnPromotion=pawnPromotion))
                if r == startrow and self.board[r+2*move_dir][c] == '--':
                    moves.append(Move((r, c), (r+2*move_dir, c), self.board))

        for capture_col_dir in [-1, 1]:
            if 0 <= c+capture_col_dir < len(self.board[r]):  # captures to left
                # Enemy piece capture
                if self.board[r+move_dir][c+capture_col_dir][0] == enemy_color:
                    if not piecePinned or pinDirection == (move_dir, -1):
                        if r+move_dir == endrow:
                            pawnPromotion = True
                            print("Capture Pawn promotion!", pawnPromotion)
                        moves.append(Move(
                            (r, c), (r+move_dir, c+capture_col_dir), self.board, pawnPromotion=pawnPromotion))
                elif (r+move_dir, c-1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r+move_dir, c+capture_col_dir), self.board, enpassantMove=True))

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            # Check if piece im looking is pinned
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # Cant remove queen pin on rook moves
                    self.pins.remove(self.pins[i])
                break
        enemy_color = 'b' if self.whiteToMove else 'w'

        for dir in ((-1, 0), (1, 0), (0, -1), (0, 1)):  # Up, Down, Left, Right
            # Check up to 7 squares in each direction
            for i in range(1, len(self.board[0])):
                endRow = r + dir[0] * i
                endCol = c + dir[1] * i
                # print(f"Checking Rook move from {r, c} to {new_pos}")
                # on board
                if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                    # Not pinned or movin while maintaining pin
                    if not piecePinned or pinDirection == dir or pinDirection == (-dir[0], -dir[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # Empty square
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy_color:  # Same color piece
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                            break  # Stop if we hit an enemy piece
                        else:  # Same color piece
                            break
                else:
                    # print("Out of bounds")
                    break

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        knight_moves = ((-2, -1), (-1, -2), (1, -2), (2, -1),
                        (2, 1), (1, 2), (-1, 2), (-2, 1))
        ally_color = 'w' if self.whiteToMove else 'b'

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])  # Remove the pin from the list
                break

        for m in knight_moves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != ally_color:  # Not ally = empty or enemy
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            # Check if piece im looking is pinned
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        enemy_color = 'b' if self.whiteToMove else 'w'

        # Up-Left, Up-Right, Down-Left, Down-Right
        for dir in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            # Check up to 7 squares in each direction
            for i in range(1, len(self.board[0])):
                endRow = r + dir[0] * i
                endCol = c + dir[1] * i
                # print(f"Checking bishop move from {r, c} to {endRow, endCol}")
                if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                    # Not pinned or movin while maintaining pin
                    if not piecePinned or pinDirection == dir or pinDirection == (-dir[0], -dir[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # Empty square
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy_color:  # Same color piece
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                            break  # Stop if we hit an enemy piece
                        else:  # Same color piece
                            break
                else:
                    # print("Out of bounds")
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        ally_color = 'w' if self.whiteToMove else 'b'
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                      (0, 1), (1, -1), (1, 0), (1, 1))

        for m in king_moves:
            # new_pos = (r + m[0], c + m[1])
            endRow = r + m[0]
            endCol = c + m[1]
            # print(f"Checking king move from {r, c} to {endRow, endCol}")

            # Check if inside the board
            if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != ally_color:
                    # Temporarily move the king to check for checks
                    if ally_color == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()

                    if not inCheck:  # If the move does not put the king in check
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))

                    # Reset king location
                    if ally_color == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        self.getCastleMoves(r, c, moves)  # Check for castling moves

    def getCastleMoves(self, r, c, moves):
        if self.inCheck:
            return

        if (self.whiteToMove and self.currentCastleRights.wks) or (not self.whiteToMove and self.currentCastleRights.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastleRights.wqs) or (not self.whiteToMove and self.currentCastleRights.bqs):
            print('HAVE QUEEN SIDE CASTLE RIGHTS')
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        print('GETTING KING SIDE CASTLE MOVES', r, c)
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            # Temporarily switch to opponent's turn
            self.whiteToMove = not self.whiteToMove
            for check_square in [(r, c+1), (r, c+2)]:
                inCheck, pins, checks = self.checkForPinsAndChecks()
                if check_square in checks:
                    # Switch back if loop ends early anyway
                    self.whiteToMove = not self.whiteToMove
                    return
            self.whiteToMove = not self.whiteToMove  # Switch back to original turn
            moves.append(Move((r, c), (r, c+2), self.board, castleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            # Temporarily switch to opponent's turn
            self.whiteToMove = not self.whiteToMove
            for check_square in [(r, c-1), (r, c-2)]:
                inCheck, pins, checks = self.checkForPinsAndChecks()
                if check_square in checks:
                    # Switch back if loop ends early anyway
                    self.whiteToMove = not self.whiteToMove
                    return
            self.whiteToMove = not self.whiteToMove  # Switch back to original turn
            moves.append(Move((r, c), (r, c-2), self.board, castleMove=True))

    def encodeGamestate(self):
        piece_to_int = {
            '--': 0,
            'wp': 1, 'wN': 2, 'wB': 3, 'wR': 4, 'wQ': 5, 'wK': 6,
            'bp': -1, 'bN': -2, 'bB': -3, 'bR': -4, 'bQ': -5, 'bK': -6
        }

        return [[piece_to_int[square] for square in row] for row in self.board]

    def getValueAndTerminated(self):
        self.getValidMoves()
        if self.checkmate:
            return 1, True
        elif self.stalemate:
            return 0, True
        return 0, False 
    
    def getOpponentValue(self, value):
        return - value
